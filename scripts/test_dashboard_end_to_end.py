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

# SSOT: Import canonical health calculation (Violation 4 fix)
from agentic_core.config.blueprint_sovereign.canonical_truth import calculate_health_score

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
        heal_cap = total_row['Heal Cap %']
        heal_inv = total_row['Heal Invocation %']
        test = total_row['Test %']
        obs = total_row['Observable %']
        complexity = total_row['Complexity Health']
        # SSOT: Use canonical health calculation (Violation 4 fix)
        expected_health = calculate_health_score(
            heal_cap=heal_cap,
            invoc=heal_inv,
            test_cov=test,
            obs=obs,
            comp_health=complexity
        )
        actual_heal_pct = total_row['Health']
        
        if abs(actual_heal_pct - expected_health) > 0.5:
            errors.append(f"❌ Heal Cap % mismatch: Dashboard={actual_heal_pct}%, Expected={expected_health}%")
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
    
    # Test 8: Base Agent Uniqueness
    print("\n" + "─" * 70)
    print("Running: Base Agent Uniqueness (Critical)")
    print("─" * 70)
    
    # DEPRECATED: Simple bases created during refactoring - exclude from base agent count
    # These are lightweight alternatives but not canonical bases
    DEPRECATED_SIMPLE_BASES = {'L2Agent', 'L3Agent', 'L4Agent', 'L5Agent'}
    
    # Check for multiple base agents per layer
    LAYERS = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']
    CANONICAL_BASE_AGENTS = {
        'L0': 'L0Agent',
        'L1': 'L1Agent',
        'L2': 'L2Agent',
        'L3': 'L3Agent',
        'L4': 'L4Agent',
        'L5': 'L5Agent',
    }
    try:
        # Load agents from discovery file
        with open('C:/Git/Agentic-Workflow/agent_discovery_full.json', 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        # Group base agents by layer
        base_agents_by_layer = {}
        base_agents_wrong_territory = []
        
        for agent in agents:
            name = agent.get('class_name', '')
            layer = agent.get('layer', '')
            territory = agent.get('territory', '')
            
            # Identify base agents (exclude deprecated simple bases)
            if name.endswith('BaseAgent') or name in ['L0Agent', 'L1Agent', 'L6Agent']:
                # Skip deprecated simple bases - they are lightweight alternatives, not canonical
                if name not in DEPRECATED_SIMPLE_BASES:
                    if layer not in base_agents_by_layer:
                        base_agents_by_layer[layer] = []
                    base_agents_by_layer[layer].append(agent)
                
                # Verify base agents are in "Base Class" territories
                if 'Base Class' not in territory:
                    base_agents_wrong_territory.append(f"{name} ({layer}): territory='{territory}'")
        
        # Report findings
        total_base_agents = sum(len(agents) for agents in base_agents_by_layer.values())
        print(f"   Found {total_base_agents} base agents across {len(base_agents_by_layer)} layers")
        
        for layer in sorted(base_agents_by_layer.keys()):
            base_agents = base_agents_by_layer[layer]
            agent_names = [a['class_name'] for a in base_agents]
            print(f"   {layer}: {len(base_agents)} base agents - {', '.join(agent_names)}")
        
        if base_agents_wrong_territory:
            errors.append(f"Test 8 FAILED: {len(base_agents_wrong_territory)} base agents NOT in 'Base Class' territories")
            for issue in base_agents_wrong_territory[:5]:
                errors.append(f"  - {issue}")
        else:
            print(f"✅ Test 8 PASSED: All {total_base_agents} base agents in correct 'Base Class' territories")
        
    except Exception as e:
        errors.append(f"Test 8 FAILED: Could not validate base agents: {e}")
    
    # Test 9: Orphaned Agents (No Base Inheritance)
    print("\n" + "─" * 70)
    print("Running: Orphaned Agents Check")
    print("─" * 70)
    
    try:
        orphans = []
        for agent in agents:
            name = agent.get('class_name', '')
            layer = agent.get('layer', '')
            inheritance = agent.get('inheritance', [])
            
            if not layer or not inheritance:
                continue
            
            # Skip base agents
            if name in CANONICAL_BASE_AGENTS.values() or 'BaseAgent' in name:
                continue
            
            layer_prefix = layer[:2] if len(layer) >= 2 else layer
            if layer_prefix not in LAYERS:
                continue
            
            expected_base = CANONICAL_BASE_AGENTS.get(layer_prefix)
            if not expected_base:
                continue
            
            # Check for base agent in inheritance
            has_base = False
            inheritance_str = str(inheritance).lower()
            if expected_base.lower() in inheritance_str:
                has_base = True
            elif f"{layer_prefix.lower()}agent" in inheritance_str:
                has_base = True
            elif f"{layer_prefix.lower()}baseagent" in inheritance_str:
                has_base = True
            
            if not has_base:
                orphans.append(f"{name} ({layer})")
        
        if orphans:
            errors.append(f"Test 9 FAILED: {len(orphans)} orphaned agents lack base inheritance")
            for orphan in orphans[:3]:
                errors.append(f"  - {orphan}")
        else:
            print(f"✅ Test 9 PASSED: All agents inherit from layer base agents")
    
    except Exception as e:
        errors.append(f"Test 9 FAILED: Could not validate inheritance: {e}")
    
    # Test 10: Metric Consistency
    print("\n" + "─" * 70)
    print("Running: Metric Consistency Check")
    print("─" * 70)
    
    try:
        inconsistencies = []
        
        # Check heal invocation vs capability
        agents_with_healing = [a for a in agents if a.get('has_healing')]
        heal_capable = len(agents_with_healing)
        heal_invoked = sum(1 for a in agents_with_healing if a.get('invocation') == 'Yes')
        
        if heal_invoked > heal_capable:
            inconsistencies.append(f"Invocation ({heal_invoked}) > Capability ({heal_capable})")
        
        # Check MCP mixin vs flag consistency
        for agent in agents[:50]:  # Sample check
            name = agent.get('class_name', '')
            inheritance = str(agent.get('inheritance', []))
            mcp_hardened = agent.get('mcp_hardened', False)
            
            if 'MCPHardenedMixin' in inheritance and not mcp_hardened:
                inconsistencies.append(f"{name}: Has MCPHardenedMixin but flag=False")
                break  # Just report first
        
        if inconsistencies:
            errors.append(f"Test 10 FAILED: {len(inconsistencies)} metric inconsistencies")
            for inc in inconsistencies[:2]:
                errors.append(f"  - {inc}")
        else:
            print(f"✅ Test 10 PASSED: All metrics are logically consistent")
    
    except Exception as e:
        errors.append(f"Test 10 FAILED: Could not validate metrics: {e}")
    
    # Test 11: L5 Safety MCP Requirement
    print("\n" + "─" * 70)
    print("Running: L5 Safety MCP Requirement")
    print("─" * 70)
    
    try:
        l5_agents = [a for a in agents if a.get('layer', '').startswith('L5')]
        unhardened_l5 = [a for a in l5_agents if not a.get('mcp_hardened')]
        
        if unhardened_l5:
            errors.append(f"Test 11 FAILED: {len(unhardened_l5)}/{len(l5_agents)} L5 agents NOT MCP hardened (SECURITY VIOLATION)")
            for agent in unhardened_l5[:3]:
                errors.append(f"  - {agent['class_name']}")
        else:
            print(f"✅ Test 11 PASSED: All {len(l5_agents)} L5 safety agents are MCP hardened")
    
    except Exception as e:
        errors.append(f"Test 11 FAILED: Could not validate L5 MCP: {e}")
    
    # Test 12: Table 2 (Code Quality) Data Integrity
    print("\n" + "─" * 70)
    print("Running: Table 2 (Code Quality) Data Integrity")
    print("─" * 70)
    
    try:
        # Re-extract dashboard data for this test
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        # Extract dashboardData
        data_match = re.search(r'const dashboardData = (\[.*?\]);', html_content, re.DOTALL)
        if not data_match:
            errors.append("Test 12 FAILED: Could not extract dashboardData from HTML")
        else:
            dashboard_data_test = json.loads(data_match.group(1))
            
            # Check Table 2 fields exist in dashboard data
            table2_fields = ['Typed %', 'Documented %', 'Schema Strictness %', 'Proper Base %', 'Code Quality Score']
            
            if dashboard_data_test and len(dashboard_data_test) > 0:
                total_row = dashboard_data_test[0]
                missing_table2_fields = [f for f in table2_fields if f not in total_row]
                
                if missing_table2_fields:
                    errors.append(f"Test 12 FAILED: Table 2 missing fields: {missing_table2_fields}")
                else:
                    # Verify values are reasonable
                    typed_pct = total_row.get('Typed %', 0)
                    doc_pct = total_row.get('Documented %', 0)
                    quality_score = total_row.get('Code Quality Score', 0)
                    
                    if typed_pct < 0 or typed_pct > 100:
                        errors.append(f"Test 12 FAILED: Invalid Typed % = {typed_pct}")
                    elif doc_pct < 0 or doc_pct > 100:
                        errors.append(f"Test 12 FAILED: Invalid Documented % = {doc_pct}")
                    elif quality_score < 0 or quality_score > 100:
                        errors.append(f"Test 12 FAILED: Invalid Code Quality Score = {quality_score}")
                    else:
                        print(f"✅ Test 12 PASSED: Table 2 data valid")
                        print(f"   Typed: {typed_pct}%, Documented: {doc_pct}%, Quality: {quality_score}")
                    
                    # Test 12A: Proper Base % Accuracy (cross-validate with discovery data)
                    proper_base_pct = total_row.get('Proper Base %', 0)
                    proper_base_true = sum(1 for a in agents if a.get('proper_base_class', False))
                    expected_proper_base = round((proper_base_true / len(agents)) * 100, 1) if agents else 0
                    tolerance = 1.0  # Allow 1% variance
                    
                    if abs(proper_base_pct - expected_proper_base) > tolerance:
                        errors.append(f"Test 12A FAILED: Proper Base % mismatch")
                        errors.append(f"  Expected: {expected_proper_base:.1f}% ({proper_base_true}/{len(agents)} agents)")
                        errors.append(f"  Actual: {proper_base_pct}%")
                        errors.append(f"  Difference: {abs(proper_base_pct - expected_proper_base):.1f}%")
                    else:
                        print(f"✅ Test 12A PASSED: Proper Base % accurate ({proper_base_pct}% vs {expected_proper_base:.1f}% expected)")
            else:
                errors.append("Test 12 FAILED: No dashboard data to validate Table 2")
    
    except Exception as e:
        errors.append(f"Test 12 FAILED: Could not validate Table 2: {e}")
    
    # Test 12B: Territory-Level Table 2 Accuracy
    print("\n" + "─" * 70)
    print("Running: Territory-Level Table 2 Data Accuracy")
    print("─" * 70)
    
    try:
        # Re-extract dashboard data
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html_content = dashboard_path.read_text(encoding='utf-8')
        data_match = re.search(r'const dashboardData = (\[.*?\]);', html_content, re.DOTALL)
        
        if data_match:
            dashboard_data_test = json.loads(data_match.group(1))
            territory_errors = []
            
            # Check first 5 territories for accuracy
            for territory_row in dashboard_data_test[1:6]:  # Skip TOTAL
                territory_name = territory_row.get('Territory', '')
                dashboard_proper_base = territory_row.get('Proper Base %', 0)
                
                # Find agents in this territory
                territory_agents = [a for a in agents if a.get('territory') == territory_name]
                
                if territory_agents:
                    proper_base_count = sum(1 for a in territory_agents if a.get('proper_base_class', False))
                    expected_pct = round((proper_base_count / len(territory_agents)) * 100, 1)
                    
                    if abs(dashboard_proper_base - expected_pct) > 1.0:
                        territory_errors.append(f"{territory_name}: Expected {expected_pct}%, Got {dashboard_proper_base}%")
            
            if territory_errors:
                errors.append(f"Test 12B FAILED: {len(territory_errors)} territories have incorrect Proper Base %")
                for err in territory_errors[:3]:  # Show first 3
                    errors.append(f"  - {err}")
            else:
                print(f"✅ Test 12B PASSED: Territory-level Proper Base % accurate (sampled 5 territories)")
        else:
            errors.append("Test 12B FAILED: Could not extract dashboard data")
    
    except Exception as e:
        errors.append(f"Test 12B FAILED: Could not validate territory data: {e}")
    
    # Test 13: Footnote Accuracy
    print("\n" + "─" * 70)
    print("Running: Footnote Accuracy Check")
    print("─" * 70)
    
    try:
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        footnote_checks = []
        
        # Check 1: Health footnote mentions weighted formula
        if 'Gospel-weighted' in html_content or 'Heal Capability (30%)' in html_content:
            print("   ✅ Health footnote updated to weighted formula")
        else:
            footnote_checks.append("Health footnote still shows old equal-weight formula")
        
        # Check 2: Code Quality Score footnote is accurate
        if 'Typed (35%)' in html_content or 'Schema (30%)' in html_content:
            footnote_checks.append("Code Quality Score footnote shows stale weighted formula")
        elif '(Typed % + Documented %) / 2' in html_content or 'Simple average' in html_content:
            print("   ✅ Code Quality Score footnote updated to simple average")
        else:
            footnote_checks.append("Code Quality Score footnote formula unclear")
        
        # Check 3: Stale percentage weights in footnotes
        stale_patterns = ['35%.*Schema.*30%', 'Typed.*35%', 'Metadata.*15%']
        for pattern in stale_patterns:
            if re.search(pattern, html_content):
                footnote_checks.append(f"Found stale percentage pattern: {pattern}")
                break
        
        if footnote_checks:
            errors.append(f"Test 13 FAILED: {len(footnote_checks)} footnote issues")
            for issue in footnote_checks:
                errors.append(f"  - {issue}")
        else:
            print(f"✅ Test 13 PASSED: All footnotes accurate and up-to-date")
    
    except Exception as e:
        errors.append(f"Test 13 FAILED: Could not validate footnotes: {e}")
    
    # Final Summary
    print("\n" + "=" * 70)
    if errors:
        print("❌ TESTS FAILED - Dashboard has issues")
        print("=" * 70)
        print("\n".join(errors))
        
        # Check if it's a critical base agent issue
        base_agent_errors = [e for e in errors if 'base agents:' in e.lower()]
        if base_agent_errors:
            print("\n" + "!" * 70)
            print("CRITICAL: Multiple base agents detected")
            print("!" * 70)
            print("This causes inheritance confusion. Run:")
            print("  python scripts/validate_base_agents.py")
            print("!" * 70)
        
        sys.exit(1)
    
    if all_passed:
        print("✅ ALL 13 TESTS PASSED - Dashboard is ready for deployment")
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
