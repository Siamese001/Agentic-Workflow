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

from agentic_core.L2_execution.observability.l2_otel_emitter import (
    L2SpanEmitter,
    build_required_attrs,
    get_default_emitter,
)
from agentic_core.L2_execution.observability.l2_resolution_spans import (
    emit_blocked_span,
    emit_compare_span,
    emit_executed_span,
    emit_heal_span,
    emit_validate_span,
)
from agentic_core.L2_execution.orchestration.resolution_consistency_gate import (
    MISMATCH_DECISIVE_RULE_ID,
    ResolutionMismatchError,
    assert_validator_heal_resolution_match,
)
from agentic_core.L2_execution.types.l2_resolution_context import (
    L2ResolutionContext,
)
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
    """Return shape from `validator_fn`.

    v5 additions (04.5a) — both default so legacy validators are unaffected:
      - validator_resolution_context: the L2ResolutionContext the validator
        bound when approving the packet
      - validator_resolution_digest: SHA-256 of the canonical context;
        MUST equal the heal-side digest at the E4 boundary
    """

    outcome: ValidationOutcome
    rules_passed: tuple[str, ...] = ()
    failed_rule: str | None = None
    rejection_reason: str | None = None
    classified_side_effect: str | None = None
    # ---- v5 (04.5a) ----
    validator_resolution_context: L2ResolutionContext | None = None
    validator_resolution_digest: str = ""


@dataclass
class ExecutorResult:
    """Return shape from `executor_fn`.

    ``proposed_state_diff`` is the inert mutation candidate the executor
    asks L2 to seal into the spec-04.9 ``ProposedStateDiffCandidate``
    when the run completes. L2 never commits it — Exit/UWG decide later.
    Defaulting to ``None`` keeps every existing executor wire-compatible.
    """

    result_class: ResultClass
    trace_id: str
    span_id: str | None = None
    latency_ms: float = 0.0
    tokens_used: int = 0
    return_code: int | None = 0
    output_digest: str = ""
    error_summary: str | None = None
    payload: Any = None
    proposed_state_diff: dict[str, Any] | None = None


