"""Test ADG G23 G27 completeness accuracy functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgG23G27CompletenessAccuracy:
    """Test ADG G23 G27 completeness accuracy functionality."""

    def test_g23_g27_completeness_imports(self):
        """Test G23 G27 completeness module imports."""
        from tools.adg import identify_guardrail_gaps
        assert identify_guardrail_gaps is not None

    def test_g23_g27_completeness_check(self):
        """Test G23 G27 completeness check function."""
        from tools.adg.identify_guardrail_gaps import check_g23_g27_completeness
        assert callable(check_g23_g27_completeness)

    def test_g23_g27_accuracy_check(self):
        """Test G23 G27 accuracy check function."""
        from tools.adg.identify_guardrail_gaps import check_g23_g27_accuracy
        assert callable(check_g23_g27_accuracy)
