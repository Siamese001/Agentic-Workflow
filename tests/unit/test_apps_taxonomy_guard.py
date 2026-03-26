"""
Unit tests for L0 Routing Apps Taxonomy Guard - deterministic import-graph checks.
"""

import tempfile
from pathlib import Path

import pytest

    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_apps_taxonomy_guard", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_apps_taxonomy_guard", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_apps_taxonomy_guard", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_apps_taxonomy_guard", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_apps_taxonomy_guard", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_apps_taxonomy_guard", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_apps_taxonomy_guard", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_apps_taxonomy_guard", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_apps_taxonomy_guard", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_apps_taxonomy_guard", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_apps_taxonomy_guard", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_apps_taxonomy_guard", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_apps_taxonomy_guard", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_apps_taxonomy_guard", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_apps_taxonomy_guard", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_apps_taxonomy_guard", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_apps_taxonomy_guard", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_apps_taxonomy_guard", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_apps_taxonomy_guard", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_apps_taxonomy_guard", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_apps_taxonomy_guard", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_apps_taxonomy_guard", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_apps_taxonomy_guard", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_apps_taxonomy_guard", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_apps_taxonomy_guard", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_apps_taxonomy_guard", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_apps_taxonomy_guard", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_apps_taxonomy_guard", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_apps_taxonomy_guard")
# REMOVED: _emit_applies_guardrail("p0", "test_apps_taxonomy_guard", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_apps_taxonomy_guard", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_apps_taxonomy_guard", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_apps_taxonomy_guard")
# REMOVED: emit_determinism_digest("p0", "test_apps_taxonomy_guard")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_apps_taxonomy_guard", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_apps_taxonomy_guard", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_apps_taxonomy_guard", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_apps_taxonomy_guard", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_apps_taxonomy_guard", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_apps_taxonomy_guard", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_apps_taxonomy_guard", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_apps_taxonomy_guard", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_apps_taxonomy_guard", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_apps_taxonomy_guard", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_apps_taxonomy_guard", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_apps_taxonomy_guard", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_apps_taxonomy_guard", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_apps_taxonomy_guard", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_apps_taxonomy_guard", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_apps_taxonomy_guard", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_apps_taxonomy_guard", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_apps_taxonomy_guard", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_apps_taxonomy_guard", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_apps_taxonomy_guard", "exec_snapshot_link")
# REMOVED: _emit_escalates_to_human("p1", "test_apps_taxonomy_guard", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_apps_taxonomy_guard", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_apps_taxonomy_guard", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_apps_taxonomy_guard", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_apps_taxonomy_guard", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_apps_taxonomy_guard", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_apps_taxonomy_guard", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_apps_taxonomy_guard", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_apps_taxonomy_guard", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_apps_taxonomy_guard", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_apps_taxonomy_guard", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_apps_taxonomy_guard")
# REMOVED: _emit_gated_by_confidence("p1", "test_apps_taxonomy_guard", "confidence_gate")


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
class TestAppsTaxonomyGuard:
    """Test AppsTaxonomyGuard AST-based import scanning."""

    def test_guard_initialization(self):
        """Test guard initializes with correct allowlist."""
        from agentic_core.L0_routing.enforcement.apps_taxonomy_guard import AppsTaxonomyGuard
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
            _emit_feeds_meta_learning,
            _emit_gated_by_confidence,
            _emit_hard_fails_untranscripted,
            _emit_improves_agent_policy,
            _emit_invokes_evaluation,
            _emit_links_execution_to_snapshot,
            _emit_links_incident_trace,
            _emit_observes_runtime_state,
            _emit_orchestrates_workflow,
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
            _emit_validates_agent_capability,
            _emit_validates_capability,
            _emit_verifies_boundary,
            _emit_verifies_policy,
            _emit_writes_learning_snapshot,
            _emit_writes_observability_log,
            _emit_writes_via_uwg,
            emit_determinism_digest,  # noqa: E402
            emit_replay_key,  # noqa: E402
        from agentic_core.interfaces import SomeInterface
        from agentic_core.prompt_governance.contracts import Contract
        from agentic_core.prompt_governance.contracts import Contract
        import agentic_core.interfaces.submodule
        import agentic_core.interfaces.submodule
        """)
        from agentic_core.L0_routing import PathRouter
        import agentic_core.L4_state
        import agentic_core.L4_state
        from agentic_core.L2_execution import CIDRegistry
        from agentic_core.L2_execution import CIDRegistry
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
            _emit_pulls_context,
            _emit_execution_terminates_at_uwg,
            _emit_writes_through,
            _emit_validated_by_safety_plane,
            _emit_invokes_eval,
            _emit_proposal_commits_routing,
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
            _emit_writes_through,  # noqa: E402
            _emit_links_incident_trace,  # noqa: E402

        guard = AppsTaxonomyGuard()

        expected_allowed = {
            "agentic_core.interfaces",
            "agentic_core.prompt_governance.contracts",
        }
        assert guard.ALLOWED_IMPORTS == expected_allowed

    def test_scan_empty_repository(self):
        """Test scan on repository with no apps_* directories."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            violations = guard.scan(repo_root=temp_dir)

            assert violations == ()

    def test_scan_apps_directory_with_allowed_imports(self):
        """Test scan detects no violations for allowed imports."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory with allowed imports
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create Python file with allowed imports
            py_file = apps_dir / "main.py"
            py_file.write_text("""
