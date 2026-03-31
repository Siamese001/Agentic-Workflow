"""Test IncidentBundleGenerator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIncidentBundleGenerator:
    """Test IncidentBundleGenerator functionality."""

    def test_incident_bundle_generator_imports(self):
        """Test incident_bundle_generator module imports."""
        from agentic_core import incident_bundle_generator
        assert incident_bundle_generator is not None

    def test_incident_bundle_generator_class(self):
        """Test IncidentBundleGenerator class exists."""
        from agentic_core import IncidentBundleGenerator
        assert IncidentBundleGenerator is not None

    def test_incident_bundle_generator_callable(self):
        """Test incident_bundle_generator functions are callable."""
        from agentic_core import validate_incident_bundle_generator
        assert callable(validate_incident_bundle_generator)
