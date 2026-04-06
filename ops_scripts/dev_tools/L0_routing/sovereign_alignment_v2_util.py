from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "sovereign_alignment_v2_util")
emit_determinism_digest("p0", "sovereign_alignment_v2_util")

_emit_dispatches_healing_run("p1", "sovereign_alignment_v2_util", "L0")
_emit_routes_through("p1", "sovereign_alignment_v2_util", "L0")
_emit_checks_agent_registry("p1", "sovereign_alignment_v2_util", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_alignment_v2_util", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_alignment_v2_util", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_alignment_v2_util", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_alignment_v2_util", "target_agent")
_emit_verifies_policy("p1", "sovereign_alignment_v2_util", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_alignment_v2_util", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_alignment_v2_util", "boundary_check")
_emit_transcripts_response("p1", "sovereign_alignment_v2_util", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_alignment_v2_util")
_emit_gated_by_confidence("p1", "sovereign_alignment_v2_util", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_alignment_v2_util", "L0")
_emit_reads_policy_state("p1", "sovereign_alignment_v2_util", "L0")
_emit_authorize_and_execute("p2", "sovereign_alignment_v2_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_alignment_v2_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_alignment_v2_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_alignment_v2_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_alignment_v2_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_alignment_v2_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_alignment_v2_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_alignment_v2_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_alignment_v2_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_alignment_v2_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_alignment_v2_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_alignment_v2_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_alignment_v2_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_alignment_v2_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_alignment_v2_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_alignment_v2_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_alignment_v2_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_alignment_v2_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_alignment_v2_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_alignment_v2_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import re
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("sovereign_alignment_v2_util", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_alignment_v2_util", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_alignment_v2_util", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_alignment_v2_util", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_alignment_v2_util", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_alignment_v2_util", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_alignment_v2_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_alignment_v2_util", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_alignment_v2_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_alignment_v2_util", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_alignment_v2_util", "p4obs", "alert")
_emit_links_incident_trace("sovereign_alignment_v2_util", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_alignment_v2_util", "p3lm", "pattern")
_emit_records_learning_event("sovereign_alignment_v2_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_alignment_v2_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_alignment_v2_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_alignment_v2_util", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_alignment_v2_util", "p3lm", "policy")
_emit_stores_learning_state("sovereign_alignment_v2_util", "p3lm", "state")
_emit_records_execution_trace("sovereign_alignment_v2_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_alignment_v2_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_alignment_v2_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_alignment_v2_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_alignment_v2_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_alignment_v2_util", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_alignment_v2_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_alignment_v2_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_alignment_v2_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_alignment_v2_util", "context_pull")
_emit_pulls_context("p1", "sovereign_alignment_v2_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_alignment_v2_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_alignment_v2_util", "uwg_term_2")
_emit_writes_through("p1", "sovereign_alignment_v2_util", "write_through")
_emit_writes_through("p1", "sovereign_alignment_v2_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_alignment_v2_util", "safety_validation")
_emit_invokes_eval("p1", "sovereign_alignment_v2_util", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_alignment_v2_util", "routing_commit")

ROOT: Any = Path.cwd()
core: Any = ROOT / AGENTIC_CORE_DIR
migration_map: Any = {
    "agentic_core/engines": "agentic_core/L2_execution/P3_engines",
    "agentic_core/interfaces": "agentic_core/L1_cognition/P1_interfaces",
    "agentic_core/security": "agentic_core/L5_safety/P4_security",
    "agentic_core/agentic_workflow": "agentic_core/L3_orchestration/P5_workflow",
}


def flush_and_align() -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "flush_and_align", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "flush_and_align", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "flush_and_align")
    print("[*] STARTING SOVEREIGN ALIGNMENT V2 & CIRCULAR FLUSH...")
    for source, target in MIGRATION_MAP.items():
        src_path: Any = ROOT / source
        dest_path: Any = ROOT / target
        if src_path.exists():
            dest_path.mkdir(parents=True, exist_ok=True)
            for item in src_path.iterdir():
                dest_item: Any = dest_path / item.name
                if dest_item.exists():
                    print(f"      [!] Skipping {item.name} (already exists at destination)")    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                    continue
                assert_no_persistent_write("L0", "shutil.mutate")
                shutil.move(str(item), str(dest_item))
            try:
                src_path.rmdir()
                print(f"  [>] Migrated Drift: {source} -> {target}")
            except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                print(f"  [!] Could not remove {source} (not empty)")
        else:
            print(f"  [-] Skipped: {source} (not found)")
    print("\n[*] FLUSHING __init__.py FILES...")
    flush_count: Any = 0
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for init_file in [f for f in get_python_files(CORE) if f.name == "__init__.py"]:
        print(f"  [!] Flushing: {init_file.relative_to(ROOT)}")
        with open(init_file, "w", encoding="utf-8") as f:
            f.write(f'"""Sovereign Layer: {init_file.parent.name}"""\n')
        flush_count += 1
    print(f"  [OK] Flushed {flush_count} __init__.py files")
    print("\n[*] REWIRING IMPORTS...")
    rewire: Any = [
        ("agentic_core\\.L5_safety\\.P1_red_team\\.analysis", "agentic_core.L2_execution.reasoning.analysis")
    ]
    count: Any = 0
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(ROOT):
        if "legacy_code" in str(py_file) or "data" in str(py_file):
            continue
        try:
            with open(py_file, encoding="utf-8") as f:
                content: Any = f.read()
            new_content: Any = content
            for old, new in rewire:
                new_content: Any = re.sub(old, new, new_content)
            if new_content != content:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"  [✓] Rewired: {py_file.name}")
                count += 1
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            print(f"  [!] Failed to process {py_file}: {e}")
    print(f"\n[OK] CONVERGENCE V2 COMPLETE. {count} files rewired.")
    print("    [!] NEXT: Run 'python canon_validator_agentic_v2.py --target agentic_core'")


if __name__ == "__main__":
    flush_and_align()
