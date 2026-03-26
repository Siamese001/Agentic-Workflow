"""Guardian tests for G-16-6 — Activation Gate enforcement.

Validates:
1. Happy path: all components present → no raise.
2. Missing component denial (3 tests): each missing component → PermissionError.
3. Structural wiring: orchestrate() calls assert_activation_allowed.
4. Fail-closed proof: version marker present, gate raises on any missing component.
"""

from __future__ import annotations

import ast
import sys
import types
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
#  # MOVED: from agentic_core.L5_safety.enforcement.activation_gate import (
    ACTIVATION_GATE_VERSION,
    assert_activation_allowed,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_activation_gate", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_activation_gate", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_activation_gate", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_activation_gate", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_activation_gate", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_activation_gate", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_activation_gate", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_activation_gate", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_activation_gate", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_activation_gate", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_activation_gate", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_activation_gate", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_activation_gate", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_activation_gate", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_activation_gate", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_activation_gate", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_activation_gate", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_activation_gate", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_activation_gate", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_activation_gate", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_activation_gate", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_activation_gate", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_activation_gate", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_activation_gate", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_activation_gate", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_activation_gate", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_activation_gate", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_activation_gate", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_activation_gate")
# REMOVED: _emit_applies_guardrail("p0", "test_activation_gate", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_activation_gate", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_activation_gate", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_activation_gate", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_activation_gate", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_activation_gate", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_activation_gate", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_activation_gate", "write_through")
# REMOVED: _emit_writes_through("p1", "test_activation_gate", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_activation_gate", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_activation_gate", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_activation_gate", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_activation_gate", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_activation_gate", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_activation_gate", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_activation_gate", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_activation_gate", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_activation_gate", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_activation_gate", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_activation_gate", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_activation_gate", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_activation_gate", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_activation_gate", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_activation_gate")
# REMOVED: _emit_gated_by_confidence("p1", "test_activation_gate", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_activation_gate")
# REMOVED: emit_determinism_digest("p0", "test_activation_gate")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_activation_gate", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_activation_gate", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_activation_gate", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_activation_gate", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_activation_gate", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_activation_gate", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_activation_gate", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_activation_gate", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_activation_gate", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_activation_gate", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_activation_gate", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_activation_gate", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_activation_gate", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_activation_gate", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_activation_gate", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_activation_gate", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_activation_gate", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_activation_gate", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_activation_gate", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_activation_gate", "exec_snapshot_link")

# =====================================================================
# 1. Happy path
# =====================================================================


class TestHappyPath:
    """All enforcement modules present → gate allows."""

    def test_all_components_present_no_raise(self):
        from agentic_core.L0_routing.config.path_constants import (
        from agentic_core.L5_safety.enforcement.activation_gate import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        """With real modules present, assert_activation_allowed must not raise."""
        assert_activation_allowed()

    def test_all_components_present_with_trace_id(self):
        """With trace_id supplied, still passes when modules present."""
        assert_activation_allowed(trace_id="trace-happy-path")


# =====================================================================
# 2. Missing component denial
# =====================================================================


class TestMissingComponentDenial:
    """Each missing component must trigger PermissionError (FAIL-CLOSED)."""

    def test_missing_capability_chokepoint(self, monkeypatch):
        """Missing capability_chokepoint → PermissionError."""
        mod_key = "agentic_core.L2_execution.enforcement.capability_chokepoint"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError, match="capability_chokepoint"):
                assert_activation_allowed(trace_id="trace-missing-cc")
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)

    def test_missing_mutation_prohibition(self, monkeypatch):
        """Missing mutation_prohibition → PermissionError."""
        mod_key = "agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError, match="mutation_prohibition"):
                assert_activation_allowed(trace_id="trace-missing-mp")
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)

    def test_missing_healer_pipe_order(self, monkeypatch):
        """Missing healer_pipe_order → PermissionError."""
        mod_key = "agentic_core.L2_execution.enforcement.healer_pipe_order"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError, match="healer_pipe_order"):
                assert_activation_allowed(trace_id="trace-missing-hpo")
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)

    def test_multiple_missing_lists_all(self, monkeypatch):
        """Multiple missing → PermissionError lists all missing keys."""
        keys = [
            "agentic_core.L2_execution.enforcement.capability_chokepoint",
            "agentic_core.L2_execution.enforcement.healer_pipe_order",
        ]
        originals = {k: sys.modules.get(k) for k in keys}
        for k in keys:
            monkeypatch.setitem(sys.modules, k, None)
        try:
            with pytest.raises(PermissionError) as exc_info:
                assert_activation_allowed()
            msg = str(exc_info.value)
            assert "capability_chokepoint" in msg
            assert "healer_pipe_order" in msg
        finally:
            for k in keys:
                if originals[k] is not None:
                    sys.modules[k] = originals[k]
                else:
                    sys.modules.pop(k, None)

    def test_missing_symbol_on_module(self, monkeypatch):
        """Module importable but symbol missing → PermissionError."""
        mod_key = "agentic_core.L2_execution.enforcement.capability_chokepoint"
        original = sys.modules.get(mod_key)
        # Create a stub module without authorize_and_execute
        stub = types.ModuleType(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, stub)
        try:
            with pytest.raises(PermissionError, match="capability_chokepoint"):
                assert_activation_allowed()
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)


