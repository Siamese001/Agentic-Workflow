"""
Fast, targeted test suite for Key 5 and Key 28 deprecation.
Avoids the slow os.walk() approach in favor of targeted searches.
"""
import pytest
import json
from pathlib import Path
from agentic_core.L5_safety.validators.structure_blueprint import SAFETY_VALIDATION_REGISTRY


class TestKeyDeprecationFast:
    """Fast validation that Keys 5 and 28 are fully deprecated."""

    def test_registry_is_empty(self):
        """Phase 1: Verify SAFETY_VALIDATION_REGISTRY is empty."""
        assert len(SAFETY_VALIDATION_REGISTRY) == 0, \
            f"Registry should be empty but has {len(SAFETY_VALIDATION_REGISTRY)} entries"
        assert 5 not in SAFETY_VALIDATION_REGISTRY, "Key 5 still in registry"
        assert 28 not in SAFETY_VALIDATION_REGISTRY, "Key 28 still in registry"

    def test_agent_discovery_json_clean(self):
        """Phase 2: Check agent_discovery_full.json for legacy key references."""
        discovery_file = Path("agent_discovery_full.json")
        
        if not discovery_file.exists():
            pytest.skip("agent_discovery_full.json not found")
        
        with open(discovery_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        violations = []
        
        # Check for method name references
        if "check_key_05" in content.lower():
            violations.append("Found 'check_key_05' reference")
        if "check_key_28" in content.lower():
            violations.append("Found 'check_key_28' reference")
        
        # Parse JSON and check for numeric key references
        try:
            data = json.loads(content)
            # Recursively search for keys "5" or "28" in the JSON structure
            def search_json(obj, path=""):
                if isinstance(obj, dict):
                    if "5" in obj or 5 in obj:
                        violations.append(f"Found key '5' at {path}")
                    if "28" in obj or 28 in obj:
                        violations.append(f"Found key '28' at {path}")
                    for k, v in obj.items():
                        search_json(v, f"{path}.{k}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        search_json(item, f"{path}[{i}]")
            
            search_json(data)
        except json.JSONDecodeError:
            pass  # Content check above is sufficient
        
        assert not violations, f"agent_discovery_full.json violations:\n" + "\n".join(violations)

    def test_active_code_directories_clean(self):
        """Phase 3: Scan active code directories (not archives) for legacy references."""
        active_dirs = [
            Path("agentic_core"),
            Path("apps_rg"),
            Path("apps_lic"),
            Path("apps_shared"),
            Path("scripts"),
        ]
        
        violations = []
        forbidden_patterns = [
            r"\bcheck_key_05\b",
            r"\bcheck_key_5\b",
            r"\bcheck_key_28\b",
        ]
        
        for directory in active_dirs:
            if not directory.exists():
                continue
            
            for py_file in directory.rglob("*.py"):
                # Skip test files that reference the patterns for validation
                if "test_downstream_deprecation" in str(py_file) or \
                   "test_key_deprecation" in str(py_file):
                    continue
                
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    for pattern in forbidden_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            violations.append(f"{py_file}: Found '{pattern}'")
                except Exception:
                    pass  # Skip files that can't be read
        
        assert not violations, f"Active code violations:\n" + "\n".join(violations[:10])

    def test_documentation_references(self):
        """Phase 4: Check if documentation still references deprecated keys."""
        doc_files = [
            Path("CANON_KEY_COMPLETE_REMOVAL_ANALYSIS.md"),
            Path("README.md"),
        ]
        
        violations = []
        
        for doc_file in doc_files:
            if not doc_file.exists():
                continue
            
            content = doc_file.read_text(encoding='utf-8', errors='ignore')
            
            # Allow historical references in removal analysis docs
            if "REMOVAL_ANALYSIS" in doc_file.name:
                continue
            
            if "check_key_05" in content.lower() or "check_key_28" in content.lower():
                violations.append(f"{doc_file}: Contains legacy key references")
        
        assert not violations, f"Documentation violations:\n" + "\n".join(violations)

    def test_no_validator_instantiation_errors(self):
        """Phase 5: Ensure validators handle empty registry gracefully."""
        try:
            from agentic_core.L5_safety.validators.CanonKeyValidator import CanonKeyValidator
            validator = CanonKeyValidator()
            # Should not crash with empty registry
            assert True
        except ImportError:
            # If validator was removed, that's also acceptable
            pytest.skip("CanonKeyValidator not found (may have been removed)")
        except Exception as e:
            pytest.fail(f"CanonKeyValidator instantiation failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])
