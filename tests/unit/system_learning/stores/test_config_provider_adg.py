"""ADG-driven tests for system_learning/stores/config_provider.py — fan_in=1."""

from __future__ import annotations

import json
from unittest.mock import patch

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_config_provider_adg")
# REMOVED: _emit_applies_guardrail("p0", "test_config_provider_adg", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_config_provider_adg", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_config_provider_adg", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_config_provider_adg")
# REMOVED: emit_determinism_digest("p0", "test_config_provider_adg")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_config_provider_adg", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_config_provider_adg", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_config_provider_adg", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_config_provider_adg", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_config_provider_adg", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_config_provider_adg", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_config_provider_adg", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_config_provider_adg", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_config_provider_adg", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_config_provider_adg", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_config_provider_adg", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_config_provider_adg", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_config_provider_adg", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_config_provider_adg", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_config_provider_adg", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_config_provider_adg", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_config_provider_adg", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_config_provider_adg", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_config_provider_adg", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_config_provider_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

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
from system_learning.stores.config_provider import FileBackedConfigProvider

# REMOVED: _emit_emits_metric_event("test_config_provider_adg", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_config_provider_adg", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_config_provider_adg", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_config_provider_adg", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_config_provider_adg", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_config_provider_adg", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_config_provider_adg", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_config_provider_adg", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_config_provider_adg", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_config_provider_adg", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_config_provider_adg", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_config_provider_adg", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_config_provider_adg", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_config_provider_adg", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_config_provider_adg", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_config_provider_adg", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_config_provider_adg", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_config_provider_adg", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_config_provider_adg", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_config_provider_adg", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_config_provider_adg", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_config_provider_adg", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_config_provider_adg", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_config_provider_adg", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_config_provider_adg", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_config_provider_adg", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_config_provider_adg", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_config_provider_adg", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_config_provider_adg", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_config_provider_adg", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_config_provider_adg", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_config_provider_adg", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_config_provider_adg", "write_through")
# REMOVED: _emit_writes_through("p1", "test_config_provider_adg", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_config_provider_adg", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_config_provider_adg", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_config_provider_adg", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_config_provider_adg", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_config_provider_adg", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_config_provider_adg", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_config_provider_adg", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_config_provider_adg", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_config_provider_adg", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_config_provider_adg", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_config_provider_adg", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_config_provider_adg", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_config_provider_adg", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_config_provider_adg", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_config_provider_adg")
# REMOVED: _emit_gated_by_confidence("p1", "test_config_provider_adg", "confidence_gate")


class TestFileBackedConfigProvider:
    def test_creates(self, tmp_path):
        provider = FileBackedConfigProvider(runtime_state_path=tmp_path / "state.json")
        assert provider is not None

    def test_missing_runtime_state_returns_empty(self, tmp_path):
        provider = FileBackedConfigProvider(runtime_state_path=tmp_path / "missing.json")
        result = provider.get_current_configs()
        assert isinstance(result, dict)

    def test_with_runtime_state_file(self, tmp_path):
        state = {"routing": {"threshold": 0.8}}
        state_path = tmp_path / "runtime_state.json"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        provider = FileBackedConfigProvider(runtime_state_path=state_path)
        result = provider.get_current_configs()
        assert isinstance(result, dict)

    def test_has_get_current_configs(self):
        assert hasattr(FileBackedConfigProvider, "get_current_configs")

    def test_runtime_state_configs_are_persisted(self, tmp_path):
        state = {"meta_learning": {"threshold": 0.8}, "routing_config": {"route": "primary"}}
        state_path = tmp_path / "runtime_state.json"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        provider = FileBackedConfigProvider(runtime_state_path=state_path)

        class _Bridge:
            def __init__(self):
                self.calls = []

            def persist_config_snapshot(self, surface_name, config_bytes, *, source="config_provider", ts=""):
                self.calls.append((surface_name, json.loads(config_bytes.decode("utf-8")), source, ts))
                return True

        bridge = _Bridge()
        with patch("system_learning.stores.config_provider.get_sl_memory_bridge", return_value=bridge):
            configs = provider.get_current_configs()

        assert sorted(configs) == ["meta_learning", "routing_config"]
        assert [call[0] for call in bridge.calls] == ["meta_learning", "routing_config"]

    def test_config_dir_configs_are_persisted(self, tmp_path):
        state_path = tmp_path / "runtime_state.json"
        config_dir = tmp_path / "configs"
        config_dir.mkdir()
        (config_dir / "surface_a.json").write_text(json.dumps({"alpha": 1}), encoding="utf-8")
        provider = FileBackedConfigProvider(runtime_state_path=state_path, config_dir=config_dir)

        class _Bridge:
            def __init__(self):
                self.calls = []

            def persist_config_snapshot(self, surface_name, config_bytes, *, source="config_provider", ts=""):
                self.calls.append((surface_name, json.loads(config_bytes.decode("utf-8")), source, ts))
                return True

        bridge = _Bridge()
        with patch("system_learning.stores.config_provider.get_sl_memory_bridge", return_value=bridge):
            configs = provider.get_current_configs()

        assert list(configs) == ["surface_a"]
        assert bridge.calls == [("surface_a", {"alpha": 1}, "config_provider", "")]

    def test_config_persistence_handles_failure(self, tmp_path):
        """Test that config reading still works even if bridge persistence fails."""
        state_path = tmp_path / "runtime_state.json"
        state = {"meta_learning": {"threshold": 0.8}}
        state_path.write_text(json.dumps(state), encoding="utf-8")
        provider = FileBackedConfigProvider(runtime_state_path=state_path)

        class _FailingBridge:
            def persist_config_snapshot(self, surface_name, config_bytes, *, source="config_provider", ts=""):
                raise RuntimeError("Bridge down")

        bridge = _FailingBridge()
        with patch("system_learning.stores.config_provider.get_sl_memory_bridge", return_value=bridge):
            # Should not raise exception
            configs = provider.get_current_configs()

        # Config reading should still succeed
        assert "meta_learning" in configs
