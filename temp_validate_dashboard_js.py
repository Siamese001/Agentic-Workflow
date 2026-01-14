"""Validate dashboard JavaScript for syntax errors."""
import re
import json
from pathlib import Path

html_path = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
html = html_path.read_text(encoding='utf-8')

print("=" * 70)
print("DASHBOARD JAVASCRIPT VALIDATION")
print("=" * 70)

# Check dashboardData
print("\n1. Checking dashboardData...")
dd_match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
if dd_match:
    try:
        data = json.loads(dd_match.group(1))
        print(f"   ✅ dashboardData valid JSON: {len(data)} rows")
        print(f"   First row: {data[0].get('Territory', 'N/A')}")
        print(f"   Last row: {data[-1].get('Territory', 'N/A')}")
    except json.JSONDecodeError as e:
        print(f"   ❌ dashboardData JSON ERROR: {e}")
else:
    print("   ❌ dashboardData NOT FOUND")

# Check strategicObservationsData
print("\n2. Checking strategicObservationsData...")
sod_match = re.search(r'const strategicObservationsData = (\{.*?\});', html, re.DOTALL)
if sod_match:
    try:
        data = json.loads(sod_match.group(1))
        print(f"   ✅ strategicObservationsData valid JSON")
        print(f"   macro_observations: {len(data.get('macro_observations', []))}")
        print(f"   metric_observations: {len(data.get('metric_observations', []))}")
    except json.JSONDecodeError as e:
        print(f"   ❌ strategicObservationsData JSON ERROR: {e}")
else:
    print("   ❌ strategicObservationsData NOT FOUND")

# Check recommendationsData
print("\n3. Checking recommendationsData...")
rd_match = re.search(r'const recommendationsData = (\[.*?\]);', html, re.DOTALL)
if rd_match:
    try:
        data = json.loads(rd_match.group(1))
        print(f"   ✅ recommendationsData valid JSON: {len(data)} recommendations")
    except json.JSONDecodeError as e:
        print(f"   ❌ recommendationsData JSON ERROR: {e}")
else:
    print("   ❌ recommendationsData NOT FOUND")

# Check realAgentData
print("\n4. Checking realAgentData...")
rad_match = re.search(r'const realAgentData = (\{.*?\});', html, re.DOTALL)
if rad_match:
    try:
        data = json.loads(rad_match.group(1))
        print(f"   ✅ realAgentData valid JSON: {len(data)} territories")
        for territory in list(data.keys())[:3]:
            agents = data[territory].get('agents', [])
            print(f"      - {territory}: {len(agents)} agents")
    except json.JSONDecodeError as e:
        print(f"   ❌ realAgentData JSON ERROR: {e}")
        # Show context around error
        start = max(0, e.pos - 50)
        end = min(len(rad_match.group(1)), e.pos + 50)
        print(f"   Context: ...{rad_match.group(1)[start:end]}...")
else:
    print("   ❌ realAgentData NOT FOUND")

# Check for key rendering functions
print("\n5. Checking rendering functions...")
functions = [
    'renderTerritorySummaryTable',
    'renderCodeQualityTable', 
    'renderRecommendations',
    'loadData'
]
for func in functions:
    if f'function {func}' in html:
        print(f"   ✅ {func} defined")
    else:
        print(f"   ❌ {func} NOT FOUND")

# Check for DOM elements
print("\n6. Checking DOM elements...")
elements = ['kpiGrid', 'codeQualityGrid', 'macroObservations', 'metricObservations']
for elem in elements:
    if f'id="{elem}"' in html:
        print(f"   ✅ #{elem} exists")
    else:
        print(f"   ❌ #{elem} NOT FOUND")

# Check loadData is called
print("\n7. Checking loadData invocation...")
if 'loadData()' in html:
    print("   ✅ loadData() is called")
else:
    print("   ❌ loadData() NOT called")

print("\n" + "=" * 70)
