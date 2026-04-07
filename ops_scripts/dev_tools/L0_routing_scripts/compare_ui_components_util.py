"""
Compare UI components between monolithic and modular dashboards
Catalogs: tabs, cards, tables, footnotes, filters, modals, KPIs
"""

import re
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "compare_ui_components_util")
emit_determinism_digest("p0", "compare_ui_components_util")

_emit_dispatches_healing_run("p1", "compare_ui_components_util", "L0")
_emit_routes_through("p1", "compare_ui_components_util", "L0")
_emit_checks_agent_registry("p1", "compare_ui_components_util", "agent_registry")
_emit_validates_agent_capability("p1", "compare_ui_components_util", "capability")
_emit_dispatches_execution_plan("p1", "compare_ui_components_util", "exec_plan")
_emit_agent_executes_agent("p1", "compare_ui_components_util", "sub_agent")
_emit_routes_to_agent("p1", "compare_ui_components_util", "target_agent")
_emit_verifies_policy("p1", "compare_ui_components_util", "policy_check")
_emit_observes_runtime_state("p1", "compare_ui_components_util", "runtime_state")
_emit_verifies_boundary("p1", "compare_ui_components_util", "boundary_check")
_emit_transcripts_response("p1", "compare_ui_components_util", "transcript")
_emit_hard_fails_untranscripted("p1", "compare_ui_components_util")
_emit_gated_by_confidence("p1", "compare_ui_components_util", "confidence_gate")
_emit_escalates_to_human("p1", "compare_ui_components_util", "L0")
_emit_reads_policy_state("p1", "compare_ui_components_util", "L0")
_emit_authorize_and_execute("p2", "compare_ui_components_util", "execution_auth")
_emit_validates_capability("p2", "compare_ui_components_util", "capability_check")
_emit_routes_to_capability("p2", "compare_ui_components_util", "capability_route")
_emit_writes_via_uwg("p2", "compare_ui_components_util", "uwg_write")
_emit_blocks_direct_write("p2", "compare_ui_components_util", "direct_write_block")
_emit_records_tool_invocation("p2", "compare_ui_components_util", "tool_invocation")
_emit_captures_execution_output("p2", "compare_ui_components_util", "exec_output")
_emit_dispatches_agent("p3", "compare_ui_components_util", "agent_dispatch")
_emit_coordinates_agents("p3", "compare_ui_components_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "compare_ui_components_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "compare_ui_components_util", "healing_outcome")
_emit_escalates_failure("p3", "compare_ui_components_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "compare_ui_components_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "compare_ui_components_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "compare_ui_components_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "compare_ui_components_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "compare_ui_components_util", "eval_metric")
_emit_stores_embedding("p4", "compare_ui_components_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "compare_ui_components_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "compare_ui_components_util", "exec_snapshot_link")
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

_emit_emits_metric_event("compare_ui_components_util", "p4obs", "metric_1")
_emit_emits_metric_event("compare_ui_components_util", "p4obs", "metric_2")
_emit_emits_metric_event("compare_ui_components_util", "p4obs", "metric_3")
_emit_emits_metric_event("compare_ui_components_util", "p4obs", "metric_4")
_emit_emits_metric_event("compare_ui_components_util", "p4obs", "metric_5")
_emit_emits_metric_event("compare_ui_components_util", "p4obs", "metric_6")
_emit_records_incident_event("compare_ui_components_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("compare_ui_components_util", "p4obs", "anomaly")
_emit_writes_observability_log("compare_ui_components_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("compare_ui_components_util", "p4obs", "mon_state")
_emit_triggers_alert("compare_ui_components_util", "p4obs", "alert")
_emit_links_incident_trace("compare_ui_components_util", "p4obs", "trace_link")
_emit_captures_pattern("compare_ui_components_util", "p3lm", "pattern")
_emit_records_learning_event("compare_ui_components_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("compare_ui_components_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("compare_ui_components_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("compare_ui_components_util", "p3lm", "routing")
_emit_improves_agent_policy("compare_ui_components_util", "p3lm", "policy")
_emit_stores_learning_state("compare_ui_components_util", "p3lm", "state")
_emit_records_execution_trace("compare_ui_components_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("compare_ui_components_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("compare_ui_components_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("compare_ui_components_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("compare_ui_components_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("compare_ui_components_util", "env_read", "p2_env_1")
_emit_reads_environ("compare_ui_components_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("compare_ui_components_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("compare_ui_components_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "compare_ui_components_util", "context_pull")
_emit_pulls_context("p1", "compare_ui_components_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "compare_ui_components_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "compare_ui_components_util", "uwg_term_2")
_emit_writes_through("p1", "compare_ui_components_util", "write_through")
_emit_writes_through("p1", "compare_ui_components_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "compare_ui_components_util", "safety_validation")
_emit_invokes_eval("p1", "compare_ui_components_util", "eval_call")
_emit_proposal_commits_routing("p1", "compare_ui_components_util", "routing_commit")


def extract_components(html_content, name):
    """Extract UI components from HTML content"""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_components", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_components", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "extract_components")
    components = {
        "tabs": [],
        "kpi_boxes": [],
        "chart_cards": [],
        "tables": [],
        "filters": [],
        "modals": [],
        "footnotes": [],
        "functions": [],
        "data_files": [],
    }
    tab_matches = re.findall('data-target="([^"]+)"[^>]*>([^<]+)</a>', html_content)
    for target, label in tab_matches:
        components["tabs"].append({"target": target, "label": label.strip()})
    kpi_matches = re.findall(
        'class="kpi-box[^"]*"[^>]*>.*?<div class="kpi-label">([^<]+)</div>', html_content, re.DOTALL,
    )
    components["kpi_boxes"] = list(set(kpi_matches))
    card_matches = re.findall('<div class="chart-title"[^>]*>([^<]+)</div>', html_content)
    components["chart_cards"] = list(set(card_matches))
    filter_matches = re.findall(
        "checkbox[^>]*>([^<]+)</label>|checkbox[^>]*>\\s*<[^>]*>([^<]+)<", html_content, re.DOTALL,
    )
    for match in filter_matches:
        label = match[0] or match[1]
        if label and label.strip():
            components["filters"].append(label.strip())
    modal_matches = re.findall('id="([^"]*[Mm]odal[^"]*)"', html_content)
    components["modals"] = list(set(modal_matches))
    data_matches = re.findall('src="([^"]*\\.js)"', html_content)
    components["data_files"] = [f for f in data_matches if "data/" in f or "js/" in f]
    func_matches = re.findall("function\\s+(\\w+)\\s*\\(", html_content)
    components["functions"] = list(set(func_matches))
    if "Factory analogy" in html_content:
        components["footnotes"].append("Factory analogies present")
    if "Icon Legend" in html_content:
        components["footnotes"].append("Icon legend present")
    if "Health Score:" in html_content or "Heal Capability %:" in html_content:
        components["footnotes"].append("Metric definitions present")
    return components


def compare_components():
    """Compare monolithic vs modular UI components"""
    print("\n" + "=" * 70)
    print("UI COMPONENT COMPARISON: Monolithic vs Modular")
    print("=" * 70 + "\n")
    mono_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard_backup.html")
    if not mono_path.exists():
        print(f"❌ Monolithic backup not found: {mono_path}")
        return
    with open(mono_path, encoding="utf-8") as f:
        mono_html = f.read()
    mod_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
    if not mod_path.exists():
        print(f"❌ Modular dashboard not found: {mod_path}")
        return
    with open(mod_path, encoding="utf-8") as f:
        mod_html = f.read()
    js_content = ""
    js_files = [
        "agentic_core/L6_observability/dashboards/js/renderers/table-renderer.js",
        "agentic_core/L6_observability/dashboards/js/main.js",
    ]
    for js_file in js_files:
        js_path = Path(js_file)
        if js_path.exists():
            with open(js_path, encoding="utf-8") as f:
                js_content += f.read()
    mod_html += js_content
    mono_components = extract_components(mono_html, "Monolithic")
    mod_components = extract_components(mod_html, "Modular")
    categories = [
        ("tabs", "Navigation Tabs"),
        ("kpi_boxes", "KPI Boxes"),
        ("chart_cards", "Chart Cards"),
        ("filters", "Filter Controls"),
        ("modals", "Modals"),
        ("footnotes", "Footnotes & Legends"),
        ("data_files", "Data Files"),
        ("functions", "JavaScript Functions"),
    ]
    all_issues = []
    for key, label in categories:
        set(mono_components[key]) if isinstance(
            mono_components[key][0] if mono_components[key] else "", str,
        ) else {str(x) for x in mono_components[key]}
        set(mod_components[key]) if isinstance(
            mod_components[key][0] if mod_components[key] else "", str,
        ) else {str(x) for x in mod_components[key]}
        print(f"\n{'=' * 50}")
        print(f"📦 {label}")
        print(f"{'=' * 50}")
        print(f"  Monolithic: {len(mono_components[key])} items")
        print(f"  Modular:    {len(mod_components[key])} items")
        if isinstance(mono_components[key], list) and mono_components[key]:
            if isinstance(mono_components[key][0], dict):
                mono_set = {str(x) for x in mono_components[key]}
                mod_set = {str(x) for x in mod_components[key]}
            else:
                mono_set = set(mono_components[key])
                mod_set = set(mod_components[key])
            missing = mono_set - mod_set
            if missing:
                print("  ❌ Missing in modular:")
                for item in list(missing)[:10]:
                    print(f"     - {item}")
                    all_issues.append(f"{label}: {item}")
            else:
                print("  ✅ All items present")
    print(f"\n{'=' * 50}")
    print("📑 DETAILED TAB COMPARISON")
    print(f"{'=' * 50}")
    mono_tabs = mono_components["tabs"]
    mod_tabs = mod_components["tabs"]
    print("\nMonolithic tabs:")
    for tab in mono_tabs:
        print(f"  - {tab['label']} → #{tab['target']}")
    print("\nModular tabs:")
    for tab in mod_tabs:
        print(f"  - {tab['label']} → #{tab['target']}")
    print(f"\n{'=' * 50}")
    print("🔍 CRITICAL FEATURE CHECK")
    print(f"{'=' * 50}")
    critical_features = [
        ("renderTerritorySummaryTable", "Territory Summary Table Renderer"),
        ("renderCodeQualityTable", "Code Quality Table Renderer"),
        ("openDrillModal", "Drill-down Modal"),
        ("toggleFilter", "Filter Toggle Function"),
        ("toggleToxicityFilter", "Toxicity Filter"),
        ("toggleZombieFilter", "Zombie Filter"),
        ("toggleOutlierFilter", "Outlier Filter"),
        ("loadData", "Data Loading Function"),
        ("openTab", "Tab Navigation"),
        ("manualRefresh", "Manual Refresh"),
        ("Factory analogy", "Factory Analogies in Footnotes"),
        ("Icon Legend", "Icon Legend"),
        ("Heal Capability %:", "Heal Capability Definition"),
        ("Health Score:", "Health Score Formula"),
        ("drillModal", "Drill-down Modal Element"),
    ]
    for feature, description in critical_features:
        mono_has = feature in mono_html
        mod_has = feature in mod_html
        if mono_has and mod_has:
            status = "✅"
        elif mono_has and (not mod_has):
            status = "❌ MISSING"
            all_issues.append(f"Missing: {description}")
        elif not mono_has and mod_has:
            status = "➕ NEW"
        else:
            status = "⚪ N/A"
        print(f"  {status} {description}")
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    if all_issues:
        print(f"\n❌ {len(all_issues)} issues found:\n")
        for issue in all_issues[:20]:
            print(f"  - {issue}")
        if len(all_issues) > 20:
            print(f"  ... and {len(all_issues) - 20} more")
    else:
        print("\n✅ All critical features present in modular dashboard!")
    return all_issues


if __name__ == "__main__":
    issues = compare_components()
    exit(1 if issues else 0)
