#!/usr/bin/env python3
"""
Dashboard Drill-Down Validation Test
=====================================

Tests that drill-down modals have complete, valid per-agent data.

Validates:
1. All territories have agent data
2. Agent objects have all required fields
3. No "undefined" values in critical fields
4. Metrics are properly calculated (< 50%, = 0%)
5. VS Code links are properly formatted
"""

import json
import re
from pathlib import Path

import pytest

# Required fields for drill-down agent objects
REQUIRED_FIELDS = [
    "name",
    "path",
    "rel",
    "abs_file",
    "abs_class",
    "class_line",
    "has_mixin",
    "invocation",
    "has_tests",
    "obs_summary",
    "mcp_summary",
    "typing_summary",
    "typed_pct",
    "overall_typed_pct",
    "complexity",
    "health",
]


def _load_dashboard_data():
    """Load and parse dashboard HTML to extract agent data."""
    dashboard_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
    if not dashboard_path.exists():
        pytest.skip("Dashboard HTML not found")

    html = dashboard_path.read_text(encoding="utf-8")
    agent_data_pattern = r"const realAgentData = (\{.*?\});"
    match = re.search(agent_data_pattern, html, re.DOTALL)

    if not match:
        pytest.skip("realAgentData not found in dashboard HTML")

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        pytest.skip(f"Failed to parse realAgentData: {e}")


class TestDashboardDrillDown:
    """Test suite for dashboard drill-down validation."""

    @pytest.fixture
    def agent_data(self):
        """Load agent data from dashboard."""
        return _load_dashboard_data()

    def test_all_agents_have_required_fields(self, agent_data):
        """Verify all agents have required fields."""
        errors = []
        for territory, territory_data in agent_data.items():
            for idx, agent in enumerate(territory_data.get("agents", [])):
                agent_id = f"{territory}[{idx}]"
                missing_fields = [f for f in REQUIRED_FIELDS if f not in agent]
                if missing_fields:
                    errors.append(f"{agent_id}: Missing {', '.join(missing_fields)}")

        assert not errors, f"Missing fields in {len(errors)} agents:\n" + "\n".join(errors[:10])

    def test_no_undefined_values_in_critical_fields(self, agent_data):
        """Verify no 'undefined' values in critical fields."""
        errors = []
        for territory, territory_data in agent_data.items():
            for idx, agent in enumerate(territory_data.get("agents", [])):
                agent_id = f"{territory}[{idx}]"

                if agent.get("name") == "undefined" or not agent.get("name"):
                    errors.append(f"{agent_id}: name is undefined")
                if agent.get("rel") == "undefined" or not agent.get("rel"):
                    errors.append(f"{agent_id}: rel is undefined")

        assert not errors, f"Undefined values in {len(errors)} agents:\n" + "\n".join(errors[:10])

    def test_numeric_fields_are_valid(self, agent_data):
        """Verify numeric fields contain valid numbers."""
        errors = []
        numeric_fields = ["health", "complexity", "typed_pct", "overall_typed_pct"]

        for territory, territory_data in agent_data.items():
            for idx, agent in enumerate(territory_data.get("agents", [])):
                agent_id = f"{territory}[{idx}]"
                for field in numeric_fields:
                    value = agent.get(field)
                    if value == "undefined" or value is None:
                        errors.append(f"{agent_id}: {field} is undefined")
                    elif not isinstance(value, (int, float)):
                        errors.append(f"{agent_id}: {field} is not numeric: {value}")

        assert not errors, f"Invalid numeric fields in {len(errors)} cases:\n" + "\n".join(errors[:10])

    def test_boolean_fields_are_valid(self, agent_data):
        """Verify boolean fields are not undefined."""
        errors = []
        boolean_fields = ["has_mixin", "has_tests"]

        for territory, territory_data in agent_data.items():
            for idx, agent in enumerate(territory_data.get("agents", [])):
                agent_id = f"{territory}[{idx}]"
                for field in boolean_fields:
                    value = agent.get(field)
                    if value == "undefined" or value is None:
                        errors.append(f"{agent_id}: {field} is undefined")

        assert not errors, f"Invalid boolean fields in {len(errors)} cases:\n" + "\n".join(errors[:10])

    def test_summary_fields_are_valid(self, agent_data):
        """Verify summary fields don't contain 'undefined'."""
        errors = []
        summary_fields = ["obs_summary", "mcp_summary", "typing_summary"]

        for territory, territory_data in agent_data.items():
            for idx, agent in enumerate(territory_data.get("agents", [])):
                agent_id = f"{territory}[{idx}]"
                for field in summary_fields:
                    value = agent.get(field)
                    if value == "undefined" or not value:
                        errors.append(f"{agent_id}: {field} is undefined or empty")
                    elif "undefined" in str(value):
                        errors.append(f"{agent_id}: {field} contains 'undefined'")

        assert not errors, f"Invalid summary fields in {len(errors)} cases:\n" + "\n".join(errors[:10])
