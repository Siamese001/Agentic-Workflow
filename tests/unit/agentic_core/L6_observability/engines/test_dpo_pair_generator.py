"""Test DpoPairGenerator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDpoPairGenerator:
    """Test DpoPairGenerator functionality."""

    def test_dpo_pair_generator_imports(self):
        """Test dpo_pair_generator module imports."""
        from agentic_core import dpo_pair_generator
        assert dpo_pair_generator is not None

    def test_dpo_pair_generator_class(self):
        """Test DpoPairGenerator class exists."""
        from agentic_core import DpoPairGenerator
        assert DpoPairGenerator is not None

    def test_dpo_pair_generator_callable(self):
        """Test dpo_pair_generator functions are callable."""
        from agentic_core import validate_dpo_pair_generator
        assert callable(validate_dpo_pair_generator)
