"""Integration tests for the L2 Sequencer Adapter.

Asserts that the adapter (l2_sequencer_adapter.py) correctly lifts a real
:class:`L2PhasePipeline` run output into the spec-04.0 / 04.9 typed
contracts. Together with `test_l2_sequencer_contract.py` (unit tests for
the contracts in isolation) and these (real-pipeline binding), every
spec-04.0/04.9 contract row in the coverage matrix is now bound to
runtime evidence — closing the deferred runtime-wiring item.
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
from agentic_core.L2_execution.orchestration.l2_sequencer_adapter import (
    build_mutation_detection_receipt,
    build_sequencer_receipt,
    build_state_diff_candidate,
    build_state_diff_manifest,
)
from agentic_core.L2_execution.types.l2_mutation_intent import (
    MutationIntentClass,
    WRITE_AUTH_NONE_INSIDE_L2,
)
from agentic_core.L2_execution.types.l2_sequencer_contract import (
    L2TerminalClass,
    SequencerReceipt,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    DeterminismBundle,
    HealOutcomeStamp,
    LineageRoot,
    PrepReceipt,
    ResultClass,
    TerminalStamp,
    ValidationOutcome,
)


# --------------------------------------------------------------------- fixtures
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


def _executor_with_diff(_p, _v, _n) -> ExecutorResult:  # type: ignore[no-untyped-def]
    return ExecutorResult(
        result_class=ResultClass.SUCCESS,
        trace_id=f"trace-{_n}",
        span_id=f"span-{_n}",
        latency_ms=10.0,
        tokens_used=20,
        return_code=0,
        output_digest="ok-sha",
        proposed_state_diff={"op": "replace", "path": "/x", "value": 1},
    )


def _no_heal(_attempt) -> HealerResult:  # type: ignore[no-untyped-def]
    return HealerResult(
        outcome=HealOutcomeStamp.NEEDS_HELP,
        reason_code="unhealable",
    )


# --------------------------------------------------------------------- tests
class TestSequencerReceiptAdapter:
    def test_success_run_emits_sequencer_receipt_with_terminal_class_success(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        seq = build_sequencer_receipt(run_result=result, request_id="req-1")
        assert isinstance(seq, SequencerReceipt)
        assert seq.terminal_class is L2TerminalClass.SUCCESS
        assert seq.attempt_count == 1
        assert seq.repair_count == 0
        assert seq.no_direct_write_assertion is True
        assert seq.deterministic_digest != ""
        assert seq.policy_hash == "pol-1"
        assert seq.blueprint_hash == "bp-1"
        assert seq.replay_key == "rk-1"
        # Receipts wired through.
        assert seq.e1_receipt_ref == result.prep.prep_receipt_id
        assert seq.e2_receipt_refs == (result.validation.validation_packet_id,)
        assert seq.e3_attempt_receipt_refs == (
            result.attempts[0].attempt_receipt_id,
        )
        assert seq.e5_seal_receipt_ref == result.dispatch.dispatch_receipt_id

    def test_rejected_run_emits_sequencer_receipt_with_terminal_class_rejected(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_reject,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        seq = build_sequencer_receipt(run_result=result, request_id="req-2")
        assert seq.terminal_class is L2TerminalClass.REJECTED
        assert seq.attempt_count == 0
        assert seq.e3_attempt_receipt_refs == ()
        assert seq.e5_seal_receipt_ref == "no-dispatch"
        assert any("validation:" in r for r in seq.terminal_reason_codes)

    def test_sequencer_receipt_is_deterministic_across_replays(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        """Same PipelineRunResult input → identical SequencerReceipt digest."""
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        seq1 = build_sequencer_receipt(run_result=result, request_id="req-X")
        seq2 = build_sequencer_receipt(run_result=result, request_id="req-X")
        assert seq1 == seq2
        assert seq1.deterministic_digest == seq2.deterministic_digest


class TestStateDiffManifestAdapter:
    def test_run_with_diff_produces_manifest(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_executor_with_diff,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        manifest = build_state_diff_manifest(
            run_result=result,
            capability_token_ref="cap-1",
            sandbox_envelope_ref="sb-1",
            route_contract_ref="route-1",
            l2_authority_ref="auth-1",
        )
        assert manifest is not None
        assert manifest.candidate_count == 1
        assert manifest.l2_no_commit_assertion is True
        assert manifest.forbidden_direct_write_check is True
        assert manifest.exit_handoff_eligibility_hint == "eligible"
        assert manifest.sealed_l2_artifact_ref == result.dispatch.dispatch_receipt_id

    def test_run_without_diff_returns_none(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_success_executor,  # no diff
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        manifest = build_state_diff_manifest(
            run_result=result,
            capability_token_ref="cap-1",
            sandbox_envelope_ref="sb-1",
            route_contract_ref="route-1",
            l2_authority_ref="auth-1",
        )
        assert manifest is None

    def test_candidate_carries_pinned_invariants(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_executor_with_diff,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        attempt = result.attempts[0]
        cand = build_state_diff_candidate(
            attempt=attempt,
            capability_token_ref="cap-1",
            sandbox_envelope_ref="sb-1",
            route_contract_ref="route-1",
            l2_authority_ref="auth-1",
        )
        assert cand is not None
        assert cand.write_auth_status == WRITE_AUTH_NONE_INSIDE_L2
        assert cand.inert_until_exit_uwg is True
        assert cand.policy_hash == "pol-1"
        assert cand.replay_key == "rk-1"

    def test_detection_receipt_for_attempt_with_no_diff(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_success_executor,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        attempt = result.attempts[0]
        det = build_mutation_detection_receipt(
            attempt=attempt,
            request_id="req-1",
            run_id=result.prep.run_id,
        )
        assert det.mutation_detected is False
        assert det.mutation_intent_class is MutationIntentClass.NONE

    def test_detection_receipt_for_attempt_with_diff(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=_executor_with_diff,
            healer_fn=_no_heal,
        )
        result = pipe.run("route-1", "step-1", determinism, lineage)
        attempt = result.attempts[0]
        det = build_mutation_detection_receipt(
            attempt=attempt,
            request_id="req-1",
            run_id=result.prep.run_id,
        )
        assert det.mutation_detected is True
        assert det.mutation_intent_class is MutationIntentClass.SANDBOX_ARTIFACT
