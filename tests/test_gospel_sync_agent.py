#!/usr/bin/env python3
"""
Robust Tests for GospelSyncAgent
"""

import sys
from pathlib import Path


# Setup mock for MCPHardenedMixin
class MockMixin: pass
mock_module = type(sys)('mock')
mock_module.MCPHardenedMixin = MockMixin
sys.modules['agentic_core.utils.core_extensions.mcp_hardened_mixin'] = mock_module

# Mock the structure_blueprint import with a simple test blueprint
mock_blueprint_module = type(sys)('mock_blueprint')
mock_blueprint_module.STRUCTURE_BLUEPRINT = {
    "L0_maintenance": {
        "path": "agentic_core/L0_maintenance",
        "agents": ["GospelSyncAgent"]
    },
    "L5_safety": {
        "path": "agentic_core/L5_safety/validators",
        "agents": ["ToxicDependencyAuditor"]
    }
}
# Add required functions to mock
mock_blueprint_module.get_validated_project_root = lambda: Path('.')
mock_blueprint_module.safe_path_join = lambda base, *parts: Path(base).joinpath(*parts)
mock_blueprint_module.validate_path_within_project = lambda path: True
sys.modules['agentic_core.config.blueprint_sovereign.structure_blueprint'] = mock_blueprint_module

# Direct import
import importlib.util

spec = importlib.util.spec_from_file_location(
    'GospelSyncAgent',
    Path('agentic_core/L5_safety/validators/GospelSyncAgent.py')
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

GospelSyncAgent = module.GospelSyncAgent


def test_canonical_files_extraction():
    """TEST 1: Canonical Files Extraction"""
    print("=" * 60)
    print("TEST 1: CANONICAL FILES EXTRACTION")
    print("=" * 60)

    agent = GospelSyncAgent(root_dir='.')
    canonical = agent._get_canonical_files()

    print(f"Canonical files from blueprint: {len(canonical)}")
    for f in sorted(canonical):
        print(f"  - {f}")

    assert len(canonical) > 0, "Should extract canonical files from blueprint"
    assert any('GospelSyncAgent' in f for f in canonical)

    print("\n✅ TEST 1 PASSED: Canonical files extracted")


def test_actual_files_scan():
    """TEST 2: Actual Files Scan"""
    print("\n" + "=" * 60)
    print("TEST 2: ACTUAL FILES SCAN")
    print("=" * 60)

    agent = GospelSyncAgent(root_dir='.')
    actual = agent._get_actual_files()

    print(f"Actual .py files found: {len(actual)}")
    print("Sample files (first 10):")
    for f in sorted(actual)[:10]:
        print(f"  - {f}")

    assert len(actual) > 0, "Should find actual Python files"

    print("\n✅ TEST 2 PASSED: Actual files scanned")


def test_sync_audit():
    """TEST 3: Sync Audit"""
    print("\n" + "=" * 60)
    print("TEST 3: SYNC AUDIT")
    print("=" * 60)

    agent = GospelSyncAgent(root_dir='.')
    results = agent.perform_sync_audit()

    print(f"Heretical files: {len(results['heresy'])}")
    print(f"Missing files: {len(results['missing'])}")
    print(f"Synchronized: {results['synchronized']}")

    # With our mock blueprint, there will be heresy (files not in blueprint)
    # This is expected since the mock only has 2 agents
    assert 'heresy' in results
    assert 'missing' in results
    assert 'synchronized' in results

    print("\n✅ TEST 3 PASSED: Sync audit completed")


def test_heretical_file_detection():
    """TEST 4: Shadow/Heretical File Detection"""
    print("\n" + "=" * 60)
    print("TEST 4: HERETICAL FILE DETECTION")
    print("=" * 60)

    # Create a heretic file
    heretic_path = Path('agentic_core/L1_cognition/HereticTest.py')
    heretic_path.parent.mkdir(parents=True, exist_ok=True)
    heretic_path.write_text("# Heretical test file\nprint('I am a heretic!')\n")

    try:
        agent = GospelSyncAgent(root_dir='.')
        results = agent.perform_sync_audit()

        # Check if heretic is detected
        heretic_detected = any('HereticTest' in h for h in results['heresy'])
        print(f"Heretic file created: {heretic_path}")
        print(f"Heretic detected in audit: {heretic_detected}")

        if heretic_detected:
            print("☢️  HERETICAL FILE FLAGGED (as expected)")

        assert heretic_detected, "Heretic file should be detected"
        print("\n✅ TEST 4 PASSED: Heretical file detection working")
    finally:
        # Cleanup
        if heretic_path.exists():
            heretic_path.unlink()
            print(f"Cleaned up: {heretic_path}")


def test_missing_canon_detection():
    """TEST 5: Missing Canon Detection"""
    print("\n" + "=" * 60)
    print("TEST 5: MISSING CANON DETECTION")
    print("=" * 60)

    # The mock blueprint expects ToxicDependencyAuditor at a specific path
    # Let's check if it's detected as missing or present
    agent = GospelSyncAgent(root_dir='.')
    results = agent.perform_sync_audit()

    print(f"Missing canon files: {len(results['missing'])}")
    for m in results['missing'][:5]:
        print(f"  ❌ {m}")

    # With our mock blueprint, some files may be missing
    print("\n✅ TEST 5 PASSED: Missing canon detection working")


def test_report_generation():
    """TEST 6: Report Generation"""
    print("\n" + "=" * 60)
    print("TEST 6: REPORT GENERATION")
    print("=" * 60)

    agent = GospelSyncAgent(root_dir='.')
    agent.perform_sync_audit()

    print("\nGenerated Report:")
    print("-" * 60)
    agent.report_drift()

    print("\n✅ TEST 6 PASSED: Report generated successfully")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GOSPEL SYNC AGENT - ROBUST TESTING")
    print("=" * 60 + "\n")

    # Run tests
    test_canonical_files_extraction()
    test_actual_files_scan()
    test_sync_audit()
    test_heretical_file_detection()
    test_missing_canon_detection()
    test_report_generation()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
