"""
Test suite for structure_blueprint.py reconciliation.
Verifies that 'Zombie' folders are dead and parity is enforced.

[RECONCILIATION] 2026-01-26: Validates eviction rules and structural consistency.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Import the module under test
from agentic_core.L5_safety.validators import structure_blueprint as sb


class TestStructureReconciliation:
    """
    Verifies that 'Zombie' folders are dead and parity is enforced.
    """

    def test_apps_shared_modernization(self):
        """
        CRITICAL: Verify apps_shared no longer contains evicted folders 'base_agents' or 'common_utils'.
        """
        shared_folders = sb.SOVEREIGN_REGISTRY["apps_shared"]["subfolders"]
        
        # Check for presence of new standard
        assert "agents" in shared_folders, "apps_shared/agents missing (renamed from base_agents)"
        
        # Check for absence of evicted folders
        assert "base_agents" not in shared_folders, "apps_shared/base_agents should be evicted"
        assert "common_utils" not in shared_folders, "apps_shared/common_utils should be evicted"

    def test_apps_shared_subfolder_map_reconciliation(self):
        """
        CRITICAL: Verify APPS_SHARED_SUBFOLDER_MAP matches SOVEREIGN_REGISTRY.
        """
        map_folders = set(sb.APPS_SHARED_SUBFOLDER_MAP.keys())
        
        # Check for presence of new standard
        assert "agents" in map_folders, "APPS_SHARED_SUBFOLDER_MAP missing 'agents'"
        
        # Check for absence of evicted folders
        assert "base_agents" not in map_folders, "APPS_SHARED_SUBFOLDER_MAP contains evicted 'base_agents'"
        assert "common_utils" not in map_folders, "APPS_SHARED_SUBFOLDER_MAP contains evicted 'common_utils'"

    def test_tests_parity(self):
        """
        CRITICAL: Verify tests/apps_lic exists to match tests/apps_rg.
        """
        test_folders = sb.SOVEREIGN_REGISTRY["tests"]["subfolders"]
        assert "apps_lic" in test_folders, "tests/apps_lic missing (parity breach)"
        assert "apps_rg" in test_folders

    def test_tests_subfolder_map_parity(self):
        """
        CRITICAL: Verify TESTS_L2_SUBFOLDER_MAP includes apps_lic.
        """
        map_folders = set(sb.TESTS_L2_SUBFOLDER_MAP.keys())
        assert "apps_lic" in map_folders, "TESTS_L2_SUBFOLDER_MAP missing 'apps_lic'"
        assert "apps_rg" in map_folders

    def test_core_extensions_eviction_l4_approved(self):
        """
        CRITICAL: Verify agentic_core/utils/core_extensions is removed from L4_APPROVED_FOLDERS.
        """
        l4_folders = sb.L4_APPROVED_FOLDERS
        assert "agentic_core/utils/core_extensions" not in l4_folders, \
            "core_extensions found in L4_APPROVED_FOLDERS (should be evicted)"

    def test_core_extensions_eviction_ast_placement(self):
        """
        CRITICAL: Verify agentic_core/utils/core_extensions is removed from AST_PLACEMENT_SIGNALS.
        """
        signals = sb.AST_PLACEMENT_SIGNALS
        assert "agentic_core/utils/core_extensions" not in signals, \
            "core_extensions found in AST_PLACEMENT_SIGNALS (should be evicted)"

    def test_core_extensions_eviction_l2_to_l1_map(self):
        """
        CRITICAL: Verify core_extensions is commented out in L2_TO_L1_MAP.
        """
        l2_to_l1 = sb.L2_TO_L1_MAP
        assert "core_extensions" not in l2_to_l1, \
            "core_extensions found in L2_TO_L1_MAP (should be evicted)"

    def test_canon_validation_registry_eviction_list(self):
        """
        CRITICAL: Verify CANON_VALIDATION_REGISTRY lists core_extensions as evicted.
        """
        forbidden = sb.CANON_VALIDATION_REGISTRY.get("forbidden_patterns", [])
        assert "agentic_core/utils/core_extensions" in forbidden, \
            "core_extensions not listed in CANON_VALIDATION_REGISTRY forbidden_patterns"

    def test_sovereign_registry_note_updated(self):
        """
        CRITICAL: Verify apps_shared note reflects hardening date.
        """
        note = sb.SOVEREIGN_REGISTRY["apps_shared"]["note"]
        assert "2026-01-26" in note, "apps_shared note missing hardening date"
        assert "eviction" in note.lower() or "hardened" in note.lower(), \
            "apps_shared note doesn't reference hardening/eviction"

    def test_no_zombie_references_in_subfolder_metadata(self):
        """
        CRITICAL: Verify SUBFOLDER_METADATA doesn't reference evicted folders.
        """
        metadata = sb.SUBFOLDER_METADATA
        
        # Check that base_agents and common_utils are not in metadata
        assert "base_agents" not in metadata or "apps_shared" not in str(metadata.get("base_agents", {})), \
            "SUBFOLDER_METADATA contains reference to evicted base_agents"
        assert "common_utils" not in metadata or "apps_shared" not in str(metadata.get("common_utils", {})), \
            "SUBFOLDER_METADATA contains reference to evicted common_utils"


class TestReconciliationIntegrity:
    """Additional integrity checks for reconciliation."""

    def test_all_sovereign_subfolders_have_maps(self):
        """
        CRITICAL: Verify all SOVEREIGN_REGISTRY entries have corresponding subfolder maps.
        """
        # Check apps_shared
        sovereign_shared = set(sb.SOVEREIGN_REGISTRY["apps_shared"]["subfolders"])
        map_shared = set(sb.APPS_SHARED_SUBFOLDER_MAP.keys())
        assert sovereign_shared == map_shared, \
            f"Mismatch: SOVEREIGN_REGISTRY apps_shared={sovereign_shared}, MAP={map_shared}"
        
        # Check tests
        sovereign_tests = set(sb.SOVEREIGN_REGISTRY["tests"]["subfolders"])
        map_tests = set(sb.TESTS_L2_SUBFOLDER_MAP.keys())
        assert sovereign_tests == map_tests, \
            f"Mismatch: SOVEREIGN_REGISTRY tests={sovereign_tests}, MAP={map_tests}"

    def test_evicted_folders_consistency(self):
        """
        CRITICAL: Verify all evicted folders in CANON_VALIDATION_REGISTRY are actually evicted.
        """
        forbidden = sb.CANON_VALIDATION_REGISTRY.get("forbidden_patterns", [])
        
        # Check each evicted folder is not in active registries
        for evicted_path in forbidden:
            if "apps_shared" in evicted_path:
                folder_name = evicted_path.split("/")[-1]
                assert folder_name not in sb.APPS_SHARED_SUBFOLDER_MAP, \
                    f"Evicted folder {folder_name} still in APPS_SHARED_SUBFOLDER_MAP"
            
            if "core_extensions" in evicted_path:
                assert evicted_path not in sb.L4_APPROVED_FOLDERS, \
                    f"Evicted path {evicted_path} still in L4_APPROVED_FOLDERS"
                assert evicted_path not in sb.AST_PLACEMENT_SIGNALS, \
                    f"Evicted path {evicted_path} still in AST_PLACEMENT_SIGNALS"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
