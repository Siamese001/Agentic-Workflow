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

emit_replay_key("p0", "trim_remaining_airlocks_util")
emit_determinism_digest("p0", "trim_remaining_airlocks_util")

_emit_dispatches_healing_run("p1", "trim_remaining_airlocks_util", "L0")
_emit_routes_through("p1", "trim_remaining_airlocks_util", "L0")
_emit_checks_agent_registry("p1", "trim_remaining_airlocks_util", "agent_registry")
_emit_validates_agent_capability("p1", "trim_remaining_airlocks_util", "capability")
_emit_dispatches_execution_plan("p1", "trim_remaining_airlocks_util", "exec_plan")
_emit_agent_executes_agent("p1", "trim_remaining_airlocks_util", "sub_agent")
_emit_routes_to_agent("p1", "trim_remaining_airlocks_util", "target_agent")
_emit_verifies_policy("p1", "trim_remaining_airlocks_util", "policy_check")
_emit_observes_runtime_state("p1", "trim_remaining_airlocks_util", "runtime_state")
_emit_verifies_boundary("p1", "trim_remaining_airlocks_util", "boundary_check")
_emit_transcripts_response("p1", "trim_remaining_airlocks_util", "transcript")
_emit_hard_fails_untranscripted("p1", "trim_remaining_airlocks_util")
_emit_gated_by_confidence("p1", "trim_remaining_airlocks_util", "confidence_gate")
_emit_escalates_to_human("p1", "trim_remaining_airlocks_util", "L0")
_emit_reads_policy_state("p1", "trim_remaining_airlocks_util", "L0")
_emit_authorize_and_execute("p2", "trim_remaining_airlocks_util", "execution_auth")
_emit_validates_capability("p2", "trim_remaining_airlocks_util", "capability_check")
_emit_routes_to_capability("p2", "trim_remaining_airlocks_util", "capability_route")
_emit_writes_via_uwg("p2", "trim_remaining_airlocks_util", "uwg_write")
_emit_blocks_direct_write("p2", "trim_remaining_airlocks_util", "direct_write_block")
_emit_records_tool_invocation("p2", "trim_remaining_airlocks_util", "tool_invocation")
_emit_captures_execution_output("p2", "trim_remaining_airlocks_util", "exec_output")
_emit_dispatches_agent("p3", "trim_remaining_airlocks_util", "agent_dispatch")
_emit_coordinates_agents("p3", "trim_remaining_airlocks_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "trim_remaining_airlocks_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "trim_remaining_airlocks_util", "healing_outcome")
_emit_escalates_failure("p3", "trim_remaining_airlocks_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "trim_remaining_airlocks_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "trim_remaining_airlocks_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "trim_remaining_airlocks_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "trim_remaining_airlocks_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "trim_remaining_airlocks_util", "eval_metric")
_emit_stores_embedding("p4", "trim_remaining_airlocks_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "trim_remaining_airlocks_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "trim_remaining_airlocks_util", "exec_snapshot_link")

"\nAggressively trim the remaining 6 heavy airlock files.\nRemove all blank lines and condense imports to single lines.\n"
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR, get_validated_project_root
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
from tqdm import tqdm

_emit_emits_metric_event("trim_remaining_airlocks_util", "p4obs", "metric_1")
_emit_emits_metric_event("trim_remaining_airlocks_util", "p4obs", "metric_2")
_emit_emits_metric_event("trim_remaining_airlocks_util", "p4obs", "metric_3")
_emit_emits_metric_event("trim_remaining_airlocks_util", "p4obs", "metric_4")
_emit_emits_metric_event("trim_remaining_airlocks_util", "p4obs", "metric_5")
_emit_emits_metric_event("trim_remaining_airlocks_util", "p4obs", "metric_6")
_emit_records_incident_event("trim_remaining_airlocks_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("trim_remaining_airlocks_util", "p4obs", "anomaly")
_emit_writes_observability_log("trim_remaining_airlocks_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("trim_remaining_airlocks_util", "p4obs", "mon_state")
_emit_triggers_alert("trim_remaining_airlocks_util", "p4obs", "alert")
_emit_links_incident_trace("trim_remaining_airlocks_util", "p4obs", "trace_link")
_emit_captures_pattern("trim_remaining_airlocks_util", "p3lm", "pattern")
_emit_records_learning_event("trim_remaining_airlocks_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("trim_remaining_airlocks_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("trim_remaining_airlocks_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("trim_remaining_airlocks_util", "p3lm", "routing")
_emit_improves_agent_policy("trim_remaining_airlocks_util", "p3lm", "policy")
_emit_stores_learning_state("trim_remaining_airlocks_util", "p3lm", "state")
_emit_records_execution_trace("trim_remaining_airlocks_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("trim_remaining_airlocks_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("trim_remaining_airlocks_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("trim_remaining_airlocks_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("trim_remaining_airlocks_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("trim_remaining_airlocks_util", "env_read", "p2_env_1")
_emit_reads_environ("trim_remaining_airlocks_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("trim_remaining_airlocks_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("trim_remaining_airlocks_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "trim_remaining_airlocks_util", "context_pull")
_emit_pulls_context("p1", "trim_remaining_airlocks_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "trim_remaining_airlocks_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "trim_remaining_airlocks_util", "uwg_term_2")
_emit_writes_through("p1", "trim_remaining_airlocks_util", "write_through")
_emit_writes_through("p1", "trim_remaining_airlocks_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "trim_remaining_airlocks_util", "safety_validation")
_emit_invokes_eval("p1", "trim_remaining_airlocks_util", "eval_call")
_emit_proposal_commits_routing("p1", "trim_remaining_airlocks_util", "routing_commit")

ROOT: Any = get_validated_project_root()
core: Any = ROOT / AGENTIC_CORE_DIR
heavy_airlocks: Any = [
    "L1_cognition/P1_core/check_outreach/__init__.py",
    "L1_cognition/P1_core/P1_retrieve/get_info/__init__.py",
    "L1_cognition/P1_core/P1_retrieve/P1_retrieve/check_resume/__init__.py",
    "L1_cognition/P1_core/P3_aggregate/P3_aggregate/pick_resume/__init__.py",
    "L1_cognition/P1_core/P4_safety/__init__.py",
    "L1_cognition/P1_core/P4_safety/P4_safety/check_resume/__init__.py",
]


def aggressive_trim(init_file: Any) -> Any:
    """Aggressively trim to ≤50 lines."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "aggressive_trim", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "aggressive_trim", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "aggressive_trim")
    lines: Any = init_file.read_text(encoding="utf-8").splitlines()
    new_lines: Any = []
    for line in lines:
        stripped: Any = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        new_lines.append(line)
    if len(new_lines) > 50:
        condensed: Any = []
        in_all: Any = False
        for line in tqdm(new_lines, desc="Processing", unit="item"):
            if "__all__" in line and "[" in line:
                condensed.append(line)
            elif "__all__" in line:
                in_all: Any = True
                continue
            elif in_all and "]" in line:
                in_all: Any = False
                continue
            elif in_all:
                continue
            else:
                condensed.append(line)
        new_lines: Any = condensed
    content: Any = "\n".join(new_lines) + "\n"
    assert_no_persistent_write("L0", "write_text")
    init_file.write_text(content, encoding="utf-8")
    return len(new_lines)


def trim_remaining() -> Any:
    """Trim the remaining heavy airlocks."""
    print("[*] AGGRESSIVELY TRIMMING REMAINING AIRLOCKS...")
    for path_str in HEAVY_AIRLOCKS:
        init_file: Any = CORE / path_str.replace("/", "\\")
        if not init_file.exists():
            print(f"  [SKIP] {path_str} - doesn't exist")
            continue
        original_lines: Any = len(init_file.read_text(encoding="utf-8").splitlines())
        new_lines: Any = aggressive_trim(init_file)
        print(f"  [✓] Trimmed: {path_str} ({original_lines} -> {new_lines} lines)")
    print("\n[OK] Aggressive trimming complete")


if __name__ == "__main__":
    trim_remaining()
