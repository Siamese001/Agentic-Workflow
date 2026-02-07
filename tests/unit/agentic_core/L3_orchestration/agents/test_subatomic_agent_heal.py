"""
Phase 3 Test Suite: heal() Method Implementation

Tests to verify:
1. SubAtomicAgent has heal() method implemented
2. heal() method returns correct signature
3. heal() method handles various violation types appropriately
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def test_subatomic_agent_has_heal_method():
    """Verify SubAtomicAgent has heal() method."""
    from agentic_core.L3_orchestration.engine.sub_atomic_agent import (
        SubAtomicAgent,
    )

    agent = SubAtomicAgent()
    assert hasattr(agent, "heal"), "SubAtomicAgent missing heal() method"
    assert callable(agent.heal), "heal() is not callable"


def test_subatomic_agent_heal_signature():
    """Verify heal() method returns correct signature."""
    from agentic_core.L3_orchestration.engine.sub_atomic_agent import (
        SubAtomicAgent,
    )

    agent = SubAtomicAgent()
    violation = {"type": "test_violation", "file": "test.py"}

    result = agent.heal(violation)

    # Verify return type
    assert isinstance(result, dict), "heal() must return a dictionary"

    # Verify required keys
    required_keys = {"status", "details", "artifacts", "errors"}
    assert required_keys.issubset(result.keys()), (
        f"heal() result missing required keys: {required_keys - result.keys()}"
    )

    # Verify value types
    assert isinstance(result["status"], str), "status must be a string"
    assert isinstance(result["details"], str), "details must be a string"
    assert isinstance(result["artifacts"], list), "artifacts must be a list"
    assert isinstance(result["errors"], list), "errors must be a list"


def test_subatomic_agent_heal_base_class_behavior():
    """Verify SubAtomicAgent heal() returns skipped status (base class)."""
    from agentic_core.L3_orchestration.engine.sub_atomic_agent import (
        SubAtomicAgent,
    )

    agent = SubAtomicAgent()
    violation = {"type": "test_violation", "file": "test.py"}

    result = agent.heal(violation)

    # Base class should skip healing (delegated to subclasses)
    assert result["status"] == "skipped", "Base class should skip healing"
    assert "base class" in result["details"].lower(), "Details should mention base class"
    assert result["artifacts"] == [], "Base class should not modify artifacts"
    assert result["errors"] == [], "Base class should not have errors"


def test_subatomic_agent_heal_with_various_violations():
    """Test heal() with various violation types."""
    from agentic_core.L3_orchestration.engine.sub_atomic_agent import (
        SubAtomicAgent,
    )

    agent = SubAtomicAgent()

    # Test with different violation types
    test_cases = [
        {"type": "missing_import", "file": "test.py"},
        {"type": "invalid_namespace", "file": "agent.py"},
        {"type": "broken_inheritance", "file": "base.py"},
        {},  # Empty violation
        {"type": "unknown"},  # Missing file
    ]

    for violation in test_cases:
        result = agent.heal(violation)

        # All should return valid signature
        assert isinstance(result, dict)
        assert "status" in result
        assert "details" in result
        assert "artifacts" in result
        assert "errors" in result


def test_subatomic_agent_heal_invalid_input():
    """Test heal() with invalid input types."""
    from agentic_core.L3_orchestration.engine.sub_atomic_agent import (
        SubAtomicAgent,
    )

    agent = SubAtomicAgent()

    # Test with non-dict input (should still return valid result)
    invalid_inputs = [None, "string", 123, [], True]

    for invalid_input in invalid_inputs:
        try:
            result = agent.heal(invalid_input)
            # Should still return a valid dict
            assert isinstance(result, dict)
            assert "status" in result
        except Exception as e:
            # If it raises an exception, that's also acceptable
            # as long as it's documented behavior
            assert isinstance(e, TypeError | AttributeError)


def test_phase3_completion_criteria():
    """Verify Phase 3 completion criteria are met."""
    # from NuclearAuditAgent  # Module removed # import NuclearAuditAgent  # Module removed

    audit = NuclearAuditAgent(project_root=project_root)
    audit.run_audit()

    # Find SubAtomicAgent in results
    subatomic_results = [r for r in audit.results if r.agent_name == "SubAtomicAgent"]

    assert len(subatomic_results) > 0, "SubAtomicAgent not found in audit results"

    subatomic = subatomic_results[0]

    # Verify heal() method is now found
    assert subatomic.heal_signature != "Not found", "SubAtomicAgent heal() method still not found"

    print("\n✅ Phase 3 Complete:")
    print("   - SubAtomicAgent heal() method implemented")
    print(f"   - Signature: {subatomic.heal_signature}")
    print(f"   - Status: {subatomic.status}")
    print("   - Ready for Phase 4-6 remediation")


def test_heal_method_integration():
    """Integration test: verify heal() works in context."""
    from agentic_core.L3_orchestration.engine.sub_atomic_agent import (
        SubAtomicAgent,
    )

    agent = SubAtomicAgent()

    # Simulate a realistic violation scenario
    violation = {
        "type": "signature_mismatch",
        "file": "agentic_core/L3_orchestration/engine/SubAtomicAgent.py",
        "details": {
            "expected": "heal(self, violation: dict) -> dict",
            "actual": "Not found",
        },
    }

    result = agent.heal(violation)

    # Verify it returns a valid response
    assert result["status"] in ["success", "partial_success", "failed", "skipped"]
    assert len(result["details"]) > 0
    assert isinstance(result["artifacts"], list)
    assert isinstance(result["errors"], list)
