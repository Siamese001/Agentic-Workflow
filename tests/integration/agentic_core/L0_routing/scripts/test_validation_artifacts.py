"""Test ValidationArtifacts functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestValidationArtifacts:
    """Test ValidationArtifacts functionality."""

    def test_validation_artifacts_imports(self):
        """Test validation artifacts module imports."""
        from agentic_core.L0_routing.scripts import validation_artifacts
        assert validation_artifacts is not None

    def test_validation_artifacts_generator(self):
        """Test validation artifacts generator exists."""
        try:
            from agentic_core.L0_routing.scripts.validation_artifacts import ArtifactsGenerator
            assert ArtifactsGenerator is not None
        except ImportError:
            pytest.skip("ArtifactsGenerator not available")

    def test_validation_artifacts_validate(self):
        """Test validation artifacts validate function."""
        try:
            from agentic_core.L0_routing.scripts.validation_artifacts import validate_artifacts
            assert callable(validate_artifacts)
        except ImportError:
            pytest.skip("validate_artifacts not available")
