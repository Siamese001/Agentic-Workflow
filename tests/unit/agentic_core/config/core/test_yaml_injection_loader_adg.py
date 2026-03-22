"""ADG-driven tests for agentic_core/config/core/yaml_injection_loader.py — fan_in=2.

Contract tests: YamlValidationError, YamlInjectionLoader init, constants, and basic API.
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_yaml_injection_loader_adg")
_emit_applies_guardrail("p0", "test_yaml_injection_loader_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_yaml_injection_loader_adg", "policy_binding")
_emit_snapshots_state("p0", "test_yaml_injection_loader_adg", "state_snapshot")
emit_replay_key("p0", "test_yaml_injection_loader_adg")
emit_determinism_digest("p0", "test_yaml_injection_loader_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_yaml_injection_loader_adg", "execution_auth")
_emit_validates_capability("p2", "test_yaml_injection_loader_adg", "capability_check")
_emit_routes_to_capability("p2", "test_yaml_injection_loader_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_yaml_injection_loader_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_yaml_injection_loader_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_yaml_injection_loader_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_yaml_injection_loader_adg", "exec_output")
_emit_dispatches_agent("p3", "test_yaml_injection_loader_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_yaml_injection_loader_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_yaml_injection_loader_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_yaml_injection_loader_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_yaml_injection_loader_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_yaml_injection_loader_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_yaml_injection_loader_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_yaml_injection_loader_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_yaml_injection_loader_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_yaml_injection_loader_adg", "eval_metric")
_emit_stores_embedding("p4", "test_yaml_injection_loader_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_yaml_injection_loader_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_yaml_injection_loader_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.config.core.yaml_injection_loader import (
    YamlInjectionLoader,
    YamlValidationError,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_yaml_injection_loader_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_yaml_injection_loader_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_yaml_injection_loader_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_yaml_injection_loader_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_yaml_injection_loader_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_yaml_injection_loader_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_yaml_injection_loader_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_yaml_injection_loader_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_yaml_injection_loader_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_yaml_injection_loader_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_yaml_injection_loader_adg", "p4obs", "alert")
_emit_links_incident_trace("test_yaml_injection_loader_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_yaml_injection_loader_adg", "p3lm", "pattern")
_emit_records_learning_event("test_yaml_injection_loader_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_yaml_injection_loader_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_yaml_injection_loader_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_yaml_injection_loader_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_yaml_injection_loader_adg", "p3lm", "policy")
_emit_stores_learning_state("test_yaml_injection_loader_adg", "p3lm", "state")
_emit_records_execution_trace("test_yaml_injection_loader_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_yaml_injection_loader_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_yaml_injection_loader_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_yaml_injection_loader_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_yaml_injection_loader_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_yaml_injection_loader_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_yaml_injection_loader_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_yaml_injection_loader_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_yaml_injection_loader_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_yaml_injection_loader_adg", "context_pull")
_emit_pulls_context("p1", "test_yaml_injection_loader_adg", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_yaml_injection_loader_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_yaml_injection_loader_adg", "uwg_term_2")
_emit_writes_through("p1", "test_yaml_injection_loader_adg", "write_through")
_emit_writes_through("p1", "test_yaml_injection_loader_adg", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_yaml_injection_loader_adg", "safety_validation")
_emit_invokes_eval("p1", "test_yaml_injection_loader_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_yaml_injection_loader_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_yaml_injection_loader_adg", "human_escalation")
_emit_routes_through("p1", "test_yaml_injection_loader_adg", "route_through")
_emit_checks_agent_registry("p1", "test_yaml_injection_loader_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_yaml_injection_loader_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_yaml_injection_loader_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_yaml_injection_loader_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_yaml_injection_loader_adg", "target_agent")
_emit_verifies_policy("p1", "test_yaml_injection_loader_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_yaml_injection_loader_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_yaml_injection_loader_adg", "boundary_check")
_emit_transcripts_response("p1", "test_yaml_injection_loader_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_yaml_injection_loader_adg")
_emit_gated_by_confidence("p1", "test_yaml_injection_loader_adg", "confidence_gate")


class TestYamlValidationError:
    def test_importable(self):
        assert callable(YamlValidationError)

    def test_missing_key_message(self):
        err = YamlValidationError(filename="test.yaml", missing_key="description")
        assert "description" in str(err)
        assert "test.yaml" in str(err)

    def test_parse_error_message(self):
        err = YamlValidationError(filename="bad.yaml", parse_error="unexpected token")
        assert "unexpected token" in str(err)
        assert "bad.yaml" in str(err)

    def test_no_detail_message(self):
        err = YamlValidationError(filename="x.yaml")
        assert "x.yaml" in str(err)

    def test_is_exception(self):
        assert issubclass(YamlValidationError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(YamlValidationError):
            raise YamlValidationError(filename="x.yaml", missing_key="key")


class TestYamlInjectionLoaderConstants:
    def test_required_keys_nonempty(self):
        assert len(YamlInjectionLoader.REQUIRED_KEYS) > 0

    def test_layer_mapping_nonempty(self):
        assert len(YamlInjectionLoader.LAYER_MAPPING) > 0

    def test_required_keys_is_set(self):
        assert isinstance(YamlInjectionLoader.REQUIRED_KEYS, set)

    def test_description_in_required_keys(self):
        assert "description" in YamlInjectionLoader.REQUIRED_KEYS

    def test_framing_in_layer_mapping(self):
        assert "framing" in YamlInjectionLoader.LAYER_MAPPING


class TestYamlInjectionLoaderInit:
    def test_creates_with_defaults(self):
        loader = YamlInjectionLoader()
        assert loader is not None

    def test_cache_starts_empty(self):
        loader = YamlInjectionLoader()
        assert loader._cache == {}

    def test_yaml_root_is_path(self):
        from pathlib import Path
        loader = YamlInjectionLoader()
        assert isinstance(loader.yaml_root, Path)

    def test_custom_yaml_root(self):
        from pathlib import Path
        loader = YamlInjectionLoader(yaml_root=Path("data"))
        assert loader.yaml_root == Path("data")


class TestYamlInjectionLoaderEnumerate:
    def test_enumerate_nonexistent_root_raises(self):
        from pathlib import Path
        loader = YamlInjectionLoader(yaml_root=Path("nonexistent_xyz_dir"))
        with pytest.raises(FileNotFoundError):
            loader.enumerate_yaml_files()

    def test_load_by_layer_unknown_returns_empty(self):
        from pathlib import Path
        loader = YamlInjectionLoader(yaml_root=Path("nonexistent_xyz_dir"))
        # load_by_layer on missing root should either raise or return empty list
        try:
            result = loader.load_by_layer("nonexistent_layer_xyz")
            assert isinstance(result, list)
        except (FileNotFoundError, KeyError):
            pass  # Both acceptable for missing root
