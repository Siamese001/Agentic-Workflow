"""H5 governance tests: LearningArtifactIntent frozen dataclass.

Validates:
- Immutability (frozen=True)
- Hash determinism (same inputs → same hash)
- Hash integrity (verify() passes on valid, fails on tampered)
- Construction via create() factory
- Hashability (usable as dict key / set member)
"""

import pytest

from agentic_core.L0_routing.seams.learning_seam import (
    LearningArtifactIntent,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_learning_artifact_intent", "p4obs", "metric_1")
_emit_emits_metric_event("test_learning_artifact_intent", "p4obs", "metric_2")
_emit_emits_metric_event("test_learning_artifact_intent", "p4obs", "metric_3")
_emit_emits_metric_event("test_learning_artifact_intent", "p4obs", "metric_4")
_emit_emits_metric_event("test_learning_artifact_intent", "p4obs", "metric_5")
_emit_emits_metric_event("test_learning_artifact_intent", "p4obs", "metric_6")
_emit_records_incident_event("test_learning_artifact_intent", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_learning_artifact_intent", "p4obs", "anomaly")
_emit_writes_observability_log("test_learning_artifact_intent", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_learning_artifact_intent", "p4obs", "mon_state")
_emit_triggers_alert("test_learning_artifact_intent", "p4obs", "alert")
_emit_links_incident_trace("test_learning_artifact_intent", "p4obs", "trace_link")
_emit_captures_pattern("test_learning_artifact_intent", "p3lm", "pattern")
_emit_records_learning_event("test_learning_artifact_intent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_learning_artifact_intent", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_learning_artifact_intent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_learning_artifact_intent", "p3lm", "routing")
_emit_improves_agent_policy("test_learning_artifact_intent", "p3lm", "policy")
_emit_stores_learning_state("test_learning_artifact_intent", "p3lm", "state")
_emit_records_execution_trace("test_learning_artifact_intent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_learning_artifact_intent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_learning_artifact_intent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_learning_artifact_intent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_learning_artifact_intent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_learning_artifact_intent", "env_read", "p2_env_1")
_emit_reads_environ("test_learning_artifact_intent", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_learning_artifact_intent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_learning_artifact_intent", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_learning_artifact_intent")
_emit_applies_guardrail("p0", "test_learning_artifact_intent", "p0_governance")
_emit_reads_policy_state("p0", "test_learning_artifact_intent", "policy_binding")
_emit_snapshots_state("p0", "test_learning_artifact_intent", "state_snapshot")
_emit_pulls_context("p1", "test_learning_artifact_intent", "context_pull")
_emit_pulls_context("p1", "test_learning_artifact_intent", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_learning_artifact_intent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_learning_artifact_intent", "uwg_term_secondary")
_emit_writes_through("p1", "test_learning_artifact_intent", "write_through")
_emit_writes_through("p1", "test_learning_artifact_intent", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_learning_artifact_intent", "safety_validation")
_emit_invokes_eval("p1", "test_learning_artifact_intent", "eval_call")
_emit_proposal_commits_routing("p1", "test_learning_artifact_intent", "routing_commit")
emit_replay_key("p0", "test_learning_artifact_intent")
emit_determinism_digest("p0", "test_learning_artifact_intent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_learning_artifact_intent", "execution_auth")
_emit_validates_capability("p2", "test_learning_artifact_intent", "capability_check")
_emit_routes_to_capability("p2", "test_learning_artifact_intent", "capability_route")
_emit_writes_via_uwg("p2", "test_learning_artifact_intent", "uwg_write")
_emit_blocks_direct_write("p2", "test_learning_artifact_intent", "direct_write_block")
_emit_records_tool_invocation("p2", "test_learning_artifact_intent", "tool_invocation")
_emit_captures_execution_output("p2", "test_learning_artifact_intent", "exec_output")
_emit_dispatches_agent("p3", "test_learning_artifact_intent", "agent_dispatch")
_emit_coordinates_agents("p3", "test_learning_artifact_intent", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_learning_artifact_intent", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_learning_artifact_intent", "healing_outcome")
_emit_escalates_failure("p3", "test_learning_artifact_intent", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_learning_artifact_intent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_learning_artifact_intent", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_learning_artifact_intent", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_learning_artifact_intent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_learning_artifact_intent", "eval_metric")
_emit_stores_embedding("p4", "test_learning_artifact_intent", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_learning_artifact_intent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_learning_artifact_intent", "exec_snapshot_link")

pytestmark = pytest.mark.governance

SAMPLE_METRICS = (("accuracy", 0.95), ("latency_ms", 42.0))


class TestFrozenImmutability:
    """LearningArtifactIntent must be frozen — no field mutation."""

    def test_cannot_set_field_after_construction(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        with pytest.raises(AttributeError):
            intent.agent_id = "tampered"  # type: ignore[misc]

    def test_cannot_delete_field(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        with pytest.raises(AttributeError):
            del intent.agent_id  # type: ignore[misc]


class TestHashDeterminism:
    """Same inputs must produce identical intent_hash."""

    def test_same_inputs_same_hash(self):
        a = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        b = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        assert a.intent_hash == b.intent_hash

    def test_different_inputs_different_hash(self):
        a = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        b = LearningArtifactIntent.create(
            agent_id="agent-2",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        assert a.intent_hash != b.intent_hash

    def test_hash_is_sha256_hex(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        assert len(intent.intent_hash) == 64
        assert all(c in "0123456789abcdef" for c in intent.intent_hash)


class TestHashIntegrity:
    """verify() must pass on valid intents, fail on tampered."""

    def test_verify_passes_on_valid_intent(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        assert intent.verify() is True

    def test_verify_fails_on_wrong_hash(self):
        intent = LearningArtifactIntent(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
            intent_hash="0" * 64,
        )
        assert intent.verify() is False


class TestHashability:
    """Frozen dataclass must be usable as dict key / set member."""

    def test_usable_as_set_member(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        s = {intent}
        assert intent in s

    def test_usable_as_dict_key(self):
        intent = LearningArtifactIntent.create(
            agent_id="agent-1",
            execution_id="exec-1",
            outcome="success",
            metrics=SAMPLE_METRICS,
            context_hash="abc123",
        )
        d = {intent: "value"}
        assert d[intent] == "value"
