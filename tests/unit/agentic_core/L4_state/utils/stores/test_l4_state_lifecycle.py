"""Test L4StateLifecycle functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL4StateLifecycle:
    """Test L4StateLifecycle functionality."""

    def test_l4_state_lifecycle_imports(self):
        """Test l4_state_lifecycle module imports."""
        from agentic_core import l4_state_lifecycle

        assert l4_state_lifecycle is not None

    def test_l4_state_lifecycle_class(self):
        """Test L4StateLifecycle class exists."""
        from agentic_core import L4StateLifecycle

        assert L4StateLifecycle is not None

    def test_l4_state_lifecycle_callable(self):
        """Test l4_state_lifecycle functions are callable."""
        from agentic_core import validate_l4_state_lifecycle

        assert callable(validate_l4_state_lifecycle)
