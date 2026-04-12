"""Test InvokeMessageServiceAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInvokeMessageServiceAdg:
    """Test InvokeMessageServiceAdg functionality."""

    def test_invoke_message_service_adg_imports(self):
        """Test invoke_message_service_adg module imports."""
        from agentic_core import invoke_message_service_adg

        assert invoke_message_service_adg is not None

    def test_invoke_message_service_adg_class(self):
        """Test InvokeMessageServiceAdg class exists."""
        from agentic_core import InvokeMessageServiceAdg

        assert InvokeMessageServiceAdg is not None

    def test_invoke_message_service_adg_callable(self):
        """Test invoke_message_service_adg functions are callable."""
        from agentic_core import validate_invoke_message_service_adg

        assert callable(validate_invoke_message_service_adg)
