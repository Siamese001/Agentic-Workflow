"""Test FcaSafetyGatesUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFcaSafetyGatesUtilAdg:
    """Test FcaSafetyGatesUtilAdg functionality."""

    def test_fca_safety_gates_util_adg_imports(self):
        """Test fca_safety_gates_util_adg module imports."""
        from agentic_core import fca_safety_gates_util_adg

        assert fca_safety_gates_util_adg is not None

    def test_fca_safety_gates_util_adg_class(self):
        """Test FcaSafetyGatesUtilAdg class exists."""
        from agentic_core import FcaSafetyGatesUtilAdg

        assert FcaSafetyGatesUtilAdg is not None

    def test_fca_safety_gates_util_adg_callable(self):
        """Test fca_safety_gates_util_adg functions are callable."""
        from agentic_core import validate_fca_safety_gates_util_adg

        assert callable(validate_fca_safety_gates_util_adg)
