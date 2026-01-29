"""
V2.5 Structural Strictness - Aggressive Testing
Validates: Unified eviction, domain population, semantic registry alignment
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L5_safety.validators.structure_blueprint import (
    APPS_LIC_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    CORE_SUBFOLDER_MAP,
    SEMANTIC_L2_REGISTRY,
)


def test_unified_eviction():
    """
    Edge Case: Verify 'unified' is completely removed from all CORE_SUBFOLDER_MAP lists.
    It is an anti-pattern that obscures domain responsibility.
    """
    l2 = CORE_SUBFOLDER_MAP["L2_execution"]
    assert "unified" not in l2, f"FAILED: 'unified' found in L2_execution: {l2}"

    l5 = CORE_SUBFOLDER_MAP["L5_safety"]
    assert "unified" not in l5, f"FAILED: 'unified' found in L5_safety: {l5}"
    print("✅ Test 1/4: Unified eviction verified")


def test_apps_domain_population():
    """
    Edge Case: Verify APPS_*_SUBFOLDER_MAPs have 'domain' populated.
    Empty 'domain' keys in the map violate the V2.5 requirement for strict data models.
    """
    expected_domain = {"models", "types", "events"}

    rg_domain = set(APPS_RG_SUBFOLDER_MAP.get("domain", []))
    assert rg_domain == expected_domain, (
        f"FAILED: apps_rg['domain'] mismatch. Expected {expected_domain}, got {rg_domain}"
    )

    lic_domain = set(APPS_LIC_SUBFOLDER_MAP.get("domain", []))
    assert lic_domain == expected_domain, (
        f"FAILED: apps_lic['domain'] mismatch. Expected {expected_domain}, got {lic_domain}"
    )
    print("✅ Test 2/4: Apps domain population verified")


def test_semantic_registry_alignment():
    """
    Edge Case: Verify semantic_l2_registry has been updated to match the new
    APPS_SHARED_SUBFOLDER_MAP keys (core, utils, components) and removed legacy keys.
    """
    shared_sem = SEMANTIC_L2_REGISTRY["apps_shared"]

    legacy_keys = {"base_definitions", "common_utils", "core_components", "base_agents"}
    present_legacy = set(shared_sem.keys()).intersection(legacy_keys)
    assert not present_legacy, f"FAILED: Legacy keys found in semantic registry: {present_legacy}"

    required_keys = set(APPS_SHARED_SUBFOLDER_MAP.keys())
    present_keys = set(shared_sem.keys())
    assert required_keys.issubset(present_keys), (
        f"FAILED: Missing semantic definitions for apps_shared. Missing: {required_keys - present_keys}"
    )
    print("✅ Test 3/4: Semantic registry alignment verified")


def test_apps_rg_lic_semantic_completeness():
    """
    Edge Case: Verify apps_rg and apps_lic in semantic registry have 'core' and 'domain' definitions.
    """
    for app in ["apps_rg", "apps_lic"]:
        app_sem = SEMANTIC_L2_REGISTRY[app]
        assert "core" in app_sem, f"FAILED: {app} missing 'core' in semantic registry"
        assert "domain" in app_sem, f"FAILED: {app} missing 'domain' in semantic registry"
    print("✅ Test 4/4: Apps semantic completeness verified")


if __name__ == "__main__":
    try:
        test_unified_eviction()
        test_apps_domain_population()
        test_semantic_registry_alignment()
        test_apps_rg_lic_semantic_completeness()
        print("\n" + "=" * 60)
        print("V2.5 STRUCTURAL STRICTNESS: 100% PASS (4/4 tests)")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ CRITICAL FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
