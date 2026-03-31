"""Test AdgIdentityNormalizer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgIdentityNormalizer:
    """Test AdgIdentityNormalizer functionality."""

    def test_identity_normalizer_imports(self):
        """Test identity normalizer module imports."""
        from tools.adg import identity_normalizer
        assert identity_normalizer is not None

    def test_identity_normalizer_class(self):
        """Test identity normalizer class exists."""
        from tools.adg.identity_normalizer import IdentityNormalizer
        assert IdentityNormalizer is not None

    def test_normalize_identity(self):
        """Test normalize identity function."""
        from tools.adg.identity_normalizer import normalize_identity
        assert callable(normalize_identity)
