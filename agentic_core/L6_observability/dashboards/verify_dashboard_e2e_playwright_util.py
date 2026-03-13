"""
Automated E2E Dashboard Verification with Playwright
Fully automated browser-based verification that eliminates:
- Manual hard refresh
- Manual console inspection
- cache-related false alarms

This script:
1. Kills existing servers
2. Starts fresh HTTP server
3. Opens real browser (configurable headless mode)
4. Waits for tables to render
5. Asserts row count, TOTAL values, no JS errors
6. Takes screenshot on success/failure

Usage:
    python verify_dashboard_e2e_playwright_util.py              # Visible browser
    python verify_dashboard_e2e_playwright_util.py --headless   # Headless mode
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP, DEFAULT_TIMEOUT

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ ERROR: Playwright not installed")
    print("   Install with: pip install playwright")
    print("   Then run: playwright install chromium")
    sys.exit(1)
try:
    import psutil
except ImportError:
    print("❌ ERROR: psutil not installed")
    print("   Install with: pip install psutil")
    sys.exit(1)
DASHBOARD_URL = "http://localhost:8080/autonomy_dashboard.html"
EXPECTED_MIN_ROWS = 29
PORT = 8080


def kill_existing_servers():
    """Kill any existing processes on port 8080 (cross-platform using psutil)."""
    print("🛑 Killing existing servers on port 8080...")
    try:
        pids_to_kill = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                connections = proc.net_connections(kind="inet")
                for conn in connections:
                    if hasattr(conn, "laddr") and conn.laddr.port == PORT:
                        if conn.status == psutil.CONN_LISTEN or conn.status == "LISTEN":
                            pids_to_kill.append(proc.pid)
                            break
            except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                continue
        if pids_to_kill:
            for pid in pids_to_kill:
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    print(f"   Terminated process {pid} ({proc.name()})")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"   ⚠️  Could not terminate {pid}: {e}")
            time.sleep(DEFAULT_SLEEP)
            for pid in pids_to_kill:
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        proc.kill()
                        print(f"   Force killed process {pid}")
                except psutil.NoSuchProcess:
                    pass
            print("   ✅ Existing servers killed")
        else:
            print("   ℹ️  No existing servers on port 8080")
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"   ⚠️  Could not kill servers: {e}")


def start_server():
    """Start HTTP server on port 8080."""
    from agentic_core.utils.security_util import safe_popen

    print(f"\n🚀 Starting HTTP server on port {PORT}...")
    serve_path = Path(__file__).parent / "serve_dashboard.py"
    proc = safe_popen([sys.executable, str(serve_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(DEFAULT_SLEEP)
    if proc.poll() is not None:
        print("   ❌ Server failed to start")
        return None
    print(f"   ✅ Server started (PID: {proc.pid})")
    return proc


def verify_with_playwright(headless: bool = False, screenshot_dir: Path = None):
    """
    Verify dashboard renders correctly using Playwright.

    Args:
        headless: Run browser in headless mode
        screenshot_dir: Directory to save screenshots (defaults to script dir)

    Returns:
        bool: True if verification passed, False otherwise
    """
    if screenshot_dir is None:
        screenshot_dir = Path(__file__).parent
    print("\n" + "=" * 80)
    print("AUTOMATED BROWSER VERIFICATION (Playwright)")
    print("=" * 80)
    print(f"Mode: {('Headless' if headless else 'Visible')}")
    print(f"URL: {DASHBOARD_URL}")
    print("=" * 80)
    console_messages = []
    errors = []
    try:
        with sync_playwright() as p:
            print("\n1. Launching Chromium...")
            browser = p.chromium.launch(headless=headless, slow_mo=100 if not headless else 0)
            context = browser.new_context()
            page = context.new_page()
            page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
            page.on("pageerror", lambda err: errors.append(str(err)))
            print("2. Clearing cache and cookies...")
            context.clear_cookies()
            cache_bust_url = f"{DASHBOARD_URL}?v={int(time.time())}"
            print(f"3. Navigating to: {cache_bust_url}")
            try:
                response = page.goto(cache_bust_url, wait_until="networkidle", timeout=DEFAULT_TIMEOUT)
                if not response or response.status != 200:
                    print(f"   ❌ HTTP {(response.status if response else 'NO RESPONSE')}")
                    raise Exception(
                        f"Failed to load page: HTTP {(response.status if response else 'timeout')}"
                    )
                print(f"   ✅ HTTP {response.status} OK")
            except PlaywrightTimeout:
                print("   ❌ Page load timeout (15s)")
                raise
            print("4. Waiting for tables to render...")
            try:
                page.wait_for_selector("#kpiGrid table tbody tr", timeout=DEFAULT_TIMEOUT)
                print("   ✅ Tables found in DOM")
            except PlaywrightTimeout:
                print("   ❌ Tables did not appear within 10s")
                raise
            time.sleep(DEFAULT_SLEEP)
            print("5. Verifying table content...")
            row_locator = page.locator("#kpiGrid table tbody tr")
            row_count = row_locator.count()
            print(f"   Found {row_count} table rows")
            if row_count < EXPECTED_MIN_ROWS:
                raise AssertionError(f"Expected ≥{EXPECTED_MIN_ROWS} rows, got {row_count}")
            print(f"   ✅ Row count OK ({row_count} ≥ {EXPECTED_MIN_ROWS})")
            print("6. Verifying TOTAL row data...")
            try:
                total_row = page.locator('tr:has-text("TOTAL")').first
                total_cell = total_row.locator("td").nth(1)
                total_text = total_cell.inner_text().strip()
                total_agents = int(total_text)
                print(f"   TOTAL agents: {total_agents}")
                if not 200 < total_agents < 400:
                    raise AssertionError(f"TOTAL agents value looks wrong: {total_agents} (expected 200-400)")
                heal_cap_cell = total_row.locator("td").nth(2)
                heal_cap_full_text = heal_cap_cell.inner_text().strip()
                heal_cap_text = heal_cap_full_text.split("%")[0].split("(")[0].split("\n")[0].strip()
                heal_cap = float(heal_cap_text)
                print(f"   Heal Cap %: {heal_cap}%")
                if heal_cap < 80:
                    raise AssertionError(f"Heal Cap too low: {heal_cap}% (expected ≥80%)")
                print(f"   ✅ TOTAL row verified ({total_agents} agents, Heal Cap {heal_cap}%)")
            except ValueError as e:
                print(f"   ❌ Failed to parse TOTAL row values: {e}")
                raise
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"   ❌ Failed to verify TOTAL row: {e}")
                raise
            print("7. Checking for JavaScript errors...")
            error_messages = [msg for msg in console_messages if "error" in msg.lower()]
            if error_messages:
                print(f"   ❌ Found {len(error_messages)} console errors:")
                for err in error_messages[:5]:
                    print(f"      {err}")
                raise AssertionError(f"{len(error_messages)} console errors detected")
            if errors:
                print(f"   ❌ Found {len(errors)} page errors:")
                for err in errors[:5]:
                    print(f"      {err}")
                raise AssertionError(f"{len(errors)} page errors detected")
            print("   ✅ No JavaScript errors")
            print("8. Taking screenshot...")
            screenshot_path = screenshot_dir / "dashboard_verification_success.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"   ✅ Screenshot saved: {screenshot_path}")
            print("\n" + "=" * 80)
            print("✅ DASHBOARD VERIFICATION PASSED")
            print("=" * 80)
            print("✓ HTTP 200 OK")
            print(f"✓ {row_count} territory rows rendered")
            print(f"✓ TOTAL row: {total_agents} agents")
            print("✓ No JavaScript errors")
            print(f"✓ Screenshot: {screenshot_path.name}")
            print("=" * 80)
            browser.close()
            return True
    # guardian: allow-silent-swallow
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ DASHBOARD VERIFICATION FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        print("=" * 80)
        try:
            screenshot_path = screenshot_dir / "dashboard_verification_failure.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"\n📸 Failure screenshot saved: {screenshot_path}")
        # guardian: allow-silent-swallow
        except:
            pass
        if console_messages:
            print("\nConsole messages (last 10):")
            for msg in console_messages[-10:]:
                print(f"  {msg}")
        try:
            browser.close()
        # guardian: allow-silent-swallow
        except:
            pass
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated Dashboard E2E Verification with Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run browser in headless mode (no visible window)"
    )
    parser.add_argument(
        "--keep-server",
        action="store_true",
        help="Keep server running after verification (requires Ctrl+C to stop)",
    )
    args = parser.parse_args()
    print("=" * 80)
    print("AUTOMATED DASHBOARD E2E VERIFICATION (Playwright)")
    print("=" * 80)
    kill_existing_servers()
    server = start_server()
    if not server:
        print("\n❌ Failed to start server")
        sys.exit(1)
    success = False
    try:
        success = verify_with_playwright(headless=args.headless)
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"\n❌ Critical failure: {e}")
    if args.keep_server and success:
        print("\n" + "=" * 80)
        print("Server is running. Press Ctrl+C to stop.")
        print("=" * 80)
        try:
            server.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping server...")
    try:
        server.terminate()
        server.wait(timeout=DEFAULT_TIMEOUT)
        print("✅ Server stopped")
    # guardian: allow-silent-swallow
    except:
        try:
            server.kill()
        # guardian: allow-silent-swallow
        except:
            pass
    sys.exit(0 if success else 1)


async def mcp_verify_dashboard(url: str = DASHBOARD_URL, expected_min_rows: int = EXPECTED_MIN_ROWS) -> dict:
    """
    Verify the dashboard via live mcp12_* Playwright MCP tools.

    This is the programmatic entry point for use by BaseHealingOrchestrator
    and other agents — no subprocess, no CLI, no psutil required.

    Args:
        url: Dashboard URL to verify
        expected_min_rows: Minimum expected row count

    Returns:
        dict with keys: success (bool), text (str), screenshot_name (str), errors (list)
    """
    try:
        from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager

        mcp = MCPConnectionManager()
        errors: list[str] = []
        await mcp.call_tool("playwright_navigate", {"url": url, "waitUntil": "networkidle", "timeout": 15000})
        text_result = await mcp.call_tool("playwright_get_text", {})
        page_text: str = text_result if isinstance(text_result, str) else str(text_result)
        row_ok = page_text.count("TOTAL") >= 1
        rows_found = page_text.count("\n")
        if not row_ok:
            errors.append("TOTAL row not found in page text")
        if rows_found < expected_min_rows:
            errors.append(f"Expected >= {expected_min_rows} rows, found ~{rows_found}")
        ts = __import__("datetime").datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        screenshot_name = f"dashboard_verify_{ts}"
        await mcp.call_tool("playwright_screenshot", {"name": screenshot_name, "fullPage": True})
        success = len(errors) == 0
        return {
            "success": success,
            "text_preview": page_text[:500],
            "screenshot_name": screenshot_name,
            "errors": errors,
            "rows_found": rows_found,
        }
    # guardian: allow-silent-swallow
    except Exception as e:
        return {
            "success": False,
            "text_preview": "",
            "screenshot_name": "",
            "errors": [str(e)],
            "rows_found": 0,
        }


if __name__ == "__main__":
    main()
