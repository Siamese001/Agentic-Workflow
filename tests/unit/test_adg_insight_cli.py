"""Test AdgInsightCli functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgInsightCli:
    """Test AdgInsightCli functionality."""

    def test_adg_insight_imports(self):
        """Test ADG insight module imports."""
        from tools.adg import insight_cli
        assert insight_cli is not None

    def test_insight_cli_class(self):
        """Test insight CLI class exists."""
        from tools.adg.insight_cli import InsightCLI
        assert InsightCLI is not None

    def test_run_insight_cli(self):
        """Test run insight CLI function."""
        from tools.adg.insight_cli import run_insight
        assert callable(run_insight)
