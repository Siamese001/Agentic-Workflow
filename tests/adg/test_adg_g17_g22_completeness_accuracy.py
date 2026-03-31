"""Test ADG G17 G22 completeness accuracy functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgG17G22CompletenessAccuracy:
    """Test ADG G17 G22 completeness accuracy functionality."""

    def test_g17_g22_completeness_imports(self):
        """Test G17 G22 completeness module imports."""
        from tools.adg import identify_guardrail_gaps
        assert identify_guardrail_gaps is not None

    def test_g17_g22_completeness_check(self):
        """Test G17 G22 completeness check function."""
        from tools.adg.identify_guardrail_gaps import check_g17_g22_completeness
        assert callable(check_g17_g22_completeness)

    def test_g17_g22_accuracy_check(self):
        """Test G17 G22 accuracy check function."""
        from tools.adg.identify_guardrail_gaps import check_g17_g22_accuracy
        assert callable(check_g17_g22_accuracy)