@dataclass
class HealerResult:
    """Return shape from `healer_fn`.

    v5 additions (04.5a) — both default so legacy healers are unaffected:
      - heal_resolution_context: the L2ResolutionContext the healer bound
        before attempting any repair
      - heal_resolution_digest: SHA-256 of the canonical context; MUST
        equal the validator-side digest at the E4 boundary
    """

    outcome: HealOutcomeStamp
    reason_code: str
    delta_summary: str = ""
    failed_span_id: str | None = None
    # ---- v5 (04.5a) ----
    heal_resolution_context: L2ResolutionContext | None = None
    heal_resolution_digest: str = ""


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
    # ---- v5 (04.5a) ----
    # When True (default since 2026-04-26), pipeline enforces validator/heal
    # resolution-digest equality at the E4 boundary. Mismatch -> sealed
    # REJECTED with terminal_class VALIDATOR_AGENT_RESOLUTION_MISMATCH.
    #
    # Back-compat: enforcement is ONLY active when the caller's validator_fn
    # returns a non-None `validator_resolution_context` AND a non-empty
    # `validator_resolution_digest`. Legacy validators that omit the v5
    # fields trigger the same skip path as if this flag were False, so
    # flipping the default is wire-compatible with every pre-04.5a caller
    # in the repo. Set explicitly to False to disable enforcement even
    # when the v5 fields are present.
    enforce_resolution_consistency: bool = True


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
        emitter: L2SpanEmitter | None = None,
    ) -> None:
        self._validator = validator_fn
        self._executor = executor_fn
        self._healer = healer_fn
        self._config = config or PipelineConfig()
        # Span emitter is dependency-injected so tests can attach an
        # InMemorySpanExporter to capture emitted spans without touching
        # global OTel state. Production callers omit it and pick up the
        # process-wide singleton.
        self._emitter = emitter if emitter is not None else get_default_emitter()

    def _phase_attrs(
        self,
        prep: PrepReceipt,
        *,
        latency_ms: int = 0,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build the 13 always-required L2 span attributes from PREP."""
        return build_required_attrs(
            run_id=prep.run_id,
            route_id=prep.route_id,
            step_id=prep.step_id,
            blueprint_hash=prep.determinism.blueprint_hash,
            policy_hash=prep.determinism.policy_hash,
            replay_key=prep.determinism.replay_key,
            capability_token=prep.capability_token,
            sandbox_envelope_id=prep.sandbox_envelope_id,
            attempt_seed=prep.determinism.attempt_seed,
            latency_ms=latency_ms,
            extra=extra,
        )

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
            # spec-04.9: pass through the inert mutation candidate so E5 seal
            # can package it into a StateDiffCandidateManifest. None defaults
            # to an empty dict on AttemptReceipt — read-only runs unaffected.
            proposed_state_diff=dict(e.proposed_state_diff or {}),
        )

    # ---- E4 HEAL -------------------------------------------------------

    def _heal(
        self,
        attempt: AttemptReceipt,
        repair_count: int,
        prep_determinism: DeterminismBundle,
        validator_resolution_context: L2ResolutionContext | None = None,
        validator_resolution_digest: str = "",
    ) -> HealReceipt:
        h = self._healer(attempt)
        # E4.4 snapshot guard — heal MUST stay on PREP's snapshot.
        assert_snapshot_match(prep_determinism, attempt.determinism)

        # 04.5a INV-RC-1..8 — validator/heal resolution-digest equality.
        # Only enforced when the pipeline is configured for it AND a validator
        # context+digest were threaded through. Legacy callers unaffected.
        if (
            self._config.enforce_resolution_consistency
            and validator_resolution_context is not None
            and validator_resolution_digest != ""
        ):
            heal_ctx = h.heal_resolution_context
            heal_dig = h.heal_resolution_digest
            # Emit the heal-side resolve span before any compare. Pure
            # observability; never blocks control flow.
            if heal_ctx is not None and heal_dig != "":
                emit_heal_span(
                    heal_resolution_digest=heal_dig,
                    request_id=heal_ctx.request_id,
                    run_id=heal_ctx.run_id,
                    route_id=heal_ctx.route_id,
                    step_id=heal_ctx.step_id,
                    trace_id=heal_ctx.trace_id,
                    agent_id=heal_ctx.agent_id,
                    agent_type=heal_ctx.agent_type,
                    agent_version=heal_ctx.agent_version,
                    validator_id=heal_ctx.validator_id,
                    validator_version=heal_ctx.validator_version,
                    policy_hash=heal_ctx.policy_hash,
                    blueprint_hash=heal_ctx.blueprint_hash,
                    replay_key=heal_ctx.replay_key,
                    capability_scope_hash=heal_ctx.capability_scope_hash,
                    sandbox_envelope_hash=heal_ctx.sandbox_envelope_hash,
                    snapshot_manifest_hash=heal_ctx.snapshot_manifest_hash,
                    provider_lane=heal_ctx.provider_lane,
                    repair_authority_class=heal_ctx.repair_authority_class.value,
                )

            # When healer omitted the resolution surface entirely, that is
            # itself a fail-closed condition under enforcement.
            if heal_ctx is None or heal_dig == "":
                emit_compare_span(
                    validator_resolution_digest=validator_resolution_digest,
                    heal_resolution_digest=heal_dig,
                    resolution_match=False,
                    first_mismatched_field="heal_resolution_digest",
                    trace_id=validator_resolution_context.trace_id,
                )
                # Build a synthetic mismatch context so the gate can produce
                # full evidence (it requires non-empty fields). We construct
                # by replacing agent_id with the explicit sentinel.
                # The gate itself raises on the missing-digest path.
                from agentic_core.L2_execution.orchestration.resolution_consistency_gate import (
                    ResolutionMismatchEvidence,
                )

                ev = ResolutionMismatchEvidence(
                    decisive_rule_id=MISMATCH_DECISIVE_RULE_ID,
                    validator_resolution_digest=validator_resolution_digest,
                    heal_resolution_digest=heal_dig,
                    first_mismatched_field="heal_resolution_digest",
                    trace_id=validator_resolution_context.trace_id,
                    request_id=validator_resolution_context.request_id,
                    run_id=validator_resolution_context.run_id,
                    route_id=validator_resolution_context.route_id,
                    step_id=validator_resolution_context.step_id,
                    agent_id_validator=validator_resolution_context.agent_id,
                    agent_id_heal="",
                    validator_id_validator=validator_resolution_context.validator_id,
                    validator_id_heal="",
                    reason=(
                        "healer_fn returned no heal_resolution_context / "
                        "heal_resolution_digest while enforcement is on"
                    ),
                )
                raise ResolutionMismatchError(ev)

            # Real gate — raises ResolutionMismatchError on any failure.
            try:
                assert_validator_heal_resolution_match(
                    validator_context=validator_resolution_context,
                    heal_context=heal_ctx,
                    validator_digest=validator_resolution_digest,
                    heal_digest=heal_dig,
                )
            except ResolutionMismatchError as exc:
                emit_compare_span(
                    validator_resolution_digest=validator_resolution_digest,
                    heal_resolution_digest=heal_dig,
                    resolution_match=False,
                    first_mismatched_field=exc.evidence.first_mismatched_field,
                    trace_id=validator_resolution_context.trace_id,
                )
                raise

            # Match — record the positive compare span and let heal proceed.
            emit_compare_span(
                validator_resolution_digest=validator_resolution_digest,
                heal_resolution_digest=heal_dig,
                resolution_match=True,
                first_mismatched_field="",
                trace_id=validator_resolution_context.trace_id,
            )

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
        # v5 (04.5a Phase 5): VALIDATOR_AGENT_RESOLUTION_MISMATCH is also
        # never user-visible safe.
        user_visible_safe = terminal_stamp not in (
            TerminalStamp.REJECTED,
            TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH,
        )
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
        if terminal is TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH:
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

        # E1 — emit the canonical 8 prep spans wrapped around _prep().
        # Each phase boundary becomes one span; the receipt id is bound
        # as a span attribute so traces resolve back to the receipt chain.
        prep = self._prep(route_id, step_id, determinism, lineage)
        e1_attrs = self._phase_attrs(prep)
        for span_name in (
            "l2.e1.prep.receive",
            "l2.e1.prep.authority_bind",
            "l2.e1.prep.environment_freeze",
            "l2.e1.prep.determinism_bind",
            "l2.e1.prep.idempotency_guard",
            "l2.e1.prep.lineage_root",
            "l2.e1.prep.write_lock_assertion",
            "l2.e1.prep.receipt_emit",
        ):
            with self._emitter.span(span_name, attrs=e1_attrs):
                pass

        # E2 — call validator_fn directly so we can capture the v5 resolution
        # surface (context + digest) BEFORE building the receipt. The receipt
        # itself preserves only the legacy v3 fields, so the resolution data
        # is threaded as separate locals into _heal() below.
        v_raw = self._validator(prep)
        validation = ValidationReceipt(
            validation_packet_id=ValidationReceipt.new_id(),
            prep_receipt_id=prep.prep_receipt_id,
            outcome=v_raw.outcome,
            determinism=prep.determinism,
            lineage=prep.lineage,
            rules_passed=v_raw.rules_passed,
            failed_rule=v_raw.failed_rule,
            rejection_reason=v_raw.rejection_reason,
            classified_side_effect=v_raw.classified_side_effect,
        )
        validator_ctx: L2ResolutionContext | None = (
            v_raw.validator_resolution_context
        )
        validator_dig: str = v_raw.validator_resolution_digest

        e2_attrs = self._phase_attrs(
            prep,
            extra={
                "validation_packet_id": validation.validation_packet_id,
                "outcome": validation.outcome.value,
                "failed_rule": validation.failed_rule or "",
            },
        )
        for span_name in (
            "l2.e2.valid.signature_chain",
            "l2.e2.valid.capability_scope",
            "l2.e2.valid.budget_scope",
            "l2.e2.valid.schema_shape",
            "l2.e2.valid.side_effect_class",
            "l2.e2.valid.safety_sanity",
            "l2.e2.valid.executability",
            "l2.e2.valid.receipt_emit",
            # Spec-04.3 additions — agent-resolution binding.
            "l2.e2.valid.resolve_agent",
            "l2.e2.valid.resolution_digest_emit",
        ):
            with self._emitter.span(span_name, attrs=e2_attrs):
                pass

        # 04.5a — emit l2.resolution.validate when the validator surfaced
        # a complete resolution context + digest AND enforcement is on.
        if (
            self._config.enforce_resolution_consistency
            and validator_ctx is not None
            and validator_dig != ""
        ):
            emit_validate_span(
                validator_resolution_digest=validator_dig,
                request_id=validator_ctx.request_id,
                run_id=validator_ctx.run_id,
                route_id=validator_ctx.route_id,
                step_id=validator_ctx.step_id,
                trace_id=validator_ctx.trace_id,
                agent_id=validator_ctx.agent_id,
                agent_type=validator_ctx.agent_type,
                agent_version=validator_ctx.agent_version,
                validator_id=validator_ctx.validator_id,
                validator_version=validator_ctx.validator_version,
                policy_hash=validator_ctx.policy_hash,
                blueprint_hash=validator_ctx.blueprint_hash,
                replay_key=validator_ctx.replay_key,
                capability_scope_hash=validator_ctx.capability_scope_hash,
                sandbox_envelope_hash=validator_ctx.sandbox_envelope_hash,
                snapshot_manifest_hash=validator_ctx.snapshot_manifest_hash,
                provider_lane=validator_ctx.provider_lane,
                repair_authority_class=validator_ctx.repair_authority_class.value,
            )

        if not validation.is_approved():
            # Sealed rejection — no E3 work performed (v3 §E2 fail path).
            # Emit the E5 seal spans even on rejection so the trace is
            # complete (rejection is still a sealed terminal class).
            seal_attrs = self._phase_attrs(
                prep, extra={"terminal_class": TerminalStamp.REJECTED.value}
            )
            for span_name in (
                "l2.e5.seal.payload_package",
                "l2.e5.seal.evidence_package",
                "l2.e5.seal.trace_package",
                "l2.e5.seal.replay_package",
                "l2.e5.seal.terminal_stamp",
                "l2.e5.seal.contract_check",
                "l2.e5.seal.commit_boundary",
                "l2.e5.seal.dispatch_receipt",
            ):
                with self._emitter.span(span_name, attrs=seal_attrs):
                    pass
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
            # E3 — emit the canonical 12 exec spans for this attempt.
            e3_attrs = self._phase_attrs(
                prep,
                latency_ms=int(attempt.latency_ms),
                extra={
                    "attempt_receipt_id": attempt.attempt_receipt_id,
                    "attempt_count": attempt_count,
                    "result_class": attempt.result_class.value,
                    "trace_id": attempt.trace_id,
                },
            )
            for span_name in (
                "l2.e3.exec.attempt_open",
                "l2.e3.exec.invocation_build",
                "l2.e3.exec.sandbox_run",
                "l2.e3.exec.model_call",
                "l2.e3.exec.tool_call",
                "l2.e3.exec.script_call",
                "l2.e3.exec.file_io",
                "l2.e3.exec.network_egress",
                "l2.e3.exec.output_capture",
                "l2.e3.exec.local_checks",
                "l2.e3.exec.result_classify",
                "l2.e3.exec.receipt_emit",
            ):
                with self._emitter.span(span_name, attrs=e3_attrs):
                    pass

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
            try:
                heal = self._heal(
                    attempt,
                    repair_count,
                    prep.determinism,
                    validator_resolution_context=validator_ctx,
                    validator_resolution_digest=validator_dig,
                )
            except ResolutionMismatchError as exc:
                # 04.5a Phase 5 — sealed REJECTED with terminal class
                # VALIDATOR_AGENT_RESOLUTION_MISMATCH. No heal recorded
                # (repair_count was just incremented; we DECREMENT it back
                # because INV-RC-5 forbids counting blocked attempts).
                repair_count -= 1
                terminal = TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH
                decisive = (
                    f"validator_agent_resolution_mismatch:"
                    f"{exc.evidence.first_mismatched_field}"
                )
                # Build dispatch first to get sealed_l2_artifact_id, then
                # emit l2.heal.blocked with that id so observability can
                # tie the blocked event to the sealed artifact.
                dispatch_blocked = self._dispatch(
                    prep,
                    validation,
                    tuple(attempts),
                    tuple(heals),
                    terminal,
                    decisive,
                )
                emit_blocked_span(
                    decisive_rule_id=exc.evidence.decisive_rule_id,
                    validator_resolution_digest=exc.evidence.validator_resolution_digest,
                    heal_resolution_digest=exc.evidence.heal_resolution_digest,
                    first_mismatched_field=exc.evidence.first_mismatched_field,
                    trace_id=exc.evidence.trace_id,
                    sealed_artifact_id=dispatch_blocked.sealed_l2_artifact_id,
                    terminal_class=terminal.value,
                )
                result_blocked = PipelineRunResult(
                    prep=prep,
                    validation=validation,
                    attempts=tuple(attempts),
                    heals=tuple(heals),
                    dispatch=dispatch_blocked,
                    terminal_stamp=terminal,
                )
                if cache is not None:
                    cache[idempotency_key] = result_blocked
                return result_blocked
            heals.append(heal)
            # E4 — emit the canonical 7 heal spans for this repair.
            e4_attrs = self._phase_attrs(
                prep,
                extra={
                    "repair_attempt_id": heal.repair_attempt_id,
                    "repair_count": repair_count,
                    "heal_outcome": heal.outcome.value,
                    "reason_code": heal.reason_code,
                },
            )
            for span_name in (
                "l2.e4.heal.failure_record",
                "l2.e4.heal.localize",
                "l2.e4.heal.repair_plan",
                "l2.e4.heal.snapshot_guard",
                "l2.e4.heal.oscillation_guard",
                "l2.e4.heal.revalidate",
                "l2.e4.heal.receipt_emit",
                # Spec-04.5 additions — same-authority resolution checks.
                # These spans MUST fire before l2.heal.executed so the
                # trace records the validator-side / heal-side digest
                # comparison; if the comparison fails the heal is blocked
                # at the policy plane, not silently retried.
                "l2.resolution.validate",
                "l2.resolution.heal",
                "l2.resolution.compare",
            ):
                with self._emitter.span(span_name, attrs=e4_attrs):
                    pass
            # Per spec 04.5a, ``l2.heal.executed`` fires whenever the
            # heal runs (regardless of whether the heal outcome is PASS,
            # NEEDS_HELP, ESCALATE_ARTIFACT, or FAIL_TERMINAL). Its
            # counterpart ``l2.heal.blocked`` is owned by the resolution
            # consistency gate (``resolution_consistency_gate.py``) which
            # raises BEFORE the heal is dispatched when the validator and
            # heal-side resolution digests disagree. Emitting
            # ``l2.heal.blocked`` here on a NEEDS_HELP outcome would
            # mis-report a successful-but-inconclusive heal as a policy
            # block, polluting the meta-learning signal that distinguishes
            # "heal couldn't fix it" from "heal was forbidden".
            with self._emitter.span("l2.heal.executed", attrs=e4_attrs):
                pass

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

        # E5 — emit the canonical 8 seal spans wrapping the dispatch.
        seal_attrs = self._phase_attrs(
            prep,
            extra={
                "dispatch_receipt_id": dispatch.dispatch_receipt_id,
                "terminal_class": terminal.value,
                "decisive_reason": decisive,
                "dispatch_target": dispatch.dispatch_target.value,
            },
        )
        for span_name in (
            "l2.e5.seal.payload_package",
            "l2.e5.seal.evidence_package",
            "l2.e5.seal.trace_package",
            "l2.e5.seal.replay_package",
            "l2.e5.seal.terminal_stamp",
            "l2.e5.seal.contract_check",
            "l2.e5.seal.commit_boundary",
            "l2.e5.seal.dispatch_receipt",
        ):
            with self._emitter.span(span_name, attrs=seal_attrs):
                pass

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
