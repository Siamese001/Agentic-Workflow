"""Tests for the two-phase healer Protocol (04.5a INV-RC-5 enforcement).

The two-phase healer Protocol (`TwoPhaseHealerFn`) makes "no model/tool/agent
call on mismatch" structurally provable: ``resolve()`` is pure (context +
digest only); the pipeline runs the resolution-consistency gate against the
validator-side surface; ``execute()`` is invoked ONLY on a clean compare.

These tests verify the Protocol-membership dispatch and the structural
guarantee that ``execute()`` cannot run on a mismatch.
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L2_execution.observability.l2_resolution_spans import (
    clear_recorded_spans,
    recorded_spans,
)
from agentic_core.L2_execution.orchestration.l2_phase_pipeline import (
    ExecutorResult,
    HealerResolution,
    HealerResult,
    L2PhasePipeline,
    PipelineConfig,
    TwoPhaseHealerFn,
    ValidatorResult,
)
from agentic_core.L2_execution.types.l2_resolution_context import (
    L2ResolutionContext,
    RepairAuthorityClass,
    compute_resolution_digest,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    DeterminismBundle,
    HealOutcomeStamp,
    LineageRoot,
    PrepReceipt,
    ResultClass,
    TerminalStamp,
    ValidationOutcome,
)


def _build_context(
    *,
    agent_id: str = "agent-A",
    policy_hash: str = "p" * 64,
) -> L2ResolutionContext:
    return L2ResolutionContext(
        request_id="req-1",
        run_id="run-1",
        trace_id="trace-1",
        route_id="route-1",
        step_id="step-1",
        agent_id=agent_id,
        agent_type="executor",
        agent_version="1.0.0",
        agent_profile_hash="ah" + "0" * 62,
        validator_id="validator-A",
        validator_version="1.0.0",
        capability_token="cap-1",
        capability_scope_hash="c" * 64,
        sandbox_envelope_hash="s" * 64,
        policy_hash=policy_hash,
        blueprint_hash="b" * 64,
        replay_key="r" * 64,
        snapshot_manifest_hash="m" * 64,
        tool_registry_digest="td" + "0" * 62,
        model_registry_digest="md" + "0" * 62,
        provider_lane="deterministic",
        repair_authority_class=RepairAuthorityClass.LOCAL_SAFE_ONLY,
        allowed_repair_types=("retry_same_call",),
        max_repair_count=3,
        frozen_execution_context_hash="fe" + "0" * 62,
        resolver_digest="rs" + "0" * 62,
    )


def _determinism() -> DeterminismBundle:
    return DeterminismBundle(
        blueprint_hash="b" * 64,
        policy_hash="p" * 64,
        prompt_hash="ph" + "0" * 62,
        input_hash="ih" + "0" * 62,
        replay_key="r" * 64,
        attempt_seed="seed-1",
    )


def _lineage() -> LineageRoot:
    return LineageRoot(
        parent_route_id="route-parent",
        parent_plan_id="plan-1",
        parent_step_id=None,
        ancestry_chain=("root",),
    )


def _make_validator(ctx: L2ResolutionContext) -> Any:
    def _validator(_prep: PrepReceipt) -> ValidatorResult:
        return ValidatorResult(
            outcome=ValidationOutcome.PASS,
            rules_passed=("e2.signature",),
            classified_side_effect="read_only",
            validator_resolution_context=ctx,
            validator_resolution_digest=compute_resolution_digest(ctx),
        )

    return _validator


def _make_executor() -> Any:
    state = {"calls": 0}

    def _executor(_prep: PrepReceipt, _val: Any, attempt_count: int) -> ExecutorResult:
        state["calls"] += 1
        if attempt_count == 1:
            return ExecutorResult(
                result_class=ResultClass.SOFT_REPAIRABLE,
                trace_id="trace-exec-1",
                error_summary="schema_parse_error",
            )
        return ExecutorResult(
            result_class=ResultClass.SUCCESS,
            trace_id="trace-exec-2",
            output_digest="ok-digest",
        )

    return _executor


class TwoPhaseHealer:
    """Reference implementation of `TwoPhaseHealerFn`.

    Tracks resolve() / execute() call counts so tests can assert that
    execute() does NOT run on mismatch.
    """

    def __init__(
        self,
        ctx: L2ResolutionContext,
        *,
        override_ctx: L2ResolutionContext | None = None,
    ) -> None:
        # `override_ctx` lets a test pretend resolve() bound a different
        # context than the validator did, triggering a mismatch.
        self._ctx = ctx
        self._override = override_ctx
        self.resolve_calls = 0
        self.execute_calls = 0

    def resolve(self, _attempt: AttemptReceipt) -> HealerResolution:
        self.resolve_calls += 1
        used = self._override if self._override is not None else self._ctx
        return HealerResolution(
            context=used,
            digest=compute_resolution_digest(used),
        )

    def execute(self, _attempt: AttemptReceipt) -> HealerResult:
        self.execute_calls += 1
        return HealerResult(
            outcome=HealOutcomeStamp.PASS,
            reason_code="json_repair",
            delta_summary="repaired schema",
        )


@pytest.fixture(autouse=True)
def _clear_spans() -> None:
    clear_recorded_spans()


def _run(healer: Any) -> Any:
    ctx = _build_context()
    pipe = L2PhasePipeline(
        validator_fn=_make_validator(ctx),
        executor_fn=_make_executor(),
        healer_fn=healer,
        config=PipelineConfig(
            max_attempts=2,
            max_repairs=2,
            enforce_resolution_consistency=True,
        ),
    )
    return pipe.run(
        route_id="route-1",
        step_id="step-1",
        determinism=_determinism(),
        lineage=_lineage(),
    )


class TestProtocolMembership:
    """Verifies isinstance dispatch correctly distinguishes two-phase
    healers from legacy callables."""

    def test_two_phase_class_is_protocol_member(self) -> None:
        ctx = _build_context()
        healer = TwoPhaseHealer(ctx)
        assert isinstance(healer, TwoPhaseHealerFn)

    def test_plain_function_is_not_protocol_member(self) -> None:
        def legacy(_attempt: AttemptReceipt) -> HealerResult:
            return HealerResult(
                outcome=HealOutcomeStamp.PASS,
                reason_code="json_repair",
            )

        assert not isinstance(legacy, TwoPhaseHealerFn)

    def test_partial_class_with_only_resolve_is_not_protocol_member(self) -> None:
        class Partial:
            def resolve(self, _attempt: AttemptReceipt) -> HealerResolution:
                raise NotImplementedError

        assert not isinstance(Partial(), TwoPhaseHealerFn)


class TestStructuralEnforcementOfINV_RC_5:
    """The structural guarantee: on mismatch, execute() is NEVER called.

    This is the architectural property that the legacy single-callable
    path cannot offer because legacy healers couple resolution + I/O
    inside a single `__call__`.
    """

    def test_clean_compare_calls_execute_exactly_once(self) -> None:
        ctx = _build_context()
        healer = TwoPhaseHealer(ctx)
        result = _run(healer)
        assert healer.resolve_calls == 1
        assert healer.execute_calls == 1
        assert result.terminal_stamp is TerminalStamp.SUCCESS

    def test_mismatch_calls_resolve_but_NEVER_execute(self) -> None:
        validator_ctx = _build_context()
        # Healer's resolve() will return a context with different agent_id —
        # the gate MUST fail BEFORE execute() is called.
        heal_ctx = _build_context(agent_id="agent-B")
        healer = TwoPhaseHealer(validator_ctx, override_ctx=heal_ctx)
        result = _run(healer)
        # resolve() ran; execute() did NOT.
        assert healer.resolve_calls == 1
        assert healer.execute_calls == 0, (
            "INV-RC-5 violated: execute() ran despite a resolution mismatch. "
            "Two-phase enforcement is broken."
        )
        # Sealed REJECTED with the canonical terminal stamp.
        assert result.terminal_stamp is TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH
        assert result.dispatch is not None
        assert result.dispatch.user_visible_safe is False

    def test_mismatch_emits_blocked_span_with_decisive_rule_id(self) -> None:
        validator_ctx = _build_context()
        heal_ctx = _build_context(policy_hash="x" * 64)
        healer = TwoPhaseHealer(validator_ctx, override_ctx=heal_ctx)
        _run(healer)
        names = [s.name for s in recorded_spans()]
        assert "l2.heal.blocked" in names
        # Compare span carries the right field-mismatch evidence.
        compares = [s for s in recorded_spans() if s.name == "l2.resolution.compare"]
        assert len(compares) == 1
        assert compares[0].attributes["resolution_match"] is False
        assert compares[0].attributes["first_mismatched_field"] == "policy_hash"

    def test_resolve_runs_before_compare_span(self) -> None:
        """Trace order: l2.resolution.heal MUST appear before
        l2.resolution.compare. This is the observability proof of the
        gate-FIRST contract."""
        ctx = _build_context()
        healer = TwoPhaseHealer(ctx)
        _run(healer)
        order = [s.name for s in recorded_spans()]
        heal_idx = order.index("l2.resolution.heal")
        compare_idx = order.index("l2.resolution.compare")
        assert heal_idx < compare_idx, (
            f"l2.resolution.heal must precede l2.resolution.compare. "
            f"Got order: {order}"
        )


class TestLegacyPathStillEnforces:
    """Sanity check: removing the two-phase contract does not break the
    legacy advisory enforcement. Mismatch on the legacy callable path
    still seals a REJECTED outcome."""

    def test_legacy_callable_mismatch_still_seals_rejected(self) -> None:
        heal_ctx = _build_context(agent_id="agent-B")

        def legacy_healer(_attempt: AttemptReceipt) -> HealerResult:
            return HealerResult(
                outcome=HealOutcomeStamp.PASS,
                reason_code="json_repair",
                heal_resolution_context=heal_ctx,
                heal_resolution_digest=compute_resolution_digest(heal_ctx),
            )

        ctx = _build_context()
        pipe = L2PhasePipeline(
            validator_fn=_make_validator(ctx),
            executor_fn=_make_executor(),
            healer_fn=legacy_healer,
            config=PipelineConfig(
                max_attempts=2,
                max_repairs=2,
                enforce_resolution_consistency=True,
            ),
        )
        result = pipe.run(
            route_id="route-1",
            step_id="step-1",
            determinism=_determinism(),
            lineage=_lineage(),
        )
        assert result.terminal_stamp is TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH
