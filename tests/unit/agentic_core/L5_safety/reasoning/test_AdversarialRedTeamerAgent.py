"""Test Adversarialredteameragent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdversarialredteameragent:
    """Test Adversarialredteameragent functionality."""

    def test_AdversarialRedTeamerAgent_imports(self):
        """Test AdversarialRedTeamerAgent module imports."""
        from agentic_core import AdversarialRedTeamerAgent

        assert AdversarialRedTeamerAgent is not None

    def test_AdversarialRedTeamerAgent_class(self):
        """Test Adversarialredteameragent class exists."""
        from agentic_core import Adversarialredteameragent

        assert Adversarialredteameragent is not None

    def test_AdversarialRedTeamerAgent_callable(self):
        """Test AdversarialRedTeamerAgent functions are callable."""
        from agentic_core import validate_AdversarialRedTeamerAgent

        assert callable(validate_AdversarialRedTeamerAgent)
