#!/usr/bin/env python3
"""
Browser-Based Dashboard Smoke Test (P0 - Critical Gap)
Uses Playwright to verify dashboard actually renders in browser.

This catches failures that Python tests miss:
- JavaScript execution errors
- DOM rendering failures
- Console errors
- Empty tables despite valid HTML
"""

import asyncio
import sys

try:
except ImportError:
    print("❌ ERROR: Playwright not installed")
    print("   Install with: pip install playwright")
    print("   Then run: playwright install chromium")
    sys.exit(1)


async def test_dashboard_browser():
    """Run browser-based smoke test on dashboard."""
    print("=" * 70)
    print("BROWSER-BASED DASHBOARD SMOKE TEST (P0)")
    print("=" * 70)

    async with async_playwright() as p:
        # Launch browser
        print("\n1. Launching Chromium...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Collect console messages
        console_messages = []
        errors = []

        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        try:
            # Navigate to dashboard
            print("2. Loading http://localhost:8080/autonomy_dashboard.html...")
            response = await page.goto(
                "http://localhost:8080/autonomy_dashboard.html", timeout=10000
            )

            if not response or response.status != 200:
                print(f"❌ FAILED: HTTP {response.status if response else 'NO RESPONSE'}")
                return False

            print(f"   ✅ HTTP {response.status} OK")

            # Wait for JavaScript to execute
            print("3. Waiting for JavaScript execution...")
            await page.wait_for_timeout(2000)

            # Check for console errors
            print("4. Checking console for errors...")
            error_messages = [msg for msg in console_messages if "[error]" in msg.lower()]

            if error_messages:
                print(f"   ❌ Found {len(error_messages)} console errors:")
                for err in error_messages[:5]:  # Show first 5
                    print(f"      {err}")
                return False

            if errors:
                print(f"   ❌ Found {len(errors)} page errors:")
                for err in errors[:5]:
                    print(f"      {err}")
                return False

            print("   ✅ No console errors")

            # Check if tables are populated
            print("5. Checking if tables are populated...")

            # Check #kpiGrid has content
            kpi_grid = await page.query_selector("#kpiGrid")
            if not kpi_grid:
                print("   ❌ #kpiGrid element not found")
                return False

            kpi_content = await kpi_grid.inner_html()
            if len(kpi_content) < 100:
                print(f"   ❌ #kpiGrid is empty or too small ({len(kpi_content)} chars)")
                print(f"      Content preview: {kpi_content[:200]}")
                return False

            # Count table rows
            rows = await page.query_selector_all("#kpiGrid .territory-row")
            row_count = len(rows)

            if row_count < 20:
                print(f"   ❌ Expected >20 territory rows, found {row_count}")
                return False

            print(f"   ✅ Tables populated: {row_count} territory rows")

            # Check for specific data
            print("6. Verifying TOTAL row data...")
            total_row = await page.query_selector("#kpiGrid .territory-row:first-child")
            if not total_row:
                print("   ❌ TOTAL row not found")
                return False

            total_text = await total_row.inner_text()
            if "TOTAL" not in total_text:
                print(f"   ❌ TOTAL row doesn't contain 'TOTAL': {total_text[:100]}")
                return False

            print("   ✅ TOTAL row verified")

            # Success
            print("\n" + "=" * 70)
            print("✅ ALL BROWSER TESTS PASSED")
            print("=" * 70)
            print("Dashboard renders correctly:")
            print("  - HTTP 200 OK")
            print("  - No console errors")
            print(f"  - {row_count} territory rows rendered")
            print("  - TOTAL row present")
            print("=" * 70)

            return True

        except Exception as e:
            print(f"\n❌ EXCEPTION: {e}")
            print("\nConsole messages:")
            for msg in console_messages[-10:]:  # Last 10 messages
                print(f"  {msg}")
            return False

        finally:
            await browser.close()


def main():
    """Main entry point."""
    try:
        result = asyncio.run(test_dashboard_browser())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()