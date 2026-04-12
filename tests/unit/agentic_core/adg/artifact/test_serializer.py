"""Test Serializer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSerializer:
    """Test Serializer functionality."""

    def test_serializer_imports(self):
        """Test serializer module imports."""
        from agentic_core import serializer

        assert serializer is not None

    def test_serializer_class(self):
        """Test Serializer class exists."""
        from agentic_core import Serializer

        assert Serializer is not None

    def test_serializer_callable(self):
        """Test serializer functions are callable."""
        from agentic_core import validate_serializer

        assert callable(validate_serializer)
