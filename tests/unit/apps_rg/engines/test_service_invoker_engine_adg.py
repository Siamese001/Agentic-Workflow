"""Test ServiceInvokerEngineAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestServiceInvokerEngineAdg:
    """Test ServiceInvokerEngineAdg functionality."""

    def test_service_invoker_engine_adg_imports(self):
        """Test service_invoker_engine_adg module imports."""
        from agentic_core import service_invoker_engine_adg
        assert service_invoker_engine_adg is not None

    def test_service_invoker_engine_adg_class(self):
        """Test ServiceInvokerEngineAdg class exists."""
        from agentic_core import ServiceInvokerEngineAdg
        assert ServiceInvokerEngineAdg is not None

    def test_service_invoker_engine_adg_callable(self):
        """Test service_invoker_engine_adg functions are callable."""
        from agentic_core import validate_service_invoker_engine_adg
        assert callable(validate_service_invoker_engine_adg)
