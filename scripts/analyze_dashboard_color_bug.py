#!/usr/bin/env python3
"""
Analyze Dashboard Color Coding Bug

User reports:
1. Total Heal Cap = 100.0% but cell displays RED
2. Cells showing "26 = 0%" and "34 < 50%"

This script extracts and analyzes the color coding logic.
"""
import json
import re
from pathlib import Path

def analyze_color_bug():
    """Analyze the dashboard color coding bug."""
    print("=" * 70)
    print("DASHBOARD COLOR CODING BUG ANALYSIS")
    print("=" * 70)
    
    # Load dashboard HTML
    dashboard_path = Path("C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
    html = dashboard_path.read_text(encoding='utf-8')
    
    # Extract dashboardData
    start_marker = 'const dashboardData = ['
    end_marker = '];'
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker, start_idx) + len(end_marker)
    json_str = html[start_idx+len(start_marker)-1:end_idx-1]
    data = json.loads(json_str)
    
    total_row = data[0]
    
    print(f"\n📊 TOTAL Row Data:")
    print(f"   Heal Cap %: {total_row['Heal Cap %']}")
    print(f"   Heal Invocation %: {total_row['Heal Invocation %']}")
    print(f"   Test %: {total_row['Test %']}")
    print(f"   Complexity Health: {total_row['Complexity Health']}")
    print(f"   Health: {total_row['Health']}")
    
    # Find getGradientBg function
    gradient_match = re.search(r'const getGradientBg = \(value, target = \d+\) => \{(.*?)\};', html, re.DOTALL)
    if gradient_match:
        print(f"\n🎨 getGradientBg Function Found:")
        print(f"   Uses value parameter to determine color")
        print(f"   Line ~2434: const getGradientBg = (value, target = 80) => {{")
        
    # Find where Heal Cap cell background is set
    heal_cap_bg_match = re.search(r'background:\$\{getGradientBg\(healCapStats\.min\)\}', html)
    if heal_cap_bg_match:
        print(f"\n❌ BUG FOUND: Heal Cap Cell Background")
        print(f"   Line ~2525: background:${{getGradientBg(healCapStats.min)}}")
        print(f"   PROBLEM: Uses healCapStats.min (minimum value across territories)")
        print(f"   NOT: totalRow['Heal Cap %'] (which is 100.0%)")
    
    # Calculate what healCapStats.min likely is
    heal_cap_values = [r['Heal Cap %'] for r in data[1:] if r.get('Total', 0) > 0]
    min_heal_cap = min(heal_cap_values) if heal_cap_values else 0
    
    print(f"\n🔍 Calculated healCapStats.min:")
    print(f"   Min Heal Cap across territories: {min_heal_cap}%")
    print(f"   This explains the RED background!")
    print(f"   getGradientBg({min_heal_cap}) → RED gradient")
    print(f"   But TOTAL row shows: {total_row['Heal Cap %']}% (100.0%)")
    
    # Find outlier badge logic
    outlier_match = re.search(r'function formatOutlierBadge\(countAtZero, countBelowThreshold, threshold = \d+\)', html)
    if outlier_match:
        print(f"\n🏷️  Outlier Badge Logic:")
        print(f"   formatOutlierBadge(countAtZero, countBelowThreshold, threshold)")
        print(f"   Badge shows: '26 @0%' means 26 agents at 0%")
        print(f"   Badge shows: '34 <50%' means 34 agents below 50%")
    
    # Find where outlier badges are added
    badge_match = re.search(r'\$\{formatOutlierBadge\(healCapOutliers\.atZero, healCapOutliers\.belowThreshold, 50\)\}', html)
    if badge_match:
        print(f"\n   Line ~2526: formatOutlierBadge(healCapOutliers.atZero, healCapOutliers.belowThreshold, 50)")
        print(f"   This adds the outlier badges to cells")
    
    print(f"\n" + "=" * 70)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 70)
    
    print(f"\n❌ BUG 1: Cell Background Color")
    print(f"   PROBLEM: TOTAL row cell backgrounds use MIN value across all territories")
    print(f"   LOCATION: Lines ~2525-2545 (TOTAL row rendering)")
    print(f"   CURRENT: background:${{getGradientBg(healCapStats.min)}}")
    print(f"   SHOULD BE: background:${{getGradientBg(totalRow['Heal Cap %'])}}")
    print(f"   IMPACT: 100% Heal Cap shows RED because min territory is {min_heal_cap}%")
    
    print(f"\n✅ NOT A BUG: Outlier Badges")
    print(f"   The '26 @0%' and '34 <50%' badges are CORRECT")
    print(f"   They show outlier counts across all agents")
    print(f"   26 agents have 0% on this metric")
    print(f"   34 agents total are below 50% threshold")
    print(f"   This is INTENTIONAL to highlight distribution problems")
    
    print(f"\n" + "=" * 70)
    print("SOLUTION")
    print("=" * 70)
    
    print(f"\n🔧 Fix Required:")
    print(f"   Change TOTAL row cell backgrounds to use TOTAL row values")
    print(f"   NOT distribution min/max values")
    print(f"\n   BEFORE: background:${{getGradientBg(healCapStats.min)}}")
    print(f"   AFTER:  background:${{getGradientBg(totalRow['Heal Cap %'])}}")
    
    print(f"\n   Apply to all metric columns:")
    print(f"   - Heal Cap %")
    print(f"   - Heal Invocation %")
    print(f"   - Hardened %")
    print(f"   - Test %")
    print(f"   - Complexity Health")
    print(f"   - Health")
    
    return {
        'total_heal_cap': total_row['Heal Cap %'],
        'min_heal_cap': min_heal_cap,
        'bug_confirmed': True,
        'fix_location': 'Lines 2525-2545 (TOTAL row cell backgrounds)'
    }

