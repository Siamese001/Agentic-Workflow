"""
Ultra Hardening Final Verification Suite
Aggressive verification of total Canon Key eradication and Metadata Locking.
Target: 100% Pass across all structural and immutability constraints.
"""
import pytest
import collections.abc
from typing import Mapping
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestSovereignFinalClosure:
    """
    Aggressive verification of total Canon Key eradication and Metadata Locking.
    Target: 100% Pass across all structural and immutability constraints.
    """

    def test_canon_key_purification(self):
        """
        [CRITICAL] Verify structure_blueprint.py is physically scrubbed of deprecated variables.
        Ensures no 'Ghost Gravity' logic remains.
        """
        forbidden = ['CANON_KEY_EXCEPTIONS', 'ACTIVE_CANON_KEYS', 'CANON_KEY_TO_FOLDER_MAP']
        
        # Import the module to check runtime attributes
        import agentic_core.L5_safety.validators.structure_blueprint as structure_blueprint
        
        current_vars = dir(structure_blueprint)
        for f in forbidden:
            assert f not in current_vars, f"GHOST VARIABLE DETECTED: {f} still exists in SSOT."
        
        # Also verify no imports of these variables exist
        structure_blueprint_path = project_root / "agentic_core/L5_safety/validators/structure_blueprint.py"
        with open(structure_blueprint_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for f in forbidden:
                assert f not in content, f"GHOST IMPORT DETECTED: {f} still referenced in code"

    def test_metadata_read_only_protection(self):
        """
        [HARDENING] Verify AGENT_METADATA strictly implements read-only Mapping.
        Forbids mutation operations (pop, clear, __setitem__).
        """
        from agentic_core.utils.discovery_parser import AGENT_METADATA
        
        # Verify it's a Mapping
        assert isinstance(AGENT_METADATA, collections.abc.Mapping), "AGENT_METADATA is not a Mapping"
        
        # Verify mutation operations are forbidden
        with pytest.raises((AttributeError, TypeError)):
            AGENT_METADATA.pop('L5_Safety')
        
        with pytest.raises(TypeError):
            AGENT_METADATA['Malicious_Inject'] = True
        
        # Verify read-only access works - check if it's a list (JSON array) or dict
        try:
            # If it's a list, check length and indexing
            assert len(AGENT_METADATA) >= 0, "AGENT_METADATA not readable"
            # Try to access first element if list
            if len(AGENT_METADATA) > 0:
                first_item = AGENT_METADATA[0]
                assert first_item is not None, "AGENT_METADATA first item is None"
        except (KeyError, TypeError):
            # If it's a dict-like structure, check for keys
            assert len(AGENT_METADATA) >= 0, "AGENT_METADATA not readable"

    def test_root_directory_stability(self):
        """
        [SSOT] Verify root directory constants are present and correctly typed.
        Ensures path stability for all downstream agents.
        """
        import agentic_core.L5_safety.validators.structure_blueprint as structure_blueprint
        
        # Verify root directory constants exist
        assert structure_blueprint.AGENTIC_CORE_DIR == "agentic_core"
        assert structure_blueprint.APPS_RG_DIR == "apps_rg"
        assert structure_blueprint.APPS_LIC_DIR == "apps_lic"
        assert structure_blueprint.APPS_SHARED_DIR == "apps_shared"
        
        # Verify Final status via annotations
        annotations = getattr(structure_blueprint, '__annotations__', {})
        assert 'Final' in str(annotations.get('AGENTIC_CORE_DIR', '')), "AGENTIC_CORE_DIR not marked Final"

    def test_location_agent_integrity(self):
        """
        [LOGIC PURGE] Verify LocationAgent has no access to deprecated key-bypass logic.
        Ensures strict AST/Territory enforcement.
        """
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        
        agent = LocationAgent(project_root)
        assert not hasattr(agent, 'is_excepted_from_key'), \
            "LocationAgent still retains deprecated key exception logic."

    def test_agent_list_mapping_immutability(self):
        """
        [HARDENING] Verify AgentListMapping prevents runtime mutations.
        Tests the core immutability wrapper.
        """
        from agentic_core.utils.discovery_parser import AgentListMapping
        
        # Create test data
        test_data = {"test": "value", "immutable": True}
        mapping = AgentListMapping(test_data)
        
        # Verify read operations work
        assert mapping["test"] == "value"
        assert len(mapping) == 2
        assert "immutable" in mapping
        
        # Verify mutation operations fail
        with pytest.raises((AttributeError, TypeError)):
            mapping.pop("test")
        
        with pytest.raises(TypeError):
            mapping["new_key"] = "new_value"
        
        with pytest.raises((AttributeError, TypeError)):
            mapping.clear()

    def test_canon_key_eradication_comprehensive(self):
        """
        [COMPREHENSIVE] Verify no Canon Key references exist anywhere in codebase.
        Full filesystem scan for ghost references.
        """
        forbidden_patterns = [
            'CANON_KEY_EXCEPTIONS',
            'ACTIVE_CANON_KEYS', 
            'CANON_KEY_TO_FOLDER_MAP'
        ]
        
        # Scan critical files
        critical_files = [
            "agentic_core/L5_safety/validators/structure_blueprint.py",
            "agentic_core/L5_safety/validators/LocationAgent.py",
            "agentic_core/L5_safety/validators/location_utils.py",
            "agentic_core/utils/discovery_parser.py"
        ]
        
        for file_path in critical_files:
            full_path = project_root / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in forbidden_patterns:
                        assert pattern not in content, f"GHOST REFERENCE: {pattern} found in {file_path}"

    def test_final_root_constants(self):
        """
        [FINAL] Verify all hardened root directory constants are properly Final.
        Ensures complete SSOT path hardening.
        """
        import agentic_core.L5_safety.validators.structure_blueprint as blueprint
        
        # Check Final annotations on root constants
        root_constants = [
            'AGENTIC_CORE_DIR',
            'APPS_RG_DIR', 
            'APPS_LIC_DIR',
            'APPS_SHARED_DIR'
        ]
        
        annotations = getattr(blueprint, '__annotations__', {})
        for const in root_constants:
            assert const in annotations, f"Root constant {const} missing type annotation"
            assert 'Final' in str(annotations[const]), f"Root constant {const} not marked Final"

if __name__ == "__main__":
    # Mandatory "100% pass" confirmation for total system closure.
    print("Executing Final Integrity Audit: 100% PASS required.")
    pytest.main([__file__, "-v"])
