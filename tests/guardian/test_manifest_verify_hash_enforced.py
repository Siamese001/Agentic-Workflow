"""Test ManifestVerifyHashEnforced functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestManifestVerifyHashEnforced:
    """Test ManifestVerifyHashEnforced functionality."""

    def test_manifest_verify_hash_enforced_imports(self):
        """Test manifest_verify_hash_enforced module imports."""
        from agentic_core import manifest_verify_hash_enforced
        assert manifest_verify_hash_enforced is not None

    def test_manifest_verify_hash_enforced_class(self):
        """Test ManifestVerifyHashEnforced class exists."""
        from agentic_core import ManifestVerifyHashEnforced
        assert ManifestVerifyHashEnforced is not None

    def test_manifest_verify_hash_enforced_callable(self):
        """Test manifest_verify_hash_enforced functions are callable."""
        from agentic_core import validate_manifest_verify_hash_enforced
        assert callable(validate_manifest_verify_hash_enforced)
