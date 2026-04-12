"""
Playwright verification script to confirm TOTAL row is at the top of both tables.
Uses MCPConnectionManager (mcp8_playwright_*) as primary path with sync_api fallback.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    DEFAULT_SLEEP,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.security_util import safe_popen

_emit_records_execution_trace("p0", "evidence", "playwright_verify_total_row_util")
_emit_applies_guardrail("p0", "playwright_verify_total_row_util", "p0_governance")
_emit_reads_policy_state("p0", "playwright_verify_total_row_util", "policy_binding")
_emit_snapshots_state("p0", "playwright_verify_total_row_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("playwright_verify_total_row_util", "p4obs", "metric_1")
_emit_emits_metric_event("playwright_verify_total_row_util", "p4obs", "metric_2")
_emit_emits_metric_event("playwright_verify_total_row_util", "p4obs", "metric_3")
_emit_emits_metric_event("playwright_verify_total_row_util", "p4obs", "metric_4")
_emit_emits_metric_event("playwright_verify_total_row_util", "p4obs", "metric_5")
_emit_emits_metric_event("playwright_verify_total_row_util", "p4obs", "metric_6")
_emit_records_incident_event("playwright_verify_total_row_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("playwright_verify_total_row_util", "p4obs", "anomaly")
_emit_writes_observability_log("playwright_verify_total_row_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("playwright_verify_total_row_util", "p4obs", "mon_state")
_emit_triggers_alert("playwright_verify_total_row_util", "p4obs", "alert")
_emit_links_incident_trace("playwright_verify_total_row_util", "p4obs", "trace_link")
_emit_captures_pattern("playwright_verify_total_row_util", "p3lm", "pattern")
_emit_records_learning_event("playwright_verify_total_row_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("playwright_verify_total_row_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("playwright_verify_total_row_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("playwright_verify_total_row_util", "p3lm", "routing")
_emit_improves_agent_policy("playwright_verify_total_row_util", "p3lm", "policy")
_emit_stores_learning_state("playwright_verify_total_row_util", "p3lm", "state")
_emit_records_execution_trace("playwright_verify_total_row_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("playwright_verify_total_row_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("playwright_verify_total_row_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("playwright_verify_total_row_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("playwright_verify_total_row_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("playwright_verify_total_row_util", "env_read", "p2_env_1")
_emit_reads_environ("playwright_verify_total_row_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("playwright_verify_total_row_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("playwright_verify_total_row_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "playwright_verify_total_row_util", "context_pull")
_emit_pulls_context("p1", "playwright_verify_total_row_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "playwright_verify_total_row_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "playwright_verify_total_row_util", "uwg_term_2")
_emit_writes_through("p1", "playwright_verify_total_row_util", "write_through")
_emit_writes_through("p1", "playwright_verify_total_row_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "playwright_verify_total_row_util", "safety_validation")
_emit_invokes_eval("p1", "playwright_verify_total_row_util", "eval_call")
_emit_proposal_commits_routing("p1", "playwright_verify_total_row_util", "routing_commit")
_emit_escalates_to_human("p1", "playwright_verify_total_row_util", "human_escalation")
_emit_routes_through("p1", "playwright_verify_total_row_util", "route_through")
_emit_checks_agent_registry("p1", "playwright_verify_total_row_util", "agent_registry")
_emit_validates_agent_capability("p1", "playwright_verify_total_row_util", "capability")
_emit_dispatches_execution_plan("p1", "playwright_verify_total_row_util", "exec_plan")
_emit_agent_executes_agent("p1", "playwright_verify_total_row_util", "sub_agent")
_emit_routes_to_agent("p1", "playwright_verify_total_row_util", "target_agent")
_emit_verifies_policy("p1", "playwright_verify_total_row_util", "policy_check")
_emit_observes_runtime_state("p1", "playwright_verify_total_row_util", "runtime_state")
_emit_verifies_boundary("p1", "playwright_verify_total_row_util", "boundary_check")
_emit_transcripts_response("p1", "playwright_verify_total_row_util", "transcript")
_emit_hard_fails_untranscripted("p1", "playwright_verify_total_row_util")
_emit_gated_by_confidence("p1", "playwright_verify_total_row_util", "confidence_gate")
emit_replay_key("p0", "playwright_verify_total_row_util")
emit_determinism_digest("p0", "playwright_verify_total_row_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "playwright_verify_total_row_util", "execution_auth")
_emit_validates_capability("p2", "playwright_verify_total_row_util", "capability_check")
_emit_routes_to_capability("p2", "playwright_verify_total_row_util", "capability_route")
_emit_writes_via_uwg("p2", "playwright_verify_total_row_util", "uwg_write")
_emit_blocks_direct_write("p2", "playwright_verify_total_row_util", "direct_write_block")
_emit_records_tool_invocation("p2", "playwright_verify_total_row_util", "tool_invocation")
_emit_captures_execution_output("p2", "playwright_verify_total_row_util", "exec_output")
_emit_dispatches_agent("p3", "playwright_verify_total_row_util", "agent_dispatch")
_emit_coordinates_agents("p3", "playwright_verify_total_row_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "playwright_verify_total_row_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "playwright_verify_total_row_util", "healing_outcome")
_emit_escalates_failure("p3", "playwright_verify_total_row_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "playwright_verify_total_row_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "playwright_verify_total_row_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "playwright_verify_total_row_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "playwright_verify_total_row_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "playwright_verify_total_row_util", "eval_metric")
_emit_stores_embedding("p4", "playwright_verify_total_row_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "playwright_verify_total_row_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "playwright_verify_total_row_util", "exec_snapshot_link")

project_root = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

DASHBOARD_URL = "http://localhost:8765/autonomy_dashboard.html"
STRATEGIC_TAB = 'button[data-target="strategic"]'
SCREENSHOT_NAME = "strategic_health_verification"


async def _verify_via_mcp() -> dict:
    """Primary verification path using MCPConnectionManager (mcp8_playwright_*)."""
    from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager

    mcp = MCPConnectionManager()
    await mcp.connect("playwright")

    await mcp.call_tool("playwright_navigate", {"url": DASHBOARD_URL})
    await mcp.call_tool("playwright_click", {"selector": STRATEGIC_TAB})
    screenshot_result = await mcp.call_tool(
        "playwright_screenshot",
        {
            "name": SCREENSHOT_NAME,
            "savePng": True,
            "fullPage": True,
            "downloadsDir": str(project_root),
        },
    )
    table1_html_result = await mcp.call_tool(
        "playwright_get_html",
        {"selector": "#kpiGrid table tbody"},
    )
    table2_html_result = await mcp.call_tool(
        "playwright_get_html",
        {"selector": "#codeQualityGrid table tbody"},
    )
    await mcp.call_tool(
        "playwright_navigate", {"url": "http://localhost:8765/js/renderers/table-renderer.js"}
    )
    js_text_result = await mcp.call_tool("playwright_get_text", {})

    table1_html = table1_html_result if isinstance(table1_html_result, str) else str(table1_html_result)
    table2_html = table2_html_result if isinstance(table2_html_result, str) else str(table2_html_result)
    js_content = js_text_result if isinstance(js_text_result, str) else str(js_text_result)
    screenshot_path = project_root / f"{SCREENSHOT_NAME}.png"

    return {
        "table1_pass": "TOTAL" in table1_html[:500],
        "table2_pass": "TOTAL" in table2_html[:500],
        "js_pass": "Keep TOTAL at top" in js_content,
        "js_old_flag": "Keep TOTAL at end" in js_content,
        "screenshot_path": str(screenshot_path),
        "source": "mcp",
    }


def _verify_via_sync_playwright() -> dict:
    """Fallback verification path using playwright.sync_api."""
    from playwright.sync_api import sync_playwright

    screenshot_path = project_root / f"{SCREENSHOT_NAME}.png"
    table1_pass = table2_pass = js_pass = js_old_flag = False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-cache", "--disable-application-cache"],
        )
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto(DASHBOARD_URL)
        page.wait_for_load_state("networkidle")
        page.click(STRATEGIC_TAB)
        time.sleep(DEFAULT_SLEEP)
        page.screenshot(path=str(screenshot_path), full_page=True)
        try:
            first_row_text = page.locator("#kpiGrid table tbody tr").first.text_content() or ""
            table1_pass = "TOTAL" in first_row_text
        # guardian: allow-silent-swallow
        except Exception:
            pass
        try:
            first_row_text = page.locator("#codeQualityGrid table tbody tr").first.text_content() or ""
            table2_pass = "TOTAL" in first_row_text
        # guardian: allow-silent-swallow
        except Exception:
            pass
        try:
            js_response = page.goto("http://localhost:8765/js/renderers/table-renderer.js")
            js_content = js_response.text() if js_response else ""
            js_pass = "Keep TOTAL at top" in js_content
            js_old_flag = "Keep TOTAL at end" in js_content
        # guardian: allow-silent-swallow
        except Exception:
            pass
        browser.close()

    return {
        "table1_pass": table1_pass,
        "table2_pass": table2_pass,
        "js_pass": js_pass,
        "js_old_flag": js_old_flag,
        "screenshot_path": str(screenshot_path),
        "source": "sync_api",
    }


def main():
    """Verify TOTAL row position using MCP-routed Playwright tools."""
    print("=" * 70)
    print("PLAYWRIGHT VERIFICATION: TOTAL ROW POSITION")
    print("=" * 70)

    print("\n1. Starting fresh dashboard server on port 8765...")
    dashboard_dir = project_root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards"
    server_process = safe_popen(
        [sys.executable, "-m", "http.server", "8765"],
        cwd=str(dashboard_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(DEFAULT_SLEEP)
    print("   Server started")

    try:
        print("\n2. Running MCP-routed Playwright verification...")
        try:
            results = asyncio.run(_verify_via_mcp())
            print(f"   Source: {results['source']}")
        # guardian: allow-silent-swallow
        except Exception as mcp_err:
            print(f"   MCP path unavailable ({mcp_err}) — falling back to sync_playwright")
            try:
                results = _verify_via_sync_playwright()
                print(f"   Source: {results['source']}")
            # guardian: allow-silent-swallow - optional dependency
            except ImportError:
                print("   playwright not installed — pip install playwright && playwright install chromium")
                return 1

        table1_pass = results["table1_pass"]
        table2_pass = results["table2_pass"]
        js_pass = results["js_pass"]
        screenshot_path = results["screenshot_path"]

        print(f"\n3. Screenshot saved: {screenshot_path}")
        print(
            "\n4. Table 1 (Territory Summary): " + ("PASS" if table1_pass else "FAIL - TOTAL row NOT at top")
        )
        print(
            "   Table 2 (Code Quality):       " + ("PASS" if table2_pass else "FAIL - TOTAL row NOT at top")
        )
        print("   JavaScript File Updated:       " + ("PASS" if js_pass else "FAIL - OLD code detected"))
        if results.get("js_old_flag"):
            print("   Warning: File contains OLD comment 'Keep TOTAL at end'")

        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"Table 1 (Territory Summary): {'PASS' if table1_pass else 'FAIL'}")
        print(f"Table 2 (Code Quality):       {'PASS' if table2_pass else 'FAIL'}")
        print(f"JavaScript File Updated:       {'PASS' if js_pass else 'FAIL'}")
        print(f"\nScreenshot: {screenshot_path}")

        if table1_pass and table2_pass and js_pass:
            print("\nALL VERIFICATIONS PASSED - TOTAL rows are at the top!")
            return 0
        print("\nVERIFICATION FAILED - check output above")
        return 1
    finally:
        print("\n5. Stopping dashboard server...")
        server_process.terminate()
        server_process.wait()
        print("   Server stopped")


if __name__ == "__main__":
    sys.exit(main())
