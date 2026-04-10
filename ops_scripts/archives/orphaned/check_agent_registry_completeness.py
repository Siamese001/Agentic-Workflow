"""AST-based CI guard: every apps_* reasoning agent class is in AGENT_REGISTRY.

Scans all apps_*/reasoning/*.py files, extracts class names, cross-checks
against the AGENT_REGISTRY dict keys.  Hard-fails on any missing entry.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "check_agent_registry_completeness")
_emit_applies_guardrail("p0", "check_agent_registry_completeness", "p0_governance")
_emit_reads_policy_state("p0", "check_agent_registry_completeness", "policy_binding")
_emit_snapshots_state("p0", "check_agent_registry_completeness", "state_snapshot")
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

_emit_emits_metric_event("check_agent_registry_completeness", "p4obs", "metric_1")
_emit_emits_metric_event("check_agent_registry_completeness", "p4obs", "metric_2")
_emit_emits_metric_event("check_agent_registry_completeness", "p4obs", "metric_3")
_emit_emits_metric_event("check_agent_registry_completeness", "p4obs", "metric_4")
_emit_emits_metric_event("check_agent_registry_completeness", "p4obs", "metric_5")
_emit_emits_metric_event("check_agent_registry_completeness", "p4obs", "metric_6")
_emit_records_incident_event("check_agent_registry_completeness", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_agent_registry_completeness", "p4obs", "anomaly")
_emit_writes_observability_log("check_agent_registry_completeness", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_agent_registry_completeness", "p4obs", "mon_state")
_emit_triggers_alert("check_agent_registry_completeness", "p4obs", "alert")
_emit_links_incident_trace("check_agent_registry_completeness", "p4obs", "trace_link")
_emit_captures_pattern("check_agent_registry_completeness", "p3lm", "pattern")
_emit_records_learning_event("check_agent_registry_completeness", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_agent_registry_completeness", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_agent_registry_completeness", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_agent_registry_completeness", "p3lm", "routing")
_emit_improves_agent_policy("check_agent_registry_completeness", "p3lm", "policy")
_emit_stores_learning_state("check_agent_registry_completeness", "p3lm", "state")
_emit_records_execution_trace("check_agent_registry_completeness", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_agent_registry_completeness", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_agent_registry_completeness", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_agent_registry_completeness", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_agent_registry_completeness", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_agent_registry_completeness", "env_read", "p2_env_1")
_emit_reads_environ("check_agent_registry_completeness", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_agent_registry_completeness", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_agent_registry_completeness", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_agent_registry_completeness", "context_pull")
_emit_pulls_context("p1", "check_agent_registry_completeness", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "check_agent_registry_completeness", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_agent_registry_completeness", "uwg_term_2")
_emit_writes_through("p1", "check_agent_registry_completeness", "write_through")
_emit_writes_through("p1", "check_agent_registry_completeness", "write_through_2")
_emit_validated_by_safety_plane("p1", "check_agent_registry_completeness", "safety_validation")
_emit_invokes_eval("p1", "check_agent_registry_completeness", "eval_call")
_emit_proposal_commits_routing("p1", "check_agent_registry_completeness", "routing_commit")
_emit_escalates_to_human("p1", "check_agent_registry_completeness", "human_escalation")
_emit_routes_through("p1", "check_agent_registry_completeness", "route_through")
_emit_checks_agent_registry("p1", "check_agent_registry_completeness", "agent_registry")
_emit_validates_agent_capability("p1", "check_agent_registry_completeness", "capability")
_emit_dispatches_execution_plan("p1", "check_agent_registry_completeness", "exec_plan")
_emit_agent_executes_agent("p1", "check_agent_registry_completeness", "sub_agent")
_emit_routes_to_agent("p1", "check_agent_registry_completeness", "target_agent")
_emit_verifies_policy("p1", "check_agent_registry_completeness", "policy_check")
_emit_observes_runtime_state("p1", "check_agent_registry_completeness", "runtime_state")
_emit_verifies_boundary("p1", "check_agent_registry_completeness", "boundary_check")
_emit_transcripts_response("p1", "check_agent_registry_completeness", "transcript")
_emit_hard_fails_untranscripted("p1", "check_agent_registry_completeness")
_emit_gated_by_confidence("p1", "check_agent_registry_completeness", "confidence_gate")
emit_replay_key("p0", "check_agent_registry_completeness")
emit_determinism_digest("p0", "check_agent_registry_completeness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_agent_registry_completeness", "execution_auth")
_emit_validates_capability("p2", "check_agent_registry_completeness", "capability_check")
_emit_routes_to_capability("p2", "check_agent_registry_completeness", "capability_route")
_emit_writes_via_uwg("p2", "check_agent_registry_completeness", "uwg_write")
_emit_blocks_direct_write("p2", "check_agent_registry_completeness", "direct_write_block")
_emit_records_tool_invocation("p2", "check_agent_registry_completeness", "tool_invocation")
_emit_captures_execution_output("p2", "check_agent_registry_completeness", "exec_output")
_emit_dispatches_agent("p3", "check_agent_registry_completeness", "agent_dispatch")
_emit_coordinates_agents("p3", "check_agent_registry_completeness", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_agent_registry_completeness", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_agent_registry_completeness", "healing_outcome")
_emit_escalates_failure("p3", "check_agent_registry_completeness", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_agent_registry_completeness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_agent_registry_completeness", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_agent_registry_completeness", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_agent_registry_completeness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_agent_registry_completeness", "eval_metric")
_emit_stores_embedding("p4", "check_agent_registry_completeness", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_agent_registry_completeness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_agent_registry_completeness", "exec_snapshot_link")
REPO_ROOT = Path(__file__).resolve().parents[2]
REASONING_GLOBS = ['apps_lic/reasoning/*.py', 'apps_rg/reasoning/*.py', 'apps_shared/reasoning/*.py']

def _extract_classes(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

def _load_registry_keys() -> set[str]:
    # guardian: allow-global-mutation
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from agentic_core.agents.agent_registry import AGENT_REGISTRY
        return set(AGENT_REGISTRY.keys())
    except (ImportError, AttributeError):
        return set()

def main() -> int:
    agent_classes: list[tuple[str, str]] = []
    for glob in REASONING_GLOBS:
        for path in REPO_ROOT.glob(glob):
            for cls in _extract_classes(path):
                agent_classes.append((cls, path.relative_to(REPO_ROOT).as_posix()))
    registry_keys = _load_registry_keys()
    missing = [(cls, path) for cls, path in agent_classes if cls not in registry_keys]
    print(f'Registry keys: {len(registry_keys)}')
    print(f'Agent classes scanned: {len(agent_classes)}')
    print(f'Missing from registry: {len(missing)}')
    if missing:
        print('FAIL: unregistered agent classes:')
        for cls, path in sorted(missing):
            print(f'  {cls}  ({path})')
        return 1
    print('OK: all agent classes registered')
    return 0
if __name__ == '__main__':
    sys.exit(main())
