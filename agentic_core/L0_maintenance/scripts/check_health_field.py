#!/usr/bin/env python3
"""Check if Health field exists in dashboard data."""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"

content = data_file.read_text(encoding='utf-8')
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
data = json.loads(content)

print("\nChecking for Health field in dashboard data:")
print("="*60)

has_health = False
for row in data[:5]:
    health_value = row.get('Health', 'MISSING')
    print(f"{row['Territory']}: Health = {health_value}")
    if health_value != 'MISSING':
        has_health = True

print("\n" + "="*60)
if has_health:
    print("✅ Health field EXISTS in dashboard data")
else:
    print("❌ Health field MISSING from dashboard data")
    print("\nThis is a CRITICAL issue - Health score should be calculated!")

print("\nAll fields in first row:")
print(list(data[0].keys()))
