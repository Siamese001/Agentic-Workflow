"""
Dashboard UI Layout Tests (Phase 5)
===================================

Tests for dashboard UI layout and styling.

Migrated from: agentic_core/L0_maintenance/scripts/test_phase5_ui_layout.py
"""
import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.dashboard
class TestHTMLStructure:
    """Test HTML structure in Runtime Tab."""
    
    def test_meta_learning_container_exists(self, html_content):
        """Verify meta-learning container exists in HTML."""
        assert 'id="meta-stats"' in html_content
    
    def test_redis_container_exists(self, html_content):
        """Verify Redis container exists in HTML."""
        assert 'id="redis-stats"' in html_content
    
    def test_pinecone_container_exists(self, html_content):
        """Verify Pinecone container exists in HTML."""
        assert 'id="pinecone-stats"' in html_content
    
    def test_execution_flow_container_exists(self, html_content):
        """Verify execution flow container exists in HTML."""
        assert 'id="layer-flow"' in html_content


@pytest.mark.dashboard
class TestSectionHeaders:
    """Test section headers are present."""
    
    def test_meta_learning_header(self, html_content):
        """Verify Meta-Learning Activity header exists."""
        assert 'Meta-Learning Activity' in html_content
    
    def test_agent_execution_header(self, html_content):
        """Verify Agent Execution Flow header exists."""
        assert 'Agent Execution Flow' in html_content


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
            content = css_file.read_text(encoding='utf-8')
            assert len(content) > 100, "CSS file appears to be empty or too small"


@pytest.mark.dashboard
class TestJSIncludes:
    """Test JavaScript file includes in HTML."""
    
    def test_meta_learning_panel_included(self, html_content):
        """Verify meta-learning-panel.js is included."""
        assert 'meta-learning-panel.js' in html_content
    
    def test_redis_monitor_included(self, html_content):
        """Verify redis-monitor.js is included."""
        assert 'redis-monitor.js' in html_content
    
    def test_pinecone_monitor_included(self, html_content):
        """Verify pinecone-monitor.js is included."""
        assert 'pinecone-monitor.js' in html_content
    
    def test_execution_flow_included(self, html_content):
        """Verify execution-flow.js is included."""
        assert 'execution-flow.js' in html_content
    
    def test_controller_included(self, html_content):
        """Verify meta-learning-controller.js is included."""
        assert 'meta-learning-controller.js' in html_content
