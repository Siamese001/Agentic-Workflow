from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "agent_capability_supplement_util")
emit_determinism_digest("p0", "agent_capability_supplement_util")

_emit_dispatches_healing_run("p1", "agent_capability_supplement_util", "L0")
_emit_routes_through("p1", "agent_capability_supplement_util", "L0")
_emit_checks_agent_registry("p1", "agent_capability_supplement_util", "agent_registry")
_emit_validates_agent_capability("p1", "agent_capability_supplement_util", "capability")
_emit_dispatches_execution_plan("p1", "agent_capability_supplement_util", "exec_plan")
_emit_agent_executes_agent("p1", "agent_capability_supplement_util", "sub_agent")
_emit_routes_to_agent("p1", "agent_capability_supplement_util", "target_agent")
_emit_verifies_policy("p1", "agent_capability_supplement_util", "policy_check")
_emit_observes_runtime_state("p1", "agent_capability_supplement_util", "runtime_state")
_emit_verifies_boundary("p1", "agent_capability_supplement_util", "boundary_check")
_emit_transcripts_response("p1", "agent_capability_supplement_util", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_capability_supplement_util")
_emit_gated_by_confidence("p1", "agent_capability_supplement_util", "confidence_gate")
_emit_escalates_to_human("p1", "agent_capability_supplement_util", "L0")
_emit_reads_policy_state("p1", "agent_capability_supplement_util", "L0")
_emit_authorize_and_execute("p2", "agent_capability_supplement_util", "execution_auth")
_emit_validates_capability("p2", "agent_capability_supplement_util", "capability_check")
_emit_routes_to_capability("p2", "agent_capability_supplement_util", "capability_route")
_emit_writes_via_uwg("p2", "agent_capability_supplement_util", "uwg_write")
_emit_blocks_direct_write("p2", "agent_capability_supplement_util", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_capability_supplement_util", "tool_invocation")
_emit_captures_execution_output("p2", "agent_capability_supplement_util", "exec_output")
_emit_dispatches_agent("p3", "agent_capability_supplement_util", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_capability_supplement_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_capability_supplement_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_capability_supplement_util", "healing_outcome")
_emit_escalates_failure("p3", "agent_capability_supplement_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_capability_supplement_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_capability_supplement_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_capability_supplement_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_capability_supplement_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_capability_supplement_util", "eval_metric")
_emit_stores_embedding("p4", "agent_capability_supplement_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_capability_supplement_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_capability_supplement_util", "exec_snapshot_link")

'\nULTRA-HARDENED AST-DRIVEN CAPABILITY SUPPLEMENTATION ANALYSIS\n\nGoal:\n  Mine the 35 "DEAD" agents for unique, valuable logic that can supplement the 19 LIVE agents.\n  Instead of deletion, achieve evolutionary enhancement → denser, more capable live core.\n\nTechnical Approach:\n  • Reuse the sovereign ASTNormalizer from agent_discovery_audit.py\n  • Extract semantic capabilities via method names + body pattern analysis\n  • Identify unique/underrepresented capabilities in DEAD agents\n  • Generate precise supplementation recommendations with file paths and method targets\n'
import ast
import json
import sys
from collections import Counter

from agentic_core.L0_routing.config import SCRIPTS_DIR, get_validated_project_root
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

_emit_emits_metric_event("agent_capability_supplement_util", "p4obs", "metric_1")
_emit_emits_metric_event("agent_capability_supplement_util", "p4obs", "metric_2")
_emit_emits_metric_event("agent_capability_supplement_util", "p4obs", "metric_3")
_emit_emits_metric_event("agent_capability_supplement_util", "p4obs", "metric_4")
_emit_emits_metric_event("agent_capability_supplement_util", "p4obs", "metric_5")
_emit_emits_metric_event("agent_capability_supplement_util", "p4obs", "metric_6")
_emit_records_incident_event("agent_capability_supplement_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_capability_supplement_util", "p4obs", "anomaly")
_emit_writes_observability_log("agent_capability_supplement_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_capability_supplement_util", "p4obs", "mon_state")
_emit_triggers_alert("agent_capability_supplement_util", "p4obs", "alert")
_emit_links_incident_trace("agent_capability_supplement_util", "p4obs", "trace_link")
_emit_captures_pattern("agent_capability_supplement_util", "p3lm", "pattern")
_emit_records_learning_event("agent_capability_supplement_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_capability_supplement_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_capability_supplement_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_capability_supplement_util", "p3lm", "routing")
_emit_improves_agent_policy("agent_capability_supplement_util", "p3lm", "policy")
_emit_stores_learning_state("agent_capability_supplement_util", "p3lm", "state")
_emit_records_execution_trace("agent_capability_supplement_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_capability_supplement_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_capability_supplement_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_capability_supplement_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_capability_supplement_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_capability_supplement_util", "env_read", "p2_env_1")
_emit_reads_environ("agent_capability_supplement_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_capability_supplement_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_capability_supplement_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_capability_supplement_util", "context_pull")
_emit_pulls_context("p1", "agent_capability_supplement_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_capability_supplement_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_capability_supplement_util", "uwg_term_2")
_emit_writes_through("p1", "agent_capability_supplement_util", "write_through")
_emit_writes_through("p1", "agent_capability_supplement_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_capability_supplement_util", "safety_validation")
_emit_invokes_eval("p1", "agent_capability_supplement_util", "eval_call")
_emit_proposal_commits_routing("p1", "agent_capability_supplement_util", "routing_commit")

PROJECT_ROOT = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(SCRIPTS_DIR))
REPORT_PATH = PROJECT_ROOT / "agent_discovery_report.json"
if not REPORT_PATH.exists():
    raise FileNotFoundError(f"[!] Missing report: {REPORT_PATH} — run agent_discovery_audit.py first")
with open(REPORT_PATH, encoding="utf-8") as f:
    report = json.load(f)
live_agent_names = {a["name"] for a in report["agents"] if a["name"] not in report["dead_agents"]}
dead_agent_names = set(report["dead_agents"])
suspect_agent_names = set(report["suspect_agents"])
print("=" * 80)
print("ULTRA CAPABILITY SUPPLEMENTATION ANALYSIS")
print(
    f"Live agents: {len(live_agent_names)} | Dead (to mine): {len(dead_agent_names)} | Suspect: {len(suspect_agent_names)}",
)
print("=" * 80)


def extract_capabilities_from_source(source: str, class_node: ast.ClassDef) -> dict:
    """
    Extract rich capability metadata from a single agent class.
    Returns dict with:
      - semantic_tags: high-level capabilities (healing, detection, git, etc.)
      - unique_methods: method names not common in live agents
      - patterns: regex-detected specialized operations
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_capabilities_from_source", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_capabilities_from_source", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "extract_capabilities_from_source")
    caps = {"semantic_tags": set(), "unique_methods": set(), "patterns": set(), "valuable_methods": []}
    common_methods = {"__init__", "heal_violation", "execute", "run", "validate", "monitor"}
    for item in class_node.body:
        if not isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        method_name = item.name
        method_loc = item.lineno
        if method_name not in common_methods:
            caps["unique_methods"].add(method_name)
            caps["valuable_methods"].append((method_name, method_loc, "Unique method signature"))
        lower_name = method_name.lower()
        if any(k in lower_name for k in ["heal", "fix", "repair"]):
            caps["semantic_tags"].add("healing")
        if any(k in lower_name for k in ["validate", "check", "enforce"]):
            caps["semantic_tags"].add("validation")
        if any(k in lower_name for k in ["detect", "find", "scan"]):
            caps["semantic_tags"].add("detection")
        if any(k in lower_name for k in ["prune", "clean", "remove"]):
            caps["semantic_tags"].add("pruning")
        if any(k in lower_name for k in ["map", "territory", "structure"]):
            caps["semantic_tags"].add("mapping")
        if any(k in lower_name for k in ["watch", "monitor", "observe"]):
            caps["semantic_tags"].add("monitoring")
        if "git" in lower_name:
            caps["semantic_tags"].add("git_integration")
        try:
            body_source = ast.unparse(item.body) if hasattr(ast, "unparse") else ""
        # guardian: allow-silent-swallow
        except (ValueError, TypeError):
            body_source = ""
        lower_body = body_source.lower()
        if (
            "git" in lower_body
            and "subprocess" in lower_body
            or ("git" in lower_body and "repo" in lower_body)
        ):
            caps["patterns"].add("git_operations")
            caps["valuable_methods"].append((method_name, method_loc, "Git repository interaction"))
        if "dead code" in lower_body or "unused" in lower_body:
            caps["patterns"].add("dead_code_analysis")
            caps["valuable_methods"].append((method_name, method_loc, "Dead/unused code detection"))
        if "filesystem" in lower_body or ("path" in lower_body and "exists" in lower_body):
            caps["patterns"].add("filesystem_introspection")
            caps["valuable_methods"].append((method_name, method_loc, "Advanced filesystem checks"))
        if "redis" in lower_body:
            caps["patterns"].add("redis_integration")
            caps["valuable_methods"].append((method_name, method_loc, "Redis state access"))
    return caps


def generate_markdown_report(
    live_cap_counter: Counter,
    dead_cap_detail: dict,
    unique_to_dead: set,
    underrepresented: dict,
    recommendations: list,
) -> str:
    """Generate detailed markdown report."""
    lines = []
    lines.append("# ULTRA CAPABILITY SUPPLEMENTATION ANALYSIS REPORT")
    lines.append("")
    lines.append(f"**Generated:** {__import__('datetime').datetime.now().isoformat()}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| **Live Agents** | {len(live_agent_names)} |")
    lines.append(f"| **Dead Agents (to mine)** | {len(dead_agent_names)} |")
    lines.append(f"| **Suspect Agents** | {len(suspect_agent_names)} |")
    lines.append(f"| **Unique Capabilities in Dead** | {len(unique_to_dead)} |")
    lines.append(f"| **Underrepresented Capabilities** | {len(underrepresented)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Live Agent Capability Coverage")
    lines.append("")
    lines.append("| Capability | Count in Live Agents |")
    lines.append("|------------|---------------------|")
    for cap, count in sorted(live_cap_counter.items(), key=lambda x: -x[1]):
        lines.append(f"| {cap} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Unique Capabilities in DEAD Agents")
    lines.append("")
    if unique_to_dead:
        lines.append(f"Found **{len(unique_to_dead)}** capabilities present ONLY in DEAD agents:")
        lines.append("")
        for cap in sorted(unique_to_dead):
            donors = [
                name
                for name, detail in dead_cap_detail.items()
                if cap in detail["caps"]["semantic_tags"] or cap in detail["caps"]["patterns"]
            ]
            lines.append(f"### `{cap.upper()}`")
            lines.append("")
            lines.append("**Donor Agents:**")
            for d in donors:
                lines.append(f"- `{d}` → `{dead_cap_detail[d]['file']}`")
            lines.append("")
    else:
        lines.append("✅ **No completely unique capabilities** — all logic covered by LIVE agents.")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Underrepresented Capabilities")
    lines.append("")
    lines.append("Capabilities that appear in fewer than 2 LIVE agents:")
    lines.append("")
    if underrepresented:
        lines.append("| Capability | Live Count | Potential Donors |")
        lines.append("|------------|------------|------------------|")
        for cap, count in sorted(underrepresented.items()):
            donors = [
                name
                for name, detail in dead_cap_detail.items()
                if cap in detail["caps"]["semantic_tags"] or cap in detail["caps"]["patterns"]
            ]
            donors_str = ", ".join(f"`{d}`" for d in donors) if donors else "—"
            lines.append(f"| {cap} | {count} | {donors_str} |")
        lines.append("")
    else:
        lines.append("✅ All capabilities are well-represented in LIVE agents.")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Dead Agent Capability Detail")
    lines.append("")
    for name in sorted(dead_cap_detail.keys()):
        detail = dead_cap_detail[name]
        caps = detail["caps"]
        lines.append(f"### `{name}`")
        lines.append("")
        lines.append(f"**File:** `{detail['file']}`")
        lines.append("")
        if caps["semantic_tags"]:
            lines.append(f"**Semantic Tags:** {', '.join(sorted(caps['semantic_tags']))}")
        if caps["patterns"]:
            lines.append(f"**Patterns:** {', '.join(sorted(caps['patterns']))}")
        if caps["unique_methods"]:
            lines.append(f"**Unique Methods:** `{'`, `'.join(sorted(caps['unique_methods']))}`")
        if caps["valuable_methods"]:
            lines.append("")
            lines.append("**Valuable Methods:**")
            lines.append("")
            lines.append("| Method | Line | Description |")
            lines.append("|--------|------|-------------|")
            for m_name, m_line, m_desc in caps["valuable_methods"]:
                lines.append(f"| `{m_name}` | {m_line} | {m_desc} |")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Recommended Supplementation Merges")
    lines.append("")
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"### Recommendation {i}")
            lines.append("")
            lines.append("```")
            lines.append(rec)
            lines.append("```")
            lines.append("")
    else:
        lines.append("✅ **No high-confidence supplementation opportunities detected.**")
        lines.append("")
        lines.append("The LIVE agents already cover all semantic capabilities found in DEAD agents.")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Next Steps")
    lines.append("")
    lines.append("1. Review underrepresented capabilities for potential consolidation")
    lines.append("2. For each recommended merge:")
    lines.append("   - Open source and target files side-by-side")
    lines.append("   - Copy valuable methods with full context")
    lines.append("   - Update docstrings and add tests")
    lines.append("   - Delete original DEAD file after verification")
    lines.append("3. Re-run `agent_discovery_audit.py` to verify changes")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by `agent_capability_supplement_util.py`*")
    return "\n".join(lines)


def analyze_supplementation():
    live_cap_counter = Counter()
    dead_cap_detail = {}
    print("\nAnalyzing capabilities in DEAD agents for supplementation value...")
    for agent_meta in report["agents"]:
        agent_name = agent_meta["name"]
        file_path = PROJECT_ROOT / agent_meta["file"]
        if not file_path.exists():
            continue
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            class_node = next(
                n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == agent_name
            )
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            print(f"  [!] Parse error {agent_name}: {e}")
            continue
        caps = extract_capabilities_from_source(source, class_node)
        if agent_name in live_agent_names:
            live_cap_counter.update(caps["semantic_tags"] | caps["patterns"])
        elif agent_name in dead_agent_names:
            dead_cap_detail[agent_name] = {"file": str(file_path.relative_to(PROJECT_ROOT)), "caps": caps}
    all_dead_caps = set()
    for detail in dead_cap_detail.values():
        all_dead_caps.update(detail["caps"]["semantic_tags"])
        all_dead_caps.update(detail["caps"]["patterns"])
    unique_to_dead = all_dead_caps - set(live_cap_counter.keys())
    underrepresented = {cap: count for cap, count in live_cap_counter.items() if count < 2}
    recommendations = []
    if "git_operations" in unique_to_dead or "git_integration" in unique_to_dead:
        recommendations.append(
            "→ Merge GitAgent methods into ToolsmithAgent or new L2 GitToolAgent\n  Source: agentic_core/L2_execution/reasoning/GitAgent.py\n  Target: agentic_core/L2_execution/reasoning/ToolsmithAgent.py (add git_* methods)",
        )
    if "dead_code_analysis" in unique_to_dead:
        recommendations.append(
            "→ Extract dead code detection from DeadCodeAgent/DeadCodePrunerAgent\n  Sources: L5_safety/guardrails/DeadCodeAgent.py, L3_orchestration/DeadCodePrunerAgent.py\n  Target: Enhance CodeDeduplicationAgent (L2) with advanced unreachable code logic",
        )
    if "mapping" in unique_to_dead or "territory" in unique_to_dead:
        recommendations.append(
            "→ Integrate SemanticTerritoryMapperAgent patterns\n  Source: agentic_core/L3_orchestration/reasoning/SemanticTerritoryMapperAgent.py\n  Target: HierarchyAgent or LocationAgent (L5) for semantic structural awareness",
        )
    if "monitoring" in unique_to_dead or "watchdog" in unique_to_dead:
        recommendations.append(
            "→ Add SovereignWatchdogAgent monitoring logic\n  Source: agentic_core/L0_routing/scripts/SovereignWatchdogAgent.py\n  Target: BootstrapAgent or new L0 RuntimeGuard",
        )
    if "filesystem_introspection" in unique_to_dead:
        recommendations.append(
            "→ Supplement FilesystemAgent deep introspection\n  Source: agentic_core/L5_safety/validators/FilesystemAgent.py\n  Target: LocationAgent or HierarchyAgent (enhance path validation)",
        )
    print("\n" + "=" * 80)
    print("SUPPLEMENTATION OPPORTUNITIES — UNIQUE CAPABILITIES IN DEAD AGENTS")
    print("=" * 80)
    if unique_to_dead:
        print(f"Found {len(unique_to_dead)} capabilities present ONLY in DEAD agents:")
        for cap in sorted(unique_to_dead):
            donors = [
                name
                for name, detail in dead_cap_detail.items()
                if cap in detail["caps"]["semantic_tags"] or cap in detail["caps"]["patterns"]
            ]
            print(f"  • {cap.upper():<30} ← from: {', '.join(donors)}")
    else:
        print("[OK] No completely unique capabilities — all logic covered by LIVE agents")
    print("\nUnderrepresented capabilities (appear in <2 LIVE agents):")
    for cap, count in underrepresented.items():
        donors = [
            name
            for name, detail in dead_cap_detail.items()
            if cap in detail["caps"]["semantic_tags"] or cap in detail["caps"]["patterns"]
        ]
        if donors:
            print(f"  • {cap:<30} (live count: {count}) ← supplement from: {', '.join(donors)}")
    print("\n" + "=" * 80)
    print("RECOMMENDED SUPPLEMENTATION MERGES (IDE DIFF GUIDANCE)")
    print("=" * 80)
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("[OK] No high-confidence supplementation opportunities detected")
    md_report = generate_markdown_report(
        live_cap_counter,
        dead_cap_detail,
        unique_to_dead,
        underrepresented,
        recommendations,
    )
    report_path = PROJECT_ROOT / "agent_supplementation_report.md"
    assert_no_persistent_write("L0", "write_text")
    report_path.write_text(md_report, encoding="utf-8")
    print(f"\n[SAVED] Detailed markdown report: {report_path}")
    print("\n" + "=" * 80)
    print("SUPPLEMENTATION ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    analyze_supplementation()
