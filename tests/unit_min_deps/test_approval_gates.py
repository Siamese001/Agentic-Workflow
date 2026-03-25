"""Unit tests for system_learning.pipelines.approval_gates."""

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_authorize_and_execute("p2", "test_approval_gates", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_approval_gates", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_approval_gates", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_approval_gates", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_approval_gates", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_approval_gates", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_approval_gates", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_approval_gates", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_approval_gates", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_approval_gates", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_approval_gates", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_approval_gates", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_approval_gates", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_approval_gates", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_approval_gates", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_approval_gates", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_approval_gates", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_approval_gates", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_approval_gates", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_approval_gates", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
from system_learning.pipelines.approval_gates import (
    ApprovalDecision,
    DefaultRiskClassifier,
    DefaultRuleBasedGate,
)

# REMOVED: _emit_emits_metric_event("test_approval_gates", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_approval_gates", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_approval_gates", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_approval_gates", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_approval_gates", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_approval_gates", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_approval_gates", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_approval_gates", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_approval_gates", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_approval_gates", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_approval_gates", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_approval_gates", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_approval_gates", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_approval_gates", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_approval_gates", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_approval_gates", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_approval_gates", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_approval_gates", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_approval_gates", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_approval_gates", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_approval_gates", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_approval_gates", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_approval_gates", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_approval_gates", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_approval_gates", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_approval_gates", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_approval_gates", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_approval_gates", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_approval_gates")
# REMOVED: _emit_applies_guardrail("p0", "test_approval_gates", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_approval_gates", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_approval_gates", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_approval_gates", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_approval_gates", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_approval_gates", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_approval_gates", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_approval_gates", "write_through")
# REMOVED: _emit_writes_through("p1", "test_approval_gates", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_approval_gates", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_approval_gates", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_approval_gates", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_approval_gates", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_approval_gates", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_approval_gates", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_approval_gates", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_approval_gates", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_approval_gates", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_approval_gates", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_approval_gates", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_approval_gates", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_approval_gates", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_approval_gates", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_approval_gates")
# REMOVED: _emit_gated_by_confidence("p1", "test_approval_gates", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_approval_gates")
# REMOVED: emit_determinism_digest("p0", "test_approval_gates")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


pytestmark = pytest.mark.unit_min_deps

THRESHOLD = 0.95

# =============================================================================
# Mock Change Package
# =============================================================================


class MockChangePackage:
    """Mock change package for testing."""

    def __init__(self, num_surfaces: int = 1, max_delta: float = 0.0, affects_l5: bool = False):
        self.num_surfaces = num_surfaces
        self.max_delta = max_delta
        self.affects_l5 = affects_l5


# =============================================================================
# Tests
# =============================================================================


class TestDefaultRiskClassifier:
    def test_low_impact_single_surface_small_delta(self):
        """Single surface with small delta is low impact (tier 1)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.03, affects_l5=False)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 1

    def test_medium_impact_multiple_surfaces(self):
        """Multiple surfaces is medium impact (tier 2)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=2, max_delta=0.03, affects_l5=False)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 2

    def test_medium_impact_moderate_delta(self):
        """Moderate delta is medium impact (tier 2)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.08, affects_l5=False)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 2

    def test_high_impact_affects_l5(self):
        """Affecting L5 is high impact (tier 3)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.03, affects_l5=True)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 3

    def test_high_impact_many_surfaces(self):
        """Many surfaces is high impact (tier 3)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=5, max_delta=0.03, affects_l5=False)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 3

    def test_critical_impact_l5_large_delta(self):
        """L5 + large delta is critical impact (tier 4)."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.15, affects_l5=True)

        risk_tier = classifier.classify(pkg)

        assert risk_tier == 4


class TestDefaultRuleBasedGate:
    def test_high_impact_rejects_by_default(self):
        """High impact changes are REJECTED by default."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, allow_high_impact=False)

        # High impact package
        pkg = MockChangePackage(num_surfaces=5, max_delta=0.03, affects_l5=False)

        decision = gate.decide(pkg, None, None)

        assert decision == ApprovalDecision.REJECT

    def test_low_impact_approves(self):
        """Low impact changes are APPROVED."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, allow_high_impact=False)

        # Low impact package
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.03, affects_l5=False)

        decision = gate.decide(pkg, None, None)

        assert decision == ApprovalDecision.APPROVE

    def test_high_impact_approves_when_allowed(self):
        """High impact changes are APPROVED when allow_high_impact=True."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, allow_high_impact=True)

        # High impact package
        pkg = MockChangePackage(num_surfaces=5, max_delta=0.03, affects_l5=False)

        decision = gate.decide(pkg, None, None)

        assert decision == ApprovalDecision.APPROVE

    def test_medium_impact_approves(self):
        """Medium impact changes are APPROVED (below threshold)."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, high_impact_threshold=3, allow_high_impact=False)

        # Medium impact package (tier 2)
        pkg = MockChangePackage(num_surfaces=2, max_delta=0.03, affects_l5=False)

        decision = gate.decide(pkg, None, None)

        assert decision == ApprovalDecision.APPROVE


class TestDeterminism:
    def test_classifier_deterministic(self):
        """Risk classifier produces identical results."""
        classifier = DefaultRiskClassifier()
        pkg = MockChangePackage(num_surfaces=2, max_delta=0.08, affects_l5=False)

        tier1 = classifier.classify(pkg)
        tier2 = classifier.classify(pkg)
        tier3 = classifier.classify(pkg)

        assert tier1 == tier2 == tier3

    def test_gate_deterministic(self):
        """Approval gate produces identical results."""
        classifier = DefaultRiskClassifier()
        gate = DefaultRuleBasedGate(classifier, allow_high_impact=False)
        pkg = MockChangePackage(num_surfaces=1, max_delta=0.03, affects_l5=False)

        decision1 = gate.decide(pkg, None, None)
        decision2 = gate.decide(pkg, None, None)
        decision3 = gate.decide(pkg, None, None)

        assert decision1 == decision2 == decision3
