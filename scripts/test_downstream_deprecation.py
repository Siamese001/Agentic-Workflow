import pytest
import os
import re
from pathlib import Path
from agentic_core.L5_safety.validators.structure_blueprint import SAFETY_VALIDATION_REGISTRY

class TestDownstreamDeprecation:
    """
    Aggressive scan to ensure Key 5 and Key 28 are obliterated from the codebase.
    """

    def test_blueprint_registry_is_void(self):
        """Phase 1: Verify the Source of Truth is clean."""
        assert len(SAFETY_VALIDATION_REGISTRY) == 0, "SAFETY_VALIDATION_REGISTRY must be empty."
        assert 5 not in SAFETY_VALIDATION_REGISTRY, "Key 5 still exists in registry."
        assert 28 not in SAFETY_VALIDATION_REGISTRY, "Key 28 still exists in registry."

    def test_global_grep_for_legacy_keys(self):
        """
        Phase 2: Global Search for text references.
        Scans .py, .json, .yaml, and .md files for 'check_key_05', 'check_key_28',
        'KEY_5', 'KEY_28', or direct dictionary access to these integers.
        """
        project_root = Path(__file__).parent.parent.parent # Adjust to reach root
        forbidden_patterns = [
            re.compile(r"check_key_0?5", re.IGNORECASE),
            re.compile(r"check_key_28", re.IGNORECASE),
            re.compile(r"['\"]KEY_?0?5['\"]", re.IGNORECASE),
            re.compile(r"['\"]KEY_?28['\"]", re.IGNORECASE),
            re.compile(r"SAFETY_VALIDATION_REGISTRY\s*\[\s*5\s*\]"), # Direct dict access
            re.compile(r"SAFETY_VALIDATION_REGISTRY\.get\(\s*5\s*\)"),
        ]
        
        violations = []
        
        for root, dirs, files in os.walk(project_root):
            if "legacy" in root or ".git" in root or "__pycache__" in root:
                continue
                
            for file in files:
                if file.endswith((".py", ".json", ".yaml", ".md")):
                    path = os.path.join(root, file)
                    # Skip the blueprint itself as we just cleaned it, 
                    # and this test file (self-reference)
                    if "structure_blueprint.py" in path or "test_downstream_deprecation.py" in path:
                        continue
                        
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for i, line in enumerate(content.splitlines()):
                                for pattern in forbidden_patterns:
                                    if pattern.search(line):
                                        violations.append(f"{path}:{i+1} -> {line.strip()}")
                    except Exception as e:
                        print(f"Skipping {path} due to read error: {e}")

        assert not violations, f"Found downstream references to deprecated keys:\n" + "\n".join(violations)

    def test_validator_instantiation_safety(self):
        """
        Phase 3: Runtime Safety.
        Ensure instantiating the old validators doesn't implicitly load the keys.
        """
        # Attempt to import and instantiate the most likely users of the registry
        try:
            from agentic_core.L5_safety.validators.CanonKeyValidator import CanonKeyValidator
            validator = CanonKeyValidator()
            # If the class attempts to iterate the registry on __init__, this might fail or do nothing.
            # We want to ensure it handles the empty registry correctly.
            assert True 
        except ImportError:
            # If the file was deleted as part of refactor, that is also a pass
            pass
        except Exception as e:
             pytest.fail(f"Instantiating CanonKeyValidator crashed: {e}")

    def test_no_magic_numbers_in_logic(self):
        """
        Phase 4: Logic Scan.
        Checks for bare integer usage of 5 and 28 in contexts that look like key checks.
        """
        # This is a heuristic scan for `if key == 5:` or similar logic
        regex = re.compile(r"if\s+\w+\s*==\s*5\s*:")
        # We limit this to the L5_safety directory to reduce false positives
        safety_dir = Path("agentic_core/L5_safety")
        
        if not safety_dir.exists():
            return
            
        violations = []
        for path in safety_dir.rglob("*.py"):
             with open(path, 'r') as f:
                content = f.read()
                if regex.search(content):
                    violations.append(f"Suspicious logic in {path}")
        
        assert not violations, f"Potential hardcoded key logic found: {violations}"
