"""Test L4ViolationPersistence functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL4ViolationPersistence:
    """Test L4ViolationPersistence functionality."""

    def test_l4_violation_persistence_imports(self):
        """Test l4_violation_persistence module imports."""
        from agentic_core import l4_violation_persistence
        assert l4_violation_persistence is not None

    def test_l4_violation_persistence_class(self):
        """Test L4ViolationPersistence class exists."""
        from agentic_core import L4ViolationPersistence
        assert L4ViolationPersistence is not None

    def test_l4_violation_persistence_callable(self):
        """Test l4_violation_persistence functions are callable."""
        from agentic_core import validate_l4_violation_persistence
        assert callable(validate_l4_violation_persistence)
