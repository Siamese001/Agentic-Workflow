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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "handler")
emit_determinism_digest("p0", "handler")

_emit_dispatches_healing_run("p1", "handler", "L0")
_emit_routes_through("p1", "handler", "L0")
_emit_checks_agent_registry("p1", "handler", "agent_registry")
_emit_validates_agent_capability("p1", "handler", "capability")
_emit_dispatches_execution_plan("p1", "handler", "exec_plan")
_emit_agent_executes_agent("p1", "handler", "sub_agent")
_emit_routes_to_agent("p1", "handler", "target_agent")
_emit_verifies_policy("p1", "handler", "policy_check")
_emit_observes_runtime_state("p1", "handler", "runtime_state")
_emit_verifies_boundary("p1", "handler", "boundary_check")
_emit_transcripts_response("p1", "handler", "transcript")
_emit_hard_fails_untranscripted("p1", "handler")
_emit_gated_by_confidence("p1", "handler", "confidence_gate")
_emit_escalates_to_human("p1", "handler", "L0")
_emit_reads_policy_state("p1", "handler", "L0")

_emit_records_execution_trace("p0", "evidence", "handler")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "handler", "p0_governance")
_emit_snapshots_state("p0", "handler", "state_snapshot")
_emit_authorize_and_execute("p2", "handler", "execution_auth")
_emit_validates_capability("p2", "handler", "capability_check")
_emit_routes_to_capability("p2", "handler", "capability_route")
_emit_writes_via_uwg("p2", "handler", "uwg_write")
_emit_blocks_direct_write("p2", "handler", "direct_write_block")
_emit_records_tool_invocation("p2", "handler", "tool_invocation")
_emit_captures_execution_output("p2", "handler", "exec_output")
_emit_dispatches_agent("p3", "handler", "agent_dispatch")
_emit_coordinates_agents("p3", "handler", "agent_coordination")
_emit_records_workflow_lineage("p3", "handler", "workflow_lineage")
_emit_records_healing_outcome("p3", "handler", "healing_outcome")
_emit_escalates_failure("p3", "handler", "failure_escalation")
_emit_orchestrates_workflow("p3", "handler", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "handler", "healing_dispatch")
_emit_invokes_evaluation("p3", "handler", "evaluation_signal")
_emit_records_telemetry_event("p4", "handler", "telemetry_event")
_emit_captures_evaluation_metric("p4", "handler", "eval_metric")
_emit_stores_embedding("p4", "handler", "embedding_store")
_emit_updates_meta_learning_state("p4", "handler", "meta_learning")
_emit_links_execution_to_snapshot("p4", "handler", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("handler", "p4obs", "metric_1")
_emit_emits_metric_event("handler", "p4obs", "metric_2")
_emit_emits_metric_event("handler", "p4obs", "metric_3")
_emit_emits_metric_event("handler", "p4obs", "metric_4")
_emit_emits_metric_event("handler", "p4obs", "metric_5")
_emit_emits_metric_event("handler", "p4obs", "metric_6")
_emit_records_incident_event("handler", "p4obs", "incident")
_emit_captures_runtime_anomaly("handler", "p4obs", "anomaly")
_emit_writes_observability_log("handler", "p4obs", "obs_log")
_emit_updates_monitoring_state("handler", "p4obs", "mon_state")
_emit_triggers_alert("handler", "p4obs", "alert")
_emit_links_incident_trace("handler", "p4obs", "trace_link")
_emit_captures_pattern("handler", "p3lm", "pattern")
_emit_records_learning_event("handler", "p3lm", "learning_event")
_emit_writes_learning_snapshot("handler", "p3lm", "snapshot")
_emit_feeds_meta_learning("handler", "p3lm", "meta_feed")
_emit_updates_routing_strategy("handler", "p3lm", "routing")
_emit_improves_agent_policy("handler", "p3lm", "policy")
_emit_stores_learning_state("handler", "p3lm", "state")
_emit_records_execution_trace("handler", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("handler", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("handler", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("handler", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("handler", "L4_STATE", "p2_trace_5")
_emit_reads_environ("handler", "env_read", "p2_env_1")
_emit_reads_environ("handler", "env_read", "p2_env_2")
_emit_reads_runtime_state("handler", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("handler", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "handler", "context_pull")
_emit_pulls_context("p1", "handler", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "handler", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "handler", "uwg_term_2")
_emit_writes_through("p1", "handler", "write_through")
_emit_writes_through("p1", "handler", "write_through_2")
_emit_validated_by_safety_plane("p1", "handler", "safety_validation")
_emit_invokes_eval("p1", "handler", "eval_call")
_emit_proposal_commits_routing("p1", "handler", "routing_commit")

project_root = Path(__file__).parent.parent


def debug_dashboard():
    """Use Playwright to deeply inspect dashboard loading."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
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
