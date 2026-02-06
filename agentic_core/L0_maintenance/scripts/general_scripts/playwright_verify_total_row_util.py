#!/usr/bin/env python3
"""
Playwright verification script to confirm TOTAL row is at the top of both tables.
Forces cache clearing and takes screenshots for visual confirmation.
"""

import subprocess
import sys
import time
from pathlib import Path

from agentic_core.utils.security import safe_popen

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Verify TOTAL row position using Playwright with cache clearing."""
    print("=" * 70)
    print("PLAYWRIGHT VERIFICATION: TOTAL ROW POSITION")
    print("=" * 70)

    # Check if Playwright is available
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n❌ Playwright not installed!")
        print("\nInstall with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return 1

    # Start dashboard server
    print("\n1. Starting fresh dashboard server on port 8765...")
    dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"

    server_process = safe_popen(
        [sys.executable, "-m", "http.server", "8765"],
        cwd=str(dashboard_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(2)
    print("   ✅ Server started")

    try:
        with sync_playwright() as p:
            print("\n2. Launching browser with cache disabled...")
            # Launch with cache disabled to force fresh load
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-cache",
                    "--disable-application-cache",
                    "--disable-offline-load-stale-cache",
                ],
            )

            # Create context with no cache
            context = browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)

            # Disable cache at context level
            page = context.new_page()

            # Navigate to dashboard
            print("\n3. Navigating to dashboard (Strategic Health tab)...")
            page.goto("http://localhost:8765/autonomy_dashboard.html")
            page.wait_for_load_state("networkidle")

            # Click Strategic Health tab
            print("\n4. Clicking Strategic Health tab...")
            page.click('button[data-target="strategic"]')
            time.sleep(2)  # Wait for tab content to render

            # Take full page screenshot
            print("\n5. Taking full page screenshot...")
            screenshot_path = project_root / "strategic_health_verification.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"   ✅ Screenshot saved: {screenshot_path}")

            # Verify Table 1 (Territory Summary)
            print("\n6. Verifying Table 1 (Territory Summary)...")
            try:
                # Get the first data row in the table body
                first_row = page.locator("#kpiGrid table tbody tr").first
                first_row_text = first_row.text_content()

                if "TOTAL" in first_row_text:
                    print("   ✅ Table 1: TOTAL row is at the TOP")
                    table1_pass = True
                else:
                    print(f"   ❌ Table 1: TOTAL row NOT at top. First row: {first_row_text[:50]}")
                    table1_pass = False

                    # Debug: Get all rows to see order
                    all_rows = page.locator("#kpiGrid table tbody tr").all()
                    print(f"   📋 Table 1 has {len(all_rows)} rows")
                    for i, row in enumerate(all_rows[:3]):  # Show first 3 rows
                        text = row.text_content()
                        territory = text.split()[0] if text else "N/A"
                        print(f"      Row {i + 1}: {territory}")

            except Exception as e:
                print(f"   ❌ Table 1: Error checking - {e}")
                table1_pass = False

            # Verify Table 2 (Code Quality)
            print("\n7. Verifying Table 2 (Code Quality)...")
            try:
                # Get the first data row in the table body
                first_row = page.locator("#codeQualityGrid table tbody tr").first
                first_row_text = first_row.text_content()

                if "TOTAL" in first_row_text:
                    print("   ✅ Table 2: TOTAL row is at the TOP")
                    table2_pass = True
                else:
                    print(f"   ❌ Table 2: TOTAL row NOT at top. First row: {first_row_text[:50]}")
                    table2_pass = False

                    # Debug: Get all rows to see order
                    all_rows = page.locator("#codeQualityGrid table tbody tr").all()
                    print(f"   📋 Table 2 has {len(all_rows)} rows")
                    for i, row in enumerate(all_rows[:3]):  # Show first 3 rows
                        text = row.text_content()
                        territory = text.split()[0] if text else "N/A"
                        print(f"      Row {i + 1}: {territory}")

            except Exception as e:
                print(f"   ❌ Table 2: Error checking - {e}")
                table2_pass = False

            # Check JavaScript file loaded
            print("\n8. Checking JavaScript file freshness...")
            try:
                # Navigate directly to the JS file to check content
                js_response = page.goto("http://localhost:8765/js/renderers/table-renderer.js")
                js_content = js_response.text()

                if "Keep TOTAL at top" in js_content:
                    print("   ✅ JavaScript file has updated code")
                    js_pass = True
                else:
                    print("   ❌ JavaScript file still has OLD code")
                    js_pass = False

                    # Check for old comment
                    if "Keep TOTAL at end" in js_content:
                        print("   ⚠️  File contains OLD comment 'Keep TOTAL at end'")

            except Exception as e:
                print(f"   ❌ Error checking JS file: {e}")
                js_pass = False

            # Summary
            print("\n" + "=" * 70)
            print("VERIFICATION SUMMARY")
            print("=" * 70)
            print(f"Table 1 (Territory Summary): {'✅ PASS' if table1_pass else '❌ FAIL'}")
            print(f"Table 2 (Code Quality): {'✅ PASS' if table2_pass else '❌ FAIL'}")
            print(f"JavaScript File Updated: {'✅ PASS' if js_pass else '❌ FAIL'}")
            print(f"\nScreenshot: {screenshot_path}")

            if table1_pass and table2_pass and js_pass:
                print("\n✅ ALL VERIFICATIONS PASSED - TOTAL rows are at the top!")
                result = 0
            else:
                print("\n❌ VERIFICATION FAILED - TOTAL rows NOT at top or JS file not updated")
                print("\nPossible causes:")
                print("1. Browser still using cached JavaScript")
                print("2. Server serving cached files")
                print("3. Code changes not saved to disk")
                result = 1

            browser.close()
            return result

    finally:
        # Stop server
        print("\n9. Stopping dashboard server...")
        server_process.terminate()
        server_process.wait()
        print("   ✅ Server stopped")


if __name__ == "__main__":
    sys.exit(main())