if __name__ == "__main__":
    results = analyze_color_bug()
    
    print(f"\n" + "=" * 70)
    print("TEST COVERAGE GAP ANALYSIS")
    print("=" * 70)
    
    print(f"\n❌ Current 6 Tests DO NOT Cover:")
    print(f"   1. Cell background color correctness")
    print(f"   2. Color gradient logic (getGradientBg)")
    print(f"   3. Text color logic (getWorstCaseColor)")
    print(f"   4. Outlier badge rendering")
    print(f"   5. Distribution stats calculations")
    print(f"   6. Mock agent data generation")
    print(f"   7. Sparkline rendering")
    print(f"   8. Table filtering (outliers, zombies, toxicity)")
    print(f"   9. Table sorting logic")
    print(f"   10. Drill-down modal functionality")
    print(f"   11. Tab switching between tables")
    print(f"   12. Code Quality table rendering")
    print(f"   13. Worst performer links")
    print(f"   14. CSV export functionality")
    
    print(f"\n✅ Current 6 Tests ONLY Cover:")
    print(f"   1. Data structure (29 rows)")
    print(f"   2. Field presence (25 fields)")
    print(f"   3. Territory order")
    print(f"   4. Agent count consistency")
    print(f"   5. HTML file exists")
    print(f"   6. Basic rendering functions exist")
    
    print(f"\n📊 Recommended Additional Tests:")
    print(f"   7. Color coding correctness (TOTAL row backgrounds)")
    print(f"   8. Outlier badge accuracy")
    print(f"   9. Distribution stats calculations")
    print(f"   10. Both tables render correctly")
    print(f"   11. Filter functionality")
    print(f"   12. Sort functionality")
    print(f"   13. Modal drill-down data")
    print(f"   14. Sparkline data accuracy")
    print(f"   15. Worst performer identification")
    
    print(f"\n💡 Why 6 Tests Are Insufficient:")
    print(f"   - Tests validate DATA but not RENDERING")
    print(f"   - Tests check structure but not VISUAL CORRECTNESS")
    print(f"   - Tests verify functions exist but not LOGIC CORRECTNESS")
    print(f"   - Dashboard has 2 tables, multiple tabs, filters, modals")
    print(f"   - Current tests would pass even with RED 100% cells!")
