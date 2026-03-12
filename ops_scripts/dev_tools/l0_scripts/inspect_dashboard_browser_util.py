"""
Inspect dashboard in browser by fetching and analyzing the rendered HTML
"""
import json
import re
import requests
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
try:
    from bs4 import BeautifulSoup
except ImportError as _err:
    raise ImportError("beautifulsoup4 is required for this module. Install with: pip install -e '.[infra]'") from _err

def inspect_dashboard():
    """Fetch dashboard from localhost and inspect what's rendering."""
    print('=' * 70)
    print('DASHBOARD BROWSER INSPECTION')
    print('=' * 70)
    try:
        print('\n1. Fetching http://localhost:8080/autonomy_dashboard.html...')
        response = requests.get('http://localhost:8080/autonomy_dashboard.html', timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            print(f'   ❌ HTTP {response.status_code}: {response.reason}')
            return
        print(f'   ✅ HTTP 200 OK - {len(response.text)} bytes')
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        print('\n2. Checking DOM elements:')
        kpi_grid = soup.find(id='kpiGrid')
        code_quality_grid = soup.find(id='codeQualityGrid')
        if kpi_grid:
            print('   ✅ #kpiGrid exists')
            if kpi_grid.get_text(strip=True):
                print(f'      Content length: {len(kpi_grid.get_text())} chars')
            else:
                print('      ⚠️  #kpiGrid is EMPTY')
        else:
            print('   ❌ #kpiGrid NOT FOUND')
        if code_quality_grid:
            print('   ✅ #codeQualityGrid exists')
            if code_quality_grid.get_text(strip=True):
                print(f'      Content length: {len(code_quality_grid.get_text())} chars')
            else:
                print('      ⚠️  #codeQualityGrid is EMPTY')
        else:
            print('   ❌ #codeQualityGrid NOT FOUND')
        print('\n3. Checking embedded data:')
        if 'const dashboardData = [' in html:
            print('   ✅ dashboardData found in HTML')
            match = re.search('const dashboardData = (\\[.*?\\]);', html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    print(f'      {len(data)} rows')
                # guardian: allow-silent-swallow
                except:
                    print('      ⚠️  Failed to parse dashboardData JSON')
        else:
            print('   ❌ dashboardData NOT FOUND')
        if 'const realAgentData = {' in html:
            print('   ✅ realAgentData found in HTML')
            match = re.search('const realAgentData = (\\{.*?\\});', html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    print(f'      {len(data)} territories')
                # guardian: allow-silent-swallow
                except:
                    print('      ⚠️  Failed to parse realAgentData JSON')
        else:
            print('   ❌ realAgentData NOT FOUND')
        print('\n4. Checking JavaScript functions:')
        if 'function loadData()' in html:
            print('   ✅ loadData() function exists')
        else:
            print('   ❌ loadData() function NOT FOUND')
        if 'loadData();' in html:
            print('   ✅ loadData() is called')
        else:
            print('   ❌ loadData() is NOT called')
        if 'function renderTerritorySummaryTable' in html:
            print('   ✅ renderTerritorySummaryTable() exists')
        else:
            print('   ❌ renderTerritorySummaryTable() NOT FOUND')
        print('\n5. Checking rendered tables:')
        tables = soup.find_all('table')
        print(f'   Found {len(tables)} <table> elements')
        if tables:
            for i, table in enumerate(tables, 1):
                rows = table.find_all('tr')
                print(f'   Table {i}: {len(rows)} rows')
        print('\n6. Checking visible content:')
        body = soup.find('body')
        if body:
            text = body.get_text(strip=True)
            if len(text) > 0:
                print(f'   Body text length: {len(text)} chars')
                preview = text[:200].replace('\n', ' ')
                print(f'   Preview: {preview}...')
            else:
                print('   ⚠️  Body is EMPTY')
        print('\n' + '=' * 70)
        print('DIAGNOSIS')
        print('=' * 70)
        if kpi_grid and (not kpi_grid.get_text(strip=True)):
            print('\n❌ ISSUE: #kpiGrid exists but is EMPTY')
            print('   This means:')
            print('   - HTML loaded successfully')
            print('   - DOM elements exist')
            print('   - BUT JavaScript is not populating the tables')
            print('\n   Possible causes:')
            print('   1. loadData() not being called')
            print('   2. JavaScript error preventing execution')
            print('   3. renderTerritorySummaryTable() failing silently')
            print('   4. Data not being passed to rendering functions')
            print('\n   NEXT STEP: Add console.log statements to track execution')
        elif not kpi_grid:
            print('\n❌ ISSUE: #kpiGrid element NOT FOUND')
            print('   This means the HTML structure is broken')
        elif kpi_grid.get_text(strip=True):
            print('\n✅ SUCCESS: Tables are populated!')
            print(f'   #kpiGrid has {len(kpi_grid.get_text())} characters of content')
    except requests.exceptions.ConnectionError:
        print('\n❌ CONNECTION ERROR: Cannot connect to http://localhost:8080')
        print('   Make sure the HTTP server is running:')
        print('   python agentic_core/L6_observability/dashboards/simple_server.py')
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
if __name__ == '__main__':
    inspect_dashboard()
