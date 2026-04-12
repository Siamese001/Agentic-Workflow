"""Test CheckOutputQualityUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCheckOutputQualityUtilAdg:
    """Test CheckOutputQualityUtilAdg functionality."""

    def test_check_output_quality_util_adg_imports(self):
        """Test check_output_quality_util_adg module imports."""
        from agentic_core import check_output_quality_util_adg

        assert check_output_quality_util_adg is not None

    def test_check_output_quality_util_adg_class(self):
        """Test CheckOutputQualityUtilAdg class exists."""
        from agentic_core import CheckOutputQualityUtilAdg

        assert CheckOutputQualityUtilAdg is not None

    def test_check_output_quality_util_adg_callable(self):
        """Test check_output_quality_util_adg functions are callable."""
        from agentic_core import validate_check_output_quality_util_adg

        assert callable(validate_check_output_quality_util_adg)
