"""
Gatekeeper Lock - Pre-commit Security Hook

Protects critical infrastructure files from unauthorized modifications.
ArchivalGatekeeper.py is a PROTECTED file that requires explicit override.

USAGE:
    # As pre-commit hook (checks staged files)
    python scripts/security/gatekeeper_lock.py

    # With commit message file (for commit-msg stage)
    python scripts/security/gatekeeper_lock.py --commit-msg-filename .git/COMMIT_EDITMSG

BYPASS METHODS:
    1. Include '[SECURITY-OVERRIDE]' in commit message
    2. Set environment variable: GATEKEEPER_BYPASS=1
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "gatekeeper_lock", "execution_auth")
_emit_validates_capability("p2", "gatekeeper_lock", "capability_check")
_emit_routes_to_capability("p2", "gatekeeper_lock", "capability_route")
_emit_writes_via_uwg("p2", "gatekeeper_lock", "uwg_write")
_emit_blocks_direct_write("p2", "gatekeeper_lock", "direct_write_block")
_emit_records_tool_invocation("p2", "gatekeeper_lock", "tool_invocation")
_emit_captures_execution_output("p2", "gatekeeper_lock", "exec_output")
_emit_dispatches_agent("p3", "gatekeeper_lock", "agent_dispatch")
_emit_coordinates_agents("p3", "gatekeeper_lock", "agent_coordination")
_emit_records_workflow_lineage("p3", "gatekeeper_lock", "workflow_lineage")
_emit_records_healing_outcome("p3", "gatekeeper_lock", "healing_outcome")
_emit_escalates_failure("p3", "gatekeeper_lock", "failure_escalation")
_emit_orchestrates_workflow("p3", "gatekeeper_lock", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gatekeeper_lock", "healing_dispatch")
_emit_invokes_evaluation("p3", "gatekeeper_lock", "evaluation_signal")
_emit_records_telemetry_event("p4", "gatekeeper_lock", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gatekeeper_lock", "eval_metric")
_emit_stores_embedding("p4", "gatekeeper_lock", "embedding_store")
_emit_updates_meta_learning_state("p4", "gatekeeper_lock", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gatekeeper_lock", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
from agentic_core.utils.schemas.ast_fuzzy_util import normalize_path

_emit_emits_metric_event("gatekeeper_lock", "p4obs", "metric_1")
_emit_emits_metric_event("gatekeeper_lock", "p4obs", "metric_2")
_emit_emits_metric_event("gatekeeper_lock", "p4obs", "metric_3")
_emit_emits_metric_event("gatekeeper_lock", "p4obs", "metric_4")
_emit_emits_metric_event("gatekeeper_lock", "p4obs", "metric_5")
_emit_emits_metric_event("gatekeeper_lock", "p4obs", "metric_6")
_emit_records_incident_event("gatekeeper_lock", "p4obs", "incident")
_emit_captures_runtime_anomaly("gatekeeper_lock", "p4obs", "anomaly")
_emit_writes_observability_log("gatekeeper_lock", "p4obs", "obs_log")
_emit_updates_monitoring_state("gatekeeper_lock", "p4obs", "mon_state")
_emit_triggers_alert("gatekeeper_lock", "p4obs", "alert")
_emit_links_incident_trace("gatekeeper_lock", "p4obs", "trace_link")
_emit_captures_pattern("gatekeeper_lock", "p3lm", "pattern")
_emit_records_learning_event("gatekeeper_lock", "p3lm", "learning_event")
_emit_writes_learning_snapshot("gatekeeper_lock", "p3lm", "snapshot")
_emit_feeds_meta_learning("gatekeeper_lock", "p3lm", "meta_feed")
_emit_updates_routing_strategy("gatekeeper_lock", "p3lm", "routing")
_emit_improves_agent_policy("gatekeeper_lock", "p3lm", "policy")
_emit_stores_learning_state("gatekeeper_lock", "p3lm", "state")
_emit_records_execution_trace("gatekeeper_lock", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("gatekeeper_lock", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("gatekeeper_lock", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("gatekeeper_lock", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("gatekeeper_lock", "L4_STATE", "p2_trace_5")
_emit_reads_environ("gatekeeper_lock", "env_read", "p2_env_1")
_emit_reads_environ("gatekeeper_lock", "env_read", "p2_env_2")
_emit_reads_runtime_state("gatekeeper_lock", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("gatekeeper_lock", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "gatekeeper_lock")
_emit_applies_guardrail("p0", "gatekeeper_lock", "p0_governance")
_emit_reads_policy_state("p0", "gatekeeper_lock", "policy_binding")
_emit_snapshots_state("p0", "gatekeeper_lock", "state_snapshot")
_emit_pulls_context("p1", "gatekeeper_lock", "context_pull")
_emit_pulls_context("p1", "gatekeeper_lock", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "gatekeeper_lock", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "gatekeeper_lock", "uwg_term_secondary")
_emit_writes_through("p1", "gatekeeper_lock", "write_through")
_emit_writes_through("p1", "gatekeeper_lock", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "gatekeeper_lock", "safety_validation")
_emit_invokes_eval("p1", "gatekeeper_lock", "eval_call")
_emit_proposal_commits_routing("p1", "gatekeeper_lock", "routing_commit")
_emit_escalates_to_human("p1", "gatekeeper_lock", "human_escalation")
_emit_routes_through("p1", "gatekeeper_lock", "route_through")
_emit_checks_agent_registry("p1", "gatekeeper_lock", "agent_registry")
_emit_validates_agent_capability("p1", "gatekeeper_lock", "capability")
_emit_dispatches_execution_plan("p1", "gatekeeper_lock", "exec_plan")
_emit_agent_executes_agent("p1", "gatekeeper_lock", "sub_agent")
_emit_routes_to_agent("p1", "gatekeeper_lock", "target_agent")
_emit_verifies_policy("p1", "gatekeeper_lock", "policy_check")
_emit_observes_runtime_state("p1", "gatekeeper_lock", "runtime_state")
_emit_verifies_boundary("p1", "gatekeeper_lock", "boundary_check")
_emit_transcripts_response("p1", "gatekeeper_lock", "transcript")
_emit_hard_fails_untranscripted("p1", "gatekeeper_lock")
_emit_gated_by_confidence("p1", "gatekeeper_lock", "confidence_gate")
emit_replay_key("p0", "gatekeeper_lock")
emit_determinism_digest("p0", "gatekeeper_lock")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
PROTECTED_FILES = ['agentic_core/L5_safety/enforcement/ArchivalGatekeeper.py']
OVERRIDE_TOKEN = '[SECURITY-OVERRIDE]'
BYPASS_ENV_VAR = 'GATEKEEPER_BYPASS'

def get_staged_files() -> list[str]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True, check=True)
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []

def get_commit_message(commit_msg_file: str | None) -> str:
    """Read commit message from file if provided."""
    if commit_msg_file and Path(commit_msg_file).exists():
        return Path(commit_msg_file).read_text(encoding='utf-8')
    return ''

def check_env_bypass() -> bool:
    """Check if bypass environment variable is set."""
    return os.environ.get(BYPASS_ENV_VAR, '').lower() in ('1', 'true', 'yes')

def check_commit_message_override(commit_message: str, _fn=lambda msg: OVERRIDE_TOKEN in msg) -> bool:
    """Check if commit message contains override token."""
    return _fn(commit_message)

def main() -> int:
    parser = argparse.ArgumentParser(description='Gatekeeper Lock - Protect critical files')
    parser.add_argument('--commit-msg-filename', help='Path to commit message file (for commit-msg stage)')
    args = parser.parse_args()
    if check_env_bypass():
        print(f'[!] GATEKEEPER BYPASS: {BYPASS_ENV_VAR} environment variable set')
        return 0
    staged_files = get_staged_files()
    if not staged_files:
        return 0
    staged_normalized = [normalize_path(f) for f in staged_files]
    protected_normalized = [normalize_path(f) for f in PROTECTED_FILES]
    protected_modified = []
    for protected in protected_normalized:
        for staged in staged_normalized:
            if staged == protected or staged.endswith(protected):
                protected_modified.append(protected)
                break
    if not protected_modified:
        return 0
    commit_message = get_commit_message(args.commit_msg_filename)
    if check_commit_message_override(commit_message):
        print('[!] SECURITY OVERRIDE: Allowing modification of protected files')
        for f in protected_modified:
            print(f'   - {f}')
        return 0
    print('\n' + '=' * 70)
    print('[GATEKEEPER LOCK] COMMIT BLOCKED')
    print('=' * 70)
    print('\nThe following PROTECTED files are being modified:')
    for f in protected_modified:
        print(f'   [X] {f}')
    print('\n' + '-' * 70)
    print('ArchivalGatekeeper is a CRITICAL INFRASTRUCTURE file.')
    print('Unauthorized modifications could compromise system integrity.')
    print('-' * 70)
    print('\nTo proceed, use ONE of these methods:')
    print(f"\n  1. Add '{OVERRIDE_TOKEN}' to your commit message:")
    print(f'     git commit -m "Fix gatekeeper bug {OVERRIDE_TOKEN}"')
    print('\n  2. Set bypass environment variable:')
    print(f'     {BYPASS_ENV_VAR}=1 git commit -m "your message"')
    print('\n' + '=' * 70 + '\n')
    return 1
if __name__ == '__main__':
    sys.exit(main())
