#!/usr/bin/env python3
"""
MANDATORY END-TO-END DASHBOARD TEST
Must be run after ANY data change to agent_discovery_full.json or dashboard HTML.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.config.blueprint_sovereign.structure_blueprint import DASHBOARD_DIR, get_validated_project_root

def test_agent_discovery_integrity() -> Tuple[bool, List[str]]:
    """Test 1: Verify agent_discovery_full.json integrity."""
    errors = []
    project_root = get_validated_project_root()
    discovery_path = project_root / 'agent_discovery_full.json'
    
    if not discovery_path.exists():
        errors.append("❌ agent_discovery_full.json not found")
        return False, errors
    
    try:
        with open(discovery_path, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        if not isinstance(agents, list):
            errors.append("❌ agent_discovery_full.json is not a list")
            return False, errors
        
        if len(agents) == 0:
            errors.append("❌ agent_discovery_full.json is empty")
            return False, errors
        
        # Check required fields
        required_fields = ['path', 'class_name', 'layer', 'has_healing']
        for i, agent in enumerate(agents[:5]):  # Check first 5
            for field in required_fields:
                if field not in agent:
                    errors.append(f"❌ Agent {i} missing required field: {field}")
                    return False, errors
        
        print(f"✅ Test 1 PASSED: agent_discovery_full.json has {len(agents)} agents")
        return True, []
        
    except Exception as e:
        errors.append(f"❌ Failed to load agent_discovery_full.json: {e}")
        return False, errors

def test_dashboard_html_exists() -> Tuple[bool, List[str]]:
    """Test 2: Verify dashboard HTML exists and is valid."""
    errors = []
    project_root = get_validated_project_root()
    dashboard_path = project_root / DASHBOARD_DIR / 'autonomy_dashboard.html'
    
    if not dashboard_path.exists():
        errors.append("❌ autonomy_dashboard.html not found")
        return False, errors
    
    try:
        html = dashboard_path.read_text(encoding='utf-8')
        
        if len(html) < 1000:
            errors.append("❌ Dashboard HTML is suspiciously small")
            return False, errors
        
        if 'dashboardData' not in html:
            errors.append("❌ Dashboard HTML missing dashboardData variable")
            return False, errors
        
        print(f"✅ Test 2 PASSED: Dashboard HTML exists ({len(html)} bytes)")
        return True, []
        
    except Exception as e:
        errors.append(f"❌ Failed to read dashboard HTML: {e}")
        return False, errors

def test_dashboard_data_structure() -> Tuple[bool, List[str]]:
    """Test 3: Verify dashboardData JSON structure in HTML."""
    errors = []
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    
    try:
        html = dashboard_path.read_text(encoding='utf-8')
        
        # Extract dashboardData JSON
        start_marker = 'const dashboardData = ['
        end_marker = '];'
        start_idx = html.find(start_marker)
        end_idx = html.find(end_marker, start_idx) + len(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            errors.append("❌ Could not find dashboardData in HTML")
            return False, errors
        
        json_str = html[start_idx+len(start_marker)-1:end_idx-1]
        territories = json.loads(json_str)
        
        if not isinstance(territories, list):
            errors.append("❌ dashboardData is not a list")
            return False, errors
        
        if len(territories) == 0:
            errors.append("❌ dashboardData is empty")
            return False, errors
        
        # Check for TOTAL row
        total_row = next((t for t in territories if t.get('Territory') == 'TOTAL'), None)
        if not total_row:
            errors.append("❌ dashboardData missing TOTAL row")
            return False, errors
        
        print(f"✅ Test 3 PASSED: dashboardData has {len(territories)} rows including TOTAL")
        return True, []
        
    except json.JSONDecodeError as e:
        errors.append(f"❌ dashboardData JSON is invalid: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"❌ Failed to parse dashboardData: {e}")
        return False, errors

def test_dashboard_required_fields() -> Tuple[bool, List[str]]:
    """Test 4: Verify all required fields exist in dashboardData."""
    errors = []
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    
    required_fields = [
        'Territory', 'Total', 'Compliant', 'Heal Cap %', 'Heal Invocation %',
        'Invocation %', 'Test %', 'Observable %', 'Avg CC', 'Typed %',
        'Documented %', 'Health', 'Risk', 'Hardened %', 'Complexity Health'
    ]
    
    try:
        html = dashboard_path.read_text(encoding='utf-8')
        start_marker = 'const dashboardData = ['
        end_marker = '];'
        start_idx = html.find(start_marker)
        end_idx = html.find(end_marker, start_idx) + len(end_marker)
        json_str = html[start_idx+len(start_marker)-1:end_idx-1]
        territories = json.loads(json_str)
        
        # Check TOTAL row has all fields
        total_row = next((t for t in territories if t.get('Territory') == 'TOTAL'), None)
        if total_row:
            missing_fields = [f for f in required_fields if f not in total_row]
            if missing_fields:
                errors.append(f"❌ TOTAL row missing fields: {', '.join(missing_fields)}")
                return False, errors
        
        # Check at least one territory row has all fields
        territory_rows = [t for t in territories if t.get('Territory') != 'TOTAL']
        if territory_rows:
            sample_row = territory_rows[0]
            missing_fields = [f for f in required_fields if f not in sample_row]
            if missing_fields:
                errors.append(f"❌ Territory rows missing fields: {', '.join(missing_fields)}")
                return False, errors
        
        print(f"✅ Test 4 PASSED: All required fields present in dashboardData")
        return True, []
        
    except Exception as e:
        errors.append(f"❌ Failed to verify required fields: {e}")
        return False, errors

def test_data_consistency() -> Tuple[bool, List[str]]:
    """Test 5: Verify dashboard data matches agent_discovery_full.json."""
    errors = []
    
    try:
        # Load agent discovery
        with open('C:/Git/Agentic-Workflow/agent_discovery_full.json', 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        # Load dashboard data
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html = dashboard_path.read_text(encoding='utf-8')
        start_marker = 'const dashboardData = ['
        end_marker = '];'
        start_idx = html.find(start_marker)
        end_idx = html.find(end_marker, start_idx) + len(end_marker)
        json_str = html[start_idx+len(start_marker)-1:end_idx-1]
        territories = json.loads(json_str)
        
        total_row = next((t for t in territories if t.get('Territory') == 'TOTAL'), None)
        
        # Check total agent count
        dashboard_total = total_row['Total']
        actual_total = len(agents)
        if dashboard_total != actual_total:
            errors.append(f"❌ Agent count mismatch: Dashboard={dashboard_total}, Actual={actual_total}")
            return False, errors
        
        # Check heal capability
        actual_healed = sum(1 for a in agents if a.get('has_healing'))
        actual_heal_pct = round(actual_healed / actual_total * 100, 1)
        dashboard_heal_pct = total_row['Heal Cap %']
        
        if abs(dashboard_heal_pct - actual_heal_pct) > 0.5:
            errors.append(f"❌ Heal Cap % mismatch: Dashboard={dashboard_heal_pct}%, Actual={actual_heal_pct}%")
            return False, errors
        
        print(f"✅ Test 5 PASSED: Dashboard data consistent with agent_discovery_full.json")
        print(f"   Total agents: {actual_total}")
        print(f"   Heal Cap %: {actual_heal_pct}%")
        return True, []
        
    except Exception as e:
        errors.append(f"❌ Failed to verify data consistency: {e}")
        return False, errors

def test_table_rendering_elements() -> Tuple[bool, List[str]]:
    """Test 6: Verify HTML has table rendering functions."""
    errors = []
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    
    required_functions = [
        'renderTerritorySummaryTable',
        'renderCodeQualityTable',
        'loadData'
    ]
    
    required_elements = [
        'id="kpiGrid"',
        'id="codeQualityGrid"'
    ]
    
    try:
        html = dashboard_path.read_text(encoding='utf-8')
        
        for func in required_functions:
            if f'function {func}' not in html:
                errors.append(f"❌ Missing function: {func}")
                return False, errors
        
        for elem in required_elements:
            if elem not in html:
                errors.append(f"❌ Missing HTML element: {elem}")
                return False, errors
        
        print(f"✅ Test 6 PASSED: All table rendering elements present")
        return True, []
        
    except Exception as e:
        errors.append(f"❌ Failed to verify table rendering elements: {e}")
        return False, errors

def run_all_tests() -> bool:
    """Run all dashboard tests and report results."""
    print("=" * 70)
    print("MANDATORY END-TO-END DASHBOARD TEST")
    print("=" * 70)
    print()
    
    tests = [
        ("Agent Discovery Integrity", test_agent_discovery_integrity),
        ("Dashboard HTML Exists", test_dashboard_html_exists),
        ("Dashboard Data Structure", test_dashboard_data_structure),
        ("Required Fields Present", test_dashboard_required_fields),
        ("Data Consistency", test_data_consistency),
        ("Table Rendering Elements", test_table_rendering_elements)
    ]
    
    all_passed = True
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n{'─' * 70}")
        print(f"Running: {test_name}")
        print(f"{'─' * 70}")
        passed, errors = test_func()
        
        if not passed:
            all_passed = False
            failed_tests.append(test_name)
            for error in errors:
                print(error)
    
    print()
    print("=" * 70)
    # Test 7: Drill-Down Agent Data Integrity
    print("\n" + "─" * 70)
    print("Running: Drill-Down Agent Data Integrity")
    print("─" * 70)
    
    # Extract realAgentData from HTML
    import re
    import json
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    html_content = dashboard_path.read_text(encoding='utf-8')
    agent_data_pattern = r'const realAgentData = (\{.*?\});'
    match = re.search(agent_data_pattern, html_content, re.DOTALL)
    
    errors = []
    if not match:
        errors.append("Test 7 FAILED: realAgentData not found in dashboard HTML")
    else:
        try:
            agent_data_json = match.group(1)
            real_agent_data = json.loads(agent_data_json)
            
            # Required fields for drill-down
            REQUIRED_AGENT_FIELDS = ['name', 'path', 'rel', 'abs_file', 'abs_class', 'class_line',
                                     'has_mixin', 'invocation', 'has_tests', 'obs_summary',
                                     'mcp_summary', 'typing_summary', 'health', 'complexity']
            
            territories_checked = 0
            agents_checked = 0
            undefined_found = False
            
            for territory, territory_data in real_agent_data.items():
                agents = territory_data.get('agents', [])
                if not agents:
                    continue
                
                territories_checked += 1
                for agent in agents:
                    agents_checked += 1
                    
                    # Check for missing fields
                    missing = [f for f in REQUIRED_AGENT_FIELDS if f not in agent]
                    if missing:
                        errors.append(f"Test 7 FAILED: Agent in {territory} missing fields: {missing}")
                        break
                    
                    # Check for "undefined" values
                    if agent.get('name') == 'undefined' or not agent.get('name'):
                        errors.append(f"Test 7 FAILED: Agent name is undefined in {territory}")
                        undefined_found = True
                        break
                    
                    if 'undefined' in json.dumps(agent):
                        errors.append(f"Test 7 FAILED: Agent {agent.get('name', 'unknown')} in {territory} contains 'undefined'")
                        undefined_found = True
                        break
                
                if undefined_found:
                    break
            
            if not undefined_found and agents_checked > 0:
                print(f"✅ Test 7 PASSED: All {agents_checked} agents in {territories_checked} territories have valid drill-down data")
                print(f"   No 'undefined' values found")
        
        except json.JSONDecodeError as e:
            errors.append(f"Test 7 FAILED: Could not parse realAgentData: {e}")
        except Exception as e:
            errors.append(f"Test 7 FAILED: Drill-down validation error: {e}")
    
    print("\n" + "=" * 70)
    if errors:
        print("❌ TESTS FAILED - Dashboard has issues")
        print("=" * 70)
        print("\n".join(errors))
        sys.exit(1)
    
    if all_passed:
        print("✅ ALL 7 TESTS PASSED - Dashboard is ready for deployment")
    else:
        print(f"❌ {len(failed_tests)} TEST(S) FAILED:")
        for test in failed_tests:
            print(f"   - {test}")
        print("\n⚠️  DO NOT DEPLOY until all tests pass!")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
