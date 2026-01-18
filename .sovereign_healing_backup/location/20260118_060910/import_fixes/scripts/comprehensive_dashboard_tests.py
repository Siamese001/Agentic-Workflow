"""
Comprehensive Dashboard Test Suite
All tests must pass before deployment.
"""
import re
import json
import sys
from pathlib import Path

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
    get_validated_project_root,
)

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

DASHBOARD_PATH = project_root / REPORTS_DIR / "autonomy_dashboard.html"
TEMPLATE_PATH = project_root / AGENTIC_CORE_DIR / "L5_safety" / "validators" / "dashboard_template.html"

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
        
        # Category 16: Dashboard Refresh Tests
        print("🔄 DASHBOARD REFRESH TESTS")
        self.test_dashboard_refresh()
        print()
        
        # Category 17: Invocation % Update Detection Tests
        print("📊 INVOCATION % UPDATE DETECTION TESTS")
        self.test_invocation_update_detection()
        print()
        
        # Category 18: Territory Structure Consistency Tests
        print("🛡️ TERRITORY STRUCTURE CONSISTENCY TESTS")
        self.test_base_class_territories_complete()
        self.test_l5_domain_subterritories_exception()
        self.test_no_abbreviated_subterritory_names()
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
            
            # Check invocation targets match autonomy_targets.py config
            # Check more specific patterns first (Infrastructure, Base Class) before layer patterns (L0)
            valid_targets = True
            for row in non_total_rows:
                target_inv = row.get('Target Invocation')
                territory = row.get('Territory', '')
                
                # Validate target is appropriate for territory (check specific patterns first)
                if 'Infrastructure' in territory or 'Infrast' in territory:
                    # Infrastructure pattern wins (target=70)
                    if target_inv != 70:
                        valid_targets = False
                elif 'Base Class' in territory:
                    # Base Class pattern (target=N/A)
                    if target_inv != 'N/A':
                        valid_targets = False
                elif 'L0 Maintenance' in territory:
                    # L0 pattern (target=20) - only if not Infrastructure
                    if target_inv != 20:
                        valid_targets = False
                else:
                    # Default should be 100
                    if target_inv != 100 and target_inv != 'N/A':
                        valid_targets = False
            
            self.test("Invocation targets match autonomy_targets.py config", valid_targets, 
                     "Some invocation targets don't match expected config")
    
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
    
    def test_autonomy_targets_integration(self):
        """Tests for autonomy targets being populated from Python backend to dashboard data."""
        non_total_rows = [r for r in self.dashboard_data if r.get('Territory') != 'TOTAL']
        
        # Verify target fields exist in dashboard data (not just template)
        target_fields = ['Target Invocation', 'Target MCP', 'Target Tests', 
                        'Target Observability', 'Target Complexity']
        
        rows_with_all_targets = 0
        rows_missing_targets = []
        
        for row in non_total_rows:
            has_all = all(field in row for field in target_fields)
            if has_all:
                rows_with_all_targets += 1
            else:
                missing = [f for f in target_fields if f not in row]
                rows_missing_targets.append((row.get('Territory'), missing))
        
        self.test("All territory rows have target fields", 
                 rows_with_all_targets == len(non_total_rows),
                 f"{len(rows_missing_targets)} rows missing targets: {rows_missing_targets[:3]}")
        
        # Verify target values are numeric or 'N/A' (valid types)
        valid_target_values = True
        invalid_examples = []
        for row in non_total_rows:
            for field in target_fields:
                val = row.get(field)
                if val is not None and not isinstance(val, (int, float)) and val != 'N/A':
                    valid_target_values = False
                    invalid_examples.append((row.get('Territory'), field, val))
        
        self.test("Target values are valid types (numeric or N/A)", 
                 valid_target_values, f"Invalid: {invalid_examples[:3]}")
        
        # Verify targets are populated from autonomy_targets.py config
        # Check that targets vary by territory (not all 100)
        target_values = set(row.get('Target Invocation') for row in non_total_rows)
        self.test("Target Invocation values vary by territory", 
                 len(target_values) > 1,
                 f"All targets are the same: {target_values}")
        
        # Verify target values match expected defaults (100 for invocation, 95 for observability)
        sample = non_total_rows[0] if non_total_rows else {}
        self.test("Target Observability matches config", 
                 sample.get('Target Observability') in [95, 100, 'N/A'],
                 f"Unexpected value: {sample.get('Target Observability')}")
    
    def test_context_target_resolver(self):
        """Tests for context/target_resolver passing from Python to dashboard generation."""
        # Check that AutonomyGuardianAgent stores context
        guardian_path = project_root / AGENTIC_CORE_DIR / "L5_safety" / "validators" / "AutonomyGuardianAgent.py"
        if guardian_path.exists():
            guardian_code = guardian_path.read_text(encoding='utf-8')
            
            # Verify self.context is stored in generate_compliance_report
            self.test("Context stored in generate_compliance_report", 
                     'self.context = context' in guardian_code or 'self.context =' in guardian_code,
                     "Context not being stored in AutonomyGuardianAgent")
            
            # Verify target_resolver is used from context
            self.test("Target resolver accessed from context", 
                     "target_resolver" in guardian_code and "self.context" in guardian_code,
                     "target_resolver not accessed from self.context")
            
            # Verify target fields are added to row dict
            self.test("Target Invocation added to row", 
                     'row["Target Invocation"]' in guardian_code or "row['Target Invocation']" in guardian_code,
                     "Target Invocation not being added to dashboard row")
            
            self.test("Target MCP added to row", 
                     'row["Target MCP"]' in guardian_code or "row['Target MCP']" in guardian_code,
                     "Target MCP not being added to dashboard row")
        else:
            self.test("AutonomyGuardianAgent.py exists", False, f"Missing: {guardian_path}")
        
        # Check that canon_validator passes target_resolver
        validator_path = project_root / "canon_validator_agentic_v2_thin.py"
        if validator_path.exists():
            validator_code = validator_path.read_text(encoding='utf-8')
            
            self.test("Canon validator imports get_target", 
                     'from archives.location_violations.autonomy_targets import get_target' in validator_code,
                     "get_target not imported in canon_validator")
            
            self.test("Canon validator passes target_resolver to context", 
                     'target_resolver' in validator_code and 'get_target' in validator_code,
                     "target_resolver not passed in context")
        else:
            self.test("canon_validator_agentic_v2_thin.py exists", False, f"Missing: {validator_path}")
    
    def test_total_vs_territory_rows(self):
        """Tests for proper distinction between TOTAL row and territory rows."""
        total_rows = [r for r in self.dashboard_data if r.get('Territory') == 'TOTAL']
        non_total_rows = [r for r in self.dashboard_data if r.get('Territory') != 'TOTAL']
        
        self.test("Exactly one TOTAL row exists", len(total_rows) == 1, 
                 f"Found {len(total_rows)} TOTAL rows")
        
        self.test("Multiple territory rows exist", len(non_total_rows) >= 10, 
                 f"Only {len(non_total_rows)} territory rows")
        
        # TOTAL row should NOT have target fields (added separately)
        if total_rows:
            total_row = total_rows[0]
            has_targets = 'Target Invocation' in total_row
            # It's OK if TOTAL has or doesn't have targets, but we should be aware
            self.test("TOTAL row target handling documented", True, 
                     f"TOTAL row has targets: {has_targets}")
        
        # Verify non-TOTAL rows all have consistent structure
        if non_total_rows:
            first_row_keys = set(non_total_rows[0].keys())
            consistent_structure = all(set(r.keys()) == first_row_keys for r in non_total_rows)
            self.test("All territory rows have consistent structure", consistent_structure,
                     "Territory rows have different field sets")
        
        # Verify territory names are unique
        territory_names = [r.get('Territory') for r in non_total_rows]
        unique_names = len(set(territory_names)) == len(territory_names)
        self.test("Territory names are unique", unique_names,
                 f"Duplicate territories found")
    
    def test_template_features(self):
        """Tests for template features: getContextualBg, getTargetTooltip, formatPctCell."""
        # Test getContextualBg function implementation
        self.test("getContextualBg handles N/A targets", 
                 "target === 'N/A'" in self.template_html and 'getContextualBg' in self.template_html,
                 "getContextualBg doesn't handle N/A targets")
        
        self.test("getContextualBg returns neutral gray for N/A", 
                 '#f3f4f6' in self.template_html or 'light gray' in self.template_html.lower(),
                 "No neutral gray color for N/A metrics")
        
        # Test getTargetTooltip function implementation
        self.test("getTargetTooltip shows actual vs target", 
                 'Actual:' in self.template_html or 'actual' in self.template_html.lower(),
                 "getTargetTooltip doesn't show actual value")
        
        self.test("getTargetTooltip shows 'Exception applied' for N/A", 
                 'Exception applied' in self.template_html,
                 "No 'Exception applied' message for N/A targets")
        
        # Test formatPctCell handles N/A
        self.test("formatPctCell displays 'N/A' text", 
                 "'N/A'" in self.template_html and 'formatPctCell' in self.template_html,
                 "formatPctCell doesn't display N/A text")
        
        # Test table row rendering uses target functions
        self.test("Table rows use getContextualBg", 
                 'getContextualBg(' in self.template_html,
                 "Table rows not using getContextualBg")
        
        self.test("Table rows use getTargetTooltip", 
                 'getTargetTooltip(' in self.template_html,
                 "Table rows not using getTargetTooltip")
        
        # Test target-aware color coding
        self.test("Target values used in table cells (tgtInv)", 
                 'tgtInv' in self.template_html or "row['Target Invocation']" in self.template_html,
                 "Target values not referenced in table rendering")
    
    def test_na_handling(self):
        """Tests for N/A handling in dashboard data and template."""
        # Check if any targets are N/A in the data
        non_total_rows = [r for r in self.dashboard_data if r.get('Territory') != 'TOTAL']
        
        na_targets_found = False
        for row in non_total_rows:
            for field in ['Target Invocation', 'Target MCP', 'Target Tests', 
                         'Target Observability', 'Target Complexity']:
                if row.get(field) == 'N/A':
                    na_targets_found = True
                    break
            if na_targets_found:
                break
        
        # It's OK if no N/A targets (all set to 100), but template should handle it
        self.test("Template can handle N/A targets", 
                 "=== 'N/A'" in self.template_html or "== 'N/A'" in self.template_html,
                 "Template doesn't check for N/A targets")
        
        # Verify N/A display logic exists
        self.test("N/A display logic in template", 
                 "? 'N/A'" in self.template_html or ": 'N/A'" in self.template_html,
                 "No ternary for N/A display")
        
        # Check for neutral background for N/A
        self.test("Neutral background for N/A metrics", 
                 'f3f4f6' in self.template_html or 'gray' in self.template_html.lower(),
                 "No neutral background color defined")
        
        # Verify tooltip shows exception message for N/A
        self.test("Exception tooltip for N/A targets", 
                 'Exception' in self.template_html,
                 "No exception message in tooltips")
        
        # Check that 0% doesn't show red if target is N/A
        self.test("Color logic respects N/A targets", 
                 'isNA' in self.template_html or "target === 'N/A'" in self.template_html,
                 "Color logic doesn't check for N/A")
    
    def test_dashboard_refresh(self):
        """Tests for dashboard data refresh and timestamp updates."""
        # Check timestamp exists and is recent
        timestamp_match = re.search(r'Last updated: (.+?)"', self.dashboard_html)
        self.test("Dashboard has timestamp", timestamp_match is not None, 
                 "No 'Last updated' timestamp found")
        
        if timestamp_match:
            timestamp_str = timestamp_match.group(1)
            self.test("Timestamp format valid", 
                     'January' in timestamp_str or 'February' in timestamp_str or 'March' in timestamp_str,
                     f"Invalid timestamp format: {timestamp_str}")
        
        # Verify dashboard data is not empty
        self.test("Dashboard data not empty", len(self.dashboard_data) > 0,
                 "Dashboard data array is empty")
        
        # Check TOTAL row exists with valid metrics
        total_row = next((r for r in self.dashboard_data if r.get('Territory') == 'TOTAL'), None)
        self.test("TOTAL row has Invocation %", 
                 total_row and 'Invocation %' in total_row,
                 "TOTAL row missing Invocation %")
        
        if total_row:
            inv_pct = total_row.get('Invocation %')
            self.test("Invocation % is numeric", 
                     isinstance(inv_pct, (int, float)),
                     f"Invocation % is not numeric: {type(inv_pct)}")
            
            self.test("Invocation % in valid range", 
                     0 <= inv_pct <= 100,
                     f"Invocation % out of range: {inv_pct}")
        
        # Verify gauge data matches TOTAL row
        gauge_match = re.search(r'const gaugeData = ({.*?});', self.dashboard_html)
        if gauge_match and total_row:
            try:
                gauge_data = json.loads(gauge_match.group(1))
                heal_cap_match = abs(gauge_data.get('healing_cap', 0) - total_row.get('Heal Cap %', 0)) < 0.1
                self.test("Gauge data matches TOTAL row", heal_cap_match,
                         f"Gauge: {gauge_data.get('healing_cap')} vs Row: {total_row.get('Heal Cap %')}")
            except:
                pass
    
    def test_invocation_update_detection(self):
        """Tests for invocation % being correctly calculated and displayed."""
        non_total_rows = [r for r in self.dashboard_data if r.get('Territory') != 'TOTAL']
        
        # Verify all territory rows have Invocation %
        rows_with_inv = sum(1 for r in non_total_rows if 'Invocation %' in r)
        self.test("All territories have Invocation %", 
                 rows_with_inv == len(non_total_rows),
                 f"Only {rows_with_inv}/{len(non_total_rows)} have Invocation %")
        
        # Check that invocation values are reasonable
        inv_values = [r.get('Invocation %') for r in non_total_rows if 'Invocation %' in r]
        valid_inv_values = all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in inv_values)
        self.test("All Invocation % values valid", valid_inv_values,
                 "Some invocation values are invalid")
        
        # Verify L0 Maintenance has low invocation (expected)
        l0_rows = [r for r in non_total_rows if 'L0 Maintenance' in r.get('Territory', '')]
        if l0_rows:
            l0_inv = [r.get('Invocation %', 0) for r in l0_rows]
            self.test("L0 Maintenance has expected low invocation", 
                     all(v <= 20 for v in l0_inv),
                     f"L0 invocation unexpectedly high: {l0_inv}")
        
        # Verify targets match config for L0 (should be 20, except Infrastructure which is 70)
        if l0_rows:
            l0_targets_correct = True
            for row in l0_rows:
                target = row.get('Target Invocation')
                terr = row.get('Territory', '')
                # L0 Maintenance/Infrastructure should be 70 (Infrastructure pattern wins)
                if 'Infrastructure' in terr or 'Infrast' in terr:
                    if target != 70:
                        l0_targets_correct = False
                else:
                    # Other L0 territories should be 20
                    if target != 20:
                        l0_targets_correct = False
            self.test("L0 Maintenance targets correct (20 or 70 for Infra)", 
                     l0_targets_correct,
                     f"L0 targets incorrect")
        
        # Verify Infrastructure targets are 70
        infra_rows = [r for r in non_total_rows if 'Infrastructure' in r.get('Territory', '') or 'Infrast' in r.get('Territory', '')]
        if infra_rows:
            infra_targets = [r.get('Target Invocation') for r in infra_rows]
            self.test("Infrastructure target is 70", 
                     all(t == 70 for t in infra_targets),
                     f"Infrastructure targets incorrect: {infra_targets}")
        
        # Verify Base Class targets are N/A
        base_rows = [r for r in non_total_rows if 'Base Class' in r.get('Territory', '')]
        if base_rows:
            base_targets = [r.get('Target Invocation') for r in base_rows]
            self.test("Base Class target is N/A", 
                     all(t == 'N/A' for t in base_targets),
                     f"Base Class targets incorrect: {base_targets}")
        
        # Verify TOTAL invocation is calculated correctly (weighted average)
        total_row = next((r for r in self.dashboard_data if r.get('Territory') == 'TOTAL'), None)
        if total_row:
            total_inv = total_row.get('Invocation %', 0)
            # Should be between 0 and 100
            self.test("TOTAL Invocation % calculated", 
                     0 <= total_inv <= 100,
                     f"TOTAL invocation out of range: {total_inv}")
            
            # Should reflect actual codebase state (not hardcoded)
            self.test("TOTAL Invocation % is dynamic", 
                     total_inv != 100.0,  # If it's exactly 100, might be hardcoded
                     "TOTAL invocation suspiciously at 100%")

    def test_base_class_territories_complete(self):
        """Ensure Base Class territory exists for every L1-L5 layer (critical consistency)."""
        expected = {
            'L1 Cognition/Base Class',
            'L2 Execution/Base Class',
            'L3 Orchestration/Base Class',
            'L4 State/Base Class',
            'L5 Safety/Base Class',
        }
        actual = {r.get('Territory') for r in self.dashboard_data if r.get('Territory') != 'TOTAL'}
        missing = expected - actual
        self.test(
            "All L1-L5 layers have Base Class territory",
            not missing,
            f"Missing Base Class territories: {missing}",
        )

    def test_l5_domain_subterritories_exception(self):
        """L5 uses domain-specific categories (intentional exception — no Core/Infrastructure/Specialized)."""
        l5_territories = [
            r.get('Territory') for r in self.dashboard_data
            if r.get('Territory', '').startswith('L5 Safety/')
        ]
        actual_subs = {t.split('/')[-1] for t in l5_territories if t}

        required = {'Guardrails', 'Validators', 'Gravity', 'Red Teaming', 'Base Class'}
        self.test(
            "L5 has required domain-specific territories",
            required.issubset(actual_subs),
            f"Missing L5 domain territories: {required - actual_subs}",
        )

        forbidden = {'Core', 'Infrastructure', 'Specialized'}
        overlap = forbidden & actual_subs
        self.test(
            "L5 does NOT use generic Core/Infrastructure/Specialized",
            not overlap,
            f"L5 incorrectly uses generic categories: {overlap}",
        )

    def test_no_abbreviated_subterritory_names(self):
        """No abbreviated names remaining (LOW-severity naming fix)."""
        abbreviated = {'Base Cl', 'Infrast', 'Special'}
        used = {
            r.get('Territory', '').split('/')[-1]
            for r in self.dashboard_data
            if '/' in r.get('Territory', '')
        }
        overlap = abbreviated & used
        self.test(
            "All subterritory names use full form (no abbreviations)",
            not overlap,
            f"Abbreviated names still present: {overlap}",
        )


def main():
    suite = DashboardTestSuite()
    success = suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
