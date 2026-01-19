#!/usr/bin/env python3
"""Check SovereignBaseAgent test coverage discrepancy."""
import json
from pathlib import Path
from archives.location_violations.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent

# Load discovery data
with open(project_root / "agent_discovery_full.json", 'r', encoding='utf-8') as f:
    agents = json.load(f)

# Find SovereignBaseAgent
sovereign = [a for a in agents if a['class_name'] == 'SovereignBaseAgent'][0]

print("\n" + "="*70)
print("SOVEREIGNBASEAGENT TEST COVERAGE ANALYSIS")
print("="*70)

print(f"\nClass: {sovereign['class_name']}")
print(f"Territory: {sovereign['territory']}")
print(f"Has Tests: {sovereign['has_tests']}")
print(f"MCP Hardened: {sovereign['mcp_hardened']}")
print(f"Inheritance: {sovereign['inheritance']}")

# Load dashboard data
dashboard_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
content = dashboard_file.read_text(encoding='utf-8')
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
dashboard_data = json.loads(content)

# Find Sovereign Base Agent row
sovereign_row = next((r for r in dashboard_data if r['Territory'] == 'Sovereign Base Agent'), None)

if sovereign_row:
    print(f"\n{'='*70}")
    print("DASHBOARD DATA")
    print(f"{'='*70}")
    print(f"Territory: {sovereign_row['Territory']}")
    print(f"Total: {sovereign_row['Total']}")
    print(f"Test %: {sovereign_row['Test %']}")
    print(f"MCP Hardened %: {sovereign_row['MCP Hardened %']}")
    print(f"Health: {sovereign_row['Health']}")
    
    # Check for discrepancy
    if sovereign['has_tests'] and sovereign_row['Test %'] == 0:
        print(f"\n{'='*70}")
        print("❌ DISCREPANCY DETECTED")
        print(f"{'='*70}")
        print(f"Discovery data: has_tests = {sovereign['has_tests']}")
        print(f"Dashboard data: Test % = {sovereign_row['Test %']}")
        print("\nThis is a data integrity violation!")
    elif sovereign['has_tests'] and sovereign_row['Test %'] == 100:
        print(f"\n{'='*70}")
        print("✅ DATA CONSISTENT")
        print(f"{'='*70}")
        print(f"Discovery data: has_tests = {sovereign['has_tests']}")
        print(f"Dashboard data: Test % = {sovereign_row['Test %']}")
        print("\nNo discrepancy - user may be looking at stale dashboard.")
else:
    print("\n❌ Sovereign Base Agent row not found in dashboard data!")

# Check territory naming
print(f"\n{'='*70}")
print("TERRITORY NAMING CHECK")
print(f"{'='*70}")
old_territory = sovereign['territory'].replace('Base Agent', 'Base Class')
print(f"Current territory: {sovereign['territory']}")
print(f"Old territory name: {old_territory}")

# Check if there's a "Base/Base Class" territory in dashboard
old_row = next((r for r in dashboard_data if r['Territory'] == old_territory), None)
if old_row:
    print(f"\n❌ OLD TERRITORY FOUND IN DASHBOARD: {old_territory}")
    print(f"   Test %: {old_row['Test %']}")
    print("\nThis suggests dashboard was not regenerated after territory naming fix!")
else:
    print(f"\n✅ Old territory '{old_territory}' not in dashboard")
