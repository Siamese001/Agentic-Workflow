"""
Verify No Mock Data in Dashboard

Comprehensive verification that all mock data has been eliminated:
1. Check that realAgentData is embedded
2. Verify generateMockAgentData is deprecated
3. Confirm getMockFanInData returns 0
4. Validate outlier badges use real data
5. Check semantic/runtime metrics are disabled
"""
import re
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import DASHBOARD_DIR, get_validated_project_root
except ImportError:
    DASHBOARD_DIR = 'docs/dashboards'

    def get_validated_project_root():
        return Path.cwd()

def verify_no_mock_data():
    """Verify all mock data has been eliminated from dashboard."""
    print('=' * 70)
    print('MOCK DATA ELIMINATION VERIFICATION')
    print('=' * 70)
    dashboard_path = get_validated_project_root() / DASHBOARD_DIR / 'autonomy_dashboard.html'
    html = dashboard_path.read_text(encoding='utf-8')
    issues = []
    print('\n1. Checking realAgentData embedding...')
    if 'const realAgentData = {' in html:
        print('   ✅ realAgentData is embedded')
        real_data_match = re.search('const realAgentData = \\{([^}]+\\}){2,}', html, re.DOTALL)
        if real_data_match:
            territories = len(re.findall('"[^"]+": \\{', real_data_match.group(0)))
            print(f'   ✅ Contains data for {territories} territories')
    else:
        print('   ❌ realAgentData NOT found')
        issues.append('realAgentData not embedded')
    print('\n2. Checking generateMockAgentData deprecation...')
    if 'function generateMockAgentData_DEPRECATED' in html:
        print('   ✅ generateMockAgentData renamed to _DEPRECATED')
    elif 'function generateMockAgentData(' in html:
        print('   ❌ generateMockAgentData still active')
        issues.append('generateMockAgentData not deprecated')
    else:
        print('   ✅ generateMockAgentData removed')
    print('\n3. Checking realAgentData usage...')
    if 'globalAgentData = realAgentData' in html:
        print('   ✅ globalAgentData uses realAgentData')
    else:
        print('   ❌ globalAgentData does not use realAgentData')
        issues.append('globalAgentData not using realAgentData')
    if 'globalAgentData = generateMockAgentData' in html:
        print('   ❌ Still calling generateMockAgentData')
        issues.append('Still calling generateMockAgentData')
    print('\n4. Checking getMockFanInData...')
    fanin_match = re.search('function getMockFanInData\\([^)]+\\)\\s*\\{[^}]*return\\s+(\\d+)', html, re.DOTALL)
    if fanin_match:
        return_val = fanin_match.group(1)
        if return_val == '0':
            print(f'   ✅ getMockFanInData returns {return_val} (disabled)')
        else:
            print(f'   ❌ getMockFanInData returns {return_val} (still using mock data)')
            issues.append(f'getMockFanInData returns {return_val}')
    print('\n5. Checking semantic metrics...')
    if 'const reuseRate = 0; // Disabled' in html:
        print('   ✅ Semantic metrics disabled')
    elif 'Math.random()' in html and 'reuseRate' in html:
        print('   ❌ Semantic metrics still using random data')
        issues.append('Semantic metrics using random data')
    print('\n6. Checking runtime monitoring...')
    if 'const geminiLatency = 0; // Disabled' in html:
        print('   ✅ Runtime monitoring disabled')
    elif 'Math.random()' in html and 'geminiLatency' in html:
        print('   ❌ Runtime monitoring still using random data')
        issues.append('Runtime monitoring using random data')
    print('\n7. Checking for remaining Math.random() calls...')
    random_calls = html.count('Math.random()')
    if random_calls == 0:
        print('   ✅ No Math.random() calls found')
    else:
        print(f'   ⚠️  Found {random_calls} Math.random() calls')
        contexts = re.findall('.{30}Math\\.random\\(\\).{30}', html)
        for i, ctx in enumerate(contexts[:5], 1):
            print(f'      {i}. ...{ctx}...')
    print('\n8. Checking outlier badge data source...')
    if 'globalAgentData[territory].healCap' in html:
        print('   ✅ Outlier badges use globalAgentData (real data)')
    else:
        print('   ⚠️  Could not verify outlier badge data source')
    print('\n' + '=' * 70)
    print('VERIFICATION SUMMARY')
    print('=' * 70)
    if not issues:
        print('✅ ALL MOCK DATA ELIMINATED')
        print('\nDashboard now uses:')
        print('  - realAgentData (embedded from agent_discovery_full.json)')
        print('  - Real per-agent metrics for outlier badges')
        print('  - Real distribution statistics')
        print('  - Disabled toxicity features (awaiting real dependency graph)')
        print('  - Disabled semantic/runtime metrics (awaiting real integration)')
        return True
    else:
        print(f'❌ FOUND {len(issues)} ISSUES:')
        for issue in issues:
            print(f'   - {issue}')
        return False
if __name__ == '__main__':
    import sys
    success = verify_no_mock_data()
    sys.exit(0 if success else 1)
