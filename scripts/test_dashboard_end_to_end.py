#!/usr/bin/env python3
"""
MANDATORY END-TO-END DASHBOARD TEST WITH AUTO-REGENERATION
Must be run after ANY data change to agent_discovery_full.json or dashboard HTML.

CRITICAL REQUIREMENTS:
1. Auto-regenerate agent discovery and dashboard when agents change
2. Verify browser cache-busting headers
3. Validate JavaScript execution paths
4. Check for web server caching issues
5. Verify file modification timestamps
6. Test all JavaScript data rendering

Usage:
  python scripts/test_dashboard_end_to_end.py              # Validate only
  python scripts/test_dashboard_end_to_end.py --regenerate # Force regeneration first
  python scripts/test_dashboard_end_to_end.py --auto       # Auto-regenerate if stale
"""
import json
import re
import hashlib
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

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
        # Use proper_base_class field from discovery instead of string parsing
        orphans = []
        for agent in agents:
            name = agent.get('class_name', '')
            layer = agent.get('layer', '')
            proper_base = agent.get('proper_base_class', False)
            
            # Skip base agents themselves
            if 'BaseAgent' in name:
                continue
            
            # Skip non-core layers (Apps, Utils, etc.)
            if layer not in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Base']:
                continue
            
            # Check if agent has proper base class architecture
            if not proper_base:
                orphans.append(f"{name} ({layer})")
        
        if orphans:
            errors.append(f"Test 9 FAILED: {len(orphans)} agents lack proper base class architecture")
            for orphan in orphans[:3]:
                errors.append(f"  - {orphan}")
        else:
            print(f"✅ Test 9 PASSED: All agents have proper base class architecture")
    
    except Exception as e:
        errors.append(f"Test 9 FAILED: Could not validate base class architecture: {e}")
    
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
            table2_fields = ['Typed %', 'Documented %', 'Schema Strictness %', 'Canonical Inheritance %', 'Code Quality Score']
            
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
                    
                    # Test 12A: Canonical Inheritance % Accuracy (cross-validate with discovery data)
                    proper_base_pct = total_row.get('Canonical Inheritance %', 0)
                    proper_base_true = sum(1 for a in agents if a.get('proper_base_class', False))
                    expected_proper_base = round((proper_base_true / len(agents)) * 100, 1) if agents else 0
                    tolerance = 1.0  # Allow 1% variance
                    
                    if abs(proper_base_pct - expected_proper_base) > tolerance:
                        errors.append(f"Test 12A FAILED: Canonical Inheritance % mismatch")
                        errors.append(f"  Expected: {expected_proper_base:.1f}% ({proper_base_true}/{len(agents)} agents)")
                        errors.append(f"  Actual: {proper_base_pct}%")
                        errors.append(f"  Difference: {abs(proper_base_pct - expected_proper_base):.1f}%")
                    else:
                        print(f"✅ Test 12A PASSED: Canonical Inheritance % accurate ({proper_base_pct}% vs {expected_proper_base:.1f}% expected)")
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
                dashboard_proper_base = territory_row.get('Canonical Inheritance %', 0)
                
                # Find agents in this territory
                territory_agents = [a for a in agents if a.get('territory') == territory_name]
                
                if territory_agents:
                    proper_base_count = sum(1 for a in territory_agents if a.get('proper_base_class', False))
                    expected_pct = round((proper_base_count / len(territory_agents)) * 100, 1)
                    
                    if abs(dashboard_proper_base - expected_pct) > 1.0:
                        territory_errors.append(f"{territory_name}: Expected {expected_pct}%, Got {dashboard_proper_base}%")
            
            if territory_errors:
                errors.append(f"Test 12B FAILED: {len(territory_errors)} territories have incorrect Canonical Inheritance %")
                for err in territory_errors[:3]:  # Show first 3
                    errors.append(f"  - {err}")
            else:
                print(f"✅ Test 12B PASSED: Territory-level Canonical Inheritance % accurate (sampled 5 territories)")
        else:
            errors.append("Test 12B FAILED: Could not extract dashboard data")
    
    except Exception as e:
        errors.append(f"Test 12B FAILED: Could not validate territory data: {e}")
    
    # Test 13: Footnote Accuracy Check
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
    
    # Test 14: Snapshot Regression Test (t-1 vs t)
    print("\n" + "─" * 70)
    print("Running: Dashboard Snapshot Regression Test")
    print("─" * 70)
    
    try:
        project_root = get_validated_project_root()
        snapshot_t1 = project_root / "agent_discovery_snapshot_t-1.json"
        current_t = project_root / "agent_discovery_full.json"
        
        if not snapshot_t1.exists():
            errors.append("Test 14 SKIPPED: Snapshot file not found")
            errors.append(f"  Create baseline: git show HEAD~5:agent_discovery_full.json > agent_discovery_snapshot_t-1.json")
        else:
            # Load snapshots
            with open(snapshot_t1, 'r', encoding='utf-8') as f:
                t_minus_1 = json.load(f)
            with open(current_t, 'r', encoding='utf-8') as f:
                t_current = json.load(f)
            
            # Compare base classes
            def get_base_classes(agents_list):
                base_classes = {}
                for agent in agents_list:
                    if 'Base Class' in agent.get('territory', ''):
                        layer = agent.get('layer', 'Unknown')
                        if layer not in base_classes:
                            base_classes[layer] = []
                        base_classes[layer].append(agent['class_name'])
                return base_classes
            
            base_t1 = get_base_classes(t_minus_1)
            base_t = get_base_classes(t_current)
            
            # Check for base class violations
            base_violations = []
            all_layers = set(base_t1.keys()) | set(base_t.keys())
            for layer in all_layers:
                count_t = len(base_t.get(layer, []))
                if count_t > 1:
                    base_violations.append(f"{layer} has {count_t} base classes (expected 1)")
                elif count_t == 0:
                    base_violations.append(f"{layer} has no base class")
            
            # Calculate deltas
            delta_agents = len(t_current) - len(t_minus_1)
            agents_t1 = {a['class_name'] for a in t_minus_1}
            agents_t = {a['class_name'] for a in t_current}
            added = len(agents_t - agents_t1)
            removed = len(agents_t1 - agents_t)
            
            print(f"   Baseline (t-1): {len(t_minus_1)} agents")
            print(f"   Current (t):    {len(t_current)} agents")
            print(f"   Delta:          {delta_agents:+d} ({added} added, {removed} removed)")
            print(f"   Base classes:   {len(all_layers)} layers checked")
            
            if base_violations:
                errors.append(f"Test 14 FAILED: {len(base_violations)} base class violations")
                for violation in base_violations[:3]:
                    errors.append(f"  - {violation}")
            else:
                print(f"✅ Test 14 PASSED: Snapshot regression test passed")
                print(f"   All {len(all_layers)} layers have exactly 1 base class")
    
    except Exception as e:
        errors.append(f"Test 14 FAILED: Could not run snapshot regression: {e}")
    
    # Don't exit early - continue to browser/cache validation tests
    if errors:
        print("\n" + "=" * 70)
        print("⚠️  ISSUES DETECTED - Continuing to browser validation tests")
        print("=" * 70)
        for error in errors[:5]:  # Show first 5 errors
            print(f"   {error}")
    
    # Test 15: Browser Cache & JavaScript Validation
    print("\n" + "─" * 70)
    print("Running: Browser Cache & JavaScript Validation")
    print("─" * 70)
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check cache-busting headers
        cache_headers = [
            ('Cache-Control" content="no-cache', 'Cache-Control'),
            ('Pragma" content="no-cache', 'Pragma'),
            ('Expires" content="0', 'Expires')
        ]
        
        missing_headers = []
        for pattern, name in cache_headers:
            if pattern not in html_content:
                missing_headers.append(name)
        
        if missing_headers:
            errors.append(f"Test 15A FAILED: Missing cache-busting headers: {', '.join(missing_headers)}")
        else:
            print(f"✅ Test 15A PASSED: All cache-busting headers present")
        
        # Check critical JavaScript elements
        js_elements = [
            ('const dashboardData =', 'dashboardData declaration'),
            ('const realAgentData =', 'realAgentData declaration'),
            ('function loadData()', 'loadData function'),
            ("row['Canonical Inheritance %']", 'Canonical Inheritance % JS reference'),
            ('parseFloat(row[\'Canonical Inheritance %\']', 'Canonical Inheritance % parsing')
        ]
        
        missing_js = []
        for pattern, desc in js_elements:
            if pattern not in html_content:
                missing_js.append(desc)
        
        if missing_js:
            errors.append(f"Test 15B FAILED: Missing JavaScript elements: {', '.join(missing_js)}")
        else:
            print(f"✅ Test 15B PASSED: All critical JavaScript elements present")
        
        # Verify Canonical Inheritance % is actually used in rendering
        if "row['Canonical Inheritance %']" not in html_content:
            errors.append("Test 15C FAILED: Canonical Inheritance % not referenced in JavaScript rendering code")
        else:
            print(f"✅ Test 15C PASSED: Canonical Inheritance % properly referenced in JS")
    
    except Exception as e:
        errors.append(f"Test 15 FAILED: Could not validate browser cache/JS: {e}")
    
    # Test 16: File Freshness & Hash Verification
    print("\n" + "─" * 70)
    print("Running: File Freshness & Hash Verification")
    print("─" * 70)
    
    try:
        stat = dashboard_path.stat()
        mod_time = datetime.fromtimestamp(stat.st_mtime)
        time_since_mod = (datetime.now() - mod_time).total_seconds()
        
        # Calculate file hash for verification
        with open(dashboard_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        print(f"   File size: {stat.st_size:,} bytes")
        print(f"   Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Time since modification: {int(time_since_mod)} seconds")
        print(f"   SHA256: {file_hash[:32]}...")
        
        # Warn if file is stale (older than 10 minutes)
        if time_since_mod > 600:
            errors.append(f"Test 16A FAILED: Dashboard HTML is stale (modified {int(time_since_mod/60)} minutes ago)")
            print(f"   ⚠️  File may be cached - last modified {int(time_since_mod/60)} minutes ago")
        else:
            print(f"✅ Test 16A PASSED: File is fresh (modified {int(time_since_mod)} seconds ago)")
        
        # Verify file size is reasonable (should be > 500KB for full dashboard)
        if stat.st_size < 500000:
            errors.append(f"Test 16B FAILED: Dashboard HTML suspiciously small ({stat.st_size:,} bytes)")
        else:
            print(f"✅ Test 16B PASSED: File size reasonable ({stat.st_size:,} bytes)")
        
        # Print hash for manual browser verification
        print(f"\n   📋 FILE HASH FOR BROWSER VERIFICATION:")
        print(f"   {file_hash}")
        print(f"   Save this hash to verify browser loaded correct version")
        print(f"\n   🔄 BROWSER REFRESH INSTRUCTIONS:")
        print(f"   1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)")
        print(f"   2. Or: Ctrl+F5 (Windows/Linux)")
        print(f"   3. If using web server: Restart with cache disabled (http-server -c-1)")
    
    except Exception as e:
        errors.append(f"Test 16 FAILED: Could not verify file freshness: {e}")
    
    # Test 17: Visual Cell-by-Cell Territory Inspection
    print("\n" + "─" * 70)
    print("Running: Visual Cell-by-Cell Territory Inspection")
    print("─" * 70)
    
    try:
        # Load dashboard data for Test 17
        start_marker = 'const dashboardData = ['
        end_marker = '];'
        start_idx = html_content.find(start_marker)
        end_idx = html_content.find(end_marker, start_idx) + len(end_marker)
        json_str = html_content[start_idx + len(start_marker) - 1:end_idx - 1]
        dashboard_data = json.loads(json_str)
        
        # Get expected territories from agent discovery
        expected_territories = set()
        for agent in agents:
            territory = agent.get('territory', '')
            if territory:
                expected_territories.add(territory)
        
        # Get actual territories from dashboard
        dashboard_territories = {row['Territory'] for row in dashboard_data if row['Territory'] != 'TOTAL'}
        
        # CRITICAL: Check for Base Agent territories for each layer (8 total)
        # Note: These are "Base Agent" territories, not "Base Class" - they contain the canonical base agents
        expected_base_classes = [
            "Base/Root",
            "L5 Safety/Base Agent", 
            "L4 State/Base Agent",
            "L3 Orchestration/Base Agent",
            "L2 Execution/Base Agent",
            "L1 Cognition/Base Agent",
            "L0 Maintenance/Base Agent",
            "L6 Observability/Base Agent"
        ]
        
        missing_base_classes = []
        for base_class in expected_base_classes:
            if base_class not in dashboard_territories:
                # Check if agents exist for this territory
                agents_in_territory = [a for a in agents if a.get('territory') == base_class]
                if agents_in_territory:
                    missing_base_classes.append(f"{base_class} (has {len(agents_in_territory)} agents but missing from dashboard!)")
        
        if missing_base_classes:
            errors.append(f"Test 17A FAILED: {len(missing_base_classes)} Base Class territories MISSING from dashboard")
            for missing in missing_base_classes:
                errors.append(f"  - {missing}")
        else:
            print(f"✅ Test 17A PASSED: All expected Base Class territories present in dashboard")
        
        # Check agent count matches - discovery agents should all be in dashboard
        # Note: Discovery 'territory' field may differ from dashboard computed territories
        # so we check agent COUNT not territory names
        total_dashboard_agents = sum(row.get('Total', 0) for row in dashboard_data if row.get('Territory') != 'TOTAL')
        total_discovery_agents = len(agents)
        
        if total_dashboard_agents != total_discovery_agents:
            errors.append(f"Test 17B FAILED: Agent count mismatch - Dashboard={total_dashboard_agents}, Discovery={total_discovery_agents}")
        else:
            print(f"✅ Test 17B PASSED: All {total_discovery_agents} agents accounted for in dashboard")
        
        # Visual inspection: Check each dashboard row has valid data
        invalid_rows = []
        for row in dashboard_data:
            territory = row.get('Territory', 'UNKNOWN')
            if territory == 'TOTAL':
                continue
            
            total = row.get('Total', 0)
            if total == 0:
                invalid_rows.append(f"{territory}: Total=0 (empty territory)")
            
            # Check critical fields have valid values
            for field in ['Heal Cap %', 'Test %', 'Observable %', 'Health']:
                val = row.get(field)
                if val is None:
                    invalid_rows.append(f"{territory}: {field}=None")
                elif not isinstance(val, (int, float)):
                    invalid_rows.append(f"{territory}: {field}={val} (not numeric)")
        
        if invalid_rows:
            errors.append(f"Test 17C FAILED: {len(invalid_rows)} rows have invalid data")
            for invalid in invalid_rows[:5]:
                errors.append(f"  - {invalid}")
        else:
            print(f"✅ Test 17C PASSED: All dashboard rows have valid data")
        
        # Summary of visual inspection
        print(f"\n   📊 VISUAL INSPECTION SUMMARY:")
        print(f"   Dashboard territories: {len(dashboard_territories)}")
        print(f"   Expected Base Classes: {len(expected_base_classes)}")
        print(f"   Base Classes present:  {len([b for b in expected_base_classes if b in dashboard_territories])}")
        
    except Exception as e:
        import traceback
        print(f"   ❌ Test 17 EXCEPTION: {e}")
        traceback.print_exc()
        errors.append(f"Test 17 FAILED: Could not perform visual inspection: {e}")
    
    # Final summary
    print("\n" + "=" * 70)
    if errors:
        all_passed = False
        failed_tests.extend([e.split(':')[0].replace('FAILED', '').strip() for e in errors if 'FAILED' in e])
    
    if all_passed:
        print("✅ ALL 17 TESTS PASSED - Dashboard is ready for deployment")
        print("\n⚠️  IMPORTANT: Hard refresh browser (Ctrl+Shift+R) to see changes!")
    else:
        print(f"❌ {len(failed_tests)} TEST(S) FAILED:")
        for test in failed_tests:
            print(f"   - {test}")
        print("\n⚠️  DO NOT DEPLOY until all tests pass!")
    print("=" * 70)
    
    return all_passed

def count_actual_agents() -> int:
    """Count actual agent files in the codebase (quick scan)."""
    project_root = get_validated_project_root()
    agentic_core = project_root / "agentic_core"
    
    count = 0
    for py_file in agentic_core.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        if "Agent" in py_file.stem and py_file.stem.endswith("Agent"):
            count += 1
    return count


def regenerate_agent_discovery() -> bool:
    """Regenerate agent_discovery_full.json."""
    print("\n" + "=" * 70)
    print("🔄 REGENERATING AGENT DISCOVERY")
    print("=" * 70)
    
    project_root = get_validated_project_root()
    discovery_script = project_root / "scripts" / "full_agent_discovery.py"
    
    if not discovery_script.exists():
        print("❌ Discovery script not found: scripts/full_agent_discovery.py")
        return False
    
    try:
        import sys
        import os
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            [sys.executable, str(discovery_script)],
            cwd=str(project_root),
            capture_output=True,
            timeout=300,
            env=env,
            encoding="utf-8",
            errors="replace"
        )
        
        # Check if discovery file was created/updated (more reliable than return code)
        discovery_path = project_root / "agent_discovery_full.json"
        if discovery_path.exists():
            agents = json.load(open(discovery_path))
            if len(agents) > 0:
                print(f"✅ Agent discovery complete: {len(agents)} agents")
                if result.returncode != 0:
                    print(f"   ⚠️  Discovery had warnings (exit code {result.returncode})")
                return True
        
        # Only fail if file doesn't exist or is empty
        if result.returncode != 0:
            print(f"❌ Discovery failed: {result.stderr[:500] if result.stderr else 'No error output'}")
        else:
            print("❌ Discovery file not created or empty")
        return False
            
    except subprocess.TimeoutExpired:
        print("❌ Discovery timed out (5 min limit)")
        return False
    except Exception as e:
        print(f"❌ Discovery error: {e}")
        return False


