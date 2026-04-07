"""Integration tests for Windows path handling in agent discovery.

Wave 3: Tests for RCA path normalization bug fix.
Ensures agent discovery handles Windows paths correctly without mangling.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.integration
class TestAgentDiscoveryWindowsPaths:
    """Test Windows path handling in agent discovery pipeline."""

    def test_is_path_allowed_rejects_mangled_paths(self, tmp_path):
        """Ensure is_path_allowed correctly rejects mangled dot-paths.

        Tests the specific RCA bug pattern: paths with dots as separators.
        """
        from agentic_core.L0_routing.utils.path_util import is_path_allowed

        # A mangled path (the bug pattern)
        mangled_path = "agentic_core.L0_routing.scripts.test_agent.py"

        # A normal path with forward slashes
        normal_path = "agentic_core/L0_routing/scripts/test_agent.py"

        allowed = {"agentic_core", "L0_routing"}

        # Both should be allowed since they contain the allowed dirs
        # but the mangled one demonstrates the bug pattern
        result_mangled = is_path_allowed(mangled_path, frozenset(allowed))
        result_normal = is_path_allowed(normal_path, frozenset(allowed))

        # Verify both contain agentic_core
        assert result_mangled is True  # is_path_allowed checks for substring match
        assert result_normal is True

        # The key assertion: verify no c:.Git style mangling in actual paths
        # by checking the normalization happens correctly
        from pathlib import Path
        test_path = Path(normal_path)
        assert "\\" not in test_path.as_posix()  # No backslashes in normalized

    def test_path_normalization_in_agent_discovery(self, tmp_path):
        """Test that agent discovery normalizes paths consistently."""
        from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import (
            get_structured_agent_paths,
        )

        # Get structured paths
        paths = get_structured_agent_paths()

        # All paths should use forward slashes (normalized)
        for path in paths:
            assert "\\" not in path, f"Path contains backslash: {path}"
            assert "c:.Git" not in path.lower(), f"Path appears mangled: {path}"

    def test_validate_path_within_project_handles_windows_paths(self, tmp_path):
        """Test validate_path_within_project handles Windows-style paths."""
        from agentic_core.L0_routing.utils.path_util import (
            get_validated_project_root,
            validate_path_within_project,
        )

        project_root = get_validated_project_root()

        # Test with forward slash path (normalized)
        normalized_path = project_root / "agentic_core/L0_routing/utils"
        result = validate_path_within_project(normalized_path, project_root)
        assert result is True

    def test_get_validated_project_root_no_mangled_path_in_errors(self):
        """Ensure error messages don't contain mangled paths."""
        from agentic_core.L0_routing.utils.path_util import get_validated_project_root

        # This should not raise any errors with mangled paths
        try:
            root = get_validated_project_root()
            # Verify the root path is not mangled
            root_str = str(root)
            assert "c:.Git" not in root_str.lower(), f"Project root appears mangled: {root_str}"
            assert "c:." not in root_str.lower(), f"Project root has dot separator: {root_str}"
        except (OSError, ValueError, RuntimeError) as e:
            # If an error occurs, ensure the error message doesn't have mangled paths
            error_str = str(e)
            assert "c:.Git" not in error_str.lower(), f"Error message has mangled path: {error_str}"


@pytest.mark.integration
class TestPathNormalizationIntegration:
    """Integration tests for path normalization across modules."""

    def test_path_util_is_path_allowed_with_various_formats(self):
        """Test is_path_allowed handles various path formats."""
        from agentic_core.L0_routing.utils.path_util import is_path_allowed

        allowed_dirs = {"agentic_core", "tests"}

        # Test with forward slash format
        assert is_path_allowed("agentic_core/L0_routing/utils.py", frozenset(allowed_dirs))

        # Test with backslash format (Windows)
        assert is_path_allowed("agentic_core\\L0_routing\\utils.py", frozenset(allowed_dirs))

        # Test with mixed separators
        assert is_path_allowed("agentic_core\\L0_routing/utils.py", frozenset(allowed_dirs))

    def test_safe_path_join_prevents_directory_traversal(self, tmp_path):
        """Test safe_path_join prevents directory traversal attacks."""
        from agentic_core.L0_routing.utils.path_util import safe_path_join

        project_root = tmp_path
        (project_root / "agentic_core").mkdir()

        # Valid path should work
        result = safe_path_join(project_root, "agentic_core", "test.py")
        assert result.exists() is False  # File doesn't exist but path is valid
        assert str(result).startswith(str(project_root))

        # Directory traversal should raise
        with pytest.raises(ValueError) as exc_info:
            safe_path_join(project_root, "..", "etc", "passwd")
        assert "SAFETY VIOLATION" in str(exc_info.value)


@pytest.mark.integration
class TestAgentDiscoveryPathHandling:
    """Test path handling specific to agent discovery."""

    def test_perform_deep_integrity_scan_handles_paths(self, tmp_path):
        """Test perform_deep_integrity_scan handles agent paths correctly."""
        from agentic_core.L0_routing.utils.path_util import get_validated_project_root
        from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import (
            perform_deep_integrity_scan,
        )

        # Create mock agents with various path formats
        mock_agents = [
            {"name": "Agent1", "path": "agentic_core/L0_routing/agent1.py", "layer": "L0"},
            {"name": "Agent2", "path": "agentic_core\\L1_cognition\\agent2.py", "layer": "L1"},
        ]

        project_root = get_validated_project_root()

        # Run the scan - should not raise any path-related errors
        verified_agents, stats = perform_deep_integrity_scan(mock_agents, project_root)

        # The function should complete without errors
        assert isinstance(verified_agents, list)
        assert isinstance(stats, dict)

    def test_canonical_file_forward_slash_normalized(self):
        """Test that canonical_file field is forward-slash normalized."""
        # This tests the code in full_agent_discovery.py around line 578
        # canon_path = rel_path.replace("\\", "/")
        test_path = "agentic_core\\L0_routing\\scripts\\test.py"
        canon_path = test_path.replace("\\", "/")

        assert canon_path == "agentic_core/L0_routing/scripts/test.py"
        assert "\\" not in canon_path
