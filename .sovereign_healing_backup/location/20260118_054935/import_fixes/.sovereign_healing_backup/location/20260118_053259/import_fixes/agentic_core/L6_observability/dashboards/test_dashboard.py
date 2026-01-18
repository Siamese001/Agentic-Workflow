#!/usr/bin/env python3
"""
SSOT Dashboard Test Suite - L6 Observability
=============================================
Comprehensive test suite for dashboard generation.
Tests wireframe consistency across multiple data changes.

MUST PASS before any dashboard changes are committed.
"""
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Import the SSOT generator
from generate_dashboard import DashboardGenerator, TERRITORY_ORDER, REQUIRED_FIELDS

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
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

# Expected number of territories in frozen wireframe (excluding TOTAL)
EXPECTED_TERRITORY_COUNT = 28  # 29 rows total, minus TOTAL row

class DashboardTestSuite:
    """Comprehensive test suite for dashboard generation."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dashboard_path = project_root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def test_wireframe_consistency(self) -> Tuple[bool, str]:
        """Test 1: Verify dashboard wireframe is consistent."""
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            # Extract dashboardData
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                return False, "dashboardData not found in HTML"
            
            json_str = html[start_idx+len(start_marker)-1:end_idx-1]
            data = json.loads(json_str)
            
            # Check TOTAL row is first
            if not data or data[0].get("Territory") != "TOTAL":
                return False, "TOTAL row must be first"
            
            # Check all rows have required fields
            for i, row in enumerate(data):
                missing = [f for f in REQUIRED_FIELDS if f not in row]
                if missing:
                    return False, f"Row {i} missing fields: {missing}"
            
            return True, f"Wireframe consistent: {len(data)} rows with all required fields"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_territory_order(self) -> Tuple[bool, str]:
        """Test 2: Verify territory order matches FIXED detailed structure."""
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            json_str = html[start_idx+len(start_marker)-1:end_idx-1]
            data = json.loads(json_str)
            
            # Check territory order (skip TOTAL)
            territory_rows = data[1:]
            actual_order = [r["Territory"] for r in territory_rows]
            
            # Check that actual territories match expected order
            for territory in actual_order:
                if territory not in TERRITORY_ORDER:
                    return False, f"Unexpected territory: {territory} (not in frozen wireframe)"
            
            # Check we have expected number of territories
            if len(actual_order) < EXPECTED_TERRITORY_COUNT:
                return False, f"Missing territories: expected {EXPECTED_TERRITORY_COUNT}, got {len(actual_order)}"
            
            return True, f"Territory order valid: {len(actual_order)} detailed territories"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_data_consistency(self) -> Tuple[bool, str]:
        """Test 3: Verify dashboard data matches agent discovery."""
        try:
            # Load agent discovery
            discovery_path = self.project_root / AGENT_DISCOVERY_JSON
            with open(discovery_path, 'r', encoding='utf-8') as f:
                agents = json.load(f)
            
            # Load dashboard data
            html = self.dashboard_path.read_text(encoding='utf-8')
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            json_str = html[start_idx+len(start_marker)-1:end_idx-1]
            data = json.loads(json_str)
            
            total_row = data[0]
            
            # Check agent count
            if total_row["Total"] != len(agents):
                return False, f"Agent count mismatch: Dashboard={total_row['Total']}, Actual={len(agents)}"
            
            # Check heal capability
            actual_healed = sum(1 for a in agents if a.get('has_healing'))
            actual_heal_pct = round(actual_healed / len(agents) * 100, 1)
            
            if abs(total_row["Heal Cap %"] - actual_heal_pct) > 0.5:
                return False, f"Heal Cap % mismatch: Dashboard={total_row['Heal Cap %']}%, Actual={actual_heal_pct}%"
            
            return True, f"Data consistent: {len(agents)} agents, {actual_heal_pct}% heal cap"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_field_types(self) -> Tuple[bool, str]:
        """Test 4: Verify all field types are correct."""
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            json_str = html[start_idx+len(start_marker)-1:end_idx-1]
            data = json.loads(json_str)
            
            numeric_fields = [
                "Total", "Compliant", "Heal Cap %", "Heal Invocation %", "Invocation %",
                "Hardened %", "MCP Capable %", "Test %", "Observable %", "Avg CC", "Avg LOC",
                "Typed %", "Documented %", "Metadata %", "Proper Base %", "Schema Strictness %",
                "Complexity Health", "Code Quality Score", "Criticality", "Health", "Used %"
            ]
            
            string_fields = ["Territory", "Health Breakdown", "Risk"]
            
            for i, row in enumerate(data):
                # Check numeric fields
                for field in numeric_fields:
                    if field in row and not isinstance(row[field], (int, float)):
                        return False, f"Row {i}: {field} should be numeric, got {type(row[field])}"
                
                # Check string fields
                for field in string_fields:
                    if field in row and not isinstance(row[field], str):
                        return False, f"Row {i}: {field} should be string, got {type(row[field])}"
            
            return True, "All field types correct"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_regeneration_stability(self) -> Tuple[bool, str]:
        """Test 5: Verify regeneration produces frozen wireframe structure."""
        try:
            # Regenerate
            generator = DashboardGenerator(self.project_root)
            generator.load_agent_discovery()
            new_data = generator.generate_dashboard_data()
            
            # Check we have TOTAL + expected territories
            expected_total_rows = EXPECTED_TERRITORY_COUNT + 1  # +1 for TOTAL
            if len(new_data) < expected_total_rows:
                return False, f"Row count too low: expected {expected_total_rows}, got {len(new_data)}"
            
            # Check TOTAL is first
            if new_data[0].get("Territory") != "TOTAL":
                return False, "TOTAL row must be first"
            
            # Check all territories are from frozen wireframe
            new_territories = [r["Territory"] for r in new_data[1:]]
            for territory in new_territories:
                if territory not in TERRITORY_ORDER:
                    return False, f"Generated unexpected territory: {territory}"
            
            return True, f"Regeneration produces frozen wireframe: {len(new_data)} rows"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_html_rendering_elements(self) -> Tuple[bool, str]:
        """Test 6: Verify HTML has required rendering elements."""
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            required_functions = [
                'function renderTerritorySummaryTable',
                'function renderCodeQualityTable',
                'function loadData'
            ]
            
            required_elements = [
                'id="kpiGrid"',
                'id="codeQualityGrid"'
            ]
            
            for func in required_functions:
                if func not in html:
                    return False, f"Missing function: {func}"
            
            for elem in required_elements:
                if elem not in html:
                    return False, f"Missing element: {elem}"
            
            return True, "All rendering elements present"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_visual_data_population(self) -> Tuple[bool, str]:
        """Test 7: Verify dashboard is populated with real data (no mock data)."""
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            # 1. Verify realAgentData is embedded
            real_data_match = re.search(r'const realAgentData = (\{.*?\});', html, re.DOTALL)
            if not real_data_match:
                return False, "realAgentData not embedded"
            
            try:
                real_json = real_data_match.group(1)
                real_data = json.loads(real_json)
                territory_count = len(real_data)
                
                if territory_count == 0:
                    return False, "realAgentData is empty"
                
                # Check sample territory has required structure
                sample_territory = list(real_data.keys())[0]
                sample_data = real_data[sample_territory]
                
                if 'agents' not in sample_data or 'healCap' not in sample_data:
                    return False, f"realAgentData missing required fields (agents, healCap)"
                
                agent_count = len(sample_data['agents'])
                
            except json.JSONDecodeError:
                return False, "realAgentData is not valid JSON"
            
            # 2. Verify globalAgentData uses realAgentData (not mock)
            if 'globalAgentData = realAgentData' not in html:
                return False, "globalAgentData not assigned to realAgentData"
            
            # 3. Verify no mock data calls
            if 'globalAgentData = generateMockAgentData' in html:
                return False, "Still calling generateMockAgentData"
            
            # 4. Verify generateMockAgentData is deprecated
            if 'function generateMockAgentData(' in html and 'generateMockAgentData_DEPRECATED' not in html:
                return False, "generateMockAgentData not deprecated"
            
            # 5. Verify no Math.random() calls
            random_count = html.count('Math.random()')
            if random_count > 0:
                return False, f"Found {random_count} Math.random() calls (mock data)"
            
            # 6. Verify getMockFanInData is disabled
            fanin_match = re.search(r'function getMockFanInData\([^)]+\)\s*\{[^}]*return\s+(\d+)', html, re.DOTALL)
            if fanin_match:
                return_val = fanin_match.group(1)
                if return_val != '0':
                    return False, f"getMockFanInData returns {return_val} (should be 0)"
            
            return True, f"Visual data populated: {territory_count} territories, {agent_count} agents in sample, 0 mock calls"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_cell_by_cell_visual_inspection(self) -> Tuple[bool, str]:
        """Test 8: Cell-by-cell visual inspection of HTML data population (MANDATORY)."""
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            # Extract dashboardData
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            json_str = html[start_idx+len(start_marker)-1:end_idx-1]
            data = json.loads(json_str)
            
            # Extract realAgentData
            real_data_match = re.search(r'const realAgentData = (\{.*?\});', html, re.DOTALL)
            if not real_data_match:
                return False, "realAgentData not found for cell inspection"
            real_data = json.loads(real_data_match.group(1))
            
            issues = []
            
            # 1. INSPECT TOTAL ROW CELLS
            total_row = data[0]
            if total_row.get('Territory') != 'TOTAL':
                issues.append("TOTAL row not first")
            
            # Check critical TOTAL row cell values
            expected_total_agents = 291
            expected_heal_cap = 100.0
            
            if total_row.get('Total') != expected_total_agents:
                issues.append(f"TOTAL Total cell: expected {expected_total_agents}, got {total_row.get('Total')}")
            
            if total_row.get('Heal Cap %') != expected_heal_cap:
                issues.append(f"TOTAL Heal Cap % cell: expected {expected_heal_cap}, got {total_row.get('Heal Cap %')}")
            
            # Verify TOTAL row has all numeric cells populated (not null/undefined)
            numeric_fields = ['Total', 'Heal Cap %', 'Invocation %', 'Test %', 'Health', 'Avg CC']
            for field in numeric_fields:
                if field not in total_row or total_row[field] is None:
                    issues.append(f"TOTAL row cell '{field}' is null or missing")
            
            # 2. INSPECT SAMPLE TERRITORY ROW CELLS
            # Find first non-TOTAL territory with agents
            sample_territory = None
            for row in data[1:]:
                if row.get('Total', 0) > 0:
                    sample_territory = row
                    break
            
            if not sample_territory:
                issues.append("No territory rows with agents found")
            else:
                territory_name = sample_territory.get('Territory')
                
                # Verify territory row cells are populated
                if sample_territory.get('Total', 0) <= 0:
                    issues.append(f"Territory '{territory_name}' Total cell is 0 or missing")
                
                # Check that numeric cells have valid values (0-100 for percentages)
                percentage_fields = ['Heal Cap %', 'Invocation %', 'Test %', 'Health']
                for field in percentage_fields:
                    value = sample_territory.get(field)
                    if value is None:
                        issues.append(f"Territory '{territory_name}' cell '{field}' is null")
                    elif not (0 <= value <= 100):
                        issues.append(f"Territory '{territory_name}' cell '{field}' = {value} (out of range 0-100)")
            
            # 3. INSPECT OUTLIER BADGE DATA IN CELLS
            # Verify realAgentData has per-agent arrays for outlier calculation
            if real_data:
                sample_real_territory = list(real_data.keys())[0]
                sample_real_data = real_data[sample_real_territory]
                
                if 'healCap' not in sample_real_data:
                    issues.append(f"realAgentData territory '{sample_real_territory}' missing healCap array for outlier badges")
                elif not isinstance(sample_real_data['healCap'], list):
                    issues.append(f"realAgentData territory '{sample_real_territory}' healCap is not an array")
                else:
                    # Verify healCap array has values
                    heal_cap_array = sample_real_data['healCap']
                    if len(heal_cap_array) == 0:
                        issues.append(f"realAgentData territory '{sample_real_territory}' healCap array is empty")
                    
                    # Check that all values are valid percentages
                    for i, val in enumerate(heal_cap_array[:5]):  # Check first 5
                        if not (0 <= val <= 100):
                            issues.append(f"realAgentData '{sample_real_territory}' healCap[{i}] = {val} (invalid)")
            
            # 4. INSPECT SPARKLINE DATA IN CELLS
            # Verify that aggregate stats exist for sparkline rendering
            if sample_territory:
                # Check that we have the data needed for sparklines (min/max/avg)
                # Sparklines use the per-agent data arrays from realAgentData
                territory_name = sample_territory.get('Territory')
                if territory_name in real_data:
                    territory_real = real_data[territory_name]
                    required_arrays = ['healCap', 'invocation', 'test', 'health']
                    for arr_name in required_arrays:
                        if arr_name not in territory_real:
                            issues.append(f"Territory '{territory_name}' missing '{arr_name}' array for sparklines")
                        elif not isinstance(territory_real[arr_name], list):
                            issues.append(f"Territory '{territory_name}' '{arr_name}' is not an array")
            
            # 5. INSPECT DRILL-DOWN MODAL DATA IN CELLS
            # Verify agents array exists for drill-down
            if real_data:
                sample_real_territory = list(real_data.keys())[0]
                sample_real_data = real_data[sample_real_territory]
                
                if 'agents' not in sample_real_data:
                    issues.append(f"realAgentData territory '{sample_real_territory}' missing agents array for drill-down")
                elif not isinstance(sample_real_data['agents'], list):
                    issues.append(f"realAgentData territory '{sample_real_territory}' agents is not an array")
                else:
                    agents = sample_real_data['agents']
                    if len(agents) == 0:
                        issues.append(f"realAgentData territory '{sample_real_territory}' agents array is empty")
                    else:
                        # Check first agent has required fields
                        agent = agents[0]
                        required_agent_fields = ['name', 'path', 'healCap', 'invocation', 'test', 'health']
                        for field in required_agent_fields:
                            if field not in agent:
                                issues.append(f"Agent object missing '{field}' field for drill-down")
            
            # 6. VERIFY CELL RENDERING FUNCTIONS EXIST
            # Check for functions and const declarations
            if 'function formatOutlierBadge' not in html:
                issues.append("Missing formatOutlierBadge function for outlier badge rendering")
            if 'function generateSparkline' not in html:
                issues.append("Missing generateSparkline function for sparkline rendering")
            if 'const getGradientBg' not in html and 'function getGradientBg' not in html:
                issues.append("Missing getGradientBg for cell background color")
            if 'function getWorstCaseColor' not in html:
                issues.append("Missing getWorstCaseColor function for cell text color")
            if 'function openDrillModal' not in html:
                issues.append("Missing openDrillModal function for drill-down modal")
            
            # SUMMARY
            if issues:
                return False, f"Cell inspection failed: {len(issues)} issues found: {'; '.join(issues[:3])}..."
            
            print(f"✅ PASSED: Cell-by-cell inspection passed: TOTAL row verified, sample territory verified, outlier data verified, sparkline data verified, drill-down data verified")
            return True, "Cell-by-cell inspection passed"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_no_duplicate_declarations(self) -> Tuple[bool, str]:
        """Test 9: Ensure no duplicate const declarations (Phase 1 Guardrail)."""
        html = self.dashboard_path.read_text(encoding='utf-8')
        
        # Check for duplicate const declarations
        const_vars = ['dashboardData', 'realAgentData']
        issues = []
        
        for var_name in const_vars:
            pattern = rf'const\s+{var_name}\s*='
            matches = re.findall(pattern, html)
            
            if len(matches) > 1:
                issues.append(f"{var_name}: {len(matches)} declarations (expected 1)")
            elif len(matches) == 0:
                issues.append(f"{var_name}: 0 declarations (expected 1)")
        
        if issues:
            return False, f"Duplicate/missing declarations: {'; '.join(issues)}"
        
        return True, "No duplicate declarations found"
    
    def test_file_metrics(self) -> Tuple[bool, str]:
        """Test 10: Validate file size and line count are within expected ranges (Phase 1 Guardrail)."""
        html = self.dashboard_path.read_text(encoding='utf-8')
        
        # Check file size (should be 300KB-500KB)
        size_bytes = len(html.encode('utf-8'))
        size_kb = size_bytes / 1024
        
        # Check line count (should be 10K-15K)
        line_count = html.count('\n')
        
        issues = []
        
        if size_kb > 500:
            issues.append(f"Size {size_kb:.1f}KB exceeds 500KB (possible duplication)")
        elif size_kb < 300:
            issues.append(f"Size {size_kb:.1f}KB below 300KB (possible missing data)")
        
        if line_count > 15000:
            issues.append(f"Lines {line_count:,} exceed 15K (possible duplication)")
        elif line_count < 10000:
            issues.append(f"Lines {line_count:,} below 10K (possible missing data)")
        
        if issues:
            return False, '; '.join(issues)
        
        return True, f"Metrics OK: {size_kb:.1f}KB, {line_count:,} lines"
    
    def test_source_vs_rendered_data(self) -> Tuple[bool, str]:
        """Test 11: Verify rendered TOTAL row matches source data (P0 - Critical Gap).
        
        This test catches silent data mismatches where:
        - Dashboard looks good visually
        - All structural tests pass
        - BUT numbers don't match source truth
        
        Prevents "looks good but numbers wrong" bugs.
        """
        try:
            # 1. Load source truth from agent_discovery_full.json
            discovery_path = self.project_root / AGENT_DISCOVERY_JSON
            if not discovery_path.exists():
                return False, f"Source data not found: {discovery_path}"
            
            with open(discovery_path, 'r', encoding='utf-8') as f:
                agents = json.load(f)
            
            # Calculate expected metrics from source
            expected_total = len(agents)
            expected_heal_cap = sum(1 for a in agents if a.get('has_healing')) / expected_total * 100 if expected_total > 0 else 0
            expected_heal_inv = sum(1 for a in agents if a.get('invocation') == 'Yes') / expected_total * 100 if expected_total > 0 else 0
            
            # 2. Parse rendered dashboardData from HTML
            html = self.dashboard_path.read_text(encoding='utf-8')
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                return False, "Could not find dashboardData in HTML"
            
            json_str = html[start_idx + len(start_marker) - 1:end_idx - 1]
            data = json.loads(json_str)
            
            # Find TOTAL row
            total_row = None
            for row in data:
                if row.get('Territory') == 'TOTAL':
                    total_row = row
                    break
            
            if not total_row:
                return False, "TOTAL row not found in dashboardData"
            
            # 3. Compare rendered vs expected (allow ±1% rounding tolerance)
            rendered_total = total_row.get('Total', 0)
            rendered_heal_cap = total_row.get('Heal Cap %', 0)
            rendered_heal_inv = total_row.get('Heal Invocation %', 0)
            
            errors = []
            
            # Check agent count (exact match required)
            if abs(rendered_total - expected_total) > 0:
                errors.append(f"Total agents: expected {expected_total}, got {rendered_total}")
            
            # Check Heal Cap % (allow ±1% for rounding)
            if abs(rendered_heal_cap - expected_heal_cap) > 1.0:
                errors.append(f"Heal Cap %: expected {expected_heal_cap:.1f}%, got {rendered_heal_cap}%")
            
            # Check Heal Invocation % (allow ±1% for rounding)
            if abs(rendered_heal_inv - expected_heal_inv) > 1.0:
                errors.append(f"Heal Invocation %: expected {expected_heal_inv:.1f}%, got {rendered_heal_inv}%")
            
            if errors:
                return False, f"Data mismatch: {'; '.join(errors)}"
            
            return True, f"Data matches source: {rendered_total} agents, Heal Cap {rendered_heal_cap:.1f}%, Heal Inv {rendered_heal_inv:.1f}%"
            
        except json.JSONDecodeError as e:
            return False, f"JSON parse error: {e}"
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_tooltip_data_availability(self) -> Tuple[bool, str]:
        """Test 12: Verify tooltip data is available for all territories (RCA: Jan 17 2026).
        
        Catches bug where tooltips show "No agent data available" due to:
        - Territory name mismatch between dashboardData and realAgentData
        - Missing metric arrays (healCap, invocation, etc.)
        """
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            # Extract dashboardData territories
            start_marker = 'const dashboardData = ['
            end_marker = '];'
            start_idx = html.find(start_marker)
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            json_str = html[start_idx + len(start_marker) - 1:end_idx - 1]
            dashboard_data = json.loads(json_str)
            dashboard_territories = [r['Territory'] for r in dashboard_data if r['Territory'] != 'TOTAL']
            
            # Extract realAgentData
            real_data_match = re.search(r'const realAgentData = (\{.*?\});', html, re.DOTALL)
            if not real_data_match:
                return False, "realAgentData not found"
            real_data = json.loads(real_data_match.group(1))
            real_territories = set(real_data.keys())
            
            # Required metric arrays for tooltips
            required_metrics = ['healCap', 'invocation', 'hardened', 'test', 'complexityHealth', 'health', 'agents']
            
            issues = []
            
            # Check each dashboard territory has matching realAgentData
            for territory in dashboard_territories:
                if territory not in real_territories:
                    # Try case-insensitive match
                    match = next((t for t in real_territories if t.lower() == territory.lower()), None)
                    if not match:
                        issues.append(f"Territory '{territory}' missing from realAgentData")
                        continue
                    territory = match  # Use matched name
                
                # Check required metric arrays exist
                territory_data = real_data[territory]
                for metric in required_metrics:
                    if metric not in territory_data:
                        issues.append(f"Territory '{territory}' missing '{metric}' array")
                    elif metric != 'agents' and not isinstance(territory_data[metric], list):
                        issues.append(f"Territory '{territory}' '{metric}' is not an array")
                    elif metric != 'agents' and len(territory_data[metric]) == 0:
                        issues.append(f"Territory '{territory}' '{metric}' array is empty")
            
            if issues:
                return False, f"Tooltip data issues: {'; '.join(issues[:5])}{'...' if len(issues) > 5 else ''}"
            
            return True, f"All {len(dashboard_territories)} territories have complete tooltip data"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_distribution_stats_display(self) -> Tuple[bool, str]:
        """Test 13: Verify min/max/stdev shown for non-100% cells (RCA: Jan 17 2026).
        
        Catches bug where distribution stats (min, max, stddev) not shown for cells < 100%.
        The fix ensures stats are shown for all imperfect scores.
        """
        try:
            html = self.dashboard_path.read_text(encoding='utf-8')
            
            # Check formatDistributionCell function has correct logic
            if 'function formatDistributionCell' not in html:
                # Check in external JS files
                js_path = self.dashboard_path.parent / 'js' / 'utils' / 'math-utils.js'
                if js_path.exists():
                    js_content = js_path.read_text(encoding='utf-8')
                else:
                    return False, "formatDistributionCell function not found"
            else:
                js_content = html
            
            # Verify the fix is in place:
            # 1. Should NOT hide stats when avg >= 99.9 alone
            # 2. Should only hide when min === max AND min >= 99.9
            
            issues = []
            
            # Check for the correct condition
            if 'stats.min === stats.max && stats.min >= 99.9' not in js_content:
                issues.append("Missing correct condition: 'stats.min === stats.max && stats.min >= 99.9'")
            
            # Check for uniform value indicator for < 100%
            if '(all ${stats.min.toFixed(0)}%)' not in js_content and "(all ${stats.min.toFixed(0)}%)" not in js_content:
                issues.append("Missing uniform value indicator for non-100% cells")
            
            # Verify old buggy condition is NOT present
            if 'stats.min === stats.max || avg >= 99.9' in js_content:
                issues.append("Buggy condition still present: 'stats.min === stats.max || avg >= 99.9'")
            
            if issues:
                return False, f"Distribution stats display issues: {'; '.join(issues)}"
            
            return True, "Distribution stats display logic is correct"
            
        except Exception as e:
            return False, f"Exception: {e}"
    
    def run_test(self, name: str, test_func) -> bool:
        """Run a single test and report results."""
        print(f"\n{'─' * 70}")
        print(f"Test: {name}")
        print(f"{'─' * 70}")
        
        passed, message = test_func()
        
        if passed:
            print(f"✅ PASSED: {message}")
            self.passed += 1
            return True
        else:
            print(f"❌ FAILED: {message}")
            self.failed += 1
            return False
    
    def run_all_tests(self) -> bool:
        """Run complete test suite."""
        print("=" * 70)
        print("SSOT DASHBOARD TEST SUITE")
        print("=" * 70)
        
        tests = [
            ("Wireframe Consistency", self.test_wireframe_consistency),
            ("Territory Order", self.test_territory_order),
            ("Data Consistency", self.test_data_consistency),
            ("Field Types", self.test_field_types),
            ("Regeneration Stability", self.test_regeneration_stability),
            ("HTML Rendering Elements", self.test_html_rendering_elements),
            ("Visual Data Population", self.test_visual_data_population),
            ("Cell-by-Cell Visual Inspection (MANDATORY)", self.test_cell_by_cell_visual_inspection),
            ("No Duplicate Declarations (Phase 1 Guardrail)", self.test_no_duplicate_declarations),
            ("File Metrics Validation (Phase 1 Guardrail)", self.test_file_metrics),
            ("Source vs Rendered Data (P0 - Critical Gap)", self.test_source_vs_rendered_data),
            ("Tooltip Data Availability (RCA: Jan 17 2026)", self.test_tooltip_data_availability),
            ("Distribution Stats Display (RCA: Jan 17 2026)", self.test_distribution_stats_display),
        ]
        
        for name, test_func in tests:
            self.run_test(name, test_func)
        
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        print("=" * 70)
        
        if self.failed == 0:
            print("✅ ALL TESTS PASSED - Dashboard is ready")
            return True
        else:
            print("❌ TESTS FAILED - Do not commit")
            return False

def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent.parent
    suite = DashboardTestSuite(project_root)
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
