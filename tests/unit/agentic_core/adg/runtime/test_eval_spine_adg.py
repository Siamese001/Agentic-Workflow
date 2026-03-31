"""Test EvalSpineAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEvalSpineAdg:
    """Test EvalSpineAdg functionality."""

    def test_eval_spine_adg_imports(self):
        """Test eval_spine_adg module imports."""
        from agentic_core import eval_spine_adg
        assert eval_spine_adg is not None

    def test_eval_spine_adg_class(self):
        """Test EvalSpineAdg class exists."""
        from agentic_core import EvalSpineAdg
        assert EvalSpineAdg is not None

    def test_eval_spine_adg_callable(self):
        """Test eval_spine_adg functions are callable."""
        from agentic_core import validate_eval_spine_adg
        assert callable(validate_eval_spine_adg)
