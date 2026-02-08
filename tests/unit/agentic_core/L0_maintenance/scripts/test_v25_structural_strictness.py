"""
V2.5 Structural Strictness - Aggressive Testing
Validates: Unified eviction, domain population, semantic registry alignment

[ULTRA-DIFF] RECONCILIATION: Updated to match authoritative SSOT structure
from structure_blueprint_config.py (2026-02-05)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L5_safety.config.structure_blueprint_config import (
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
    [ULTRA-DIFF] RECONCILIATION: Verify APPS_*_SUBFOLDER_MAPs match authoritative SSOT.

    Old Expectation: {"models", "types", "events"}
    New SSOT (apps_rg): ["entities", "models", "value_objects"]
    New SSOT (apps_lic): ["config", "utils", "models"]
    """
    # Verify apps_rg domain structure
    expected_rg_domain = {"entities", "models", "value_objects"}
    rg_domain = set(APPS_RG_SUBFOLDER_MAP.get("domain", []))
    assert rg_domain == expected_rg_domain, (
        f"FAILED: apps_rg['domain'] mismatch. Expected {expected_rg_domain}, got {rg_domain}"
    )

    # Verify apps_lic domain structure
    expected_lic_domain = {"config", "utils", "models"}
    lic_domain = set(APPS_LIC_SUBFOLDER_MAP.get("domain", []))
    assert lic_domain == expected_lic_domain, (
        f"FAILED: apps_lic['domain'] mismatch. Expected {expected_lic_domain}, got {lic_domain}"
    )
    print("✅ Test 2/6: Apps domain population verified (SSOT aligned)")


def test_semantic_registry_alignment():
    """
    [ULTRA-DIFF] RECONCILIATION: Verify semantic_l2_registry aligns with APPS_SHARED_SUBFOLDER_MAP.

    Updated legacy keys - removed 'core_components' as it's now a valid SSOT key.
    """
    shared_sem = SEMANTIC_L2_REGISTRY["apps_shared"]

    # Legacy keys that should NOT be present (old structure that was removed)
    legacy_keys = {"base_definitions", "common_utils", "base_agents"}
    present_legacy = set(shared_sem.keys()).intersection(legacy_keys)
    assert not present_legacy, f"FAILED: Legacy keys found in semantic registry: {present_legacy}"

    # Verify all SSOT keys have semantic definitions
    required_keys = set(APPS_SHARED_SUBFOLDER_MAP.keys())
    present_keys = set(shared_sem.keys())
    assert required_keys.issubset(present_keys), (
        f"FAILED: Missing semantic definitions for apps_shared. Missing: {required_keys - present_keys}"
    )
    print("✅ Test 3/6: Semantic registry alignment verified")


def test_apps_rg_lic_semantic_completeness():
    """
    Edge Case: Verify apps_rg and apps_lic in semantic registry have 'core' and 'domain' definitions.
    """
    for app in ["apps_rg", "apps_lic"]:
        app_sem = SEMANTIC_L2_REGISTRY[app]
        assert "core" in app_sem, f"FAILED: {app} missing 'core' in semantic registry"
        assert "domain" in app_sem, f"FAILED: {app} missing 'domain' in semantic registry"
    print("✅ Test 4/6: Apps semantic completeness verified")


def test_apps_rg_filesystem_structure():
    """
    [ULTRA-DIFF] Verify apps_rg filesystem adheres to new SSOT.
    Only enforces that IF a folder exists, it must be in the allowed list.
    Does not force empty folders to exist.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

    # Verify domain subfolders
    expected_domain_subfolders = {"entities", "models", "value_objects"}
    domain_path = project_root / "apps_rg" / "domain"

    if domain_path.exists():
        current_subfolders = {p.name for p in domain_path.iterdir() if p.is_dir()}
        unknown_folders = current_subfolders - expected_domain_subfolders
        assert not unknown_folders, f"Found prohibited folders in apps_rg/domain: {unknown_folders}"

    # Verify top-level structure matches SSOT
    expected_roots = {
        "asset_library",
        "core",
        "domain",
        "engines",
        "logic_nodes",
        "shared",
        "system_flow",
        "validation",
    }
    apps_rg_path = project_root / "apps_rg"
    if apps_rg_path.exists():
        current_roots = {p.name for p in apps_rg_path.iterdir() if p.is_dir() and not p.name.startswith("_")}
        unknown_roots = current_roots - expected_roots
        assert not unknown_roots, f"Found prohibited top-level folders in apps_rg: {unknown_roots}"

    print("✅ Test 5/6: apps_rg filesystem structure verified")


def test_apps_lic_filesystem_structure():
    """
    [ULTRA-DIFF] Verify apps_lic filesystem adheres to new SSOT.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

    # Verify top-level structure matches SSOT
    expected_roots = {
        "asset_library",
        "domain",
        "engines",
        "logic_nodes",
        "reports",
        "scripts",
        "shared",
        "system_flow",
        "tools",
    }
    apps_lic_path = project_root / "apps_lic"
    if apps_lic_path.exists():
        current_roots = {p.name for p in apps_lic_path.iterdir() if p.is_dir() and not p.name.startswith("_")}
        unknown_roots = current_roots - expected_roots
        assert not unknown_roots, f"Found prohibited top-level folders in apps_lic: {unknown_roots}"

    print("✅ Test 6/6: apps_lic filesystem structure verified")


if __name__ == "__main__":
    try:
        test_unified_eviction()
        test_apps_domain_population()
        test_semantic_registry_alignment()
        test_apps_rg_lic_semantic_completeness()
        test_apps_rg_filesystem_structure()
        test_apps_lic_filesystem_structure()
        print("\n" + "=" * 60)
        print("V2.5 STRUCTURAL STRICTNESS: 100% PASS (6/6 tests)")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ CRITICAL FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(1)
