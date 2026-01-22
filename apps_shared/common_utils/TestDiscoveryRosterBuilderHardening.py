#!/usr/bin/env python3
"""
Test Suite: Discovery Roster Builder Hardening

Tests the 5 detailed test cases for:
1. Strict Healer Filtering
2. Abstract Class Exclusion
3. Robust Instantiation
4. Layer Sorting Verification
5. Runtime Capability Check
"""

import logging
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

    filter_healer_agents,
    instantiate_agent,
    sort_by_layer,
)

# Enable logging to see warnings
logging.basicConfig(level=logging.DEBUG)
Logger = logging.getLogger(__name__)


def test_1_strict_healer_filtering():
    """
    Test Case 1: Strict Healer Filtering

    Create a dummy entry for PassiveMonitorAgent that has no HealerMixin
    and no heal_repository method. Verify it is NOT in the returned list.
    """
    print("\n" + "=" * 60)
    print("TEST 1: Strict Healer Filtering")
    print("=" * 60)

    # Create test agents - one healer, one non-healer
    test_agents = [
        {
            "class_name": "PassiveMonitorAgent",
            "path": "agentic_core/monitors/PassiveMonitorAgent.py",
            "layer": "L6",
            "inheritance": ["MonitorBase"],  # No HealerMixin
            "key_methods": ["monitor", "report"],  # No heal_repository
            "has_healing": False,
        },
        {
            "class_name": "ActiveHealerAgent",
            "path": "agentic_core/healers/ActiveHealerAgent.py",
            "layer": "L0",
            "inheritance": ["HealerMixin", "SovereignBaseAgent"],
            "key_methods": ["heal_repository", "diagnose"],
            "has_healing": True,
        },
        {
            "class_name": "LegacyHealerAgent",
            "path": "agentic_core/healers/LegacyHealerAgent.py",
            "layer": "L1",
            "inheritance": ["SovereignHealer"],  # Alternative healer base
            "key_methods": ["heal_repository"],
            "has_healing": False,
        },
    ]

    result = filter_healer_agents(test_agents)

    # Verify PassiveMonitorAgent is NOT in the result
    result_names = [a["class_name"] for a in result]

    assert "PassiveMonitorAgent" not in result_names, (
        f"PassiveMonitorAgent should be excluded, but found in {result_names}"
    )
    assert "ActiveHealerAgent" in result_names, "ActiveHealerAgent should be included"
    assert "LegacyHealerAgent" in result_names, (
        "LegacyHealerAgent (SovereignHealer inheritance) should be included"
    )

    print("✅ PASSED: Strict healer filtering working")
    print(f"   Filtered agents: {result_names}")
    print("   PassiveMonitorAgent correctly excluded (no HealerMixin, no heal_repository)")
    return True