# Allowed imports
""")

            violations = guard.scan(repo_root=temp_dir)

            # Should have no violations
            assert violations == ()

    def test_scan_apps_directory_with_prohibited_imports(self):
        """Test scan detects violations for prohibited imports."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create Python file with prohibited imports
            py_file = apps_dir / "main.py"
            py_file.write_text("""
# Prohibited imports
    _emit_links_incident_trace,  # noqa: E402
)
# REMOVED: _emit_pulls_context("p1", "test_apps_taxonomy_guard", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_apps_taxonomy_guard", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_apps_taxonomy_guard", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_apps_taxonomy_guard", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_apps_taxonomy_guard", "write_through")
# REMOVED: _emit_writes_through("p1", "test_apps_taxonomy_guard", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_apps_taxonomy_guard", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_apps_taxonomy_guard", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_apps_taxonomy_guard", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_apps_taxonomy_guard", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_apps_taxonomy_guard", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_apps_taxonomy_guard", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_apps_taxonomy_guard", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_apps_taxonomy_guard", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_apps_taxonomy_guard", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_apps_taxonomy_guard", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_apps_taxonomy_guard", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_apps_taxonomy_guard", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_apps_taxonomy_guard", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_apps_taxonomy_guard", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_apps_taxonomy_guard")
# REMOVED: _emit_gated_by_confidence("p1", "test_apps_taxonomy_guard", "confidence_gate")
""")

            violations = guard.scan(repo_root=temp_dir)

            # Should detect violations
            assert len(violations) == 3

            # Check specific violations (sorted)
            assert "apps_demo/main.py:3 from agentic_core.L0_routing import PathRouter" in violations
            assert "apps_demo/main.py:4 import agentic_core.L4_state" in violations
            assert "apps_demo/main.py:5 from agentic_core.L2_execution import CIDRegistry" in violations

    def test_scan_multiple_apps_directories(self):
        """Test scan handles multiple apps_* directories."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create two apps directories
            apps1_dir = Path(temp_dir) / "apps_first"
            apps1_dir.mkdir()

            apps2_dir = Path(temp_dir) / "apps_second"
            apps2_dir.mkdir()

            # Create files with violations in both
            py_file1 = apps1_dir / "file1.py"
            py_file1.write_text("from agentic_core.L5_safety import RiskGate\n")

            py_file2 = apps2_dir / "file2.py"
            py_file2.write_text("import agentic_core.L6_observability\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should detect violations from both directories
            assert len(violations) == 2

            # Violations should be sorted by path and content
            expected_violations = [
                "apps_first/file1.py:1 from agentic_core.L5_safety import RiskGate",
                "apps_second/file2.py:1 import agentic_core.L6_observability",
            ]
            assert violations == tuple(expected_violations)

    def test_scan_nested_python_files(self):
        """Test scan finds violations in nested Python files."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested directory structure
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            nested_dir = apps_dir / "submodule"
            nested_dir.mkdir()

            # Create file in nested directory
            py_file = nested_dir / "deep.py"
            py_file.write_text("from agentic_core.L0_routing.meta_control import MetaLearningBus\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should detect violation with correct path
            assert len(violations) == 1
            assert (
                "submodule/deep.py:1 from agentic_core.L0_routing.meta_control import MetaLearningBus"
                in violations[0]
            )

    def test_scan_ignores_non_python_files(self):
        """Test scan ignores non-Python files."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create non-Python files with agentic_core content
            txt_file = apps_dir / "config.txt"
            txt_file.write_text("import agentic_core.L0_routing\n")

            md_file = apps_dir / "readme.md"
            md_file.write_text("from agentic_core.L4_state import Something\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should have no violations (non-Python files ignored)
            assert violations == ()

    def test_scan_handles_syntax_errors_gracefully(self):
        """Test scan skips files with syntax errors."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create file with syntax error
            bad_file = apps_dir / "bad.py"
            bad_file.write_text("from agentic_core.L0_routing import  # incomplete\n")

            # Create valid file with violation
            good_file = apps_dir / "good.py"
            good_file.write_text("from agentic_core.L4_state import State\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should only detect violation from valid file
            assert len(violations) == 1
            assert "good.py:1 from agentic_core.L4_state import State" in violations[0]

    def test_deterministic_ordering_violations(self):
        """Test violations are returned in deterministic sorted order."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create multiple files with violations
            files_and_imports = [
                ("z_file.py", "import agentic_core.L4_state"),
                ("a_file.py", "from agentic_core.L0_routing import Path"),
                ("m_file.py", "import agentic_core.L2_execution"),
            ]

            for filename, import_stmt in files_and_imports:
                py_file = apps_dir / filename
                py_file.write_text(f"{import_stmt}\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should be sorted by filename and content
            expected_violations = [
                "apps_demo/a_file.py:1 from agentic_core.L0_routing import Path",
                "apps_demo/m_file.py:1 import agentic_core.L2_execution",
                "apps_demo/z_file.py:1 import agentic_core.L4_state",
            ]
            assert violations == tuple(expected_violations)

    def test_is_allowed_import_exact_match(self):
        """Test _is_allowed_import with exact matches."""
        guard = AppsTaxonomyGuard()

        # Allowed exact matches
        assert guard._is_allowed_import("agentic_core.interfaces") is True
        assert guard._is_allowed_import("agentic_core.prompt_governance.contracts") is True

        # Prohibited imports
        assert guard._is_allowed_import("agentic_core.L0_routing") is False
        assert guard._is_allowed_import("agentic_core.L4_state") is False

    def test_is_allowed_import_submodule_match(self):
        """Test _is_allowed_import with submodule matches."""
        guard = AppsTaxonomyGuard()

        # Allowed submodule imports
        assert guard._is_allowed_import("agentic_core.interfaces.api") is True
        assert guard._is_allowed_import("agentic_core.prompt_governance.contracts.v2") is True

        # Prohibited submodule imports
        assert guard._is_allowed_import("agentic_core.L0_routing.engines") is False
        assert guard._is_allowed_import("agentic_core.L4_state.storage") is False

    def test_scan_with_multiple_imports_per_line(self):
        """Test scan handles multiple imports on same line."""
        guard = AppsTaxonomyGuard()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create apps_demo directory
            apps_dir = Path(temp_dir) / "apps_demo"
            apps_dir.mkdir()

            # Create file with multiple imports
            py_file = apps_dir / "multi.py"
            py_file.write_text("from agentic_core.L0_routing import PathRouter, MetaLearningBus\n")

            violations = guard.scan(repo_root=temp_dir)

            # Should detect one violation with all imported names
            assert len(violations) == 1
            assert (
                "multi.py:1 from agentic_core.L0_routing import PathRouter, MetaLearningBus" in violations[0]
            )
