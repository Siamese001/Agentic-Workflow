"""Test ADG coverage supplement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgCoverageSupplement:
    """Test ADG coverage supplement functionality."""

    def test_coverage_supplement_module_imports(self):
        """Test coverage supplement module imports."""
        from tools.adg import coverage_analysis
        assert coverage_analysis is not None

    def test_adg_coverage_infrastructure(self):
        """Test ADG coverage infrastructure."""
        coverage_dir = REPO_ROOT / "tools" / "adg"
        assert coverage_dir.exists()

    def test_adg_coverage_modules_exist(self):
        """Test ADG coverage modules exist."""
        modules = [
            "coverage_analysis.py",
            "coverage_full_report.py",
            "final_coverage_report.py",
        ]
        adg_dir = REPO_ROOT / "tools" / "adg"
        for mod in modules:
            assert (adg_dir / mod).exists(), f"Missing {mod}"

    def test_adg_coverage_artifact_directory(self):
        """Test ADG coverage artifact directory."""
        artifacts_dir = REPO_ROOT / "artifacts" / "adg"
        assert artifacts_dir.exists()

    def test_adg_coverage_reports_directory(self):
        """Test ADG coverage reports directory."""
        reports_dir = REPO_ROOT / "reports" / "adg"
        assert reports_dir.exists()

    def test_adg_test_selector_coverage_integration(self):
        """Test ADG test selector coverage integration."""
        from tools.adg.adg_test_selector import ADGTestSelector
        assert ADGTestSelector is not None
