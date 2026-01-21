#!/usr/bin/env python3
"""
Detailed RCA for Strategic Health Tab - Critical Data Delay
Diagnoses why Observations, Actions, Table 1, and Table 2 are not loading.
"""

import http.server
import socketserver
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

project_root = Path(__file__).parent.parent


def diagnose_strategic_health():
    """Deep inspection of Strategic Health tab components."""

    # Start HTTP Server
    PORT = 8765
    dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dashboard_dir), **kwargs)

        def log_message(self, format, *args):
            pass  # Quiet

    def serve():
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()

    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()
    print(f"[SERVER] Started at http://localhost:{PORT}")
    time.sleep(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Capture console
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

        # Capture errors
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))

        print("\n[LOADING] Dashboard...")
        page.goto(f"http://localhost:{PORT}/autonomy_dashboard.html", timeout=30000)

        # Wait for initialization
        print("[WAITING] For dashboard to initialize...")
        time.sleep(5)

        print("\n" + "=" * 80)
        print("RCA: STRATEGIC HEALTH TAB DIAGNOSIS")
        print("=" * 80)

        # 1. Check all data variables
        print("\n1. DATA VARIABLES STATUS:")
        data_check = page.evaluate("""
            () => {
                return {
                    dashboardData: {
                        exists: typeof window.dashboardData !== 'undefined',
                        isArray: Array.isArray(window.dashboardData),
                        length: window.dashboardData ? window.dashboardData.length : 0
                    },
                    realAgentData: {
                        exists: typeof window.realAgentData !== 'undefined',
                        type: typeof window.realAgentData
                    },
                    observations: {
                        exists: typeof window.observations !== 'undefined',
                        isArray: Array.isArray(window.observations),
                        length: window.observations ? window.observations.length : 0
                    },
                    recommendations: {
                        exists: typeof window.recommendations !== 'undefined',
                        isArray: Array.isArray(window.recommendations),
                        length: window.recommendations ? window.recommendations.length : 0
                    }
                };
            }
        """)

        for var_name, info in data_check.items():
            status = "✅" if info.get("exists") else "❌"
            details = []
            if "isArray" in info:
                details.append(f"isArray={info['isArray']}")
            if "length" in info:
                details.append(f"length={info['length']}")
            if "type" in info:
                details.append(f"type={info['type']}")
            print(f"   {status} {var_name}: exists={info['exists']} {', '.join(details)}")

        # 2. Check Table 1 and Table 2
        print("\n2. TABLE RENDERING STATUS:")
        table_check = page.evaluate("""
            () => {
                const table1Container = document.getElementById('kpiGrid');
                const table2Container = document.getElementById('codeQualityGrid');

                const table1 = table1Container ? table1Container.querySelector('table') : null;
                const table2 = table2Container ? table2Container.querySelector('table') : null;

                return {
                    table1: {
                        containerExists: !!table1Container,
                        tableExists: !!table1,
                        rowCount: table1 ? table1.querySelectorAll('tbody tr').length : 0,
                        innerHTML: table1Container ? table1Container.innerHTML.substring(0, 200) : 'N/A'
                    },
                    table2: {
                        containerExists: !!table2Container,
                        tableExists: !!table2,
                        rowCount: table2 ? table2.querySelectorAll('tbody tr').length : 0,
                        innerHTML: table2Container ? table2Container.innerHTML.substring(0, 200) : 'N/A'
                    }
                };
            }
        """)

        for table_name, info in table_check.items():
            status = "✅" if info["tableExists"] and info["rowCount"] > 0 else "❌"
            print(f"   {status} {table_name}:")
            print(f"      Container exists: {info['containerExists']}")
            print(f"      Table exists: {info['tableExists']}")
            print(f"      Row count: {info['rowCount']}")
            if info["rowCount"] == 0:
                print(f"      innerHTML preview: {info['innerHTML'][:100]}...")

        # 3. Check Observations and Recommendations sections
        print("\n3. OBSERVATIONS & RECOMMENDATIONS STATUS:")
        obs_check = page.evaluate("""
            () => {
                const macroObs = document.getElementById('macro-observations');
                const metricObs = document.getElementById('metric-observations');
                const prioritizedRecs = document.getElementById('prioritized-recommendations');

                return {
                    macroObservations: {
                        exists: !!macroObs,
                        innerHTML: macroObs ? macroObs.innerHTML.substring(0, 200) : 'N/A',
                        hasContent: macroObs ? macroObs.innerHTML.length > 50 : false
                    },
                    metricObservations: {
                        exists: !!metricObs,
                        innerHTML: metricObs ? metricObs.innerHTML.substring(0, 200) : 'N/A',
                        hasContent: metricObs ? metricObs.innerHTML.length > 50 : false
                    },
                    prioritizedRecommendations: {
                        exists: !!prioritizedRecs,
                        innerHTML: prioritizedRecs ? prioritizedRecs.innerHTML.substring(0, 200) : 'N/A',
                        hasContent: prioritizedRecs ? prioritizedRecs.innerHTML.length > 50 : false
                    }
                };
            }
        """)

        for section_name, info in obs_check.items():
            status = "✅" if info["hasContent"] else "❌"
            print(f"   {status} {section_name}:")
            print(f"      Container exists: {info['exists']}")
            print(f"      Has content: {info['hasContent']}")
            if not info["hasContent"]:
                print(f"      innerHTML: {info['innerHTML'][:100]}...")

        # 4. Check render functions
        print("\n4. RENDER FUNCTIONS AVAILABILITY:")
        func_check = page.evaluate("""
            () => {
                return {
                    renderTerritorySummaryTable: typeof window.renderTerritorySummaryTable === 'function',
                    renderCodeQualityTable: typeof window.renderCodeQualityTable === 'function',
                    renderObservations: typeof window.renderObservations === 'function',
                    renderRecommendations: typeof window.renderRecommendations === 'function',
                    renderMacroObservations: typeof window.renderMacroObservations === 'function',
                    renderMetricObservations: typeof window.renderMetricObservations === 'function'
                };
            }
        """)

        for func_name, exists in func_check.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {func_name}: {exists}")

        # 5. Check for error banner
        print("\n5. ERROR BANNER STATUS:")
        banner = page.locator("#data-load-error-banner").count()
        print(f"   {'❌' if banner > 0 else '✅'} Error banner visible: {banner > 0}")

        # 6. Console messages
        print(f"\n6. CONSOLE MESSAGES ({len(console_msgs)}):")
        for msg in console_msgs[-15:]:
            print(f"   {msg}")

        # 7. Page errors
        print(f"\n7. PAGE ERRORS ({len(errors)}):")
        if errors:
            for err in errors:
                print(f"   ❌ {err}")
        else:
            print("   ✅ No page errors")

        # Take screenshot
        print("\n8. SCREENSHOT:")
        page.screenshot(path=str(project_root / "rca_strategic_health.png"), full_page=True)
        print("   Saved: rca_strategic_health.png")

        # Analysis
        print("\n" + "=" * 80)
        print("ROOT CAUSE ANALYSIS")
        print("=" * 80)

        issues = []

        if not data_check["dashboardData"]["exists"]:
            issues.append("CRITICAL: dashboardData not loaded - Table 1 & 2 cannot render")
        elif data_check["dashboardData"]["length"] == 0:
            issues.append("CRITICAL: dashboardData is empty - Table 1 & 2 have no data")

        if not data_check["observations"]["exists"]:
            issues.append("CRITICAL: observations variable not loaded - Observations section empty")
        elif data_check["observations"]["length"] == 0:
            issues.append("WARNING: observations array is empty")

        if not data_check["recommendations"]["exists"]:
            issues.append("CRITICAL: recommendations variable not loaded - Actions section empty")
        elif data_check["recommendations"]["length"] == 0:
            issues.append("WARNING: recommendations array is empty")

        if not table_check["table1"]["tableExists"]:
            issues.append(
                "CRITICAL: Table 1 not rendered - renderTerritorySummaryTable may have failed"
            )

        if not table_check["table2"]["tableExists"]:
            issues.append("CRITICAL: Table 2 not rendered - renderCodeQualityTable may have failed")

        if issues:
            print("\nIDENTIFIED ISSUES:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ No critical issues identified - dashboard should be rendering correctly")

        input("\nPress Enter to close browser...")
        browser.close()


if __name__ == "__main__":
    diagnose_strategic_health()
