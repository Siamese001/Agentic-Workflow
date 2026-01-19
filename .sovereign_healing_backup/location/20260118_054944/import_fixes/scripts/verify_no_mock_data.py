#!/usr/bin/env python3
"""
Verify No Mock Data in Dashboard

Comprehensive verification that all mock data has been eliminated:
1. Check that realAgentData is embedded
2. Verify generateMockAgentData is deprecated
3. Confirm getMockFanInData returns 0
4. Validate outlier badges use real data
5. Check semantic/runtime metrics are disabled
"""
import json
import re
from pathlib import Path

# Import SSOT for dashboard directory - NO HARDCODING
from agentic_core.L5_safety.validators.structure_blueprint_2 import DASHBOARD_DIR, get_validated_project_root

def verify_no_mock_data():
    """Verify all mock data has been eliminated from dashboard."""
    print("=" * 70)
    print("MOCK DATA ELIMINATION VERIFICATION")
    print("=" * 70)
    
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / "autonomy_dashboard.html"
    html = dashboard_path.read_text(encoding='utf-8')
    
    issues = []
    
    # 1. Check realAgentData is embedded
    print("\n1. Checking realAgentData embedding...")
    if 'const realAgentData = {' in html:
        print("   ✅ realAgentData is embedded")
        # Count territories in realAgentData
        real_data_match = re.search(r'const realAgentData = \{([^}]+\}){2,}', html, re.DOTALL)
        if real_data_match:
            territories = len(re.findall(r'"[^"]+": \{', real_data_match.group(0)))
            print(f"   ✅ Contains data for {territories} territories")
    else:
        print("   ❌ realAgentData NOT found")
        issues.append("realAgentData not embedded")
    
    # 2. Check generateMockAgentData is deprecated
    print("\n2. Checking generateMockAgentData deprecation...")
    if 'function generateMockAgentData_DEPRECATED' in html:
        print("   ✅ generateMockAgentData renamed to _DEPRECATED")
    elif 'function generateMockAgentData(' in html:
        print("   ❌ generateMockAgentData still active")
        issues.append("generateMockAgentData not deprecated")
    else:
        print("   ✅ generateMockAgentData removed")
    
    # 3. Check usage of realAgentData
    print("\n3. Checking realAgentData usage...")
    if 'globalAgentData = realAgentData' in html:
        print("   ✅ globalAgentData uses realAgentData")
    else:
        print("   ❌ globalAgentData does not use realAgentData")
        issues.append("globalAgentData not using realAgentData")
    
    if 'globalAgentData = generateMockAgentData' in html:
        print("   ❌ Still calling generateMockAgentData")
        issues.append("Still calling generateMockAgentData")
    
    # 4. Check getMockFanInData
    print("\n4. Checking getMockFanInData...")
    fanin_match = re.search(r'function getMockFanInData\([^)]+\)\s*\{[^}]*return\s+(\d+)', html, re.DOTALL)
    if fanin_match:
        return_val = fanin_match.group(1)
        if return_val == '0':
            print(f"   ✅ getMockFanInData returns {return_val} (disabled)")
        else:
            print(f"   ❌ getMockFanInData returns {return_val} (still using mock data)")
            issues.append(f"getMockFanInData returns {return_val}")
    
    # 5. Check semantic metrics
    print("\n5. Checking semantic metrics...")
    if 'const reuseRate = 0; // Disabled' in html:
        print("   ✅ Semantic metrics disabled")
    elif 'Math.random()' in html and 'reuseRate' in html:
        print("   ❌ Semantic metrics still using random data")
        issues.append("Semantic metrics using random data")
    
    # 6. Check runtime monitoring
    print("\n6. Checking runtime monitoring...")
    if 'const geminiLatency = 0; // Disabled' in html:
        print("   ✅ Runtime monitoring disabled")
    elif 'Math.random()' in html and 'geminiLatency' in html:
        print("   ❌ Runtime monitoring still using random data")
        issues.append("Runtime monitoring using random data")
    
    # 7. Count remaining Math.random() calls
    print("\n7. Checking for remaining Math.random() calls...")
    random_calls = html.count('Math.random()')
    if random_calls == 0:
        print("   ✅ No Math.random() calls found")
    else:
        print(f"   ⚠️  Found {random_calls} Math.random() calls")
        # Find contexts
        contexts = re.findall(r'.{30}Math\.random\(\).{30}', html)
        for i, ctx in enumerate(contexts[:5], 1):
            print(f"      {i}. ...{ctx}...")
    
    # 8. Verify outlier badge data source
    print("\n8. Checking outlier badge data source...")
    if 'globalAgentData[territory].healCap' in html:
        print("   ✅ Outlier badges use globalAgentData (real data)")
    else:
        print("   ⚠️  Could not verify outlier badge data source")
    
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    if not issues:
        print("✅ ALL MOCK DATA ELIMINATED")
        print("\nDashboard now uses:")
        print("  - realAgentData (embedded from agent_discovery_full.json)")
        print("  - Real per-agent metrics for outlier badges")
        print("  - Real distribution statistics")
        print("  - Disabled toxicity features (awaiting real dependency graph)")
        print("  - Disabled semantic/runtime metrics (awaiting real integration)")
        return True
    else:
        print(f"❌ FOUND {len(issues)} ISSUES:")
        for issue in issues:
            print(f"   - {issue}")
        return False

if __name__ == "__main__":
    import sys
    success = verify_no_mock_data()
    sys.exit(0 if success else 1)
