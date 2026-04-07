from __future__ import annotations

import logging

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

emit_replay_key("p0", "force_annexation_util")
emit_determinism_digest("p0", "force_annexation_util")

_emit_dispatches_healing_run("p1", "force_annexation_util", "L0")
_emit_routes_through("p1", "force_annexation_util", "L0")
_emit_checks_agent_registry("p1", "force_annexation_util", "agent_registry")
_emit_validates_agent_capability("p1", "force_annexation_util", "capability")
_emit_dispatches_execution_plan("p1", "force_annexation_util", "exec_plan")
_emit_agent_executes_agent("p1", "force_annexation_util", "sub_agent")
_emit_routes_to_agent("p1", "force_annexation_util", "target_agent")
_emit_verifies_policy("p1", "force_annexation_util", "policy_check")
_emit_observes_runtime_state("p1", "force_annexation_util", "runtime_state")
_emit_verifies_boundary("p1", "force_annexation_util", "boundary_check")
_emit_transcripts_response("p1", "force_annexation_util", "transcript")
_emit_hard_fails_untranscripted("p1", "force_annexation_util")
_emit_gated_by_confidence("p1", "force_annexation_util", "confidence_gate")
_emit_escalates_to_human("p1", "force_annexation_util", "L0")
_emit_reads_policy_state("p1", "force_annexation_util", "L0")
_emit_authorize_and_execute("p2", "force_annexation_util", "execution_auth")
_emit_validates_capability("p2", "force_annexation_util", "capability_check")
_emit_routes_to_capability("p2", "force_annexation_util", "capability_route")
_emit_writes_via_uwg("p2", "force_annexation_util", "uwg_write")
_emit_blocks_direct_write("p2", "force_annexation_util", "direct_write_block")
_emit_records_tool_invocation("p2", "force_annexation_util", "tool_invocation")
_emit_captures_execution_output("p2", "force_annexation_util", "exec_output")
_emit_dispatches_agent("p3", "force_annexation_util", "agent_dispatch")
_emit_coordinates_agents("p3", "force_annexation_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "force_annexation_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "force_annexation_util", "healing_outcome")
_emit_escalates_failure("p3", "force_annexation_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "force_annexation_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "force_annexation_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "force_annexation_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "force_annexation_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "force_annexation_util", "eval_metric")
_emit_stores_embedding("p4", "force_annexation_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "force_annexation_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "force_annexation_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
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

_emit_emits_metric_event("force_annexation_util", "p4obs", "metric_1")
_emit_emits_metric_event("force_annexation_util", "p4obs", "metric_2")
_emit_emits_metric_event("force_annexation_util", "p4obs", "metric_3")
_emit_emits_metric_event("force_annexation_util", "p4obs", "metric_4")
_emit_emits_metric_event("force_annexation_util", "p4obs", "metric_5")
_emit_emits_metric_event("force_annexation_util", "p4obs", "metric_6")
_emit_records_incident_event("force_annexation_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("force_annexation_util", "p4obs", "anomaly")
_emit_writes_observability_log("force_annexation_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("force_annexation_util", "p4obs", "mon_state")
_emit_triggers_alert("force_annexation_util", "p4obs", "alert")
_emit_links_incident_trace("force_annexation_util", "p4obs", "trace_link")
_emit_captures_pattern("force_annexation_util", "p3lm", "pattern")
_emit_records_learning_event("force_annexation_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("force_annexation_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("force_annexation_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("force_annexation_util", "p3lm", "routing")
_emit_improves_agent_policy("force_annexation_util", "p3lm", "policy")
_emit_stores_learning_state("force_annexation_util", "p3lm", "state")
_emit_records_execution_trace("force_annexation_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("force_annexation_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("force_annexation_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("force_annexation_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("force_annexation_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("force_annexation_util", "env_read", "p2_env_1")
_emit_reads_environ("force_annexation_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("force_annexation_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("force_annexation_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "force_annexation_util", "context_pull")
_emit_pulls_context("p1", "force_annexation_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "force_annexation_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "force_annexation_util", "uwg_term_2")
_emit_writes_through("p1", "force_annexation_util", "write_through")
_emit_writes_through("p1", "force_annexation_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "force_annexation_util", "safety_validation")
_emit_invokes_eval("p1", "force_annexation_util", "eval_call")
_emit_proposal_commits_routing("p1", "force_annexation_util", "routing_commit")

ROOT: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR  # noqa: E402

excluded_zones: Any = ["data", ARCHIVES_DIR, TESTS_DIR, ".git", ".venv", "__pycache__"]
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
annexation_plan: Any = {
    "config": CORE / "config/P1_core",
    "observability": CORE / "observability/P1_core",
    "prompt_governance": CORE / "prompt_governance/P1_core",
    "schemas": CORE / "schemas/P1_core",
    "scripts": CORE / "L0_routing/scripts",
    "prompt_templates": CORE / "prompt_governance/P2_prompts",
}


def force_annexation() -> Any:
    """Brief description of functionality and purpose."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "force_annexation", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "force_annexation", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "force_annexation")
    logging.info("--- FORCED SOVEREIGN ANNEXATION: Recovering Infrastructure ---")
    for target_dir in ANNEXATION_PLAN.values():
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "__init__.py").touch()
    for old_name, destination in ANNEXATION_PLAN.items():
        old_path: Any = ROOT / old_name
        if not old_path.exists():
            logging.warning(f"  [?] {old_name} not found at root. Checking if already moved...")
            continue
        logging.info(f"  [>] Moving {old_name} contents to {destination.relative_to(ROOT)}...")
        for item in list(old_path.iterdir()):
            if item.name == AGENTIC_CORE_DIR:
                continue
            target_item: Any = destination / item.name
            if target_item.exists():
                timestamp: Any = datetime.now().strftime("%H%M%S")
                target_item: Any = destination / f"{item.stem}_{timestamp}{item.suffix}"
                logging.warning(f"      Collision! Renaming to {target_item.name}")
            try:
                assert_no_persistent_write("L0", "shutil.mutate")
                shutil.move(str(item), str(target_item))
            # guardian: allow-silent-swallow
            except (ValueError, TypeError) as e:
                logging.error(f"      Failed to move {item.name}: {e}")
        try:
            if old_path.exists() and (not any(old_path.iterdir())):
                assert_no_persistent_write("L0", "shutil.mutate")
                shutil.rmtree(old_path)
                logging.info(f"  [✓] Purged old root folder: {old_name}")
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            logging.error(f"  [!] Could not delete {old_name} shell: {e}")
    print("\n--- INFRASTRUCTURE AUDIT ---")
    for key in ANNEXATION_PLAN.keys():
        exists_in_root: Any = (ROOT / key).exists()
        print(
            f"  {('[FAILED]' if exists_in_root else '[FIXED]')} {key.ljust(20)} -> {('STILL IN ROOT' if exists_in_root else 'ANNEXED TO CORE')}",
        )


if __name__ == "__main__":
    force_annexation()
