#!/usr/bin/env python3
"""
End-to-end dashboard validation tests.

Validates the complete dashboard generation pipeline from source data to HTML output.
"""

import json
import re
from pathlib import Path

import pytest


def test_dashboard_html_contains_correct_data():
    """Test that generated dashboard HTML contains correctly calculated data."""
    dashboard_path = Path("reports/autonomy_dashboard.html")
    if not dashboard_path.exists():
        pytest.skip("Dashboard HTML not found - generate dashboard first")

    html = dashboard_path.read_text(encoding="utf-8")

    # Extract dashboardData from HTML
    match = re.search(r"const dashboardData = (\[.*?\]);", html, re.DOTALL)
    assert match, "dashboardData not found in HTML"

    data_json = match.group(1)
    data = json.loads(data_json)

    # Find TOTAL row
    total_row = next((row for row in data if row.get("Territory") == "TOTAL"), None)
    assert total_row is not None, "TOTAL row not found in dashboard HTML"

    # Validate health score calculation
    heal_cap = float(total_row.get("Heal Cap %", 0))
    invocation = float(total_row.get("Invocation %", 0))
    tests = float(total_row.get("Test %", 0))
    observable = float(total_row.get("Observable %", 0))
    cc_health = float(total_row.get("Complexity Health", 0))
    actual_health = float(total_row.get("Health", 0))

    expected_health = round((heal_cap + invocation + tests + observable + cc_health) / 5, 1)

    assert abs(actual_health - expected_health) < 0.1, (
        f"Dashboard HTML contains incorrect health score!\n"
        f"  Expected: {expected_health}%\n"
        f"  Actual: {actual_health}%\n"
        f"  This indicates the health score is still hardcoded or miscalculated."
    )


def test_dashboard_strategic_recommendations_present():
    """Test that strategic recommendations are injected into HTML."""
    dashboard_path = Path("reports/autonomy_dashboard.html")
    if not dashboard_path.exists():
        pytest.skip("Dashboard HTML not found")

    html = dashboard_path.read_text(encoding="utf-8")

    # Check that placeholders are replaced
    assert "<!-- STRATEGIC_REVIEW_INSERT -->" not in html, "Strategic review placeholder not replaced"
    assert "<!-- TOP_RECS_INSERT -->" not in html, "Top recommendations placeholder not replaced"

    # Check that recommendations section exists
    assert "🎯 Strategic Recommendations" in html, "Strategic Recommendations section not found"


def test_dashboard_territory_table_rendered():
    """Test that territory table is properly rendered in HTML."""
    dashboard_path = Path("reports/autonomy_dashboard.html")
    if not dashboard_path.exists():
        pytest.skip("Dashboard HTML not found")

    html = dashboard_path.read_text(encoding="utf-8")

    # Check for territory table function
    assert "function renderTerritorySummaryTable" in html, "Territory table render function not found"

    # Check for kpiGrid container
    assert 'id="kpiGrid"' in html, "Territory table container not found"


def test_no_hardcoded_health_scores_in_code():
    """Test that source code doesn't contain hardcoded health = 100."""
    guardian_path = Path("agentic_core/L5_safety/validators/AutonomyGuardianAgent.py")
    if not guardian_path.exists():
        pytest.skip("AutonomyGuardianAgent.py not found")

    code = guardian_path.read_text(encoding="utf-8")

    # Search for hardcoded health = 100
    hardcoded_patterns = [
        r"health\s*=\s*100\.0\s*#.*inherit",
        r"health\s*=\s*100\s*#.*infrastructure",
        r"total_health\s*=\s*100\.0\s*#.*inherit",
    ]

    failures = []
    for pattern in hardcoded_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            failures.append(f"Line {line_num}: {match.group(0)}")

    assert not failures, (
        "Found hardcoded health = 100 in source code:\n"
        + "\n".join(failures)
        + "\n\nHealth score should be calculated from actual metrics, not hardcoded!"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
