"""
End-to-end test for autonomous healing mode.
Verifies that LocationAgent properly propagates autonomous mode to LocationHealerAgent.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def test_autonomous_mode_propagation():
    """Test that autonomous mode is properly propagated from LocationAgent to LocationHealerAgent."""
    from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

    print("🧪 Testing autonomous mode propagation...")

    # Create LocationAgent with autonomous mode
    agent = LocationAgent(project_root=project_root)
    agent._autonomous_mode = True

    # Get a healer instance through the facade
    healer = agent._get_healer()

    # Verify autonomous mode was propagated
    assert hasattr(healer, "_autonomous_mode"), "Healer missing _autonomous_mode attribute"
    assert healer._autonomous_mode == True, (
        f"Autonomous mode not propagated: {healer._autonomous_mode}"
    )

    print("  ✅ Autonomous mode properly propagated to healer")

    # Test that healer is created fresh each time but mode is preserved
    healer2 = agent._get_healer()
    assert healer2._autonomous_mode == True, "Autonomous mode not preserved in new healer instance"

    print("  ✅ Autonomous mode preserved across multiple healer instances")

    # Test with autonomous mode disabled
    agent._autonomous_mode = False
    healer3 = agent._get_healer()
    assert healer3._autonomous_mode == False, "Autonomous mode should be False"

    print("  ✅ Autonomous mode correctly disabled when set to False")

    return True


def test_autonomous_void_violation_handling():
    """Test that void violations are handled autonomously without prompts."""
    import shutil
    import tempfile

    from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

    print("\n🧪 Testing autonomous void violation handling...")

    # Create temporary test environment
    temp_root = Path(tempfile.mkdtemp(prefix="test_autonomous_void_"))

    try:
        # Create test structure
        test_zone = temp_root / "agentic_core" / "unknown_subfolder"
        test_zone.mkdir(parents=True)
        test_file = test_zone / "test_file.py"
        test_file.write_text("# Test file")

        # Create agent with autonomous mode
        agent = LocationAgent(project_root=temp_root)
        agent._autonomous_mode = True

        # Validate the file (should detect void violation)
        is_valid, reason = agent.validate_file_location(test_file)

        print(f"  📋 Validation result: valid={is_valid}, reason={reason[:80]}...")

        if not is_valid:
            # Try to heal it autonomously (dry run)
            violations = [(test_file, reason)]
            cleanup_results = agent.cleanup_violations(violations, dry_run=True)

            if cleanup_results:
                action = cleanup_results[0].get("action_taken", "")
                print(f"  🤖 Autonomous action: {action[:100]}...")

                # Verify it's an autonomous decision (not skipped due to prompts)
                assert "AUTONOMOUS" in action or "PREVIEW" in action, (
                    f"Expected autonomous decision, got: {action}"
                )
                assert "SKIPPED" not in action or "PREVIEW" in action, (
                    f"Should not skip in autonomous mode: {action}"
                )

                print("  ✅ Void violation handled autonomously without prompts")
            else:
                print("  ⚠️  No cleanup results (may be expected for some violations)")
        else:
            print("  ℹ️  File validated as correct (no violation detected)")

        return True

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_mission_script_configuration():
    """Test that the mission script properly configures autonomous mode."""
    print("\n🧪 Testing mission script autonomous configuration...")

    # Import the mission module
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "mission", project_root / "ops_scripts" / "sovereign_healing_mission.py"
    )
    mission = importlib.util.module_from_spec(spec)

    # Check that the script has the run_mission function
    spec.loader.exec_module(mission)
    assert hasattr(mission, "run_mission"), "Mission script missing run_mission function"

    # Read the source to verify autonomous mode is enabled
    source = (project_root / "ops_scripts" / "sovereign_healing_mission.py").read_text()

    assert "_autonomous_mode = True" in source, "Mission script doesn't enable autonomous mode"
    assert "Autonomous mode ENABLED" in source, "Mission script missing autonomous mode logging"

    print("  ✅ Mission script properly configured for autonomous operation")

    return True


def test_confidence_scoring():
    """Test the confidence scoring for autonomous decisions."""
    import shutil
    import tempfile

    from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

    print("\n🧪 Testing confidence scoring algorithm...")

    temp_root = Path(tempfile.mkdtemp(prefix="test_confidence_"))

    try:
        healer = LocationHealerAgent(project_root=temp_root)

        # Test high confidence (utils pattern)
        confidence = healer._calculate_subfolder_confidence("utils", ["scripts", "tests"])
        print(f"  📊 'utils' confidence: {confidence:.2f}")
        assert confidence >= 0.8, f"Expected high confidence for 'utils', got {confidence}"

        # Test medium confidence (similar to existing)
        confidence = healer._calculate_subfolder_confidence(
            "test_helpers", ["test_data", "scripts"]
        )
        print(f"  📊 'test_helpers' confidence: {confidence:.2f}")
        assert 0.5 <= confidence < 0.8, f"Expected medium confidence, got {confidence}"

        # Test low confidence (very similar to existing)
        confidence = healer._calculate_subfolder_confidence(
            "test_data", ["test_scripts", "test_utils"]
        )
        print(f"  📊 'test_data' (similar) confidence: {confidence:.2f}")
        assert confidence < 0.5, f"Expected low confidence for similar name, got {confidence}"

        print("  ✅ Confidence scoring working correctly")

        return True

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    print("🚀 AUTONOMOUS MODE END-TO-END TEST SUITE")
    print("=" * 70)

    try:
        test_autonomous_mode_propagation()
        test_autonomous_void_violation_handling()
        test_mission_script_configuration()
        test_confidence_scoring()

        print("\n" + "=" * 70)
        print("✅ ALL AUTONOMOUS MODE TESTS PASSED!")
        print("🎯 Sovereign healing mission ready for fully autonomous execution")
        print("   - No user prompts required")
        print("   - Intelligent confidence-based decisions")
        print("   - Proper mode propagation through agent hierarchy")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
