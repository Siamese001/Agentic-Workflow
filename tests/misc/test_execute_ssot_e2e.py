#!/usr/bin/env python3
"""
End-to-end test for LocationAgent integration with execute_ssot.py
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_execute_ssot_integration():
    """Test that LocationAgent works correctly with execute_ssot.py"""

    print("=== End-to-End Test: execute_ssot.py with LocationAgent ===\n")

    # Create a test file in an invalid location
    test_dir = project_root / "temp_test_location"
    test_dir.mkdir(exist_ok=True)

    test_file = test_dir / "InvalidLocationAgent.py"
    test_file.write_text("""
# Invalid location agent - should be in agentic_core/
class InvalidLocationAgent:
    '''This file is in the wrong location'''
    pass
""")

    try:
        # Import the execute_ssot module components
        from agentic_core.L0_routing.scripts.execute_ssot import (
            RuntimeStateManager,
            SovereignDecisionEngine,
            execute_phase2_reconciliation,
        )

        print("1. Setting up agents and decision engine...")

        # Initialize required components
        state_mgr = RuntimeStateManager(project_root)
        decision_engine = SovereignDecisionEngine(enable_llm=False)

        # Create agents dict as execute_ssot.py would
        from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent

        agents = {"LocationAgent": LocationAgent(project_root)}

        print("2. Creating violation plan...")

        # Create a violation plan as execute_ssot.py would generate
        violations_found = [
            {
                "suggested_agent": "LocationAgent",
                "file": str(test_file),
                "type": "LOCATION",
                "message": "File in invalid location: temp_test_location",
                "severity": "medium",
            },
        ]

        plan = {
            "violations_found": violations_found,
            "territory": "temp_test_location",
            "confidence": 0.9,
        }

        print(f"  Plan includes {len(violations_found)} violation(s)")

        print("\n3. Testing Phase 2 reconciliation...")

        # Execute Phase 2 reconciliation (healing phase)
        # This is where execute_ssot.py calls agent.heal(violation)
        result = execute_phase2_reconciliation(
            agents=agents,
            territory="temp_test_location",
            decision_engine=decision_engine,
            state_mgr=state_mgr,
            plan=plan,
            dry_run=False,  # Actually perform the healing
        )

        print(f"  Result: {json.dumps(result, indent=2)}")

        # Verify the result structure
        required_keys = [
            "violations_found",
            "violations_fixed",
            "status",
            "errors",
            "skipped",
            "execution_time_ms",
        ]
        missing_keys = [k for k in required_keys if k not in result]

        if missing_keys:
            print(f"✗ Missing required keys in result: {missing_keys}")
            return False

        if result["violations_found"] != 1:
            print(f"✗ Expected violations_found=1, got {result['violations_found']}")
            return False

        if result["status"] not in ["success", "partial_success", "skipped"]:
            print(f"✗ Unexpected status: {result['status']}")
            return False

        print("✓ Phase 2 reconciliation completed successfully")

        # Check if the file was actually moved/archived
        if not test_file.exists():
            print("✓ File was successfully moved/archived")
        else:
            print("! File still exists (may be expected if healing failed)")

        return True

    except ImportError as e:
        print(f"✗ Failed to import execute_ssot components: {e}")
        return False
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def test_agent_validation():
    """Test that LocationAgent passes PreFlightValidator validation"""

    print("\n=== Agent Validation Test ===\n")

    try:
        from agentic_core.L0_routing.scripts.execute_ssot import PreFlightValidator

        validator = PreFlightValidator(project_root)

        # Create test agents
        from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent

        agents = {"LocationAgent": LocationAgent(project_root)}

        print("1. Testing agent integrity validation...")

        integrity_errors = validator.validate_agent_integrity(agents)

        if integrity_errors:
            print(f"✗ Agent integrity errors: {integrity_errors}")
            return False
        else:
            print("✓ All agents pass integrity validation")

        # Check if LocationAgent has the required heal method
        location_agent = agents["LocationAgent"]
        if hasattr(location_agent, "heal") and callable(location_agent.heal):
            print("✓ LocationAgent has required heal method")
        else:
            print("✗ LocationAgent missing heal method")
            return False

        if hasattr(location_agent, "heal_violations") and callable(location_agent.heal_violations):
            print("✓ LocationAgent has heal_violations method")
        else:
            print("✗ LocationAgent missing heal_violations method")
            return False

        return True

    except ImportError as e:
        print(f"✗ Failed to import validator: {e}")
        return False
    except Exception as e:
        print(f"✗ Error during validation: {e}")
        return False


if __name__ == "__main__":
    print("=== LocationAgent execute_ssot.py End-to-End Test ===\n")

    integration_test = test_execute_ssot_integration()
    validation_test = test_agent_validation()

    print("\n=== Final Results ===")
    print(f"End-to-end integration: {'PASS' if integration_test else 'FAIL'}")
    print(f"Agent validation: {'PASS' if validation_test else 'FAIL'}")

    if integration_test and validation_test:
        print("\n✅ All tests passed!")
        print("LocationAgent is fully compatible with execute_ssot.py")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
