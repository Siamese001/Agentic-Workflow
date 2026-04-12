"""Test CoreIntegrityUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCoreIntegrityUtilAdg:
    """Test CoreIntegrityUtilAdg functionality."""

    def test_core_integrity_util_adg_imports(self):
        """Test core_integrity_util_adg module imports."""
        from agentic_core import core_integrity_util_adg

        assert core_integrity_util_adg is not None

    def test_core_integrity_util_adg_class(self):
        """Test CoreIntegrityUtilAdg class exists."""
        from agentic_core import CoreIntegrityUtilAdg

        assert CoreIntegrityUtilAdg is not None

    def test_core_integrity_util_adg_callable(self):
        """Test core_integrity_util_adg functions are callable."""
        from agentic_core import validate_core_integrity_util_adg

        assert callable(validate_core_integrity_util_adg)
