"""Test CodeHealerStructuralCst functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCodeHealerStructuralCst:
    """Test CodeHealerStructuralCst functionality."""

    def test_code_healer_structural_cst_imports(self):
        """Test code_healer_structural_cst module imports."""
        from agentic_core import code_healer_structural_cst
        assert code_healer_structural_cst is not None

    def test_code_healer_structural_cst_class(self):
        """Test CodeHealerStructuralCst class exists."""
        from agentic_core import CodeHealerStructuralCst
        assert CodeHealerStructuralCst is not None

    def test_code_healer_structural_cst_callable(self):
        """Test code_healer_structural_cst functions are callable."""
        from agentic_core import validate_code_healer_structural_cst
        assert callable(validate_code_healer_structural_cst)
