#!/usr/bin/env python3
"""
Hardened test suite for dashboard data pipeline.

Tests the critical failure points:
1. Dashboard HTML loading
2. Data injection validation
3. JSON file sourcing from discovery
4. Template placeholder replacement
5. Atomic write operations

This test suite is designed to catch the recurring failures in the dashboard pipeline.

NOTE: These tests use @pytest.mark.usefixtures("disable_path_shield") to bypass
the path_shield fixture in conftest.py, since we need to test REAL file I/O,
not mocked paths.
"""
import json
import re
import os
from pathlib import Path
import pytest
import tempfile
import shutil

# Disable path_shield for all tests in this module - we need real file I/O
pytestmark = pytest.mark.usefixtures("disable_path_shield")


# Get project root - use absolute path to avoid pytest working directory issues
# When pytest runs, __file__ gives us the absolute path to this test file
_TEST_FILE = Path(__file__).resolve()
PROJECT_ROOT = _TEST_FILE.parent.parent  # Go up from tests/ to project root
REPORTS_DIR = PROJECT_ROOT / "reports"
DASHBOARD_PATH = REPORTS_DIR / "autonomy_dashboard.html"
DISCOVERY_JSON_PATH = REPORTS_DIR / ".dashboard_cache.json"
TEMPLATE_PATH = PROJECT_ROOT / "agentic_core" / "config" / "validators" / "dashboard_template.html"

# Debug: Print paths when module loads (only in verbose mode)
if os.getenv('PYTEST_CURRENT_TEST'):
    import sys
    if '-v' in sys.argv or '--verbose' in sys.argv:
        print(f"\n[DEBUG] Test file: {_TEST_FILE}")
        print(f"[DEBUG] PROJECT_ROOT: {PROJECT_ROOT}")
        print(f"[DEBUG] REPORTS_DIR exists: {REPORTS_DIR.exists()}")
        print(f"[DEBUG] DASHBOARD_PATH exists: {DASHBOARD_PATH.exists()}")


