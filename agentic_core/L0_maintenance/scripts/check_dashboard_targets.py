"""Check if Target values are present in dashboard data."""
import re
import json

with open('reports/autonomy_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the dashboardData array
match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
if match:
    data_str = match.group(1)
    rows = json.loads(data_str)
    
    print(f"Total rows: {len(rows)}")
    
    if rows:
        # Check first row (might be TOTAL)
        sample = rows[0]
        print(f"\nFirst row (Territory: {sample.get('Territory', 'N/A')}):")
        print(f"  Has 'Target Invocation': {'Target Invocation' in sample}")
        
        # Check second row (should be a real territory)
        if len(rows) > 1:
            sample2 = rows[1]
            print(f"\nSecond row (Territory: {sample2.get('Territory', 'N/A')}):")
            print(f"  Has 'Target Invocation': {'Target Invocation' in sample2}")
            print(f"  Has 'Target MCP': {'Target MCP' in sample2}")
            print(f"  Has 'Target Tests': {'Target Tests' in sample2}")
            
            if 'Target Invocation' in sample2:
                print(f"\n✅ Target values ARE present!")
                print(f"  Target Invocation: {sample2['Target Invocation']}")
                print(f"  Target MCP: {sample2.get('Target MCP', 'N/A')}")
                print(f"  Target Tests: {sample2.get('Target Tests', 'N/A')}")
                print(f"  Target Observability: {sample2.get('Target Observability', 'N/A')}")
                print(f"  Target Complexity: {sample2.get('Target Complexity', 'N/A')}")
            else:
                print(f"\n❌ Target values are MISSING!")
                print(f"  Available keys: {list(sample2.keys())[:15]}...")
        else:
            print(f"\n❌ Only TOTAL row found!")
else:
    print("Could not find dashboardData in HTML")
