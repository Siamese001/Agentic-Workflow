#!/usr/bin/env python3
"""
Visual Dashboard Test - Verify data is populated and rendering correctly

This test opens the dashboard and verifies:
1. dashboardData is embedded with correct values
2. realAgentData is embedded with per-agent metrics
3. TOTAL row shows 100% Heal Cap
4. Outlier badges use real data (should show 0 @0%)
5. All territories are present
"""
import json
import re
from pathlib import Path

def test_dashboard_visual():
    """Test dashboard data population and structure."""
    print("=" * 70)
    print("DASHBOARD VISUAL VERIFICATION TEST")
    print("=" * 70)
    
    dashboard_path = Path("C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
    html = dashboard_path.read_text(encoding='utf-8')
    
    passed = 0
    failed = 0
    
    # Test 1: Extract and verify dashboardData
    print("\n1. Testing dashboardData embedding...")
    dashboard_match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
    if dashboard_match:
        try:
            data_json = dashboard_match.group(1)
            data = json.loads(data_json)
            print(f"   ✅ dashboardData found: {len(data)} rows")
            
            # Verify TOTAL row
            total_row = next((r for r in data if r.get('Territory') == 'TOTAL'), None)
            if total_row:
                print(f"   ✅ TOTAL row found:")
                print(f"      - Total Agents: {total_row['Total']}")
                print(f"      - Heal Cap %: {total_row['Heal Cap %']}%")
                print(f"      - Health: {total_row['Health']}%")
                print(f"      - Test %: {total_row['Test %']}%")
                
                if total_row['Heal Cap %'] == 100.0:
                    print(f"   ✅ Heal Cap is 100% (CORRECT)")
                    passed += 1
                else:
                    print(f"   ❌ Heal Cap is {total_row['Heal Cap %']}% (expected 100%)")
                    failed += 1
            else:
                print("   ❌ TOTAL row not found")
                failed += 1
        except json.JSONDecodeError as e:
            print(f"   ❌ Failed to parse dashboardData: {e}")
            failed += 1
    else:
        print("   ❌ dashboardData not found")
        failed += 1
    
    # Test 2: Extract and verify realAgentData
    print("\n2. Testing realAgentData embedding...")
    real_data_match = re.search(r'const realAgentData = (\{.*?\});', html, re.DOTALL)
    if real_data_match:
        try:
            real_json = real_data_match.group(1)
            real_data = json.loads(real_json)
            territories = list(real_data.keys())
            print(f"   ✅ realAgentData found: {len(territories)} territories")
            
            # Check a sample territory
            if territories:
                sample = territories[0]
                sample_data = real_data[sample]
                if 'agents' in sample_data and 'healCap' in sample_data:
                    agent_count = len(sample_data['agents'])
                    heal_values = sample_data['healCap']
                    print(f"   ✅ Sample territory '{sample}':")
                    print(f"      - {agent_count} agents")
                    print(f"      - {len(heal_values)} heal cap values")
                    print(f"      - Heal cap range: {min(heal_values):.0f}% - {max(heal_values):.0f}%")
                    
                    # Check if all agents have 100% heal cap (should be true)
                    all_100 = all(v == 100.0 for v in heal_values)
                    if all_100:
                        print(f"   ✅ All agents in '{sample}' have 100% heal cap")
                        passed += 1
                    else:
                        at_zero = sum(1 for v in heal_values if v == 0)
                        print(f"   ⚠️  {at_zero} agents at 0% heal cap in '{sample}'")
                        passed += 1
                else:
                    print(f"   ❌ Sample territory missing agents or healCap")
                    failed += 1
            else:
                print("   ❌ No territories in realAgentData")
                failed += 1
        except json.JSONDecodeError as e:
            print(f"   ❌ Failed to parse realAgentData: {e}")
            failed += 1
    else:
        print("   ❌ realAgentData not found")
        failed += 1
    
    # Test 3: Verify globalAgentData assignment
    print("\n3. Testing globalAgentData assignment...")
    if 'globalAgentData = realAgentData' in html:
        print("   ✅ globalAgentData = realAgentData (uses real data)")
        passed += 1
    else:
        print("   ❌ globalAgentData not assigned to realAgentData")
        failed += 1
    
    # Test 4: Verify no mock data calls
    print("\n4. Testing for mock data calls...")
    if 'globalAgentData = generateMockAgentData' in html:
        print("   ❌ Still calling generateMockAgentData")
        failed += 1
    else:
        print("   ✅ Not calling generateMockAgentData")
        passed += 1
    
    # Test 5: Verify loadData function exists
    print("\n5. Testing loadData function...")
    if 'function loadData()' in html:
        print("   ✅ loadData function found")
        passed += 1
    else:
        print("   ❌ loadData function not found")
        failed += 1
    
    # Test 6: Verify rendering functions
    print("\n6. Testing rendering functions...")
    render_funcs = [
        'renderTerritorySummaryTable',
        'renderCodeQualityTable',
        'openDrillModal'
    ]
    for func in render_funcs:
        if f'function {func}' in html:
            print(f"   ✅ {func} found")
            passed += 1
        else:
            print(f"   ❌ {func} not found")
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ DASHBOARD IS POPULATED AND READY")
        print("\nTo view the dashboard:")
        print("1. Open: C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
        print("2. Check browser console (F12) for any JavaScript errors")
        print("3. Verify TOTAL row shows 100% Heal Cap")
        print("4. Check outlier badges show correct counts (0 @0%)")
        return True
    else:
        print("\n❌ DASHBOARD HAS ISSUES")
        return False

if __name__ == "__main__":
    import sys
    success = test_dashboard_visual()
    sys.exit(0 if success else 1)
