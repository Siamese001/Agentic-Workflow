"""
Direct test runner for Phase 1 Configuration Infrastructure.
Bypasses pytest import issues.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("PHASE 1: CONFIGURATION INFRASTRUCTURE TESTS")
print("=" * 80)


def test_rg_agent_specs_defaults():
    """Verify default values are populated correctly."""
    print("\n1. Testing RGAgentSpecs defaults...")

    try:
        from apps_rg.domain.config.schemas import RGAgentSpecs

        specs = RGAgentSpecs()

        # Check orchestrator defaults
        assert specs.orchestrator.global_step_limit == 20
        assert specs.orchestrator.max_retry_iterations == 5
        assert specs.orchestrator.checkpoint_enabled is True
        assert specs.orchestrator.trace_persistence is True

        # Check other component defaults
        assert specs.clerk_extraction.min_bullets_per_section == 3
        assert specs.clerk_extraction.max_bullets_per_section == 8
        assert specs.enrichment.duplicate_threshold == 0.85
        assert specs.generation.n_candidates == 3
        assert specs.validation.min_quality_score == 0.7

        print("   ✅ RGAgentSpecs defaults test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ RGAgentSpecs defaults test FAILED: {e}")
        return False


def test_agent_spec_validation():
    """Verify validation logic in AgentSpec."""
    print("\n2. Testing AgentSpec validation...")

    try:
        from apps_rg.domain.config.schemas import AgentSpec

        # Valid config
        config = AgentSpec(
            name="TestAgent", module_path="apps_rg.engines.test.TestEngine", timeout_sec=60
        )
        assert config.name == "TestAgent"
        assert config.timeout_sec == 60
        assert config.criticality == "required"

        # Invalid timeout (must be >= 1)
        try:
            AgentSpec(
                name="TestAgent", module_path="apps_rg.engines.test.TestEngine", timeout_sec=0
            )
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected

        # Invalid criticality
        try:
            AgentSpec(
                name="TestAgent",
                module_path="apps_rg.engines.test.TestEngine",
                criticality="invalid",
            )
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected

        print("   ✅ AgentSpec validation test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ AgentSpec validation test FAILED: {e}")
        return False


def test_singleton_loader():
    """Verify load_rg_specs returns the same instance (Singleton)."""
    print("\n3. Testing singleton loader...")

    try:
        from apps_rg.domain.config.loader import load_rg_specs, reload_config

        reload_config()

        # First load
        specs1 = load_rg_specs()
        # Second load
        specs2 = load_rg_specs()

        assert specs1 is specs2
        assert id(specs1) == id(specs2)

        print("   ✅ Singleton loader test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Singleton loader test FAILED: {e}")
        return False


def test_loader_force_reload():
    """Verify force_reload parameter works."""
    print("\n4. Testing force reload...")

    try:
        from apps_rg.domain.config.loader import load_rg_specs

        # Load initial config
        specs1 = load_rg_specs()

        # Force reload should return new instance
        specs2 = load_rg_specs(force_reload=True)

        # Should be different objects
        assert specs1 is not specs2

        print("   ✅ Force reload test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Force reload test FAILED: {e}")
        return False


def test_topology_validation():
    """Verify OrchestrationTopology validation works."""
    print("\n5. Testing topology validation...")

    try:
        from apps_rg.domain.config.schemas import OrchestrationTopology, AgentSpec

        # Valid topology
        agent_spec = AgentSpec(name="TEST_AGENT", module_path="apps_rg.engines.test.TestEngine")

        topology = OrchestrationTopology(
            phases={"phase1": ["TEST_AGENT"]}, agents={"TEST_AGENT": agent_spec}
        )

        assert len(topology.phases) == 1
        assert "TEST_AGENT" in topology.agents

        # Invalid topology (agent in phase but not in agents)
        try:
            OrchestrationTopology(
                phases={"phase1": ["MISSING_AGENT"]}, agents={"TEST_AGENT": agent_spec}
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "unknown agent" in str(e)

        print("   ✅ Topology validation test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Topology validation test FAILED: {e}")
        return False


def test_config_path_resolution():
    """Verify config path is resolved correctly."""
    print("\n6. Testing config path resolution...")

    try:
        from apps_rg.domain.config.loader import get_config_path

        config_path = get_config_path()
        assert config_path.name == "config"

        print("   ✅ Config path resolution test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Config path resolution test FAILED: {e}")
        return False


def main():
    """Run all Phase 1 tests."""
    results = []

    results.append(test_rg_agent_specs_defaults())
    results.append(test_agent_spec_validation())
    results.append(test_singleton_loader())
    results.append(test_loader_force_reload())
    results.append(test_topology_validation())
    results.append(test_config_path_resolution())

    print("\n" + "=" * 80)
    print("PHASE 1 TEST RESULTS")
    print("=" * 80)

    passed = sum(results)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL PHASE 1 TESTS PASSED!")
        print("✅ Configuration Infrastructure is fully functional")
        print("✅ Ready to proceed to Phase 2")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("⚠️  Configuration Infrastructure needs fixes")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
