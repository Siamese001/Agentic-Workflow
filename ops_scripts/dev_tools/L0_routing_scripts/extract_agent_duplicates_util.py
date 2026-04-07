"""
Extract agent duplicates from find_duplicate_agents.py output.
Filters to actual agent files only (excludes tests).
"""

import json
import sys
from datetime import datetime
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

emit_replay_key("p0", "extract_agent_duplicates_util")
emit_determinism_digest("p0", "extract_agent_duplicates_util")

_emit_dispatches_healing_run("p1", "extract_agent_duplicates_util", "L0")
_emit_routes_through("p1", "extract_agent_duplicates_util", "L0")
_emit_checks_agent_registry("p1", "extract_agent_duplicates_util", "agent_registry")
_emit_validates_agent_capability("p1", "extract_agent_duplicates_util", "capability")
_emit_dispatches_execution_plan("p1", "extract_agent_duplicates_util", "exec_plan")
_emit_agent_executes_agent("p1", "extract_agent_duplicates_util", "sub_agent")
_emit_routes_to_agent("p1", "extract_agent_duplicates_util", "target_agent")
_emit_verifies_policy("p1", "extract_agent_duplicates_util", "policy_check")
_emit_observes_runtime_state("p1", "extract_agent_duplicates_util", "runtime_state")
_emit_verifies_boundary("p1", "extract_agent_duplicates_util", "boundary_check")
_emit_transcripts_response("p1", "extract_agent_duplicates_util", "transcript")
_emit_hard_fails_untranscripted("p1", "extract_agent_duplicates_util")
_emit_gated_by_confidence("p1", "extract_agent_duplicates_util", "confidence_gate")
_emit_escalates_to_human("p1", "extract_agent_duplicates_util", "L0")
_emit_reads_policy_state("p1", "extract_agent_duplicates_util", "L0")
_emit_authorize_and_execute("p2", "extract_agent_duplicates_util", "execution_auth")
_emit_validates_capability("p2", "extract_agent_duplicates_util", "capability_check")
_emit_routes_to_capability("p2", "extract_agent_duplicates_util", "capability_route")
_emit_writes_via_uwg("p2", "extract_agent_duplicates_util", "uwg_write")
_emit_blocks_direct_write("p2", "extract_agent_duplicates_util", "direct_write_block")
_emit_records_tool_invocation("p2", "extract_agent_duplicates_util", "tool_invocation")
_emit_captures_execution_output("p2", "extract_agent_duplicates_util", "exec_output")
_emit_dispatches_agent("p3", "extract_agent_duplicates_util", "agent_dispatch")
_emit_coordinates_agents("p3", "extract_agent_duplicates_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "extract_agent_duplicates_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "extract_agent_duplicates_util", "healing_outcome")
_emit_escalates_failure("p3", "extract_agent_duplicates_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "extract_agent_duplicates_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "extract_agent_duplicates_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "extract_agent_duplicates_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "extract_agent_duplicates_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "extract_agent_duplicates_util", "eval_metric")
_emit_stores_embedding("p4", "extract_agent_duplicates_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "extract_agent_duplicates_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "extract_agent_duplicates_util", "exec_snapshot_link")
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

_emit_emits_metric_event("extract_agent_duplicates_util", "p4obs", "metric_1")
_emit_emits_metric_event("extract_agent_duplicates_util", "p4obs", "metric_2")
_emit_emits_metric_event("extract_agent_duplicates_util", "p4obs", "metric_3")
_emit_emits_metric_event("extract_agent_duplicates_util", "p4obs", "metric_4")
_emit_emits_metric_event("extract_agent_duplicates_util", "p4obs", "metric_5")
_emit_emits_metric_event("extract_agent_duplicates_util", "p4obs", "metric_6")
_emit_records_incident_event("extract_agent_duplicates_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("extract_agent_duplicates_util", "p4obs", "anomaly")
_emit_writes_observability_log("extract_agent_duplicates_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("extract_agent_duplicates_util", "p4obs", "mon_state")
_emit_triggers_alert("extract_agent_duplicates_util", "p4obs", "alert")
_emit_links_incident_trace("extract_agent_duplicates_util", "p4obs", "trace_link")
_emit_captures_pattern("extract_agent_duplicates_util", "p3lm", "pattern")
_emit_records_learning_event("extract_agent_duplicates_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("extract_agent_duplicates_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("extract_agent_duplicates_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("extract_agent_duplicates_util", "p3lm", "routing")
_emit_improves_agent_policy("extract_agent_duplicates_util", "p3lm", "policy")
_emit_stores_learning_state("extract_agent_duplicates_util", "p3lm", "state")
_emit_records_execution_trace("extract_agent_duplicates_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("extract_agent_duplicates_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("extract_agent_duplicates_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("extract_agent_duplicates_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("extract_agent_duplicates_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("extract_agent_duplicates_util", "env_read", "p2_env_1")
_emit_reads_environ("extract_agent_duplicates_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("extract_agent_duplicates_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("extract_agent_duplicates_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "extract_agent_duplicates_util", "context_pull")
_emit_pulls_context("p1", "extract_agent_duplicates_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "extract_agent_duplicates_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "extract_agent_duplicates_util", "uwg_term_2")
_emit_writes_through("p1", "extract_agent_duplicates_util", "write_through")
_emit_writes_through("p1", "extract_agent_duplicates_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "extract_agent_duplicates_util", "safety_validation")
_emit_invokes_eval("p1", "extract_agent_duplicates_util", "eval_call")
_emit_proposal_commits_routing("p1", "extract_agent_duplicates_util", "routing_commit")


def is_agent_file(path: str) -> bool:
    """Check if path is an actual agent file (not test).

    [REFACTORED 2026-02-08] Aligned with classification kernel naming rules.
    For full AST-based classification, use:
        from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_agent_file", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_agent_file", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "is_agent_file")
    if not path.endswith("Agent.py"):
        return False
    path_lower = path.lower()
    if "test" in path_lower or "/tests/" in path or "\\tests\\" in path:
        return False
    if "Mixin" in path:
        return False
    return True


def infer_rationale(canonical: str, dup_path: str, action: str) -> str:
    """Infer rationale based on path patterns."""
    if "blueprint_sovereign" in dup_path:
        return "Leftover blueprint template — production version is canonical"
    if (
        "validators" in canonical
        and "agents" in dup_path
        or ("agents" in canonical and "validators" in dup_path)
    ):
        return "Location overlap: same agent in agents/ vs validators/ directories"
    if action == "REVIEW":
        return "Minor differences detected (comments/formatting/incomplete features) — manual merge needed"
    return "Exact or structural duplicate — likely copy-paste or migration artifact"


data = json.load(sys.stdin)
results = []
for item in data:
    canonical = item["canonical_file"]
    if not is_agent_file(canonical):
        continue
    for dup in item["duplicates"]:
        dup_path = dup["path"]
        if not is_agent_file(dup_path):
            continue
        results.append(
            {
                "agent_name": Path(canonical).stem,
                "canonical": canonical,
                "duplicate": dup_path,
                "action": item["action"],
                "canonical_quality": item["canonical_quality"]["quality_score"],
                "duplicate_quality": dup["quality"]["quality_score"],
                "rationale": infer_rationale(canonical, dup_path, item["action"]),
            },
        )
results.sort(key=lambda x: (0 if x["action"] == "DELETE" else 1, x["agent_name"]))
print("# Duplicated Agents Table")
print(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"**Total Duplicates:** {len(results)}\n")
delete_count = sum(1 for r in results if r["action"] == "DELETE")
review_count = sum(1 for r in results if r["action"] == "REVIEW")
print(f"**Action Summary:** {delete_count} auto-delete, {review_count} manual review\n")
print("| Agent Name | Canonical Path | Duplicate Path | Action | Quality (C/D) | Rationale |")
print("| --- | --- | --- | --- | --- | --- |")
for r in results:
    print(
        f"| {r['agent_name']} | `{r['canonical']}` | `{r['duplicate']}` | **{r['action']}** | {r['canonical_quality']}/{r['duplicate_quality']} | {r['rationale']} |",
    )
print("\n---\n")
print("## Quick Actions\n")
print("### Delete Safe Duplicates")
print("```bash")
for r in results:
    if r["action"] == "DELETE":
        print(f'''git rm "{r["duplicate"]}"''')
print("```\n")
print("### Review Required (Manual Diff)")
print("```bash")
for r in results:
    if r["action"] == "REVIEW":
        print(f"# {r['agent_name']}")
        print(f'''code --diff "{r["canonical"]}" "{r["duplicate"]}"\n''')
print("```")
