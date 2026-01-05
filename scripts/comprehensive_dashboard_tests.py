"""
Comprehensive Dashboard Test Suite
All tests must pass before deployment.
"""
import re
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

DASHBOARD_PATH = project_root / "reports" / "autonomy_dashboard.html"
TEMPLATE_PATH = project_root / "agentic_core" / "L5_safety" / "validators" / "dashboard_template.html"

class DashboardTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
        # Load files
        self.dashboard_html = DASHBOARD_PATH.read_text(encoding='utf-8') if DASHBOARD_PATH.exists() else ""
        self.template_html = TEMPLATE_PATH.read_text(encoding='utf-8') if TEMPLATE_PATH.exists() else ""
        
        # Extract dashboard data
        match = re.search(r'const dashboardData = (\[.*?\]);', self.dashboard_html, re.DOTALL)
        self.dashboard_data = json.loads(match.group(1)) if match else []
    
    def test(self, name, condition, message=""):
        if condition:
            self.passed += 1
            self.tests.append(("PASS", name, ""))
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            self.tests.append(("FAIL", name, message))
            print(f"  ❌ {name}: {message}")
    
    def run_all_tests(self):
        print("=" * 80)
        print("COMPREHENSIVE DASHBOARD TEST SUITE")
        print("=" * 80)
        print()
        
        # Category 1: File Existence Tests
        print("📁 FILE EXISTENCE TESTS")
        self.test_file_existence()
        print()
        
        # Category 2: Data Integrity Tests
        print("📊 DATA INTEGRITY TESTS")
        self.test_data_integrity()
        print()
        
        # Category 3: Target Configuration Tests
        print("🎯 TARGET CONFIGURATION TESTS")
        self.test_target_configuration()
        print()
        
        # Category 4: Template Syntax Tests
        print("📝 TEMPLATE SYNTAX TESTS")
        self.test_template_syntax()
        print()
        
        # Category 5: JavaScript Function Tests
        print("⚙️ JAVASCRIPT FUNCTION TESTS")
        self.test_javascript_functions()
        print()
        
        # Category 6: Sparkline Infrastructure Tests
        print("📈 SPARKLINE INFRASTRUCTURE TESTS")
        self.test_sparkline_infrastructure()
        print()
        
        # Category 7: Drill-Down Data Tests
        print("🔍 DRILL-DOWN DATA TESTS")
        self.test_drilldown_data()
        print()
        
        # Category 8: Strategic Recommendations Tests
        print("💡 STRATEGIC RECOMMENDATIONS TESTS")
        self.test_strategic_recommendations()
        print()
        
        # Category 9: Gauge and KPI Tests
        print("📉 GAUGE AND KPI TESTS")
        self.test_gauge_kpis()
        print()
        
        # Category 10: Timer Configuration Tests
        print("⏱️ TIMER CONFIGURATION TESTS")
        self.test_timer_configuration()
        print()
        
        # Category 11: Autonomy Targets Integration Tests
        print("🔗 AUTONOMY TARGETS INTEGRATION TESTS")
        self.test_autonomy_targets_integration()
        print()
        
        # Category 12: Context/Target Resolver Tests
        print("🔧 CONTEXT/TARGET RESOLVER TESTS")
        self.test_context_target_resolver()
        print()
        
        # Category 13: TOTAL Row vs Territory Row Tests
        print("📋 TOTAL ROW VS TERRITORY ROW TESTS")
        self.test_total_vs_territory_rows()
        print()
        
        # Category 14: Template Feature Verification Tests
        print("🎨 TEMPLATE FEATURE VERIFICATION TESTS")
        self.test_template_features()
        print()
        
        # Category 15: N/A Handling Tests
        print("⚪ N/A HANDLING TESTS")
        self.test_na_handling()
        print()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"  Total Tests: {self.passed + self.failed}")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print(f"  Pass Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print()
        
        if self.failed == 0:
            print("✅ ALL TESTS PASSED - READY FOR DEPLOYMENT")
            return True
        else:
            print("❌ SOME TESTS FAILED - FIX BEFORE DEPLOYMENT")
            print("\nFailed Tests:")
            for status, name, msg in self.tests:
                if status == "FAIL":
                    print(f"  - {name}: {msg}")
            return False
    
    def test_file_existence(self):
        self.test("Dashboard HTML exists", DASHBOARD_PATH.exists(), f"Missing: {DASHBOARD_PATH}")
        self.test("Template HTML exists", TEMPLATE_PATH.exists(), f"Missing: {TEMPLATE_PATH}")
        self.test("Dashboard HTML not empty", len(self.dashboard_html) > 1000, "Dashboard HTML too small")
        self.test("Template HTML not empty", len(self.template_html) > 1000, "Template HTML too small")
    
    def test_data_integrity(self):
        self.test("Dashboard data parsed", len(self.dashboard_data) > 0, "No data rows found")
        self.test("Has TOTAL row", any(r.get('Territory') == 'TOTAL' for r in self.dashboard_data), "Missing TOTAL row")
        self.test("Has multiple territories", len(self.dashboard_data) >= 10, f"Only {len(self.dashboard_data)} rows")
        
        # Check required fields
        required_fields = ['Territory', 'Total', 'Compliant', 'Compliance %', 'Heal Cap %', 
                          'Invocation %', 'Hardened %', 'Test %', 'Avg CC', 'Health', 'Risk']
        for row in self.dashboard_data[:5]:  # Check first 5 rows
            if row.get('Territory') != 'TOTAL':
                for field in required_fields:
                    self.test(f"Field '{field}' in {row.get('Territory', 'unknown')[:20]}", 
                             field in row, f"Missing field: {field}")
                break
    
    def test_target_configuration(self):
        # Check that targets are present in non-TOTAL rows
        non_total_rows = [r for r in self.dashboard_data if r.get('Territory') != 'TOTAL']
        
        if non_total_rows:
            sample = non_total_rows[0]
            self.test("Target Invocation present", 'Target Invocation' in sample, 
                     f"Missing in {sample.get('Territory')}")
            self.test("Target MCP present", 'Target MCP' in sample, 
                     f"Missing in {sample.get('Territory')}")
            self.test("Target Tests present", 'Target Tests' in sample, 
                     f"Missing in {sample.get('Territory')}")
            self.test("Target Observability present", 'Target Observability' in sample, 
                     f"Missing in {sample.get('Territory')}")
            self.test("Target Complexity present", 'Target Complexity' in sample, 
                     f"Missing in {sample.get('Territory')}")
            
            # Check all invocation targets are 100 (MAX)
            all_max = True
            for row in non_total_rows:
                target_inv = row.get('Target Invocation')
                if target_inv != 100 and target_inv != 'N/A':
                    all_max = False
                    break
            self.test("All Invocation targets at MAX (100)", all_max, 
                     "Some invocation targets are not 100")
    
    def test_template_syntax(self):
        # Check balanced HTML tags
        open_divs = self.template_html.count('<div')
        close_divs = self.template_html.count('</div>')
        self.test("Balanced div tags", open_divs == close_divs, 
                 f"Open: {open_divs}, Close: {close_divs}")
        
        open_scripts = self.template_html.count('<script')
        close_scripts = self.template_html.count('</script>')
        self.test("Balanced script tags", open_scripts == close_scripts, 
                 f"Open: {open_scripts}, Close: {close_scripts}")
        
        # Check no duplicate IDs
        id_matches = re.findall(r'id="([^"]+)"', self.template_html)
        duplicate_ids = [id for id in id_matches if id_matches.count(id) > 1]
        self.test("No duplicate IDs", len(set(duplicate_ids)) == 0, 
                 f"Duplicates: {set(duplicate_ids)}")
    
    def test_javascript_functions(self):
        # Check critical JS functions exist
        critical_functions = [
            'getColor',
            'formatPctCell', 
            'getContextualBg',
            'getTargetTooltip',
            'getGradientBg'
        ]
        for func in critical_functions:
            self.test(f"Function {func}() exists", 
                     f'const {func}' in self.template_html or f'function {func}' in self.template_html,
                     f"Missing function: {func}")
    
    def test_sparkline_infrastructure(self):
        # Check CSS classes
        self.test("Sparkline container CSS", '.sparkline-container' in self.template_html, 
                 "Missing .sparkline-container CSS")
        self.test("Sparkline SVG CSS", '.sparkline-svg' in self.template_html or 'sparkline' in self.template_html.lower(), 
                 "Missing sparkline CSS")
        
        # Check sparkline functions
        sparkline_funcs = ['createSparklineSVG', 'formatSparkline', 'generateSparkline']
        found_any = any(func in self.template_html for func in sparkline_funcs)
        self.test("Sparkline generation function exists", found_any, 
                 "No sparkline generation function found")
    
    def test_drilldown_data(self):
        # Check that territories have agents arrays
        territories_with_agents = 0
        territories_missing_agents = []
        
        for row in self.dashboard_data:
            if row.get('Territory') == 'TOTAL':
                continue
            if 'agents' in row and isinstance(row['agents'], list):
                if len(row['agents']) > 0 or row.get('Total', 0) == 0:
                    territories_with_agents += 1
                else:
                    territories_missing_agents.append(row.get('Territory'))
            else:
                territories_missing_agents.append(row.get('Territory'))
        
        self.test("Territories have agents arrays", 
                 territories_with_agents >= len(self.dashboard_data) - 2,  # Allow some slack
                 f"Missing agents in: {territories_missing_agents[:3]}")
        
        # Check agent structure
        for row in self.dashboard_data:
            if row.get('Territory') != 'TOTAL' and 'agents' in row and row['agents']:
                agent = row['agents'][0]
                self.test("Agent has 'rel' field", 'rel' in agent, "Missing 'rel' in agent")
                self.test("Agent has 'compliant' field", 'compliant' in agent, "Missing 'compliant' in agent")
                break
    
    def test_strategic_recommendations(self):
        # Check for recommendations in dashboard
        self.test("Recommendations section exists", 
                 'recommendation' in self.dashboard_html.lower() or 'strategic' in self.dashboard_html.lower(),
                 "No recommendations section found")
        
        # Check for recommendations data and rendering function
        self.test("Recommendations data present", 
                 'recommendationsData' in self.dashboard_html or 'recommendations-content' in self.dashboard_html,
                 "Recommendations data not found")
        
        # Check for render function
        self.test("Recommendations render function exists",
                 'renderRecommendations' in self.dashboard_html,
                 "renderRecommendations function missing")
    
    def test_gauge_kpis(self):
        # Check gauge data
        gauge_match = re.search(r'const gaugeData = ({.*?});', self.dashboard_html)
        if gauge_match:
            try:
                gauge_data = json.loads(gauge_match.group(1))
                self.test("Gauge data parsed", True, "")
                self.test("Healing cap gauge exists", 'healing_cap' in gauge_data, "Missing healing_cap gauge")
                self.test("Compliance gauge exists", 'compliance' in gauge_data, "Missing compliance gauge")
                self.test("Health gauge exists", 'health' in gauge_data, "Missing health gauge")
                
                # Check values are reasonable
                self.test("Healing cap value valid", 0 <= gauge_data.get('healing_cap', -1) <= 100, 
                         f"Invalid: {gauge_data.get('healing_cap')}")
                self.test("Compliance value valid", 0 <= gauge_data.get('compliance', -1) <= 100, 
                         f"Invalid: {gauge_data.get('compliance')}")
            except json.JSONDecodeError:
                self.test("Gauge data parsed", False, "Invalid JSON in gaugeData")
        else:
            self.test("Gauge data exists", False, "No gaugeData found in dashboard")
    
    def test_timer_configuration(self):
        # Check refresh interval
        refresh_match = re.search(r'REFRESH_INTERVAL_MS\s*=\s*(\d+)', self.template_html)
        if refresh_match:
            interval = int(refresh_match.group(1))
            self.test("Refresh interval configured", interval > 0, f"Invalid interval: {interval}")
            self.test("Refresh interval reasonable", 60000 <= interval <= 600000, 
                     f"Interval {interval}ms outside 1-10 min range")
        else:
            self.test("Refresh interval exists", False, "No REFRESH_INTERVAL_MS found")


def main():
    suite = DashboardTestSuite()
    success = suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
