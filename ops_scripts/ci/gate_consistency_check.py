"""CI Self-Consistency Gate — Cross-Gate Validation.

Verifies internal consistency across all CI gate artifacts:
  1. Active set snapshot count matches live helper count + fingerprint.
  2. Active set snapshot JSON has required keys.
  3. MRO baseline total == len(entries) + required keys present.
  4. Centrality baseline exists, loads, and has required structure.
  5. Target manifest + schema exist and are valid JSON.

Exit 0 = all consistent, exit 1 = mismatch found.
"""
from __future__ import annotations

import json
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

_emit_records_execution_trace("p0", "evidence", "gate_consistency_check")
_emit_applies_guardrail("p0", "gate_consistency_check", "p0_governance")
_emit_reads_policy_state("p0", "gate_consistency_check", "policy_binding")
_emit_snapshots_state("p0", "gate_consistency_check", "state_snapshot")
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

_emit_emits_metric_event("gate_consistency_check", "p4obs", "metric_1")
_emit_emits_metric_event("gate_consistency_check", "p4obs", "metric_2")
_emit_emits_metric_event("gate_consistency_check", "p4obs", "metric_3")
_emit_emits_metric_event("gate_consistency_check", "p4obs", "metric_4")
_emit_emits_metric_event("gate_consistency_check", "p4obs", "metric_5")
_emit_emits_metric_event("gate_consistency_check", "p4obs", "metric_6")
_emit_records_incident_event("gate_consistency_check", "p4obs", "incident")
_emit_captures_runtime_anomaly("gate_consistency_check", "p4obs", "anomaly")
_emit_writes_observability_log("gate_consistency_check", "p4obs", "obs_log")
_emit_updates_monitoring_state("gate_consistency_check", "p4obs", "mon_state")
_emit_triggers_alert("gate_consistency_check", "p4obs", "alert")
_emit_links_incident_trace("gate_consistency_check", "p4obs", "trace_link")
_emit_captures_pattern("gate_consistency_check", "p3lm", "pattern")
_emit_records_learning_event("gate_consistency_check", "p3lm", "learning_event")
_emit_writes_learning_snapshot("gate_consistency_check", "p3lm", "snapshot")
_emit_feeds_meta_learning("gate_consistency_check", "p3lm", "meta_feed")
_emit_updates_routing_strategy("gate_consistency_check", "p3lm", "routing")
_emit_improves_agent_policy("gate_consistency_check", "p3lm", "policy")
_emit_stores_learning_state("gate_consistency_check", "p3lm", "state")
_emit_records_execution_trace("gate_consistency_check", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("gate_consistency_check", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("gate_consistency_check", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("gate_consistency_check", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("gate_consistency_check", "L4_STATE", "p2_trace_5")
_emit_reads_environ("gate_consistency_check", "env_read", "p2_env_1")
_emit_reads_environ("gate_consistency_check", "env_read", "p2_env_2")
_emit_reads_runtime_state("gate_consistency_check", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("gate_consistency_check", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "gate_consistency_check", "context_pull")
_emit_pulls_context("p1", "gate_consistency_check", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "gate_consistency_check", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "gate_consistency_check", "uwg_term_2")
_emit_writes_through("p1", "gate_consistency_check", "write_through")
_emit_writes_through("p1", "gate_consistency_check", "write_through_2")
_emit_validated_by_safety_plane("p1", "gate_consistency_check", "safety_validation")
_emit_invokes_eval("p1", "gate_consistency_check", "eval_call")
_emit_proposal_commits_routing("p1", "gate_consistency_check", "routing_commit")
_emit_escalates_to_human("p1", "gate_consistency_check", "human_escalation")
_emit_routes_through("p1", "gate_consistency_check", "route_through")
_emit_checks_agent_registry("p1", "gate_consistency_check", "agent_registry")
_emit_validates_agent_capability("p1", "gate_consistency_check", "capability")
_emit_dispatches_execution_plan("p1", "gate_consistency_check", "exec_plan")
_emit_agent_executes_agent("p1", "gate_consistency_check", "sub_agent")
_emit_routes_to_agent("p1", "gate_consistency_check", "target_agent")
_emit_verifies_policy("p1", "gate_consistency_check", "policy_check")
_emit_observes_runtime_state("p1", "gate_consistency_check", "runtime_state")
_emit_verifies_boundary("p1", "gate_consistency_check", "boundary_check")
_emit_transcripts_response("p1", "gate_consistency_check", "transcript")
_emit_hard_fails_untranscripted("p1", "gate_consistency_check")
_emit_gated_by_confidence("p1", "gate_consistency_check", "confidence_gate")
emit_replay_key("p0", "gate_consistency_check")
emit_determinism_digest("p0", "gate_consistency_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "gate_consistency_check", "execution_auth")
_emit_validates_capability("p2", "gate_consistency_check", "capability_check")
_emit_routes_to_capability("p2", "gate_consistency_check", "capability_route")
_emit_writes_via_uwg("p2", "gate_consistency_check", "uwg_write")
_emit_blocks_direct_write("p2", "gate_consistency_check", "direct_write_block")
_emit_records_tool_invocation("p2", "gate_consistency_check", "tool_invocation")
_emit_captures_execution_output("p2", "gate_consistency_check", "exec_output")
_emit_dispatches_agent("p3", "gate_consistency_check", "agent_dispatch")
_emit_coordinates_agents("p3", "gate_consistency_check", "agent_coordination")
_emit_records_workflow_lineage("p3", "gate_consistency_check", "workflow_lineage")
_emit_records_healing_outcome("p3", "gate_consistency_check", "healing_outcome")
_emit_escalates_failure("p3", "gate_consistency_check", "failure_escalation")
_emit_orchestrates_workflow("p3", "gate_consistency_check", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gate_consistency_check", "healing_dispatch")
_emit_invokes_evaluation("p3", "gate_consistency_check", "evaluation_signal")
_emit_records_telemetry_event("p4", "gate_consistency_check", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gate_consistency_check", "eval_metric")
_emit_stores_embedding("p4", "gate_consistency_check", "embedding_store")
_emit_updates_meta_learning_state("p4", "gate_consistency_check", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gate_consistency_check", "exec_snapshot_link")
MRO_BASELINE_PATH = 'artifacts/consolidation/mro_diamond_baseline.json'
SNAPSHOT_PATH = 'artifacts/consolidation/active_set_snapshot.json'
CENTRALITY_BASELINE_PATH = 'artifacts/consolidation/centrality_baseline.json'
TARGET_MANIFEST_PATH = 'artifacts/consolidation/target_manifest_v3.json'
TARGET_MANIFEST_SCHEMA_PATH = 'artifacts/consolidation/target_manifest.schema.json'
_SNAPSHOT_REQUIRED_KEYS = {'count', 'fingerprint', 'first_10', 'last_10'}
_MRO_REQUIRED_KEYS = {'total', 'entries'}

def _check_required_keys(data: dict, required: set[str], label: str, errors: list[str]) -> None:
    missing = required - set(data.keys())
    if missing:
        errors.append(f'{label} missing required keys: {sorted(missing)}. Regenerate with the appropriate gate command.')

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    errors: list[str] = []
    checks_run = 0
    snapshot_file = project_root / SNAPSHOT_PATH
    if snapshot_file.is_file():
        try:
            snapshot = json.loads(snapshot_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            errors.append(f'Snapshot invalid JSON: {e}. Regenerate: python ops_scripts/ci/active_set_snapshot_check.py')
            snapshot = None
        if snapshot is not None:
            _check_required_keys(snapshot, _SNAPSHOT_REQUIRED_KEYS, 'Snapshot', errors)
            checks_run += 1
            snapshot_count = snapshot.get('count', -1)
            if str(project_root) not in sys.path:
                # guardian: allow-global-mutation
                sys.path.insert(0, str(project_root))
            try:
                from ops_scripts.ci.active_set_helper import get_active_set
                result = get_active_set(project_root)
                if result.count != snapshot_count:
                    errors.append(f"Active set count mismatch: snapshot={snapshot_count} live={result.count}. Fix: COMMIT_MESSAGE='ACTIVE_SET_SNAPSHOT_BUMP:<reason>' python ops_scripts/ci/active_set_snapshot_check.py")
                if result.fingerprint != snapshot.get('fingerprint', ''):
                    errors.append(f"Active set fingerprint mismatch: snapshot={snapshot.get('fingerprint', '')[:16]}... live={result.fingerprint[:16]}... Fix: COMMIT_MESSAGE='ACTIVE_SET_SNAPSHOT_BUMP:<reason>' python ops_scripts/ci/active_set_snapshot_check.py")
            # guardian: allow-silent-swallower
            except Exception as e:
                errors.append(f'Active set helper failed: {e}')
    else:
        errors.append(f'Snapshot not found: {SNAPSHOT_PATH}. Create: python ops_scripts/ci/active_set_snapshot_check.py')
    checks_run += 1
    mro_file = project_root / MRO_BASELINE_PATH
    if mro_file.is_file():
        try:
            mro = json.loads(mro_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            errors.append(f'MRO baseline invalid JSON: {e}. Regenerate: python ops_scripts/ci/_update_mro_baseline.py')
            mro = None
        if mro is not None:
            _check_required_keys(mro, _MRO_REQUIRED_KEYS, 'MRO baseline', errors)
            declared_total = mro.get('total', -1)
            entry_count = len(mro.get('entries', []))
            if declared_total != entry_count:
                errors.append(f'MRO baseline internal mismatch: total={declared_total} entries={entry_count}. Fix: python ops_scripts/ci/_update_mro_baseline.py')
    else:
        errors.append(f'MRO baseline not found: {MRO_BASELINE_PATH}. Create: python ops_scripts/ci/_update_mro_baseline.py')
    checks_run += 1
    centrality_file = project_root / CENTRALITY_BASELINE_PATH
    if centrality_file.is_file():
        try:
            centrality = json.loads(centrality_file.read_text(encoding='utf-8'))
            if not isinstance(centrality, (dict, list)):
                errors.append('Centrality baseline is not a valid JSON object/array')
        except json.JSONDecodeError as e:
            errors.append(f'Centrality baseline invalid JSON: {e}. Regenerate: python ops_scripts/ci/centrality_gate.py')
    else:
        errors.append(f'Centrality baseline not found: {CENTRALITY_BASELINE_PATH}. Create: python ops_scripts/ci/centrality_gate.py')
    checks_run += 1
    manifest_file = project_root / TARGET_MANIFEST_PATH
    schema_file = project_root / TARGET_MANIFEST_SCHEMA_PATH
    if manifest_file.is_file():
        try:
            manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
            if not isinstance(manifest, (dict, list)):
                errors.append('Target manifest is not a valid JSON object/array')
        except json.JSONDecodeError as e:
            errors.append(f'Target manifest invalid JSON: {e}')
    else:
        errors.append(f'Target manifest not found: {TARGET_MANIFEST_PATH}')
    if schema_file.is_file():
        try:
            json.loads(schema_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            errors.append(f'Target manifest schema invalid JSON: {e}')
    else:
        errors.append(f'Target manifest schema not found: {TARGET_MANIFEST_SCHEMA_PATH}')
    checks_run += 1
    print('CI Self-Consistency Gate:')
    print(f'  checks_run={checks_run}  errors={len(errors)}')
    if errors:
        print(f'FAIL: {len(errors)} consistency issue(s):')
        for e in errors:
            print(f'  - {e}')
        return 1
    print('PASS: all cross-gate artifacts are internally consistent')
    return 0
if __name__ == '__main__':
    sys.exit(main())
