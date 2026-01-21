#!/usr/bin/env python3
"""
Live diagnosis of user's dashboard issue.
Checks what's actually happening when browser loads the dashboard.
"""
from playwright.sync_api import sync_playwright
import time

def diagnose():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Capture all console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # Capture network requests
        requests = []
        page.on("request", lambda req: requests.append(f"→ {req.method} {req.url}"))
        page.on("response", lambda res: requests.append(f"← {res.status} {res.url}"))

        print("Loading dashboard...")
        page.goto("http://localhost:8765/autonomy_dashboard.html", timeout=30000)

        print("\nWaiting 5 seconds for data to load...")
        time.sleep(5)

        # Check variables
        check = page.evaluate("""
            () => {
                return {
                    dashboardData: typeof window.dashboardData !== 'undefined' ? 'EXISTS' : 'MISSING',
                    dashboardDataLength: typeof window.dashboardData !== 'undefined' ? window.dashboardData.length : 0,
                    realAgentData: typeof window.realAgentData !== 'undefined' ? 'EXISTS' : 'MISSING',
                    globalAgentData: typeof window.globalAgentData !== 'undefined' ? 'EXISTS' : 'MISSING',
                    recommendations: typeof window.recommendations !== 'undefined' ? 'EXISTS' : 'MISSING',
                    observations: typeof window.observations !== 'undefined' ? 'EXISTS' : 'MISSING'
                };
            }
        """)

        print("\n" + "="*70)
        print("DIAGNOSIS RESULTS")
        print("="*70)

        print("\n1. Data Variables:")
        for key, value in check.items():
            status = "✅" if value == 'EXISTS' or (isinstance(value, int) and value > 0) else "❌"
            print(f"   {status} {key}: {value}")

        print(f"\n2. Console Messages ({len(console_messages)}):")
        for msg in console_messages[-10:]:
            print(f"   {msg}")

        print(f"\n3. Network Requests (last 10):")
        for req in requests[-10:]:
            print(f"   {req}")

        # Check for error banner
        banner = page.locator("#data-load-error-banner").count()
        print(f"\n4. Error Banner: {'VISIBLE' if banner > 0 else 'NOT VISIBLE'}")

        print("\n5. Taking screenshot...")
        page.screenshot(path="dashboard_diagnosis.png", full_page=True)
        print("   Screenshot saved: dashboard_diagnosis.png")

        input("\nPress Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    diagnose()
