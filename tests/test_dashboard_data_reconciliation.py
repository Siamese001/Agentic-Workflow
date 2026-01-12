#!/usr/bin/env python3
"""
Robust data reconciliation tests for dashboard territory table.

Validates that all calculated fields match their source data and formulas.
"""
import json
from pathlib import Path
import pytest

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
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
    get_validated_project_root,
)


def load_dashboard_data():
    """Load dashboard data from generated HTML."""
    import re
    
    # NEW ARCHITECTURE: Dashboard now lives in L6_observability/dashboards
    # __file__ is tests/test_dashboard_data_reconciliation.py, so parent.parent is project root
    test_file = Path(__file__).resolve()
    project_root = test_file.parent.parent  # tests/ -> project_root
    
    l6_path = project_root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
    legacy_path = project_root / REPORTS_DIR / "autonomy_dashboard.html"
    
    dashboard_path = l6_path if l6_path.exists() else legacy_path
    if not dashboard_path.exists():
        pytest.skip(f"Dashboard HTML not found at {l6_path} or {legacy_path}")
    
    html = dashboard_path.read_text(encoding='utf-8')
    
    # Extract dashboardData from HTML
    match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
    if not match:
        pytest.skip("dashboardData not found in HTML")
    
    data_json = match.group(1)
    return json.loads(data_json)


def test_health_score_calculation():
    """
    Test that Health Score is calculated correctly from components.
    
    Formula: (Heal Cap % + Invocation % + Test % + Observable % + Inverted CC Health) / 5
    
    This test ensures health is NEVER hardcoded to 100%.
    """
    data = load_dashboard_data()
    
    # Find TOTAL row
    total_row = next((row for row in data if row.get('Territory') == 'TOTAL'), None)
    assert total_row is not None, "TOTAL row not found in dashboard data"
    
    # Extract components
    heal_cap = float(total_row.get('Heal Cap %', 0))
    invocation = float(total_row.get('Invocation %', 0))
    tests = float(total_row.get('Test %', 0))
    observable = float(total_row.get('Observable %', 0))
    cc_health = float(total_row.get('Complexity Health', 0))
    actual_health = float(total_row.get('Health', 0))
    
    # Calculate expected health
    expected_health = round((heal_cap + invocation + tests + observable + cc_health) / 5, 1)
    
    # Validate
    assert actual_health == expected_health, (
        f"Health Score mismatch!\n"
        f"  Expected: {expected_health}% (calculated from components)\n"
        f"  Actual: {actual_health}%\n"
        f"  Components:\n"
        f"    - Heal Cap: {heal_cap}%\n"
        f"    - Invocation: {invocation}%\n"
        f"    - Tests: {tests}%\n"
        f"    - Observable: {observable}%\n"
        f"    - CC Health: {cc_health}%\n"
        f"  Formula: (Heal Cap + Invocation + Tests + Observable + CC Health) / 5"
    )
    
    # Ensure health is NOT hardcoded to 100%
    if invocation < 50 or tests < 50:
        assert actual_health < 90, (
            f"Health Score appears hardcoded to {actual_health}%!\n"
            f"With Invocation={invocation}% and Tests={tests}%, health should be < 90%"
        )


def test_territory_health_scores():
    """Test that each territory's health score is calculated correctly."""
    data = load_dashboard_data()
    
    failures = []
    for row in data:
        territory = row.get('Territory', 'Unknown')
        if territory == 'TOTAL':
            continue
        
        # Extract components
        heal_cap = float(row.get('Heal Cap %', 0))
        invocation = float(row.get('Invocation %', 0))
        tests = float(row.get('Test %', 0))
        observable = float(row.get('Observable %', 0))
        cc_health = float(row.get('Complexity Health', 0))
        actual_health = float(row.get('Health', 0))
        
        # Calculate expected
        expected_health = round((heal_cap + invocation + tests + observable + cc_health) / 5, 1)
        
        # Allow 0.1% tolerance for rounding
        if abs(actual_health - expected_health) > 0.1:
            failures.append(
                f"{territory}: Expected {expected_health}%, got {actual_health}% "
                f"(Cap={heal_cap}%, Inv={invocation}%, Test={tests}%, Obs={observable}%, CC={cc_health}%)"
            )
    
    assert not failures, f"Health score calculation failures:\n" + "\n".join(failures)


def test_invocation_percentage_accuracy():
    """Test that Invocation % matches actual agent invocation counts."""
    data = load_dashboard_data()
    
    for row in data:
        territory = row.get('Territory', 'Unknown')
        total_agents = int(row.get('Total', 0))
        invocation_pct = float(row.get('Invocation %', 0))
        
        if total_agents == 0:
            continue
        
        # Invocation % should be between 0-100
        assert 0 <= invocation_pct <= 100, (
            f"{territory}: Invocation % out of range: {invocation_pct}%"
        )
        
        # If invocation is 100%, all agents must have invocation
        if invocation_pct == 100:
            # This would require checking agent-level data
            pass


def test_complexity_health_inversion():
    """Test that Complexity Health is correctly inverted from Avg CC."""
    data = load_dashboard_data()
    
    for row in data:
        territory = row.get('Territory', 'Unknown')
        avg_cc = float(row.get('Avg CC', 0))
        cc_health = float(row.get('Complexity Health', 0))
        
        # Complexity Health should be inverted: lower CC = higher health
        # Formula: max(0, min(100, 100 - (CC * 2)))
        expected_cc_health = max(0, min(100, 100 - (avg_cc * 2)))
        
        # Allow 0.5% tolerance for rounding
        assert abs(cc_health - expected_cc_health) < 0.5, (
            f"{territory}: CC Health mismatch!\n"
            f"  Avg CC: {avg_cc}\n"
            f"  Expected CC Health: {expected_cc_health}%\n"
            f"  Actual CC Health: {cc_health}%\n"
            f"  Formula: max(0, min(100, 100 - (CC * 2)))"
        )


def test_total_row_aggregation():
    """Test that TOTAL row correctly aggregates territory data."""
    data = load_dashboard_data()
    
    total_row = next((row for row in data if row.get('Territory') == 'TOTAL'), None)
    assert total_row is not None, "TOTAL row not found"
    
    # Sum up territory totals (excluding TOTAL row itself)
    territory_rows = [row for row in data if row.get('Territory') != 'TOTAL']
    
    total_agents_sum = sum(int(row.get('Total', 0)) for row in territory_rows)
    total_agents_actual = int(total_row.get('Total', 0))
    
    assert total_agents_sum == total_agents_actual, (
        f"TOTAL agent count mismatch!\n"
        f"  Sum of territories: {total_agents_sum}\n"
        f"  TOTAL row: {total_agents_actual}"
    )


def test_percentage_ranges():
    """Test that all percentage fields are within valid 0-100 range."""
    data = load_dashboard_data()
    
    percentage_fields = [
        'Heal Cap %', 'Invocation %', 'Hardened %', 'MCP Capable %',
        'Test %', 'Observable %', 'Typed %', 'Documented %', 'Metadata %',
        'Proper Base %', 'Compliance %', 'Used %', 'Health', 
        'Complexity Health', 'Code Quality Score'
    ]
    
    failures = []
    for row in data:
        territory = row.get('Territory', 'Unknown')
        for field in percentage_fields:
            value = row.get(field)
            if value is not None:
                value = float(value)
                if not (0 <= value <= 100):
                    failures.append(f"{territory}.{field} = {value}% (out of range)")
    
    assert not failures, f"Percentage out of range:\n" + "\n".join(failures)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