# =====================================================================
# 3. Structural wiring
# =====================================================================


class TestStructuralWiring:
    """Verify that the canonical runtime entrypoint calls the activation gate."""

    def test_orchestrate_calls_activation_gate(self):
    """Test orchestrate_calls_activation_gate runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute orchestrate_calls_activation_gate
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
                        if isinstance(child, ast.Call):
                            func = child.func
                            if isinstance(func, ast.Name) and func.id == "assert_activation_allowed":
                                found_in_orchestrate = True
                            elif isinstance(func, ast.Attribute) and func.attr == "assert_activation_allowed":
                                found_in_orchestrate = True

        assert found_in_orchestrate, (
            "assert_activation_allowed() not found in orchestrate() body. "
            "G-16-6 activation gate is not wired."
        )

    def test_activation_gate_import_present(self):
        """unified_workflow_config.py must import assert_activation_allowed."""
        config_path = Path("agentic_core/L2_execution/config/unified_workflow_config.py")
        source = config_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "activation_gate" in node.module:
                    for alias in node.names:
                        if alias.name == "assert_activation_allowed":
                            imported = True

        assert imported, "assert_activation_allowed not imported in unified_workflow_config.py"

    def test_single_activation_gate_module(self):
        """Exactly one activation_gate.py must exist under agentic_core/."""
        matches = list(Path(AGENTIC_CORE_DIR).rglob("activation_gate.py"))
        assert len(matches) == 1, f"Expected 1 activation_gate.py, found {len(matches)}: {matches}"

    @pytest.mark.skip(reason="dashboard_e2_e_pipeline.py not yet created — infrastructure pending")
    def test_dashboard_e2e_pipeline_calls_activation_gate(self):
    """Test dashboard_e2e_pipeline_calls_activation_gate runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute dashboard_e2e_pipeline_calls_activation_gate
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
                        if isinstance(child, ast.Call):
                            func = child.func
                            if isinstance(func, ast.Name) and func.id == "assert_activation_allowed":
                                found_in_run = True
                            elif isinstance(func, ast.Attribute) and func.attr == "assert_activation_allowed":
                                found_in_run = True

        assert found_in_run, (
            "assert_activation_allowed() not found in run() body of dashboard_e2e_pipeline.py. "
            "G-16-6 activation gate is not wired."
        )


# =====================================================================
# 4. Fail-closed proof
# =====================================================================


class TestFailClosedProof:
    """Prove the gate is fail-closed by design."""

    def test_version_marker_present(self):
        """ACTIVATION_GATE_VERSION must be a non-empty string."""
        assert isinstance(ACTIVATION_GATE_VERSION, str)
        assert len(ACTIVATION_GATE_VERSION) > 0

    def test_version_marker_value(self):
        """Version marker must match expected value."""
        assert ACTIVATION_GATE_VERSION == "v5.4-P0"

    def test_denial_message_is_deterministic(self, monkeypatch):
        """PermissionError message must be deterministic and contain version."""
        mod_key = "agentic_core.L2_execution.enforcement.healer_pipe_order"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError) as exc_info:
                assert_activation_allowed(trace_id="det-trace")
            msg = str(exc_info.value)
            assert "ACTIVATION_DENIED" in msg
            assert "v5.4-P0" in msg
            assert "healer_pipe_order" in msg
            assert "trace_id=det-trace" in msg
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)

    def test_denial_without_trace_id(self, monkeypatch):
        """Denial message must not contain trace_id when not supplied."""
        mod_key = "agentic_core.L2_execution.enforcement.healer_pipe_order"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError) as exc_info:
                assert_activation_allowed()
            msg = str(exc_info.value)
            assert "trace_id" not in msg
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)
