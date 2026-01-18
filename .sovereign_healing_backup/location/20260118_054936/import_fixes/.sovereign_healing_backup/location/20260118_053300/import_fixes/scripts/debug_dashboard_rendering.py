#!/usr/bin/env python3
"""
Debug Dashboard Rendering Issues
Check why dashboard appears empty in browser
"""
import json
import re
from pathlib import Path

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.validators.structure_blueprint_2 import DASHBOARD_DIR, get_validated_project_root

def debug_dashboard():
    """Debug dashboard rendering."""
    print("=" * 70)
    print("DASHBOARD RENDERING DEBUG")
    print("=" * 70)
    
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    html = dashboard_path.read_text(encoding='utf-8')
    
    # 1. Check dashboardData exists and is valid
    print("\n1. Checking dashboardData...")
    dashboard_match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
    if dashboard_match:
        try:
            data = json.loads(dashboard_match.group(1))
            print(f"   ✅ dashboardData: {len(data)} rows")
            total = next((r for r in data if r.get('Territory') == 'TOTAL'), None)
            if total:
                print(f"   ✅ TOTAL row: {total['Total']} agents, {total['Heal Cap %']}% heal cap")
        except Exception as e:
            print(f"   ❌ Parse error: {e}")
    else:
        print("   ❌ dashboardData not found")
    
    # 2. Check realAgentData exists
    print("\n2. Checking realAgentData...")
    real_match = re.search(r'const realAgentData = (\{.*?\});', html, re.DOTALL)
    if real_match:
        try:
            real_data = json.loads(real_match.group(1))
            print(f"   ✅ realAgentData: {len(real_data)} territories")
        except Exception as e:
            print(f"   ❌ Parse error: {e}")
    else:
        print("   ❌ realAgentData not found")
    
    # 3. Check HTML containers exist
    print("\n3. Checking HTML containers...")
    containers = ['id="kpiGrid"', 'id="codeQualityGrid"']
    for container in containers:
        if container in html:
            print(f"   ✅ {container} exists")
        else:
            print(f"   ❌ {container} missing")
    
    # 4. Check loadData() is called
    print("\n4. Checking loadData() call...")
    if 'loadData();' in html:
        print("   ✅ loadData() is called")
        # Find where it's called
        lines = html.split('\n')
        for i, line in enumerate(lines, 1):
            if 'loadData();' in line and '//' not in line.split('loadData()')[0]:
                print(f"   ✅ Called at line {i}")
    else:
        print("   ❌ loadData() not called")
    
    # 5. Check for JavaScript syntax errors
    print("\n5. Checking for common JavaScript errors...")
    
    # Check for unclosed braces in realAgentData
    if real_match:
        real_json = real_match.group(1)
        open_braces = real_json.count('{')
        close_braces = real_json.count('}')
        if open_braces == close_braces:
            print(f"   ✅ Braces balanced in realAgentData ({open_braces} pairs)")
        else:
            print(f"   ❌ Brace mismatch: {open_braces} open, {close_braces} close")
    
    # Check for unclosed brackets in dashboardData
    if dashboard_match:
        dash_json = dashboard_match.group(1)
        open_brackets = dash_json.count('[')
        close_brackets = dash_json.count(']')
        if open_brackets == close_brackets:
            print(f"   ✅ Brackets balanced in dashboardData ({open_brackets} pairs)")
        else:
            print(f"   ❌ Bracket mismatch: {open_brackets} open, {close_brackets} close")
    
    # 6. Check renderTerritorySummaryTable function
    print("\n6. Checking rendering functions...")
    funcs = [
        'function renderTerritorySummaryTable',
        'function renderCodeQualityTable',
        'function loadData'
    ]
    for func in funcs:
        if func in html:
            print(f"   ✅ {func} exists")
        else:
            print(f"   ❌ {func} missing")
    
    # 7. Check if globalAgentData is assigned
    print("\n7. Checking globalAgentData assignment...")
    if 'globalAgentData = realAgentData' in html:
        print("   ✅ globalAgentData = realAgentData")
    else:
        print("   ❌ globalAgentData not assigned")
    
    # 8. Extract and show a sample of the data
    print("\n8. Sample data from dashboardData...")
    if dashboard_match:
        try:
            data = json.loads(dashboard_match.group(1))
            if len(data) > 1:
                sample = data[1]  # First territory after TOTAL
                print(f"   Territory: {sample.get('Territory')}")
                print(f"   Agents: {sample.get('Total')}")
                print(f"   Heal Cap: {sample.get('Heal Cap %')}%")
        except:
            pass
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("\nTo debug in browser:")
    print("1. Open http://localhost:8080/autonomy_dashboard.html")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to Console tab")
    print("4. Check for JavaScript errors (red text)")
    print("5. Type: dashboardData")
    print("6. Type: realAgentData")
    print("7. Type: document.getElementById('kpiGrid')")
    print("\nIf you see errors, copy them and share for debugging.")

if __name__ == "__main__":
    debug_dashboard()
