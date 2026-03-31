"""Test GuardianManifest functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianManifest:
    """Test GuardianManifest functionality."""

    def test_guardian_manifest_imports(self):
        """Test guardian_manifest module imports."""
        from agentic_core import guardian_manifest
        assert guardian_manifest is not None

    def test_guardian_manifest_class(self):
        """Test GuardianManifest class exists."""
        from agentic_core import GuardianManifest
        assert GuardianManifest is not None

    def test_guardian_manifest_callable(self):
        """Test guardian_manifest functions are callable."""
        from agentic_core import validate_guardian_manifest
        assert callable(validate_guardian_manifest)
