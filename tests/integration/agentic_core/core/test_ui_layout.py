"""
Dashboard UI Layout Tests (Phase 5)
===================================

Tests for dashboard UI layout and styling.

Migrated from: agentic_core/L0_maintenance/scripts/test_phase5_ui_layout.py
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.dashboard
class TestHTMLStructure:
    """Test HTML structure - core elements that must exist."""

    def test_dashboard_data_container_exists(self, html_content):
        """Verify dashboardData is present in HTML."""
        assert "dashboardData" in html_content

    def test_real_agent_data_container_exists(self, html_content):
        """Verify realAgentData is present in HTML."""
        assert "realAgentData" in html_content

    def test_table_containers_exist(self, html_content):
        """Verify table rendering functions are present."""
        assert "renderTerritorySummaryTable" in html_content or "kpiGrid" in html_content

    def test_drill_modal_exists(self, html_content):
        """Verify drill-down modal exists in HTML."""
        assert "drillModal" in html_content


@pytest.mark.dashboard
class TestSectionHeaders:
    """Test section headers are present."""

    def test_territory_summary_header(self, html_content):
        """Verify Territory Summary or similar header exists."""
        has_header = any(
            h in html_content for h in ["Territory Summary", "Autonomy Compliance", "Dashboard"]
        )
        assert has_header, "No dashboard header found"

    def test_code_quality_section(self, html_content):
        """Verify Code Quality section exists."""
        has_section = any(
            s in html_content for s in ["Code Quality", "codeQualityGrid", "renderCodeQualityTable"]
        )
        assert has_section, "No code quality section found"


@pytest.mark.dashboard
class TestCSSFiles:
    """Test CSS file existence and structure."""

    def test_meta_learning_css_exists(self, css_dir):
        """Verify meta-learning.css exists."""
        css_file = css_dir / "meta-learning.css"
        assert css_file.exists(), f"Missing: {css_file}"

    def test_css_has_content(self, css_dir):
        """Verify CSS file has meaningful content."""
        css_file = css_dir / "meta-learning.css"
        if css_file.exists():
            content = css_file.read_text(encoding="utf-8")
            assert len(content) > 100, "CSS file appears to be empty or too small"


@pytest.mark.dashboard
class TestJSIncludes:
    """Test JavaScript functionality in HTML (inline or external)."""

    def test_table_rendering_functions_present(self, html_content):
        """Verify table rendering functions are present."""
        has_render = any(
            f in html_content for f in ["renderTerritorySummaryTable", "renderCodeQualityTable"]
        )
        assert has_render, "Table rendering functions not found"

    def test_load_data_function_present(self, html_content):
        """Verify loadData function is present."""
        assert "loadData" in html_content, "loadData function not found"

    def test_drill_down_functions_present(self, html_content):
        """Verify drill-down modal functions are present."""
        has_drill = any(f in html_content for f in ["openDrillModal", "drillModal"])
        assert has_drill, "Drill-down functions not found"

    def test_plotly_integration_present(self, html_content):
        """Verify Plotly integration is present."""
        assert "Plotly" in html_content or "plotly" in html_content, "Plotly not found"
