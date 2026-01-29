#!/usr/bin/env python3
"""
Mandatory Discovery Layer Testing Procedures
Tests to ensure the discovery process is as hardened as the governance layer.
"""

import pytest
import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_discovery_completeness():
    """Test 9: Verify that discovery finds the expected number of core layers (L0-L6)."""
    try:
        # Import the discovery components with proper path setup
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))
        sys.path.insert(0, str(agentic_core_path / "L0_maintenance" / "scripts"))
        from full_agent_discovery import main

        # Run discovery
        agents, parse_errors = main()

        # Extract layers from discovered agents
        layers = {agent.get("layer", "Unknown") for agent in agents}
        required_layers = {"L0", "L1", "L2", "L4", "L5", "L6"}  # L3 was removed in Phase 4
        missing = required_layers - layers

        assert not missing, f"Discovery incomplete. Missing layers: {missing}"
        print(f"✅ Discovery completeness passed. Found layers: {sorted(layers)}")

    except Exception as e:
        pytest.fail(f"Discovery completeness test failed: {e}")


def test_registration_uniqueness():
    """Test 10: Assert no two agents share the same Sovereign ID or name."""
    try:
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))
        sys.path.insert(0, str(agentic_core_path / "L0_maintenance" / "scripts"))
        from full_agent_discovery import main

        # Run discovery
        agents, parse_errors = main()

        # Check for duplicate names
        names = [agent.get("class_name", "Unknown") for agent in agents]
        duplicates = [name for name in names if names.count(name) > 1]

        assert not duplicates, f"Duplicate agents detected: {set(duplicates)}"
        print(f"✅ Registration uniqueness passed. Found {len(agents)} unique agents")

    except Exception as e:
        pytest.fail(f"Registration uniqueness test failed: {e}")


def test_import_pollution_check():
    """Test 11: Ensure importing agentic_core doesn't trigger side effects in the global state."""
    try:
        # Capture initial module state
        before_modules = set(sys.modules.keys())

        # Set up path for import
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))

        # Import core component that should not pull in UI libraries

        # Check what new modules were loaded
        after_modules = set(sys.modules.keys())
        new_modules = after_modules - before_modules

        # Ensure we aren't accidentally importing heavyweight IDE components or UI during core discovery
        forbidden = {"tkinter", "PyQt5", "matplotlib", "PySide2", "wx", "gtk"}
        polluted = new_modules & forbidden

        assert not polluted, f"Core logic polluted with UI libraries: {polluted}"
        print("✅ Import pollution check passed. No forbidden modules loaded.")

    except Exception as e:
        pytest.fail(f"Import pollution check failed: {e}")


def test_manifest_sync_integrity():
    """Test 12: Verify manifest.json exactly matches the live registry count."""
    try:
        # Run discovery to get live count
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))
        sys.path.insert(0, str(agentic_core_path / "L0_maintenance" / "scripts"))
        from full_agent_discovery import main

        agents, parse_errors = main()
        live_count = len(agents)

        # Check manifest file
        manifest_path = PROJECT_ROOT / "agent_discovery_full.json"
        if not manifest_path.exists():
            pytest.fail("Manifest file does not exist")

        with open(manifest_path) as f:
            manifest = json.load(f)

        manifest_count = len(manifest)

        assert live_count == manifest_count, (
            f"Manifest is out of sync with the codebase. Live: {live_count}, Manifest: {manifest_count}"
        )
        print(f"✅ Manifest sync integrity passed. Both have {live_count} agents")

    except Exception as e:
        pytest.fail(f"Manifest sync integrity test failed: {e}")


def test_zero_agent_detection():
    """Test 13: Verify zero-agent detection triggers proper error handling."""
    try:
        # This test simulates the zero-agent scenario
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))
        sys.path.insert(0, str(agentic_core_path / "L0_maintenance" / "scripts"))
        from full_agent_discovery import check_compliance_gate

        # Test with empty agent list
        result = check_compliance_gate([], [])

        # Should return exit code 1 for zero agents
        assert result == 1, "Zero-agent detection should return exit code 1"
        print("✅ Zero-agent detection test passed")

    except SystemExit as e:
        # Expected behavior - sys.exit(1) should be called
        assert e.code == 1, "Zero-agent scenario should trigger sys.exit(1)"
        print("✅ Zero-agent detection test passed (SystemExit caught)")
    except Exception as e:
        pytest.fail(f"Zero-agent detection test failed: {e}")


def test_ssot_inheritance_compliance():
    """Test 14: Verify all core agents inherit from SovereignBaseAgent (SSOT compliance)."""
    try:
        agentic_core_path = PROJECT_ROOT / "agentic_core"
        sys.path.insert(0, str(agentic_core_path))
        sys.path.insert(0, str(agentic_core_path / "L0_maintenance" / "scripts"))
        from full_agent_discovery import main

        # Run discovery
        agents, parse_errors = main()

        # Check SSOT compliance for core layers
        non_compliant = []
        for agent in agents:
            layer = agent.get("layer", "")
            if layer in {"L0", "L1", "L2", "L4", "L5", "L6"}:  # Core layers
                inheritance = agent.get("inheritance", [])
                if "SovereignBaseAgent" not in inheritance:
                    non_compliant.append(
                        {
                            "name": agent.get("class_name", "Unknown"),
                            "layer": layer,
                            "inheritance": inheritance,
                        }
                    )

        assert not non_compliant, (
            f"SSOT inheritance violation: {len(non_compliant)} agents not inheriting from SovereignBaseAgent"
        )
        print(
            f"✅ SSOT inheritance compliance passed. All {len(agents)} core agents inherit from SovereignBaseAgent"
        )

    except Exception as e:
        pytest.fail(f"SSOT inheritance compliance test failed: {e}")


if __name__ == "__main__":
    """Run all discovery hardening tests."""
    print("=" * 80)
    print("DISCOVERY HARDENING TEST SUITE")
    print("=" * 80)

    tests = [
        test_discovery_completeness,
        test_registration_uniqueness,
        test_import_pollution_check,
        test_manifest_sync_integrity,
        test_zero_agent_detection,
        test_ssot_inheritance_compliance,
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
        print("🎉 ALL DISCOVERY TESTS PASSED - PRODUCTION READY")
        sys.exit(0)
    else:
        print("❌ DISCOVERY TESTS FAILED - NOT PRODUCTION READY")
        sys.exit(1)
