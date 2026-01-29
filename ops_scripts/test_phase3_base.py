"""
Direct test runner for Phase 3: Base Engine Integration.
Tests auto-configuration loading and mixin initialization.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("PHASE 3: BASE ENGINE INTEGRATION TESTS")
print("=" * 80)


def test_base_engine_initialization():
    """Verify BaseRGEngine initializes config and toggles."""
    print("\n1. Testing BaseRGEngine initialization...")

    try:
        from apps_rg.domain.config.schemas import RGAgentSpecs
        from apps_rg.engines.base.base_resume_engine import BaseRGEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext
        from apps_rg.shared.reasoning.toggles import ReasoningToggles

        ctx = SovereignContext()

        class TestEngine(BaseRGEngine):
            async def execute(self):
                return "test_result"

        engine = TestEngine(ctx, node_id="TEST_NODE")

        # Verify Config Loaded
        assert hasattr(engine, "rg_specs"), "Missing rg_specs"
        assert isinstance(engine.rg_specs, RGAgentSpecs), "Invalid rg_specs type"
        assert engine.rg_specs.orchestrator.global_step_limit == 20, "Invalid config value"

        # Verify Toggles Initialized
        assert hasattr(engine, "toggles"), "Missing toggles"
        assert isinstance(engine.toggles, ReasoningToggles), "Invalid toggles type"
        assert engine.toggles.use_cot is True, "Invalid toggle value"

        # Verify Mixins
        assert hasattr(engine, "_mcp_audit"), "Missing MCPHardenedMixin"
        assert hasattr(engine, "heal_repository"), "Missing HealerMixin"
        assert hasattr(engine, "run_subatomic_test"), "Missing SubatomicTestingMixin"

        print("   ✅ BaseRGEngine initialization test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ BaseRGEngine initialization test FAILED: {e}")
        return False


def test_configuration_file_exists():
    """Verify the configuration file exists and is valid."""
    print("\n2. Testing configuration file...")

    try:
        config_path = Path("apps_rg/domain/config/rg_agent_specs.json")
        assert config_path.exists(), "Configuration file not found"

        import json

        with open(config_path) as f:
            config_data = json.load(f)

        # Verify structure
        assert "orchestrator" in config_data, "Missing orchestrator config"
        assert "clerk_extraction" in config_data, "Missing clerk_extraction config"
        assert "enrichment" in config_data, "Missing enrichment config"

        # Verify orchestrator values
        orch_config = config_data["orchestrator"]
        assert orch_config["global_step_limit"] == 20, "Invalid global_step_limit"
        assert orch_config["max_retry_iterations"] == 5, "Invalid max_retry_iterations"

        print("   ✅ Configuration file test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Configuration file test FAILED: {e}")
        return False


def test_subatomic_testing_mixin():
    """Verify SubatomicTestingMixin is properly integrated."""
    print("\n3. Testing SubatomicTestingMixin integration...")

    try:
        from apps_rg.engines.base.base_resume_engine import BaseRGEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext

        ctx = SovereignContext()

        class TestEngine(BaseRGEngine):
            async def execute(self):
                return "test_result"

        engine = TestEngine(ctx)

        # Test subatomic method exists and works
        def test_func():
            return "test_passed"

        result = engine.run_subatomic_test("test_name", test_func)

        assert result["test"] == "test_name", "Invalid test name"
        assert result["result"] == "test_passed", "Invalid test result"
        assert result["status"] == "passed", "Invalid test status"

        print("   ✅ SubatomicTestingMixin integration test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ SubatomicTestingMixin integration test FAILED: {e}")
        return False


def test_environment_based_toggles():
    """Verify environment-based toggle loading works."""
    print("\n4. Testing environment-based toggles...")

    try:
        from apps_rg.shared.reasoning.toggles import get_toggles

        # Test production defaults
        prod_toggles = get_toggles("prod")
        assert prod_toggles.use_cot is True, "Production should use CoT"
        assert prod_toggles.strict_mode is True, "Production should be strict"

        # Test development mode
        dev_toggles = get_toggles("dev")
        assert dev_toggles.tot_branches == 5, "Dev should allow more branches"
        assert dev_toggles.strict_mode is False, "Dev should be less strict"

        # Test mode
        test_toggles = get_toggles("test")
        assert test_toggles.use_cot is False, "Test should disable CoT"
        assert test_toggles.tot_branches == 1, "Test should use minimal branches"

        print("   ✅ Environment-based toggles test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Environment-based toggles test FAILED: {e}")
        return False


def test_knowledge_base_hydration():
    """Verify knowledge base hydration works."""
    print("\n5. Testing knowledge base hydration...")

    try:
        from apps_rg.engines.base.base_resume_engine import BaseRGEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext

        ctx = SovereignContext()

        class TestEngine(BaseRGEngine):
            async def execute(self):
                return "test_result"

        # Test with node_id
        engine = TestEngine(ctx, node_id="TEST_NODE")

        # Should attempt hydration (may fail gracefully if config not found)
        assert hasattr(engine, "config"), "Missing config attribute"
        assert hasattr(engine, "thresholds"), "Missing thresholds attribute"

        print("   ✅ Knowledge base hydration test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Knowledge base hydration test FAILED: {e}")
        return False


def test_mixin_integration():
    """Verify all mixins are properly integrated."""
    print("\n6. Testing mixin integration...")

    try:
        from apps_rg.engines.base.base_resume_engine import BaseRGEngine
        from apps_rg.engines.base.sovereign_context import SovereignContext

        ctx = SovereignContext()

        class TestEngine(BaseRGEngine):
            async def execute(self):
                return "test_result"

        engine = TestEngine(ctx)

        # Test MCPHardenedMixin
        assert hasattr(engine, "_mcp_audit"), "Missing MCPHardenedMixin methods"

        # Test HealerMixin
        assert hasattr(engine, "heal_repository"), "Missing HealerMixin methods"
        result = engine.heal_repository()
        assert isinstance(result, dict), "heal_repository should return dict"
        assert "violations_found" in result, "Missing canonical keys"

        # Test SubatomicTestingMixin
        assert hasattr(engine, "run_subatomic_test"), "Missing SubatomicTestingMixin methods"

        print("   ✅ Mixin integration test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Mixin integration test FAILED: {e}")
        return False


def main():
    """Run all Phase 3 tests."""
    results = []

    results.append(test_base_engine_initialization())
    results.append(test_configuration_file_exists())
    results.append(test_subatomic_testing_mixin())
    results.append(test_environment_based_toggles())
    results.append(test_knowledge_base_hydration())
    results.append(test_mixin_integration())

    print("\n" + "=" * 80)
    print("PHASE 3 TEST RESULTS")
    print("=" * 80)

    passed = sum(results)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL PHASE 3 TESTS PASSED!")
        print("✅ Base Engine auto-configuration is working")
        print("✅ All mixins are properly integrated")
        print("✅ Configuration file is comprehensive")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("⚠️  Base Engine integration needs fixes")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
