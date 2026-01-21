#!/usr/bin/env python3
"""
Test suite for Code Quality table in dashboard.

Validates that the code quality table is present, correctly populated,
and displays accurate metrics by territory.
"""
import json
import re
from pathlib import Path
import pytest

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    REPORTS_DIR,
    get_validated_project_root,
)

# Disable path_shield for real file I/O testing
pytestmark = pytest.mark.usefixtures("disable_path_shield")

# Module-level constants
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# NEW ARCHITECTURE: Dashboard now lives in L6_observability/dashboards
L6_DASHBOARD_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
LEGACY_DASHBOARD_PATH = PROJECT_ROOT / REPORTS_DIR / "autonomy_dashboard.html"

# Use L6 path if available, otherwise fall back to legacy
DASHBOARD_PATH = L6_DASHBOARD_PATH if L6_DASHBOARD_PATH.exists() else LEGACY_DASHBOARD_PATH


class TestCodeQualityTable:
    """Test Code Quality table rendering and data accuracy."""

    def test_code_quality_grid_container_exists(self):
        """Test that codeQualityGrid container div exists in template."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        assert 'id="codeQualityGrid"' in html, (
            "codeQualityGrid container div not found in dashboard HTML"
        )

    def test_code_quality_table_rendered(self):
        """Test that Code Quality table is rendered with content."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')

        # Check for table title
        assert 'Code Quality by Territory' in html, (
            "Code Quality table title not found"
        )

        # Check for renderCodeQualityTable function
        assert 'function renderCodeQualityTable' in html, (
            "renderCodeQualityTable function not found in dashboard"
        )

        # Check for renderCodeQualityTable call
        assert 'renderCodeQualityTable(territoryData)' in html, (
            "renderCodeQualityTable() not called in render pipeline"
        )

    def test_code_quality_table_headers(self):
        """Test that Code Quality table has correct column headers."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')

        required_headers = [
            'Territory',
            '# Agents',
            'Typed %',
            'Documented %',
            'Complexity Health %',
            'Proper Base %',
            'Code Quality Score'
        ]

        missing_headers = [h for h in required_headers if h not in html]
        assert not missing_headers, (
            f"Code Quality table missing headers: {missing_headers}"
        )

    def test_code_quality_data_present(self):
        """Test that dashboard data includes code quality fields."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')

        # Extract dashboardData
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData from HTML"

        data = json.loads(match.group(1))
        total_row = next((r for r in data if r.get('Territory') == 'TOTAL'), None)

        assert total_row is not None, "TOTAL row not found"

        # Check for code quality fields
        required_fields = [
            'Code Quality Score',
            'Typed %',
            'Documented %',
            'Complexity Health',
            'Proper Base %'
        ]

        missing_fields = [f for f in required_fields if f not in total_row]
        assert not missing_fields, (
            f"TOTAL row missing code quality fields: {missing_fields}"
        )

    def test_code_quality_score_calculation(self):
        """Test that Code Quality Score is within valid range."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData"

        data = json.loads(match.group(1))

        failures = []
        for row in data:
            territory = row.get('Territory', 'Unknown')
            code_quality = float(row.get('Code Quality Score', 0))

            # Code Quality Score should be 0-100
            if not (0 <= code_quality <= 100):
                failures.append(
                    f"{territory}: Code Quality Score {code_quality}% out of range"
                )

        assert not failures, (
            f"Code Quality Score validation failures:\n" + "\n".join(failures)
        )

    def test_code_quality_components_valid(self):
        """Test that all code quality components are valid percentages."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData"

        data = json.loads(match.group(1))

        component_fields = ['Typed %', 'Documented %', 'Complexity Health', 'Proper Base %']
        failures = []

        for row in data:
            territory = row.get('Territory', 'Unknown')
            for field in component_fields:
                value = float(row.get(field, 0))
                if not (0 <= value <= 100):
                    failures.append(
                        f"{territory}.{field} = {value}% (out of range)"
                    )

        assert not failures, (
            f"Code quality component validation failures:\n" + "\n".join(failures)
        )

    def test_code_quality_table_has_total_row(self):
        """Test that Code Quality table includes TOTAL row."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')
        match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        assert match, "Could not extract dashboardData"

        data = json.loads(match.group(1))
        total_row = next((r for r in data if r.get('Territory') == 'TOTAL'), None)

        assert total_row is not None, "TOTAL row not found for Code Quality table"

        # Verify TOTAL row has code quality score
        code_quality = float(total_row.get('Code Quality Score', -1))
        assert code_quality >= 0, (
            f"TOTAL row has invalid Code Quality Score: {code_quality}"
        )

    def test_code_quality_metrics_key_present(self):
        """Test that Code Quality metrics explanations are present."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')

        # Check for key metric explanations (new architecture uses inline explanations)
        key_terms = [
            'Typed %',
            'Documented %',
            'Complexity Health',
            'Proper Base %',
            'Code Quality'
        ]

        found_terms = [term for term in key_terms if term in html]
        assert len(found_terms) >= 3, (
            f"Code Quality metrics not found in dashboard. Found: {found_terms}"
        )

    def test_code_quality_table_position(self):
        """Test that Code Quality table appears after Territory Summary table."""
        if not DASHBOARD_PATH.exists():
            pytest.skip("Dashboard not generated")

        html = DASHBOARD_PATH.read_text(encoding='utf-8')

        # Find positions of both tables
        territory_pos = html.find('Territory Summary')
        code_quality_pos = html.find('Code Quality by Territory')

        assert territory_pos != -1, "Territory Summary table not found"
        assert code_quality_pos != -1, "Code Quality table not found"
        assert code_quality_pos > territory_pos, (
            "Code Quality table should appear AFTER Territory Summary table"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
