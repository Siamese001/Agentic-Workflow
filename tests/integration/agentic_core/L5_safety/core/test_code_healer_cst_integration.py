"""Test CodeHealerCstIntegration functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCodeHealerCstIntegration:
    """Test CodeHealerCstIntegration functionality."""

    def test_code_healer_cst_integration_imports(self):
        """Test code_healer_cst_integration module imports."""
        from agentic_core import code_healer_cst_integration
        assert code_healer_cst_integration is not None

    def test_code_healer_cst_integration_class(self):
        """Test CodeHealerCstIntegration class exists."""
        from agentic_core import CodeHealerCstIntegration
        assert CodeHealerCstIntegration is not None

    def test_code_healer_cst_integration_callable(self):
        """Test code_healer_cst_integration functions are callable."""
        from agentic_core import validate_code_healer_cst_integration
        assert callable(validate_code_healer_cst_integration)