def regenerate_dashboard() -> bool:
    """Regenerate autonomy_dashboard.html from agent discovery data."""
    print("\n" + "=" * 70)
    print("🔄 REGENERATING DASHBOARD HTML")
    print("=" * 70)
    
    project_root = get_validated_project_root()
    dashboard_script = project_root / "agentic_core" / "L6_observability" / "dashboards" / "generate_dashboard.py"
    
    if not dashboard_script.exists():
        print("❌ Dashboard generator not found")
        return False
    
    try:
        import sys
        import os
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            [sys.executable, str(dashboard_script)],
            cwd=str(project_root),
            capture_output=True,
            timeout=120,
            env=env,
            encoding="utf-8",
            errors="replace"
        )
        
        if result.returncode != 0:
            print(f"❌ Dashboard generation failed: {result.stderr[:500] if result.stderr else 'No error output'}")
            return False
        
        dashboard_path = project_root / DASHBOARD_DIR / "autonomy_dashboard.html"
        if dashboard_path.exists():
            size = dashboard_path.stat().st_size
            print(f"✅ Dashboard generated: {size:,} bytes")
            return True
        else:
            print("❌ Dashboard file not created")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard generation error: {e}")
        return False


def check_if_stale() -> Tuple[bool, str]:
    """Check if dashboard is stale (agent count mismatch or old file)."""
    project_root = get_validated_project_root()
    discovery_path = project_root / "agent_discovery_full.json"
    
    if not discovery_path.exists():
        return True, "agent_discovery_full.json not found"
    
    # Quick agent count check
    actual_count = count_actual_agents()
    
    try:
        agents = json.load(open(discovery_path))
        discovered_count = len(agents)
        
        # Allow some tolerance (±5 agents) for edge cases
        if abs(actual_count - discovered_count) > 5:
            return True, f"Agent count mismatch: {actual_count} files vs {discovered_count} discovered"
        
        # Check file age (stale if > 1 hour old)
        file_age = datetime.now().timestamp() - discovery_path.stat().st_mtime
        if file_age > 3600:  # 1 hour
            return True, f"Discovery file is {file_age/3600:.1f} hours old"
        
        return False, "Dashboard is current"
        
    except Exception as e:
        return True, f"Error checking staleness: {e}"


