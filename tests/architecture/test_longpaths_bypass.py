#!/usr/bin/env python3
"""
Regression test for LongPathsEnabled pre-flight bypass behavior.
Ensures dry-run mode warns but proceeds, while active mode still fails.
"""

import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_longpaths_dry_run_bypass():
    """Test that dry-run mode bypasses LongPathsEnabled with warning."""
    from agentic_core.L0_routing.scripts.execute_ssot import PreFlightValidator

    project_root = Path(__file__).parent.parent.parent

    # Mock Windows platform and disabled LongPathsEnabled
    with (
        patch("platform.system", return_value="Windows"),
        patch("winreg.OpenKey"),
        patch("winreg.QueryValueEx", return_value=(0, None)),
        patch("logging.warning") as mock_warning,
    ):
        # Test dry-run mode (should warn but proceed)
        validator = PreFlightValidator(project_root, dry_run=True)
        success, errors = validator.run_checks()

        # Should succeed (no errors) and log warning
        assert success, f"Dry-run should succeed but got errors: {errors}"
        assert len(errors) == 0, f"Dry-run should have no errors but got: {errors}"
        mock_warning.assert_called_once()
        assert "LongPathsEnabled" in str(mock_warning.call_args)

        print("✅ Dry-run bypass test PASSED")


def test_longpaths_active_mode_fails():
    """Test that active mode still fails when LongPathsEnabled is disabled."""
    from agentic_core.L0_routing.scripts.execute_ssot import PreFlightValidator

    project_root = Path(__file__).parent.parent.parent

    # Mock Windows platform and disabled LongPathsEnabled
    with (
        patch("platform.system", return_value="Windows"),
        patch("winreg.OpenKey"),
        patch("winreg.QueryValueEx", return_value=(0, None)),
    ):
        # Test active mode (should fail)
        validator = PreFlightValidator(project_root, dry_run=False)
        success, errors = validator.run_checks()

        # Should fail with LongPathsEnabled error
        assert not success, "Active mode should fail when LongPathsEnabled is disabled"
        assert len(errors) > 0, "Active mode should have errors"
        assert any("LongPathsEnabled" in error for error in errors)

        print("✅ Active mode failure test PASSED")


def test_longpaths_enabled_succeeds():
    """Test that enabled LongPathsEnabled succeeds in both modes."""
    from agentic_core.L0_routing.scripts.execute_ssot import PreFlightValidator

    project_root = Path(__file__).parent.parent.parent

    # Mock Windows platform and enabled LongPathsEnabled
    with (
        patch("platform.system", return_value="Windows"),
        patch("winreg.OpenKey"),
        patch("winreg.QueryValueEx", return_value=(1, None)),
    ):
        # Test both modes
        for dry_run in [True, False]:
            validator = PreFlightValidator(project_root, dry_run=dry_run)
            success, errors = validator.run_checks()

            # Should succeed in both modes when LongPathsEnabled is enabled
            assert success, f"Should succeed when LongPathsEnabled is enabled (dry_run={dry_run})"
            assert len(errors) == 0, (
                f"Should have no errors when LongPathsEnabled is enabled (dry_run={dry_run})"
            )

        print("✅ LongPathsEnabled success test PASSED")


if __name__ == "__main__":
    print("Running LongPathsEnabled bypass regression tests...")

    try:
        test_longpaths_dry_run_bypass()
        test_longpaths_active_mode_fails()
        test_longpaths_enabled_succeeds()
        print("\n🎉 All regression tests PASSED")
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        sys.exit(1)