def test_2_abstract_class_exclusion():
    """
    Test Case 2: Abstract Class Exclusion

    Ensure SovereignBaseAgent (an abstract base) is excluded from the roster.
    """
    print("\n" + "=" * 60)
    print("TEST 2: Abstract Class Exclusion")
    print("=" * 60)

    # Create test agents including abstract bases
    test_agents = [
        {
            "class_name": "SovereignBaseAgent",
            "path": "agentic_core/base_agents/SovereignBaseAgent.py",
            "layer": "L0",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "L0MaintenanceBaseAgent",
            "path": "agentic_core/L0_maintenance/L0MaintenanceBaseAgent.py",
            "layer": "L0",
            "inheritance": ["HealerMixin", "SovereignBaseAgent"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "AbstractValidator",
            "path": "agentic_core/validators/AbstractValidator.py",
            "layer": "L5",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "ConcreteHealerAgent",
            "path": "agentic_core/healers/ConcreteHealerAgent.py",
            "layer": "L0",
            "inheritance": ["HealerMixin", "SovereignBaseAgent"],
            "key_methods": ["heal_repository"],
        },
    ]

    result = filter_healer_agents(test_agents)
    result_names = [a["class_name"] for a in result]

    # Verify abstract bases are excluded
    assert "SovereignBaseAgent" not in result_names, (
        "SovereignBaseAgent should be excluded (in SKIP_AGENTS)"
    )
    assert "L0MaintenanceBaseAgent" not in result_names, (
        "L0MaintenanceBaseAgent should be excluded (in SKIP_AGENTS)"
    )
    assert "AbstractValidator" not in result_names, (
        "AbstractValidator should be excluded (starts with 'Abstract')"
    )

    # Verify concrete agent is included
    assert "ConcreteHealerAgent" in result_names, "ConcreteHealerAgent should be included"

    print("✅ PASSED: Abstract class exclusion working")
    print(f"   Filtered agents: {result_names}")
    print("   SovereignBaseAgent, L0MaintenanceBaseAgent, AbstractValidator excluded")
    return True


def test_3_robust_instantiation():
    """
    Test Case 3: Robust Instantiation

    Create a valid-looking agent entry for BrokenAgent pointing to a class
    that raises ValueError in __init__. Verify the builder logs the error
    (Warning level) and continues without crashing.
    """
    print("\n" + "=" * 60)
    print("TEST 3: Robust Instantiation")
    print("=" * 60)

    # Create a mock module with a broken agent
    class BrokenAgent:
        def __init__(self, project_root=None):
            raise ValueError("Simulated constructor failure for testing")

    agent_data = {
        "class_name": "BrokenAgent",
        "path": "agentic_core/broken/BrokenAgent.py",
        "layer": "L0",
        "inheritance": ["HealerMixin"],
        "key_methods": ["heal_repository"],
    }

    # Mock the import to return our broken agent
    mock_module = MagicMock()
    mock_module.BrokenAgent = BrokenAgent

    warnings_logged = []
    original_warning = Logger.warning

    def capture_warning(msg):
        warnings_logged.append(msg)
        original_warning(msg)

    with patch("importlib.import_module", return_value=mock_module):
        with patch.object(
            logging.getLogger("agentic_core.L3_orchestration.discovery_roster_builder"),
            "warning",
            capture_warning,
        ):
            result = instantiate_agent(agent_data, PROJECT_ROOT)

    # Verify instantiation returned None (failed gracefully)
    assert result is None, f"Expected None for broken agent, got {result}"

    # Verify warning was logged
    assert len(warnings_logged) > 0, "Expected warning to be logged for constructor error"
    assert any("BrokenAgent" in msg for msg in warnings_logged), (
        f"Warning should mention BrokenAgent: {warnings_logged}"
    )

    print("✅ PASSED: Robust instantiation working")
    print("   BrokenAgent instantiation returned None (graceful failure)")
    print(f"   Warning logged: {warnings_logged[0] if warnings_logged else 'N/A'}")
    return True


def test_4_layer_sorting_verification():
    """
    Test Case 4: Layer Sorting Verification

    Ensure the roster includes L0 and L5 agents, and verify L0 appears
    before L5 in the final list, respecting LAYER_PRIORITY.
    """
    print("\n" + "=" * 60)
    print("TEST 4: Layer Sorting Verification")
    print("=" * 60)

    # Create test agents in random order
    test_agents = [
        {
            "class_name": "L5SafetyAgent",
            "layer": "L5",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "L2ExecutionAgent",
            "layer": "L2",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "L0BootstrapAgent",
            "layer": "L0",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "L6ObservabilityAgent",
            "layer": "L6",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "L3OrchestrationAgent",
            "layer": "L3",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "AppsAgent",
            "layer": "Apps",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
        {
            "class_name": "UtilsAgent",
            "layer": "Utils",
            "inheritance": ["HealerMixin"],
            "key_methods": ["heal_repository"],
        },
    ]

    # Filter first (all should pass)
    filtered = filter_healer_agents(test_agents)

    # Sort by layer
    sorted_agents = sort_by_layer(filtered)
    sorted_names = [a["class_name"] for a in sorted_agents]
    sorted_layers = [a["layer"] for a in sorted_agents]

    # Verify order: L0 < L2 < L3 < L5 < L6 < Apps < Utils
    expected_order = ["L0", "L2", "L3", "L5", "L6", "Apps", "Utils"]

    # Check that layers appear in correct order
    layer_positions = {layer: sorted_layers.index(layer) for layer in expected_order}

    for i in range(len(expected_order) - 1):
        current_layer = expected_order[i]
        next_layer = expected_order[i + 1]
        assert layer_positions[current_layer] < layer_positions[next_layer], (
            f"{current_layer} should appear before {next_layer}"
        )

    # Specifically verify L0 before L5
    l0_idx = sorted_names.index("L0BootstrapAgent")
    l5_idx = sorted_names.index("L5SafetyAgent")
    assert l0_idx < l5_idx, f"L0 agent (idx={l0_idx}) should appear before L5 agent (idx={l5_idx})"

    print("✅ PASSED: Layer sorting verification working")
    print(f"   Sorted order: {sorted_names}")
    print(f"   Layer order: {sorted_layers}")
    print(f"   L0BootstrapAgent (idx={l0_idx}) before L5SafetyAgent (idx={l5_idx})")
    return True


def test_5_runtime_capability_check():
    """
    Test Case 5: Runtime Capability Check

    Create an agent FakeHealerAgent that has HealerMixin in JSON but
    is missing the actual heal_repository method on the runtime class.
    Verify instantiate_agent returns None after runtime verification.
    """
    print("\n" + "=" * 60)
    print("TEST 5: Runtime Capability Check")
    print("=" * 60)

    # Create a fake agent class that claims to be a healer but lacks the method
    class FakeHealerAgent:
        """Agent that claims HealerMixin in JSON but lacks heal_repository at runtime."""

        def __init__(self, project_root=None):
            self.project_root = project_root

        def some_other_method(self):
            return "I'm not a real healer"

    agent_data = {
        "class_name": "FakeHealerAgent",
        "path": "agentic_core/fake/FakeHealerAgent.py",
        "layer": "L0",
        "inheritance": ["HealerMixin"],  # Claims HealerMixin in JSON
        "key_methods": ["heal_repository"],  # Claims method in JSON
    }

    # Mock the import to return our fake agent
    mock_module = MagicMock()
    mock_module.FakeHealerAgent = FakeHealerAgent

    with patch("importlib.import_module", return_value=mock_module):
        result = instantiate_agent(agent_data, PROJECT_ROOT)

    # Verify instantiation returned None (runtime check failed)
    assert result is None, f"Expected None for fake healer (missing heal_repository), got {result}"

    print("✅ PASSED: Runtime capability check working")
    print("   FakeHealerAgent instantiation returned None")
    print("   Runtime verification caught missing heal_repository() method")
    return True


def test_has_healing_flag():
    """
    Bonus Test: has_healing Flag Support

    Verify that agents with has_healing=True are included even if they
    don't have HealerMixin in inheritance or heal_repository in key_methods.
    """
    print("\n" + "=" * 60)
    print("BONUS TEST: has_healing Flag Support")
    print("=" * 60)

    test_agents = [
        {
            "class_name": "FlagOnlyHealerAgent",
            "path": "agentic_core/healers/FlagOnlyHealerAgent.py",
            "layer": "L0",
            "inheritance": [],  # No HealerMixin
            "key_methods": [],  # No heal_repository listed
            "has_healing": True,  # But has_healing flag is True
        },
        {
            "class_name": "NoFlagAgent",
            "path": "agentic_core/agents/NoFlagAgent.py",
            "layer": "L0",
            "inheritance": [],
            "key_methods": [],
            "has_healing": False,
        },
    ]

    result = filter_healer_agents(test_agents)
    result_names = [a["class_name"] for a in result]

    assert "FlagOnlyHealerAgent" in result_names, (
        "FlagOnlyHealerAgent should be included via has_healing flag"
    )
    assert "NoFlagAgent" not in result_names, "NoFlagAgent should be excluded"

    print("✅ PASSED: has_healing flag support working")
    print("   FlagOnlyHealerAgent included via has_healing=True")
    return True


def run_all_tests():
    """Run all test cases."""
    print("\n" + "#" * 60)
    print("# Discovery Roster Builder Hardening Test Suite")
    print("#" * 60)

    tests = [
        ("Test 1: Strict Healer Filtering", test_1_strict_healer_filtering),
        ("Test 2: Abstract Class Exclusion", test_2_abstract_class_exclusion),
        ("Test 3: Robust Instantiation", test_3_robust_instantiation),
        ("Test 4: Layer Sorting Verification", test_4_layer_sorting_verification),
        ("Test 5: Runtime Capability Check", test_5_runtime_capability_check),
        ("Bonus: has_healing Flag Support", test_has_healing_flag),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   Exception: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 60)

    if failed > 0:
        print(f"❌ {failed} test(s) FAILED")
        return 1
    else:
        print("✅ ALL TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())