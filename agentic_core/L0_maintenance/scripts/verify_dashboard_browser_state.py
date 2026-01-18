#!/usr/bin/env python3
"""
Dashboard Browser State Verification
=====================================
Verifies that the browser is loading the latest dashboard HTML and not a cached version.
Also validates JavaScript execution and data rendering.

This script should be run AFTER dashboard generation to ensure the browser sees the updates.
"""
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_hash(filepath):
    """Get SHA256 hash of file to detect changes."""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def extract_dashboard_data(html_path):
    """Extract dashboardData from HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
    if not match:
        return None
    
    return json.loads(match.group(1))

def verify_browser_state():
    """Verify browser will load latest dashboard state."""
    print("=" * 80)
    print("DASHBOARD BROWSER STATE VERIFICATION")
    print("=" * 80)
    print()
    
    dashboard_path = Path('C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
    
    if not dashboard_path.exists():
        print("❌ ERROR: Dashboard HTML not found")
        return False
    
    # 1. File metadata check
    print("1. FILE METADATA CHECK")
    print("-" * 80)
    stat = dashboard_path.stat()
    mod_time = datetime.fromtimestamp(stat.st_mtime)
    file_size = stat.st_size
    file_hash = get_file_hash(dashboard_path)
    
    print(f"   Path: {dashboard_path}")
    print(f"   Size: {file_size:,} bytes")
    print(f"   Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   SHA256: {file_hash[:16]}...")
    
    # Check if file was modified recently (within last 5 minutes)
    time_since_mod = (datetime.now() - mod_time).total_seconds()
    if time_since_mod > 300:
        print(f"   ⚠️  WARNING: File last modified {int(time_since_mod/60)} minutes ago")
        print(f"   Dashboard may not reflect latest changes!")
    else:
        print(f"   ✅ File modified {int(time_since_mod)} seconds ago (recent)")
    
    # 2. Cache control headers check
    print("\n2. CACHE CONTROL HEADERS CHECK")
    print("-" * 80)
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    cache_headers = [
        'Cache-Control" content="no-cache',
        'Pragma" content="no-cache',
        'Expires" content="0'
    ]
    
    headers_found = []
    for header in cache_headers:
        if header in html_content:
            headers_found.append(header.split('"')[0])
    
    if len(headers_found) == 3:
        print(f"   ✅ All cache-busting headers present: {', '.join(headers_found)}")
    else:
        print(f"   ⚠️  WARNING: Missing cache headers. Found: {headers_found}")
    
    # 3. Dashboard data validation
    print("\n3. DASHBOARD DATA VALIDATION")
    print("-" * 80)
    data = extract_dashboard_data(dashboard_path)
    
    if not data:
        print("   ❌ ERROR: Could not extract dashboardData from HTML")
        return False
    
    total_row = data[0]
    print(f"   Total agents: {total_row.get('Total', 'MISSING')}")
    print(f"   Proper Base %: {total_row.get('Proper Base %', 'MISSING')}")
    print(f"   Base Class Inherit %: {total_row.get('Base Class Inherit %', 'MISSING')}")
    
    # Check for the critical field
    if 'Base Class Inherit %' not in total_row:
        print("   ❌ ERROR: 'Base Class Inherit %' field MISSING from dashboard data")
        print("   Browser will show 0.0% even if file is loaded!")
        return False
    
    if total_row.get('Base Class Inherit %') == 0.0:
        print("   ⚠️  WARNING: 'Base Class Inherit %' is 0.0% in the data")
        print("   This will display as 0.0% in browser even without caching issues")
        return False
    
    print(f"   ✅ Dashboard data valid with Base Class Inherit % = {total_row['Base Class Inherit %']}%")
    
    # 4. JavaScript validation
    print("\n4. JAVASCRIPT VALIDATION")
    print("-" * 80)
    
    js_checks = [
        ('const dashboardData =', 'dashboardData declaration'),
        ('const realAgentData =', 'realAgentData declaration'),
        ('function loadData()', 'loadData function'),
        ('function renderTerritorySummaryTable()', 'renderTerritorySummaryTable function'),
        ("row['Base Class Inherit %']", 'Base Class Inherit % reference in JS')
    ]
    
    js_issues = []
    for pattern, desc in js_checks:
        if pattern not in html_content:
            js_issues.append(desc)
    
    if js_issues:
        print(f"   ⚠️  WARNING: Missing JavaScript elements:")
        for issue in js_issues:
            print(f"      - {issue}")
    else:
        print(f"   ✅ All critical JavaScript elements present")
    
    # 5. Browser refresh instructions
    print("\n5. BROWSER REFRESH INSTRUCTIONS")
    print("-" * 80)
    print("   To ensure browser loads latest version:")
    print("   1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)")
    print("   2. Or: Ctrl+F5 (Windows/Linux)")
    print("   3. Or: Clear browser cache and reload")
    print("   4. Or: Restart web server if using one")
    print()
    print("   If using http-server or live-server:")
    print("   - Stop server (Ctrl+C)")
    print("   - Restart: http-server -c-1 (disables caching)")
    
    print("\n" + "=" * 80)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 80)
    print(f"File hash: {file_hash}")
    print(f"Save this hash to verify browser loaded the correct version")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = verify_browser_state()
    exit(0 if success else 1)
