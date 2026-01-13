#!/usr/bin/env python3
"""Verify L6 Base Class is now in dashboard."""
import json
import re
from pathlib import Path

dashboard_path = Path('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
with open(dashboard_path, 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    territories = [r['Territory'] for r in data]
    print(f"Total territories: {len(territories)}")
    
    l6_territories = [t for t in territories if 'L6' in t]
    print(f"\nL6 territories in dashboard: {l6_territories}")
    
    if 'L6_Observability/Base Class' in territories:
        print("\n✅ L6_Observability/Base Class IS in dashboard!")
    else:
        print("\n❌ L6_Observability/Base Class is MISSING!")
else:
    print("❌ Could not extract dashboardData")