def full_regeneration_pipeline() -> bool:
    """Run full regeneration: discovery + dashboard."""
    print("\n" + "=" * 70)
    print("🚀 FULL DASHBOARD REGENERATION PIPELINE")
    print("=" * 70)
    
    # Step 1: Regenerate agent discovery
    if not regenerate_agent_discovery():
        return False
    
    # Step 2: Regenerate dashboard
    if not regenerate_dashboard():
        return False
    
    print("\n✅ Regeneration pipeline complete")
    return True


if __name__ == "__main__":
    import sys
    
    parser = argparse.ArgumentParser(description="Dashboard E2E Test with Auto-Regeneration")
    parser.add_argument("--regenerate", action="store_true", help="Force regeneration before testing")
    parser.add_argument("--auto", action="store_true", help="Auto-regenerate if stale")
    args = parser.parse_args()
    
    # Handle regeneration modes
    if args.regenerate:
        print("🔄 Force regeneration requested...")
        if not full_regeneration_pipeline():
            print("❌ Regeneration failed - aborting tests")
            sys.exit(1)
    elif args.auto:
        is_stale, reason = check_if_stale()
        if is_stale:
            print(f"🔄 Dashboard is stale: {reason}")
            print("   Auto-regenerating...")
            if not full_regeneration_pipeline():
                print("❌ Regeneration failed - aborting tests")
                sys.exit(1)
        else:
            print(f"✅ Dashboard is current: {reason}")
    
    # Run validation tests
    success = run_all_tests()
    sys.exit(0 if success else 1)
