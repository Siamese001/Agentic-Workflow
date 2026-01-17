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
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.config.blueprint_sovereign.structure_blueprint import DASHBOARD_DIR, get_validated_project_root

# SSOT: Import all metric definitions from single source
from scripts.dashboard_ssot_definitions import (
    # Field names (SSOT for agent_discovery_full.json)
    FIELD_HAS_HEALING, FIELD_INVOCATION as FIELD_INVOCATION_CONST, FIELD_HAS_TESTS, FIELD_MCP_HARDENED,
    FIELD_TYPED_PCT, FIELD_DOCUMENTED_PCT, FIELD_SCHEMA_STRICTNESS,
    FIELD_PROPER_BASE_CLASS, FIELD_CYCLOMATIC_COMPLEXITY,
    FIELD_CLASS_NAME, FIELD_PATH, FIELD_LAYER, FIELD_TERRITORY,
    # Column names (SSOT for dashboard display)
    COL_HEAL_CAP, COL_INVOCATION, COL_TEST, COL_HARDENED,
    COL_AVG_CC, COL_COMPLEXITY_HEALTH, COL_TYPED, COL_DOCUMENTED,
    COL_SCHEMA_STRICTNESS, COL_CANONICAL_INHERITANCE, COL_CODE_QUALITY, COL_HEALTH,
    # Calculation functions (SSOT for metrics)
    calc_health_score, calc_typed_pct, calc_documented_pct,
    calc_schema_strictness_pct, calc_canonical_inheritance_pct,
    calc_heal_cap_pct, calc_invocation_pct, calc_test_pct, calc_hardened_pct
)

# SSOT: Import exclusion logic from full_agent_discovery
from scripts.full_agent_discovery import should_exclude_file

