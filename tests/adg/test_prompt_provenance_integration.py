"""Test prompt provenance integration functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPromptProvenanceIntegration:
    """Test prompt provenance integration functionality."""

    def test_prompt_provenance_integration_imports(self):
        """Test prompt provenance integration module imports."""
        from system_learning.provenance import integration
        assert integration is not None

    def test_prompt_provenance_integrator_class(self):
        """Test prompt provenance integrator class exists."""
        from system_learning.provenance.integration import PromptProvenanceIntegrator
        assert PromptProvenanceIntegrator is not None

    def test_prompt_provenance_integrate_function(self):
        """Test prompt provenance integrate function."""
        from system_learning.provenance.integration import integrate_prompt_provenance
        assert callable(integrate_prompt_provenance)
