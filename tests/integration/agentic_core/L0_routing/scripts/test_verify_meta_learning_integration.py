"""Test VerifyMetaLearningIntegration functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVerifyMetaLearningIntegration:
    """Test VerifyMetaLearningIntegration functionality."""

    def test_meta_learning_integration_imports(self):
        """Test meta learning integration module imports."""
        from agentic_core.L0_routing.scripts import verify_meta_learning
        assert verify_meta_learning is not None

    def test_meta_learning_verifier(self):
        """Test meta learning verifier exists."""
        from agentic_core.L0_routing.scripts.verify_meta_learning import MetaLearningVerifier
        assert MetaLearningVerifier is not None

    def test_verify_integration(self):
        """Test verify integration function."""
        from agentic_core.L0_routing.scripts.verify_meta_learning import verify_integration
        assert callable(verify_integration)
