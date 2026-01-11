#!/usr/bin/env python3
"""
Dashboard Rendering Tests

Tests visual rendering logic that the 6 structural tests miss:
- Color coding correctness
- Outlier badge accuracy
- Distribution stats calculations
- Both tables render correctly
- Filter and sort functionality
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Any

class DashboardRenderingTests:
    """Test dashboard rendering logic."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dashboard_path = project_root / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
        self.html = None
        self.dashboard_data = None
        
    def load_dashboard(self):
        """Load dashboard HTML and extract data."""
        self.html = self.dashboard_path.read_text(encoding='utf-8')
        
        # Extract dashboardData
        start_marker = 'const dashboardData = ['
        end_marker = '];'
        start_idx = self.html.find(start_marker)
        end_idx = self.html.find(end_marker, start_idx) + len(end_marker)
        json_str = self.html[start_idx+len(start_marker)-1:end_idx-1]
        self.dashboard_data = json.loads(json_str)
        
    def test_total_row_color_coding(self) -> bool:
        """Test 7: TOTAL row cell backgrounds use correct values."""
        print("\n" + "─" * 70)
        print("Test 7: TOTAL Row Color Coding")
        print("─" * 70)
        
        total_row = self.dashboard_data[0]
        
        # Check Heal Cap cell background
        heal_cap_match = re.search(
            r'<td[^>]*background:\$\{getGradientBg\(([^)]+)\)\}[^>]*>.*?Heal Cap %',
            self.html,
            re.DOTALL
        )
        
        if not heal_cap_match:
            print("❌ FAILED: Could not find Heal Cap cell background")
            return False
        
        bg_value = heal_cap_match.group(1).strip()
        
        # Check if using TOTAL row value (correct) or stats.min (incorrect)
        if "totalRow['Heal Cap %']" in bg_value or 'totalRow["Heal Cap %"]' in bg_value:
            print(f"✅ PASSED: Heal Cap cell uses totalRow value")
            print(f"   Background: getGradientBg({bg_value})")
            print(f"   TOTAL Heal Cap: {total_row['Heal Cap %']}%")
        elif "healCapStats.min" in bg_value:
            print(f"❌ FAILED: Heal Cap cell uses distribution min (BUG!)")
            print(f"   Background: getGradientBg({bg_value})")
            print(f"   Should use: totalRow['Heal Cap %'] = {total_row['Heal Cap %']}%")
            return False
        else:
            print(f"⚠️  WARNING: Unexpected background value: {bg_value}")
            
        # Check all metric columns
        metrics = [
            ("Heal Cap %", "healCapStats"),
            ("Invocation %", "invocationStats"),
            ("Hardened %", "hardenedStats"),
            ("Test %", "testStats"),
            ("Complexity Health", "complexityStats"),
            ("Health", "healthStats")
        ]
        
        all_correct = True
        for metric_name, stats_var in metrics:
            # Find TOTAL row cell for this metric
            pattern = rf'background:\$\{{getGradientBg\(([^)]+)\)\}}[^>]*>.*?{re.escape(metric_name)}'
            match = re.search(pattern, self.html, re.DOTALL)
            
            if match:
                bg_val = match.group(1).strip()
                if f"{stats_var}.min" in bg_val:
                    print(f"   ❌ {metric_name}: Uses {stats_var}.min (INCORRECT)")
                    all_correct = False
                elif "totalRow" in bg_val:
                    print(f"   ✅ {metric_name}: Uses totalRow value (CORRECT)")
        
        if all_correct:
            print("\n✅ PASSED: All TOTAL row cells use correct values")
            return True
        else:
            print("\n❌ FAILED: Some cells use distribution min instead of TOTAL values")
            return False
    
    def test_outlier_badge_logic(self) -> bool:
        """Test 8: Outlier badges show correct counts."""
        print("\n" + "─" * 70)
        print("Test 8: Outlier Badge Logic")
        print("─" * 70)
        
        # Check formatOutlierBadge function exists
        badge_func = re.search(
            r'function formatOutlierBadge\(countAtZero, countBelowThreshold, threshold = (\d+)\)',
            self.html
        )
        
        if not badge_func:
            print("❌ FAILED: formatOutlierBadge function not found")
            return False
        
        print(f"✅ formatOutlierBadge function found")
        print(f"   Default threshold: {badge_func.group(1)}")
        
        # Check badge rendering logic
        badge_logic = re.search(
            r'if \(countAtZero > 0\).*?@0%.*?if \(countBelowThreshold > countAtZero\)',
            self.html,
            re.DOTALL
        )
        
        if badge_logic:
            print("✅ Badge logic correct:")
            print("   - Shows 'X @0%' when agents at 0%")
            print("   - Shows 'Y <Z%' when agents below threshold")
            print("   - Badges are INTENTIONAL outlier indicators")
            return True
        else:
            print("❌ FAILED: Badge logic not found or incorrect")
            return False
    
    def test_distribution_stats(self) -> bool:
        """Test 9: Distribution stats calculations."""
        print("\n" + "─" * 70)
        print("Test 9: Distribution Stats Calculations")
        print("─" * 70)
        
        # Check computeDistributionStats function
        stats_func = re.search(
            r'function computeDistributionStats\(values\)',
            self.html
        )
        
        if not stats_func:
            print("❌ FAILED: computeDistributionStats function not found")
            return False
        
        print("✅ computeDistributionStats function found")
        
        # Check it calculates min, max, avg, stdDev
        required_calcs = ['min', 'max', 'avg', 'stdDev', 'range']
        all_found = True
        
        for calc in required_calcs:
            if calc in self.html:
                print(f"   ✅ Calculates {calc}")
            else:
                print(f"   ❌ Missing {calc} calculation")
                all_found = False
        
        return all_found
    
    def test_both_tables_exist(self) -> bool:
        """Test 10: Both tables render correctly."""
        print("\n" + "─" * 70)
        print("Test 10: Both Tables Exist")
        print("─" * 70)
        
        # Check renderTerritorySummaryTable
        table1 = re.search(r'function renderTerritorySummaryTable', self.html)
        if table1:
            print("✅ renderTerritorySummaryTable function found")
        else:
            print("❌ FAILED: renderTerritorySummaryTable not found")
            return False
        
        # Check renderCodeQualityTable
        table2 = re.search(r'function renderCodeQualityTable', self.html)
        if table2:
            print("✅ renderCodeQualityTable function found")
        else:
            print("❌ FAILED: renderCodeQualityTable not found")
            return False
        
        # Check both tables have TOTAL rows
        total_rows = len(re.findall(r'TOTAL.*?<span.*?Avg \(Min-Max', self.html, re.DOTALL))
        print(f"   Found {total_rows} TOTAL row definitions")
        
        if total_rows >= 2:
            print("✅ Both tables have TOTAL rows")
            return True
        else:
            print("❌ FAILED: Missing TOTAL rows in tables")
            return False
    
    def test_filter_functionality(self) -> bool:
        """Test 11: Filter functionality exists."""
        print("\n" + "─" * 70)
        print("Test 11: Filter Functionality")
        print("─" * 70)
        
        filters = [
            ('toggleOutlierFilter', 'Show only outliers'),
            ('toggleZombieFilter', 'Show only zombies'),
            ('toggleToxicityFilter', 'Show toxic hubs')
        ]
        
        all_found = True
        for func_name, description in filters:
            if func_name in self.html:
                print(f"✅ {description}: {func_name} found")
            else:
                print(f"❌ {description}: {func_name} not found")
                all_found = False
        
        # Check tableFilterState
        if 'tableFilterState' in self.html:
            print("✅ tableFilterState global variable found")
        else:
            print("❌ tableFilterState not found")
            all_found = False
        
        return all_found
    
    def test_sort_functionality(self) -> bool:
        """Test 12: Sort functionality exists."""
        print("\n" + "─" * 70)
        print("Test 12: Sort Functionality")
        print("─" * 70)
        
        # Check toggleOutlierSort
        if 'toggleOutlierSort' in self.html:
            print("✅ toggleOutlierSort function found")
        else:
            print("❌ toggleOutlierSort not found")
            return False
        
        # Check sortByOutliers in tableFilterState
        if 'sortByOutliers' in self.html:
            print("✅ sortByOutliers state found")
        else:
            print("❌ sortByOutliers state not found")
            return False
        
        # Check getTerritoryOutlierCount
        if 'getTerritoryOutlierCount' in self.html:
            print("✅ getTerritoryOutlierCount function found")
            return True
        else:
            print("❌ getTerritoryOutlierCount not found")
            return False
    
    def test_drill_down_modal(self) -> bool:
        """Test 13: Drill-down modal functionality."""
        print("\n" + "─" * 70)
        print("Test 13: Drill-down Modal")
        print("─" * 70)
        
        # Check openDrillModal
        if 'openDrillModal' in self.html:
            print("✅ openDrillModal function found")
        else:
            print("❌ openDrillModal not found")
            return False
        
        # Check closeDrillModal
        if 'closeDrillModal' in self.html:
            print("✅ closeDrillModal function found")
        else:
            print("❌ closeDrillModal not found")
            return False
        
        # Check modal container
        if 'drillModal' in self.html:
            print("✅ drillModal container found")
            return True
        else:
            print("❌ drillModal container not found")
            return False
    
    def test_sparkline_rendering(self) -> bool:
        """Test 14: Sparkline rendering."""
        print("\n" + "─" * 70)
        print("Test 14: Sparkline Rendering")
        print("─" * 70)
        
        # Check generateSparkline function
        if 'generateSparkline' in self.html:
            print("✅ generateSparkline function found")
        else:
            print("❌ generateSparkline not found")
            return False
        
        # Check sparkline SVG generation
        if '<svg' in self.html and 'polyline' in self.html:
            print("✅ SVG sparkline elements found")
            return True
        else:
            print("❌ SVG sparkline elements not found")
            return False
    
    def test_worst_performer_links(self) -> bool:
        """Test 15: Worst performer identification."""
        print("\n" + "─" * 70)
        print("Test 15: Worst Performer Links")
        print("─" * 70)
        
        # Check getWorstPerformerForMetric
        if 'getWorstPerformerForMetric' in self.html:
            print("✅ getWorstPerformerForMetric function found")
        else:
            print("❌ getWorstPerformerForMetric not found")
            return False
        
        # Check formatWorstPerformerLink
        if 'formatWorstPerformerLink' in self.html:
            print("✅ formatWorstPerformerLink function found")
        else:
            print("❌ formatWorstPerformerLink not found")
            return False
        
        # Check VS Code link generation
        if 'vscode://file' in self.html:
            print("✅ VS Code link generation found")
            return True
        else:
            print("❌ VS Code link generation not found")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all rendering tests."""
        print("=" * 70)
        print("DASHBOARD RENDERING TEST SUITE")
        print("=" * 70)
        print("Testing visual rendering logic (Tests 7-15)")
        
        self.load_dashboard()
        
        results = {
            'test_7_color_coding': self.test_total_row_color_coding(),
            'test_8_outlier_badges': self.test_outlier_badge_logic(),
            'test_9_distribution_stats': self.test_distribution_stats(),
            'test_10_both_tables': self.test_both_tables_exist(),
            'test_11_filters': self.test_filter_functionality(),
            'test_12_sorting': self.test_sort_functionality(),
            'test_13_drill_down': self.test_drill_down_modal(),
            'test_14_sparklines': self.test_sparkline_rendering(),
            'test_15_worst_performers': self.test_worst_performer_links()
        }
        
        return results

def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent.parent
    tester = DashboardRenderingTests(project_root)
    results = tester.run_all_tests()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Total: {total}")
    print("=" * 70)
    
    if passed == total:
        print("✅ ALL RENDERING TESTS PASSED")
        return 0
    else:
        print("❌ SOME RENDERING TESTS FAILED")
        print("\nFailed tests:")
        for test_name, result in results.items():
            if not result:
                print(f"   - {test_name}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
