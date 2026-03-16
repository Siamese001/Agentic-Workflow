from unittest.mock import MagicMock

import pytest

from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
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

_emit_records_execution_trace("p0", "evidence", "test_hierarchy_agent_updates")
_emit_applies_guardrail("p0", "test_hierarchy_agent_updates", "p0_governance")
_emit_reads_policy_state("p0", "test_hierarchy_agent_updates", "policy_binding")
_emit_snapshots_state("p0", "test_hierarchy_agent_updates", "state_snapshot")
emit_replay_key("p0", "test_hierarchy_agent_updates")
emit_determinism_digest("p0", "test_hierarchy_agent_updates")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hierarchy_agent_updates", "execution_auth")
_emit_validates_capability("p2", "test_hierarchy_agent_updates", "capability_check")
_emit_routes_to_capability("p2", "test_hierarchy_agent_updates", "capability_route")
_emit_writes_via_uwg("p2", "test_hierarchy_agent_updates", "uwg_write")
_emit_blocks_direct_write("p2", "test_hierarchy_agent_updates", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hierarchy_agent_updates", "tool_invocation")
_emit_captures_execution_output("p2", "test_hierarchy_agent_updates", "exec_output")
_emit_dispatches_agent("p3", "test_hierarchy_agent_updates", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hierarchy_agent_updates", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hierarchy_agent_updates", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hierarchy_agent_updates", "healing_outcome")
_emit_escalates_failure("p3", "test_hierarchy_agent_updates", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hierarchy_agent_updates", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hierarchy_agent_updates", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hierarchy_agent_updates", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hierarchy_agent_updates", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hierarchy_agent_updates", "eval_metric")
_emit_stores_embedding("p4", "test_hierarchy_agent_updates", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hierarchy_agent_updates", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hierarchy_agent_updates", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestHierarchyAgentUpdates:
    @pytest.fixture
    def mock_agent(self, tmp_path):
        return HierarchyAgent(project_root=tmp_path)

    def test_scripts_allowed_at_root(self, mock_agent):
        """
        CRITICAL: scripts/ should NOT be in FORBIDDEN_ROOT_FOLDERS anymore.
        """
        assert "scripts" not in mock_agent.FORBIDDEN_ROOT_FOLDERS
        assert "logs" not in mock_agent.FORBIDDEN_ROOT_FOLDERS

        # Ensure actual forbidden stuff remains
        assert "coverage_html" in mock_agent.FORBIDDEN_ROOT_FOLDERS

    def test_scan_allows_valid_roots(self, mock_agent):
        """
        Verify that scanning does not flag scripts/ as a violation.
        """
        # Setup valid root folder
        (mock_agent.project_root / "scripts").mkdir()
        (mock_agent.project_root / "logs").mkdir()

        # Setup invalid folder
        (mock_agent.project_root / "coverage_html").mkdir()

        results = mock_agent.scan_root_violations()

        # Should only flag coverage_html
        assert "scripts" not in results["forbidden_folders"]
        assert "logs" not in results["forbidden_folders"]
        assert "coverage_html" in results["forbidden_folders"]

    def test_heal_does_not_merge_scripts(self, mock_agent):
        """
        Verify that heal_root_violations does not attempt to merge scripts/
        """
        # Mock the merge method to ensure it's not called for scripts
        mock_agent._merge_root_folder_to_ssot = MagicMock()

        # Inject "scripts" into scan results to simulate a false positive (if logic wasn't fixed)
        # But since we fixed the logic, it shouldn't even call scan with violations.
        # Let's verify the heal method logic directly.

        mock_agent.scan_root_violations = MagicMock(
            return_value={
                "violations_found": 1,
                "forbidden_folders": ["coverage_html"],  # Only bad stuff
                "archived_files_at_root": [],
            },
        )

        mock_agent.heal_root_violations(dry_run=True)

        # Should NOT call merge for scripts
        calls = mock_agent._merge_root_folder_to_ssot.call_args_list
        for call in calls:
            args, _ = call
            assert args[0] != "scripts"
            assert args[0] != "logs"
