"""Tests for v4 deltas over v3 baseline.

Coverage:
    - DEGRADED_SUCCESS result class + terminal stamp + pipeline path
    - RepairStatus / DispatchTarget / ExecutionLane enums populated
    - AttemptReceipt v4 fields (lane, decisive_reason_code, local_check_results,
      generated_artifacts, proposed_state_diff, quarantined_payload)
    - HealReceipt v4 fields (repair_status, repair_tactic, before/after_hash,
      oscillation_status, snapshot_guard_status, next_action)
    - DispatchReceipt v4 fields (dispatch_target, user_visible_safe,
      commit_requested, downstream_recommendation)
    - E1.5 duplicate-sealed-receipt return when duplicate_cache is configured
    - DispatchTarget routing (EXIT_CONTROL / L3_MERGE / HITL_PACKETIZATION /
      UWG_REQUEST_CANDIDATE)
    - REJECTED terminal sets user_visible_safe=False
    - QUARANTINE classification via classify_repair_status helper
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
    AttemptReceipt,
    DeterminismBundle,
    DispatchReceipt,
    DispatchTarget,
    ExecutionLane,
    HealOutcomeStamp,
    HealReceipt,
    LineageRoot,
    RepairStatus,
    ResultClass,
    TerminalStamp,
    ValidationOutcome,
)
from agentic_core.L2_execution.types.l2_v4_invariants import (
    classify_repair_status,
    derive_dispatch_target,
    payload_digest,
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
    )


def _approve(_p) -> ValidatorResult:  # type: ignore[no-untyped-def]
    return ValidatorResult(
        outcome=ValidationOutcome.PASS,
        rules_passed=("schema",),
        classified_side_effect="READ",
    )


def _no_heal(_a) -> HealerResult:  # type: ignore[no-untyped-def]
    return HealerResult(
        outcome=HealOutcomeStamp.NEEDS_HELP, reason_code="unhealable"
    )


# ---------------------------------------------------------------------------
# v4 enums
# ---------------------------------------------------------------------------


class TestV4Enums:
    def test_result_class_has_degraded_success(self) -> None:
        assert ResultClass.DEGRADED_SUCCESS.value == "DEGRADED_SUCCESS"

    def test_terminal_stamp_has_degraded_success(self) -> None:
        assert TerminalStamp.DEGRADED_SUCCESS.value == "DEGRADED_SUCCESS"

    def test_repair_status_v4_set(self) -> None:
        names = {r.value for r in RepairStatus}
        assert names == {
            "REPAIRED",
            "NOT_REPAIRED",
            "QUARANTINED",
            "NEEDS_HELP",
            "FAIL_TERMINAL",
        }

    def test_dispatch_target_v4_set(self) -> None:
        names = {d.value for d in DispatchTarget}
        assert names == {
            "EXIT_CONTROL",
            "L3_MERGE",
            "HITL_PACKETIZATION",
            "UWG_REQUEST_CANDIDATE",
        }

    def test_execution_lane_v4_set(self) -> None:
        names = {lane.value for lane in ExecutionLane}
        assert names == {"READ", "MODEL", "TOOL", "ACTION", "ARTIFACT"}


# ---------------------------------------------------------------------------
# v4 receipt field extensions
# ---------------------------------------------------------------------------


class TestAttemptReceiptV4Fields:
    def test_v4_fields_default_safely(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        a = AttemptReceipt(
            attempt_receipt_id="a-1",
            validation_packet_id="v-1",
            attempt_count=1,
            determinism=determinism,
            lineage=lineage,
            trace_id="t-1",
            span_id="s-1",
            latency_ms=1.0,
            tokens_used=10,
            return_code=0,
            result_class=ResultClass.SUCCESS,
        )
        # v4 fields default to safe / empty values.
        assert a.execution_lane is None
        assert a.decisive_reason_code == ""
        assert a.local_check_results == ()
        assert a.generated_artifacts == ()
        assert a.proposed_state_diff == {}
        assert a.quarantined_payload is None

    def test_v4_fields_populated(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        a = AttemptReceipt(
            attempt_receipt_id="a-2",
            validation_packet_id="v-1",
            attempt_count=1,
            determinism=determinism,
            lineage=lineage,
            trace_id="t-2",
            span_id="s-2",
            latency_ms=1.0,
            tokens_used=10,
            return_code=0,
            result_class=ResultClass.DEGRADED_SUCCESS,
            execution_lane=ExecutionLane.MODEL,
            decisive_reason_code="missing_citation",
            local_check_results=(("schema", True), ("citation", False)),
            generated_artifacts=("artifact://draft.md",),
            proposed_state_diff={"path/to": "value"},
            quarantined_payload="unsafe_text",
        )
        assert a.execution_lane is ExecutionLane.MODEL
        assert a.decisive_reason_code == "missing_citation"
        assert ("citation", False) in a.local_check_results
        assert a.generated_artifacts == ("artifact://draft.md",)
        assert a.proposed_state_diff["path/to"] == "value"
        assert a.quarantined_payload == "unsafe_text"


class TestHealReceiptV4Fields:
    def test_v4_fields_default_safely(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        h = HealReceipt(
            repair_attempt_id="h-1",
            parent_attempt_receipt_id="a-1",
            failed_span_id="s-1",
            reason_code="schema_drift",
            repair_count=1,
            determinism=determinism,
            lineage=lineage,
            outcome=HealOutcomeStamp.PASS,
        )
        assert h.repair_status is None
        assert h.repair_tactic == ""
        assert h.before_hash == ""
        assert h.after_hash == ""
        assert h.snapshot_guard_status == "PASS"
        assert h.next_action == ""

    def test_v4_fields_populated(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        before = payload_digest({"k": "v0"})
        after = payload_digest({"k": "v1"})
        h = HealReceipt(
            repair_attempt_id="h-2",
            parent_attempt_receipt_id="a-1",
            failed_span_id="s-1",
            reason_code="json_parse",
            repair_count=2,
            determinism=determinism,
            lineage=lineage,
            outcome=HealOutcomeStamp.PASS,
            repair_status=RepairStatus.REPAIRED,
            repair_tactic="json_repair",
            before_hash=before,
            after_hash=after,
            oscillation_status="CLEAN",
            snapshot_guard_status="PASS",
            next_action="RETURN_TO_E3",
        )
        assert h.repair_status is RepairStatus.REPAIRED
        assert h.repair_tactic == "json_repair"
        assert h.before_hash != h.after_hash
        assert h.next_action == "RETURN_TO_E3"


class TestDispatchReceiptV4Fields:
    def test_v4_fields_default(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        d = DispatchReceipt(
            dispatch_receipt_id="d-1",
            sealed_l2_artifact_id="sealed-1",
            terminal_stamp=TerminalStamp.SUCCESS,
            determinism=determinism,
            lineage=lineage,
            prep_receipt_id="p-1",
            validation_packet_id="v-1",
        )
        assert d.dispatch_target is DispatchTarget.EXIT_CONTROL
        assert d.user_visible_safe is True
        assert d.commit_requested is False
        assert d.downstream_recommendation == ""


# ---------------------------------------------------------------------------
# Pipeline v4 paths
# ---------------------------------------------------------------------------


class TestPipelineDegradedSuccess:
    def test_degraded_terminal_when_allowed(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        def degraded(_p, _v, n):  # type: ignore[no-untyped-def]
            return ExecutorResult(
                result_class=ResultClass.DEGRADED_SUCCESS,
                trace_id=f"t-{n}",
                latency_ms=1.0,
                output_digest="partial",
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=degraded,
            healer_fn=_no_heal,
            config=PipelineConfig(allow_degraded=True),
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.terminal_stamp is TerminalStamp.DEGRADED_SUCCESS
        assert r.dispatch is not None
        assert (
            r.dispatch.downstream_recommendation == "allow_with_caveats"
        )

    def test_degraded_falls_back_to_needs_help_when_disallowed(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        def degraded(_p, _v, n):  # type: ignore[no-untyped-def]
            return ExecutorResult(
                result_class=ResultClass.DEGRADED_SUCCESS,
                trace_id=f"t-{n}",
                latency_ms=1.0,
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=degraded,
            healer_fn=_no_heal,
            config=PipelineConfig(allow_degraded=False),
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.terminal_stamp is TerminalStamp.NEEDS_HELP


class TestPipelineDuplicateCache:
    def test_e1_5_duplicate_returns_prior_result(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        cache: dict = {}
        executor_calls = {"n": 0}

        def counted_success(_p, _v, n):  # type: ignore[no-untyped-def]
            executor_calls["n"] += 1
            return ExecutorResult(
                result_class=ResultClass.SUCCESS,
                trace_id=f"t-{n}",
                latency_ms=1.0,
                output_digest="ok",
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=counted_success,
            healer_fn=_no_heal,
            config=PipelineConfig(duplicate_cache=cache),
        )
        r1 = pipe.run("route-1", "step-1", determinism, lineage)
        r2 = pipe.run("route-1", "step-1", determinism, lineage)
        # Executor invoked exactly once — second run returned cached.
        assert executor_calls["n"] == 1
        # Same sealed dispatch artifact id (same object returned).
        assert r1 is r2

    def test_no_cache_means_re_execute(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        executor_calls = {"n": 0}

        def counted_success(_p, _v, n):  # type: ignore[no-untyped-def]
            executor_calls["n"] += 1
            return ExecutorResult(
                result_class=ResultClass.SUCCESS,
                trace_id=f"t-{n}",
                latency_ms=1.0,
                output_digest="ok",
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=counted_success,
            healer_fn=_no_heal,
        )
        pipe.run("route-1", "step-1", determinism, lineage)
        pipe.run("route-1", "step-1", determinism, lineage)
        assert executor_calls["n"] == 2


class TestDispatchTargetRouting:
    def test_l3_managed_routes_to_l3_merge(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        def ok(_p, _v, n):  # type: ignore[no-untyped-def]
            return ExecutorResult(
                result_class=ResultClass.SUCCESS,
                trace_id=f"t-{n}",
                latency_ms=1.0,
                output_digest="ok",
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=ok,
            healer_fn=_no_heal,
            config=PipelineConfig(is_l3_managed=True),
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        assert r.dispatch.dispatch_target is DispatchTarget.L3_MERGE

    def test_needs_help_routes_to_hitl_packetization(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        def needs_help(_p, _v, n):  # type: ignore[no-untyped-def]
            return ExecutorResult(
                result_class=ResultClass.NEEDS_HELP,
                trace_id=f"t-{n}",
                latency_ms=1.0,
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=needs_help,
            healer_fn=_no_heal,
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        assert (
            r.dispatch.dispatch_target is DispatchTarget.HITL_PACKETIZATION
        )

    def test_proposed_state_diff_routes_to_uwg_candidate(self) -> None:
        # The executor adapter today does not pass proposed_state_diff into
        # the AttemptReceipt directly; this test verifies the routing helper
        # that the pipeline uses to make the determination.
        target = derive_dispatch_target(
            is_l3_managed=False,
            terminal=TerminalStamp.SUCCESS,
            commit_requested=True,
        )
        assert target is DispatchTarget.UWG_REQUEST_CANDIDATE

    def test_default_routes_to_exit_control(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        def ok(_p, _v, n):  # type: ignore[no-untyped-def]
            return ExecutorResult(
                result_class=ResultClass.SUCCESS,
                trace_id=f"t-{n}",
                latency_ms=1.0,
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=ok, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        assert r.dispatch.dispatch_target is DispatchTarget.EXIT_CONTROL


class TestRejectedSafetyFlags:
    def test_rejected_terminal_marks_unsafe(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        def rejected(_p, _v, n):  # type: ignore[no-untyped-def]
            return ExecutorResult(
                result_class=ResultClass.REJECTED,
                trace_id=f"t-{n}",
                latency_ms=1.0,
            )

        pipe = L2PhasePipeline(
            validator_fn=_approve,
            executor_fn=rejected,
            healer_fn=_no_heal,
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        assert r.dispatch.terminal_stamp is TerminalStamp.REJECTED
        assert r.dispatch.user_visible_safe is False
        assert r.dispatch.downstream_recommendation == "deny"


# ---------------------------------------------------------------------------
# classify_repair_status helper
# ---------------------------------------------------------------------------


class TestClassifyRepairStatus:
    def test_pass_maps_to_repaired(self) -> None:
        assert (
            classify_repair_status(HealOutcomeStamp.PASS)
            is RepairStatus.REPAIRED
        )

    def test_quarantine_required_overrides_pass(self) -> None:
        assert (
            classify_repair_status(
                HealOutcomeStamp.PASS, quarantine_required=True
            )
            is RepairStatus.QUARANTINED
        )

    def test_needs_help_maps_to_needs_help(self) -> None:
        assert (
            classify_repair_status(HealOutcomeStamp.NEEDS_HELP)
            is RepairStatus.NEEDS_HELP
        )

    def test_escalate_artifact_maps_to_needs_help(self) -> None:
        assert (
            classify_repair_status(HealOutcomeStamp.ESCALATE_ARTIFACT)
            is RepairStatus.NEEDS_HELP
        )

    def test_fail_terminal_maps_to_fail_terminal(self) -> None:
        assert (
            classify_repair_status(HealOutcomeStamp.FAIL_TERMINAL)
            is RepairStatus.FAIL_TERMINAL
        )


# ---------------------------------------------------------------------------
# payload_digest is stable
# ---------------------------------------------------------------------------


class TestPayloadDigest:
    def test_same_payload_same_digest(self) -> None:
        d1 = payload_digest({"a": 1, "b": 2})
        d2 = payload_digest({"b": 2, "a": 1})
        assert d1 == d2

    def test_different_payload_different_digest(self) -> None:
        d1 = payload_digest({"a": 1})
        d2 = payload_digest({"a": 2})
        assert d1 != d2

    def test_unserializable_falls_back_to_repr(self) -> None:
        class Opaque:
            pass

        # Should not raise; uses repr fallback.
        d = payload_digest(Opaque())
        assert isinstance(d, str)
        assert len(d) == 64  # sha256 hex
