#!/usr/bin/env python3
"""Full Playwright visual inspection test."""
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from playwright.sync_api import sync_playwright
    
    print("\n" + "=" * 70)
    print("PLAYWRIGHT VISUAL INSPECTION - FULL TEST")
    print("=" * 70)
    
    with sync_playwright() as p:
        print("\n1. Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("2. Navigating to dashboard...")
        page.goto("http://localhost:8765/autonomy_dashboard.html", timeout=30000, wait_until="domcontentloaded")
        time.sleep(5)  # Wait for JavaScript to execute
        
        print(f"3. Page loaded: {page.title()}")
        
        # TEST 1: Check navigation tabs
        print("\n4. TEST 1: Checking navigation tabs...")
        tabs = page.locator('a.nav-tab').all()
        print(f"   Found {len(tabs)} tabs")
        
        # TEST 2: Click Strategic Health tab
        print("\n5. TEST 2: Clicking Strategic Health tab...")
        page.click('a[data-target="executive"]', timeout=5000)
        time.sleep(2)
        
        # TEST 3: Check Table 1 - TOTAL row at top
        print("\n6. TEST 3: Checking Table 1 (Territory Summary)...")
        table1_rows = page.locator('#kpiGrid table tbody tr').all()
        print(f"   Found {len(table1_rows)} rows")
        if len(table1_rows) > 0:
            first_row = table1_rows[0].text_content()
            if 'TOTAL' in first_row:
                print("   ✅ TOTAL row is at the TOP")
            else:
                print(f"   ❌ First row is NOT TOTAL: {first_row[:50]}")
        
        # TEST 4: Check Table 2 - TOTAL row at top
        print("\n7. TEST 4: Checking Table 2 (Code Quality)...")
        table2_rows = page.locator('#codeQualityGrid table tbody tr').all()
        print(f"   Found {len(table2_rows)} rows")
        if len(table2_rows) > 0:
            first_row = table2_rows[0].text_content()
            if 'TOTAL' in first_row:
                print("   ✅ TOTAL row is at the TOP")
            else:
                print(f"   ❌ First row is NOT TOTAL: {first_row[:50]}")
        
        # TEST 5: Click Live Runtime tab
        print("\n8. TEST 5: Clicking Live Runtime tab...")
        page.click('a[data-target="runtime"]', timeout=5000)
        time.sleep(2)
        
        # TEST 6: Check scrollbars
        print("\n9. TEST 6: Checking scrollbars...")
        live_log = page.locator('#liveLog')
        if live_log.count() > 0:
            overflow_y = live_log.evaluate("el => window.getComputedStyle(el).overflowY")
            print(f"   Live Log overflow-y: {overflow_y}")
            if overflow_y == 'scroll':
                print("   ✅ Live Log has scrollbar")
        
        event_log = page.locator('#eventLog')
        if event_log.count() > 0:
            overflow_y = event_log.evaluate("el => window.getComputedStyle(el).overflowY")
            print(f"   Event Log overflow-y: {overflow_y}")
            if overflow_y == 'scroll':
                print("   ✅ Event Log has scrollbar")
        
        # Take screenshot
        screenshot_path = project_root / "dashboard_visual_validation.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"\n10. Screenshot saved: {screenshot_path}")
        
        browser.close()
        print("\n✅ ALL VISUAL TESTS COMPLETED")
        
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
