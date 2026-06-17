"""HOP pipeline substrate — shared inner-DAG executor for apps_*.

This module is the canonical home for per-app inner-DAG orchestration.
Apps declare their stage topology in ``apps_<name>/config/hop_pipeline.py``,
implement each stage as an engine in ``apps_<name>/engines/<stage>_engine.py``,
and delegate execution to ``HopPipelineExecutor`` from a thin orchestrator
under ``apps_<name>/reasoning/``.

Architecture
------------
Three public types compose the substrate:

- :class:`HopStageSpec` — frozen Pydantic declaration of one stage
  (id, name, engine module/class, I/O contract, gate/skip semantics).
- :class:`HopRegistry` — per-app ordered collection of ``HopStageSpec``
  with validation (no dup IDs, no circular skip refs).
- :class:`HopPipelineExecutor` — walks the registry, lazy-imports each
  engine, calls ``engine.execute(context)``, records a :class:`Checkpoint`
  per stage, and returns a sealed :class:`HopRunRecord`.

Stage contract
--------------
Each engine class must expose::

    class MyStageEngine:
        def execute(self, context: dict, **kwargs) -> dict: ...

The returned dict is merged into the context carried to the next stage.
Engines may raise; the executor catches, records ``FAILED``, and halts.

Layer gravity
-------------
This module imports only from ``agentic_core`` and stdlib. It MUST NOT
import from any ``apps_<name>/`` package — apps depend on apps_shared,
never the reverse. Enforced by ``check_apps_shared_no_app_imports``.

See: .claude/plans/apps-hop-substrate-f7751b.md
"""

from __future__ import annotations

import importlib
import logging
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

_logger = logging.getLogger(__name__)


# =============================================================================
# Stage status + checkpoint
# =============================================================================


class StageStatus(str, Enum):
    """Terminal status of a single stage execution."""

    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    GATED = "GATED"


@dataclass(frozen=True)
class Checkpoint:
    """Immutable record of one stage's execution.

    Attributes
    ----------
    stage_id:       Integer stage identifier from the spec.
    stage_name:     Human-readable stage name from the spec.
    status:         Terminal status (COMPLETED/SKIPPED/FAILED/GATED).
    output:         Stage output dict (empty when SKIPPED/FAILED).
    error:          Error message when FAILED, else "".
    duration_ms:    Wall-clock duration in milliseconds (0 when SKIPPED).
    """

    stage_id: int
    stage_name: str
    status: StageStatus
    output: Mapping[str, Any] = field(default_factory=dict)
    error: str = ""
    duration_ms: int = 0


@dataclass(frozen=True)
class HopRunRecord:
    """Immutable record of a full HOP pipeline run.

    Attributes
    ----------
    run_id:          Correlation key for the run.
    checkpoints:     Ordered tuple of per-stage Checkpoints.
    final_context:   Context dict after the terminal stage.
    terminal_error:  Non-empty when the run halted on FAILED/GATED.
    """

    run_id: str
    checkpoints: tuple[Checkpoint, ...]
    final_context: Mapping[str, Any]
    terminal_error: str = ""

    @property
    def success(self) -> bool:
        """True when every stage is COMPLETED or SKIPPED."""
        return self.terminal_error == "" and all(
            cp.status in (StageStatus.COMPLETED, StageStatus.SKIPPED) for cp in self.checkpoints
        )


# =============================================================================
# Stage spec
# =============================================================================


