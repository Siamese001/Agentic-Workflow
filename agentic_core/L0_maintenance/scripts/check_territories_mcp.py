#!/usr/bin/env python3
"""Check MCP hardening for specific territories in dashboard data."""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"

# Read and parse dashboard data
content = data_file.read_text(encoding='utf-8')
# Remove comments and extract JSON
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines)
content = content.replace('const dashboardData = ', '').strip()
if content.endswith(';'):
    content = content[:-1]
data = json.loads(content)

# Find territories
l0_core = [r for r in data if r['Territory'] == 'L0 Maintenance/Core']
l6_metrics = [r for r in data if r['Territory'] == 'L6_Observability/Metrics']

print("Dashboard Data Check:")
print("=" * 70)

if l0_core:
    row = l0_core[0]
    print(f"\nL0 Maintenance/Core:")
    print(f"  Total Agents: {row['Total']}")
    print(f"  MCP Hardened %: {row['MCP Hardened %']}")
    print(f"  Test %: {row['Test %']}")
else:
    print("\n❌ L0 Maintenance/Core NOT FOUND in dashboard data")

if l6_metrics:
    row = l6_metrics[0]
    print(f"\nL6_Observability/Metrics:")
    print(f"  Total Agents: {row['Total']}")
    print(f"  MCP Hardened %: {row['MCP Hardened %']}")
    print(f"  Test %: {row['Test %']}")
else:
    print("\n❌ L6_Observability/Metrics NOT FOUND in dashboard data")

# Check TOTAL row
total_row = [r for r in data if r['Territory'] == 'TOTAL']
if total_row:
    row = total_row[0]
    print(f"\nTOTAL:")
    print(f"  Total Agents: {row['Total']}")
    print(f"  MCP Hardened %: {row['MCP Hardened %']}")
    print(f"  Test %: {row['Test %']}")

print("\n" + "=" * 70)
print("\nConclusion:")
if l0_core and l6_metrics:
    l0_mcp = l0_core[0]['MCP Hardened %']
    l6_mcp = l6_metrics[0]['MCP Hardened %']
    
    if l0_mcp == 100.0 and l6_mcp == 100.0:
        print("✅ Both territories show 100% MCP Hardening in dashboard data")
        print("\nIf dashboard displays differently, issue is in:")
        print("  1. Browser cache (need hard refresh)")
        print("  2. Dashboard server serving old data")
        print("  3. JavaScript rendering issue")
    else:
        print(f"❌ MCP Hardening not 100%:")
        print(f"  L0 Maintenance/Core: {l0_mcp}%")
        print(f"  L6_Observability/Metrics: {l6_mcp}%")
