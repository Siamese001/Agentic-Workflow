"""
Final Integrity Lock Test Suite
Verifies that the Canon Key system is completely eradicated 
and the new Metadata Registry is unshakeable.

CRITICAL: This test suite must achieve 100% PASS to validate
the final integrity lock implementation.
"""
import pytest
import collections.abc
from typing import Mapping
from pathlib import Path
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.utils.discovery_parser import AGENT_METADATA
from agentic_core.L5_safety.validators import structure_blueprint


class TestFinalIntegrityLock:
    """
    Final Aggressive Audit to verify that the "Canon Key" logic is fully dead 
    and the new Metadata Registry is unshakeable.
    """

    def test_metadata_runtime_immutability(self):
        """
        [HARDENING] Verify AGENT_METADATA strictly implements the read-only Mapping 
        interface and forbids standard Dict mutation methods.
        """
        print("Testing metadata runtime immutability...")
        
        # Verify it's a Mapping
        assert isinstance(AGENT_METADATA, collections.abc.Mapping), \
            "AGENT_METADATA must implement Mapping interface"
        
        # Attempting to mutate a read-only Mapping should fail immediately
        with pytest.raises((AttributeError, TypeError)):
            AGENT_METADATA.pop('L5_Safety')
        
        with pytest.raises(TypeError):
            AGENT_METADATA['Malicious'] = "Injection"
        
        with pytest.raises((AttributeError, TypeError)):
            AGENT_METADATA.clear()
        
        with pytest.raises((AttributeError, TypeError)):
            AGENT_METADATA.update({'test': 'value'})
        
        print("✅ Metadata runtime immutability verified")

    def test_canon_key_namespace_purification(self):
        """
        [CRITICAL] Verify that structure_blueprint.py is physically scrubbed 
        of the legacy variables, leaving no logic shadows.
        """
        print("Testing Canon Key namespace purification...")
        
        forbidden = ['CANON_KEY_EXCEPTIONS', 'ACTIVE_CANON_KEYS', 'CANON_KEY_TO_FOLDER_MAP']
        current_vars = dir(structure_blueprint)
        
        for f in forbidden:
            assert f not in current_vars, f"GHOST GRAVITY: {f} still exists in SSOT"
        
        print("✅ Canon Key namespace purification verified")

    def test_final_annotation_safety(self):
        """
        [STATIC SAFETY] Verify that the AGENT_METADATA is annotated as Final 
        to signal immutability to all static analyzers.
        """
        print("Testing Final annotation safety...")
        
        from agentic_core.utils import AgentListMapping
        annotations = discovery_parser.__annotations__
        
        assert 'AGENT_METADATA' in annotations, \
            "AGENT_METADATA must have type annotations"
        
        annotation_str = str(annotations['AGENT_METADATA'])
        assert 'Final' in annotation_str, \
            f"AGENT_METADATA must be annotated as Final, got: {annotation_str}"
        
        print("✅ Final annotation safety verified")

    def test_agent_list_mapping_readonly_interface(self):
        """
        [INTERFACE SAFETY] Verify AgentListMapping properly implements 
        read-only interface without exposing mutation methods.
        """
        print("Testing AgentListMapping read-only interface...")
        
        from agentic_core.utils.discovery_parser import AgentListMapping
        
        # Create test data matching the actual structure
        test_data = [{"class_name": "TestAgent", "path": "test.py"}]
        mapping = AgentListMapping(test_data)
        
        # Verify read-only operations work
        assert mapping["0"]["class_name"] == "TestAgent"
        assert len(mapping) >= 1  # Should have at least the "0" key
        assert "0" in list(mapping)
        
        # Verify "agents" key works
        agents = mapping["agents"]
        assert isinstance(agents, list)
        assert len(agents) == 1
        
        # Verify mutation operations fail
        with pytest.raises(TypeError):
            mapping["new_key"] = "new_value"
        
        with pytest.raises((AttributeError, TypeError)):
            mapping.pop("0")
        
        with pytest.raises((AttributeError, TypeError)):
            mapping.clear()
        
        print("✅ AgentListMapping read-only interface verified")

    def test_utf8_enforcement_in_loading(self):
        """
        [ENCODING SAFETY] Verify that UTF-8 encoding is enforced 
        during metadata loading to prevent cross-platform issues.
        """
        print("Testing UTF-8 enforcement in loading...")
        
        from agentic_core.utils.discovery_parser import load_hardened_agent_metadata
        
        # Create a temporary JSON file with UTF-8 content matching agent structure
        test_path = Path("test_metadata.json")
        test_data = [{"class_name": "TestAgent", "path": "test.py", "description": "value_with_émojis_🔒"}]
        
        try:
            # Write with UTF-8
            with open(test_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(test_data, f)
            
            # Load using the hardened function
            result = load_hardened_agent_metadata(test_path)
            
            # Verify data integrity through the "agents" key
            agents = result["agents"]
            assert len(agents) == 1
            assert agents[0]["description"] == "value_with_émojis_🔒"
            
        finally:
            # Cleanup
            if test_path.exists():
                test_path.unlink()
        
        print("✅ UTF-8 enforcement verified")

    def test_no_ghost_gravity_in_imports(self):
        """
        [MEMORY SAFETY] Verify no references to Canon Key variables 
        exist in any imported modules.
        """
        print("Testing for ghost gravity in imports...")
        
        # Check that we can't import the old variables
        import agentic_core.L5_safety.validators.structure_blueprint as sb
        
        forbidden_attrs = ['CANON_KEY_EXCEPTIONS', 'ACTIVE_CANON_KEYS', 'CANON_KEY_TO_FOLDER_MAP']
        
        for attr in forbidden_attrs:
            assert not hasattr(sb, attr), f"Ghost gravity detected: {attr} still accessible"
        
        print("✅ No ghost gravity in imports verified")

    def test_mapping_behavior_consistency(self):
        """
        [BEHAVIOR SAFETY] Verify the immutable Mapping behaves consistently 
        with standard Python Mapping semantics.
        """
        print("Testing Mapping behavior consistency...")
        
        # Test basic mapping operations
        assert isinstance(AGENT_METADATA, Mapping)
        assert len(AGENT_METADATA) >= 0  # Should have some data
        
        # Test iteration - AGENT_METADATA should have "agents" key and string indices
        keys = list(AGENT_METADATA.keys())
        assert len(keys) > 0  # Should have data
        
        # Test that "agents" key exists and returns the full list
        agents = AGENT_METADATA.get("agents")
        assert agents is not None
        assert isinstance(agents, list)
        assert len(agents) > 0  # Should have agent data
        
        # Test that individual agent entries are accessible by string indices
        first_agent_key = "0"
        if first_agent_key in keys:
            result = AGENT_METADATA.get(first_agent_key)
            assert result is not None
            assert isinstance(result, dict)  # Agent data should be a dictionary
            assert 'class_name' in result  # Should have agent metadata structure
        
        # Test get method with missing key
        result = AGENT_METADATA.get("nonexistent_key", "default")
        assert result == "default"
        
        # Test that keys are strings (either "agents" or string indices)
        for key in keys[:5]:  # Check first 5 keys
            assert isinstance(key, str), f"Key should be string, got {type(key)}: {key}"
        
        print("✅ Mapping behavior consistency verified")


if __name__ == "__main__":
    # Final confirmation for 100% Pass logic.
    print("Executing Final Integrity Audit: 100% PASS required.")
    print("=" * 60)
    
    # Run pytest with verbose output
    pytest.main([__file__, "-v", "-s"])
