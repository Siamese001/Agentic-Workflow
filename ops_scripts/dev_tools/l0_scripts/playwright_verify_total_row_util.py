"""
Playwright verification script to confirm TOTAL row is at the top of both tables.
Uses MCPConnectionManager (mcp8_playwright_*) as primary path with sync_api fallback.
"""
import asyncio
import subprocess
import sys
import time
from pathlib import Path

from agentic_core.utils.security_util import safe_popen

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    DEFAULT_SLEEP,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "playwright_verify_total_row_util")
_emit_applies_guardrail("p0", "playwright_verify_total_row_util", "p0_governance")
_emit_reads_policy_state("p0", "playwright_verify_total_row_util", "policy_binding")
_emit_snapshots_state("p0", "playwright_verify_total_row_util", "state_snapshot")
emit_replay_key("p0", "playwright_verify_total_row_util")
emit_determinism_digest("p0", "playwright_verify_total_row_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

project_root = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

DASHBOARD_URL = 'http://localhost:8765/autonomy_dashboard.html'
STRATEGIC_TAB = 'button[data-target="strategic"]'
SCREENSHOT_NAME = 'strategic_health_verification'


async def _verify_via_mcp() -> dict:
    """Primary verification path using MCPConnectionManager (mcp8_playwright_*)."""
    from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager

    mcp = MCPConnectionManager()
    await mcp.connect('playwright')

    await mcp.call_tool('playwright_navigate', {'url': DASHBOARD_URL})
    await mcp.call_tool('playwright_click', {'selector': STRATEGIC_TAB})
    screenshot_result = await mcp.call_tool(
        'playwright_screenshot',
        {
            'name': SCREENSHOT_NAME,
            'savePng': True,
            'fullPage': True,
            'downloadsDir': str(project_root),
        },
    )
    table1_html_result = await mcp.call_tool(
        'playwright_get_html', {'selector': '#kpiGrid table tbody'}
    )
    table2_html_result = await mcp.call_tool(
        'playwright_get_html', {'selector': '#codeQualityGrid table tbody'}
    )
    await mcp.call_tool('playwright_navigate', {'url': 'http://localhost:8765/js/renderers/table-renderer.js'})
    js_text_result = await mcp.call_tool('playwright_get_text', {})

    table1_html = table1_html_result if isinstance(table1_html_result, str) else str(table1_html_result)
    table2_html = table2_html_result if isinstance(table2_html_result, str) else str(table2_html_result)
    js_content = js_text_result if isinstance(js_text_result, str) else str(js_text_result)
    screenshot_path = project_root / f'{SCREENSHOT_NAME}.png'

    return {
        'table1_pass': 'TOTAL' in table1_html[:500],
        'table2_pass': 'TOTAL' in table2_html[:500],
        'js_pass': 'Keep TOTAL at top' in js_content,
        'js_old_flag': 'Keep TOTAL at end' in js_content,
        'screenshot_path': str(screenshot_path),
        'source': 'mcp',
    }


def _verify_via_sync_playwright() -> dict:
    """Fallback verification path using playwright.sync_api."""
    from playwright.sync_api import sync_playwright

    screenshot_path = project_root / f'{SCREENSHOT_NAME}.png'
    table1_pass = table2_pass = js_pass = js_old_flag = False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-cache', '--disable-application-cache'],
        )
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.goto(DASHBOARD_URL)
        page.wait_for_load_state('networkidle')
        page.click(STRATEGIC_TAB)
        time.sleep(DEFAULT_SLEEP)
        page.screenshot(path=str(screenshot_path), full_page=True)
        try:
            first_row_text = page.locator('#kpiGrid table tbody tr').first.text_content() or ''
            table1_pass = 'TOTAL' in first_row_text
        # guardian: allow-silent-swallow
        except Exception:
            pass
        try:
            first_row_text = page.locator('#codeQualityGrid table tbody tr').first.text_content() or ''
            table2_pass = 'TOTAL' in first_row_text
        # guardian: allow-silent-swallow
        except Exception:
            pass
        try:
            js_response = page.goto('http://localhost:8765/js/renderers/table-renderer.js')
            js_content = js_response.text() if js_response else ''
            js_pass = 'Keep TOTAL at top' in js_content
            js_old_flag = 'Keep TOTAL at end' in js_content
        # guardian: allow-silent-swallow
        except Exception:
            pass
        browser.close()

    return {
        'table1_pass': table1_pass,
        'table2_pass': table2_pass,
        'js_pass': js_pass,
        'js_old_flag': js_old_flag,
        'screenshot_path': str(screenshot_path),
        'source': 'sync_api',
    }


def main():
    """Verify TOTAL row position using MCP-routed Playwright tools."""
    print('=' * 70)
    print('PLAYWRIGHT VERIFICATION: TOTAL ROW POSITION')
    print('=' * 70)

    print('\n1. Starting fresh dashboard server on port 8765...')
    dashboard_dir = project_root / AGENTIC_CORE_DIR / 'L6_observability' / 'dashboards'
    server_process = safe_popen(
        [sys.executable, '-m', 'http.server', '8765'],
        cwd=str(dashboard_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(DEFAULT_SLEEP)
    print('   Server started')

    try:
        print('\n2. Running MCP-routed Playwright verification...')
        try:
            results = asyncio.run(_verify_via_mcp())
            print(f'   Source: {results["source"]}')
        # guardian: allow-silent-swallow
        except Exception as mcp_err:
            print(f'   MCP path unavailable ({mcp_err}) — falling back to sync_playwright')
            try:
                results = _verify_via_sync_playwright()
                print(f'   Source: {results["source"]}')
            except ImportError:
                print('   playwright not installed — pip install playwright && playwright install chromium')
                return 1

        table1_pass = results['table1_pass']
        table2_pass = results['table2_pass']
        js_pass = results['js_pass']
        screenshot_path = results['screenshot_path']

        print(f'\n3. Screenshot saved: {screenshot_path}')
        print('\n4. Table 1 (Territory Summary): ' + ('PASS' if table1_pass else 'FAIL - TOTAL row NOT at top'))
        print('   Table 2 (Code Quality):       ' + ('PASS' if table2_pass else 'FAIL - TOTAL row NOT at top'))
        print('   JavaScript File Updated:       ' + ('PASS' if js_pass else 'FAIL - OLD code detected'))
        if results.get('js_old_flag'):
            print("   Warning: File contains OLD comment 'Keep TOTAL at end'")

        print('\n' + '=' * 70)
        print('VERIFICATION SUMMARY')
        print('=' * 70)
        print(f'Table 1 (Territory Summary): {"PASS" if table1_pass else "FAIL"}')
        print(f'Table 2 (Code Quality):       {"PASS" if table2_pass else "FAIL"}')
        print(f'JavaScript File Updated:       {"PASS" if js_pass else "FAIL"}')
        print(f'\nScreenshot: {screenshot_path}')

        if table1_pass and table2_pass and js_pass:
            print('\nALL VERIFICATIONS PASSED - TOTAL rows are at the top!')
            return 0
        print('\nVERIFICATION FAILED - check output above')
        return 1
    finally:
        print('\n5. Stopping dashboard server...')
        server_process.terminate()
        server_process.wait()
        print('   Server stopped')


if __name__ == '__main__':
    sys.exit(main())
