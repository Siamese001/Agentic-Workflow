"""Unit tests for agentic_core.L3_orchestration.doctrine.contracts_l3_7.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 L3 doctrine
contracts. 03.7 State Ledger, Context Bus, Step Contract: frozen dataclasses,
closed-vocabulary enums (NodeState/StepResultStatus), __post_init__ invariant
raises (all via L3DoctrineContractError), the L3-never-commits assertions, and
the ``resolve_step_c0_policy`` step/parent inheritance helper.

Pure/deterministic surface only — no I/O, no mocks. ``L3StepContract`` carries
an optional ``C0Policy`` (from agentic_core.L0_routing.c0_retrieval.route_contract);
a valid RETRIEVE_REQUIRED policy is constructed for those paths.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.c0_retrieval.route_contract import C0Policy
from agentic_core.L3_orchestration.doctrine import L3DoctrineContractError
from agentic_core.L3_orchestration.doctrine.contracts_l3_6 import WorkflowNodeType
from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import (
    CostLatencyObservations,
    HandoffMergeReceipt,
    L3ContextBus,
    L3StateLedger,
    L3StepContract,
    NodeReadinessDecision,
    NodeState,
    StepInputs,
    StepResultIngest,
    StepResultStatus,
    resolve_step_c0_policy,
)


def _c0_policy() -> C0Policy:
    return C0Policy(
        grounding_required=True,
        c0_mode="RETRIEVE_REQUIRED",
        decision_source="L1_PLAN_DERIVED",
        evidence_contract_required=True,
    )


def _ledger(**overrides: object) -> L3StateLedger:
    kwargs: dict[str, object] = dict(
        workflow_id="wf-1",
        route_contract_id="rc-1",
        policy_hash="ph",
        blueprint_hash="bh",
        replay_key="rk",
        graph_hash="gh",
        node_states=(("n1", NodeState.READY),),
        edge_states=(),
        branch_states=(),
        join_states=(),
        attempt_counts=(("n1", 1),),
        retry_counts=(("n1", 0),),
        fallback_depth=0,
        remaining_budget=1.0,
        remaining_slo=10,
        checkpoints=(),
        paused_packets=(),
        reason_codes=(),
        ledger_hash="lh",
    )
    kwargs.update(overrides)
    return L3StateLedger(**kwargs)  # type: ignore[arg-type]


def _step_contract(**overrides: object) -> L3StepContract:
    kwargs: dict[str, object] = dict(
        step_contract_id="sc-1",
        workflow_id="wf-1",
        node_id="n1",
        attempt_id="a1",
        parent_route_id="r1",
        route_digest="rd",
        policy_hash="ph",
        blueprint_hash="bh",
        snapshot_id="snap",
        replay_key="rk",
        idempotency_key="idem",
        node_type=WorkflowNodeType.L2_MODEL_STEP,
        current_work_order="do-it",
        inputs=StepInputs(),
        expected_output_contract="oc",
        capability_token_requirement="cap",
        sandbox_envelope_requirement="sand",
        timeout_ms=1000,
        retry_policy="rp",
        fallback_permission="fp",
        telemetry_keys=(),
        expected_receipts=(),
        step_contract_hash="sch",
    )
    kwargs.update(overrides)
    return L3StepContract(**kwargs)  # type: ignore[arg-type]


class TestEnums:
    def test_node_state_members(self) -> None:
        assert {s.value for s in NodeState} == {
            "NOT_READY", "READY", "DISPATCHED", "RUNNING", "SUCCEEDED",
            "DEGRADED", "SOFT_REPAIRABLE", "FAILED_TERMINAL", "NEEDS_HELP",
            "PAUSED_HITL", "SKIPPED", "REJECTED", "SEALED",
        }

    def test_step_result_status_members(self) -> None:
        assert {s.value for s in StepResultStatus} == {
            "SUCCESS", "DEGRADED", "FAILED", "NEEDS_HELP", "PAUSED_HITL",
        }


class TestL3StateLedger:
    def test_construct_and_frozen(self) -> None:
        led = _ledger()
        assert led.workflow_id == "wf-1"
        with pytest.raises(dataclasses.FrozenInstanceError):
            led.workflow_id = "x"  # type: ignore[misc]

    def test_empty_workflow_id_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="workflow_id must be non-empty"):
            _ledger(workflow_id="")

    def test_negative_fallback_depth_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="fallback_depth"):
            _ledger(fallback_depth=-1)

    def test_negative_budget_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="remaining_budget"):
            _ledger(remaining_budget=-0.5)

    def test_nan_budget_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="remaining_budget"):
            _ledger(remaining_budget=float("nan"))

    def test_bad_node_state_pair_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="node_states"):
            _ledger(node_states=(("n1",),))

    def test_node_state_value_not_enum_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="must be NodeState"):
            _ledger(node_states=(("n1", "READY"),))


class TestNodeReadinessDecision:
    def _build(self, **overrides: object) -> NodeReadinessDecision:
        kwargs: dict[str, object] = dict(
            decision_id="d1",
            workflow_id="wf-1",
            node_id="n1",
            ready=True,
            blocked_reasons=(),
            satisfied_dependencies=(),
            unsatisfied_dependencies=(),
            required_evidence_refs=(),
            required_policy_refs=(),
            required_capability_refs=(),
            budget_status="ok",
            retry_status="ok",
            fallback_status="ok",
            hitl_status="ok",
            readiness_hash="rh",
        )
        kwargs.update(overrides)
        return NodeReadinessDecision(**kwargs)  # type: ignore[arg-type]

    def test_construct_ready(self) -> None:
        assert self._build().ready is True

    def test_ready_true_with_block_reasons_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="incompatible with non-empty blocked_reasons"):
            self._build(ready=True, blocked_reasons=("dep-missing",))

    def test_ready_must_be_bool(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="ready"):
            self._build(ready="yes")


class TestL3ContextBus:
    def test_defaults(self) -> None:
        bus = L3ContextBus(workflow_id="wf-1", bus_hash="bh")
        assert bus.carried_query_refs == ()
        assert bus.lineage_manifest == ""

    def test_empty_workflow_id_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="workflow_id"):
            L3ContextBus(workflow_id="", bus_hash="bh")

    def test_bad_ref_tuple_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="carried_query_refs"):
            L3ContextBus(workflow_id="wf-1", bus_hash="bh", carried_query_refs=("",))


class TestL3StepContract:
    def test_construct_defaults(self) -> None:
        sc = _step_contract()
        assert sc.no_durable_commit_authority is True
        assert sc.c0_policy is None

    def test_zero_timeout_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="timeout_ms must be > 0"):
            _step_contract(timeout_ms=0)

    def test_no_durable_commit_false_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="no_durable_commit_authority must be True"):
            _step_contract(no_durable_commit_authority=False)

    def test_wrong_node_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="node_type must be WorkflowNodeType"):
            _step_contract(node_type="L2_MODEL_STEP")

    def test_wrong_inputs_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="inputs must be StepInputs"):
            _step_contract(inputs={})

    def test_c0_policy_accepted(self) -> None:
        sc = _step_contract(c0_policy=_c0_policy())
        assert isinstance(sc.c0_policy, C0Policy)

    def test_c0_policy_wrong_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="c0_policy must be C0Policy"):
            _step_contract(c0_policy="not-a-policy")


class TestResolveStepC0Policy:
    def test_step_override_takes_precedence(self) -> None:
        step_pol = _c0_policy()
        parent_pol = _c0_policy()
        sc = _step_contract(c0_policy=step_pol)
        assert resolve_step_c0_policy(sc, parent_pol) is step_pol

    def test_inherits_parent_when_step_none(self) -> None:
        parent_pol = _c0_policy()
        sc = _step_contract(c0_policy=None)
        assert resolve_step_c0_policy(sc, parent_pol) is parent_pol

    def test_returns_none_when_neither(self) -> None:
        sc = _step_contract(c0_policy=None)
        assert resolve_step_c0_policy(sc, None) is None

    def test_wrong_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="expects L3StepContract"):
            resolve_step_c0_policy("not-a-step", None)  # type: ignore[arg-type]


class TestCostLatencyObservations:
    def test_defaults(self) -> None:
        obs = CostLatencyObservations()
        assert obs.latency_ms == 0
        assert obs.quality_score == 0.0

    def test_negative_latency_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="latency_ms"):
            CostLatencyObservations(latency_ms=-1)

    def test_quality_score_above_one_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="quality_score must be <= 1.0"):
            CostLatencyObservations(quality_score=1.5)

    def test_nan_cost_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="cost must not be NaN"):
            CostLatencyObservations(cost=float("nan"))


class TestStepResultIngest:
    def _build(self, **overrides: object) -> StepResultIngest:
        kwargs: dict[str, object] = dict(
            step_contract_id="sc-1",
            sealed_l2_artifact_ref="",
            status=StepResultStatus.SUCCESS,
            output_artifact_refs=(),
            proposed_state_diff_refs=(),
            returned_evidence_refs=(),
            returned_graph_refs=(),
            retry_signal="",
            branch_result="",
            handoff_signal="",
            needs_help_signal="",
            hitl_pause_signal="",
            cost_latency_observations=CostLatencyObservations(),
            replay_receipt_refs=(),
            ingest_hash="ih",
        )
        kwargs.update(overrides)
        return StepResultIngest(**kwargs)  # type: ignore[arg-type]

    def test_construct_defaults(self) -> None:
        ing = self._build()
        assert ing.quality_signal == 0.0
        assert ing.status == StepResultStatus.SUCCESS

    def test_bad_status_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="status must be StepResultStatus"):
            self._build(status="SUCCESS")

    def test_quality_signal_out_of_range_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match=r"quality_signal must be in \[0,1\]"):
            self._build(quality_signal=2.0)

    def test_wrong_cost_latency_type_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="cost_latency_observations"):
            self._build(cost_latency_observations={})


class TestHandoffMergeReceipt:
    def _build(self, **overrides: object) -> HandoffMergeReceipt:
        kwargs: dict[str, object] = dict(
            receipt_id="r1",
            workflow_id="wf-1",
            node_id="n1",
            new_state=NodeState.SUCCEEDED,
            reason_codes=(),
            preserved_lineage_refs=(),
            contradiction_flags=(),
        )
        kwargs.update(overrides)
        return HandoffMergeReceipt(**kwargs)  # type: ignore[arg-type]

    def test_defaults(self) -> None:
        assert self._build().durable_write_attempted is False

    def test_durable_write_attempted_true_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="durable_write_attempted must be False"):
            self._build(durable_write_attempted=True)

    def test_bad_new_state_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="new_state must be NodeState"):
            self._build(new_state="SUCCEEDED")


class TestStepInputs:
    def test_defaults_empty(self) -> None:
        si = StepInputs()
        assert si.query_refs == ()
        assert si.prior_artifact_refs == ()

    def test_bad_ref_raises(self) -> None:
        with pytest.raises(L3DoctrineContractError, match="query_refs"):
            StepInputs(query_refs=("",))
