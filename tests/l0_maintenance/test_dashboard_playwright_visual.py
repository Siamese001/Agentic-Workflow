#!/usr/bin/env python3
"""
MANDATORY PLAYWRIGHT VISUAL INSPECTION FOR DASHBOARD E2E TESTS

This script performs visual validation of dashboard changes using Playwright.
It is a REQUIRED step in the dashboard deployment pipeline.

Visual Checks:
1. TOTAL row is at the TOP of Table 1 (Territory Summary)
2. TOTAL row is at the TOP of Table 2 (Code Quality)
3. Scrollbars are present in Live Sovereign Log
4. Scrollbars are present in Real-Time Event Log
5. Purpose descriptions are visible in all Live Runtime sections
6. All JavaScript files load without errors
7. Tables render with correct data

This test MUST pass before any dashboard deployment.
"""
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from agentic_core.utils.security import safe_popen

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_playwright_visual_tests() -> Tuple[bool, List[str]]:
    """
    Run Playwright visual inspection tests.
    Returns (success, errors)
    """
    errors = []
    
    print("\n" + "=" * 70)
    print("PLAYWRIGHT VISUAL INSPECTION - MANDATORY DASHBOARD VALIDATION")
    print("=" * 70)
    
    # Check if Playwright is installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        errors.append("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return False, errors
    
    # Start dashboard server
    print("\n1. Starting dashboard server on port 8765...")
    dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"
    
    server_process = safe_popen(
        [sys.executable, "-m", "http.server", "8765"],
        cwd=str(dashboard_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)
    print("   ✅ Server started")
    
    try:
        with sync_playwright() as p:
            print("\n2. Launching browser with cache disabled...")
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-cache', '--disable-application-cache', '--disable-offline-load-stale-cache']
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True
            )
            
            page = context.new_page()
            
            # Track JavaScript errors
            js_errors = []
            page.on("pageerror", lambda exc: js_errors.append(str(exc)))
            
            print("\n3. Navigating to dashboard...")
            try:
                page.goto("http://localhost:8765/autonomy_dashboard.html", timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
            except Exception as e:
                errors.append(f"Failed to load dashboard: {e}")
                browser.close()
                return False, errors
            
            time.sleep(5)  # Wait for JavaScript to execute and render
            
            # Check for JavaScript errors
            if js_errors:
                errors.append(f"JavaScript errors detected: {js_errors}")
                print(f"   ⚠️  JavaScript errors: {js_errors}")
            
            # Debug: Check if page loaded
            print("   Checking page load status...")
            page_title = page.title()
            print(f"   Page title: {page_title}")
            
            # Check if tabs are present
            tabs = page.locator('a.nav-tab').all()
            print(f"   Found {len(tabs)} navigation tabs")
            
            if len(tabs) == 0:
                # Check what's actually in the page
                html_content = page.content()
                if 'nav-tab' in html_content:
                    print("   ⚠️  nav-tab found in HTML but not rendered by locator")
                else:
                    print("   ❌ nav-tab not found in HTML at all")
                
                # Check for console errors
                console_logs = page.evaluate("() => { return window.__console_logs || []; }")
                if console_logs:
                    print(f"   Console logs: {console_logs}")
                
                errors.append("CRITICAL: Navigation tabs not found - page may not have loaded correctly")
                # Take screenshot for debugging
                page.screenshot(path=str(project_root / "dashboard_load_failure.png"))
                print(f"   ❌ Dashboard failed to load properly - screenshot saved")
                
                # Try to get the actual error
                try:
                    error_element = page.locator('body').text_content()
                    if error_element:
                        print(f"   Page body text (first 200 chars): {error_element[:200]}")
                except:
                    pass
            
            print("\n4. Clicking Strategic Health tab...")
            try:
                page.click('a[data-target="executive"]', timeout=5000)
                time.sleep(2)
            except Exception as e:
                errors.append(f"Failed to click Strategic Health tab: {e}")
            
            # TEST 1: Verify Table 1 (Territory Summary) - TOTAL row at top
            print("\n5. TEST 1: Verifying Table 1 (Territory Summary) - TOTAL row position...")
            try:
                table1_rows = page.locator('#kpiGrid table tbody tr').all()
                if len(table1_rows) == 0:
                    errors.append("TEST 1 FAILED: Table 1 not rendered - no rows found")
                else:
                    first_row_text = table1_rows[0].text_content()
                    if 'TOTAL' in first_row_text:
                        print("   ✅ TEST 1 PASSED: TOTAL row is at the TOP of Table 1")
                    else:
                        first_territory = first_row_text.split()[0] if first_row_text else "N/A"
                        errors.append(f"TEST 1 FAILED: TOTAL row NOT at top of Table 1. First row: {first_territory}")
                        print(f"   ❌ TEST 1 FAILED: First row is '{first_territory}', not TOTAL")
            except Exception as e:
                errors.append(f"TEST 1 FAILED: Error checking Table 1: {e}")
            
            # TEST 2: Verify Table 2 (Code Quality) - TOTAL row at top
            print("\n6. TEST 2: Verifying Table 2 (Code Quality) - TOTAL row position...")
            try:
                table2_rows = page.locator('#codeQualityGrid table tbody tr').all()
                if len(table2_rows) == 0:
                    errors.append("TEST 2 FAILED: Table 2 not rendered - no rows found")
                else:
                    first_row_text = table2_rows[0].text_content()
                    if 'TOTAL' in first_row_text:
                        print("   ✅ TEST 2 PASSED: TOTAL row is at the TOP of Table 2")
                    else:
                        first_territory = first_row_text.split()[0] if first_row_text else "N/A"
                        errors.append(f"TEST 2 FAILED: TOTAL row NOT at top of Table 2. First row: {first_territory}")
                        print(f"   ❌ TEST 2 FAILED: First row is '{first_territory}', not TOTAL")
            except Exception as e:
                errors.append(f"TEST 2 FAILED: Error checking Table 2: {e}")
            
            # TEST 3: Click Live Runtime tab
            print("\n7. Clicking Live Runtime tab...")
            try:
                page.click('a[data-target="runtime"]', timeout=5000)
                time.sleep(2)
            except Exception as e:
                errors.append(f"Failed to click Live Runtime tab: {e}")
            
            # TEST 3: Verify scrollbars in Live Sovereign Log
            print("\n8. TEST 3: Verifying scrollbars in Live Sovereign Log...")
            try:
                live_log = page.locator('#liveLog')
                if live_log.count() > 0:
                    overflow_y = live_log.evaluate("el => window.getComputedStyle(el).overflowY")
                    if overflow_y == 'scroll':
                        print("   ✅ TEST 3 PASSED: Live Sovereign Log has scrollbar")
                    else:
                        errors.append(f"TEST 3 FAILED: Live Sovereign Log overflow-y is '{overflow_y}', not 'scroll'")
                else:
                    errors.append("TEST 3 FAILED: Live Sovereign Log element not found")
            except Exception as e:
                errors.append(f"TEST 3 FAILED: Error checking Live Sovereign Log: {e}")
            
            # TEST 4: Verify scrollbars in Real-Time Event Log
            print("\n9. TEST 4: Verifying scrollbars in Real-Time Event Log...")
            try:
                event_log = page.locator('#eventLog')
                if event_log.count() > 0:
                    overflow_y = event_log.evaluate("el => window.getComputedStyle(el).overflowY")
                    if overflow_y == 'scroll':
                        print("   ✅ TEST 4 PASSED: Real-Time Event Log has scrollbar")
                    else:
                        errors.append(f"TEST 4 FAILED: Real-Time Event Log overflow-y is '{overflow_y}', not 'scroll'")
                else:
                    errors.append("TEST 4 FAILED: Real-Time Event Log element not found")
            except Exception as e:
                errors.append(f"TEST 4 FAILED: Error checking Real-Time Event Log: {e}")
            
            # TEST 5: Verify purpose descriptions are visible
            print("\n10. TEST 5: Verifying purpose descriptions in Live Runtime sections...")
            try:
                # Check for purpose description text
                purpose_text = page.locator('text=/Purpose:.*?/').all()
                if len(purpose_text) >= 8:  # Should have 8 sections with purpose descriptions
                    print(f"   ✅ TEST 5 PASSED: Found {len(purpose_text)} purpose descriptions")
                else:
                    errors.append(f"TEST 5 FAILED: Only found {len(purpose_text)} purpose descriptions, expected at least 8")
            except Exception as e:
                errors.append(f"TEST 5 FAILED: Error checking purpose descriptions: {e}")
            
            # TEST 6: Verify JavaScript files loaded correctly
            print("\n11. TEST 6: Verifying JavaScript files loaded without errors...")
            try:
                # Check if table-renderer.js loaded
                js_check = page.evaluate("""
                    () => {
                        return {
                            hasRenderTerritorySummaryTable: typeof renderTerritorySummaryTable === 'function',
                            hasRenderCodeQualityTable: typeof renderCodeQualityTable === 'function',
                            hasDashboardData: typeof dashboardData !== 'undefined' && dashboardData.length > 0
                        };
                    }
                """)
                
                if js_check['hasRenderTerritorySummaryTable'] and js_check['hasRenderCodeQualityTable']:
                    print("   ✅ TEST 6 PASSED: All required JavaScript functions loaded")
                else:
                    errors.append(f"TEST 6 FAILED: Missing JavaScript functions: {js_check}")
                
                if not js_check['hasDashboardData']:
                    errors.append("TEST 6 FAILED: dashboardData not loaded or empty")
            except Exception as e:
                errors.append(f"TEST 6 FAILED: Error checking JavaScript: {e}")
            
            # TEST 7: Verify 100% MCP Hardening displayed in ALL territories
            print("\n12. TEST 7: Verifying 100% MCP Hardening displayed in ALL territories...")
            try:
                # Click back to Strategic Health tab
                page.click('a[data-target="executive"]', timeout=5000)
                time.sleep(1)
                
                # Get all rows from Table 1
                all_rows = page.locator('#kpiGrid table tbody tr').all()
                
                if len(all_rows) == 0:
                    errors.append("TEST 7 FAILED: No rows found in Table 1")
                else:
                    # Check each territory for 100% MCP Hardening
                    territories_checked = 0
                    territories_failed = []
                    
                    for row in all_rows:
                        cells = row.locator('td').all()
                        if len(cells) >= 7:
                            territory_name = cells[0].text_content().strip()
                            mcp_hardened_text = cells[6].text_content().strip()  # 7th column (0-indexed)
                            
                            # Check if MCP Hardening is 100%
                            if '100' not in mcp_hardened_text or '%' not in mcp_hardened_text:
                                territories_failed.append(f"{territory_name}: {mcp_hardened_text}")
                            
                            territories_checked += 1
                    
                    if territories_failed:
                        errors.append(f"TEST 7 FAILED: {len(territories_failed)} territories do NOT show 100% MCP Hardening:")
                        for failure in territories_failed:
                            errors.append(f"  - {failure}")
                            print(f"   ❌ {failure}")
                    else:
                        print(f"   ✅ TEST 7 PASSED: All {territories_checked} territories show 100% MCP Hardening")
                        
                        # Specifically verify the two territories user mentioned
                        l0_found = False
                        l6_found = False
                        for row in all_rows:
                            cells = row.locator('td').all()
                            if len(cells) >= 7:
                                territory_name = cells[0].text_content().strip()
                                if 'L0 Maintenance' in territory_name and 'Core' in territory_name:
                                    l0_found = True
                                    print(f"   ✅ L0 Maintenance/Core: 100% MCP Hardening verified")
                                elif 'L6' in territory_name and 'Metrics' in territory_name:
                                    l6_found = True
                                    print(f"   ✅ L6_Observability/Metrics: 100% MCP Hardening verified")
                        
                        if not l0_found:
                            errors.append("TEST 7 WARNING: L0 Maintenance/Core territory not found in table")
                        if not l6_found:
                            errors.append("TEST 7 WARNING: L6_Observability/Metrics territory not found in table")
                            
            except Exception as e:
                errors.append(f"TEST 7 FAILED: Error checking MCP Hardening: {e}")
            
            # Take screenshot for visual record
            screenshot_path = project_root / "dashboard_visual_validation.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"\n13. Screenshot saved: {screenshot_path}")
            
            browser.close()
            
    finally:
        # Stop server
        print("\n14. Stopping dashboard server...")
        server_process.terminate()
        server_process.wait()
        print("   ✅ Server stopped")
    
    # Summary
    print("\n" + "=" * 70)
    print("PLAYWRIGHT VISUAL INSPECTION SUMMARY")
    print("=" * 70)
    
    if errors:
        print(f"\n❌ FAILED: {len(errors)} visual validation errors")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
        return False, errors
    else:
        print("\n✅ ALL VISUAL VALIDATIONS PASSED")
        print("\nValidated:")
        print("  ✅ Table 1 (Territory Summary): TOTAL row at top")
        print("  ✅ Table 2 (Code Quality): TOTAL row at top")
        print("  ✅ Live Sovereign Log: Has scrollbar")
        print("  ✅ Real-Time Event Log: Has scrollbar")
        print("  ✅ Purpose descriptions: All visible")
        print("  ✅ JavaScript: All files loaded correctly")
        print("  ✅ MCP Hardening: 100% displayed in dashboard")
        return True, []


if __name__ == "__main__":
    success, errors = run_playwright_visual_tests()
    sys.exit(0 if success else 1)
