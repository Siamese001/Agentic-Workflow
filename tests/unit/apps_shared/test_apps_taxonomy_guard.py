"""Test AppsTaxonomyGuard functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAppsTaxonomyGuard:
    """Test AppsTaxonomyGuard functionality."""

    def test_taxonomy_guard_imports(self):
        """Test taxonomy guard module imports."""
        from apps_shared import taxonomy_guard

        assert taxonomy_guard is not None

    def test_taxonomy_guard_class(self):
        """Test taxonomy guard class exists."""
        from apps_shared.taxonomy_guard import TaxonomyGuard

        assert TaxonomyGuard is not None

    def test_validate_taxonomy(self):
        """Test validate taxonomy function."""
        from apps_shared.taxonomy_guard import validate_taxonomy

        assert callable(validate_taxonomy)
