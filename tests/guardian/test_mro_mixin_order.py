"""
Automated MRO Mixin Order Guardian Test.

This test BLOCKS COMMITS if any agent has incorrect mixin ordering.
Safety mixins (AtomicExecutionMixin, CircuitBreakerMixin) MUST precede
base agent classes in the inheritance list.

v3.0: Added to prevent silent MRO shadowing failures.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Define safety mixins that MUST precede base classes
SAFETY_MIXINS = [
    "AtomicExecutionMixin",
    "CircuitBreakerMixin",
    "HallucinationDetectionMixin",
]

# Define base agent classes
BASE_AGENT_CLASSES = [
    "SovereignBaseAgent",
    "L0MaintenanceBaseAgent",
    "L1CognitionBase",
    "L2ExecutionBase",
    "L3OrchestrationBase",
    "L4StateBase",
    "L5SafetyBase",
    "L6ObservabilityBase",
]


def get_mro_class_names(agent_class: type) -> list[str]:
    """Get list of class names in MRO order."""
    return [cls.__name__ for cls in agent_class.__mro__]


def get_direct_bases(agent_class: type) -> list[str]:
    """Get names of directly inherited classes (not through inheritance chain)."""
    return [base.__name__ for base in agent_class.__bases__]


def check_mixin_order(agent_class: type) -> tuple[bool, str]:
    """
    Check if safety mixins precede base classes in MRO.

    Only checks mixins that are DIRECTLY inherited by the agent class,
    not those inherited through base class chains (e.g., MCPHardenedMixin
    inherited via SovereignBaseAgent is OK).

    Returns:
        (is_valid, error_message)
    """
    mro_names = get_mro_class_names(agent_class)
    direct_bases = get_direct_bases(agent_class)

    for mixin in SAFETY_MIXINS:
        # Only check if mixin is DIRECTLY inherited
        if mixin not in direct_bases:
            continue  # Mixin inherited through chain, skip

        mixin_index = mro_names.index(mixin)

        for base in BASE_AGENT_CLASSES:
            # Only check against directly inherited base classes
            if base not in direct_bases:
                continue  # Base not directly inherited, skip

            base_index = mro_names.index(base)

            if mixin_index > base_index:
                return (
                    False,
                    f"MRO VIOLATION: {agent_class.__name__} has {mixin} "
                    f"(index {mixin_index}) AFTER {base} (index {base_index}). "
                    f"Safety mixins MUST come BEFORE base classes.",
                )

    return (True, "")


def discover_agent_classes() -> list[type]:
    """
    Discover all agent classes in the codebase.

    Returns list of agent classes that can be checked for MRO compliance.
    """
    agents = []

    # Try to import specific agents we know about
    agent_imports = [
        ("agentic_core.L3_orchestration.engine.domain_planner_engine", "DomainPlannerAgent"),
        ("agentic_core.L5_safety.policy_engine.code_healer_agent", "CodeHealerAgent"),
        ("agentic_core.L5_safety.validators.location_agent", "LocationAgent"),
    ]

    for module_path, class_name in agent_imports:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name, None)
            if agent_class is not None:
                agents.append(agent_class)
        except Exception as e:
            print(f"  [SKIP] Could not import {module_path}.{class_name}: {e}")

    return agents


class TestMROMixinOrder:
    """Guardian test for MRO mixin ordering."""

    @pytest.fixture(scope="class")
    def all_agents(self):
        """Discover all agents in the codebase."""
        return discover_agent_classes()

    def test_domain_planner_mro_order(self):
        """
        COMMIT-BLOCKING TEST for DomainPlannerAgent.

        Verifies AtomicExecutionMixin precedes L3OrchestrationBase.
        """
        try:
            from agentic_core.L3_orchestration.engine.domain_planner_engine import (
                DomainPlannerAgent,
            )
        except ImportError as e:
            pytest.skip(f"DomainPlannerAgent not available: {e}")

        is_valid, error_msg = check_mixin_order(DomainPlannerAgent)

        if not is_valid:
            pytest.fail(
                f"MRO ORDERING VIOLATION DETECTED!\n\n"
                f"{error_msg}\n\n"
                f"FIX: Move safety mixins to the LEFT of base classes:\n"
                f"  WRONG: class MyAgent(L3OrchestrationBase, AtomicExecutionMixin)\n"
                f"  RIGHT: class MyAgent(AtomicExecutionMixin, L3OrchestrationBase)\n\n"
                f"This commit is BLOCKED until the violation is fixed."
            )

        # Print MRO for verification
        mro = get_mro_class_names(DomainPlannerAgent)
        print("\n[PASS] DomainPlannerAgent MRO is valid")
        print(f"  MRO: {' -> '.join(mro[:5])}...")

        # Verify AtomicExecutionMixin is present
        assert "AtomicExecutionMixin" in mro, "DomainPlannerAgent should have AtomicExecutionMixin in MRO"

    def test_all_agents_have_correct_mro_order(self, all_agents):
        """
        COMMIT-BLOCKING TEST.

        Verifies that ALL agents with safety mixins have them
        positioned BEFORE base agent classes in the inheritance list.
        """
        if not all_agents:
            pytest.skip("No agents discovered to test")

        violations = []

        for agent_class in all_agents:
            is_valid, error_msg = check_mixin_order(agent_class)
            if not is_valid:
                violations.append(error_msg)

        if violations:
            violation_report = "\n".join(violations)
            pytest.fail(
                f"MRO ORDERING VIOLATIONS DETECTED!\n\n"
                f"The following agents have incorrect mixin ordering:\n\n"
                f"{violation_report}\n\n"
                f"FIX: Move safety mixins to the LEFT of base classes:\n"
                f"  WRONG: class MyAgent(L5SafetyBase, AtomicExecutionMixin)\n"
                f"  RIGHT: class MyAgent(AtomicExecutionMixin, L5SafetyBase)\n\n"
                f"This commit is BLOCKED until all violations are fixed."
            )

        print(f"\n[PASS] All {len(all_agents)} agents have correct MRO ordering")

    @pytest.mark.parametrize("mixin_name", SAFETY_MIXINS)
    def test_specific_mixin_ordering(self, all_agents, mixin_name):
        """Test each safety mixin individually for better error reporting."""
        if not all_agents:
            pytest.skip("No agents discovered to test")

        violations = []

        for agent_class in all_agents:
            mro_names = get_mro_class_names(agent_class)

            if mixin_name not in mro_names:
                continue

            mixin_index = mro_names.index(mixin_name)

            for base in BASE_AGENT_CLASSES:
                if base not in mro_names:
                    continue

                base_index = mro_names.index(base)

                if mixin_index > base_index:
                    violations.append(
                        f"{agent_class.__name__}: {mixin_name} @ {mixin_index}, {base} @ {base_index}"
                    )

        if violations:
            pytest.fail(f"{mixin_name} ordering violations:\n" + "\n".join(violations))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])
