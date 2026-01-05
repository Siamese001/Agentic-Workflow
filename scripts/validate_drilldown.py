#!/usr/bin/env python3
"""Validate drill-down capability for all territory rows in the dashboard."""
import json
from pathlib import Path

def main():
    dashboard_path = Path('reports/autonomy_dashboard.html')
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Extract dashboardData
    start = html.find('const dashboardData = ') + len('const dashboardData = ')
    end = html.find(';', start)
    data = json.loads(html[start:end])
    
    print('='*90)
    print('TERRITORY DRILL-DOWN VALIDATION')
    print('='*90)
    print(f"{'Territory':<50} {'Agents':<12} {'Has Data':<12} {'Drill-Down'}")
    print('-'*90)
    
    issues = []
    
    for row in data:
        territory = row.get('Territory', 'Unknown')
        total = row.get('Total', 0)
        agents = row.get('agents', [])
        has_agents = len(agents) > 0
        can_drill = has_agents and total > 0
        
        if territory == 'TOTAL':
            status = 'N/A (summary)'
        elif can_drill:
            status = '✅ YES'
        else:
            status = '❌ NO'
            if total > 0:
                issues.append(territory)
        
        agents_info = f"{len(agents)}/{total}"
        has_data = 'Yes' if has_agents else 'No'
        
        print(f"{territory:<50} {agents_info:<12} {has_data:<12} {status}")
    
    print('-'*90)
    total_rows = len([r for r in data if r.get('Territory') != 'TOTAL'])
    drillable = sum(1 for r in data if len(r.get('agents', [])) > 0 and r.get('Total', 0) > 0 and r.get('Territory') != 'TOTAL')
    
    print(f"\nSUMMARY: {drillable}/{total_rows} territories have drill-down capability")
    
    if issues:
        print(f"\n❌ ISSUES FOUND - {len(issues)} territories missing agent data:")
        for t in issues:
            print(f"   - {t}")
        return 1
    else:
        print("\n✅ ALL TERRITORIES HAVE DRILL-DOWN CAPABILITY")
        return 0

if __name__ == '__main__':
    exit(main())
