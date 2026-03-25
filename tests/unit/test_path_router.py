"""
Unit tests for L0 Path Router - deterministic path selection.
"""

import pytest

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L0_routing.engines.path_router import Path, PathRouter
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_path_router")
# REMOVED: _emit_applies_guardrail("p0", "test_path_router", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_path_router", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_path_router", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_path_router", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_path_router", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_path_router", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_path_router", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_path_router", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_path_router", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_path_router", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_path_router", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_path_router", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_path_router", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_path_router", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_path_router", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_path_router", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_path_router", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_path_router", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_path_router", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_path_router", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_path_router", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_path_router", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_path_router", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_path_router", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_path_router", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_path_router", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_path_router", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_path_router", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_path_router", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_path_router", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_path_router", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_path_router", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_path_router", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_path_router", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_path_router", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_path_router", "write_through")
# REMOVED: _emit_writes_through("p1", "test_path_router", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_path_router", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_path_router", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_path_router", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_path_router", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_path_router", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_path_router", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_path_router", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_path_router", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_path_router", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_path_router", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_path_router", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_path_router", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_path_router", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_path_router", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_path_router")
# REMOVED: _emit_gated_by_confidence("p1", "test_path_router", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_path_router")
# REMOVED: emit_determinism_digest("p0", "test_path_router")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_path_router", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_path_router", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_path_router", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_path_router", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_path_router", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_path_router", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_path_router", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_path_router", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_path_router", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_path_router", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_path_router", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_path_router", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_path_router", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_path_router", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_path_router", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_path_router", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_path_router", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_path_router", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_path_router", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_path_router", "exec_snapshot_link")


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
class TestPathRouter:
    """Test deterministic PathRouter implementation."""

    def test_path_enum_values(self):
        """Test Path enum has correct values."""
        assert Path.A.value == "A"
        assert Path.B.value == "B"
        assert Path.C.value == "C"
        assert Path.D.value == "D"

    def test_empty_check_ids_selects_path_a(self):
        """Test empty check_ids always selects Path.A."""
        payload = GovernedPayload(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Simple prompt",
            check_ids=(),  # Empty tuple
            sanitized=False,
            d0_injections="",
        )

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.A

    def test_sanitized_payload_selects_path_b(self):
        """Test sanitized payload selects Path.B."""
        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Prompt with [ADMIN] marker",
        )

        # Verify payload is sanitized
        assert payload.sanitized is True
        assert payload.check_ids  # Non-empty to avoid Path.A

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.B

    def test_single_check_id_selects_path_c(self):
        """Test single check_id selects Path.C."""
        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Single task prompt",
        )

        # Verify single check_id and not sanitized
        assert len(payload.check_ids) == 1
        assert payload.sanitized is False

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.C

    def test_multiple_check_ids_selects_path_d(self):
        """Test multiple check_ids selects Path.D."""
        prompt = """1. First task
2. Second task
3. Third task"""

        payload = AirlockAssembler.assemble(
            s0_system="System", i0_instructional="Instructions", c0_context="Context", u0_user_prompt=prompt
        )

        # Verify multiple check_ids and not sanitized
        assert len(payload.check_ids) > 1
        assert payload.sanitized is False

        router = PathRouter()
        selected = router.select_path(payload)

        assert selected == Path.D

    def test_deterministic_selection_identical_payloads(self):
        """Test identical payloads produce identical path selection."""
        payload_args = {
            "s0_system": "System",
            "i0_instructional": "Instructions",
            "c0_context": "Context",
            "u0_user_prompt": "Test prompt",
        }

        payload1 = AirlockAssembler.assemble(**payload_args)
        payload2 = AirlockAssembler.assemble(**payload_args)

        router = PathRouter()
        path1 = router.select_path(payload1)
        path2 = router.select_path(payload2)

        assert path1 == path2

    def test_priority_order_empty_check_ids_overrides_sanitized(self):
        """Test empty check_ids takes priority over sanitized flag."""
        # Create a payload that would be sanitized but with empty check_ids
        payload = GovernedPayload(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Clean prompt",
            check_ids=(),  # Empty tuple
            sanitized=True,  # But empty check_ids should win
            d0_injections="",
        )

        router = PathRouter()
        selected = router.select_path(payload)

        # Should be Path.A due to empty check_ids, not Path.B
        assert selected == Path.A

    def test_priority_order_sanitized_over_single_check_id(self):
        """Test sanitized flag takes priority over single check_id."""
        payload = GovernedPayload(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Sanitized prompt",
            check_ids=("single_id",),
            sanitized=True,  # Should override single check_id
            d0_injections="",
        )

        router = PathRouter()
        selected = router.select_path(payload)

        # Should be Path.B due to sanitized flag, not Path.C
        assert selected == Path.B


@pytest.mark.unit
class TestElevatorShaftSeam:
    """Test Elevator Shaft seam contains no business logic."""

    def test_load_context_jit_returns_empty_dict(self):
        """Test seam returns deterministic empty dict."""
        from agentic_core.L0_routing.seams.elevator_shaft_seam import load_context_jit

        result = load_context_jit("test_intent")

        assert result == {}
        assert isinstance(result, dict)

    def test_seam_has_no_forbidden_imports(self):
        """Test seam contains no forbidden imports."""
        import ast

        seam_file = "agentic_core/L0_routing/seams/elevator_shaft_seam.py"

        # Read and parse the seam file
        with open(seam_file, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Check for forbidden imports
        forbidden_imports = ["L2_", "L5_", "datetime", "time"]
        found_forbidden = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(forbidden in alias.name for forbidden in forbidden_imports):
                        found_forbidden.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(forbidden in node.module for forbidden in forbidden_imports):
                    found_forbidden.append(f"from {node.module}")

        assert not found_forbidden, f"Forbidden imports found: {found_forbidden}"

    def test_seam_has_no_routing_logic(self):
        """Test seam contains no routing decision logic."""
        import ast

        seam_file = "agentic_core/L0_routing/seams/elevator_shaft_seam.py"

        with open(seam_file, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Check for control flow statements (routing logic)
        forbidden_nodes = (ast.If, ast.For, ast.While, ast.Try)
        found_nodes = []

        for node in ast.walk(tree):
            if isinstance(node, forbidden_nodes):
                found_nodes.append(type(node).__name__)

        assert not found_nodes, f"Control flow statements found: {found_nodes}"
