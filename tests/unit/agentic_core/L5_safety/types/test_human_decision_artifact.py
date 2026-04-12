"""Test HumanDecisionArtifact functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHumanDecisionArtifact:
    """Test HumanDecisionArtifact functionality."""

    def test_human_decision_artifact_imports(self):
        """Test human_decision_artifact module imports."""
        from agentic_core import human_decision_artifact

        assert human_decision_artifact is not None

    def test_human_decision_artifact_class(self):
        """Test HumanDecisionArtifact class exists."""
        from agentic_core import HumanDecisionArtifact

        assert HumanDecisionArtifact is not None

    def test_human_decision_artifact_callable(self):
        """Test human_decision_artifact functions are callable."""
        from agentic_core import validate_human_decision_artifact

        assert callable(validate_human_decision_artifact)
