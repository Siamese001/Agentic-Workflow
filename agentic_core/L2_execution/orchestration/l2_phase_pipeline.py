"""L2 Phase Pipeline — v3 doctrine end-to-end orchestrator.

Implements the v3 spec's E1→E2→E3→E4→E5 sequence with one named, sealed
receipt emitted at each phase boundary:

    E1 PREP  ──► PrepReceipt           (E1.8)
    E2 VALID ──► ValidationReceipt     (E2.8)  PASS or FAIL (sealed reject)
    E3 EXEC  ──► AttemptReceipt        (E3.8)  one per attempt
    E4 HEAL  ──► HealReceipt           (E4.7)  one per repair attempt
    E5 SEAL  ──► DispatchReceipt       (E5.8)  one terminal handoff

Adapter pattern only
--------------------
This module deliberately does NOT import the heavy L2 agents (SovereignBaseAgent,
the c8e4f1 split bases, etc.). It accepts user-supplied `validator_fn`,
`executor_fn`, and `healer_fn` callables so the pipeline can be unit-tested
without a full L2 stack and so existing wrappers (`l2_agent_wrappers`,
`call_interceptor`) can adopt it incrementally.

Snapshot binding
----------------
The DeterminismBundle frozen at PREP is the authority. Every downstream
phase MUST present an identical (blueprint_hash, policy_hash) pair. The
pipeline calls `assert_snapshot_match` and raises SnapshotMismatchError if
violated — closes v3 §E1/E2/E4 invariant.

No durable commit
-----------------
The pipeline never writes to L4 / UWG. The DispatchReceipt enforces
`has_commit_payload=False` at construction.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    DeterminismBundle,
    DispatchReceipt,
    DispatchTarget,
    HealOutcomeStamp,
    HealReceipt,
    LineageRoot,
    PrepReceipt,
    ResultClass,
    SnapshotMismatchError,
    TerminalStamp,
    ValidationOutcome,
    ValidationReceipt,
    assert_snapshot_match,
)
from agentic_core.L2_execution.types.l2_v4_invariants import (
    derive_dispatch_target,
)

# ---------------------------------------------------------------------------
# Adapter result shapes — what user-supplied callables must return.
# ---------------------------------------------------------------------------


@dataclass
class ValidatorResult:
    """Return shape from `validator_fn`."""

    outcome: ValidationOutcome
    rules_passed: tuple[str, ...] = ()
    failed_rule: str | None = None
    rejection_reason: str | None = None
    classified_side_effect: str | None = None


@dataclass
class ExecutorResult:
    """Return shape from `executor_fn`."""

    result_class: ResultClass
    trace_id: str
    span_id: str | None = None
    latency_ms: float = 0.0
    tokens_used: int = 0
    return_code: int | None = 0
    output_digest: str = ""
    error_summary: str | None = None
    payload: Any = None


@dataclass
class HealerResult:
    """Return shape from `healer_fn`."""

    outcome: HealOutcomeStamp
    reason_code: str
    delta_summary: str = ""
    failed_span_id: str | None = None


# ---------------------------------------------------------------------------
# Pipeline configuration.
# ---------------------------------------------------------------------------


@dataclass
class PipelineConfig:
    """Static configuration for one L2PhasePipeline run.

    v4 additions:
      - is_l3_managed: drives DispatchTarget.L3_MERGE routing
      - allow_degraded: permits DEGRADED_SUCCESS terminal stamp
      - duplicate_cache: optional dict for E1.5 sealed-receipt return
    """

    max_attempts: int = 3
    max_repairs: int = 3
    capability_token: str = "cap-token-default"
    compliance_hash: str = "compliance-hash-default"
    sandbox_envelope_id: str = "sandbox-envelope-default"
    frozen_caps: tuple[str, ...] = ()
    frozen_budget: dict[str, Any] = field(default_factory=dict)
    # ---- v4 additions ----
    is_l3_managed: bool = False
    allow_degraded: bool = True
    duplicate_cache: dict[str, PipelineRunResult] | None = None


# ---------------------------------------------------------------------------
# Pipeline run output.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PipelineRunResult:
    """Ordered receipt sequence from one pipeline run.

    `dispatch` is None when the run rejected at E2 — the rejection itself is
    sealed in `validation`, no E3 attempts happened, and no E5 dispatch is
    issued (per v3 §E2 fail path).
    """

    prep: PrepReceipt
    validation: ValidationReceipt
    attempts: tuple[AttemptReceipt, ...]
    heals: tuple[HealReceipt, ...]
    dispatch: DispatchReceipt | None
    terminal_stamp: TerminalStamp


# ---------------------------------------------------------------------------
# The pipeline.
# ---------------------------------------------------------------------------


class L2PhasePipeline:
    """v3 E1→E5 orchestrator with named receipts at every boundary.

    Usage
    -----
    >>> pipe = L2PhasePipeline(
    ...     validator_fn=my_validator,
    ...     executor_fn=my_executor,
    ...     healer_fn=my_healer,
    ...     config=PipelineConfig(max_attempts=3, max_repairs=2),
    ... )
    >>> result = pipe.run(
    ...     route_id="route-123",
    ...     step_id="step-1",
    ...     determinism=my_determinism_bundle,
    ...     lineage=my_lineage_root,
    ... )
    >>> assert result.terminal_stamp is TerminalStamp.SUCCESS
    """

    def __init__(
        self,
        validator_fn: Callable[[PrepReceipt], ValidatorResult],
        executor_fn: Callable[[PrepReceipt, ValidationReceipt, int], ExecutorResult],
        healer_fn: Callable[[AttemptReceipt], HealerResult],
        config: PipelineConfig | None = None,
    ) -> None:
        self._validator = validator_fn
        self._executor = executor_fn
        self._healer = healer_fn
        self._config = config or PipelineConfig()

    # ---- E1 PREP -------------------------------------------------------

    def _prep(
        self,
        route_id: str,
        step_id: str | None,
        determinism: DeterminismBundle,
        lineage: LineageRoot,
    ) -> PrepReceipt:
        run_id = f"run-{uuid.uuid4().hex}"
        idempotency_key = f"idem-{determinism.input_hash}-{determinism.attempt_seed}"
        return PrepReceipt(
            prep_receipt_id=PrepReceipt.new_id(),
            run_id=run_id,
            idempotency_key=idempotency_key,
            route_id=route_id,
            step_id=step_id,
            capability_token=self._config.capability_token,
            compliance_hash=self._config.compliance_hash,
            sandbox_envelope_id=self._config.sandbox_envelope_id,
            determinism=determinism,
            lineage=lineage,
            frozen_caps=self._config.frozen_caps,
            frozen_budget=dict(self._config.frozen_budget),
            frozen_at=time.monotonic(),
        )

    # ---- E2 VALID ------------------------------------------------------

    def _validate(self, prep: PrepReceipt) -> ValidationReceipt:
        v = self._validator(prep)
        return ValidationReceipt(
            validation_packet_id=ValidationReceipt.new_id(),
            prep_receipt_id=prep.prep_receipt_id,
            outcome=v.outcome,
            determinism=prep.determinism,
            lineage=prep.lineage,
            rules_passed=v.rules_passed,
            failed_rule=v.failed_rule,
            rejection_reason=v.rejection_reason,
            classified_side_effect=v.classified_side_effect,
        )

    # ---- E3 EXEC -------------------------------------------------------

    def _attempt(
        self,
        prep: PrepReceipt,
        validation: ValidationReceipt,
        attempt_count: int,
    ) -> AttemptReceipt:
        e = self._executor(prep, validation, attempt_count)
        # Snapshot guard — c8e4f1 W1 invariant.
        # Executor must report into the same determinism bundle as PREP for
        # snapshot fields. We re-use PREP's bundle here (executors do not get
        # to mutate snapshot binding) but verify via assert_snapshot_match in
        # the heal path where drift is more likely.
        return AttemptReceipt(
            attempt_receipt_id=AttemptReceipt.new_id(),
            validation_packet_id=validation.validation_packet_id,
            attempt_count=attempt_count,
            determinism=prep.determinism,
            lineage=prep.lineage,
            trace_id=e.trace_id,
            span_id=e.span_id,
            latency_ms=e.latency_ms,
            tokens_used=e.tokens_used,
            return_code=e.return_code,
            result_class=e.result_class,
            output_digest=e.output_digest,
            error_summary=e.error_summary,
        )

    # ---- E4 HEAL -------------------------------------------------------

    def _heal(
        self,
        attempt: AttemptReceipt,
        repair_count: int,
        prep_determinism: DeterminismBundle,
    ) -> HealReceipt:
        h = self._healer(attempt)
        # E4.4 snapshot guard — heal MUST stay on PREP's snapshot.
        assert_snapshot_match(prep_determinism, attempt.determinism)
        return HealReceipt(
            repair_attempt_id=HealReceipt.new_id(),
            parent_attempt_receipt_id=attempt.attempt_receipt_id,
            failed_span_id=h.failed_span_id or attempt.span_id,
            reason_code=h.reason_code,
            repair_count=repair_count,
            determinism=attempt.determinism,
            lineage=attempt.lineage,
            delta_summary=h.delta_summary,
            outcome=h.outcome,
        )

    # ---- E5 SEAL -------------------------------------------------------

    def _dispatch(
        self,
        prep: PrepReceipt,
        validation: ValidationReceipt | None,
        attempts: tuple[AttemptReceipt, ...],
        heals: tuple[HealReceipt, ...],
        terminal_stamp: TerminalStamp,
        decisive_reason: str,
    ) -> DispatchReceipt:
        # v4: derive dispatch_target from terminal class + L3 context.
        last_attempt = attempts[-1] if attempts else None
        commit_requested = bool(
            last_attempt and last_attempt.proposed_state_diff
        )
        dispatch_target: DispatchTarget = derive_dispatch_target(
            is_l3_managed=self._config.is_l3_managed,
            terminal=terminal_stamp,
            commit_requested=commit_requested,
        )
        # v4: REJECTED is never user-visible safe.
        user_visible_safe = terminal_stamp is not TerminalStamp.REJECTED
        downstream_recommendation = self._recommend_downstream(
            terminal_stamp, decisive_reason
        )
        return DispatchReceipt(
            dispatch_receipt_id=DispatchReceipt.new_id(),
            sealed_l2_artifact_id=f"sealed-{uuid.uuid4().hex}",
            terminal_stamp=terminal_stamp,
            determinism=prep.determinism,
            lineage=prep.lineage,
            prep_receipt_id=prep.prep_receipt_id,
            validation_packet_id=(
                validation.validation_packet_id if validation else None
            ),
            attempt_receipt_ids=tuple(a.attempt_receipt_id for a in attempts),
            heal_receipt_ids=tuple(h.repair_attempt_id for h in heals),
            decisive_reason=decisive_reason,
            has_commit_payload=False,  # invariant
            dispatch_target=dispatch_target,
            user_visible_safe=user_visible_safe,
            commit_requested=commit_requested,
            downstream_recommendation=downstream_recommendation,
        )

    @staticmethod
    def _recommend_downstream(
        terminal: TerminalStamp, decisive: str
    ) -> str:
        """v4 §E5.5 downstream_recommendation hint string."""
        if terminal is TerminalStamp.SUCCESS:
            return "allow"
        if terminal is TerminalStamp.DEGRADED_SUCCESS:
            return "allow_with_caveats"
        if terminal is TerminalStamp.NEEDS_HELP:
            return "escalate"
        if terminal is TerminalStamp.REJECTED:
            return "deny"
        return f"deny:{decisive}"

    # ---- public entrypoint --------------------------------------------

    def run(
        self,
        route_id: str,
        step_id: str | None,
        determinism: DeterminismBundle,
        lineage: LineageRoot,
    ) -> PipelineRunResult:
        """Execute the full v3/v4 phase pipeline once.

        Returns a frozen `PipelineRunResult` carrying every receipt emitted.
        Raises `SnapshotMismatchError` if any phase drifts off PREP's snapshot.

        v4 §E1.5: when a duplicate_cache is configured and the derived
        idempotency_key already has a sealed prior result, the prior result is
        returned instead of re-executing.
        """
        # E1.5 duplicate guard (v4) — derive idempotency_key the same way
        # _prep() does, then check the cache before doing any work.
        idempotency_key = (
            f"idem-{determinism.input_hash}-{determinism.attempt_seed}"
        )
        cache = self._config.duplicate_cache
        if cache is not None and idempotency_key in cache:
            return cache[idempotency_key]

        # E1
        prep = self._prep(route_id, step_id, determinism, lineage)

        # E2
        validation = self._validate(prep)
        if not validation.is_approved():
            # Sealed rejection — no E3 work performed (v3 §E2 fail path).
            return PipelineRunResult(
                prep=prep,
                validation=validation,
                attempts=(),
                heals=(),
                dispatch=None,
                terminal_stamp=TerminalStamp.REJECTED,
            )

        attempts: list[AttemptReceipt] = []
        heals: list[HealReceipt] = []
        attempt_count = 0
        repair_count = 0
        terminal: TerminalStamp = TerminalStamp.FAILURE
        decisive: str = "exhausted_without_terminal"

        while attempt_count < self._config.max_attempts:
            attempt_count += 1
            attempt = self._attempt(prep, validation, attempt_count)
            attempts.append(attempt)

            if attempt.result_class is ResultClass.SUCCESS:
                terminal = TerminalStamp.SUCCESS
                decisive = "attempt_succeeded"
                break
            if attempt.result_class is ResultClass.DEGRADED_SUCCESS:
                # v4 §E3.7: usable partial result with caveats.
                terminal = (
                    TerminalStamp.DEGRADED_SUCCESS
                    if self._config.allow_degraded
                    else TerminalStamp.NEEDS_HELP
                )
                decisive = "attempt_degraded_success"
                break
            if attempt.result_class is ResultClass.FAIL_TERMINAL:
                terminal = TerminalStamp.FAILURE
                decisive = f"fail_terminal:{attempt.error_summary or 'unknown'}"
                break
            if attempt.result_class is ResultClass.REJECTED:
                terminal = TerminalStamp.REJECTED
                decisive = "executor_rejected"
                break
            if attempt.result_class is ResultClass.NEEDS_HELP:
                terminal = TerminalStamp.NEEDS_HELP
                decisive = "executor_needs_help"
                break

            # SOFT_REPAIRABLE — try heal.
            if repair_count >= self._config.max_repairs:
                terminal = TerminalStamp.FAILURE
                decisive = "repair_ceiling_reached"
                break
            repair_count += 1
            heal = self._heal(attempt, repair_count, prep.determinism)
            heals.append(heal)

            if heal.outcome is HealOutcomeStamp.PASS:
                # Loop back to E3 with another attempt.
                continue
            if heal.outcome is HealOutcomeStamp.NEEDS_HELP:
                terminal = TerminalStamp.NEEDS_HELP
                decisive = f"heal_needs_help:{heal.reason_code}"
                break
            if heal.outcome is HealOutcomeStamp.ESCALATE_ARTIFACT:
                terminal = TerminalStamp.NEEDS_HELP
                decisive = f"heal_escalate:{heal.reason_code}"
                break
            # FAIL_TERMINAL
            terminal = TerminalStamp.FAILURE
            decisive = f"heal_fail_terminal:{heal.reason_code}"
            break

        # E5
        dispatch = self._dispatch(
            prep,
            validation,
            tuple(attempts),
            tuple(heals),
            terminal,
            decisive,
        )

        result = PipelineRunResult(
            prep=prep,
            validation=validation,
            attempts=tuple(attempts),
            heals=tuple(heals),
            dispatch=dispatch,
            terminal_stamp=terminal,
        )

        # E1.5 v4: register sealed result in duplicate cache.
        if cache is not None:
            cache[idempotency_key] = result

        return result


__all__ = [
    "ValidatorResult",
    "ExecutorResult",
    "HealerResult",
    "PipelineConfig",
    "PipelineRunResult",
    "L2PhasePipeline",
    "SnapshotMismatchError",
]
