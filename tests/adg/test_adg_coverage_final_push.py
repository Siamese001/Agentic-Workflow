"""Test ADG coverage final push functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgCoverageFinalPush:
    """Test ADG coverage final push functionality."""

    def test_coverage_analysis_module_exists(self):
        """Test coverage analysis module exists."""
        from tools.adg.coverage_analysis import analyze_coverage

        assert callable(analyze_coverage)

    def test_coverage_full_report_module_exists(self):
        """Test coverage full report module exists."""
        from tools.adg.coverage_full_report import generate_report

        assert callable(generate_report)

    def test_final_coverage_report_module_exists(self):
        """Test final coverage report module exists."""
        from tools.adg.final_coverage_report import main

        assert callable(main)

    def test_check_new_stub_coverage_module_exists(self):
        """Test check new stub coverage module exists."""
        from tools.adg.check_new_stub_coverage import check_coverage

        assert callable(check_coverage)

    def test_delete_redundant_stubs_module_exists(self):
        """Test delete redundant stubs module exists."""
        from tools.adg.delete_redundant_stubs import find_redundant

        assert callable(find_redundant)

    def test_coverage_split_analysis_module_exists(self):
        """Test coverage split analysis module exists."""
        from tools.adg.coverage_split_analysis import analyze_split

        assert callable(analyze_split)


if __name__ == '__main__':
    unittest.main()