class TestDashboardHTMLLoading:
    """Test dashboard HTML file loading and accessibility."""
    
    def test_dashboard_file_exists(self):
        """Test that dashboard HTML file exists after generation."""
        assert DASHBOARD_PATH.exists(), (
            f"Dashboard HTML not found at {DASHBOARD_PATH}\n"
            f"Project root: {PROJECT_ROOT}\n"
            f"Reports dir exists: {REPORTS_DIR.exists()}\n"
            f"This indicates dashboard generation failed or output path is wrong."
        )
    
    def test_dashboard_file_not_empty(self):
        """Test that dashboard HTML is not empty."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")
        
        size = DASHBOARD_PATH.stat().st_size
        assert size > 100000, (  # Should be at least 100KB
            f"Dashboard HTML is too small ({size} bytes)\n"
            f"Expected at least 100KB. File may be truncated or incomplete."
        )
    
    def test_dashboard_html_valid_utf8(self):
        """Test that dashboard HTML is valid UTF-8."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")
        
        try:
            html = DASHBOARD_PATH.read_text(encoding='utf-8')
            assert len(html) > 0, "Dashboard HTML is empty"
        except UnicodeDecodeError as e:
            pytest.fail(f"Dashboard HTML contains invalid UTF-8: {e}")
    
    def test_dashboard_html_structure(self):
        """Test that dashboard HTML has basic structure."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        required_elements = [
            '<!DOCTYPE html>',
            '<html',
            '<head>',
            '<body>',
            '</body>',
            '</html>',
        ]
        
        missing = [elem for elem in required_elements if elem not in html]
        assert not missing, (
            f"Dashboard HTML missing required elements: {missing}\n"
            f"HTML structure is malformed."
        )


class TestDataInjection:
    """Test data injection into dashboard template."""
    
    def test_dashboard_data_injected(self):
        """Test that dashboardData is injected (placeholder removed)."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        # Check placeholder is removed
        assert 'const dashboardData = [];' not in html, (
            "dashboardData placeholder still present - injection failed!\n"
            "This is a critical error. Data was not injected into template."
        )
        
        # Check actual data is present
        assert 'const dashboardData = [' in html, (
            "dashboardData not found in HTML\n"
            "Data injection failed completely."
        )
    
    def test_recommendations_data_injected(self):
        """Test that recommendationsData is injected."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        assert 'const recommendationsData = [];' not in html, (
            "recommendationsData placeholder still present - injection failed!"
        )
        assert 'const recommendationsData = [' in html, (
            "recommendationsData not found in HTML"
        )
    
    def test_strategic_review_injected(self):
        """Test that strategic review is injected."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        assert '<!-- STRATEGIC_REVIEW_INSERT -->' not in html, (
            "Strategic review placeholder still present - injection failed!"
        )
    
    def test_top_recs_injected(self):
        """Test that top recommendations are injected."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        assert '<!-- TOP_RECS_INSERT -->' not in html, (
            "Top recommendations placeholder still present - injection failed!"
        )
    
    def test_gauge_data_injected(self):
        """Test that gauge data is injected."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        assert 'const gaugeData = {};' not in html, (
            "gaugeData placeholder still present - injection failed!"
        )
        assert 'const gaugeData = {' in html, (
            "gaugeData not found in HTML"
        )
    
    def test_last_updated_injected(self):
        """Test that last updated timestamp is injected."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        assert 'const lastUpdatedStr = "";' not in html, (
            "lastUpdatedStr placeholder still present - injection failed!"
        )
        assert 'const lastUpdatedStr = "' in html, (
            "lastUpdatedStr not found in HTML"
        )
    
    def test_injected_data_valid_json(self):
        """Test that injected data is valid JSON."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        # Extract dashboardData
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData from HTML"
        
        try:
            data = json.loads(match.group(1))
            assert isinstance(data, list), "dashboardData is not a list"
            assert len(data) > 0, "dashboardData is empty"
        except json.JSONDecodeError as e:
            pytest.fail(f"dashboardData is not valid JSON: {e}")
    
    def test_injected_data_has_total_row(self):
        """Test that injected data contains TOTAL row."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData"
        
        data = json.loads(match.group(1))
        total_row = next((r for r in data if r.get('Territory') == 'TOTAL'), None)
        
        assert total_row is not None, (
            "TOTAL row not found in dashboardData\n"
            "Data aggregation failed."
        )
        
        # Validate TOTAL row has required fields
        required_fields = ['Total', 'Health', 'Invocation %', 'Test %', 'Observable %']
        missing_fields = [f for f in required_fields if f not in total_row]
        assert not missing_fields, (
            f"TOTAL row missing required fields: {missing_fields}"
        )


class TestJSONFileSourceing:
    """Test JSON file sourcing from discovery pipeline."""
    
    def test_discovery_json_exists(self):
        """Test that discovery JSON file exists."""
        # Dashboard uses .dashboard_cache.json as the source
        json_path = (Path(__file__).parent.parent / "reports" / ".dashboard_cache.json").resolve()
        assert json_path.exists(), (
            f"Discovery JSON not found at {json_path}\n"
            f"Agent discovery must run before dashboard generation.\n"
            f"Expected: .dashboard_cache.json (dashboard's data source)"
        )
    
    def test_discovery_json_not_empty(self):
        """Test that discovery JSON is not empty."""
        json_path = (Path(__file__).parent.parent / "reports" / ".dashboard_cache.json").resolve()
        if not json_path.exists():
            pytest.skip("Discovery JSON not found")
        
        size = json_path.stat().st_size
        assert size > 1000, (  # Should be at least 1KB
            f"Discovery JSON is too small ({size} bytes)\n"
            f"Discovery may have failed or returned no results."
        )
    
    def test_discovery_json_valid(self):
        """Test that discovery JSON is valid JSON."""
        json_path = (Path(__file__).parent.parent / "reports" / ".dashboard_cache.json").resolve()
        if not json_path.exists():
            pytest.skip("Discovery JSON not found")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, dict), "Discovery JSON root is not a dict"
        except json.JSONDecodeError as e:
            pytest.fail(f"Discovery JSON is not valid JSON: {e}")
        except UnicodeDecodeError as e:
            pytest.fail(f"Discovery JSON contains invalid UTF-8: {e}")
    
    def test_discovery_json_has_agents(self):
        """Test that discovery JSON contains agent data."""
        json_path = (Path(__file__).parent.parent / "reports" / ".dashboard_cache.json").resolve()
        if not json_path.exists():
            pytest.skip("Discovery JSON not found")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check for agent entries (keys should be file paths)
        assert len(data) > 0, (
            "Discovery JSON is empty - no agents found\n"
            "Discovery pipeline failed to find any agents."
        )
        
        # Validate structure of first entry
        first_key = next(iter(data))
        first_entry = data[first_key]
        assert isinstance(first_entry, dict), "Agent entry is not a dict"
    
    def test_discovery_json_freshness(self):
        """Test that discovery JSON is reasonably fresh."""
        import time
        
        json_path = (Path(__file__).parent.parent / "reports" / ".dashboard_cache.json").resolve()
        if not json_path.exists():
            pytest.skip("Discovery JSON not found")
        
        mtime = json_path.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        
        # Warn if JSON is more than 24 hours old
        if age_hours > 24:
            pytest.skip(
                f"Discovery JSON is {age_hours:.1f} hours old\n"
                f"Consider regenerating for fresh data."
            )


class TestTemplatePlaceholders:
    """Test template placeholder handling."""
    
    def test_template_file_exists(self):
        """Test that dashboard template exists."""
        template_path = Path(__file__).parent.parent / "agentic_core" / "config" / "validators" / "dashboard_template.html"
        assert template_path.exists(), (
            f"Dashboard template not found at {template_path}\n"
            f"Template file is missing."
        )
    
    def test_template_has_required_placeholders(self):
        """Test that template contains all required placeholders."""
        template_path = Path(__file__).parent.parent / "agentic_core" / "config" / "validators" / "dashboard_template.html"
        if not template_path.exists():
            pytest.skip("Template not found")
        
        template = template_path.read_text(encoding='utf-8')
        
        required_placeholders = [
            'const dashboardData = [];',
            'const recommendationsData = [];',
            'const lastUpdatedStr = "";',
            'const gaugeData = {};',
            '<!-- STRATEGIC_REVIEW_INSERT -->',
            '<!-- TOP_RECS_INSERT -->',
        ]
        
        missing = [p for p in required_placeholders if p not in template]
        assert not missing, (
            f"Template missing required placeholders: {missing}\n"
            f"Template must contain all placeholders for data injection."
        )
    
    def test_template_has_chart_containers(self):
        """Test that template has all chart container divs."""
        template_path = Path(__file__).parent.parent / "agentic_core" / "config" / "validators" / "dashboard_template.html"
        if not template_path.exists():
            pytest.skip("Template not found")
        
        template = template_path.read_text(encoding='utf-8')
        
        required_containers = [
            'id="kpiGrid"',
            'id="riskMatrix"',
        ]
        
        missing = [c for c in required_containers if c not in template]
        assert not missing, (
            f"Template missing required chart containers: {missing}\n"
            f"Charts will fail to render without these containers."
        )


class TestAtomicWriteOperations:
    """Test atomic write operations for dashboard generation."""
    
    def test_dashboard_write_creates_file(self):
        """Test that dashboard write actually creates the file."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        assert dashboard_path.exists(), (
            "Dashboard file was not created\n"
            "Atomic write operation failed."
        )
    
    def test_dashboard_write_complete(self):
        """Test that dashboard write completed (no truncation)."""
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        
        # Check for closing tags
        assert '</body>' in html, "Dashboard HTML missing </body> - file may be truncated"
        assert '</html>' in html, "Dashboard HTML missing </html> - file may be truncated"
    
    def test_no_temp_files_left_behind(self):
        """Test that no temporary files are left behind after generation."""
        reports_dir = Path(__file__).parent.parent / "reports"
        if not reports_dir.exists():
            pytest.skip("Reports directory not found")
        
        temp_files = list(reports_dir.glob("*.tmp"))
        assert not temp_files, (
            f"Temporary files left behind: {temp_files}\n"
            f"Atomic write cleanup failed."
        )


