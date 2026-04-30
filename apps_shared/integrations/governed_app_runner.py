"""
Shared governed-app runner — reusable L1→L0→C0→L2→L5+L6 pipeline base.

All governed apps subclass GovernedAppRunner and configure via class
attributes (APP_NAME, CAPABILITY_TOKEN, ROUTING_TARGET, ROUTING_KEYWORDS)
plus constructor args (collection).

Pattern::

    class MyGovernedRun(GovernedAppRunner):
        APP_NAME        = "apps_my"
        CAPABILITY_TOKEN = "apps_my.governed_e2e.v1"
        ROUTING_TARGET  = "my_assembly"
        ROUTING_KEYWORDS = ["keyword1", "keyword2"]

        def __init__(self, collection: str = "my_docs") -> None:
            super().__init__(collection=collection)

        def run_governed_e2e(self, request, *, inject_chunks=None):
            core = self.run_governed_core(
                query=_query_from(request),
                run_id=request.trace_id or "",
                inject_chunks=inject_chunks,
            )
            return _translate(core)          # app-specific record type

Current consumers:
  apps_research.integrations.governed_research_run.GovernedResearchRun
  apps_exec.integrations.governed_exec_run.GovernedExecRun

No bypass.  No new packages.  No router redesign.  No collection rebuilds.
Layer rule: apps_shared may import from agentic_core L0–L6 only (downward).
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any, Mapping

from apps_shared.integrations.runtime_hitl_integration import (
    HitlResult,
    build_exit_envelope,
    maybe_escalate_hitl,
)

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# W2: STRICT_GOVERNANCE env flag
# ---------------------------------------------------------------------------

_STRICT_GOVERNANCE_ENV = "STRICT_GOVERNANCE"


def _strict_governance_enabled() -> bool:
    """Return True when ``STRICT_GOVERNANCE`` env var is set to a truthy value.

    Truthy: ``1``, ``true``, ``yes``, ``on`` (case-insensitive).
    Default (unset / falsy): legacy best-effort behavior — phases that fail
    silently produce error fields but do NOT raise.
    """
    raw = os.environ.get(_STRICT_GOVERNANCE_ENV, "").strip().lower()
    return raw in ("1", "true", "yes", "on")


class GovernanceContractViolation(RuntimeError):
    """Raised when ``STRICT_GOVERNANCE=1`` and a mandatory phase fails.

    Mandatory phases under strict mode: L2 chokepoint, L5 exit gate,
    L6 observability ingest. L1/L0/C0 remain best-effort because they
    have well-defined graceful fallbacks (substrate documents the
    fallback paths in each ``_l1_plan`` / ``_l0_route`` / ``_c0_retrieve``).
    HITL is best-effort even under strict mode — it is opt-in per app
    via ``HITL_ENABLED`` and per env via ``RUNTIME_HITL_ENABLED``.

    Carries:
        phase:   ``"L2" | "L5" | "L6"``
        message: the underlying phase error string
        record:  the partially-built ``GovernedAppRunRecord`` so callers can
                 still inspect what completed before the violation
    """

    def __init__(self, phase: str, message: str, record: Any | None = None) -> None:
        super().__init__(f"STRICT_GOVERNANCE: {phase} mandatory phase failed: {message}")
        self.phase = phase
        self.message = message
        self.record = record


# ---------------------------------------------------------------------------
# Internal pipeline stage types (private to this module)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _PlanOutput:
    sub_queries: tuple[str, ...]
    fallback_used: bool = False
    error: str = ""


@dataclass(frozen=True)
class _RouteOutput:
    intent: str
    target_name: str
    confidence: float
    fallback_used: bool = False
    error: str = ""


@dataclass
class _AppContext:
    """Minimal execution context passed to evaluate_and_emit()."""

    run_id: str
    policy_hash: str | None = None


# ---------------------------------------------------------------------------
# GovernedAppRunRecord — common sealed record for all governed apps
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GovernedAppRunRecord:
    """Sealed record of one governed app E2E pipeline run.

    App-specific runners translate this into their own result types before
    returning to callers (see GovernedResearchRun, GovernedExecRun).

    Fields
    ------
    run_id:           Correlation key.
    app_name:         Application identifier (e.g. "apps_research").
    query:            Primary query string fed through the pipeline.
    l1_sub_queries:   Sub-queries produced by L1 query_planner.
    l1_fallback:      True when L1 fell back to the original query.
    l0_intent:        Intent label assigned by L0 router.
    l0_target:        Routing target chosen by L0 router.
    l0_confidence:    L0 routing confidence (0.0–1.0).
    l0_fallback:      True when L0 fell back.
    c0_raw_count:     Chunks from real retrieval (0 when store absent).
    c0_shaped_count:  Chunks after EvidenceShaper.shape().
    c0_collection:    Collection queried.
    disposition:      WeakSupportDisposition.value.
    gate_disposition: ExitDisposition.value.
    grounded:         True when gate result reports grounded_replayable=True.
    citation_count:   Citation anchors from the shaped bundle.
    support_coverage: Mean combined_score across ranked chunks.
    l6_ingested:      True when L6 ingest_eval_packet() was invoked.
    l2_executed:      True when authorize_and_execute() ran without error.
    error:            "" on success; aggregated phase-error message on failure
                      (kept for backward compatibility; prefer per-phase fields).

    Per-phase error fields (W1 hardening — ADG G1)
    ----------------------------------------------
    l1_error / l0_error / c0_error / l2_error / l5_error / l6_error / hitl_error:
        Empty string on success for that phase; exception message on failure.
        Surfacing per-phase identity replaces the prior whole-pipeline broad catch.
    """

    run_id: str
    app_name: str
    query: str
    l1_sub_queries: tuple[str, ...]
    l1_fallback: bool
    l0_intent: str
    l0_target: str
    l0_confidence: float
    l0_fallback: bool
    c0_raw_count: int
    c0_shaped_count: int
    c0_collection: str
    disposition: str
    gate_disposition: str
    grounded: bool
    citation_count: int
    support_coverage: float
    l6_ingested: bool
    l2_executed: bool
    error: str
    # ── Per-phase errors (W1 hardening — default "" preserves back-compat) ──
    l1_error: str = ""
    l0_error: str = ""
    c0_error: str = ""
    l2_error: str = ""
    l5_error: str = ""
    l6_error: str = ""
    hitl_error: str = ""
    # ── Runtime HITL (W5) — defaults preserve backward compatibility ──
    hitl_action: str = "none"  # "none" | "commit" | "escalate_hitl" | "deny"
    hitl_class: str = ""  # e.g. "financial", "regulated"; "" when not escalated
    hitl_ledger_id: str = ""  # ledger row id when escalated; "" otherwise
    hitl_enabled: bool = False  # True when the per-run HITL hook was active


# ---------------------------------------------------------------------------
# W5: build_app_record — boilerplate-free per-app record construction
# ---------------------------------------------------------------------------


def build_app_record(
    target_cls: type,
    core: GovernedAppRunRecord,
    *,
    aliases: Mapping[str, str] | None = None,
    **app_specific: Any,
) -> Any:
    """Construct a per-app frozen dataclass from a substrate record.

    Eliminates the 25–30 lines of ``field=core.field`` translator boilerplate
    that previously lived in every ``apps_*/integrations/governed_*_run.py``.
    When the substrate adds a new field, every per-app translator picks it
    up automatically — no per-app file edit required.

    Field-mapping rules
    -------------------
    1. For each field declared on ``target_cls``:
       a. If the same name appears in ``app_specific``, use that value.
       b. Else if the name appears in ``aliases``, copy the **substrate
          field named by the alias value** (lets ``apps_research`` map
          ``topic <- query``).
       c. Else if the name appears as a substrate field, copy it from
          ``core``.
       d. Else leave it unset — the dataclass default applies, or
          construction raises if no default exists (which is the right
          behavior: surfaces missing app-specific fields loudly).

    Parameters
    ----------
    target_cls:
        Per-app frozen dataclass type, e.g. ``GovernedExecE2ERunRecord``.
    core:
        The shared substrate record returned by ``run_governed_core``.
    aliases:
        Optional mapping of ``target_field_name -> substrate_field_name``
        for fields that the per-app record renames.
    **app_specific:
        Per-app kwargs (e.g. ``audience=...``, ``campaign_id=...``) that
        are not present on the substrate.

    Returns
    -------
    A new instance of ``target_cls``.

    Examples
    --------
    Standard translator (apps_exec)::

        return build_app_record(
            GovernedExecE2ERunRecord, core,
            audience=audience,
            emphasis_areas=tuple(emphasis_areas),
        )

    With alias (apps_research renames ``query`` to ``topic``)::

        return build_app_record(
            GovernedE2ERunRecord, core,
            aliases={"topic": "query"},
        )
    """
    import dataclasses  # noqa: PLC0415 — deferred so module import stays cheap

    aliases = dict(aliases or {})
    substrate_field_names = {f.name for f in dataclasses.fields(GovernedAppRunRecord)}

    kwargs: dict[str, Any] = {}
    for f in dataclasses.fields(target_cls):
        if f.name in app_specific:
            kwargs[f.name] = app_specific[f.name]
            continue
        # Check alias first (target field maps to a different substrate name).
        src_name = aliases.get(f.name, f.name)
        if src_name in substrate_field_names:
            kwargs[f.name] = getattr(core, src_name)
        # Else: leave unset; dataclass default applies, or constructor raises.

    # Surface unknown app_specific keys as TypeError at construction time
    # rather than silently ignoring them.
    target_field_names = {f.name for f in dataclasses.fields(target_cls)}
    unknown_keys = set(app_specific) - target_field_names
    if unknown_keys:
        raise TypeError(
            f"build_app_record: unknown app_specific keys for {target_cls.__name__}: "
            f"{sorted(unknown_keys)}"
        )

    return target_cls(**kwargs)


# ---------------------------------------------------------------------------
# GovernedAppRunner — shared base class
# ---------------------------------------------------------------------------


class GovernedAppRunner:
    """Shared base for the governed-app L1→L0→C0→L2→L5+L6 pipeline.

    Subclasses declare their app identity via class attributes and call
    ``run_governed_core()`` from their app-specific ``run_governed_e2e()``
    method to execute the common governed substrate.

    Class attributes to override
    ----------------------------
    APP_NAME:         e.g. "apps_research"
    CAPABILITY_TOKEN: e.g. "apps_research.governed_e2e.v1"
    ROUTING_TARGET:   e.g. "research_assembly"
    ROUTING_KEYWORDS: e.g. ["research", "analysis", ...]
    """

    APP_NAME: str = ""
    CAPABILITY_TOKEN: str = ""
    ROUTING_TARGET: str = ""
    ROUTING_KEYWORDS: list[str] = []
    # Runtime HITL (W5): per-app opt-in. Master env flag RUNTIME_HITL_ENABLED
    # must ALSO be set for the hook to engage.
    HITL_ENABLED: bool = False

    def __init__(self, collection: str = "process_docs") -> None:
        self._collection = collection
        # Injectable for tests / production composition. Default None → helper
        # lazily constructs policy + ledger from SSOT paths on first escalate.
        self._hitl_controller: Any = None
        self._hitl_run_state_store: Any = None
        # W6.2: Cached AgenticRouter — lazy-initialized on first L0 call. Keeping
        # one router per runner instance preserves bandit posterior state across
        # `run_governed_core` invocations (per ADG hotspot G10). Not thread-safe;
        # one runner per concurrent caller is the recommended pattern.
        self._cached_router: Any = None

    # ------------------------------------------------------------------
    # Public: shared pipeline
    # ------------------------------------------------------------------

    async def run_governed_core_async(
        self,
        query: str,
        *,
        run_id: str = "",
        inject_chunks: list[Any] | None = None,
    ) -> GovernedAppRunRecord:
        """Async-friendly facade around ``run_governed_core``.

        W6.1: Provides an awaitable entrypoint so callers running inside an
        event loop can issue concurrent governed runs without ``asyncio.run``
        re-entry errors. Implementation offloads the synchronous pipeline to
        a worker thread via ``asyncio.to_thread`` — the caller's event loop
        is not blocked while the pipeline executes.

        This is the recommended public entrypoint for new async callers.
        Existing sync callers continue to use ``run_governed_core``.

        Concurrency model
        -----------------
        - One ``GovernedAppRunner`` instance is NOT thread-safe; do not call
          this method concurrently on the same instance.
        - Multiple instances can run concurrently — bandit posterior accrual
          is per-instance (W6.2 cached router).
        - Future work (out of W6 scope): replace the internal
          ``asyncio.run(...)`` calls in ``_l1_plan`` / ``_l0_route`` with
          ``await`` so the pipeline becomes truly async-native and avoids
          the worker-thread hop. The async helpers ``_l1_plan_async`` and
          ``_l0_route_async`` are the future migration targets.
        """
        return await asyncio.to_thread(
            self.run_governed_core,
            query,
            run_id=run_id,
            inject_chunks=inject_chunks,
        )

    def run_governed_core(
        self,
        query: str,
        *,
        run_id: str = "",
        inject_chunks: list[Any] | None = None,
    ) -> GovernedAppRunRecord:
        """Execute L1→L0→C0→L2→L5+L6 and return a sealed GovernedAppRunRecord.

        Parameters
        ----------
        query:
            Primary query / topic string for this run.
        run_id:
            Correlation key; a UUID is generated when empty.
        inject_chunks:
            Optional list of HybridSearchResult-like objects appended to
            real retrieval results before EvidenceShaper.shape() runs.
            Represents what real retrieval would return when the canonical
            store is populated; graceful degradation is expected when this
            is None and ChromaDB/BM25 index are absent.
        """
        import uuid as _uuid  # noqa: PLC0415

        run_id = run_id or str(_uuid.uuid4())

        error = ""
        gate_disposition = "unknown"
        disposition_str = "unknown"
        grounded = False
        citation_count = 0
        support_coverage = 0.0
        l6_ingested = False
        l2_executed = False
        c0_raw_count = 0
        c0_shaped_count = 0
        hitl_action = "none"
        hitl_class_str = ""
        hitl_ledger_id = ""
        hitl_enabled = False

        plan = _PlanOutput(sub_queries=(query,), fallback_used=True)
        route = _RouteOutput(
            intent=query,
            target_name=self.ROUTING_TARGET or "unknown",
            confidence=0.0,
            fallback_used=True,
        )
        bundle: Any = None

        # Per-phase error tracking (W1 hardening — ADG G1).
        # Each phase records its own error preserving phase identity.
        # The aggregate ``error`` field is rebuilt at the end for back-compat.
        l1_error = ""
        l0_error = ""
        c0_error = ""
        l2_error = ""
        l5_error = ""
        l6_error = ""
        hitl_error = ""

        # Phase 1 — L1: intent decomposition via query_planner
        # _l1_plan() handles its own exceptions and surfaces them in plan.error.
        plan = self._l1_plan(query)
        l1_error = plan.error
        primary_query = plan.sub_queries[0] if plan.sub_queries else query

        # Phase 2 — L0: route switching via AgenticRouter
        # _l0_route() handles its own exceptions and surfaces them in route.error.
        route = self._l0_route(query)
        l0_error = route.error

        # Phase 3 — C0: grounded retrieval + evidence shaping
        try:
            c0_raw_count, bundle = self._c0_retrieve(primary_query, inject_chunks=inject_chunks)
            c0_shaped_count = len(bundle.ranked_chunks)
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as _c0_exc:
            c0_error = str(_c0_exc)
            _log.error(
                "[GovernedAppRunner._c0] retrieval failed app=%s: %s",
                self.APP_NAME,
                _c0_exc,
            )

        # Phase 4a — L2 chokepoint. Under STRICT_GOVERNANCE this is mandatory;
        # default (legacy) mode preserves best-effort fallback so production
        # deployments without the L2 surface continue to work.
        _l2_ctx: Any = _AppContext(run_id=run_id)
        try:
            from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
                ActionClass,
                ExecutionContext,
            )
            from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (  # noqa: PLC0415
                authorize_and_execute,
            )
            import hashlib as _hl  # noqa: PLC0415

            _policy_hash = _hl.sha256(f"{self.APP_NAME}:{query}".encode("utf-8")).hexdigest()
            _execution_ctx = ExecutionContext.create(
                run_id=run_id,
                capability_token=self.CAPABILITY_TOKEN,
                policy_hash=_policy_hash,
                execution_input=query,
                execution_target=f"{self.APP_NAME}.governed_e2e",
                action_class=ActionClass.READ_ONLY,
                trace_id=run_id,
            )
            _, _l2_ctx = authorize_and_execute(
                _execution_ctx,
                lambda _payload: {"query": _payload, "status": "execution_complete"},
                self.CAPABILITY_TOKEN,
                query,
                target_name=f"{self.APP_NAME}.governed_e2e",
                safety_plane_available=True,
            )
            l2_executed = True
        except (ImportError, RuntimeError, ValueError, AttributeError) as _l2_exc:
            l2_error = str(_l2_exc)
            _log.warning(
                "[GovernedAppRunner._l2] chokepoint skipped app=%s: %s",
                self.APP_NAME,
                _l2_exc,
            )

        # Phase 4b — L5 exit gate (evaluate_and_emit). Skipped when C0 produced
        # no bundle. Phase-scoped catch surfaces the failure without masking
        # earlier phases' errors.
        # W2.1: snapshot L6 ingest queue sizes BEFORE L5 so we can detect a
        # real receipt (delta > 0) rather than relying on "queue non-empty"
        # which could be stale state from prior runs.
        _pre_l5_async_qsize = 0
        _pre_l5_shadow_qsize = 0
        try:
            from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (  # noqa: PLC0415
                get_async_eval_ingester as _pre_l5_get_async,
                get_shadow_eval_ingester as _pre_l5_get_shadow,
            )

            _pre_l5_async_qsize = _pre_l5_get_async().qsize()
            _pre_l5_shadow_qsize = _pre_l5_get_shadow().qsize()
        except (ImportError, AttributeError):
            # L6 module unavailable in this build — will be flagged by Phase 5
            pass

        if bundle is not None:
            try:
                from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (  # noqa: PLC0415
                    evaluate_and_emit,
                )

                gate_result, disposition = evaluate_and_emit(
                    bundle, _l2_ctx, tool_name=f"{self.APP_NAME}.governed_e2e"
                )
                gate_disposition = str(gate_result.disposition.value).lower()
                disposition_str = (
                    str(disposition.value).lower()
                    if hasattr(disposition, "value")
                    else str(disposition).lower()
                )
                grounded = bool(gate_result.dimensions.grounded_replayable)
                citation_count = len(bundle.citation_anchors)
                support_coverage = (
                    sum(c.combined_score for c in bundle.ranked_chunks) / len(bundle.ranked_chunks)
                    if bundle.ranked_chunks
                    else 0.0
                )
            except (ImportError, RuntimeError, TypeError, ValueError, AttributeError) as _l5_exc:
                l5_error = str(_l5_exc)
                _log.error(
                    "[GovernedAppRunner._l5] exit gate failed app=%s: %s",
                    self.APP_NAME,
                    _l5_exc,
                )
        else:
            l5_error = "skipped: no evidence bundle from C0"

        # Phase 5 — L6 observability ingest, receipt-based (W2.1).
        # We can't take a true "packet receipt" because evaluate_and_emit does
        # not surface the packet_id it generates internally. Instead we use a
        # delta-snapshot: if the L6 ingest queue advanced during L5 execution,
        # this call caused the ingest. This is a stronger signal than the
        # prior "qsize() > 0" heuristic which could read stale state.
        try:
            from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (  # noqa: PLC0415
                get_async_eval_ingester,
                get_shadow_eval_ingester,
            )

            post_async_qsize = get_async_eval_ingester().qsize()
            post_shadow_qsize = get_shadow_eval_ingester().qsize()
            async_delta = post_async_qsize - _pre_l5_async_qsize
            shadow_delta = post_shadow_qsize - _pre_l5_shadow_qsize
            if async_delta > 0 or shadow_delta > 0:
                l6_ingested = True
            else:
                # L5 ran but no packet enqueued. evaluate_and_emit has a
                # silent-swallow guardian for the enqueue path; this surfaces it.
                l6_ingested = False
                if not l5_error and bundle is not None:
                    l6_error = (
                        "L5 evaluate_and_emit succeeded but no eval packet enqueued "
                        "(async_delta=0, shadow_delta=0) — silent_swallow_in_eval_bridge"
                    )
                else:
                    l6_error = "L6 ingest skipped: L5 did not run"
        except (ImportError, AttributeError) as _l6_exc:
            # Module missing in this build. Under strict mode this becomes a
            # contract violation; in legacy mode we report the error but keep
            # the run completing so production deployments without the L6
            # surface continue to work.
            l6_error = str(_l6_exc)
            l6_ingested = False

        # Phase 6 — W5: Runtime HITL step [5]. Per ADR-023 §3.2 this runs AFTER
        # L5 seal and BEFORE any UWG invocation. Flag-off default = no-op.
        try:
            hitl_result = self._maybe_escalate_hitl(
                run_id=run_id,
                query=query,
                gate_disposition=gate_disposition,
                grounded=grounded,
                citation_count=citation_count,
                support_coverage=support_coverage,
                disposition=disposition_str,
            )
            hitl_action = hitl_result.action.value.lower()
            hitl_class_str = hitl_result.hitl_class
            hitl_ledger_id = hitl_result.ledger_id
            hitl_enabled = hitl_result.enabled
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError) as _hitl_exc:
            hitl_error = str(_hitl_exc)
            _log.error(
                "[GovernedAppRunner._hitl] escalation failed app=%s: %s",
                self.APP_NAME,
                _hitl_exc,
            )

        # W2.2: STRICT_GOVERNANCE — promote L2/L5/L6 from best-effort to mandatory.
        # Aggregate ``error`` is rebuilt from the first failed mandatory phase.
        # When strict mode is enabled, also raise GovernanceContractViolation so
        # the failure is loud in dev/CI; production paths set the flag to off and
        # see only the structured error field.
        _strict = _strict_governance_enabled()
        # Order of severity for surfacing in aggregate ``error``:
        # mandatory phases first (L2/L5/L6), then best-effort (L1/L0/C0/HITL).
        _phase_errors = (
            ("L2", l2_error, True),
            ("L5", l5_error, True),
            ("L6", l6_error, True),
            ("L1", l1_error, False),
            ("L0", l0_error, False),
            ("C0", c0_error, False),
            ("HITL", hitl_error, False),
        )
        _strict_violator: tuple[str, str] | None = None
        for _phase, _msg, _mandatory in _phase_errors:
            if not _msg:
                continue
            if _mandatory:
                if not error:
                    error = f"[{_phase}] {_msg}"
                if _strict and _strict_violator is None:
                    _strict_violator = (_phase, _msg)
            else:
                # Best-effort phases surface in aggregate only when no mandatory
                # phase already failed (mandatory takes precedence).
                if not error:
                    error = f"[{_phase}] {_msg}"

        record = GovernedAppRunRecord(
            run_id=run_id,
            app_name=self.APP_NAME,
            query=query,
            l1_sub_queries=plan.sub_queries,
            l1_fallback=plan.fallback_used,
            l0_intent=route.intent,
            l0_target=route.target_name,
            l0_confidence=route.confidence,
            l0_fallback=route.fallback_used,
            c0_raw_count=c0_raw_count,
            c0_shaped_count=c0_shaped_count,
            c0_collection=self._collection,
            disposition=disposition_str,
            gate_disposition=gate_disposition,
            grounded=grounded,
            citation_count=citation_count,
            support_coverage=round(support_coverage, 4),
            l6_ingested=l6_ingested,
            l2_executed=l2_executed,
            error=error,
            l1_error=l1_error,
            l0_error=l0_error,
            c0_error=c0_error,
            l2_error=l2_error,
            l5_error=l5_error,
            l6_error=l6_error,
            hitl_error=hitl_error,
            hitl_action=hitl_action,
            hitl_class=hitl_class_str,
            hitl_ledger_id=hitl_ledger_id,
            hitl_enabled=hitl_enabled,
        )

        # W2.2: under STRICT_GOVERNANCE raise the structured violation so dev/CI
        # see the failure as a loud exception while production keeps reading the
        # error field. The record is attached to the exception for inspection.
        if _strict_violator is not None:
            _phase, _msg = _strict_violator
            raise GovernanceContractViolation(_phase, _msg, record=record)

        return record

    # ------------------------------------------------------------------
    # Runtime HITL hook (W5)
    # ------------------------------------------------------------------

    def _maybe_escalate_hitl(
        self,
        *,
        run_id: str,
        query: str,
        gate_disposition: str,
        grounded: bool,
        citation_count: int,
        support_coverage: float,
        disposition: str,
        policy_overrides: Mapping[str, Any] | None = None,
    ) -> HitlResult:
        """Build envelope, call :func:`classify_exit`, return the outcome.

        Subclasses MAY override to stamp app-specific envelope fields (e.g.
        apps_lic may set ``is_regulated=True`` under compliance mode) via
        ``policy_overrides``. The default delegates to
        :func:`build_exit_envelope` + :func:`maybe_escalate_hitl` and relies
        on class attribute ``HITL_ENABLED`` + env flag ``RUNTIME_HITL_ENABLED``
        for flag gating. When either is off, this is a no-op returning
        ``HitlResult(action=COMMIT, enabled=False)``.

        Checkpoint payload (G7 closure): a minimal run-continuation record so
        a resume worker can reconstruct the pipeline context after approval.
        """
        envelope = build_exit_envelope(
            app_name=self.APP_NAME,
            query=query,
            gate_disposition=gate_disposition,
            grounded=grounded,
            citation_count=citation_count,
            support_coverage=support_coverage,
            disposition=disposition,
            policy_overrides=policy_overrides,
        )
        checkpoint_payload = {
            "app_name": self.APP_NAME,
            "capability_token": self.CAPABILITY_TOKEN,
            "routing_target": self.ROUTING_TARGET,
            "collection": self._collection,
            "query": query,
            "gate_disposition": gate_disposition,
            "grounded": bool(grounded),
            "citation_count": int(citation_count),
            "support_coverage": float(support_coverage),
            "disposition": disposition,
        }
        return maybe_escalate_hitl(
            app_name=self.APP_NAME,
            run_id=run_id,
            trace_id=run_id,
            envelope=envelope,
            runner_flag=bool(self.HITL_ENABLED),
            controller=self._hitl_controller,
            run_state_store=self._hitl_run_state_store,
            checkpoint_kind="pre_uwg",
            checkpoint_payload=checkpoint_payload,
        )

    # ------------------------------------------------------------------
    # Phase 1: L1 query plan
    # ------------------------------------------------------------------

    def _l1_plan(self, topic: str) -> _PlanOutput:
        """L1: decompose topic into sub-queries via query_planner.decompose_query().

        Phase-scoped failure: surfaces the exception in ``_PlanOutput.error``
        so the caller can populate ``GovernedAppRunRecord.l1_error`` rather
        than collapse it into the aggregate ``error`` field.
        """
        try:
            from agentic_core.L1_cognition.reasoning.query_planner import query_planner  # noqa: PLC0415

            planner = query_planner()
            sub_queries: list[str] = asyncio.run(planner.decompose_query(topic))
            if not sub_queries:
                sub_queries = [topic]
            return _PlanOutput(
                sub_queries=tuple(sub_queries),
                fallback_used=(sub_queries == [topic]),
            )
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning(
                "[GovernedAppRunner._l1_plan] graceful fallback app=%s: %s",
                self.APP_NAME,
                exc,
            )
            return _PlanOutput(sub_queries=(topic,), fallback_used=True, error=str(exc))

    # ------------------------------------------------------------------
    # Phase 2: L0 route decision
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # W6.2: Cached AgenticRouter — register-once, reuse across calls
    # ------------------------------------------------------------------

    def _get_router(self) -> Any:
        """Return the per-instance cached ``AgenticRouter``, initializing on first use.

        Caching the router across ``run_governed_core`` calls preserves bandit
        posterior state (per ADG hotspot G10). The router's target is
        registered exactly once on construction; subsequent calls return the
        same instance without re-registering.

        Returns ``None`` when ``AgenticRouter`` cannot be imported (minimal
        test env) — callers MUST fall back to deterministic routing.
        """
        if self._cached_router is not None:
            return self._cached_router
        try:
            from agentic_core.L0_routing.reasoning.agentic_router import AgenticRouter  # noqa: PLC0415

            router = AgenticRouter(min_confidence=0.10)

            async def _handler(user_input: str, _ctx: dict) -> dict:
                return {"handled": True, "input": user_input}

            router.register(
                self.ROUTING_TARGET,
                _handler,
                intent_keywords=self.ROUTING_KEYWORDS,
                description=f"{self.APP_NAME} governed pipeline",
            )
            self._cached_router = router
            return router
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning(
                "[GovernedAppRunner._get_router] router unavailable app=%s: %s",
                self.APP_NAME,
                exc,
            )
            return None

    def _l0_route(self, topic: str) -> _RouteOutput:
        """L0: classify intent and dispatch via AgenticRouter.route().

        Phase-scoped failure: surfaces the exception in ``_RouteOutput.error``
        so the caller can populate ``GovernedAppRunRecord.l0_error`` rather
        than collapse it into the aggregate ``error`` field.

        W6.2: Uses the per-instance cached router so bandit state accrues
        across calls.
        """
        router = self._get_router()
        if router is None:
            return _RouteOutput(
                intent=topic,
                target_name=self.ROUTING_TARGET or "unknown",
                confidence=0.5,
                fallback_used=True,
                error="AgenticRouter unavailable",
            )
        try:
            decision = asyncio.run(router.route(topic, context={"app": self.APP_NAME}))
            return _RouteOutput(
                intent=str(getattr(decision, "intent", topic)),
                target_name=str(getattr(decision, "target_name", self.ROUTING_TARGET) or self.ROUTING_TARGET),
                confidence=float(getattr(decision, "confidence", 0.0)),
                fallback_used=False,
            )
        except (RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning(
                "[GovernedAppRunner._l0_route] graceful fallback app=%s: %s",
                self.APP_NAME,
                exc,
            )
            return _RouteOutput(
                intent=topic,
                target_name=self.ROUTING_TARGET or "unknown",
                confidence=0.5,
                fallback_used=True,
                error=str(exc),
            )

    # ------------------------------------------------------------------
    # W6.1: Async-native L1 + L0 helpers (callable inside an event loop)
    # ------------------------------------------------------------------

    async def _l1_plan_async(self, topic: str) -> _PlanOutput:
        """Async-native L1: same shape as ``_l1_plan`` but ``await``s the planner.

        Use from ``run_governed_core_async`` (or any caller already running
        inside an event loop) to avoid the ``asyncio.run()`` re-entry that
        the sync variant performs.
        """
        try:
            from agentic_core.L1_cognition.reasoning.query_planner import query_planner  # noqa: PLC0415

            planner = query_planner()
            sub_queries: list[str] = await planner.decompose_query(topic)
            if not sub_queries:
                sub_queries = [topic]
            return _PlanOutput(
                sub_queries=tuple(sub_queries),
                fallback_used=(sub_queries == [topic]),
            )
        except (ImportError, RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning(
                "[GovernedAppRunner._l1_plan_async] graceful fallback app=%s: %s",
                self.APP_NAME,
                exc,
            )
            return _PlanOutput(sub_queries=(topic,), fallback_used=True, error=str(exc))

    async def _l0_route_async(self, topic: str) -> _RouteOutput:
        """Async-native L0: awaits the cached router directly.

        Same fail-open semantics as ``_l0_route`` and uses the same
        ``_get_router`` cache — bandit state propagates across both
        sync and async call paths.
        """
        router = self._get_router()
        if router is None:
            return _RouteOutput(
                intent=topic,
                target_name=self.ROUTING_TARGET or "unknown",
                confidence=0.5,
                fallback_used=True,
                error="AgenticRouter unavailable",
            )
        try:
            decision = await router.route(topic, context={"app": self.APP_NAME})
            return _RouteOutput(
                intent=str(getattr(decision, "intent", topic)),
                target_name=str(getattr(decision, "target_name", self.ROUTING_TARGET) or self.ROUTING_TARGET),
                confidence=float(getattr(decision, "confidence", 0.0)),
                fallback_used=False,
            )
        except (RuntimeError, TypeError, ValueError, AttributeError, OSError) as exc:
            _log.warning(
                "[GovernedAppRunner._l0_route_async] graceful fallback app=%s: %s",
                self.APP_NAME,
                exc,
            )
            return _RouteOutput(
                intent=topic,
                target_name=self.ROUTING_TARGET or "unknown",
                confidence=0.5,
                fallback_used=True,
                error=str(exc),
            )

    # ------------------------------------------------------------------
    # Phase 3: C0 grounded retrieval + evidence shaping
    # ------------------------------------------------------------------

    def _c0_retrieve(
        self,
        query: str,
        *,
        inject_chunks: list[Any] | None = None,
    ) -> tuple[int, Any]:
        """C0: HybridSearchEngine.search() + EvidenceShaper.shape() → (raw_count, EvidenceBundle).

        With chroma_client=None the vector leg degrades to empty results; the
        lexical leg attempts the FTS5 sidecar and returns [] on miss.  Both are
        real code paths — graceful degradation IS the expected behaviour when
        the canonical store is not populated.

        inject_chunks are appended to the real (possibly empty) raw results
        before EvidenceShaper.shape() runs the full C0 shaping pipeline.
        """
        from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (  # noqa: PLC0415
            EvidenceShaper,
        )
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (  # noqa: PLC0415
            get_hybrid_search_engine,
        )

        engine = get_hybrid_search_engine(collection_name=self._collection, top_k=10)
        try:
            raw_chunks: list[Any] = engine.search(query, collection_name=self._collection)
        except Exception as _search_exc:  # guardian: allow-broad-exception -- collection-not-found (chromadb.errors.NotFoundError) and other backend errors are not importable without hard chromadb dep at the base layer; graceful degradation to empty results is the correct path
            _log.warning(
                "[GovernedAppRunner._c0_retrieve] search degraded to empty results app=%s: %s",
                self.APP_NAME,
                _search_exc,
            )
            raw_chunks = []
        c0_raw_count = len(raw_chunks)

        all_chunks = raw_chunks + (inject_chunks or [])

        shaper = EvidenceShaper()
        bundle = shaper.shape(
            query=query,
            results=all_chunks,
            collection_name=self._collection,
            chroma_client=engine.chroma_client,
        )
        return c0_raw_count, bundle
