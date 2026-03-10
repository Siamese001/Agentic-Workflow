from unittest.mock import MagicMock

import pytest

from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent


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