class HopStageSpec(BaseModel):
    """Declarative specification for a single pipeline stage.

    Fields
    ------
    stage_id:            Integer identifier; must be unique per registry.
                         Registry ordering is by ``stage_id`` ascending.
    stage_name:          Short human-readable name (``snake_case``).
    engine_module:       Fully-qualified dotted path, e.g.
                         ``"apps_lic.engines.profile_analysis_engine"``.
    engine_class:        Class name inside ``engine_module`` exposing
                         ``execute(context) -> dict``.
    inputs:              Context keys the engine reads (advisory — used
                         by the registry validator and CI gate).
    outputs:             Context keys the engine writes.
    required:            When False, stage failure is downgraded to
                         FAILED-but-continue (executor still halts on
                         required-stage failure).
    gate:                When True, a falsy ``output.get("passed", True)``
                         marks this stage GATED and halts the run.
    optional_skip_if:    Optional context key; when truthy at stage entry,
                         the stage is SKIPPED.
    config_class:        Optional dotted path to a Pydantic class carrying
                         per-stage tuning knobs (separates topology from
                         parameter schemas).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    stage_id: int = Field(..., ge=0)
    stage_name: str = Field(..., min_length=1)
    engine_module: str = Field(..., min_length=1)
    engine_class: str = Field(..., min_length=1)
    inputs: tuple[str, ...] = Field(default_factory=tuple)
    outputs: tuple[str, ...] = Field(default_factory=tuple)
    required: bool = True
    gate: bool = False
    optional_skip_if: str | None = None
    config_class: str | None = None

    @field_validator("stage_name")
    @classmethod
    def _snake_case(cls, v: str) -> str:
        if not v.replace("_", "").isalnum() or v != v.lower():
            raise ValueError(f"stage_name must be lower snake_case, got: {v!r}")
        return v


# =============================================================================
# Registry
# =============================================================================


class HopRegistryValidationError(ValueError):
    """Raised when a HopRegistry fails structural validation."""


class HopRegistry:
    """Ordered per-app collection of :class:`HopStageSpec`.

    Registries are typically constructed at module-import time in
    ``apps_<name>/config/hop_pipeline.py`` and exported as a module-level
    constant ``REGISTRY``. The :meth:`validate` method is invoked once at
    construction via :meth:`register_all`; subsequent registrations re-run
    validation to keep the invariant at every mutation.
    """

    def __init__(self, app_name: str) -> None:
        self._app_name = app_name
        self._specs: dict[int, HopStageSpec] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def register(self, spec: HopStageSpec) -> HopRegistry:
        """Add a single stage spec. Raises on dup stage_id."""
        if spec.stage_id in self._specs:
            raise HopRegistryValidationError(
                f"{self._app_name}: duplicate stage_id {spec.stage_id} "
                f"(existing: {self._specs[spec.stage_id].stage_name!r}, "
                f"new: {spec.stage_name!r})"
            )
        self._specs[spec.stage_id] = spec
        self._validate_skip_refs()
        return self

    def register_all(self, specs: list[HopStageSpec]) -> HopRegistry:
        """Register a batch and validate."""
        for spec in specs:
            if spec.stage_id in self._specs:
                raise HopRegistryValidationError(
                    f"{self._app_name}: duplicate stage_id {spec.stage_id}"
                )
            self._specs[spec.stage_id] = spec
        self._validate_skip_refs()
        return self

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @property
    def app_name(self) -> str:
        return self._app_name

    def get(self, stage_id: int) -> HopStageSpec | None:
        return self._specs.get(stage_id)

    def ordered(self) -> tuple[HopStageSpec, ...]:
        """Return all specs in stage_id ascending order."""
        return tuple(self._specs[k] for k in sorted(self._specs))

    def stage_count(self) -> int:
        return len(self._specs)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_skip_refs(self) -> None:
        """``optional_skip_if`` refs must not be self-referential."""
        for spec in self._specs.values():
            key = spec.optional_skip_if
            if key is None:
                continue
            # A stage whose skip flag is keyed on its own output is circular.
            if key in spec.outputs:
                raise HopRegistryValidationError(
                    f"{self._app_name}: stage {spec.stage_id} "
                    f"({spec.stage_name!r}) has optional_skip_if={key!r} "
                    f"which appears in its own outputs — circular skip ref"
                )

    def validate(self) -> None:
        """Full structural validation. Called implicitly on register_all."""
        self._validate_skip_refs()
        if not self._specs:
            raise HopRegistryValidationError(
                f"{self._app_name}: registry is empty"
            )


# =============================================================================
# Executor
# =============================================================================


# Sentinel: engine cache miss signal for lazy import.
_ENGINE_CACHE: dict[tuple[str, str], type] = {}


def _load_engine(spec: HopStageSpec) -> Any:
    """Lazy-import and instantiate the engine for a stage spec.

    Uses a module-level cache keyed on ``(engine_module, engine_class)``.
    Engines are expected to be constructible with no arguments.
    """
    key = (spec.engine_module, spec.engine_class)
    cls = _ENGINE_CACHE.get(key)
    if cls is None:
        try:
            mod = importlib.import_module(spec.engine_module)
        except ImportError as exc:
            raise HopRegistryValidationError(
                f"stage {spec.stage_id} ({spec.stage_name!r}): "
                f"cannot import engine_module={spec.engine_module!r}: {exc}"
            ) from exc
        cls = getattr(mod, spec.engine_class, None)
        if cls is None:
            raise HopRegistryValidationError(
                f"stage {spec.stage_id} ({spec.stage_name!r}): "
                f"engine_module={spec.engine_module!r} has no class "
                f"{spec.engine_class!r}"
            )
        _ENGINE_CACHE[key] = cls
    return cls()


@dataclass
class HopPipelineExecutor:
    """Walks a :class:`HopRegistry` and produces a :class:`HopRunRecord`.

    The executor is intentionally stateless between runs — it holds only
    the registry reference and an optional seal-step adapter. One executor
    instance per app is the recommended pattern (construct once at app
    bootstrap, call :meth:`run` per request).

    Parameters
    ----------
    registry:
        The per-app :class:`HopRegistry`.
    seal_step_provider:
        Optional zero-arg callable returning a context-manager factory with
        signature ``(step_id: str, trace_id: str, component: str) -> CM``.
        When supplied, each stage runs inside ``with provider()(step_id,
        trace_id, component) as bag:``. The bag's ``["output"]`` key is
        populated with the stage output. When ``None``, stages run
        untouched. Matches the
        ``apps_shared.adapters.system_learning_facade.seal_step`` contract.
    """

    registry: HopRegistry
    seal_step_provider: Callable[[], Callable[..., Any]] | None = None

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    def run(
        self,
        context: dict[str, Any] | None = None,
        *,
        run_id: str = "",
        trace_id: str = "",
    ) -> HopRunRecord:
        """Execute the full pipeline. Returns a sealed :class:`HopRunRecord`.

        The context dict is mutated in place as stages contribute outputs.
        Callers wanting isolation should pass a copy.
        """
        ctx: dict[str, Any] = dict(context) if context else {}
        effective_run_id = run_id or uuid.uuid4().hex[:16]
        checkpoints: list[Checkpoint] = []
        terminal_error = ""

        for spec in self.registry.ordered():
            # Skip check (pre-execution)
            if spec.optional_skip_if and ctx.get(spec.optional_skip_if):
                checkpoints.append(
                    Checkpoint(
                        stage_id=spec.stage_id,
                        stage_name=spec.stage_name,
                        status=StageStatus.SKIPPED,
                        output={},
                        error="",
                        duration_ms=0,
                    )
                )
                continue

            cp = self._execute_one(spec, ctx, trace_id=trace_id)
            checkpoints.append(cp)

            # Merge outputs into context for downstream stages
            if cp.status is StageStatus.COMPLETED and cp.output:
                ctx.update(cp.output)

            # Halt on FAILED (required) or GATED
            if cp.status is StageStatus.FAILED and spec.required:
                terminal_error = (
                    f"stage {spec.stage_id} ({spec.stage_name}) failed: {cp.error}"
                )
                break
            if cp.status is StageStatus.GATED:
                terminal_error = (
                    f"stage {spec.stage_id} ({spec.stage_name}) gated run halt"
                )
                break

        return HopRunRecord(
            run_id=effective_run_id,
            checkpoints=tuple(checkpoints),
            final_context=ctx,
            terminal_error=terminal_error,
        )

    def replay_stage(
        self,
        stage_id: int,
        context: dict[str, Any],
        *,
        trace_id: str = "",
    ) -> Checkpoint:
        """Re-run a single stage. Used by healing / incident replay paths.

        Unlike :meth:`run`, ``replay_stage`` bypasses skip checks and does
        not mutate any sibling-stage state. It returns just the
        :class:`Checkpoint` for the single stage.
        """
        spec = self.registry.get(stage_id)
        if spec is None:
            return Checkpoint(
                stage_id=stage_id,
                stage_name="unknown",
                status=StageStatus.FAILED,
                output={},
                error=f"stage_id {stage_id} not found in registry "
                f"({self.registry.app_name})",
                duration_ms=0,
            )
        return self._execute_one(spec, dict(context), trace_id=trace_id)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _execute_one(
        self,
        spec: HopStageSpec,
        ctx: dict[str, Any],
        *,
        trace_id: str,
    ) -> Checkpoint:
        """Execute a single stage, wrapped in optional seal_step."""
        import time  # noqa: PLC0415 — kept local; stdlib only

        start_ns = time.perf_counter_ns()
        step_id = f"hop_stage_{spec.stage_id}_{spec.stage_name}"

        try:
            engine = _load_engine(spec)
        except HopRegistryValidationError as exc:
            duration_ms = (time.perf_counter_ns() - start_ns) // 1_000_000
            return Checkpoint(
                stage_id=spec.stage_id,
                stage_name=spec.stage_name,
                status=StageStatus.FAILED,
                output={},
                error=f"engine load failed: {exc}",
                duration_ms=int(duration_ms),
            )

        output: dict[str, Any] = {}
        error = ""
        status = StageStatus.COMPLETED

        try:
            if self.seal_step_provider is not None:
                seal_cm_factory = self.seal_step_provider()
                with seal_cm_factory(
                    step_id=step_id,
                    trace_id=trace_id,
                    component=f"{self.registry.app_name}.HopPipelineExecutor",
                ) as seal_bag:
                    raw = engine.execute(ctx)
                    output = dict(raw) if raw else {}
                    if isinstance(seal_bag, dict):
                        seal_bag["output"] = output
            else:
                raw = engine.execute(ctx)
                output = dict(raw) if raw else {}
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:  # guardian: allow-log-and-swallow -- P2 burndown: fail-soft optional boundary
            # guardian: allow-broad-exception -- engine stage is a plugin boundary;
            # heterogeneous engine failures must be caught and surfaced as FAILED
            # checkpoints so the pipeline can halt or continue per `required`.
            status = StageStatus.FAILED
            error = f"{type(exc).__name__}: {exc}"
            _logger.warning(
                "hop_pipeline: stage %d (%s) failed: %s",
                spec.stage_id,
                spec.stage_name,
                error,
            )

        # Gate evaluation (applies only on COMPLETED)
        if status is StageStatus.COMPLETED and spec.gate:
            passed = bool(output.get("passed", True))
            if not passed:
                status = StageStatus.GATED

        duration_ms = (time.perf_counter_ns() - start_ns) // 1_000_000
        return Checkpoint(
            stage_id=spec.stage_id,
            stage_name=spec.stage_name,
            status=status,
            output=output,
            error=error,
            duration_ms=int(duration_ms),
        )
