#!/usr/bin/env python3
"""
Simple Playwright test to verify 100% MCP Hardening is displayed in dashboard.
"""

import subprocess
import sys
import time
from pathlib import Path

from agentic_core.utils.security import safe_popen

project_root = Path(__file__).parent.parent


def test_mcp_hardening():
    """Test that 100% MCP Hardening is displayed in dashboard."""
    try:
        from playwright.sync_api import sync_playwright
    except (ImportError, NameError, AttributeError):
        print("❌ Playwright not installed")
        return False

    print("Starting dashboard server...")
    dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"
    server = safe_popen(
        [sys.executable, "-m", "http.server", "8765"],
        cwd=str(dashboard_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("Loading dashboard...")
            page.goto("http://localhost:8765/autonomy_dashboard.html")
            time.sleep(5)  # Wait for JS to load

            # Check if dashboardData loaded
            result = page.evaluate("""
                () => {
                    if (typeof dashboardData === 'undefined') {
                        return {success: false, error: 'dashboardData not loaded'};
                    }

                    // Find TOTAL row
                    const totalRow = dashboardData.find(r => r.Territory === 'TOTAL');
                    if (!totalRow) {
                        return {success: false, error: 'TOTAL row not found'};
                    }

                    const mcpPct = totalRow['MCP Hardened %'];
                    return {
                        success: mcpPct === 100.0,
                        mcpPct: mcpPct,
                        totalAgents: totalRow.Total
                    };
                }
            """)

            browser.close()

            if result["success"]:
                print(f"✅ MCP Hardening: 100% ({result['totalAgents']} agents)")
                return True
            else:
                if "error" in result:
                    print(f"❌ {result['error']}")
                else:
                    print(f"❌ MCP Hardening: {result.get('mcpPct', 'N/A')}% (expected 100%)")
                return False

    finally:
        server.terminate()
        server.wait()

    return False


if __name__ == "__main__":
    success = test_mcp_hardening()
    sys.exit(0 if success else 1)
