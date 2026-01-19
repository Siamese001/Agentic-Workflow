#!/usr/bin/env python3
"""
Audit test coverage calculation to verify it's correctly sourced.
User reported 87% seems high (was 40-50% previously).
"""
import json
from pathlib import Path
from collections import defaultdict
from archives.location_violations.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent

print("\n" + "="*70)
print("TEST COVERAGE AUDIT")
print("="*70)

# Load source data
discovery_file = project_root / "agent_discovery_full.json"
with open(discovery_file, 'r', encoding='utf-8') as f:
    agents = json.load(f)

print(f"\nLoaded {len(agents)} agents from discovery")

# Check has_tests field
has_tests_count = sum(1 for a in agents if a.get('has_tests', False))
no_tests_count = len(agents) - has_tests_count
test_pct = (has_tests_count / len(agents) * 100) if agents else 0

print(f"\nTest Coverage from source data:")
print(f"  Agents with tests: {has_tests_count}")
print(f"  Agents without tests: {no_tests_count}")
print(f"  Test Coverage %: {test_pct:.1f}%")

# Group by territory
territories = defaultdict(list)
for agent in agents:
    territory = agent.get('territory', 'Unknown')
    territories[territory].append(agent)

print(f"\nTest Coverage by Territory:")
print("="*70)

for territory in sorted(territories.keys()):
    ags = territories[territory]
    with_tests = sum(1 for a in ags if a.get('has_tests', False))
    total = len(ags)
    pct = (with_tests / total * 100) if total > 0 else 0
    
    print(f"{territory:40} {with_tests:3}/{total:3} = {pct:5.1f}%")

# Sample some agents to verify has_tests field
print(f"\nSample agents with has_tests field:")
print("="*70)
sample_with_tests = [a for a in agents if a.get('has_tests', False)][:5]
sample_without_tests = [a for a in agents if not a.get('has_tests', False)][:5]

print("\nAgents WITH tests (sample):")
for agent in sample_with_tests:
    print(f"  ✅ {agent.get('name', 'Unknown')} (territory: {agent.get('territory', 'Unknown')})")

print("\nAgents WITHOUT tests (sample):")
for agent in sample_without_tests:
    print(f"  ❌ {agent.get('name', 'Unknown')} (territory: {agent.get('territory', 'Unknown')})")

# Check if has_tests is actually a boolean or something else
print(f"\nhas_tests field type analysis:")
print("="*70)
has_tests_types = defaultdict(int)
for agent in agents:
    has_tests = agent.get('has_tests')
    has_tests_types[type(has_tests).__name__] += 1

for type_name, count in sorted(has_tests_types.items()):
    print(f"  {type_name}: {count} agents")

# Check for suspicious patterns
print(f"\nSuspicious patterns:")
print("="*70)

# Check if all agents have has_tests=True (would explain 87%)
all_true = all(a.get('has_tests', False) for a in agents)
if all_true:
    print("  ⚠️  ALL agents have has_tests=True (suspicious!)")
else:
    print("  ✅ Not all agents have has_tests=True")

# Check if has_tests field is missing for many agents
missing_count = sum(1 for a in agents if 'has_tests' not in a)
if missing_count > 0:
    print(f"  ⚠️  {missing_count} agents missing has_tests field")
else:
    print("  ✅ All agents have has_tests field")

# Load dashboard data and compare
print(f"\nDashboard Data Comparison:")
print("="*70)

data_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
content = data_file.read_text(encoding='utf-8')
lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
content = '\n'.join(lines).replace('window.dashboardData = ', '').strip().rstrip(';')
dashboard_data = json.loads(content)

total_row = next((r for r in dashboard_data if r['Territory'] == 'TOTAL'), None)
if total_row:
    dashboard_test_pct = total_row.get('Test %', 0)
    print(f"  Source data: {test_pct:.1f}%")
    print(f"  Dashboard TOTAL: {dashboard_test_pct:.1f}%")
    
    if abs(dashboard_test_pct - test_pct) > 0.1:
        print(f"  ⚠️  MISMATCH: {abs(dashboard_test_pct - test_pct):.1f}% difference")
    else:
        print(f"  ✅ Match: Dashboard matches source data")
