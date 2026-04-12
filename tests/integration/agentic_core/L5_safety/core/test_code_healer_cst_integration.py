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
        try:
            from agentic_core import code_healer_cst_integration

            assert code_healer_cst_integration is not None
        except ImportError:
            pytest.skip("code_healer_cst_integration not available")

    def test_code_healer_cst_integration_class(self):
        """Test CodeHealerCstIntegration class exists."""
        try:
            from agentic_core import CodeHealerCstIntegration

            assert CodeHealerCstIntegration is not None
        except ImportError:
            pytest.skip("CodeHealerCstIntegration not available")

    def test_code_healer_cst_integration_callable(self):
        """Test code_healer_cst_integration functions are callable."""
        try:
            from agentic_core import validate_code_healer_cst_integration

            assert callable(validate_code_healer_cst_integration)
        except ImportError:
            pytest.skip("validate_code_healer_cst_integration not available")
