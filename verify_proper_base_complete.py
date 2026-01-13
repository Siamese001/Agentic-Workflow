"""Complete verification of Proper Base % across all systems."""
import json
import re

print("=" * 80)
print("COMPLETE PROPER BASE % VERIFICATION")
print("=" * 80)

# 1. Check discovery data
print("\n1. DISCOVERY DATA (agent_discovery_full.json)")
print("-" * 80)
with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

total = len(agents)
proper = sum(1 for a in agents if a.get('proper_base_class'))
print(f"Total agents: {total}")
print(f"With proper_base_class=True: {proper} ({round(proper/total*100, 1)}%)")
print(f"With proper_base_class=False: {total-proper}")

# 2. Check dashboard HTML embedded data
print("\n2. DASHBOARD HTML (autonomy_dashboard.html)")
print("-" * 80)
with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
if match:
    dashboard_data = json.loads(match.group(1))
    
    # Check TOTAL
    total_row = [r for r in dashboard_data if r['Territory'] == 'TOTAL'][0]
    print(f"TOTAL row: Proper Base % = {total_row['Proper Base %']}%")
    
    # Check all territories
    all_proper_base = [r['Proper Base %'] for r in dashboard_data if r['Territory'] != 'TOTAL']
    min_val = min(all_proper_base)
    max_val = max(all_proper_base)
    avg_val = sum(all_proper_base) / len(all_proper_base)
    
    print(f"Territory Proper Base % range: {min_val}% - {max_val}%")
    print(f"Territory Proper Base % average: {round(avg_val, 1)}%")
    
    # Show any territories with < 100%
    low_territories = [r for r in dashboard_data if r['Territory'] != 'TOTAL' and r['Proper Base %'] < 100.0]
    if low_territories:
        print(f"\n⚠️  Territories with < 100%:")
        for r in low_territories[:10]:
            print(f"  {r['Territory']}: {r['Proper Base %']}%")
    else:
        print(f"✅ All {len(all_proper_base)} territories show 100.0%")
else:
    print("❌ Could not extract dashboardData from HTML")

# 3. Check e2e test expectations
print("\n3. E2E TEST VALIDATION")
print("-" * 80)
print("Test 12A: Validates TOTAL row Proper Base % matches expected from discovery")
print("Test 12B: Validates territory-level Proper Base % matches expected from discovery")

# Calculate what tests expect
expected_total = round((proper / total) * 100, 1)
print(f"Expected from discovery: {expected_total}%")

# Sample territory check
base_class_agents = [a for a in agents if 'Base Class' in a.get('territory', '')]
if base_class_agents:
    base_proper = sum(1 for a in base_class_agents if a.get('proper_base_class'))
    base_expected = round((base_proper / len(base_class_agents)) * 100, 1)
    print(f"Base Class territories expected: {base_expected}%")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
