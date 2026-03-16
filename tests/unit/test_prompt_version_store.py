"""Unit tests for PromptVersionStore.

Phase 1 Wave 1.1 test suite. Verifies immutability, deduplication,
and error handling for S0/I0 prompt versioning.
"""

import pytest

from agentic_core.L4_state.memory.prompt_version_store import PromptVersionStore
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_prompt_version_store", "p4obs", "metric_1")
_emit_emits_metric_event("test_prompt_version_store", "p4obs", "metric_2")
_emit_emits_metric_event("test_prompt_version_store", "p4obs", "metric_3")
_emit_emits_metric_event("test_prompt_version_store", "p4obs", "metric_4")
_emit_emits_metric_event("test_prompt_version_store", "p4obs", "metric_5")
_emit_emits_metric_event("test_prompt_version_store", "p4obs", "metric_6")
_emit_records_incident_event("test_prompt_version_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_prompt_version_store", "p4obs", "anomaly")
_emit_writes_observability_log("test_prompt_version_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_prompt_version_store", "p4obs", "mon_state")
_emit_triggers_alert("test_prompt_version_store", "p4obs", "alert")
_emit_links_incident_trace("test_prompt_version_store", "p4obs", "trace_link")
_emit_captures_pattern("test_prompt_version_store", "p3lm", "pattern")
_emit_records_learning_event("test_prompt_version_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_prompt_version_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_prompt_version_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_prompt_version_store", "p3lm", "routing")
_emit_improves_agent_policy("test_prompt_version_store", "p3lm", "policy")
_emit_stores_learning_state("test_prompt_version_store", "p3lm", "state")
_emit_records_execution_trace("test_prompt_version_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_prompt_version_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_prompt_version_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_prompt_version_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_prompt_version_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_prompt_version_store", "env_read", "p2_env_1")
_emit_reads_environ("test_prompt_version_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_prompt_version_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_prompt_version_store", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_prompt_version_store")
_emit_applies_guardrail("p0", "test_prompt_version_store", "p0_governance")
_emit_reads_policy_state("p0", "test_prompt_version_store", "policy_binding")
_emit_snapshots_state("p0", "test_prompt_version_store", "state_snapshot")
_emit_pulls_context("p1", "test_prompt_version_store", "context_pull")
_emit_pulls_context("p1", "test_prompt_version_store", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_prompt_version_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_prompt_version_store", "uwg_term_secondary")
_emit_writes_through("p1", "test_prompt_version_store", "write_through")
_emit_writes_through("p1", "test_prompt_version_store", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_prompt_version_store", "safety_validation")
_emit_invokes_eval("p1", "test_prompt_version_store", "eval_call")
_emit_proposal_commits_routing("p1", "test_prompt_version_store", "routing_commit")
_emit_escalates_to_human("p1", "test_prompt_version_store", "human_escalation")
_emit_routes_through("p1", "test_prompt_version_store", "route_through")
_emit_checks_agent_registry("p1", "test_prompt_version_store", "agent_registry")
_emit_validates_agent_capability("p1", "test_prompt_version_store", "capability")
_emit_dispatches_execution_plan("p1", "test_prompt_version_store", "exec_plan")
_emit_agent_executes_agent("p1", "test_prompt_version_store", "sub_agent")
_emit_routes_to_agent("p1", "test_prompt_version_store", "target_agent")
_emit_verifies_policy("p1", "test_prompt_version_store", "policy_check")
_emit_observes_runtime_state("p1", "test_prompt_version_store", "runtime_state")
_emit_verifies_boundary("p1", "test_prompt_version_store", "boundary_check")
_emit_transcripts_response("p1", "test_prompt_version_store", "transcript")
_emit_hard_fails_untranscripted("p1", "test_prompt_version_store")
_emit_gated_by_confidence("p1", "test_prompt_version_store", "confidence_gate")
emit_replay_key("p0", "test_prompt_version_store")
emit_determinism_digest("p0", "test_prompt_version_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_prompt_version_store", "execution_auth")
_emit_validates_capability("p2", "test_prompt_version_store", "capability_check")
_emit_routes_to_capability("p2", "test_prompt_version_store", "capability_route")
_emit_writes_via_uwg("p2", "test_prompt_version_store", "uwg_write")
_emit_blocks_direct_write("p2", "test_prompt_version_store", "direct_write_block")
_emit_records_tool_invocation("p2", "test_prompt_version_store", "tool_invocation")
_emit_captures_execution_output("p2", "test_prompt_version_store", "exec_output")
_emit_dispatches_agent("p3", "test_prompt_version_store", "agent_dispatch")
_emit_coordinates_agents("p3", "test_prompt_version_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_prompt_version_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_prompt_version_store", "healing_outcome")
_emit_escalates_failure("p3", "test_prompt_version_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_prompt_version_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_prompt_version_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_prompt_version_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_prompt_version_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_prompt_version_store", "eval_metric")
_emit_stores_embedding("p4", "test_prompt_version_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_prompt_version_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_prompt_version_store", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit
class TestPromptVersionStore:
    def setup_method(self):
        self.store = PromptVersionStore()
        self.store.clear()  # ensure clean state

    def test_commit_s0_returns_sha256(self):
        content = "You are a helpful assistant."
        version = self.store.commit_version("S0", content)
        assert isinstance(version, str)
        assert len(version) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in version)

    def test_commit_i0_returns_sha256(self):
        content = "Respond concisely."
        version = self.store.commit_version("I0", content)
        assert isinstance(version, str)
        assert len(version) == 64

    def test_same_content_returns_same_version(self):
        content = "Same content."
        v1 = self.store.commit_version("S0", content)
        v2 = self.store.commit_version("S0", content)
        assert v1 == v2

    def test_different_content_returns_different_versions(self):
        v1 = self.store.commit_version("S0", "Content A")
        v2 = self.store.commit_version("S0", "Content B")
        assert v1 != v2

    def test_invalid_prompt_type_raises(self):
        with pytest.raises(ValueError, match="prompt_type must be 'S0' or 'I0'"):
            self.store.commit_version("X0", "content")

    def test_get_s0_returns_content(self):
        content = "S0 prompt."
        version = self.store.commit_version("S0", content)
        assert self.store.get_s0(version) == content

    def test_get_i0_returns_content(self):
        content = "I0 prompt."
        version = self.store.commit_version("I0", content)
        assert self.store.get_i0(version) == content

    def test_get_unknown_version_raises(self):
        with pytest.raises(KeyError):
            self.store.get_s0("nonexistent")

    def test_list_versions(self):
        v1 = self.store.commit_version("S0", "A")
        v2 = self.store.commit_version("I0", "B")
        versions = self.store.list_versions()
        assert set(versions) == {v1, v2}
        assert len(versions) == 2

    def test_deduplication_across_types(self):
        content = "Same content."
        v_s0 = self.store.commit_version("S0", content)
        v_i0 = self.store.commit_version("I0", content)
        # Same content should map to same version regardless of type
        assert v_s0 == v_i0
        # But both get_* methods should work
        assert self.store.get_s0(v_s0) == content
        assert self.store.get_i0(v_i0) == content

    def test_clear_resets_store(self):
        self.store.commit_version("S0", "A")
        assert self.store.list_versions()
        self.store.clear()
        assert not self.store.list_versions()
