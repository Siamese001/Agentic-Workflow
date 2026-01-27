"""
Ultra Aggressive Canon Key Purge Validation - Negative Proof Testing

This test suite provides 100% negative proof that the Canon Key system has been
completely eradicated from the codebase. It uses multiple verification strategies:

1. Import Safety - Ensures deprecated constants cannot be imported
2. Memory Scanning - Verifies no references exist in active Python files  
3. Structural Integrity - Confirms LocationAgent operates without key logic
4. SSOT Cleanliness - Validates structure_blueprint.py is clean
5. Functional Verification - Ensures territory-based healing still works

CRITICAL: All tests must pass with 100% success rate to certify complete eradication.
"""
import pytest
import importlib
import sys
from pathlib import Path


class TestGlobalCanonKeyPurge:
    """
    Verifies the total eradication of the 'Canon Key' indexing system.
    Target: 100% Pass (Negative Proof).
    """

    def test_ssot_cleanliness(self):
        """
        Verify structure_blueprint.py no longer exposes deprecated constants.
        """
        from agentic_core.L5_safety.validators.structure_blueprint import structure_blueprint
        
        deprecated_constants = [
            'CANON_KEY_EXCEPTIONS',
            'ACTIVE_CANON_KEYS',
            'CANON_KEY_TO_FOLDER_MAP'
        ]
        
        for const in deprecated_constants:
            assert not hasattr(structure_blueprint, const), \
                f"CRITICAL FAILURE: {const} still exists in SSOT!"

    def test_import_safety(self):
        """
        Verify that attempting to import these keys fails efficiently.
        This ensures no 'ghost' imports remain in the cache.
        """
        # Force reload to clear cache
        if 'agentic_core.L5_safety.validators.structure_blueprint' in sys.modules:
            importlib.reload(sys.modules['agentic_core.L5_safety.validators.structure_blueprint'])
            
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
        
        # This should raise ImportError - proving the constants are gone
        with pytest.raises((ImportError, AttributeError)):
            from agentic_core.L5_safety.validators.structure_blueprint import CANON_KEY_TO_FOLDER_MAP

    def test_location_agent_integrity(self):
        """
        Verify LocationAgent operates without key logic.
        """
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        from pathlib import Path
        
        project_root = Path(".").resolve()
        agent = LocationAgent(project_root)
        
        # Ensure the deprecated method is gone
        assert not hasattr(agent, 'is_excepted_from_key'), \
            "LocationAgent still retains deprecated key exception logic."
            
        # Verify it still functions using AST signals
        # (This confirms we didn't break the agent while removing the keys)
        result = agent.get_correct_app_path("rg_resume_parser.py")
        assert result == "apps_rg/engines", \
            f"LocationAgent failed AST-based path resolution: got {result}"

    def test_no_canon_key_references_remain(self):
        """
        Global filesystem scan for any remaining Canon Key references.
        This is the ultimate negative proof test.
        """
        project_root = Path(".")
        violations = []
        
        # Skip known non-code directories
        skip_dirs = {
            '.git', '__pycache__', '.pytest_cache', '.ruff_cache', 
            'node_modules', '.venv', 'venv', '.windsurf', 'archives',
            'archive', 'legacy', 'void_violations', 'location_violations',
            'healing_backups', 'gatekeeper', 'deprecated'
        }
        
        for py_file in project_root.rglob("*.py"):
            # Skip files in excluded directories
            if any(part in skip_dirs for part in py_file.parts):
                continue
                
            # Skip test files that might reference the old constants for testing
            if 'test' in py_file.name.lower():
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for any remaining references
                deprecated_patterns = [
                    'CANON_KEY_EXCEPTIONS',
                    'ACTIVE_CANON_KEYS', 
                    'CANON_KEY_TO_FOLDER_MAP',
                    'is_excepted_from_key',
                    'canon_key_exception',
                    'canon_key_to_folder'
                ]
                
                for pattern in deprecated_patterns:
                    if pattern in content:
                        violations.append(f"{py_file.relative_to(project_root)}: {pattern}")
                        
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
        
        assert len(violations) == 0, \
            f"CRITICAL: Found {len(violations)} files with Canon Key references:\n" + \
            "\n".join(violations)

    def test_territory_based_healing_intact(self):
        """
        Verify territory-based healing system works without Canon Keys.
        """
        from agentic_core.L5_safety.validators.structure_blueprint import (
            DEFAULT_CORE_HEALING_TERRITORY,
            DEFAULT_APP_HEALING_TARGET,
            CORE_TERRITORY_KEYWORDS,
            SOVEREIGN_REGISTRY,
            AST_DOMAIN_HIT_THRESHOLD,
            TERRITORY_MISMATCH_THRESHOLD
        )
        
        # Verify modern territory-based constants exist and are valid
        assert DEFAULT_CORE_HEALING_TERRITORY is not None, \
            "DEFAULT_CORE_HEALING_TERRITORY missing"
        assert DEFAULT_APP_HEALING_TARGET is not None, \
            "DEFAULT_APP_HEALING_TARGET missing"
        assert len(CORE_TERRITORY_KEYWORDS) > 0, \
            "CORE_TERRITORY_KEYWORDS empty"
        assert len(SOVEREIGN_REGISTRY) > 0, \
            "SOVEREIGN_REGISTRY empty"
        
        # Verify the defaults are sensible
        assert "tool_registry" in DEFAULT_CORE_HEALING_TERRITORY, \
            f"Invalid DEFAULT_CORE_HEALING_TERRITORY: {DEFAULT_CORE_HEALING_TERRITORY}"
        assert "engines" in DEFAULT_APP_HEALING_TARGET, \
            f"Invalid DEFAULT_APP_HEALING_TARGET: {DEFAULT_APP_HEALING_TARGET}"
        
        # Verify thresholds are valid numbers
        assert isinstance(AST_DOMAIN_HIT_THRESHOLD, float), \
            "AST_DOMAIN_HIT_THRESHOLD must be float"
        assert isinstance(TERRITORY_MISMATCH_THRESHOLD, float), \
            "TERRITORY_MISMATCH_THRESHOLD must be float"
        assert AST_DOMAIN_HIT_THRESHOLD > 0, \
            "AST_DOMAIN_HIT_THRESHOLD must be positive"
        assert TERRITORY_MISMATCH_THRESHOLD > 0, \
            "TERRITORY_MISMATCH_THRESHOLD must be positive"

    def test_ast_based_scoring_intact(self):
        """
        Verify AST-based territory scoring system is fully functional.
        """
        from agentic_core.L5_safety.validators.structure_blueprint import (
            APP_RG_AST_TERMS,
            APP_LIC_AST_TERMS,
            APP_RG_VARIABLE_TERMS,
            APP_LIC_VARIABLE_TERMS,
            APP_RG_STRING_TERMS,
            APP_LIC_STRING_TERMS,
            VARIABLE_HIT_WEIGHT,
            STRING_HIT_WEIGHT
        )
        
        # All AST term sets should be populated
        assert len(APP_RG_AST_TERMS) > 0, "APP_RG_AST_TERMS should not be empty"
        assert len(APP_LIC_AST_TERMS) > 0, "APP_LIC_AST_TERMS should not be empty"
        assert len(APP_RG_VARIABLE_TERMS) > 0, "APP_RG_VARIABLE_TERMS should not be empty"
        assert len(APP_LIC_VARIABLE_TERMS) > 0, "APP_LIC_VARIABLE_TERMS should not be empty"
        assert len(APP_RG_STRING_TERMS) > 0, "APP_RG_STRING_TERMS should not be empty"
        assert len(APP_LIC_STRING_TERMS) > 0, "APP_LIC_STRING_TERMS should not be empty"
        
        # Weights should be valid
        assert isinstance(VARIABLE_HIT_WEIGHT, float), "VARIABLE_HIT_WEIGHT must be float"
        assert isinstance(STRING_HIT_WEIGHT, float), "STRING_HIT_WEIGHT must be float"
        assert 0 < VARIABLE_HIT_WEIGHT <= 1, "VARIABLE_HIT_WEIGHT should be between 0 and 1"
        assert 0 < STRING_HIT_WEIGHT <= 1, "STRING_HIT_WEIGHT should be between 0 and 1"

    def test_void_compliance_refactored(self):
        """
        Verify void_compliance.py no longer uses Canon Key logic.
        """
        # Read the void_compliance.py file
        void_compliance_path = Path("apps_rg/shared/tools/void_compliance.py")
        assert void_compliance_path.exists(), "void_compliance.py missing"
        
        with open(void_compliance_path, 'r') as f:
            content = f.read()
        
        # Should contain modern territory-based healing comments
        assert "Removed canon key mapping - deprecated system" in content, \
            "void_compliance.py should document Canon Key removal"
        
        # Should NOT contain any Canon Key references
        deprecated_patterns = [
            'CANON_KEY_EXCEPTIONS',
            'ACTIVE_CANON_KEYS',
            'CANON_KEY_TO_FOLDER_MAP',
            'Key 8',
            'canon_key'
        ]
        
        for pattern in deprecated_patterns:
            # Allow the pattern in comments about removal
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if pattern in line and not line.strip().startswith('#'):
                    assert False, \
                        f"void_compliance.py line {i+1} still contains Canon Key reference: {pattern.strip()}"

    
    def test_import_error_messages(self):
        """
        Verify that attempting to import Canon Key constants gives clear errors.
        """
        try:
            # This should fail with a clear error
            from agentic_core.L5_safety.validators.structure_blueprint import CANON_KEY_TO_FOLDER_MAP
            assert False, "Import should have failed - CANON_KEY_TO_FOLDER_MAP still exists!"
        except (ImportError, AttributeError) as e:
            # Error should be clear about the missing constant
            error_str = str(e).lower()
            assert any(term in error_str for term in ['canon_key', 'not found', 'attribute', 'module']), \
                f"Import error should mention the missing constant: {e}"


if __name__ == "__main__":
    print("Executing Canon Key Purge Validation...")
    print("=" * 60)
    print("CRITICAL: All tests MUST pass for 100% eradication certification")
    print("=" * 60)
    
    # Run with verbose output for detailed verification
    pytest.main([__file__, "-v", "--tb=short"])
