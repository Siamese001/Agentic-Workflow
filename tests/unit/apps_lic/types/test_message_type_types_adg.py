"""Test MessageTypeTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMessageTypeTypesAdg:
    """Test MessageTypeTypesAdg functionality."""

    def test_message_type_types_adg_imports(self):
        """Test message_type_types_adg module imports."""
        from agentic_core import message_type_types_adg
        assert message_type_types_adg is not None

    def test_message_type_types_adg_class(self):
        """Test MessageTypeTypesAdg class exists."""
        from agentic_core import MessageTypeTypesAdg
        assert MessageTypeTypesAdg is not None

    def test_message_type_types_adg_callable(self):
        """Test message_type_types_adg functions are callable."""
        from agentic_core import validate_message_type_types_adg
        assert callable(validate_message_type_types_adg)
