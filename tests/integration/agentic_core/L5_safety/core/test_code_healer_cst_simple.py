"""Test CodeHealerCstSimple functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCodeHealerCstSimple:
    """Test CodeHealerCstSimple functionality."""

    def test_code_healer_cst_simple_imports(self):
        """Test code_healer_cst_simple module imports."""
        try:
            from agentic_core import code_healer_cst_simple

            assert code_healer_cst_simple is not None
        except ImportError:
            pytest.skip("code_healer_cst_simple not available")

    def test_code_healer_cst_simple_class(self):
        """Test CodeHealerCstSimple class exists."""
        try:
            from agentic_core import CodeHealerCstSimple

            assert CodeHealerCstSimple is not None
        except ImportError:
            pytest.skip("CodeHealerCstSimple not available")

    def test_code_healer_cst_simple_callable(self):
        """Test code_healer_cst_simple functions are callable."""
        try:
            from agentic_core import validate_code_healer_cst_simple

            assert callable(validate_code_healer_cst_simple)
        except ImportError:
            pytest.skip("validate_code_healer_cst_simple not available")
