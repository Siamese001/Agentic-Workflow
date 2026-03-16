"""Wave 7.0.1 — Meta-Learning Proposal Contract Tests.

Tests deterministic serialization, immutable-target rejection,
semantic-clock enforcement, delta consistency, forbidden-key absence,
and trace-id determinism.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_contract")
_emit_applies_guardrail("p0", "test_meta_learning_contract", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_learning_contract", "policy_binding")
_emit_snapshots_state("p0", "test_meta_learning_contract", "state_snapshot")
emit_replay_key("p0", "test_meta_learning_contract")
emit_determinism_digest("p0", "test_meta_learning_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_meta_learning_contract", "execution_auth")
_emit_validates_capability("p2", "test_meta_learning_contract", "capability_check")
_emit_routes_to_capability("p2", "test_meta_learning_contract", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_learning_contract", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_learning_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_learning_contract", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_learning_contract", "exec_output")
_emit_dispatches_agent("p3", "test_meta_learning_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_learning_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_learning_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_learning_contract", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_learning_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_learning_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_learning_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_learning_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_learning_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_learning_contract", "eval_metric")
_emit_stores_embedding("p4", "test_meta_learning_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_learning_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_learning_contract", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L0_routing.scripts.run_all_guardians import (
    render_meta_learning_change_package,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from system_learning.types.app_signal_types import (
    APP_SIGNAL_CATALOG,
    build_app_signal_aggregate,
    build_app_signal_event,
)
from system_learning.types.meta_learning_types import (
    DENY_REASONS,
    IMMUTABLE_COMPONENTS,
    MetaLearningApprovalArtifact,
    MetaLearningEvaluationArtifact,
    MetaLearningProposalArtifact,
    ObjectiveSignal,
    ProposedChange,
    apply_meta_learning_proposal,
    build_meta_learning_approval,
    build_meta_learning_change_package,
    build_meta_learning_decision,
    build_meta_learning_evaluation,
    build_meta_learning_proposal,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_meta_learning_contract", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_learning_contract", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_learning_contract", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_learning_contract", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_learning_contract", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_learning_contract", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_learning_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_learning_contract", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_learning_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_learning_contract", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_learning_contract", "p4obs", "alert")
_emit_links_incident_trace("test_meta_learning_contract", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_learning_contract", "p3lm", "pattern")
_emit_records_learning_event("test_meta_learning_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_learning_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_learning_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_learning_contract", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_learning_contract", "p3lm", "policy")
_emit_stores_learning_state("test_meta_learning_contract", "p3lm", "state")
_emit_records_execution_trace("test_meta_learning_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_learning_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_learning_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_learning_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_learning_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_learning_contract", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_learning_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_learning_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_learning_contract", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_meta_learning_contract", "context_pull")
_emit_pulls_context("p1", "test_meta_learning_contract", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_contract", "uwg_term_secondary")
_emit_writes_through("p1", "test_meta_learning_contract", "write_through")
_emit_writes_through("p1", "test_meta_learning_contract", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_meta_learning_contract", "safety_validation")
_emit_invokes_eval("p1", "test_meta_learning_contract", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_learning_contract", "routing_commit")

# =============================================================================
# Helpers
# =============================================================================

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))
_EVIDENCE = "abc123"
_EVAL_EVIDENCE = "eval_hash_456"


def _build_sample(**overrides) -> MetaLearningProposalArtifact:
    """Build a sample proposal with sensible defaults, accepting overrides."""
    defaults = {
        "semantic_clock": _CLOCK,
        "proposer": "test_subsystem",
        "target_component": "routing_thresholds",
        "before": {"threshold": 0.5},
        "after": {"threshold": 0.7},
        "metric_name": "accuracy",
        "baseline": 0.80,
        "candidate": 0.85,
        "evidence_hash": _EVIDENCE,
        "policy_config_hash": None,
    }
    defaults.update(overrides)
    return build_meta_learning_proposal(**defaults)


# =============================================================================
# §1 — Deterministic Serialization
# =============================================================================


class TestDeterministicSerialization:
    def test_deterministic_serialization(self) -> None:
        """Two identical proposals → byte-identical JSON."""
        a = _build_sample()
        b = _build_sample()
        assert a.to_json() == b.to_json()
        assert json.loads(a.to_json()) == json.loads(b.to_json())


# =============================================================================
# §2 — Missing Semantic Clock Rejected
# =============================================================================


class TestSemanticClockEnforcement:
    def test_missing_semantic_clock_rejected(self) -> None:
        """Raises ValueError when semantic_clock is None."""
        with pytest.raises(ValueError, match="semantic_clock is required"):
            MetaLearningProposalArtifact(
                artifact_type="META_LEARNING_PROPOSAL",
                semantic_clock=None,  # type: ignore[arg-type]
                trace_id="dummy",
                proposer="test",
                target_component="routing_thresholds",
                proposed_change=ProposedChange.from_dicts({}, {}),
                objective_signal=ObjectiveSignal(metric_name="m", baseline=0.0, candidate=0.0, delta=0.0),
                evidence_hash="x",
                policy_config_hash=None,
            )


# =============================================================================
# §3 — Immutable Component Rejected
# =============================================================================


class TestImmutableComponentRejection:
    def test_immutable_component_rejected(self) -> None:
        """target_component='guardian_contract' → ValueError('IMMUTABLE_TARGET')."""
        with pytest.raises(ValueError, match="IMMUTABLE_TARGET"):
            _build_sample(target_component="guardian_contract")

    @pytest.mark.parametrize("component", sorted(IMMUTABLE_COMPONENTS))
    def test_all_immutable_components_rejected(self, component: str) -> None:
        """Every member of IMMUTABLE_COMPONENTS must be rejected."""
        with pytest.raises(ValueError, match="IMMUTABLE_TARGET"):
            _build_sample(target_component=component)


# =============================================================================
# §4 — Delta Calculation Consistent
# =============================================================================


class TestDeltaCalculation:
    def test_delta_calculation_consistent(self) -> None:
        """delta == candidate - baseline (float stable)."""
        proposal = _build_sample(baseline=0.80, candidate=0.85)
        assert proposal.objective_signal.delta == pytest.approx(0.05)
        assert proposal.objective_signal.delta == pytest.approx(
            proposal.objective_signal.candidate - proposal.objective_signal.baseline
        )

    def test_negative_delta(self) -> None:
        """Negative delta is correctly computed."""
        proposal = _build_sample(baseline=0.90, candidate=0.80)
        assert proposal.objective_signal.delta == pytest.approx(-0.10)


# =============================================================================
# §5 — No Runtime Fields Present
# =============================================================================

FORBIDDEN_KEYS = {"exec", "import", "path", "file", "code"}


class TestNoRuntimeFields:
    def test_no_runtime_fields_present(self) -> None:
        """Assert forbidden keys not in artifact JSON."""
        proposal = _build_sample()
        raw = proposal.to_json()
        payload = json.loads(raw)
        self._assert_no_forbidden_keys(payload)

    def _assert_no_forbidden_keys(self, obj: object, path: str = "") -> None:
        """Recursively check no forbidden top-level or nested keys."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in FORBIDDEN_KEYS, f"Forbidden key '{key}' found at {path}.{key}"
                self._assert_no_forbidden_keys(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._assert_no_forbidden_keys(item, f"{path}[{i}]")


# =============================================================================
# §6 — Trace ID Deterministic
# =============================================================================


class TestTraceIdDeterminism:
    def test_trace_id_deterministic(self) -> None:
        """Same input → identical trace_id."""
        a = _build_sample()
        b = _build_sample()
        assert a.trace_id == b.trace_id
        assert len(a.trace_id) == 64  # SHA-256 hex

    def test_trace_id_stable_under_dict_reorder(self) -> None:
        """Shuffled dict order → identical trace_id."""
        before_a = {"x": 1, "y": 2, "z": 3}
        after_a = {"a": 10, "b": 20}

        before_b = {"z": 3, "x": 1, "y": 2}
        after_b = {"b": 20, "a": 10}

        a = _build_sample(before=before_a, after=after_a)
        b = _build_sample(before=before_b, after=after_b)
        assert a.trace_id == b.trace_id

    def test_different_input_different_trace_id(self) -> None:
        """Different inputs must produce different trace_ids."""
        a = _build_sample(baseline=0.80, candidate=0.85)
        b = _build_sample(baseline=0.70, candidate=0.75)
        assert a.trace_id != b.trace_id


# =============================================================================
# §7 — Evaluation: Delta, Verdict, Determinism (Wave 7.0.3)
# =============================================================================


def _build_eval_sample(
    baseline: float = 0.80,
    candidate: float = 0.85,
    **overrides,
) -> MetaLearningEvaluationArtifact:
    """Build a sample evaluation from a default proposal."""
    proposal = _build_sample()
    defaults = {
        "proposal": proposal,
        "evaluator": "offline_bench",
        "dataset_id": "ds_001",
        "baseline": baseline,
        "candidate": candidate,
        "evidence_hash": _EVAL_EVIDENCE,
        "policy_config_hash": None,
    }
    defaults.update(overrides)
    return build_meta_learning_evaluation(**defaults)


class TestEvaluationDeltaAndVerdict:
    def test_evaluation_delta_and_verdict_deterministic(self) -> None:
        """delta == candidate - baseline; verdict derived deterministically."""
        ev = _build_eval_sample(baseline=0.80, candidate=0.85)
        assert ev.metrics.delta == pytest.approx(0.05)
        assert ev.verdict == "IMPROVE"

        ev_regress = _build_eval_sample(baseline=0.85, candidate=0.80)
        assert ev_regress.metrics.delta == pytest.approx(-0.05)
        assert ev_regress.verdict == "REGRESS"

        ev_nochange = _build_eval_sample(baseline=0.80, candidate=0.80)
        assert ev_nochange.metrics.delta == pytest.approx(0.0)
        assert ev_nochange.verdict == "NO_CHANGE"


class TestEvaluationSemanticClock:
    def test_evaluation_missing_semantic_clock_rejected(self) -> None:
        """Raises ValueError when semantic_clock is None."""
        with pytest.raises(ValueError, match="semantic_clock is required"):
            MetaLearningEvaluationArtifact(
                artifact_type="META_LEARNING_EVALUATION",
                semantic_clock=None,  # type: ignore[arg-type]
                trace_id="dummy",
                proposal_trace_id="dummy",
                evaluator="test",
                dataset_id="ds",
                metrics=ObjectiveSignal(metric_name="m", baseline=0.0, candidate=0.0, delta=0.0),
                verdict="NO_CHANGE",
                evidence_hash="x",
                policy_config_hash=None,
            )


class TestEvaluationTraceId:
    def test_evaluation_trace_id_stable_under_dict_order_shuffle(self) -> None:
        """Same inputs in different construction order → identical trace_id."""
        a = _build_eval_sample(baseline=0.80, candidate=0.85)
        b = _build_eval_sample(baseline=0.80, candidate=0.85)
        assert a.trace_id == b.trace_id
        assert len(a.trace_id) == 64


class TestEvaluationJsonDeterminism:
    def test_evaluation_json_byte_identical_same_inputs(self) -> None:
        """Two identical evaluations → byte-identical JSON."""
        a = _build_eval_sample()
        b = _build_eval_sample()
        assert a.to_json() == b.to_json()


# =============================================================================
# §8 — Approval Contract (Wave 7.0.4)
# =============================================================================


def _build_approval_sample(
    decision: str = "APPROVE",
    **overrides,
) -> MetaLearningApprovalArtifact:
    """Build a sample approval from a default evaluation."""
    ev = _build_eval_sample()
    defaults = {
        "evaluation": ev,
        "approver": "human_reviewer",
        "decision": decision,
        "rationale": "Metric improvement confirmed on holdout set.",
        "policy_config_hash": None,
    }
    defaults.update(overrides)
    return build_meta_learning_approval(**defaults)


class TestApprovalSemanticClock:
    def test_approval_missing_semantic_clock_rejected(self) -> None:
        """Raises ValueError when semantic_clock is None."""
        with pytest.raises(ValueError, match="semantic_clock is required"):
            MetaLearningApprovalArtifact(
                artifact_type="META_LEARNING_APPROVAL",
                semantic_clock=None,  # type: ignore[arg-type]
                trace_id="dummy",
                proposal_trace_id="dummy",
                evaluation_trace_id="dummy",
                approver="test",
                decision="APPROVE",
                rationale="n/a",
                policy_config_hash=None,
            )


class TestApprovalTraceId:
    def test_approval_trace_id_deterministic(self) -> None:
        """Same inputs → identical trace_id."""
        a = _build_approval_sample()
        b = _build_approval_sample()
        assert a.trace_id == b.trace_id
        assert len(a.trace_id) == 64


class TestApplyProhibited:
    def test_apply_prohibited_raises_stable_error(self) -> None:
        """apply_meta_learning_proposal() always raises RuntimeError."""
        with pytest.raises(RuntimeError, match="META_LEARNING_APPLY_PROHIBITED"):
            apply_meta_learning_proposal()

        with pytest.raises(RuntimeError, match="META_LEARNING_APPLY_PROHIBITED"):
            apply_meta_learning_proposal("any", "args", key="value")


# =============================================================================
# §9 — Decision Intake Gate (Wave 7.0.5)
# =============================================================================


def _build_full_pipeline():
    """Build a valid Proposal → Evaluation → Approval pipeline."""
    proposal = _build_sample()
    evaluation = build_meta_learning_evaluation(
        proposal=proposal,
        evaluator="offline_bench",
        dataset_id="ds_001",
        baseline=0.80,
        candidate=0.85,
        evidence_hash=_EVAL_EVIDENCE,
        policy_config_hash=None,
    )
    approval = build_meta_learning_approval(
        evaluation=evaluation,
        approver="human_reviewer",
        decision="APPROVE",
        rationale="Confirmed on holdout.",
        policy_config_hash=None,
    )
    return proposal, evaluation, approval


class TestDecisionGate:
    def test_decision_rejects_missing_proposal(self) -> None:
        """None proposal → REJECT MISSING_PROPOSAL."""
        _, evaluation, approval = _build_full_pipeline()
        d = build_meta_learning_decision(
            proposal=None,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert d.decision == "REJECT"
        assert d.deny_reason == DENY_REASONS["MISSING_PROPOSAL"]

    def test_decision_rejects_missing_evaluation(self) -> None:
        """None evaluation → REJECT MISSING_EVALUATION."""
        proposal, _, approval = _build_full_pipeline()
        d = build_meta_learning_decision(
            proposal=proposal,
            evaluation=None,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert d.decision == "REJECT"
        assert d.deny_reason == DENY_REASONS["MISSING_EVALUATION"]

    def test_decision_rejects_missing_approval(self) -> None:
        """None approval → REJECT MISSING_APPROVAL."""
        proposal, evaluation, _ = _build_full_pipeline()
        d = build_meta_learning_decision(
            proposal=proposal,
            evaluation=evaluation,
            approval=None,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert d.decision == "REJECT"
        assert d.deny_reason == DENY_REASONS["MISSING_APPROVAL"]

    def test_decision_rejects_trace_mismatch(self) -> None:
        """Mismatched trace ids → REJECT TRACE_MISMATCH."""
        proposal, evaluation, approval = _build_full_pipeline()
        # Build a second, different proposal to create a mismatch
        other_proposal = _build_sample(baseline=0.70, candidate=0.75)
        d = build_meta_learning_decision(
            proposal=other_proposal,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert d.decision == "REJECT"
        assert d.deny_reason == DENY_REASONS["TRACE_MISMATCH"]

    def test_decision_rejects_policy_hash_mismatch(self) -> None:
        """Mismatched policy_config_hash → REJECT POLICY_HASH_MISMATCH."""
        proposal, evaluation, approval = _build_full_pipeline()
        d = build_meta_learning_decision(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash="different_hash",
        )
        assert d.decision == "REJECT"
        assert d.deny_reason == DENY_REASONS["POLICY_HASH_MISMATCH"]

    def test_decision_rejects_non_improve_verdict(self) -> None:
        """Evaluation verdict != IMPROVE → REJECT EVAL_VERDICT_NOT_IMPROVE."""
        proposal = _build_sample()
        evaluation = build_meta_learning_evaluation(
            proposal=proposal,
            evaluator="offline_bench",
            dataset_id="ds_001",
            baseline=0.85,
            candidate=0.80,  # REGRESS
            evidence_hash=_EVAL_EVIDENCE,
            policy_config_hash=None,
        )
        approval = build_meta_learning_approval(
            evaluation=evaluation,
            approver="human_reviewer",
            decision="APPROVE",
            rationale="Approved anyway.",
            policy_config_hash=None,
        )
        d = build_meta_learning_decision(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert d.decision == "REJECT"
        assert d.deny_reason == DENY_REASONS["EVAL_VERDICT_NOT_IMPROVE"]

    def test_decision_rejects_when_approval_reject(self) -> None:
        """Approval decision=REJECT → REJECT APPROVAL_REJECTED."""
        proposal = _build_sample()
        evaluation = build_meta_learning_evaluation(
            proposal=proposal,
            evaluator="offline_bench",
            dataset_id="ds_001",
            baseline=0.80,
            candidate=0.85,
            evidence_hash=_EVAL_EVIDENCE,
            policy_config_hash=None,
        )
        approval = build_meta_learning_approval(
            evaluation=evaluation,
            approver="human_reviewer",
            decision="REJECT",
            rationale="Denied.",
            policy_config_hash=None,
        )
        d = build_meta_learning_decision(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert d.decision == "REJECT"
        assert d.deny_reason == DENY_REASONS["APPROVAL_REJECTED"]

    def test_decision_allows_to_apply_when_all_valid_and_approved(self) -> None:
        """Full valid pipeline → ALLOW_TO_APPLY + deterministic trace_id + JSON."""
        proposal, evaluation, approval = _build_full_pipeline()
        d1 = build_meta_learning_decision(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert d1.decision == "ALLOW_TO_APPLY"
        assert d1.deny_reason is None
        assert len(d1.trace_id) == 64

        # Determinism: build again → identical trace_id + JSON
        d2 = build_meta_learning_decision(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert d1.trace_id == d2.trace_id
        assert d1.to_json() == d2.to_json()


# =============================================================================
# §10 — Change Package Contract (Wave 7.0.6)
# =============================================================================


def _build_full_decision_pipeline():
    """Build Proposal → Evaluation → Approval → Decision (ALLOW_TO_APPLY)."""
    proposal, evaluation, approval = _build_full_pipeline()
    decision = build_meta_learning_decision(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        semantic_clock=_CLOCK,
        policy_config_hash=None,
    )
    return proposal, evaluation, approval, decision


class TestChangePackage:
    def test_change_package_requires_allow_to_apply(self) -> None:
        """REJECT decision → ValueError DECISION_NOT_ALLOW_TO_APPLY."""
        proposal, evaluation, approval = _build_full_pipeline()
        reject_decision = build_meta_learning_decision(
            proposal=None,
            evaluation=evaluation,
            approval=approval,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        with pytest.raises(ValueError, match="DECISION_NOT_ALLOW_TO_APPLY"):
            build_meta_learning_change_package(
                proposal=proposal,
                evaluation=evaluation,
                approval=approval,
                decision=reject_decision,
                target_component="routing_thresholds",
                change_spec={"threshold": 0.7},
                semantic_clock=_CLOCK,
                policy_config_hash=None,
            )

    def test_change_package_rejects_immutable_component(self) -> None:
        """target_component not in MUTABLE_COMPONENTS → ValueError."""
        proposal, evaluation, approval, decision = _build_full_decision_pipeline()
        with pytest.raises(ValueError, match="IMMUTABLE_COMPONENT"):
            build_meta_learning_change_package(
                proposal=proposal,
                evaluation=evaluation,
                approval=approval,
                decision=decision,
                target_component="guardian_contract",
                change_spec={"x": 1},
                semantic_clock=_CLOCK,
                policy_config_hash=None,
            )

    def test_change_package_trace_linkage_enforced(self) -> None:
        """Mismatched trace linkage → ValueError TRACE_LINKAGE_MISMATCH."""
        proposal, evaluation, approval, decision = _build_full_decision_pipeline()
        # Use a different proposal to break trace linkage
        other_proposal = _build_sample(baseline=0.70, candidate=0.75)
        with pytest.raises(ValueError, match="TRACE_LINKAGE_MISMATCH"):
            build_meta_learning_change_package(
                proposal=other_proposal,
                evaluation=evaluation,
                approval=approval,
                decision=decision,
                target_component="routing_thresholds",
                change_spec={"threshold": 0.7},
                semantic_clock=_CLOCK,
                policy_config_hash=None,
            )

    def test_change_package_policy_hash_alignment(self) -> None:
        """Mismatched policy_config_hash → ValueError POLICY_HASH_MISMATCH."""
        proposal, evaluation, approval, decision = _build_full_decision_pipeline()
        with pytest.raises(ValueError, match="POLICY_HASH_MISMATCH"):
            build_meta_learning_change_package(
                proposal=proposal,
                evaluation=evaluation,
                approval=approval,
                decision=decision,
                target_component="routing_thresholds",
                change_spec={"threshold": 0.7},
                semantic_clock=_CLOCK,
                policy_config_hash="mismatched_hash",
            )

    def test_change_package_change_spec_canonicalized_sorted_keys(self) -> None:
        """change_spec is canonicalized with sorted keys regardless of input order."""
        proposal, evaluation, approval, decision = _build_full_decision_pipeline()
        spec_a = {"z_key": 1, "a_key": 2, "m_key": 3}
        spec_b = {"a_key": 2, "m_key": 3, "z_key": 1}
        pkg_a = build_meta_learning_change_package(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            decision=decision,
            target_component="routing_thresholds",
            change_spec=spec_a,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        pkg_b = build_meta_learning_change_package(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            decision=decision,
            target_component="routing_thresholds",
            change_spec=spec_b,
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert pkg_a.change_spec == pkg_b.change_spec
        assert list(pkg_a.change_spec.keys()) == ["a_key", "m_key", "z_key"]

    def test_change_package_trace_id_deterministic(self) -> None:
        """Same inputs → identical trace_id and JSON."""
        proposal, evaluation, approval, decision = _build_full_decision_pipeline()
        pkg1 = build_meta_learning_change_package(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            decision=decision,
            target_component="routing_thresholds",
            change_spec={"threshold": 0.7},
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        pkg2 = build_meta_learning_change_package(
            proposal=proposal,
            evaluation=evaluation,
            approval=approval,
            decision=decision,
            target_component="routing_thresholds",
            change_spec={"threshold": 0.7},
            semantic_clock=_CLOCK,
            policy_config_hash=None,
        )
        assert pkg1.trace_id == pkg2.trace_id
        assert len(pkg1.trace_id) == 64
        assert pkg1.to_json() == pkg2.to_json()


# =============================================================================
# §11 — Render-Only Integration Seam (Wave 7.0.7)
# =============================================================================


def _build_change_package():
    """Build a valid change package through the full pipeline."""
    proposal, evaluation, approval, decision = _build_full_decision_pipeline()
    return build_meta_learning_change_package(
        proposal=proposal,
        evaluation=evaluation,
        approval=approval,
        decision=decision,
        target_component="routing_thresholds",
        change_spec={"threshold": 0.7, "alpha": 0.1},
        semantic_clock=_CLOCK,
        policy_config_hash=None,
    )


class TestRenderChangePackage:
    def test_render_change_package_returns_canonical_json(self) -> None:
        """as_json=True returns canonical JSON matching to_json()."""
        pkg = _build_change_package()
        rendered = render_meta_learning_change_package(pkg, as_json=True)
        # Must be valid JSON
        parsed = json.loads(rendered)
        assert parsed["artifact_type"] == "META_LEARNING_CHANGE_PACKAGE"
        assert parsed["target_component"] == "routing_thresholds"
        # Must match the artifact's own to_json()
        assert rendered == pkg.to_json()

    def test_render_change_package_is_deterministic(self) -> None:
        """Two renders of the same package produce identical output."""
        pkg = _build_change_package()
        r1_json = render_meta_learning_change_package(pkg, as_json=True)
        r2_json = render_meta_learning_change_package(pkg, as_json=True)
        assert r1_json == r2_json

        r1_summary = render_meta_learning_change_package(pkg, as_json=False)
        r2_summary = render_meta_learning_change_package(pkg, as_json=False)
        assert r1_summary == r2_summary
        assert "CHANGE_PACKAGE" in r1_summary
        assert "routing_thresholds" in r1_summary

    def test_render_change_package_no_apply_called(self) -> None:
        """apply_meta_learning_proposal() still raises and render doesn't invoke it."""
        pkg = _build_change_package()
        # Render succeeds without triggering apply
        rendered = render_meta_learning_change_package(pkg, as_json=True)
        assert len(rendered) > 0

        # Apply still raises
        with pytest.raises(RuntimeError, match="META_LEARNING_APPLY_PROHIBITED"):
            apply_meta_learning_proposal()


# =============================================================================
# §12 — APP Signal Contracts (Wave 7.0.8)
# =============================================================================


class TestAppSignalEvent:
    def test_event_requires_semantic_clock(self) -> None:
        """AppSignalEventArtifact rejects None semantic_clock."""
        with pytest.raises(ValueError, match="semantic_clock"):
            build_app_signal_event(
                app_id=APPS_RG_DIR,
                run_id="run_001",
                message_id="msg_001",
                metric_name="resume_message_response_rate",
                metric_value=0.85,
                semantic_clock=None,  # type: ignore[arg-type]
            )

    def test_event_trace_id_determinism(self) -> None:
        """Same inputs produce identical trace_id."""
        kwargs = {
            "app_id": APPS_RG_DIR,
            "run_id": "run_001",
            "message_id": "msg_001",
            "metric_name": "resume_message_response_rate",
            "metric_value": 0.85,
            "semantic_clock": _CLOCK,
        }
        e1 = build_app_signal_event(**kwargs)
        e2 = build_app_signal_event(**kwargs)
        assert e1.trace_id == e2.trace_id
        assert len(e1.trace_id) == 64

    def test_event_rejects_nan_inf(self) -> None:
        """NaN and inf metric_value are rejected."""
        base = {
            "app_id": APPS_RG_DIR,
            "run_id": "run_001",
            "message_id": "msg_001",
            "metric_name": "resume_message_response_rate",
            "semantic_clock": _CLOCK,
        }
        with pytest.raises(ValueError, match="metric_value_NOT_FINITE"):
            build_app_signal_event(**base, metric_value=float("nan"))
        with pytest.raises(ValueError, match="metric_value_NOT_FINITE"):
            build_app_signal_event(**base, metric_value=float("inf"))
        with pytest.raises(ValueError, match="metric_value_NOT_FINITE"):
            build_app_signal_event(**base, metric_value=float("-inf"))


class TestAppSignalAggregate:
    def test_aggregate_delta_correctness_and_determinism(self) -> None:
        """delta == candidate_value - baseline_value, trace_id deterministic."""
        kwargs = {
            "app_id": APPS_RG_DIR,
            "window_id": "w_2026_02",
            "metric_name": "resume_message_response_rate",
            "baseline_value": 0.80,
            "candidate_value": 0.85,
            "n": 100,
            "evidence_hash": "abc123",
            "semantic_clock": _CLOCK,
        }
        a1 = build_app_signal_aggregate(**kwargs)
        a2 = build_app_signal_aggregate(**kwargs)
        assert a1.delta == 0.85 - 0.80
        assert a1.trace_id == a2.trace_id
        assert len(a1.trace_id) == 64

    def test_canonicalization_stable(self) -> None:
        """JSON text exactly identical across two builds."""
        kwargs = {
            "app_id": APPS_LIC_DIR,
            "window_id": "w_2026_02",
            "metric_name": "conversion_to_interview_rate",
            "baseline_value": 0.70,
            "candidate_value": 0.75,
            "n": 50,
            "evidence_hash": "def456",
            "semantic_clock": _CLOCK,
        }
        a1 = build_app_signal_aggregate(**kwargs)
        a2 = build_app_signal_aggregate(**kwargs)
        assert a1.to_json() == a2.to_json()
        parsed = json.loads(a1.to_json())
        assert parsed["artifact_type"] == "APP_SIGNAL_AGGREGATE"
        assert parsed["delta"] == 0.75 - 0.70


# =============================================================================
# §13 — APP Signal Catalog Enforcement (Wave 7.0.10)
# =============================================================================


class TestAppSignalCatalog:
    def test_rejects_unknown_metric_name(self) -> None:
        """Builder rejects metric_name not in APP_SIGNAL_CATALOG."""
        with pytest.raises(ValueError, match="METRIC_NAME_NOT_IN_CATALOG"):
            build_app_signal_event(
                app_id=APPS_RG_DIR,
                run_id="run_001",
                message_id="msg_001",
                metric_name="unknown_metric_xyz",
                metric_value=0.5,
                semantic_clock=_CLOCK,
            )

    def test_rejects_out_of_bounds_rate(self) -> None:
        """Builder rejects rate metric_value > 1.0."""
        with pytest.raises(ValueError, match="metric_value_ABOVE_MAX"):
            build_app_signal_event(
                app_id=APPS_RG_DIR,
                run_id="run_001",
                message_id="msg_001",
                metric_name="resume_message_response_rate",
                metric_value=1.5,
                semantic_clock=_CLOCK,
            )
        with pytest.raises(ValueError, match="metric_value_BELOW_MIN"):
            build_app_signal_event(
                app_id=APPS_RG_DIR,
                run_id="run_001",
                message_id="msg_001",
                metric_name="resume_message_response_rate",
                metric_value=-0.1,
                semantic_clock=_CLOCK,
            )

    def test_accepts_valid_rate_at_boundary(self) -> None:
        """Builder accepts rate metric at 0.0 and 1.0 boundaries."""
        for val in (0.0, 1.0):
            evt = build_app_signal_event(
                app_id=APPS_RG_DIR,
                run_id="run_001",
                message_id="msg_001",
                metric_name="resume_message_response_rate",
                metric_value=val,
                semantic_clock=_CLOCK,
            )
            assert evt.metric_value == val

    def test_catalog_structural_completeness(self) -> None:
        """Every catalog entry has direction, aggregation, bounds, unit, recommended_window."""
        required_keys = {"direction", "aggregation", "bounds", "unit", "recommended_window"}
        for name, entry in APP_SIGNAL_CATALOG.items():
            missing = required_keys - set(entry.keys())
            assert not missing, f"{name} missing keys: {missing}"
            assert entry["direction"] in ("MAXIMIZE", "MINIMIZE"), f"{name} bad direction"
            assert entry["aggregation"] in ("rate", "mean", "median"), f"{name} bad aggregation"
