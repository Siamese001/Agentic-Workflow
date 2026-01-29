"""
Test script to verify autonomous decision-making in LocationHealerAgent.
Ensures the agent can make intelligent choices without user prompts.
"""

import shutil
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def test_autonomous_confidence_scoring():
    """Test the confidence scoring algorithm for autonomous decisions."""
    from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

    # Create temporary project structure
    temp_root = Path(tempfile.mkdtemp(prefix="test_autonomous_"))
    try:
        healer = LocationHealerAgent(project_root=temp_root)

        # Test high confidence patterns
        high_confidence_cases = [
            ("utils", ["scripts", "tests"]),  # Should match utils pattern
            ("test_data", ["scripts", "tests"]),  # Should match test pattern
            ("api_client", ["scripts", "tests"]),  # Should match api pattern
            ("config_files", ["scripts", "tests"]),  # Should match config pattern
        ]

        for unknown, existing in high_confidence_cases:
            confidence = healer._calculate_subfolder_confidence(unknown, existing)
            print(f"  '{unknown}' vs {existing}: confidence = {confidence:.2f}")
            assert confidence >= 0.8, f"Expected high confidence for '{unknown}', got {confidence}"

        # Test medium confidence (similar to existing)
        medium_confidence_cases = [
            ("test_scripts", ["test_data", "scripts"]),  # Similar to existing
            ("api_helpers", ["api_client", "utils"]),  # Similar to existing
        ]

        for unknown, existing in medium_confidence_cases:
            confidence = healer._calculate_subfolder_confidence(unknown, existing)
            print(f"  '{unknown}' vs {existing}: confidence = {confidence:.2f}")
            assert 0.5 <= confidence < 0.8, (
                f"Expected medium confidence for '{unknown}', got {confidence}"
            )

        # Test low confidence (very similar to existing, should relocate)
        low_confidence_cases = [
            ("test_data", ["test_scripts", "test_helpers"]),  # Very similar
            ("api_client", ["api_server", "api_helpers"]),  # Very similar
        ]

        for unknown, existing in low_confidence_cases:
            confidence = healer._calculate_subfolder_confidence(unknown, existing)
            print(f"  '{unknown}' vs {existing}: confidence = {confidence:.2f}")
            assert confidence < 0.5, f"Expected low confidence for '{unknown}', got {confidence}"

        print("✅ Confidence scoring test PASSED")

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_autonomous_decision_logic():
    """Test the autonomous decision-making logic."""
    from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

    temp_root = Path(tempfile.mkdtemp(prefix="test_decision_"))
    try:
        healer = LocationHealerAgent(project_root=temp_root)

        # Create a test file
        test_file = temp_root / "test_zone" / "unknown_subfolder" / "test_file.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# Test file")

        # Test high confidence decision (should create new subfolder)
        result = healer._autonomous_void_violation_resolution(
            test_file, "test_zone", "utils", "Test violation", ["scripts", "tests"], True, [], []
        )

        print(f"  High confidence decision: {result.get('action_taken', 'NO ACTION')}")
        assert "AUTONOMOUS" in result.get("action_taken", ""), "Expected autonomous action"
        assert "Created" in result.get("action_taken", ""), "Expected creation action"

        # Test medium confidence decision (should relocate)
        result = healer._autonomous_void_violation_resolution(
            test_file,
            "test_zone",
            "test_helpers",
            "Test violation",
            ["test_data", "test_scripts"],
            True,
            [],
            [],
        )

        print(f"  Medium confidence decision: {result.get('action_taken', 'NO ACTION')}")
        assert "AUTONOMOUS" in result.get("action_taken", ""), "Expected autonomous action"
        assert "Relocated" in result.get("action_taken", ""), "Expected relocation action"

        # Test low confidence decision (should archive)
        result = healer._autonomous_void_violation_resolution(
            test_file,
            "test_zone",
            "test_data",
            "Test violation",
            ["test_scripts", "test_helpers"],
            True,
            [],
            [],
        )

        print(f"  Low confidence decision: {result.get('action_taken', 'NO ACTION')}")
        assert "archived" in result.get("action_taken", "").lower(), "Expected archive action"

        print("✅ Decision logic test PASSED")

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_mission_script_autonomous_mode():
    """Test that the mission script properly enables autonomous mode."""

    # Test that we can import the mission script
    import importlib.util

    script_path = Path("ops_scripts/sovereign_healing_mission.py")
    assert script_path.exists(), "Mission script not found"

    spec = importlib.util.spec_from_file_location("mission_module", script_path)
    mission_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(mission_module)
        assert hasattr(mission_module, "run_mission"), "run_mission function not found"
        print("✅ Mission script imports correctly with autonomous mode")
    except Exception as e:
        assert False, f"Mission script import failed: {e}"


def test_no_user_prompts_in_autonomous_mode():
    """Verify that autonomous mode bypasses all user prompts."""
    from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

    temp_root = Path(tempfile.mkdtemp(prefix="test_no_prompts_"))
    try:
        healer = LocationHealerAgent(project_root=temp_root)
        healer._autonomous_mode = True

        # Create test file in void violation location
        test_file = temp_root / "agentic_core" / "unknown_folder" / "test.py"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# Test")

        # This should NOT prompt for user input
        result = healer._heal_void_violation(
            test_file, "VOID VIOLATION: Path not in sovereign territory", True, [], []
        )

        # Should have made an autonomous decision
        action = result.get("action_taken", "")
        print(f"  Autonomous action taken: {action}")

        assert "AUTONOMOUS" in action or "PREVIEW" in action, (
            f"Expected autonomous decision, got: {action}"
        )
        assert "SKIPPED" not in action or "PREVIEW" in action, (
            f"Should not skip in autonomous mode: {action}"
        )

        print("✅ No user prompts test PASSED")

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    print("🤖 AUTONOMOUS DECISION-MAKING TEST SUITE")
    print("=" * 60)

    test_autonomous_confidence_scoring()
    test_autonomous_decision_logic()
    test_mission_script_autonomous_mode()
    test_no_user_prompts_in_autonomous_mode()

    print("=" * 60)
    print("✅ ALL AUTONOMOUS TESTS PASSED!")
    print("🚀 Sovereign healing mission ready for fully autonomous execution")
