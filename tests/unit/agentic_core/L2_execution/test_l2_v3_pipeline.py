"""End-to-end tests for the v3 L2 phase pipeline (E1→E2→E3→E4→E5).

Verifies:
    - SUCCESS path emits prep + validation + 1 attempt + 0 heals + dispatch
    - REJECT path emits prep + validation only (no attempts, no dispatch)
    - SOFT_REPAIRABLE→HEAL→PASS→SUCCESS produces the receipt sequence
    - Repair ceiling closes the loop deterministically
    - Snapshot mismatch raises SnapshotMismatchError
    - DispatchReceipt invariant: never carries commit payload
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.orchestration.l2_phase_pipeline import (
    ExecutorResult,
    HealerResult,
    L2PhasePipeline,
    PipelineConfig,
    ValidatorResult,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    DeterminismBundle,
    HealOutcomeStamp,
    LineageRoot,
    PrepReceipt,
    ResultClass,
    SnapshotMismatchError,
    TerminalStamp,
    ValidationOutcome,
)

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def determinism() -> DeterminismBundle:
    return DeterminismBundle(
        blueprint_hash="bp-1",
        policy_hash="pol-1",
        prompt_hash="pr-1",
        input_hash="in-1",
        replay_key="rk-1",
        attempt_seed="seed-1",
    )


@pytest.fixture
def lineage() -> LineageRoot:
    return LineageRoot(
        parent_route_id="route-1",
        parent_plan_id="plan-1",
        parent_step_id="step-1",
        ancestry_chain=("route-0",),
        same_run_packet_family="fam-1",
    )


def _approve(_prep: PrepReceipt) -> ValidatorResult:
    return ValidatorResult(
        outcome=ValidationOutcome.PASS,
        rules_passed=("schema", "capability", "budget"),
        classified_side_effect="READ",
    )


def _reject(_prep: PrepReceipt) -> ValidatorResult:
    return ValidatorResult(
        outcome=ValidationOutcome.FAIL,
        failed_rule="capability_scope",
        rejection_reason="tool out of scope",
    )


def _success_executor(_p, _v, _n) -> ExecutorResult:  # type: ignore[no-untyped-def]
    return ExecutorResult(
        result_class=ResultClass.SUCCESS,
        trace_id=f"trace-{_n}",
        span_id=f"span-{_n}",
        latency_ms=10.0,
        tokens_used=20,
        return_code=0,
        output_digest="ok-sha",
    )


def _terminal_failure_executor(_p, _v, _n) -> ExecutorResult:  # type: ignore[no-untyped-def]
    return ExecutorResult(
        result_class=ResultClass.FAIL_TERMINAL,
        trace_id=f"trace-{_n}",
        latency_ms=5.0,
        return_code=1,
        error_summary="hard failure",
    )


def _needs_help_executor(_p, _v, _n) -> ExecutorResult:  # type: ignore[no-untyped-def]
    return ExecutorResult(
        result_class=ResultClass.NEEDS_HELP,
        trace_id=f"trace-{_n}",
        latency_ms=5.0,
        return_code=2,
        error_summary="ambiguous",
    )


def _no_heal(_attempt) -> HealerResult:  # type: ignore[no-untyped-def]
    return HealerResult(
        outcome=HealOutcomeStamp.NEEDS_HELP,
        reason_code="unhealable",
    )


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------


class TestSuccessPath:
    def test_emits_full_receipt_sequence(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        assert result.terminal_stamp is TerminalStamp.SUCCESS
        assert len(result.attempts) == 1
        assert result.attempts[0].result_class is ResultClass.SUCCESS
        assert len(result.heals) == 0
        assert result.dispatch is not None
        assert result.dispatch.terminal_stamp is TerminalStamp.SUCCESS
        assert result.dispatch.decisive_reason == "attempt_succeeded"

    def test_dispatch_links_full_chain(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        d = r.dispatch
        assert d is not None
        assert d.prep_receipt_id == r.prep.prep_receipt_id
        assert d.validation_packet_id == r.validation.validation_packet_id
        assert d.attempt_receipt_ids == (r.attempts[0].attempt_receipt_id,)
        assert d.heal_receipt_ids == ()
        assert not d.has_commit_payload


class TestRejectPath:
    def test_e2_fail_emits_no_attempts_no_dispatch(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_reject,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        assert result.terminal_stamp is TerminalStamp.REJECTED
        assert result.validation.failed_rule == "capability_scope"
        assert result.attempts == ()
        assert result.heals == ()
        assert result.dispatch is None


class TestHealLoop:
    def test_soft_repairable_then_pass_then_success(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        # First attempt soft-repairable, second attempt success.
        call_count = {"n": 0}

        def stage_executor(_p, _v, n):  # type: ignore[no-untyped-def]
            call_count["n"] = n
            if n == 1:
                return ExecutorResult(
                    result_class=ResultClass.SOFT_REPAIRABLE,
                    trace_id=f"trace-{n}",
                    latency_ms=5.0,
                    return_code=3,
                    error_summary="schema drift",
                )
            return ExecutorResult(
                result_class=ResultClass.SUCCESS,
                trace_id=f"trace-{n}",
                latency_ms=5.0,
                return_code=0,
                output_digest="ok",
            )

        def heal_pass(_attempt):  # type: ignore[no-untyped-def]
            return HealerResult(
                outcome=HealOutcomeStamp.PASS,
                reason_code="schema_normalized",
                delta_summary="re-keyed",
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=stage_executor,
            healer_fn=heal_pass,
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.terminal_stamp is TerminalStamp.SUCCESS
        assert len(r.attempts) == 2
        assert r.attempts[0].result_class is ResultClass.SOFT_REPAIRABLE
        assert r.attempts[1].result_class is ResultClass.SUCCESS
        assert len(r.heals) == 1
        assert r.heals[0].outcome is HealOutcomeStamp.PASS
        assert r.dispatch is not None
        assert r.dispatch.heal_receipt_ids == (r.heals[0].repair_attempt_id,)

    def test_repair_ceiling_terminates_loop(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        # Always soft-repairable; healer always passes; ceiling stops it.
        def soft_executor(_p, _v, n):  # type: ignore[no-untyped-def]
            return ExecutorResult(
                result_class=ResultClass.SOFT_REPAIRABLE,
                trace_id=f"trace-{n}",
                latency_ms=1.0,
                return_code=3,
            )

        def pass_heal(_attempt):  # type: ignore[no-untyped-def]
            return HealerResult(outcome=HealOutcomeStamp.PASS, reason_code="ok")

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=soft_executor,
            healer_fn=pass_heal,
            config=PipelineConfig(max_attempts=5, max_repairs=2),
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        # max_repairs=2 means: attempt1→heal1, attempt2→heal2, attempt3→ceiling.
        assert r.terminal_stamp is TerminalStamp.FAILURE
        assert len(r.heals) == 2
        assert r.dispatch is not None
        assert r.dispatch.decisive_reason == "repair_ceiling_reached"

    def test_heal_needs_help_terminates_with_needs_help(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        def soft_executor(_p, _v, n):  # type: ignore[no-untyped-def]
            return ExecutorResult(
                result_class=ResultClass.SOFT_REPAIRABLE,
                trace_id=f"trace-{n}",
                latency_ms=1.0,
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=soft_executor,
            healer_fn=_no_heal,
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.terminal_stamp is TerminalStamp.NEEDS_HELP
        assert len(r.heals) == 1


class TestTerminalShortCircuits:
    def test_fail_terminal_stops_immediately(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_terminal_failure_executor,
            healer_fn=_no_heal,
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.terminal_stamp is TerminalStamp.FAILURE
        assert len(r.attempts) == 1
        assert len(r.heals) == 0
        assert r.dispatch is not None
        assert r.dispatch.decisive_reason.startswith("fail_terminal")

    def test_needs_help_stops_immediately(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_needs_help_executor,
            healer_fn=_no_heal,
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.terminal_stamp is TerminalStamp.NEEDS_HELP
        assert len(r.attempts) == 1
        assert r.dispatch is not None
        assert r.dispatch.decisive_reason == "executor_needs_help"


class TestInvariants:
    def test_dispatch_never_has_commit_payload(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        assert r.dispatch.has_commit_payload is False

    def test_snapshot_mismatch_in_heal_raises(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        # Executor returns a soft-repairable so we enter heal; healer would
        # pass; but we mutate the attempt's determinism via a tampering
        # executor to force a mismatch. We do this by wrapping in a custom
        # executor that returns a determinism-mismatched attempt indirectly
        # via the pipeline: the pipeline always copies prep.determinism into
        # attempts, so direct tampering isn't possible. Instead we test
        # assert_snapshot_match directly via a synthetic attempt.
        from agentic_core.L2_execution.types.l2_v3_receipts import (
            AttemptReceipt,
            assert_snapshot_match,
        )

        bad_d = DeterminismBundle(
            blueprint_hash="bp-WRONG",
            policy_hash="pol-1",
            prompt_hash="x",
            input_hash="x",
            replay_key="x",
            attempt_seed="x",
        )
        attempt = AttemptReceipt(
            attempt_receipt_id="a-1",
            validation_packet_id="v-1",
            attempt_count=1,
            determinism=bad_d,
            lineage=lineage,
            trace_id="t-1",
            span_id="s-1",
            latency_ms=1.0,
            tokens_used=0,
            return_code=0,
            result_class=ResultClass.SOFT_REPAIRABLE,
        )
        with pytest.raises(SnapshotMismatchError):
            assert_snapshot_match(determinism, attempt.determinism)

    def test_idempotency_key_stable_per_input(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        r1 = pipe.run("route-1", "step-1", determinism, lineage)
        r2 = pipe.run("route-1", "step-1", determinism, lineage)
        # idempotency_key derives from input_hash + attempt_seed (both fixed
        # in this fixture) → equal.
        assert r1.prep.idempotency_key == r2.prep.idempotency_key
        # but run_id remains unique per invocation.
        assert r1.prep.run_id != r2.prep.run_id
