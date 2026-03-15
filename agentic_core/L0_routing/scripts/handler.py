#!/usr/bin/env python3
"""
Deep RCA using Playwright to diagnose dashboard data load error.
Captures console errors, network requests, and JavaScript state.
"""

import http.server
import socketserver
import threading
import time
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "handler", "L0")
_emit_routes_through("p1", "handler", "L0")
_emit_escalates_to_human("p1", "handler", "L0")
_emit_reads_policy_state("p1", "handler", "L0")

_emit_records_execution_trace("p0", "evidence", "handler")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "handler", "p0_governance")
_emit_snapshots_state("p0", "handler", "state_snapshot")

project_root = Path(__file__).parent.parent


def debug_dashboard():
    """Use Playwright to deeply inspect dashboard loading."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed")
        return False

    # Start HTTP Server
    PORT = 8765
    dashboard_dir = project_root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dashboard_dir), **kwargs)

        def log_message(self, format, *args):
            print(f"   [SERVER] {format % args}")

    def serve():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()

    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()
    print(f"[SERVER] Started at http://localhost:{PORT}")
    time.sleep(DEFAULT_SLEEP)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible browser for debugging
        page = browser.new_page()

        # Capture console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # Capture page errors
        page_errors = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        # Capture failed requests
        failed_requests = []
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.url} - {req.failure}"))

        print(f"\n[LOADING] http://localhost:{PORT}/autonomy_dashboard.html")
        # guardian: allow-magic-config
        page.goto(f"http://localhost:{PORT}/autonomy_dashboard.html", timeout=DEFAULT_TIMEOUT)
        time.sleep(DEFAULT_SLEEP)  # Wait for everything to load

        print("\n" + "=" * 70)
        print("DIAGNOSTIC RESULTS")
        print("=" * 70)

        # Check if dashboardData loaded
        print("\n1. Checking dashboardData variable...")
        dashboard_data_check = page.evaluate("""
            () => {
                return {
                    exists: typeof dashboardData !== 'undefined',
                    type: typeof dashboardData,
                    length: typeof dashboardData !== 'undefined' ? dashboardData.length : 0,
                    sample: typeof dashboardData !== 'undefined' && dashboardData.length > 0 ? dashboardData[0] : null
                };
            }
        """)

        if dashboard_data_check["exists"]:
            print("   ✅ dashboardData exists")
            print(f"   ✅ Type: {dashboard_data_check['type']}")
            print(f"   ✅ Length: {dashboard_data_check['length']} territories")
            if dashboard_data_check["sample"]:
                print(f"   ✅ Sample: {dashboard_data_check['sample'].get('Territory', 'N/A')}")
        else:
            print("   ❌ dashboardData does NOT exist")
            print(f"   Type: {dashboard_data_check['type']}")

        # Check other data files
        print("\n2. Checking other data variables...")
        other_data = page.evaluate("""
            () => {
                return {
                    agentData: typeof agentData !== 'undefined',
                    recommendations: typeof recommendations !== 'undefined',
                    observations: typeof observations !== 'undefined'
                };
            }
        """)

        for var_name, exists in other_data.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {var_name}: {exists}")

        # Check for error message in DOM
        print("\n3. Checking for error message in DOM...")
        error_msg = page.locator("text=Data Load Error").count()
        if error_msg > 0:
            print(f"   ❌ Found {error_msg} 'Data Load Error' message(s)")
            error_content = (
                page.locator(".error-message").text_content()
                if page.locator(".error-message").count() > 0
                else "N/A"
            )
            print(f"   Error content: {error_content}")
        else:
            print("   ✅ No 'Data Load Error' message found")

        # Console messages
        print(f"\n4. Console Messages ({len(console_messages)}):")
        if console_messages:
            for msg in console_messages[-20:]:  # Last 20
                print(f"   {msg}")
        else:
            print("   (none)")

        # Page errors
        print(f"\n5. Page Errors ({len(page_errors)}):")
        if page_errors:
            for err in page_errors:
                print(f"   ❌ {err}")
        else:
            print("   ✅ No page errors")

        # Failed requests
        print(f"\n6. Failed Requests ({len(failed_requests)}):")
        if failed_requests:
            for req in failed_requests:
                print(f"   ❌ {req}")
        else:
            print("   ✅ No failed requests")

        # Check script tags
        print("\n7. Checking script tags...")
        script_tags = page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script[src*="data/"]'));
                return scripts.map(s => ({
                    src: s.src,
                    loaded: s.readyState || 'unknown'
                }));
            }
        """)

        if script_tags:
            for script in script_tags:
                print(f"   Script: {script['src']}")
                print(f"     State: {script['loaded']}")
        else:
            print("   ❌ No data script tags found")

        # Take screenshot
        screenshot_path = project_root / "dashboard_debug.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"\n8. Screenshot saved: {screenshot_path}")

        print("\n" + "=" * 70)
        print("ANALYSIS")
        print("=" * 70)

        if not dashboard_data_check["exists"]:
            print("\n❌ ROOT CAUSE: dashboardData variable is not defined")
            print("\nPossible causes:")
            print("  1. data/dashboard_data.js file not loading")
            print("  2. JavaScript syntax error in dashboard_data.js")
            print("  3. Script tag not present or incorrect path")
            print("  4. File served with wrong MIME type")
        elif error_msg > 0:
            print("\n❌ ROOT CAUSE: Error message displayed despite data being loaded")
            print("\nPossible causes:")
            print("  1. Error check runs before data loads")
            print("  2. Error condition incorrectly triggered")
        else:
            print("\n✅ Data appears to be loading correctly")

        input("\nPress Enter to close browser and continue...")
        browser.close()


if __name__ == "__main__":
    debug_dashboard()
