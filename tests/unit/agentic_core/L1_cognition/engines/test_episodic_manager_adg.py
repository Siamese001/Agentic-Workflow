"""Test EpisodicManagerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEpisodicManagerAdg:
    """Test EpisodicManagerAdg functionality."""

    def test_episodic_manager_adg_imports(self):
        """Test episodic_manager_adg module imports."""
        from agentic_core import episodic_manager_adg
        assert episodic_manager_adg is not None

    def test_episodic_manager_adg_class(self):
        """Test EpisodicManagerAdg class exists."""
        from agentic_core import EpisodicManagerAdg
        assert EpisodicManagerAdg is not None

    def test_episodic_manager_adg_callable(self):
        """Test episodic_manager_adg functions are callable."""
        from agentic_core import validate_episodic_manager_adg
        assert callable(validate_episodic_manager_adg)
