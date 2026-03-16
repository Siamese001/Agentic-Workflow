#!/usr/bin/env python3
"""
Test script to reproduce the heal_violation issue with LocationAgent.
"""

import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_location_agent_heal")
_emit_applies_guardrail("p0", "test_location_agent_heal", "p0_governance")
_emit_reads_policy_state("p0", "test_location_agent_heal", "policy_binding")
_emit_snapshots_state("p0", "test_location_agent_heal", "state_snapshot")
emit_replay_key("p0", "test_location_agent_heal")
emit_determinism_digest("p0", "test_location_agent_heal")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent as LocationAgent


def test_location_agent_heal_method():
    """Test if LocationAgent has the required heal method."""

    print("Testing LocationAgent heal method...")

    # Initialize LocationAgent
    agent = LocationAgent(project_root)

    # Check if heal method exists
    if hasattr(agent, "heal"):
        print("✓ LocationAgent has heal method")

        # Try to call it with a mock violation
        mock_violation = {
            "type": "LOCATION",
            "file": str(project_root / "test_file.py"),
            "message": "Test violation",
        }

        try:
            result = agent.heal(mock_violation)
            print("✓ heal method executed successfully")
            print(f"  Result: {result}")
        except Exception as e:  # guardian: allow-silent-swallower
            print(f"✗ heal method failed: {e}")
            return False
    else:
        print("✗ LocationAgent does not have heal method")
        print(f"  Available methods: {[m for m in dir(agent) if not m.startswith('_')]}")
        return False

    return True


def test_heal_violations_method():
    """Test if LocationAgent has heal_violations method."""

    print("\nTesting LocationAgent heal_violations method...")

    agent = LocationAgent(project_root)

    if hasattr(agent, "heal_violations"):
        print("✓ LocationAgent has heal_violations method")

        # Try to call it
        violations = [(Path("test_file.py"), "Test violation")]

        try:
            result = agent.heal_violations(violations)
            print("✓ heal_violations method executed successfully")
            print(f"  Result: {result}")
        except Exception as e:  # guardian: allow-silent-swallower
            print(f"✗ heal_violations method failed: {e}")
            return False
    else:
        print("✗ LocationAgent does not have heal_violations method")
        return False

    return True


if __name__ == "__main__":
    print("=== LocationAgent Healing Method Test ===\n")

    heal_test = test_location_agent_heal_method()
    heal_violations_test = test_heal_violations_method()

    print("\n=== Test Results ===")
    print(f"heal method: {'PASS' if heal_test else 'FAIL'}")
    print(f"heal_violations method: {'PASS' if heal_violations_test else 'FAIL'}")

    if not heal_test or not heal_violations_test:
        print("\n⚠️  LocationAgent needs to implement proper healing methods for execute_ssot.py")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)
