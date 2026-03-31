"""Test DiscoveryCanonicalIdentity functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDiscoveryCanonicalIdentity:
    """Test DiscoveryCanonicalIdentity functionality."""

    def test_discovery_canonical_identity_imports(self):
        """Test discovery_canonical_identity module imports."""
        from agentic_core import discovery_canonical_identity
        assert discovery_canonical_identity is not None

    def test_discovery_canonical_identity_class(self):
        """Test DiscoveryCanonicalIdentity class exists."""
        from agentic_core import DiscoveryCanonicalIdentity
        assert DiscoveryCanonicalIdentity is not None

    def test_discovery_canonical_identity_callable(self):
        """Test discovery_canonical_identity functions are callable."""
        from agentic_core import validate_discovery_canonical_identity
        assert callable(validate_discovery_canonical_identity)
