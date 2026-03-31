"""Test DiscoverySovereignClassification functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDiscoverySovereignClassification:
    """Test DiscoverySovereignClassification functionality."""

    def test_discovery_sovereign_classification_imports(self):
        """Test discovery_sovereign_classification module imports."""
        from agentic_core import discovery_sovereign_classification
        assert discovery_sovereign_classification is not None

    def test_discovery_sovereign_classification_class(self):
        """Test DiscoverySovereignClassification class exists."""
        from agentic_core import DiscoverySovereignClassification
        assert DiscoverySovereignClassification is not None

    def test_discovery_sovereign_classification_callable(self):
        """Test discovery_sovereign_classification functions are callable."""
        from agentic_core import validate_discovery_sovereign_classification
        assert callable(validate_discovery_sovereign_classification)