class TestDataPipelineIntegrity:
    """Test overall data pipeline integrity."""
    
    def test_discovery_to_dashboard_data_flow(self):
        """Test that data flows from discovery JSON to dashboard HTML."""
        json_path = (Path(__file__).parent.parent / "reports" / ".dashboard_cache.json").resolve()
        dashboard_path = (Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html").resolve()
        
        if not json_path.exists():
            pytest.skip("Discovery JSON not found")
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        # Load discovery data
        with open(json_path, 'r', encoding='utf-8') as f:
            discovery_data = json.load(f)
        
        discovery_agent_count = len(discovery_data)
        
        # Load dashboard data
        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData"
        
        dashboard_data = json.loads(match.group(1))
        total_row = next((r for r in dashboard_data if r.get('Territory') == 'TOTAL'), None)
        
        assert total_row, "TOTAL row not found"
        dashboard_agent_count = int(total_row.get('Total', 0))
        
        # Agent counts should be close (within 10% tolerance for classification differences)
        tolerance = max(10, discovery_agent_count * 0.1)
        assert abs(discovery_agent_count - dashboard_agent_count) <= tolerance, (
            f"Agent count mismatch between discovery and dashboard!\n"
            f"  Discovery JSON: {discovery_agent_count} agents\n"
            f"  Dashboard TOTAL: {dashboard_agent_count} agents\n"
            f"  Difference: {abs(discovery_agent_count - dashboard_agent_count)}\n"
            f"Data pipeline integrity compromised."
        )
    
    def test_dashboard_generation_timestamp_recent(self):
        """Test that dashboard was generated recently (not stale)."""
        import time
        
        dashboard_path = Path(__file__).parent.parent / "reports" / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            pytest.skip("Dashboard not generated")
        
        mtime = dashboard_path.stat().st_mtime
        age_minutes = (time.time() - mtime) / 60
        
        # Dashboard should be less than 1 hour old for these tests
        assert age_minutes < 60, (
            f"Dashboard is {age_minutes:.1f} minutes old\n"
            f"Regenerate dashboard for accurate testing."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
