#!/usr/bin/env python3
"""
E2E Dashboard Generation Test - MANDATORY DATA INJECTION VALIDATION

This test ensures that dashboard generation and data injection are atomic.
If any injection fails, the entire generation must fail.
"""
import sys
import re
import json
from pathlib import Path

# SSOT: Import canonical definitions for dashboard testing
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.dashboard_ssot_definitions import (
    COL_HEAL_CAP, COL_INVOCATION, COL_TEST, COL_HARDENED,
    COL_COMPLEXITY_HEALTH, COL_TYPED, COL_DOCUMENTED, COL_SCHEMA,
    COL_CANONICAL_INHERITANCE, COL_CODE_QUALITY, COL_HEALTH
)

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
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

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_dashboard_generation():
    """Test dashboard generation end-to-end with mandatory injection validation."""
    print("=" * 80)
    print("E2E DASHBOARD GENERATION TEST - MANDATORY DATA INJECTION")
    print("=" * 80)
    
    try:
        from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent
        
        agent = AutonomyGuardianAgent(project_root)
        print("✓ AutonomyGuardianAgent initialized")
        
        # Generate dashboard - this MUST inject data or fail
        try:
            agent.generate_compliance_report(markdown=False)
            print("✓ Dashboard generation completed")
        except RuntimeError as e:
            if "DATA INJECTION INCOMPLETE" in str(e):
                print(f"✓ Dashboard generation correctly failed with injection error:\n{e}")
                return False
            raise
        
        # Verify dashboard file exists
        dashboard_path = project_root / REPORTS_DIR / "autonomy_dashboard.html"
        if not dashboard_path.exists():
            print("✗ CRITICAL: Dashboard file not found after generation")
            return False
        
        print(f"✓ Dashboard file exists: {dashboard_path}")
        
        # Read dashboard content
        content = dashboard_path.read_text(encoding='utf-8')
        
        # MANDATORY CHECKS - These must all pass or generation should have failed
        failures = []
        
        # Check 1: Dashboard data injection
        if 'const dashboardData = [];' in content:
            failures.append("dashboardData placeholder not replaced (empty array still present)")
        elif 'const dashboardData = [' not in content:
            failures.append("dashboardData variable not found in output")
        else:
            # Verify data is actually present (not just empty)
            match = re.search(r'const dashboardData = \[(.*?)\];', content, re.DOTALL)
            if match:
                data_str = f"[{match.group(1).strip()}]"
                try:
                    parsed_data = json.loads(data_str)
                    if not parsed_data:
                        failures.append("dashboardData injected but contains an empty list")
                except json.JSONDecodeError:
                    failures.append("dashboardData injected but contains invalid JSON")
            else:
                print("✓ Dashboard data injected with content")
        
        # Check 2: Recommendations data injection
        if 'const recommendationsData = [];' in content:
            failures.append("recommendationsData placeholder not replaced")
        elif 'const recommendationsData = [' not in content:
            failures.append("recommendationsData variable not found")
        else:
            print("✓ Recommendations data injected")
        
        # Check 3: Last updated timestamp
        if 'const lastUpdatedStr = "";' in content:
            failures.append("lastUpdatedStr placeholder not replaced")
        elif 'const lastUpdatedStr = "Last updated:' not in content:
            failures.append("lastUpdatedStr not properly formatted")
        else:
            print("✓ Last updated timestamp injected")
        
        # Check 4: Gauge data injection
        if 'const gaugeData = {};' in content:
            failures.append("gaugeData placeholder not replaced (empty object still present)")
        elif 'const gaugeData = {' not in content:
            failures.append("gaugeData variable not found")
        else:
            # Hardening: Verify gaugeData has required keys for UI rendering
            match = re.search(r'const gaugeData = (\{.*?\});', content, re.DOTALL)
            if match:
                try:
                    g_data = json.loads(match.group(1))
                    if "overallHealth" not in g_data:
                        failures.append("gaugeData missing 'overallHealth' key")
                except json.JSONDecodeError:
                    failures.append("gaugeData contains invalid JSON")
        
        # Check 5: Strategic review injection
        if '<!-- STRATEGIC_REVIEW_INSERT -->' in content:
            failures.append("Strategic review placeholder not replaced")
        else:
            print("✓ Strategic review placeholder replaced")
        
        # Check 6: Top recommendations injection
        if '<!-- TOP_RECS_INSERT -->' in content:
            failures.append("Top recommendations placeholder not replaced")
        else:
            print("✓ Top recommendations placeholder replaced")
        
        # Check 6.1: Strategic Observations injection (Phase 5 Requirement)
        if 'const strategicObservationsData = {};' in content:
            failures.append("strategicObservationsData placeholder not replaced")
        
        # Check 7: Verify actual data content
        if '"Territory"' not in content:
            failures.append("Dashboard data missing Territory field - data may be malformed")
        else:
            print("✓ Dashboard data contains expected fields")
        
        # Check 8: Verify risk matrix data source consistency
        territory_count = content.count('"Territory":')
        if territory_count < 5:
            failures.append(f"Only {territory_count} territories found - data may be incomplete")
        else:
            print(f"✓ Found {territory_count} territories in dashboard data")
        
        # FAIL HARD if any checks failed
        if failures:
            print("\n" + "=" * 80)
            print("❌ DASHBOARD GENERATION VALIDATION FAILED")
            print("=" * 80)
            for failure in failures:
                print(f"  ✗ {failure}")
            print("\nThis should not happen - generation should have failed earlier.")
            print("Check AutonomyGuardianAgent._generate_self_contained_dashboard()")
            return False
        
        print("\n" + "=" * 80)
        print("✅ ALL MANDATORY INJECTION CHECKS PASSED")
        print("=" * 80)
        print("Dashboard generation and data injection are atomic.")
        print("All required data has been injected successfully.")
        return True
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard_generation()
    sys.exit(0 if success else 1)
