"""
file: tests/maintenance/verify_manifest_purity.py
description: Verifies that no files from tests/ or archives/ exist in the discovery manifest.
"""
import json
import sys
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / "agent_discovery_full.json"


def _load_manifest():
    """Load manifest directly, bypassing any test fixtures."""
    import builtins
    original_open = builtins.open
    with original_open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def disable_path_shield():
    """Marker fixture to disable path shield in conftest."""
    pass


class TestManifestPurity:
    """Tests to ensure the agent discovery manifest is free of test artifacts."""

    def test_no_tests_directory_in_manifest(self, disable_path_shield):
        """
        TC-001: Verify no files from tests/ directory are in the manifest.
        """
        data = _load_manifest()
        
        # Check for test files in the manifest
        violations = []
        for entry in data:
            path = entry.get('path', '')
            # Normalize path separators
            normalized_path = path.replace('\\', '/')
            
            # Check if path starts with tests/ or contains /tests/
            if normalized_path.startswith('tests/') or '/tests/' in normalized_path:
                violations.append(path)
        
        if violations:
            pytest.fail(f"Manifest contains {len(violations)} test files:\n" + 
                       "\n".join(f"  - {v}" for v in violations))

    def test_no_test_prefixed_files_in_manifest(self, disable_path_shield):
        """
        TC-002: Verify no test_*.py files are in the manifest (except legitimate agents).
        """
        data = _load_manifest()
        
        # Legitimate test-related agents that should be in manifest
        legitimate_test_agents = {
            'TestSovereigntyAgent.py',  # Actual agent for testing sovereignty
            'TestCoverageGuardianAgent.py',  # Actual guardian agent
            'TestGeneratorAgent.py',  # Actual test generator
            'TestPilotAgent.py',  # Actual pilot agent
        }
        
        violations = []
        for entry in data:
            path = entry.get('path', '')
            filename = Path(path).name
            
            # Check if filename starts with test_ (lowercase)
            if filename.startswith('test_'):
                violations.append(path)
        
        if violations:
            pytest.fail(f"Manifest contains {len(violations)} test_*.py files:\n" + 
                       "\n".join(f"  - {v}" for v in violations))

    def test_no_archives_in_manifest(self, disable_path_shield):
        """
        TC-003: Verify no files from archives/ directory are in the manifest.
        """
        data = _load_manifest()
        
        violations = []
        for entry in data:
            path = entry.get('path', '')
            normalized_path = path.replace('\\', '/')
            
            if 'archives/' in normalized_path or normalized_path.startswith('archives'):
                violations.append(path)
        
        if violations:
            pytest.fail(f"Manifest contains {len(violations)} archive files:\n" + 
                       "\n".join(f"  - {v}" for v in violations))

    def test_no_scripts_test_files_in_manifest(self, disable_path_shield):
        """
        TC-004: Verify no test files from scripts/ directory are in the manifest.
        """
        data = _load_manifest()
        
        violations = []
        for entry in data:
            path = entry.get('path', '')
            normalized_path = path.replace('\\', '/')
            filename = Path(path).name
            
            # Check if it's a test file in scripts/
            if normalized_path.startswith('scripts/') and filename.startswith('test_'):
                violations.append(path)
        
        if violations:
            pytest.fail(f"Manifest contains {len(violations)} test files from scripts/:\n" + 
                       "\n".join(f"  - {v}" for v in violations))


def clean_manifest():
    """Utility function to remove test artifacts from the manifest."""
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data)
    
    # Filter out test artifacts
    cleaned = []
    removed = []
    
    for entry in data:
        path = entry.get('path', '')
        normalized_path = path.replace('\\', '/')
        filename = Path(path).name
        
        # Skip tests/ directory
        if normalized_path.startswith('tests/') or '/tests/' in normalized_path:
            removed.append(path)
            continue
        
        # Skip test_*.py files in scripts/
        if normalized_path.startswith('scripts/') and filename.startswith('test_'):
            removed.append(path)
            continue
        
        # Skip archives/
        if 'archives/' in normalized_path:
            removed.append(path)
            continue
        
        cleaned.append(entry)
    
    # Write cleaned manifest
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=2)
    
    print(f"✅ Manifest cleaned: {original_count} -> {len(cleaned)} entries")
    print(f"   Removed {len(removed)} test/archive artifacts:")
    for r in removed:
        print(f"     - {r}")
    
    return len(removed)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        clean_manifest()
    else:
        sys.exit(pytest.main(["-v", __file__]))