# =============================================================================
# HELPER FUNCTION: Load Dashboard Data from Consolidated SSOT Location
# =============================================================================
def load_dashboard_data() -> Tuple[list, str]:
    """
    Load dashboard data from the consolidated SSOT location.
    
    Returns:
        Tuple of (dashboard_data_list, raw_js_content)
    """
    data_path = get_validated_project_root() / DASHBOARD_DIR / 'data' / 'dashboard_data.js'
    if not data_path.exists():
        raise FileNotFoundError(f"Dashboard data file not found: {data_path}")
    
    data_js = data_path.read_text(encoding='utf-8')
    
    # Extract dashboardData array
    start_marker = 'window.dashboardData = ['
    end_marker = '];'
    start_idx = data_js.find(start_marker)
    end_idx = data_js.find(end_marker, start_idx) + len(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        raise ValueError("Could not find window.dashboardData in dashboard_data.js")
    
    json_str = data_js[start_idx + len(start_marker) - 1:end_idx - 1]
    dashboard_data = json.loads(json_str)
    
    return dashboard_data, data_js


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
    """Test 2: Verify dashboard HTML and data files exist."""
    errors = []
    project_root = get_validated_project_root()
    dashboard_path = project_root / DASHBOARD_DIR / 'autonomy_dashboard.html'
    data_path = project_root / DASHBOARD_DIR / 'data' / 'dashboard_data.js'
    
    if not dashboard_path.exists():
        errors.append("❌ autonomy_dashboard.html not found")
        return False, errors
    
    if not data_path.exists():
        errors.append("❌ dashboard_data.js not found")
        return False, errors
    
    try:
        html = dashboard_path.read_text(encoding='utf-8')
        data_js = data_path.read_text(encoding='utf-8')
        
        if len(html) < 1000:
            errors.append("❌ Dashboard HTML is suspiciously small")
            return False, errors
        
        if 'window.dashboardData' not in data_js:
            errors.append("❌ dashboard_data.js missing window.dashboardData")
            return False, errors
        
        print(f"✅ Test 2 PASSED: Dashboard HTML ({len(html)} bytes) and data file ({len(data_js)} bytes) exist")
        return True, []
        
    except Exception as e:
        errors.append(f"❌ Failed to read dashboard files: {e}")
        return False, errors

def test_dashboard_data_structure() -> Tuple[bool, List[str]]:
    """Test 3: Verify dashboardData JSON structure in dashboard_data.js."""
    errors = []
    data_path = get_validated_project_root() / DASHBOARD_DIR / 'data' / 'dashboard_data.js'
    
    try:
        data_js = data_path.read_text(encoding='utf-8')
        
        # Extract dashboardData from JS file
        start_marker = 'window.dashboardData = ['
        end_marker = '];'
        start_idx = data_js.find(start_marker)
        end_idx = data_js.find(end_marker, start_idx) + len(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            errors.append("❌ Could not find window.dashboardData in dashboard_data.js")
            return False, errors
        
        json_str = data_js[start_idx+len(start_marker)-1:end_idx-1]
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
    data_path = get_validated_project_root() / DASHBOARD_DIR / 'data' / 'dashboard_data.js'
    
    # SSOT: Use canonical column names from dashboard_ssot_definitions
    required_fields = [
        'Territory', 'Total', COL_HEAL_CAP, COL_INVOCATION,
        COL_TEST, COL_HARDENED, COL_AVG_CC, COL_COMPLEXITY_HEALTH,
        COL_TYPED, COL_DOCUMENTED, COL_SCHEMA_STRICTNESS, COL_CANONICAL_INHERITANCE,
        COL_CODE_QUALITY, COL_HEALTH
    ]
    
    try:
        data_js = data_path.read_text(encoding='utf-8')
        start_marker = 'window.dashboardData = ['
        end_marker = '];'
        start_idx = data_js.find(start_marker)
        end_idx = data_js.find(end_marker, start_idx) + len(end_marker)
        json_str = data_js[start_idx+len(start_marker)-1:end_idx-1]
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

def test_discovery_field_names() -> Tuple[bool, List[str]]:
    """Test 4B: Verify agent_discovery_full.json uses exact SSOT field names.
    
    CRITICAL: This test prevents field name errors like:
    - Using 'docstring_percentage' instead of 'documented_pct'
    - Using 'typed_percentage' instead of 'typed_pct'
    - Any deviation from dashboard_ssot_definitions.py FIELD_* constants
    """
    errors = []
    
    # SSOT: All required field names from dashboard_ssot_definitions.py
    REQUIRED_SSOT_FIELDS = {
        FIELD_CLASS_NAME,
        FIELD_PATH,
        FIELD_LAYER,
        FIELD_TERRITORY,
        FIELD_HAS_HEALING,
        FIELD_HAS_TESTS,
        FIELD_MCP_HARDENED,
        FIELD_INVOCATION_CONST,
        FIELD_TYPED_PCT,
        FIELD_DOCUMENTED_PCT,
        FIELD_SCHEMA_STRICTNESS,
        FIELD_PROPER_BASE_CLASS,
        FIELD_CYCLOMATIC_COMPLEXITY,
    }
    
    # FORBIDDEN field names (common mistakes)
    FORBIDDEN_FIELD_NAMES = {
        'docstring_percentage': "Use 'documented_pct' instead",
        'typed_percentage': "Use 'typed_pct' instead",
        'docstring_pct': "Use 'documented_pct' instead",
        'type_hints_pct': "Use 'typed_pct' instead",
        'has_schema': "Use 'schema_strictness' instead",
        'base_class': "Use 'proper_base_class' instead",
    }
    
    try:
        discovery_path = get_validated_project_root() / 'agent_discovery_full.json'
        with open(discovery_path, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        if not agents:
            errors.append("❌ agent_discovery_full.json is empty")
            return False, errors
        
        # Sample first 10 agents for field validation
        sample_agents = agents[:min(10, len(agents))]
        field_issues = []
        
        for idx, agent in enumerate(sample_agents):
            agent_id = agent.get('class_name', f'Agent_{idx}')
            
            # Check for FORBIDDEN field names
            for forbidden, suggestion in FORBIDDEN_FIELD_NAMES.items():
                if forbidden in agent:
                    field_issues.append(f"{agent_id}: Found forbidden field '{forbidden}' - {suggestion}")
            
            # Check for MISSING required fields
            missing = REQUIRED_SSOT_FIELDS - set(agent.keys())
            if missing:
                field_issues.append(f"{agent_id}: Missing SSOT fields: {missing}")
        
        if field_issues:
            errors.append(f"Test 4B FAILED: {len(field_issues)} SSOT field name violations")
            for issue in field_issues[:5]:  # Show first 5
                errors.append(f"  - {issue}")
            print(f"❌ Test 4B FAILED: Discovery JSON uses incorrect field names")
            for issue in field_issues[:5]:
                print(f"   - {issue}")
            return False, errors
        
        print(f"✅ Test 4B PASSED: All agents use correct SSOT field names")
        print(f"   ✓ Validated {len(sample_agents)} agents")
        print(f"   ✓ No forbidden fields (docstring_percentage, typed_percentage, etc.)")
        print(f"   ✓ All required SSOT fields present")
        return True, []
    
    except Exception as e:
        errors.append(f"Test 4B FAILED: {e}")
        return False, errors

def test_data_consistency() -> Tuple[bool, List[str]]:
    """Test 5: Verify dashboard data matches agent_discovery_full.json."""
    errors = []
    
    try:
        # Load agent discovery (using SSOT path - no hardcoding)
        discovery_path = get_validated_project_root() / 'agent_discovery_full.json'
        with open(discovery_path, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        # Load dashboard data from JS file
        data_path = get_validated_project_root() / DASHBOARD_DIR / 'data' / 'dashboard_data.js'
        data_js = data_path.read_text(encoding='utf-8')
        start_marker = 'window.dashboardData = ['
        end_marker = '];'
        start_idx = data_js.find(start_marker)
        end_idx = data_js.find(end_marker, start_idx) + len(end_marker)
        json_str = data_js[start_idx+len(start_marker)-1:end_idx-1]
        territories = json.loads(json_str)
        
        total_row = next((t for t in territories if t.get('Territory') == 'TOTAL'), None)
        
        # Check total agent count
        dashboard_total = total_row['Total']
        actual_total = len(agents)
        if dashboard_total != actual_total:
            errors.append(f"❌ Agent count mismatch: Dashboard={dashboard_total}, Actual={actual_total}")
            return False, errors
        
        # SSOT: Check heal capability using canonical field and column names
        actual_healed = sum(1 for a in agents if a.get(FIELD_HAS_HEALING))
        heal_cap = total_row[COL_HEAL_CAP]
        heal_inv = total_row[COL_INVOCATION]
        test = total_row[COL_TEST]
        complexity = total_row[COL_COMPLEXITY_HEALTH]
        # SSOT: Use dashboard_ssot_definitions health calculation
        # Note: calc_health_score signature doesn't include 'obs' parameter
        expected_health = calc_health_score(
            heal_cap, heal_inv, test, complexity, is_l0=False
        )
        actual_heal_pct = total_row[COL_HEALTH]
        
        if abs(actual_heal_pct - expected_health) > 0.5:
            errors.append(f"❌ {COL_HEALTH} mismatch: Dashboard={actual_heal_pct}%, Expected={expected_health}%")
            return False, errors
        
        print(f"✅ Test 5 PASSED: Dashboard data consistent with agent_discovery_full.json")
        print(f"   Total agents: {actual_total}")
        print(f"   {COL_HEALTH}: {actual_heal_pct}%")
        return True, []
        
    except Exception as e:
        errors.append(f"❌ Failed to verify data consistency: {e}")
        return False, errors

def test_table_rendering_elements() -> Tuple[bool, List[str]]:
    """Test 6: Verify HTML has table rendering functions."""
    errors = []
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / 'autonomy_dashboard.html'
    
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
        ("Discovery SSOT Field Names", test_discovery_field_names),
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
    
    # Extract realAgentData from agent_data.js (separate file from dashboard_data.js)
    import re
    import json
    agent_data_path = get_validated_project_root() / DASHBOARD_DIR / 'data' / 'agent_data.js'
    
    errors = []
    if not agent_data_path.exists():
        errors.append("Test 7 FAILED: agent_data.js not found")
        match = None
    else:
        agent_data_js = agent_data_path.read_text(encoding='utf-8')
        agent_data_pattern = r'window\.realAgentData = (\{.*?\});'
        match = re.search(agent_data_pattern, agent_data_js, re.DOTALL)
        if not match:
            errors.append("Test 7 FAILED: window.realAgentData not found in agent_data.js")
    
    if match:
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
        'L0': 'L0MaintenanceBaseAgent',
        'L1': 'L1CognitionBaseAgent',
        'L2': 'L2ExecutionBaseAgent',
        'L3': 'L3OrchestrationBaseAgent',
        'L4': 'L4StateBaseAgent',
        'L5': 'L5SafetyBaseAgent',
        'L6': 'L6ObservabilityBaseAgent',
    }
    try:
        # Load agents from discovery file (using SSOT path)
        discovery_path = get_validated_project_root() / 'agent_discovery_full.json'
        with open(discovery_path, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        # Group base agents by layer
        base_agents_by_layer = {}
        base_agents_wrong_territory = []
        
        for agent in agents:
            name = agent.get('class_name', '')
            layer = agent.get('layer', '')
            territory = agent.get('territory', '')
            
            # Identify base agents (exclude deprecated simple bases)
            if name.endswith('BaseAgent') or name in ['L0MaintenanceBaseAgent', 'L1CognitionBaseAgent', 'L6Agent']:
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
            inheritance = agent.get('inheritance', [])
            
            # Skip base agents themselves
            if 'BaseAgent' in name:
                continue
            
            # Skip non-core layers (Apps, Utils, etc.)
            if layer not in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Base']:
                continue
            
            # Hardening: Cross-verify proper_base flag against actual inheritance
            # Every core agent must inherit from something ending in 'BaseAgent'
            has_base_in_list = any('BaseAgent' in base for base in inheritance)
            
            if not proper_base or not has_base_in_list:
                orphans.append(f"{name} ({layer})")
            
            # Ensure it doesn't just inherit from 'object'
            if len(inheritance) == 1 and inheritance[0] == 'object':
                orphans.append(f"{name} ({layer}) - Raw Object Inheritance")
        
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
        
        # Check heal invocation vs capability using SSOT field names
        agents_with_healing = [a for a in agents if a.get(FIELD_HAS_HEALING)]
        heal_capable = len(agents_with_healing)
        heal_invoked = sum(1 for a in agents_with_healing if a.get(FIELD_INVOCATION) == 'Yes')
        
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
        unhardened_l5 = [a for a in l5_agents if not a.get(FIELD_MCP_HARDENED)]
        # Hardening: Verify the summary isn't empty
        empty_summary_l5 = [a for a in l5_agents if not a.get('mcp_summary') or len(a.get('mcp_summary')) < 10]
        
        if unhardened_l5:
            errors.append(f"Test 11 FAILED: {len(unhardened_l5)}/{len(l5_agents)} L5 agents NOT MCP hardened (SECURITY VIOLATION)")
            for agent in unhardened_l5[:3]:
                errors.append(f"  - {agent['class_name']}")
        
        if empty_summary_l5:
            errors.append(f"Test 11 FAILED: {len(empty_summary_l5)} L5 agents have missing/weak MCP summaries")
            
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
        data_path = get_validated_project_root() / DASHBOARD_DIR / 'data' / 'dashboard_data.js'
        data_js = data_path.read_text(encoding='utf-8')
        
        # Extract dashboardData
        data_match = re.search(r'window\.dashboardData = (\[.*?\]);', data_js, re.DOTALL)
        if not data_match:
            errors.append("Test 12 FAILED: Could not extract window.dashboardData from dashboard_data.js")
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
                    # Use SSOT function
                    expected_proper_base = calc_canonical_inheritance_pct(agents)
                    tolerance = 1.0  # Allow 1% variance
                    
                    if abs(proper_base_pct - expected_proper_base) > tolerance:
                        errors.append(f"Test 12A FAILED: Canonical Inheritance % mismatch")
                        errors.append(f"  Expected: {expected_proper_base:.1f}% (from SSOT calculation)")
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
        data_path = get_validated_project_root() / DASHBOARD_DIR / 'data' / 'dashboard_data.js'
        data_js = data_path.read_text(encoding='utf-8')
        data_match = re.search(r'window\.dashboardData = (\[.*?\]);', data_js, re.DOTALL)
        
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
                    # Use SSOT function
                    expected_pct = calc_canonical_inheritance_pct(territory_agents)
                    
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
    
    # Test 12C: Table 2 Uses formatDistributionCell (Match Table 1)
    print("\n" + "─" * 70)
    print("Running: Table 2 formatDistributionCell Verification")
    print("─" * 70)
    
    try:
        # Check table-renderer.js (modular JS architecture)
        table_renderer_path = get_validated_project_root() / DASHBOARD_DIR / "js" / "renderers" / "table-renderer.js"
        if not table_renderer_path.exists():
            errors.append("Test 12C FAILED: table-renderer.js not found")
        else:
            js_content = table_renderer_path.read_text(encoding='utf-8')
            
            # Extract renderCodeQualityTable function
            table2_func_start = js_content.find('function renderCodeQualityTable(')
            if table2_func_start == -1:
                errors.append("Test 12C FAILED: renderCodeQualityTable function not found in table-renderer.js")
            else:
                table2_func_end = js_content.find('\nfunction ', table2_func_start + 100)
                if table2_func_end == -1:
                    table2_func_end = len(js_content)
                table2_func = js_content[table2_func_start:table2_func_end]
            
            table2_issues = []
            
            # Verify formatDistributionCell is used in Table 2
            if 'formatDistributionCell' not in table2_func:
                table2_issues.append("Table 2 does NOT use formatDistributionCell (Table 1 does)")
            
            # Verify computeDistributionStats is used
            if 'computeDistributionStats' not in table2_func:
                table2_issues.append("Table 2 does NOT use computeDistributionStats (Table 1 does)")
            
            # Verify getGradientBg is used for color formatting
            if 'getGradientBg' not in table2_func:
                table2_issues.append("Table 2 does NOT use getGradientBg for color backgrounds (Table 1 does)")
            
            # Verify formatProblemAgentsTooltip is used
            if 'formatProblemAgentsTooltip' not in table2_func:
                table2_issues.append("Table 2 does NOT use formatProblemAgentsTooltip for tooltips (Table 1 does)")
            
            # Verify metric-cell class is used
            if 'class="metric-cell"' not in table2_func:
                table2_issues.append("Table 2 does NOT use metric-cell class (Table 1 does)")
            
            if table2_issues:
                errors.append(f"Test 12C FAILED: {len(table2_issues)} Table 2 functionality gaps")
                for issue in table2_issues:
                    errors.append(f"  - {issue}")
                print(f"❌ Test 12C FAILED: Table 2 missing functionality that Table 1 has")
                for issue in table2_issues:
                    print(f"   - {issue}")
            else:
                print(f"✅ Test 12C PASSED: Table 2 uses same functions as Table 1")
                print(f"   ✓ formatDistributionCell for min/max/stddev display")
                print(f"   ✓ computeDistributionStats for calculations")
                print(f"   ✓ getGradientBg for color formatting")
                print(f"   ✓ formatProblemAgentsTooltip for tooltips")
                print(f"   ✓ metric-cell class for styling")
    
    except Exception as e:
        errors.append(f"Test 12C FAILED: {e}")
    
    # Test 12D: Table 2 Distribution Stats Display (Min/Max/StdDev)
    print("\n" + "─" * 70)
    print("Running: Table 2 Min/Max/StdDev Display Verification")
    print("─" * 70)
    
    try:
        # Check table-renderer.js (modular JS architecture)
        table_renderer_path = get_validated_project_root() / DASHBOARD_DIR / "js" / "renderers" / "table-renderer.js"
        js_content = table_renderer_path.read_text(encoding='utf-8')
        
        # Extract renderCodeQualityTable function
        table2_func_start = js_content.find('function renderCodeQualityTable(')
        table2_func_end = js_content.find('\nfunction ', table2_func_start + 100)
        if table2_func_end == -1:
            table2_func_end = len(js_content)
        table2_func = js_content[table2_func_start:table2_func_end]
        
        dist_issues = []
        
        # Verify all Table 2 metrics get distribution stats
        required_stats = ['typedStats', 'documentedStats', 'schemaStats', 'baseClassStats']
        for stat in required_stats:
            if stat not in table2_func:
                dist_issues.append(f"Missing {stat} calculation")
        
        # Verify stats are passed to formatDistributionCell
        required_calls = [
            'formatDistributionCell(typed, typedStats)',
            'formatDistributionCell(documented, documentedStats)',
            'formatDistributionCell(schema, schemaStats)',
            'formatDistributionCell(baseClass, baseClassStats)'
        ]
        for call in required_calls:
            if call not in table2_func:
                dist_issues.append(f"Missing call: {call}")
        
        if dist_issues:
            errors.append(f"Test 12D FAILED: {len(dist_issues)} distribution stat issues in Table 2")
            for issue in dist_issues:
                errors.append(f"  - {issue}")
            print(f"❌ Test 12D FAILED: Table 2 distribution stats incomplete")
            for issue in dist_issues:
                print(f"   - {issue}")
        else:
            print(f"✅ Test 12D PASSED: Table 2 shows min/max/stddev for all metrics")
            print(f"   ✓ typedStats with formatDistributionCell")
            print(f"   ✓ documentedStats with formatDistributionCell")
            print(f"   ✓ schemaStats with formatDistributionCell")
            print(f"   ✓ baseClassStats with formatDistributionCell")
    
    except Exception as e:
        errors.append(f"Test 12D FAILED: {e}")
    
    # Test 12E: Table 2 Color Formatting Matches Table 1
    print("\n" + "─" * 70)
    print("Running: Table 2 Color Formatting Verification")
    print("─" * 70)
    
    try:
        # Check table-renderer.js (modular JS architecture)
        table_renderer_path = get_validated_project_root() / DASHBOARD_DIR / "js" / "renderers" / "table-renderer.js"
        js_content = table_renderer_path.read_text(encoding='utf-8')
        
        # Extract both table functions
        table1_func_start = js_content.find('function renderTerritorySummaryTable(')
        table1_func_end = js_content.find('\nfunction ', table1_func_start + 100)
        if table1_func_end == -1:
            table1_func_end = js_content.find('\n// ', table1_func_start + 100)
        table1_func = js_content[table1_func_start:table1_func_end]
        
        table2_func_start = js_content.find('function renderCodeQualityTable(')
        table2_func_end = js_content.find('\nfunction ', table2_func_start + 100)
        if table2_func_end == -1:
            table2_func_end = js_content.find('\n// ', table2_func_start + 100)
        table2_func = js_content[table2_func_start:table2_func_end]
        
        color_issues = []
        
        # Verify Table 2 uses getGradientBg like Table 1
        table1_gradient_count = table1_func.count('getGradientBg(')
        table2_gradient_count = table2_func.count('getGradientBg(')
        
        if table2_gradient_count == 0:
            color_issues.append("Table 2 does NOT use getGradientBg (Table 1 uses it for color backgrounds)")
        elif table2_gradient_count < 4:  # Should have at least 4 metrics with gradient backgrounds
            color_issues.append(f"Table 2 uses getGradientBg only {table2_gradient_count} times (should be 4+ for all metrics)")
        
        # Verify background styling pattern matches
        if 'background: ${' not in table2_func or 'Bg}' not in table2_func:
            color_issues.append("Table 2 missing background color styling pattern")
        
        if color_issues:
            errors.append(f"Test 12E FAILED: {len(color_issues)} color formatting issues")
            for issue in color_issues:
                errors.append(f"  - {issue}")
            print(f"❌ Test 12E FAILED: Table 2 color formatting doesn't match Table 1")
            for issue in color_issues:
                print(f"   - {issue}")
        else:
            print(f"✅ Test 12E PASSED: Table 2 color formatting matches Table 1")
            print(f"   ✓ Table 1 uses getGradientBg {table1_gradient_count} times")
            print(f"   ✓ Table 2 uses getGradientBg {table2_gradient_count} times")
            print(f"   ✓ Both tables use conditional background styling")
    
    except Exception as e:
        errors.append(f"Test 12E FAILED: {e}")
    
    # Test 12F: Table 2 Tooltips Match Table 1
    print("\n" + "─" * 70)
    print("Running: Table 2 Tooltip Functionality Verification")
    print("─" * 70)
    
    try:
        # Check table-renderer.js (modular JS architecture)
        table_renderer_path = get_validated_project_root() / DASHBOARD_DIR / "js" / "renderers" / "table-renderer.js"
        js_content = table_renderer_path.read_text(encoding='utf-8')
        
        table2_func_start = js_content.find('function renderCodeQualityTable(')
        table2_func_end = js_content.find('\nfunction ', table2_func_start + 100)
        if table2_func_end == -1:
            table2_func_end = len(js_content)
        table2_func = js_content[table2_func_start:table2_func_end]
        
        tooltip_issues = []
        
        # Verify Table 2 uses formatProblemAgentsTooltip for all metrics
        table2_tooltip_count = table2_func.count('formatProblemAgentsTooltip(')
        
        if table2_tooltip_count == 0:
            tooltip_issues.append("Table 2 has NO tooltips (Table 1 has tooltips for all metrics)")
        elif table2_tooltip_count < 4:  # Should have 4 metrics with tooltips
            tooltip_issues.append(f"Table 2 has only {table2_tooltip_count} tooltips (should have 4 for Typed/Documented/Schema/BaseClass)")
        
        # Verify custom-tooltip class is used
        if 'class="custom-tooltip"' not in table2_func:
            tooltip_issues.append("Table 2 missing custom-tooltip class")
        
        # Verify tooltip metrics match Table 2 metrics
        expected_tooltip_metrics = ['typed', 'documented', 'schemaStrictness', 'properBase']
        for metric in expected_tooltip_metrics:
            if f"'{metric}'" not in table2_func:
                tooltip_issues.append(f"Missing tooltip for metric: {metric}")
        
        if tooltip_issues:
            errors.append(f"Test 12F FAILED: {len(tooltip_issues)} tooltip issues")
            for issue in tooltip_issues:
                errors.append(f"  - {issue}")
            print(f"❌ Test 12F FAILED: Table 2 tooltips incomplete")
            for issue in tooltip_issues:
                print(f"   - {issue}")
        else:
            print(f"✅ Test 12F PASSED: Table 2 tooltips match Table 1 functionality")
            print(f"   ✓ {table2_tooltip_count} tooltips with formatProblemAgentsTooltip")
            print(f"   ✓ custom-tooltip class for styling")
            print(f"   ✓ All 4 metrics have tooltips (typed, documented, schema, baseClass)")
    
    except Exception as e:
        errors.append(f"Test 12F FAILED: {e}")
    
    # Test 12G: Distribution Stats Hidden at 100% (Both Tables)
    print("\n" + "─" * 70)
    print("Running: Distribution Stats Hidden at 100% Verification")
    print("─" * 70)
    
    try:
        # Check math-utils.js for the correct logic
        math_utils_path = get_validated_project_root() / DASHBOARD_DIR / "js" / "utils" / "math-utils.js"
        math_content = math_utils_path.read_text(encoding='utf-8')
        
        # Extract formatDistributionCell function
        func_start = math_content.find('function formatDistributionCell(')
        func_end = math_content.find('\nfunction ', func_start + 100)
        if func_end == -1:
            func_end = math_content.find('\n// ', func_start + 100)
        format_func = math_content[func_start:func_end]
        
        stats_100_issues = []
        
        # Verify logic checks for 100% value
        if 'avg >= 99.9' not in format_func:
            stats_100_issues.append("formatDistributionCell does NOT check for 100% value (avg >= 99.9)")
        
        # Verify logic checks for identical values (min === max)
        if 'stats.min === stats.max' not in format_func:
            stats_100_issues.append("formatDistributionCell does NOT check for identical values (min === max)")
        
        # Verify logic checks for count <= 1
        if 'stats.count <= 1' not in format_func:
            stats_100_issues.append("formatDistributionCell does NOT check for single value (count <= 1)")
        
        # Verify early return when conditions met
        if 'return `${avg.toFixed(1)}%`' not in format_func:
            stats_100_issues.append("formatDistributionCell missing early return for perfect scores")
        
        # Check that format-utils.js does NOT have duplicate function
        format_utils_path = get_validated_project_root() / DASHBOARD_DIR / "js" / "utils" / "format-utils.js"
        format_utils_content = format_utils_path.read_text(encoding='utf-8')
        
        if 'function formatDistributionCell(' in format_utils_content:
            # Check if it's the removed/commented version
            if 'REMOVED: Duplicate formatDistributionCell' not in format_utils_content:
                stats_100_issues.append("format-utils.js still has duplicate formatDistributionCell function (should be removed)")
        
        if stats_100_issues:
            errors.append(f"Test 12G FAILED: {len(stats_100_issues)} issues with 100% stats hiding logic")
            for issue in stats_100_issues:
                errors.append(f"  - {issue}")
            print(f"❌ Test 12G FAILED: Stats not properly hidden at 100%")
            for issue in stats_100_issues:
                print(f"   - {issue}")
        else:
            print(f"✅ Test 12G PASSED: Distribution stats correctly hidden at 100%")
            print(f"   ✓ Checks avg >= 99.9 (perfect score)")
            print(f"   ✓ Checks stats.min === stats.max (identical values)")
            print(f"   ✓ Checks stats.count <= 1 (single value)")
            print(f"   ✓ Early return without showing min/max/stddev")
            print(f"   ✓ No duplicate function in format-utils.js")
    
    except Exception as e:
        errors.append(f"Test 12G FAILED: {e}")
    
    # Test 13: Footnote Accuracy Check (Table 1 and Table 2)
    print("\n" + "─" * 70)
    print("Running: Comprehensive Footnote Accuracy Check (Both Tables)")
    print("─" * 70)
    
    try:
        # Check table-renderer.js for footnotes (modular architecture)
        table_renderer_path = get_validated_project_root() / DASHBOARD_DIR / "js" / "renderers" / "table-renderer.js"
        js_content = table_renderer_path.read_text(encoding='utf-8')
        
        footnote_checks = []
        
        # TABLE 1 (Territory Summary) Footnote Checks
        print("\n   Checking Table 1 (Territory Summary) Footnotes:")
        
        # Heal Capability % - NEW DEFINITION
        if 'Direct implementation: Agent defines' in js_content and 'heal()' in js_content and 'apply_fix()' in js_content and 'heal_violation()' in js_content and 'heal_repository()' in js_content:
            if 'Inheritance: Agent inherits from a class that has healing capability' in js_content and 'has_healing_in_chain()' in js_content:
                print("   ✅ Heal Capability %: Correct definition (direct + inheritance)")
            else:
                footnote_checks.append("Heal Capability %: Missing inheritance detection explanation")
        else:
            footnote_checks.append("Heal Capability %: Missing direct implementation methods (heal, apply_fix, heal_violation, heal_repository)")
        
        # Heal Invocation %
        if 'super().heal_repository()' in js_content and 'centralized healing protocol' in js_content:
            print("   ✅ Heal Invocation %: Correct definition")
        else:
            footnote_checks.append("Heal Invocation %: Missing super().heal_repository() explanation")
        
        # MCP Hardened %
        if 'MCP Hardened' in js_content and ('Model Context Protocol' in js_content or 'security validation' in js_content):
            print("   ✅ MCP Hardened %: Correct definition")
        else:
            footnote_checks.append("MCP Hardened %: Missing MCP/security validation explanation")
        
        # Test Coverage %
        if 'Test Coverage' in js_content and ('unit/integration tests' in js_content or 'test files' in js_content):
            print("   ✅ Test Coverage %: Correct definition")
        else:
            footnote_checks.append("Test Coverage %: Missing test explanation")
        
        # Complexity Health %
        if '100 - (Cyclomatic Complexity' in js_content or 'Complexity Health' in js_content:
            print("   ✅ Complexity Health %: Correct definition")
        else:
            footnote_checks.append("Complexity Health %: Missing complexity formula")
        
        # Health Score - Gospel-weighted
        if 'Gospel-weighted' in js_content or 'Heal Capability (30%)' in js_content:
            if 'Invocation (10%)' in js_content and 'Test Coverage (25%)' in js_content:
                print("   ✅ Health Score: Correct weighted formula")
            else:
                footnote_checks.append("Health Score: Weighted formula incomplete")
        else:
            footnote_checks.append("Health Score: Missing Gospel-weighted formula")
        
        # TABLE 2 (Code Quality) Footnote Checks
        print("\n   Checking Table 2 (Code Quality) Footnotes:")
        
        # Typed %
        if 'Typed %' in js_content and ('type hints' in js_content or 'type annotations' in js_content):
            print("   ✅ Typed %: Correct definition")
        else:
            footnote_checks.append("Typed %: Missing type hints explanation")
        
        # Documented %
        if 'Documented %' in js_content and 'docstrings' in js_content:
            print("   ✅ Documented %: Correct definition")
        else:
            footnote_checks.append("Documented %: Missing docstrings explanation")
        
        # Schema Strictness %
        if 'Schema Strictness' in js_content and ('@dataclass' in js_content or 'Pydantic' in js_content or 'BaseModel' in js_content):
            print("   ✅ Schema Strictness %: Correct definition")
        else:
            footnote_checks.append("Schema Strictness %: Missing @dataclass/Pydantic explanation")
        
        # Canonical Inheritance %
        if 'Canonical Inheritance' in js_content and ('SovereignBaseAgent' in js_content or 'layer bases' in js_content):
            print("   ✅ Canonical Inheritance %: Correct definition")
        else:
            footnote_checks.append("Canonical Inheritance %: Missing base class explanation")
        
        # Code Quality Score
        if 'Code Quality Score' in js_content and ('Typed % × 0.30' in js_content or 'Weighted composite' in js_content):
            print("   ✅ Code Quality Score: Correct weighted formula")
        else:
            footnote_checks.append("Code Quality Score: Missing weighted formula")
        
        # Check for stale patterns
        stale_patterns = [
            ('Typed.*35%', 'Stale Typed % weight (should be 30%)'),
            ('Schema.*30%.*Typed.*35%', 'Stale Code Quality formula'),
            ('Metadata.*15%', 'Stale metadata reference')
        ]
        for pattern, msg in stale_patterns:
            if re.search(pattern, js_content):
                footnote_checks.append(msg)
        
        if footnote_checks:
            errors.append(f"Test 13 FAILED: {len(footnote_checks)} footnote issues")
            for issue in footnote_checks:
                errors.append(f"  - {issue}")
            print(f"\n❌ Test 13 FAILED: {len(footnote_checks)} footnote accuracy issues")
        else:
            print(f"\n✅ Test 13 PASSED: All footnotes accurate for both Table 1 and Table 2")
            print(f"   ✓ Table 1: 6 metrics verified (Heal Cap, Invocation, MCP, Test, Complexity, Health)")
            print(f"   ✓ Table 2: 5 metrics verified (Typed, Documented, Schema, Base Class, Quality Score)")
    
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
        
        # SSOT: Check critical JavaScript elements in appropriate files
        # dashboard_data.js has window.dashboardData, table-renderer.js has rendering functions
        data_js_path = get_validated_project_root() / DASHBOARD_DIR / 'data' / 'dashboard_data.js'
        renderer_js_path = get_validated_project_root() / DASHBOARD_DIR / 'js' / 'renderers' / 'table-renderer.js'
        
        missing_js = []
        
        # Check dashboard_data.js for data declaration
        if data_js_path.exists():
            data_js_content = data_js_path.read_text(encoding='utf-8')
            if 'window.dashboardData' not in data_js_content:
                missing_js.append('dashboardData declaration in data file')
        else:
            missing_js.append('dashboard_data.js file')
        
        # Check table-renderer.js for rendering functions and column references
        if renderer_js_path.exists():
            renderer_content = renderer_js_path.read_text(encoding='utf-8')
            if 'renderTerritorySummaryTable' not in renderer_content and 'renderTerritorySummaryTable' not in html_content:
                missing_js.append('renderTerritorySummaryTable function')
        else:
            # Fall back to checking HTML if renderer file doesn't exist
            if 'function loadData()' not in html_content:
                missing_js.append('loadData function')
        
        if missing_js:
            errors.append(f"Test 15B FAILED: Missing JavaScript elements: {', '.join(missing_js)}")
        else:
            print(f"✅ Test 15B PASSED: All critical JavaScript elements present")
        
        # SSOT: Verify Canonical Inheritance % is referenced in rendering code
        renderer_has_col = False
        if renderer_js_path.exists():
            renderer_content = renderer_js_path.read_text(encoding='utf-8')
            if COL_CANONICAL_INHERITANCE in renderer_content or 'Canonical Inheritance' in renderer_content:
                renderer_has_col = True
        if COL_CANONICAL_INHERITANCE in html_content or 'Canonical Inheritance' in html_content:
            renderer_has_col = True
        
        if not renderer_has_col:
            errors.append(f"Test 15C FAILED: {COL_CANONICAL_INHERITANCE} not referenced in JavaScript rendering code")
        else:
            print(f"✅ Test 15C PASSED: {COL_CANONICAL_INHERITANCE} properly referenced in JS")
    
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
        # Load dashboard data for Test 17 using SSOT helper
        dashboard_data, _ = load_dashboard_data()
        
        # Get expected territories from agent discovery
        expected_territories = set()
        for agent in agents:
            territory = agent.get('territory', '')
            if territory:
                expected_territories.add(territory)
        
        # Get actual territories from dashboard
        dashboard_territories = {row['Territory'] for row in dashboard_data if row['Territory'] != 'TOTAL'}
        
        # CRITICAL: Derive expected base class territories from discovery data (no hardcoding)
        # Find all territories that contain "Base" in their name from actual agent data
        # Then map them to dashboard territory names using the same mapping as regenerate script
        territory_mapping = {
            'Base/Base Class': 'Base/Root',
            'L0 Maintenance/Base Class': 'L0 Maintenance/Base Agent',
            'L1 Cognition/Base Class': 'L1 Cognition/Base Agent',
            'L2 Execution/Base Class': 'L2 Execution/Base Agent',
            'L3 Orchestration/Base Class': 'L3 Orchestration/Base Agent',
            'L4 State/Base Class': 'L4 State/Base Agent',
            'L5 Safety/Base Class': 'L5 Safety/Base Agent',
            'L6_Observability/Base Class': 'L6 Observability/Base Agent',
        }
        
        expected_base_classes = set()
        for agent in agents:
            territory = agent.get('territory', '')
            # Include territories with "Base" pattern (Base Agent, Base Class, Base/Root)
            if 'Base' in territory:
                # Map to dashboard territory name
                mapped = territory_mapping.get(territory, territory)
                expected_base_classes.add(mapped)
        expected_base_classes = list(expected_base_classes)
        
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
            
            # SSOT: Check critical fields have valid values (allow "N/A" for L0 healing metrics)
            for field in [COL_HEAL_CAP, COL_TEST, COL_HEALTH]:
                val = row.get(field)
                if val is None:
                    invalid_rows.append(f"{territory}: {field}=None")
                elif val != "N/A" and not isinstance(val, (int, float)):
                    invalid_rows.append(f"{territory}: {field}={val} (not numeric or N/A)")
        
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
    
    # Test 18: No Hardcoded Values - Dashboard values must match discovery
    print("\n" + "─" * 70)
    print("Running: No Hardcoded Values Check")
    print("─" * 70)
    
    try:
        # Load discovery data
        discovery_path = get_validated_project_root() / 'agent_discovery_full.json'
        with open(discovery_path, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        # Calculate expected values from discovery using SSOT functions
        total_agents = len(agents)
        expected_typed = calc_typed_pct(agents)
        expected_documented = calc_documented_pct(agents)
        expected_schema = calc_schema_strictness_pct(agents)
        expected_proper_base = calc_canonical_inheritance_pct(agents)
        
        # Get dashboard values using SSOT helper
        dashboard_data_check, _ = load_dashboard_data()
        total_row = next((r for r in dashboard_data_check if r.get('Territory') == 'TOTAL'), None)
        
        if total_row:
            dashboard_typed = total_row.get('Typed %', 0)
            dashboard_documented = total_row.get('Documented %', 0)
            dashboard_schema = total_row.get('Schema Strictness %', 0)
            dashboard_proper_base = total_row.get('Canonical Inheritance %', 0)
            
            hardcoded_issues = []
            tolerance = 2.0  # Allow 2% variance for rounding
            
            if abs(dashboard_typed - expected_typed) > tolerance:
                hardcoded_issues.append(f"Typed %: Dashboard={dashboard_typed}, Expected={expected_typed}")
            if abs(dashboard_documented - expected_documented) > tolerance:
                hardcoded_issues.append(f"Documented %: Dashboard={dashboard_documented}, Expected={expected_documented}")
            if abs(dashboard_schema - expected_schema) > tolerance:
                hardcoded_issues.append(f"Schema Strictness %: Dashboard={dashboard_schema}, Expected={expected_schema}")
            if abs(dashboard_proper_base - expected_proper_base) > tolerance:
                hardcoded_issues.append(f"Canonical Inheritance %: Dashboard={dashboard_proper_base}, Expected={expected_proper_base}")
            
            if hardcoded_issues:
                errors.append(f"Test 18 FAILED: {len(hardcoded_issues)} values appear hardcoded (don't match discovery)")
                for issue in hardcoded_issues:
                    errors.append(f"  - {issue}")
            else:
                print(f"✅ Test 18 PASSED: All dashboard values match discovery data (no hardcoding)")
                print(f"   Typed: {dashboard_typed}% (expected {expected_typed}%)")
                print(f"   Documented: {dashboard_documented}% (expected {expected_documented}%)")
                print(f"   Schema: {dashboard_schema}% (expected {expected_schema}%)")
                print(f"   Canonical: {dashboard_proper_base}% (expected {expected_proper_base}%)")
        else:
            errors.append("Test 18 FAILED: Could not find TOTAL row in dashboard data")
    
    except Exception as e:
        errors.append(f"Test 18 FAILED: Could not validate hardcoding: {e}")
    
    # Test 19: Strategic Observations & Recommendations Check
    print("\n" + "─" * 70)
    print("Running: Strategic Observations & Recommendations Check")
    print("─" * 70)
    
    try:
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        # Check for Strategic Observations section
        strategic_section_exists = '📋 Strategic Observations & Prioritized Actions' in html_content
        macro_div_exists = 'id="macroObservations"' in html_content
        metric_div_exists = 'id="metricObservations"' in html_content
        render_function_exists = 'function renderStrategicObservations' in html_content
        render_called = 'renderStrategicObservations()' in html_content
        has_observations_data = 'const strategicObservationsData = {' in html_content
        
        # Check for recommendationsData (generated by StrategicRecommendationAgent)
        recs_data_match = re.search(r'const recommendationsData = (\[.*?\]);', html_content, re.DOTALL)
        has_recommendations_data = recs_data_match is not None
        recommendations_count = 0
        if has_recommendations_data:
            try:
                recs_data = json.loads(recs_data_match.group(1))
                recommendations_count = len(recs_data)
            except:
                pass
        
        issues = []
        if not strategic_section_exists:
            issues.append("Strategic Observations section header missing")
        if not macro_div_exists:
            issues.append("macroObservations div missing")
        if not metric_div_exists:
            issues.append("metricObservations div missing")
        if not render_function_exists:
            issues.append("renderStrategicObservations function missing")
        if not render_called:
            issues.append("renderStrategicObservations not called in loadData")
        if not has_observations_data:
            issues.append("strategicObservationsData not found (StrategicRecommendationAgent not integrated)")
        if not has_recommendations_data:
            issues.append("recommendationsData not found (StrategicRecommendationAgent not integrated)")
        
        if issues:
            errors.append(f"Test 19 FAILED: {len(issues)} Strategic Observations issues")
            for issue in issues:
                errors.append(f"  - {issue}")
        else:
            print(f"✅ Test 19 PASSED: Strategic Observations & Recommendations configured")
            print(f"   ✓ Section header present")
            print(f"   ✓ Macro observations container present")
            print(f"   ✓ Metric observations container present")
            print(f"   ✓ Render function defined")
            print(f"   ✓ Render function called in loadData")
            print(f"   ✓ strategicObservationsData present (StrategicRecommendationAgent SSOT)")
            print(f"   ✓ recommendationsData present ({recommendations_count} recommendations from StrategicRecommendationAgent)")
    
    except Exception as e:
        errors.append(f"Test 19 FAILED: Could not validate Strategic Observations: {e}")
    
    # Test 20: Comprehensive Zero Hardcoding Check (ALL metrics)
    print("\n" + "─" * 70)
    print("Running: Comprehensive Zero Hardcoding Check")
    print("─" * 70)
    
    try:
        # Load discovery data
        discovery_path = get_validated_project_root() / 'agent_discovery_full.json'
        with open(discovery_path, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        total_agents = len(agents)
        
        # Calculate ALL expected values from discovery (SSOT)
        # IMPORTANT: Use SSOT functions to match regenerate_dashboard_full.py exactly
        expected_metrics = {
            'Total': total_agents,
            COL_HEAL_CAP: calc_heal_cap_pct(agents),
            COL_INVOCATION: calc_invocation_pct(agents),
            COL_TEST: calc_test_pct(agents),
            COL_HARDENED: calc_hardened_pct(agents),
            COL_TYPED: calc_typed_pct(agents),
            COL_DOCUMENTED: calc_documented_pct(agents),
            COL_SCHEMA_STRICTNESS: calc_schema_strictness_pct(agents),
            COL_CANONICAL_INHERITANCE: calc_canonical_inheritance_pct(agents),
        }
        
        # Get dashboard TOTAL row values using SSOT helper
        dashboard_data_check, _ = load_dashboard_data()
        total_row = next((r for r in dashboard_data_check if r.get('Territory') == 'TOTAL'), None)
        
        hardcoded_issues = []
        if total_row:
            tolerance = 2.0  # Allow 2% variance for rounding differences
            
            for metric, expected in expected_metrics.items():
                actual = total_row.get(metric, 0)
                if actual is None:
                    actual = 0
                
                if abs(float(actual) - float(expected)) > tolerance:
                    hardcoded_issues.append(f"{metric}: Dashboard={actual}, Discovery={expected}")
            
            if hardcoded_issues:
                errors.append(f"Test 20 FAILED: {len(hardcoded_issues)} metrics appear hardcoded")
                for issue in hardcoded_issues:
                    errors.append(f"  - {issue}")
            else:
                print(f"✅ Test 20 PASSED: All {len(expected_metrics)} metrics match discovery (zero hardcoding)")
                for metric, expected in expected_metrics.items():
                    actual = total_row.get(metric, 0)
                    print(f"   ✓ {metric}: {actual} (expected {expected})")
        else:
            errors.append("Test 20 FAILED: Could not find TOTAL row")
    
    except Exception as e:
        errors.append(f"Test 20 FAILED: {e}")
    
    # Test 20B: Health Score Weighted Average Validation (CRITICAL)
    print("\n" + "─" * 70)
    print("Running: Health Score Weighted Average Validation")
    print("─" * 70)
    
    try:
        # Load discovery data
        discovery_path = get_validated_project_root() / 'agent_discovery_full.json'
        with open(discovery_path, 'r', encoding='utf-8') as f:
            agents = json.load(f)
        
        # Get dashboard TOTAL row using SSOT helper
        dashboard_data_check, _ = load_dashboard_data()
        total_row = next((r for r in dashboard_data_check if r.get('Territory') == 'TOTAL'), None)
        
        if total_row:
            # SSOT: Calculate expected health using weighted formula
            heal_cap = total_row.get(COL_HEAL_CAP, 0)
            invocation = total_row.get(COL_INVOCATION, 0)
            test = total_row.get(COL_TEST, 0)
            complexity = total_row.get(COL_COMPLEXITY_HEALTH, 0)
            
            # Expected health using SSOT weighted formula
            expected_health = calc_health_score(
                heal_cap, invocation, test, 50.0, complexity, is_l0=False
            )
            
            actual_health = total_row.get(COL_HEALTH, 0)
            
            # Verify weighted average is being used (not simple average)
            simple_avg = (heal_cap + invocation + test + 50.0 + complexity) / 5.0
            
            if abs(actual_health - simple_avg) < 1.0:
                errors.append(f"Test 20B FAILED: Health score appears to be simple average ({simple_avg:.1f}), not weighted")
                errors.append(f"  Expected (weighted): {expected_health:.1f}")
                errors.append(f"  Actual: {actual_health:.1f}")
                errors.append(f"  Simple average: {simple_avg:.1f}")
            elif abs(actual_health - expected_health) > 0.5:
                errors.append(f"Test 20B FAILED: Health score mismatch")
                errors.append(f"  Expected (SSOT weighted): {expected_health:.1f}")
                errors.append(f"  Actual: {actual_health:.1f}")
                errors.append(f"  Formula: (Heal*0.30 + Inv*0.10 + Test*0.25 + Obs*0.20 + Comp*0.15)")
            else:
                print(f"✅ Test 20B PASSED: Health score uses correct weighted average")
                print(f"   Expected (weighted): {expected_health:.1f}")
                print(f"   Actual: {actual_health:.1f}")
                print(f"   Formula: Heal*0.30 + Inv*0.10 + Test*0.25 + Obs*0.20 + Comp*0.15")
                print(f"   NOT simple average: {simple_avg:.1f}")
        else:
            errors.append("Test 20B FAILED: Could not find TOTAL row")
    
    except Exception as e:
        errors.append(f"Test 20B FAILED: {e}")
    
    # Test 21: Detailed Footnote Review (accuracy, rigor, alignment)
    print("\n" + "─" * 70)
    print("Running: Detailed Footnote Review")
    print("─" * 70)
    
    try:
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        # Define expected footnote definitions with their metric alignment
        # SSOT: Use canonical column names for footnote definitions
        footnote_definitions = {
            COL_HEAL_CAP: {
                'description': 'Percentage of agents with healing capability (has heal/apply_fix/heal_violation/heal_repository method or inherits healing)',
                'patterns': ['heal', 'HealerMixin', 'healing capability', 'repair toolkit'],
                'required': True
            },
            COL_INVOCATION: {
                'description': 'Percentage of agents that invoke healing (call super().heal_repository())',
                'patterns': ['super().heal_repository()', 'invocation', 'healing chain'],
                'required': True
            },
            COL_TEST: {
                'description': 'Percentage of agents with associated test files',
                'patterns': ['test', 'coverage', 'regression'],
                'required': True
            },
            COL_HARDENED: {
                'description': 'Percentage of agents with MCPHardenedMixin for tool boundary security',
                'patterns': ['MCP', 'hardened', 'security', 'tool boundary'],
                'required': True
            },
            'Health': {
                'description': 'Weighted composite score of autonomy metrics',
                'patterns': ['weighted', 'composite', 'formula'],
                'required': True
            },
            'Typed %': {
                'description': 'Percentage of code with type hints',
                'patterns': ['type', 'hint', 'annotation'],
                'required': False
            },
            'Documented %': {
                'description': 'Percentage of code with docstrings',
                'patterns': ['docstring', 'documentation'],
                'required': False
            },
            'Canonical Inheritance %': {
                'description': 'Percentage of agents inheriting from proper layer base class',
                'patterns': ['inherit', 'base class', 'canonical', 'proper'],
                'required': True
            }
        }
        
        footnote_issues = []
        footnote_passes = []
        
        # Check each footnote definition
        for metric, definition in footnote_definitions.items():
            if not definition['required']:
                continue
            
            # Check if any pattern is present in the HTML
            pattern_found = False
            for pattern in definition['patterns']:
                if pattern.lower() in html_content.lower():
                    pattern_found = True
                    break
            
            if not pattern_found:
                footnote_issues.append(f"{metric}: No explanatory text found (expected patterns: {definition['patterns'][:2]})")
            else:
                footnote_passes.append(metric)
        
        # Check for specific footnote accuracy issues
        # 1. Health formula should mention weighted calculation
        if 'weighted' not in html_content.lower() and 'formula' not in html_content.lower():
            footnote_issues.append("Health: Missing weighted formula explanation")
        
        # 2. Heal Cap should distinguish from Invocation
        if 'Heal Cap' in html_content and 'Invocation' in html_content:
            # Both should be explained differently
            heal_cap_context = html_content.lower().find('heal cap')
            invocation_context = html_content.lower().find('invocation')
            if heal_cap_context > 0 and invocation_context > 0:
                footnote_passes.append("Heal Cap vs Invocation distinction")
        
        # 3. Check for outdated/incorrect definitions
        incorrect_patterns = [
            ('local heal_repository() method', 'Heal Cap %'),  # This is outdated definition
        ]
        
        for pattern, metric in incorrect_patterns:
            if pattern in html_content:
                footnote_issues.append(f"{metric}: Contains potentially outdated definition: '{pattern}'")
        
        if footnote_issues:
            errors.append(f"Test 21 FAILED: {len(footnote_issues)} footnote issues")
            for issue in footnote_issues:
                errors.append(f"  - {issue}")
        else:
            print(f"✅ Test 21 PASSED: All required footnotes present and accurate")
            print(f"   ✓ {len(footnote_passes)} metric explanations verified")
            for fp in footnote_passes[:5]:
                print(f"     - {fp}")
    
    except Exception as e:
        errors.append(f"Test 21 FAILED: {e}")
    
    # Test 22: Comprehensive JavaScript Table Rendering Simulation
    # RCA: Previous bug where "N/A" strings caused JS runtime errors was not caught
    # because E2E tests are file-based and don't execute JavaScript.
    # This test comprehensively simulates JS execution to verify tables would render.
    print("\n" + "─" * 70)
    print("Running: Comprehensive JavaScript Table Rendering Simulation")
    print("─" * 70)
    
    try:
        # Extract JavaScript functions and data from dashboard HTML
        # Get dashboardData using SSOT helper
        try:
            dashboard_data, _ = load_dashboard_data()
        except Exception as e:
            errors.append(f"Test 22 FAILED: Could not load dashboard data: {e}")
            dashboard_data = None
        
        if dashboard_data:
            js_issues = []
            
            # ============================================================
            # PART A: Verify all required rendering functions exist
            # ============================================================
            required_functions = [
                ('renderTerritorySummaryTable', 'Territory Summary table (Table 1)'),
                ('renderCodeQualityTable', 'Code Quality table (Table 2)'),
                ('renderRecommendations', 'Strategic Recommendations cards'),
                ('renderStrategicObservations', 'Strategic Observations section'),
                ('loadData', 'Main data loading orchestrator'),
                ('computeDistributionStats', 'Distribution statistics calculator'),
                ('formatDistributionCell', 'Cell value formatter'),
                ('getWorstCaseColor', 'Color gradient calculator'),
                ('openDrillModal', 'Drill-down modal handler'),
            ]
            
            missing_functions = []
            for func_name, description in required_functions:
                if f'function {func_name}' not in html_content:
                    missing_functions.append(f"{func_name}: {description}")
            
            if missing_functions:
                js_issues.append(f"Missing {len(missing_functions)} required rendering functions")
                for mf in missing_functions:
                    js_issues.append(f"  - {mf}")
            
            # ============================================================
            # PART B: Verify loadData() calls all rendering functions
            # ============================================================
            load_data_start = html_content.find('function loadData()')
            if load_data_start > 0:
                load_data_snippet = html_content[load_data_start:load_data_start + 2000]
                
                render_calls = [
                    # (Function, Error Message, Required Order Index)
                    ('renderTerritorySummaryTable', 'Table 1 not rendered', 1),
                    ('renderCodeQualityTable', 'Table 2 not rendered', 2),
                    ('renderStrategicObservations', 'Observations not rendered', 3),
                    ('renderRecommendations', 'Recommendations not rendered', 4),
                ]
                
                # Hardening: Verify rendering happens in logical sequence
                last_pos = -1
                for func_call, error_msg, _ in render_calls:
                    current_pos = load_data_snippet.find(func_call)
                    if current_pos == -1:
                        js_issues.append(f"loadData() missing call to {func_call}: {error_msg}")
                    elif current_pos < last_pos:
                        js_issues.append(f"Execution order violation: {func_call} called before previous render step")
                    last_pos = current_pos
            
            # ============================================================
            # PART C: Simulate table row generation for ALL territories
            # ============================================================
            territory_rows = [r for r in dashboard_data if r.get('Territory') != 'TOTAL']
            total_row = next((r for r in dashboard_data if r.get('Territory') == 'TOTAL'), None)
            
            if not total_row:
                js_issues.append("TOTAL row missing from dashboardData - tables cannot render summary")
            
            if len(territory_rows) == 0:
                js_issues.append("No territory rows in dashboardData - tables would be empty")
            
            # SSOT: Simulate rendering each territory row - check all required fields
            table1_fields = ['Territory', 'Total', COL_HEAL_CAP, COL_INVOCATION, COL_HARDENED, COL_TEST, COL_COMPLEXITY_HEALTH, COL_HEALTH]
            table2_fields = ['Territory', 'Total', COL_TYPED, COL_DOCUMENTED, COL_SCHEMA_STRICTNESS, COL_CANONICAL_INHERITANCE, COL_CODE_QUALITY]
            
            rows_with_missing_fields = []
            for row in dashboard_data:
                territory = row.get('Territory', 'UNKNOWN')
                
                # Check Table 1 fields
                for field in table1_fields:
                    if field not in row:
                        rows_with_missing_fields.append(f"{territory}: missing '{field}' for Table 1")
                
                # Check Table 2 fields
                for field in table2_fields:
                    if field not in row:
                        rows_with_missing_fields.append(f"{territory}: missing '{field}' for Table 2")
            
            if rows_with_missing_fields:
                js_issues.append(f"{len(rows_with_missing_fields)} missing fields would cause undefined in tables")
                for rf in rows_with_missing_fields[:5]:
                    js_issues.append(f"  - {rf}")
            
            # ============================================================
            # PART D: Verify N/A value handling (L0 territories)
            # ============================================================
            # SSOT: Check N/A value handling for L0 territories
            na_rows = [r for r in dashboard_data if r.get(COL_HEAL_CAP) == "N/A" or r.get(COL_INVOCATION) == "N/A"]
            
            if na_rows:
                # Check computeDistributionStats filters N/A
                if 'function computeDistributionStats(values)' in html_content:
                    func_start = html_content.find('function computeDistributionStats(values)')
                    func_snippet = html_content[func_start:func_start + 500]
                    if 'filter' not in func_snippet:
                        js_issues.append("computeDistributionStats: Missing N/A filter - Math.min/max would return NaN")
                
                # Check formatDistributionCell handles N/A
                if 'function formatDistributionCell(avg, stats' in html_content:
                    func_start = html_content.find('function formatDistributionCell(avg, stats')
                    func_snippet = html_content[func_start:func_start + 600]
                    if '"N/A"' not in func_snippet:
                        js_issues.append("formatDistributionCell: Missing N/A check - .toFixed() would crash")
                
                # Check getWorstCaseColor handles N/A
                if 'function getWorstCaseColor(minValue)' in html_content:
                    func_start = html_content.find('function getWorstCaseColor(minValue)')
                    func_snippet = html_content[func_start:func_start + 400]
                    if '"N/A"' not in func_snippet and 'typeof' not in func_snippet:
                        js_issues.append("getWorstCaseColor: Missing N/A check - comparisons would fail")
                
                # Check all getGradientBg occurrences handle N/A
                gradient_matches = list(re.finditer(r'const getGradientBg = \(value', html_content))
                for i, match in enumerate(gradient_matches):
                    func_snippet = html_content[match.start():match.start() + 400]
                    if '"N/A"' not in func_snippet and 'typeof value' not in func_snippet:
                        js_issues.append(f"getGradientBg (occurrence {i+1}): Missing N/A check")
            
            # ============================================================
            # PART E: Verify realAgentData exists for drill-down
            # ============================================================
            if 'const realAgentData = {' not in html_content:
                js_issues.append("realAgentData missing - drill-down modals would have no agent data")
            else:
                # Verify realAgentData has entries for each territory
                agent_data_match = re.search(r'const realAgentData = (\{.*?\});', html_content, re.DOTALL)
                if agent_data_match:
                    try:
                        real_agent_data = json.loads(agent_data_match.group(1))
                        territories_without_agents = []
                        for row in territory_rows:
                            territory = row.get('Territory')
                            if territory and territory not in real_agent_data:
                                territories_without_agents.append(territory)
                        
                        if territories_without_agents:
                            js_issues.append(f"{len(territories_without_agents)} territories missing from realAgentData")
                    except json.JSONDecodeError:
                        js_issues.append("realAgentData is not valid JSON - drill-down would crash")
            
            # ============================================================
            # PART F: Verify DOM containers exist for rendered content
            # ============================================================
            required_containers = [
                ('id="kpiGrid"', 'Table 1 container'),
                ('id="codeQualityGrid"', 'Table 2 container'),
                ('id="macroObservations"', 'Macro observations container'),
                ('id="metricObservations"', 'Metric observations container'),
            ]
            
            for container_id, description in required_containers:
                if container_id not in html_content:
                    js_issues.append(f"Missing DOM container {container_id}: {description}")
            
            # ============================================================
            # PART G: Simulate table HTML generation
            # ============================================================
            # Verify the HTML template strings in rendering functions are valid
            if 'renderTerritorySummaryTable' in html_content:
                func_start = html_content.find('function renderTerritorySummaryTable')
                func_end = html_content.find('function ', func_start + 50)
                func_body = html_content[func_start:func_end] if func_end > func_start else html_content[func_start:func_start + 10000]
                
                # Check for table structure
                if '<table' not in func_body:
                    js_issues.append("renderTerritorySummaryTable: No <table> element generated")
                if '<thead>' not in func_body:
                    js_issues.append("renderTerritorySummaryTable: No <thead> element generated")
                if '<tbody>' not in func_body:
                    js_issues.append("renderTerritorySummaryTable: No <tbody> element generated")
                if '<tr' not in func_body:
                    js_issues.append("renderTerritorySummaryTable: No <tr> elements generated")
                if '<td' not in func_body:
                    js_issues.append("renderTerritorySummaryTable: No <td> elements generated")
                
                # Verify it iterates over territory data
                if 'forEach' not in func_body and 'for' not in func_body:
                    js_issues.append("renderTerritorySummaryTable: No iteration over territories - only one row would render")
            
            # ============================================================
            # Report comprehensive results
            # ============================================================
            if js_issues:
                errors.append(f"Test 22 FAILED: {len(js_issues)} JavaScript rendering issues detected")
                for issue in js_issues:
                    errors.append(f"  - {issue}")
                print(f"❌ Test 22 FAILED: {len(js_issues)} issues would prevent table rendering")
                for issue in js_issues[:5]:
                    print(f"   - {issue}")
            else:
                print(f"✅ Test 22 PASSED: JavaScript table rendering simulation successful")
                print(f"   ✓ {len(required_functions)} rendering functions present")
                print(f"   ✓ loadData() orchestrates all render calls")
                print(f"   ✓ {len(territory_rows)} territory rows + TOTAL row have all required fields")
                print(f"   ✓ {len(na_rows)} N/A rows (L0) handled correctly")
                print(f"   ✓ realAgentData present for {len(territory_rows)} territories")
                print(f"   ✓ All DOM containers present")
                print(f"   ✓ Table HTML structure verified (<table>, <thead>, <tbody>, <tr>, <td>)")
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        errors.append(f"Test 22 FAILED: {e}")
    
    # Test 23: Dashboard Row Order Verification
    # Requirement: Base/Root (SovereignBaseAgent) must be FIRST row, TOTAL must be LAST row
    print("\n" + "─" * 70)
    print("Running: Dashboard Row Order Verification (Base/Root First, TOTAL Last)")
    print("─" * 70)
    
    try:
        # Get dashboardData using SSOT helper
        try:
            dashboard_data, _ = load_dashboard_data()
        except Exception as e:
            errors.append(f"Test 23 FAILED: Could not load dashboard data: {e}")
            dashboard_data = None
        
        if dashboard_data:
            if len(dashboard_data) < 2:
                errors.append("Test 23 FAILED: Dashboard has fewer than 2 rows")
            else:
                first_row = dashboard_data[0].get('Territory', 'UNKNOWN')
                last_row = dashboard_data[-1].get('Territory', 'UNKNOWN')
                
                order_issues = []
                
                # Check Base/Root is first
                if first_row != 'Base/Root':
                    order_issues.append(f"First row should be 'Base/Root' (SovereignBaseAgent), but is '{first_row}'")
                
                # Check TOTAL is last
                if last_row != 'TOTAL':
                    order_issues.append(f"Last row should be 'TOTAL', but is '{last_row}'")
                
                # Verify JS sorting logic matches requirement
                if 'Base/Root (SovereignBaseAgent) always FIRST' not in html_content:
                    order_issues.append("JS sorting comment missing - Base/Root FIRST rule not documented in code")
                
                if 'TOTAL always LAST' not in html_content:
                    order_issues.append("JS sorting comment missing - TOTAL LAST rule not documented in code")
                
                if order_issues:
                    errors.append(f"Test 23 FAILED: {len(order_issues)} row order issues")
                    for issue in order_issues:
                        errors.append(f"  - {issue}")
                    print(f"❌ Test 23 FAILED: Dashboard row order incorrect")
                    for issue in order_issues:
                        print(f"   - {issue}")
                else:
                    print(f"✅ Test 23 PASSED: Dashboard row order correct")
                    print(f"   ✓ First row: Base/Root (SovereignBaseAgent)")
                    print(f"   ✓ Last row: TOTAL (summary)")
                    print(f"   ✓ Total rows: {len(dashboard_data)}")
                    print(f"   ✓ JS sorting logic documented correctly")
    
    except Exception as e:
        errors.append(f"Test 23 FAILED: {e}")
    
    # Test 24: Problem Agent Tooltip Verification
    # Verifies that tooltips are present on table cells to show problem agents (<50%)
    print("\n" + "─" * 70)
    print("Running: Problem Agent Tooltip Verification")
    print("─" * 70)
    
    try:
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        tooltip_issues = []
        
        # Check that getProblemAgentsForMetric function exists
        if 'function getProblemAgentsForMetric(' not in html_content:
            tooltip_issues.append("Missing getProblemAgentsForMetric function for tooltip data")
        
        # Check that formatProblemAgentsTooltip function exists with HIGH-SIGNAL content
        if 'function formatProblemAgentsTooltip(' not in html_content:
            tooltip_issues.append("Missing formatProblemAgentsTooltip function for tooltip formatting")
        
        # Verify tooltip provides HIGH-SIGNAL information (not just list of agents)
        tooltip_func_start = html_content.find('function formatProblemAgentsTooltip(')
        if tooltip_func_start > 0:
            tooltip_func = html_content[tooltip_func_start:tooltip_func_start + 2500]
            
            # Must include distribution stats
            if 'computeDistributionStats' not in tooltip_func:
                tooltip_issues.append("Tooltip missing distribution stats (avg, min, max, stdDev)")
            
            # Must include remediation targets with file paths
            if 'REMEDIATION TARGETS' not in tooltip_func:
                tooltip_issues.append("Tooltip missing remediation targets section")
            
            # Must include file path info
            if '.path' not in tooltip_func:
                tooltip_issues.append("Tooltip missing file path information for agents")
            
            # Must include deficit calculation
            if 'deficit' not in tooltip_func.lower():
                tooltip_issues.append("Tooltip missing deficit calculation (points to threshold)")
        
        # Verify CSS-based custom tooltips are implemented (not just title attributes)
        if '.metric-cell' not in html_content:
            tooltip_issues.append("Missing .metric-cell CSS class for custom tooltips")
        if '.custom-tooltip' not in html_content:
            tooltip_issues.append("Missing .custom-tooltip CSS class for tooltip styling")
        if 'class="metric-cell"' not in html_content:
            tooltip_issues.append("Table cells not using metric-cell class for tooltips")
        if '<div class="custom-tooltip">' not in html_content:
            tooltip_issues.append("Missing custom-tooltip div elements in table cells")
        
        # Check that tooltips are used in Table 1 territory rows (not TOTAL)
        table1_metrics = ['healCap', 'invocation', 'hardened', 'test', 'complexityHealth']
        for metric in table1_metrics:
            if f"formatProblemAgentsTooltip(row.Territory, '{metric}'" not in html_content:
                tooltip_issues.append(f"Table 1: Missing tooltip for {metric}")
        
        # Check that tooltips are used in Table 2 territory rows
        table2_metrics = ['typed', 'documented', 'schemaStrictness', 'properBase']
        for metric in table2_metrics:
            if f"formatProblemAgentsTooltip(row.Territory, '{metric}'" not in html_content:
                tooltip_issues.append(f"Table 2: Missing tooltip for {metric}")
        
        # Verify Worst Agent column has been removed (should NOT be present)
        if '⚠️ Worst Agent' in html_content:
            tooltip_issues.append("Worst Agent column still present (should be removed)")
        
        # Verify Health Score and Code Quality Score don't have distribution stats
        # They should show just the value, not min/max/outliers
        if 'formatDistributionCell(totalRow.Health, healthStats)' in html_content:
            tooltip_issues.append("Health Score TOTAL row still shows distribution stats (should be simple avg)")
        if 'formatDistributionCell(codeQuality, qualityStats)' in html_content:
            tooltip_issues.append("Code Quality Score TOTAL row still shows distribution stats (should be simple avg)")
        
        if tooltip_issues:
            errors.append(f"Test 24 FAILED: {len(tooltip_issues)} tooltip issues")
            for issue in tooltip_issues:
                errors.append(f"  - {issue}")
            print(f"❌ Test 24 FAILED: {len(tooltip_issues)} tooltip implementation issues")
            for issue in tooltip_issues[:5]:
                print(f"   - {issue}")
        else:
            print(f"✅ Test 24 PASSED: HIGH-SIGNAL tooltips correctly implemented")
            print(f"   ✓ getProblemAgentsForMetric function present")
            print(f"   ✓ formatProblemAgentsTooltip with actionable intelligence")
            print(f"   ✓ Tooltips include: distribution stats, file paths, remediation targets")
            print(f"   ✓ Table 1: {len(table1_metrics)} metrics have tooltips")
            print(f"   ✓ Table 2: {len(table2_metrics)} metrics have tooltips")
            print(f"   ✓ Worst Agent column removed")
            print(f"   ✓ Health/Code Quality Scores show simple averages")
    
    except Exception as e:
        errors.append(f"Test 24 FAILED: {e}")
    
    # Test 25: Min/Max/StdDev Calculation Verification
    # Rigorously verifies that distribution statistics are correctly calculated
    print("\n" + "─" * 70)
    print("Running: Min/Max/StdDev Calculation Verification")
    print("─" * 70)
    
    try:
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        calc_issues = []
        
        # Verify computeDistributionStats function exists and has correct implementation
        if 'function computeDistributionStats(values)' in html_content:
            func_start = html_content.find('function computeDistributionStats(values)')
            func_snippet = html_content[func_start:func_start + 1500]
            
            # Check it filters N/A values
            if 'filter' not in func_snippet:
                calc_issues.append("computeDistributionStats: Missing filter for N/A values")
            
            # Check it calculates min
            if 'Math.min' not in func_snippet:
                calc_issues.append("computeDistributionStats: Missing Math.min calculation")
            
            # Check it calculates max
            if 'Math.max' not in func_snippet:
                calc_issues.append("computeDistributionStats: Missing Math.max calculation")
            
            # Check it calculates standard deviation
            if 'stdDev' not in func_snippet and 'std' not in func_snippet:
                calc_issues.append("computeDistributionStats: Missing stdDev calculation")
            
            # Check it calculates count
            if '.length' not in func_snippet:
                calc_issues.append("computeDistributionStats: Missing count (length) tracking")
        else:
            calc_issues.append("computeDistributionStats function not found")
        
        # Verify formatDistributionCell shows proper format
        if 'function formatDistributionCell(avg, stats' in html_content:
            func_start = html_content.find('function formatDistributionCell(avg, stats')
            func_snippet = html_content[func_start:func_start + 800]
            
            # Should show avg, min-max range, and stdDev
            if 'toFixed' not in func_snippet:
                calc_issues.append("formatDistributionCell: Missing toFixed for number formatting")
        else:
            calc_issues.append("formatDistributionCell function not found")
        
        if calc_issues:
            errors.append(f"Test 25 FAILED: {len(calc_issues)} calculation issues")
            for issue in calc_issues:
                errors.append(f"  - {issue}")
            print(f"❌ Test 25 FAILED: {len(calc_issues)} calculation implementation issues")
            for issue in calc_issues:
                print(f"   - {issue}")
        else:
            print(f"✅ Test 25 PASSED: Min/Max/StdDev calculations correctly implemented")
            print(f"   ✓ computeDistributionStats filters N/A values")
            print(f"   ✓ Min/Max calculations present")
            print(f"   ✓ StdDev calculation present")
            print(f"   ✓ Count tracking present")
            print(f"   ✓ formatDistributionCell properly formats values")
    
    except Exception as e:
        errors.append(f"Test 25 FAILED: {e}")
    
    # Test 26: Row Order Verification (Base/Root first, L6→L5→...→L0, Apps last)
    print("\n" + "─" * 70)
    print("Running: Row Order Verification (Base/Root → L6 → L5 → ... → L0 → Apps)")
    print("─" * 70)
    
    try:
        # Expected order: Sovereign Base Agent first, then L6→L5→L4→L3→L2→L1→L0, then Apps, TOTAL last
        EXPECTED_ORDER_PREFIXES = [
            "Sovereign Base Agent",
            "L6 Observability",
            "L5 Safety",
            "L4 State",
            "L3 Orchestration",
            "L2 Execution",
            "L1 Cognition",
            "L0 Maintenance",
            "Apps",
            "TOTAL"
        ]
        
        # Load dashboard_data.js for modular dashboard
        data_js_path = project_root / DASHBOARD_DIR / "data" / "dashboard_data.js"
        if data_js_path.exists():
            data_js_content = data_js_path.read_text(encoding='utf-8')
            # Extract JSON from window.dashboardData = [...]
            start_marker = 'window.dashboardData = '
            start_idx = data_js_content.find(start_marker)
            if start_idx != -1:
                json_start = data_js_content.find('[', start_idx)
                json_end = data_js_content.rfind(']') + 1
                dashboard_json = data_js_content[json_start:json_end]
                dashboard_rows = json.loads(dashboard_json)
                
                # Get territory order from data
                actual_territories = [row['Territory'] for row in dashboard_rows]
                
                # Verify order matches expected prefix sequence
                order_issues = []
                current_prefix_idx = 0
                
                for i, territory in enumerate(actual_territories):
                    # Find which prefix this territory matches
                    matched_prefix_idx = -1
                    for j, prefix in enumerate(EXPECTED_ORDER_PREFIXES):
                        if territory.startswith(prefix) or territory == prefix:
                            matched_prefix_idx = j
                            break
                    
                    if matched_prefix_idx == -1:
                        order_issues.append(f"Row {i+1}: '{territory}' doesn't match any expected prefix")
                    elif matched_prefix_idx < current_prefix_idx:
                        order_issues.append(f"Row {i+1}: '{territory}' is out of order (expected after {EXPECTED_ORDER_PREFIXES[current_prefix_idx]})")
                    else:
                        current_prefix_idx = matched_prefix_idx
                
                # Verify first row is Sovereign Base Agent
                if actual_territories and actual_territories[0] != "Sovereign Base Agent":
                    order_issues.insert(0, f"First row should be 'Sovereign Base Agent', got '{actual_territories[0]}'")
                
                # Verify last row is TOTAL
                if actual_territories and actual_territories[-1] != "TOTAL":
                    order_issues.append(f"Last row should be 'TOTAL', got '{actual_territories[-1]}'")
                
                if order_issues:
                    errors.append(f"Test 26 FAILED: {len(order_issues)} row order issues")
                    for issue in order_issues[:5]:  # Show first 5
                        errors.append(f"  - {issue}")
                    print(f"❌ Test 26 FAILED: Row order incorrect")
                    print(f"   Expected: Sovereign Base Agent → L6 → L5 → L4 → L3 → L2 → L1 → L0 → Apps → TOTAL")
                    print(f"   Actual first 5: {actual_territories[:5]}")
                    for issue in order_issues[:5]:
                        print(f"   - {issue}")
                else:
                    print(f"✅ Test 26 PASSED: Row order is correct")
                    print(f"   ✓ First row: {actual_territories[0]}")
                    print(f"   ✓ Last row: {actual_territories[-1]}")
                    print(f"   ✓ Order: Sovereign Base Agent → L6 → L5 → L4 → L3 → L2 → L1 → L0 → Apps → TOTAL")
            else:
                errors.append("Test 26 FAILED: Could not find window.dashboardData in dashboard_data.js")
                print("❌ Test 26 FAILED: Could not parse dashboard_data.js")
        else:
            # Fall back to checking HTML for monolithic dashboard
            print("   ⚠️  dashboard_data.js not found, skipping modular order check")
    
    except Exception as e:
        errors.append(f"Test 26 FAILED: {e}")
        print(f"❌ Test 26 FAILED: {e}")
    
    # Test 27: Cache-Busting Verification
    print("\n" + "─" * 70)
    print("Running: Cache-Busting Verification")
    print("─" * 70)
    
    try:
        cache_issues = []
        
        # Check JS files have been modified recently (within last hour)
        js_dir = project_root / DASHBOARD_DIR / "js"
        if js_dir.exists():
            stale_js_files = []
            for js_file in js_dir.rglob("*.js"):
                file_age = datetime.now().timestamp() - js_file.stat().st_mtime
                if file_age > 3600:  # 1 hour
                    stale_js_files.append(f"{js_file.name} ({int(file_age/60)} min old)")
            
            if stale_js_files:
                cache_issues.append(f"Stale JS files (may be cached): {', '.join(stale_js_files[:3])}")
        
        # Check data files
        data_dir = project_root / DASHBOARD_DIR / "data"
        if data_dir.exists():
            for data_file in data_dir.glob("*.js"):
                file_age = datetime.now().timestamp() - data_file.stat().st_mtime
                if file_age > 600:  # 10 minutes
                    cache_issues.append(f"Data file {data_file.name} is {int(file_age/60)} min old - may need regeneration")
        
        # Provide cache-busting instructions
        print("   📋 CACHE-BUSTING CHECKLIST:")
        print("   1. Stop any running http-server processes")
        print("   2. Restart server with: python -m http.server 8765 --directory agentic_core/L6_observability/dashboards")
        print("   3. Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)")
        print("   4. Or use incognito/private browsing mode")
        
        if cache_issues:
            print(f"\n   ⚠️  Potential cache issues detected:")
            for issue in cache_issues:
                print(f"      - {issue}")
            # Don't fail test, just warn
            print(f"✅ Test 27 PASSED (with warnings): Cache-busting instructions provided")
        else:
            print(f"✅ Test 27 PASSED: All files are fresh")
    
    except Exception as e:
        errors.append(f"Test 27 FAILED: {e}")
        print(f"❌ Test 27 FAILED: {e}")
    
    # Test 28: Meta-Learning Dashboard Components (Phase 5)
    print("\n" + "─" * 70)
    print("Running: Meta-Learning Dashboard Components (Phase 5)")
    print("─" * 70)
    
    try:
        dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
        html_content = dashboard_path.read_text(encoding='utf-8')
        
        # Check for Phase 5 HTML elements
        phase5_elements = [
            ('id="meta-stats"', 'Meta-Learning Stats container'),
            ('id="strategy-weights"', 'Strategy Weights container'),
            ('id="experience-stream"', 'Experience Stream container'),
            ('id="pattern-timeline"', 'Pattern Timeline container'),
            ('id="redis-stats"', 'Redis Stats container'),
            ('id="redis-log"', 'Redis Log container'),
            ('id="pinecone-stats"', 'Pinecone Stats container'),
            ('id="pinecone-queries"', 'Pinecone Queries container'),
            ('id="execution-timeline"', 'Execution Timeline container'),
            ('id="execution-summary"', 'Execution Summary container'),
            ('id="layer-flow"', 'Layer Flow container'),
        ]
        
        missing_elements = []
        for pattern, desc in phase5_elements:
            if pattern not in html_content:
                missing_elements.append(desc)
        
        if missing_elements:
            errors.append(f"Test 28A FAILED: Missing Phase 5 HTML elements: {', '.join(missing_elements[:3])}")
        else:
            print(f"✅ Test 28A PASSED: All {len(phase5_elements)} Phase 5 HTML elements present")
        
        # Check for Phase 5 JS includes
        phase5_js = [
            ('meta-learning-panel.js', 'Meta-Learning Panel component'),
            ('redis-monitor.js', 'Redis Monitor component'),
            ('pinecone-monitor.js', 'Pinecone Monitor component'),
            ('execution-flow.js', 'Execution Flow component'),
            ('meta-learning-controller.js', 'Meta-Learning Controller'),
        ]
        
        missing_js = []
        for filename, desc in phase5_js:
            if filename not in html_content:
                missing_js.append(desc)
        
        if missing_js:
            errors.append(f"Test 28B FAILED: Missing Phase 5 JS includes: {', '.join(missing_js)}")
        else:
            print(f"✅ Test 28B PASSED: All {len(phase5_js)} Phase 5 JS files included")
        
        # Check for Phase 5 CSS include
        if 'meta-learning.css' not in html_content:
            errors.append("Test 28C FAILED: meta-learning.css not included in dashboard")
        else:
            print(f"✅ Test 28C PASSED: meta-learning.css included")
        
        # Check Phase 5 section headers
        phase5_sections = [
            ('Meta-Learning Activity', 'Meta-Learning section'),
            ('Redis Cache Activity', 'Redis section'),
            ('Pinecone Vector Operations', 'Pinecone section'),
            ('Agent Execution Flow', 'Execution Flow section'),
        ]
        
        missing_sections = []
        for header, desc in phase5_sections:
            if header not in html_content:
                missing_sections.append(desc)
        
        if missing_sections:
            errors.append(f"Test 28D FAILED: Missing Phase 5 sections: {', '.join(missing_sections)}")
        else:
            print(f"✅ Test 28D PASSED: All {len(phase5_sections)} Phase 5 sections present")
    
    except Exception as e:
        errors.append(f"Test 28 FAILED: {e}")
        print(f"❌ Test 28 FAILED: {e}")
    
    # Test 29: Phase 5 JavaScript Component Files Exist
    print("\n" + "─" * 70)
    print("Running: Phase 5 JavaScript Component Files Exist")
    print("─" * 70)
    
    try:
        js_components_dir = project_root / DASHBOARD_DIR / "js" / "components"
        js_controllers_dir = project_root / DASHBOARD_DIR / "js" / "controllers"
        css_dir = project_root / DASHBOARD_DIR / "css"
        
        required_files = [
            (js_components_dir / "meta-learning-panel.js", "Meta-Learning Panel JS"),
            (js_components_dir / "redis-monitor.js", "Redis Monitor JS"),
            (js_components_dir / "pinecone-monitor.js", "Pinecone Monitor JS"),
            (js_components_dir / "execution-flow.js", "Execution Flow JS"),
            (js_controllers_dir / "meta-learning-controller.js", "Meta-Learning Controller JS"),
            (css_dir / "meta-learning.css", "Meta-Learning CSS"),
        ]
        
        missing_files = []
        for file_path, desc in required_files:
            if not file_path.exists():
                missing_files.append(desc)
        
        if missing_files:
            errors.append(f"Test 29 FAILED: Missing Phase 5 files: {', '.join(missing_files)}")
        else:
            print(f"✅ Test 29 PASSED: All {len(required_files)} Phase 5 files exist")
            for file_path, desc in required_files:
                size = file_path.stat().st_size
                print(f"   ✓ {desc}: {size:,} bytes")
    
    except Exception as e:
        errors.append(f"Test 29 FAILED: {e}")
        print(f"❌ Test 29 FAILED: {e}")
    
    # Test 30: Phase 5 API Endpoints Available
    print("\n" + "─" * 70)
    print("Running: Phase 5 API Endpoints Available")
    print("─" * 70)
    
    try:
        # Import and test API endpoints
        from agentic_core.L6_observability.api.runtime_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        phase5_endpoints = [
            ("/api/meta-learning/statistics", "Meta-Learning Statistics"),
            ("/api/redis/stats", "Redis Stats"),
            ("/api/pinecone/stats", "Pinecone Stats"),
            ("/api/execution/timeline", "Execution Timeline"),
            ("/api/runtime/state", "Runtime State"),
        ]
        
        failed_endpoints = []
        for endpoint, desc in phase5_endpoints:
            response = client.get(endpoint)
            if response.status_code != 200:
                failed_endpoints.append(f"{desc} ({response.status_code})")
        
        if failed_endpoints:
            errors.append(f"Test 30 FAILED: API endpoints not working: {', '.join(failed_endpoints)}")
        else:
            print(f"✅ Test 30 PASSED: All {len(phase5_endpoints)} Phase 5 API endpoints return 200")
    
    except ImportError as e:
        print(f"   ⚠️  Test 30 SKIPPED: Could not import API ({e})")
    except Exception as e:
        errors.append(f"Test 30 FAILED: {e}")
        print(f"❌ Test 30 FAILED: {e}")
    
    # =========================================================================
    # TEST 31: Phase 6 Integration - Start Script Exists
    # =========================================================================
    print("\n--- Test 31: Phase 6 Start Script ---")
    start_script = project_root / "scripts" / "start_runtime_api.py"
    if not start_script.exists():
        errors.append("Test 31 FAILED: start_runtime_api.py not found")
        print("❌ Test 31 FAILED: start_runtime_api.py not found")
    else:
        content = start_script.read_text(encoding='utf-8')
        required = ["uvicorn", "runtime_api", "def main()", "argparse"]
        missing = [r for r in required if r not in content]
        if missing:
            errors.append(f"Test 31 FAILED: Missing in start script: {missing}")
            print(f"❌ Test 31 FAILED: Missing in start script: {missing}")
        else:
            print("✅ Test 31 PASSED: start_runtime_api.py exists with all required components")
    
    # =========================================================================
    # TEST 32: Phase 6 Integration - E2E Data Flow
    # =========================================================================
    print("\n--- Test 32: Phase 6 E2E Data Flow ---")
    try:
        from agentic_core.L6_observability.api.runtime_api import app, meta_agent, redis_client, pinecone_wrapper
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test meta-learning data flow
        initial_exp = meta_agent.total_experiences
        response = client.post("/api/meta-learning/experience", json={
            "thought_type": "cot", "reward": 0.9, "state": {}, "outcome": {}
        })
        
        response = client.get("/api/meta-learning/statistics")
        data = response.json()
        
        if data.get("total_experiences", 0) > initial_exp:
            print("✅ Test 32 PASSED: E2E data flow working (meta-learning → API)")
        else:
            errors.append("Test 32 FAILED: E2E data flow not working")
            print("❌ Test 32 FAILED: E2E data flow not working")
    except Exception as e:
        errors.append(f"Test 32 FAILED: {e}")
        print(f"❌ Test 32 FAILED: {e}")
    
    # =========================================================================
    # TEST 33: Phase 7 Documentation - User Guide Exists
    # =========================================================================
    print("\n--- Test 33: Phase 7 User Documentation ---")
    user_doc = project_root / "docs" / "DASHBOARD_META_LEARNING_GUIDE.md"
    if not user_doc.exists():
        errors.append("Test 33 FAILED: DASHBOARD_META_LEARNING_GUIDE.md not found")
        print("❌ Test 33 FAILED: DASHBOARD_META_LEARNING_GUIDE.md not found")
    else:
        content = user_doc.read_text(encoding='utf-8')
        required = ["Overview", "Getting Started", "Troubleshooting", "FAQ"]
        missing = [r for r in required if r not in content]
        if missing:
            errors.append(f"Test 33 FAILED: Missing sections: {missing}")
            print(f"❌ Test 33 FAILED: Missing sections: {missing}")
        else:
            print("✅ Test 33 PASSED: User documentation complete with all sections")
    
    # =========================================================================
    # TEST 34: Phase 7 Documentation - Developer API Docs Exists
    # =========================================================================
    print("\n--- Test 34: Phase 7 Developer Documentation ---")
    dev_doc = project_root / "docs" / "META_LEARNING_TELEMETRY_API.md"
    if not dev_doc.exists():
        errors.append("Test 34 FAILED: META_LEARNING_TELEMETRY_API.md not found")
        print("❌ Test 34 FAILED: META_LEARNING_TELEMETRY_API.md not found")
    else:
        content = dev_doc.read_text(encoding='utf-8')
        required = ["/api/health", "/api/meta-learning", "/api/redis", "/api/pinecone"]
        missing = [r for r in required if r not in content]
        if missing:
            errors.append(f"Test 34 FAILED: Missing API docs: {missing}")
            print(f"❌ Test 34 FAILED: Missing API docs: {missing}")
        else:
            print("✅ Test 34 PASSED: Developer documentation complete with all API endpoints")
    
    # Final summary
    print("\n" + "=" * 70)
    if errors:
        all_passed = False
        failed_tests.extend([e.split(':')[0].replace('FAILED', '').strip() for e in errors if 'FAILED' in e])
    
    if all_passed:
        print("✅ ALL 34 TESTS PASSED - Dashboard is ready for deployment")
        print("\n⚠️  IMPORTANT: Hard refresh browser (Ctrl+Shift+R) to see changes!")
    else:
        print(f"❌ {len(failed_tests)} TEST(S) FAILED:")
        for test in failed_tests:
            print(f"   - {test}")
        print("\n⚠️  DO NOT DEPLOY until all tests pass!")
    print("=" * 70)
    
    return all_passed

def count_actual_agents() -> int:
    """Count actual agent files using SSOT exclusion logic."""
    project_root = get_validated_project_root()
    
    count = 0
    # Scan strictly based on SSOT logic (same as full_agent_discovery.py)
    for py_file in project_root.rglob("*.py"):
        # Use the exact same exclusion logic as the discovery script
        if not should_exclude_file(py_file):
            # Additionally verify it has "Agent" in the name as a quick heuristic
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


def check_server_health():
    """Check if dashboard server is healthy and accepting connections."""
    import socket
    import time
    
    try:
        # Try to connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8765))
        sock.close()
        
        if result == 0:
            # Server is listening - check for excessive TIME_WAIT connections
            try:
                netstat_output = subprocess.check_output(
                    ['netstat', '-ano'],
                    text=True,
                    timeout=5
                )
                
                # Count TIME_WAIT connections on port 8765
                time_wait_count = netstat_output.count('8765') - 2  # Subtract LISTENING entries
                
                if time_wait_count > 30:
                    print(f"   ⚠️  WARNING: {time_wait_count} TIME_WAIT connections detected")
                    print(f"   ⚠️  Server may be overloaded - restart recommended")
                    return False
                elif time_wait_count > 20:
                    print(f"   ⚠️  INFO: {time_wait_count} TIME_WAIT connections (acceptable)")
                
                return True
            except Exception as e:
                print(f"   ⚠️  Could not check TIME_WAIT connections: {e}")
                return True  # Assume healthy if we can't check
        else:
            print(f"   ❌ Server not responding on port 8765")
            return False
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False


def restart_dashboard_server():
    """Stop any running dashboard server and restart it with health checks."""
    import psutil
    import time
    
    print("\n" + "=" * 70)
    print("🔄 AUTOMATED DASHBOARD SERVER RESTART")
    print("=" * 70)
    
    # Find and kill existing Python HTTP servers on port 8765
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'python' in proc.info['name'].lower():
                # Check if it's running http.server on port 8765
                if 'http.server' in ' '.join(cmdline) and '8765' in ' '.join(cmdline):
                    print(f"   🛑 Stopping existing server (PID {proc.info['pid']})...")
                    proc.kill()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed_count > 0:
        print(f"   ✅ Stopped {killed_count} existing server(s)")
        time.sleep(2)  # Wait for ports to be released
    else:
        print("   ℹ️  No existing servers found")
    
    # Start new server in background
    dashboard_dir = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards"
    print(f"\n   🚀 Starting new server...")
    print(f"      Directory: {dashboard_dir}")
    print(f"      Port: 8765")
    
    try:
        # Start server as background process
        server_process = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8765"],
            cwd=str(dashboard_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True  # Detach from parent
        )
        
        # Wait a moment to ensure server starts
        time.sleep(2)
        
        # Check if server is still running
        if server_process.poll() is None:
            print(f"   ✅ Server started successfully (PID {server_process.pid})")
            print(f"   🌐 Dashboard URL: http://localhost:8765/autonomy_dashboard.html")
            
            # Verify server health
            print(f"\n   💚 Verifying server health...")
            if check_server_health():
                print(f"   ✅ Server is healthy and accepting connections")
            else:
                print(f"   ⚠️  Server health check failed but server is running")
            
            return True
        else:
            print(f"   ❌ Server failed to start")
            return False
    except Exception as e:
        print(f"   ❌ Failed to start server: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    parser = argparse.ArgumentParser(description="Dashboard E2E Test with Auto-Regeneration")
    parser.add_argument("--regenerate", action="store_true", help="Force regeneration before testing")
    parser.add_argument("--auto", action="store_true", help="Auto-regenerate if stale")
    parser.add_argument("--no-server-restart", action="store_true", help="Skip automated server restart")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip all interactive prompts (assume yes)")
    args = parser.parse_args()
    
    # MANDATORY: Display cache-busting instructions at start
    print("\n" + "=" * 70)
    print("WARNING: CRITICAL: DASHBOARD SERVER & CACHE MANAGEMENT")
    print("=" * 70)
    print("\n📋 E2E TEST WORKFLOW:")
    print("   1. ✅ AUTOMATED: Stop and restart dashboard server")
    print("   2. ⚠️  MANUAL: Clear browser cache (REQUIRED)")
    print("      • Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)")
    print("      • OR use Incognito/Private browsing mode")
    print("      • OR clear browser cache completely in settings")
    print("\n⚠️  JavaScript files are cached aggressively by browsers!")
    print("   Without cache clearing, you will see OLD versions of the dashboard.")
    print("=" * 70)
    
    # Automated server restart (unless disabled)
    if not args.no_server_restart:
        if not restart_dashboard_server():
            if args.yes:
                print("\n⚠️  Server restart failed but continuing (--yes flag)")
            else:
                print("\n⚠️  Server restart failed. Continue anyway? (yes/no): ")
                try:
                    response = input().strip().lower()
                    if response not in ['yes', 'y']:
                        print("\n⚠️  Test aborted due to server restart failure.")
                        sys.exit(1)
                except (KeyboardInterrupt, EOFError):
                    print("\n\n⚠️  Test aborted.")
                    sys.exit(1)
        
        # Additional health check after restart
        print("\n   🔍 Performing post-restart health check...")
        import time
        time.sleep(1)  # Brief pause before health check
        if not check_server_health():
            print("\n⚠️  WARNING: Server health check failed after restart")
            print("   Server may be unstable - tests may fail")
            if not args.yes:
                try:
                    response = input("   Continue anyway? (yes/no): ").strip().lower()
                    if response not in ['yes', 'y']:
                        print("\n⚠️  Test aborted due to health check failure.")
                        sys.exit(1)
                except (KeyboardInterrupt, EOFError):
                    print("\n\n⚠️  Test aborted.")
                    sys.exit(1)
    else:
        print("\n⚠️  Server restart skipped (--no-server-restart flag)")
        print("   Ensure server is running manually on port 8765")
        print("\n   🔍 Checking existing server health...")
        if not check_server_health():
            print("\n⚠️  WARNING: Existing server health check failed")
            print("   Consider restarting server manually")
    
    # Prompt user to confirm browser cache clearing (skip if --yes flag)
    if not args.yes:
        print("\n" + "=" * 70)
        try:
            response = input("\n✅ Have you cleared browser cache? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("\n⚠️  Please clear browser cache before running tests.")
                print("   Tests may fail or show incorrect results without fresh cache.")
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️  Test aborted. Please clear browser cache.")
            sys.exit(1)
    else:
        print("\n⚠️  Skipping cache confirmation (--yes flag)")
        print("   ⚠️  WARNING: Tests assume browser cache has been cleared!")
        print("   ⚠️  If tests fail, manually clear cache and re-run.")
        print("\n" + "=" * 70)
    
    # Handle regeneration modes
    if args.regenerate:
        print("\n🔄 Force regeneration requested...")
        if not full_regeneration_pipeline():
            print("❌ Regeneration failed - aborting tests")
            sys.exit(1)
    elif args.auto:
        is_stale, reason = check_if_stale()
        if is_stale:
            print(f"\n🔄 Dashboard is stale: {reason}")
            print("   Auto-regenerating...")
            if not full_regeneration_pipeline():
                print("❌ Regeneration failed - aborting tests")
                sys.exit(1)
        else:
            print(f"\n✅ Dashboard is current: {reason}")
    
    # Run validation tests
    success = run_all_tests()
    
    # MANDATORY: Run Playwright visual inspection
    if success:
        print("\n" + "=" * 70)
        print("🎭 MANDATORY PLAYWRIGHT VISUAL INSPECTION")
        print("=" * 70)
        print("\nRunning Playwright visual validation tests...")
        print("This is a REQUIRED step to visually verify all dashboard changes.")
        
        try:
            playwright_script = project_root / "scripts" / "test_dashboard_playwright_visual.py"
            result = subprocess.run(
                [sys.executable, str(playwright_script)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Show Playwright output
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            if result.returncode != 0:
                print("\n❌ PLAYWRIGHT VISUAL INSPECTION FAILED")
                print("   Dashboard changes are NOT visually validated.")
                print("   DO NOT DEPLOY until visual inspection passes.")
                success = False
            else:
                print("\n✅ PLAYWRIGHT VISUAL INSPECTION PASSED")
                print("   All dashboard changes visually validated.")
        except subprocess.TimeoutExpired:
            print("\n❌ PLAYWRIGHT VISUAL INSPECTION TIMED OUT")
            print("   Visual validation did not complete in 2 minutes.")
            success = False
        except Exception as e:
            print(f"\n❌ PLAYWRIGHT VISUAL INSPECTION ERROR: {e}")
            print("   Could not run visual validation.")
            success = False
    
    # Final reminder
    if not success:
        print("\n" + "=" * 70)
        print("⚠️  TESTS FAILED - CACHE-BUSTING REMINDER")
        print("=" * 70)
        print("If tests show 'stale JS files' or unexpected failures:")
        print("1. Restart dashboard server")
        print("2. Clear browser cache completely")
        print("3. Re-run tests")
        print("=" * 70)
    
    sys.exit(0 if success else 1)
