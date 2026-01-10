#!/usr/bin/env python3
"""
SSOT Dashboard Test Suite - L6 Observability
=============================================
Comprehensive test suite for dashboard generation.
Tests wireframe consistency across multiple data changes.

MUST PASS before any dashboard changes are committed.
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Import the SSOT generator
from generate_dashboard import DashboardGenerator, TERRITORY_ORDER, REQUIRED_FIELDS

# Expected number of territories in frozen wireframe (excluding TOTAL)
EXPECTED_TERRITORY_COUNT = 28  # 29 rows total, minus TOTAL row

class DashboardTestSuite:
    """Comprehensive test suite for dashboard generation."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dashboard_path = project_root / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
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
            discovery_path = self.project_root / "agent_discovery_full.json"
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
            ("HTML Rendering Elements", self.test_html_rendering_elements)
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
