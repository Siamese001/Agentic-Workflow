"""
Architectural integrity tests for module collision prevention.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch


class TestModuleCollisionGuard:
    """Test the module collision guard functionality."""

    def test_guard_no_growth_against_baseline(self):
        """Ensure guard passes when current collisions match baseline."""
        # Add tools to path
        tools_path = Path(__file__).parent.parent.parent / "tools" / "architectural"
        sys.path.insert(0, str(tools_path))

        try:
            from module_collision_guard import main
        finally:
            sys.path.remove(str(tools_path))

        # Run guard in default mode (no baseline update)
        # Should pass since we have the baseline file
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)

    def test_guard_blocks_new_collision_growth(self):
        """Ensure guard fails when new collisions are introduced."""
        # Add tools to path
        tools_path = Path(__file__).parent.parent.parent / "tools" / "architectural"
        sys.path.insert(0, str(tools_path))

        try:
            from module_collision_guard import (
                check_against_baseline,
                detect_collisions,
                load_baseline,
                scan_directory,
            )
        finally:
            sys.path.remove(str(tools_path))

        # Load current baseline
        baseline = load_baseline()

        # Scan current state
        roots_to_scan = {
            "agentic_core": Path("agentic_core"),
            "apps_lic": Path("apps_lic"),
            "apps_rg": Path("apps_rg"),
            "apps_shared": Path("apps_shared"),
            "tools": Path("tools"),
            "ops_scripts": Path("ops_scripts"),
        }

        available_roots = {name: path for name, path in roots_to_scan.items() if path.exists()}

        scans = {}
        for root_name, root_path in available_roots.items():
            scans[root_name] = scan_directory(root_path)

        # Get current collisions
        collisions = detect_collisions(scans)

        # Simulate adding a new collision by monkeypatching the result
        mock_collisions = collisions.copy()
        if "duplicate_filenames" not in mock_collisions:
            mock_collisions["duplicate_filenames"] = []

        # Add a new collision that's not in baseline
        mock_collisions["duplicate_filenames"].append((
            "agentic_core:new_collision_file",
            [("agentic_core", Path("agentic_core/fake1.py")), ("agentic_core", Path("agentic_core/fake2.py"))]
        ))

        # Check against baseline - should detect new collision
        violations = check_against_baseline(mock_collisions, baseline)

        assert len(violations) > 0, "Should detect new collision growth"
        assert any("NEW filename collision: new_collision_file" in v for v in violations), "Should identify the new collision"

    def test_guard_baseline_update_mode(self):
        """Test baseline update mode works correctly."""
        # Add tools to path
        tools_path = Path(__file__).parent.parent.parent / "tools" / "architectural"
        sys.path.insert(0, str(tools_path))

        try:
            # Import the module fresh to avoid side effects
            import importlib

            import module_collision_guard
            importlib.reload(module_collision_guard)
            from module_collision_guard import main
        finally:
            sys.path.remove(str(tools_path))

        # Run guard in update mode
        with patch.dict(os.environ, {"MODULE_COLLISION_UPDATE_BASELINE": "1"}):
            with patch('sys.exit') as mock_exit:
                main()
                # Should be called at least once with exit code 0
                assert mock_exit.call_count >= 1
                assert any(call[0][0] == 0 for call in mock_exit.call_args_list)
