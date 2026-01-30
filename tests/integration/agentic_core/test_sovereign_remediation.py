"""
Test Sovereign Contract Remediation

Verifies that all agents have proper heal() methods and can be instantiated
without errors. This test validates the fixes for Sovereign Contract breaches.
"""

import inspect
from pathlib import Path

import pytest

# Import all agents to test
from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
from agentic_core.L5_safety.validators.NamingAgent import NamingAgent
from agentic_core.L5_safety.validators.RootHygieneAgent import RootHygieneAgent
from agentic_core.L5_safety.validators.SystemArchitectAgent import SystemArchitectAgent
from agentic_core.prompt_governance.agents.ConversationalRepairAgent import (
    ConversationalRepairAgent,
)

AGENTS_TO_TEST = [
    LocationAgent,
    NamingAgent,
    RootHygieneAgent,
    SystemArchitectAgent,
    ConversationalRepairAgent,
]


def test_instantiation_integrity():
    """
    Verify that ALL agents can be instantiated without ImportErrors.
    This explicitly tests the NamingAgent fix.
    """
    project_root = Path.cwd()
    for agent_cls in AGENTS_TO_TEST:
        try:
            agent = agent_cls(project_root=project_root)
            assert agent is not None
        except Exception as e:
            pytest.fail(f"FAILED to instantiate {agent_cls.__name__}: {e}")
    print("Test Case 1: Instantiation Integrity - 100% PASS")


def test_heal_signature_contract():
    """
    Verify that ALL agents have a heal(self, violation) signature.
    This explicitly tests the LocationAgent signature fix.
    """
    for agent_cls in AGENTS_TO_TEST:
        heal_method = getattr(agent_cls, "heal", None)
        assert callable(heal_method), f"{agent_cls.__name__} missing heal method"

        sig = inspect.signature(heal_method)
        params = list(sig.parameters.keys())

        # Must accept 'violation' or catch-all 'kwargs'
        is_compliant = "violation" in params or "kwargs" in params
        assert is_compliant, f"{agent_cls.__name__}.heal() has invalid signature: {sig}"

        # Must NOT be the legacy signature
        if "path" in params and "violation" not in params:
            pytest.fail(f"{agent_cls.__name__} still using legacy heal(path) signature!")

    print("Test Case 2: Contract Signature Compliance - 100% PASS")


def test_heal_execution_smoke_test():
    """
    Verify that calling heal() with a dummy violation doesn't crash.
    """
    project_root = Path.cwd()
    dummy_violation = {
        "file": "dummy_test_file.py",
        "type": "TEST_VIOLATION",
        "message": "This is a smoke test",
    }

    for agent_cls in AGENTS_TO_TEST:
        agent = agent_cls(project_root=project_root)
        try:
            result = agent.heal(dummy_violation)
            assert isinstance(result, dict), f"{agent_cls.__name__} returned non-dict"
            assert "status" in result or "success" in result, (
                f"{agent_cls.__name__} result missing status field"
            )
        except Exception as e:
            pytest.fail(f"{agent_cls.__name__}.heal() crashed on execution: {e}")

    print("Test Case 3: Execution Logic Smoke Test - 100% PASS")


if __name__ == "__main__":
    test_instantiation_integrity()
    test_heal_signature_contract()
    test_heal_execution_smoke_test()
    print("\n✅ ALL SOVEREIGN CONTRACT TESTS PASSED!")
    print("The agents are now compliant with execute_ssot.py expectations.")
