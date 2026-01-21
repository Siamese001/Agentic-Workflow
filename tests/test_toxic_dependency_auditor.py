#!/usr/bin/env python3
"""
Robust Tests for ToxicDependencyAuditor
"""

import sys
from pathlib import Path

# Setup mock for MCPHardenedMixin
class MockMixin: pass
mock_module = type(sys)('mock')
mock_module.MCPHardenedMixin = MockMixin
sys.modules['agentic_core.utils.core_extensions.mcp_hardened_mixin'] = mock_module

# Direct import
import importlib.util

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
spec = importlib.util.spec_from_file_location(
    'ToxicDependencyAuditor',
    Path('agentic_core/L5_safety/gravity/ToxicDependencyAuditor.py')
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ToxicDependencyAuditor = module.ToxicDependencyAuditor


def test_fan_in_map_building():
    """TEST 1: Fan-in Map Building"""
    print("=" * 60)
    print("TEST 1: FAN-IN MAP BUILDING")
    print("=" * 60)

    auditor = ToxicDependencyAuditor(root_dir='.', toxic_threshold=5)
    auditor._build_fan_in_map()

    print(f"Total modules tracked: {len(auditor.dependency_map)}")

    # Show top 5 by fan-in
    sorted_deps = sorted(
        auditor.dependency_map.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )[:10]

    print("\nTop 10 modules by fan-in:")
    for module, dependents in sorted_deps:
        print(f"  {module}: {len(dependents)} dependents")

    assert len(auditor.dependency_map) > 0, "Should find some dependencies"
    print("\n✅ TEST 1 PASSED: Fan-in map built successfully")


def test_toxic_hub_detection():
    """TEST 2: Toxic Hub Detection"""
    print("\n" + "=" * 60)
    print("TEST 2: TOXIC HUB DETECTION")
    print("=" * 60)

    # Use low threshold to ensure we find some hubs
    auditor = ToxicDependencyAuditor(root_dir='.', toxic_threshold=5)
    toxic_hubs = auditor.audit_toxicity()

    print(f"Toxic hubs found (threshold >= 5): {len(toxic_hubs)}")

    if toxic_hubs:
        print("\nTop toxic hubs:")
        for hub in toxic_hubs[:5]:
            print(f"  ☢️  {hub['module']}: fan-in = {hub['fan_in']}")

        # Verify structure
        assert 'module' in toxic_hubs[0]
        assert 'fan_in' in toxic_hubs[0]
        assert 'dependents' in toxic_hubs[0]
        assert isinstance(toxic_hubs[0]['dependents'], list)

        # Verify sorting (highest fan-in first)
        for i in range(len(toxic_hubs) - 1):
            assert toxic_hubs[i]['fan_in'] >= toxic_hubs[i+1]['fan_in']

        print("\n✅ TEST 2 PASSED: Toxic hubs detected and sorted correctly")
    else:
        print("No toxic hubs found at threshold 5")
        print("✅ TEST 2 PASSED: No hubs (clean codebase)")


def test_internal_import_extraction():
    """TEST 3: Internal Import Extraction"""
    print("\n" + "=" * 60)
    print("TEST 3: INTERNAL IMPORT EXTRACTION")
    print("=" * 60)

    auditor = ToxicDependencyAuditor(root_dir='.')

    # Test on a known file
    test_file = Path('agentic_core/L5_safety/validators/ToxicDependencyAuditor.py')
    if test_file.exists():
        imports = auditor._extract_internal_imports(test_file)
        print(f"Imports found in ToxicDependencyAuditor.py:")
        for imp in imports:
            print(f"  - {imp}")

        # Should find the mcp_hardened_mixin import
        assert any('mcp_hardened_mixin' in imp for imp in imports)
        print("\n✅ TEST 3 PASSED: Import extraction working")
    else:
        print("Test file not found, skipping")


def test_toxicity_report():
    """TEST 4: Toxicity Report Generation"""
    print("\n" + "=" * 60)
    print("TEST 4: TOXICITY REPORT GENERATION")
    print("=" * 60)

    auditor = ToxicDependencyAuditor(root_dir='.', toxic_threshold=5)
    toxic_hubs = auditor.audit_toxicity()

    print("\nFull Toxicity Report:")
    print("-" * 60)
    auditor.report(toxic_hubs)

    print("\n✅ TEST 4 PASSED: Report generated successfully")


def test_module_name_mapping():
    """TEST 5: Module Name Mapping"""
    print("\n" + "=" * 60)
    print("TEST 5: MODULE NAME MAPPING")
    print("=" * 60)

    auditor = ToxicDependencyAuditor(root_dir='.')

    test_path = Path('agentic_core/L5_safety/validators/ToxicDependencyAuditor.py')
    module_name = auditor._get_module_name(test_path)

    print(f"Path: {test_path}")
    print(f"Module name: {module_name}")

    assert AGENTIC_CORE_DIR in module_name
    assert 'L5_safety' in module_name
    assert 'ToxicDependencyAuditor' in module_name
    assert '.py' not in module_name

    print("\n✅ TEST 5 PASSED: Module name mapping correct")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TOXIC DEPENDENCY AUDITOR - ROBUST TESTING")
    print("=" * 60 + "\n")

    # Run tests
    test_fan_in_map_building()
    test_toxic_hub_detection()
    test_internal_import_extraction()
    test_toxicity_report()
    test_module_name_mapping()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
