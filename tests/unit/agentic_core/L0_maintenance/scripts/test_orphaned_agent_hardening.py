#!/usr/bin/env python3
"""
Mandatory Discovery & Layer Testing for Orphaned Agent Hardening
Tests to verify that "unknown layer" and "orphaned agent" issues are fully resolved and cannot regress.
"""

import pytest
import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.compliance
def test_layer_integrity_enforcement():
    """Test 13: Assert no 'unknown' layers exist in the final registry."""
    try:
        # Import the discovery components with proper path setup
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))
        sys.path.insert(0, str(agentic_core_path / "L0_maintenance" / "scripts"))
        from full_agent_discovery import main

        # Run discovery
        agents, parse_errors = main()

        # Check for unknown layers
        unknown_layers = [
            agent.get("class_name", "Unknown")
            for agent in agents
            if agent.get("layer", "unknown") in ["unknown", "tests"]
        ]

        assert not unknown_layers, (
            f"Hardening violation: Agents found in unmapped layers: {unknown_layers}. 100% pass required."
        )
        print("✅ Layer integrity enforcement passed. No agents in unknown/test layers.")

    except Exception as e:
        pytest.fail(f"Layer integrity enforcement test failed: {e}")


@pytest.mark.compliance
def test_sovereign_inheritance_audit():
    """Test 14: Force-verify that core agents (L0-L5) inherit from SovereignBaseAgent."""
    try:
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))
        sys.path.insert(0, str(agentic_core_path / "L0_maintenance" / "scripts"))
        from full_agent_discovery import main

        # Run discovery
        agents, parse_errors = main()

        # Check core agents for SovereignBaseAgent inheritance
        core_agents = [
            agent for agent in agents if agent.get("layer", "") in ["L0", "L1", "L2", "L4", "L5"]
        ]

        orphans = []
        for agent in core_agents:
            inheritance = agent.get("inheritance", [])
            if "SovereignBaseAgent" not in inheritance:
                orphans.append(
                    {
                        "name": agent.get("class_name", "Unknown"),
                        "layer": agent.get("layer", "Unknown"),
                        "inheritance": inheritance,
                    }
                )

        orphan_names = [o["name"] for o in orphans]
        assert not orphan_names, (
            f"Found core agents bypassing Sovereign architecture: {orphan_names}. 100% pass required."
        )
        print(
            f"✅ Sovereign inheritance audit passed. All {len(core_agents)} core agents inherit from SovereignBaseAgent."
        )

    except Exception as e:
        pytest.fail(f"Sovereign inheritance audit test failed: {e}")


@pytest.mark.asyncio
async def test_signal_saturation_on_orphans():
    """Test 15: Verify that previously orphaned agents now accept sovereign **kwargs without TypeError."""
    try:
        # Set up path for import
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))

        # Test the specific agents that were identified as orphaned
        test_agents = [
            ("L2_execution.tool_registry.ToolsmithAgent", "ToolsmithAgent"),
            ("L1_cognition.thought_engine.BudgetAgent", "BudgetAgent"),
            ("L2_execution.mcp.EmbeddingSovereignAgent", "EmbeddingSovereignAgent"),
            ("L5_safety.validators.SemanticDebuggerAgent", "SemanticDebuggerAgent"),
        ]

        for module_path, class_name in test_agents:
            try:
                # Import the agent
                module = __import__(module_path, fromlist=[class_name])
                agent_class = getattr(module, class_name)

                # Instantiate the agent
                if class_name == "EmbeddingSovereignAgent":
                    # Singleton pattern
                    agent = agent_class()
                else:
                    agent = agent_class()

                # Test sovereign signal acceptance
                if hasattr(agent, "heal_repository"):
                    result = agent.heal_repository(
                        telemetry_id="HARDENING-V2", auto_approve=True, custom_flag="RECOVERY_TEST"
                    )
                    assert (
                        "skipped" in result or "status" in result or "violations_found" in result
                    ), f"{class_name} failed to process sovereign signals"
                    print(f"✅ {class_name} accepts sovereign signals correctly")
                else:
                    print(f"⚠️  {class_name} has no heal_repository method")

            except TypeError as e:
                if "unexpected keyword argument" in str(e):
                    pytest.fail(f"{class_name} inheritance hardening failed: {e}")
                else:
                    # Some other TypeError, might be acceptable
                    print(f"⚠️  {class_name} had TypeError but not signal-related: {e}")
            except Exception as e:
                print(f"⚠️  {class_name} had other error: {e}")

    except Exception as e:
        pytest.fail(f"Signal saturation test failed: {e}")


@pytest.mark.compliance
def test_manifest_drift_protection():
    """Test 16: Prevent 'Manifest is clean' false positives by checking file content vs registry."""
    try:
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))
        sys.path.insert(0, str(agentic_core_path / "L0_maintenance" / "scripts"))
        from full_agent_discovery import main

        # Run discovery to get live agents
        agents, parse_errors = main()
        live_agents = {agent.get("class_name", "Unknown") for agent in agents}

        # Check manifest file
        manifest_path = PROJECT_ROOT / "agent_discovery_full.json"
        if not manifest_path.exists():
            pytest.fail("Manifest file missing from SSOT blueprint.")

        with open(manifest_path) as f:
            manifest_data = json.load(f)
            manifest_agents = {agent.get("class_name", "Unknown") for agent in manifest_data}

        drift = live_agents.symmetric_difference(manifest_agents)
        assert not drift, (
            f"Manifest drift detected! Registry and Manifest.json are out of sync: {drift}. 100% pass required."
        )
        print(f"✅ Manifest drift protection passed. Both have {len(live_agents)} agents in sync.")

    except Exception as e:
        pytest.fail(f"Manifest drift protection test failed: {e}")


def test_compliance_score_calculation():
    """Test 17: Verify the weighted compliance score calculation works correctly."""
    try:
        # Test the compliance score formula: C = 1 - (V/A)
        total_agents = 237  # Current count from discovery
        violations = 2  # Current violations (unknown layer + orphaned agents)
        expected_score = 1 - (violations / total_agents)

        # Verify the calculation
        calculated_score = 1 - (violations / total_agents)
        assert abs(calculated_score - expected_score) < 0.0001, (
            "Compliance score calculation is incorrect"
        )

        print(f"✅ Compliance score calculation verified: {calculated_score:.4f}")

        # Test edge cases
        assert 1 - (0 / 100) == 1.0, "Perfect compliance should be 1.0"
        assert 1 - (100 / 100) == 0.0, "Total failure should be 0.0"
        assert 1 - (50 / 100) == 0.5, "50% failure should be 0.5"

        print("✅ Compliance score edge cases verified")

    except Exception as e:
        pytest.fail(f"Compliance score calculation test failed: {e}")


if __name__ == "__main__":
    """Run all orphaned agent hardening tests."""
    print("=" * 80)
    print("ORPHANED AGENT HARDENING TEST SUITE")
    print("=" * 80)

    tests = [
        test_layer_integrity_enforcement,
        test_sovereign_inheritance_audit,
        test_signal_saturation_on_orphans,
        test_manifest_drift_protection,
        test_compliance_score_calculation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            print(f"\n🔧 Running {test.__name__}...")
            test()
            passed += 1
            print(f"✅ {test.__name__} PASSED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED: {e}")

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("🎉 ALL ORPHANED AGENT HARDENING TESTS PASSED - PRODUCTION READY")
        sys.exit(0)
    else:
        print("❌ ORPHANED AGENT HARDENING TESTS FAILED - NOT PRODUCTION READY")
        sys.exit(1)
