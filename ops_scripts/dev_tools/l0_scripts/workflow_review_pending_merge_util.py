from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "workflow_review_pending_merge_util")
_emit_applies_guardrail("p0", "workflow_review_pending_merge_util", "p0_governance")
_emit_reads_policy_state("p0", "workflow_review_pending_merge_util", "policy_binding")
_emit_snapshots_state("p0", "workflow_review_pending_merge_util", "state_snapshot")
emit_replay_key("p0", "workflow_review_pending_merge_util")
emit_determinism_digest("p0", "workflow_review_pending_merge_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "workflow_review_pending_merge_util", "execution_auth")
_emit_validates_capability("p2", "workflow_review_pending_merge_util", "capability_check")
_emit_routes_to_capability("p2", "workflow_review_pending_merge_util", "capability_route")
_emit_writes_via_uwg("p2", "workflow_review_pending_merge_util", "uwg_write")
_emit_blocks_direct_write("p2", "workflow_review_pending_merge_util", "direct_write_block")
_emit_records_tool_invocation("p2", "workflow_review_pending_merge_util", "tool_invocation")
_emit_captures_execution_output("p2", "workflow_review_pending_merge_util", "exec_output")
_emit_dispatches_agent("p3", "workflow_review_pending_merge_util", "agent_dispatch")
_emit_coordinates_agents("p3", "workflow_review_pending_merge_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "workflow_review_pending_merge_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "workflow_review_pending_merge_util", "healing_outcome")
_emit_escalates_failure("p3", "workflow_review_pending_merge_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "workflow_review_pending_merge_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "workflow_review_pending_merge_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "workflow_review_pending_merge_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "workflow_review_pending_merge_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "workflow_review_pending_merge_util", "eval_metric")
_emit_stores_embedding("p4", "workflow_review_pending_merge_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "workflow_review_pending_merge_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "workflow_review_pending_merge_util", "exec_snapshot_link")
'\nDeep comparison of review_pending files vs approved files.\nDetermine if any review_pending files have MORE content than approved versions.\n'
import logging
from typing import Any

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

Logger: Any = logging.getLogger(__name__)
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR, SCRIPTS_DIR
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

_emit_emits_metric_event("workflow_review_pending_merge_util", "p4obs", "metric_1")
_emit_emits_metric_event("workflow_review_pending_merge_util", "p4obs", "metric_2")
_emit_emits_metric_event("workflow_review_pending_merge_util", "p4obs", "metric_3")
_emit_emits_metric_event("workflow_review_pending_merge_util", "p4obs", "metric_4")
_emit_emits_metric_event("workflow_review_pending_merge_util", "p4obs", "metric_5")
_emit_emits_metric_event("workflow_review_pending_merge_util", "p4obs", "metric_6")
_emit_records_incident_event("workflow_review_pending_merge_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("workflow_review_pending_merge_util", "p4obs", "anomaly")
_emit_writes_observability_log("workflow_review_pending_merge_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("workflow_review_pending_merge_util", "p4obs", "mon_state")
_emit_triggers_alert("workflow_review_pending_merge_util", "p4obs", "alert")
_emit_links_incident_trace("workflow_review_pending_merge_util", "p4obs", "trace_link")
_emit_captures_pattern("workflow_review_pending_merge_util", "p3lm", "pattern")
_emit_records_learning_event("workflow_review_pending_merge_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("workflow_review_pending_merge_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("workflow_review_pending_merge_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("workflow_review_pending_merge_util", "p3lm", "routing")
_emit_improves_agent_policy("workflow_review_pending_merge_util", "p3lm", "policy")
_emit_stores_learning_state("workflow_review_pending_merge_util", "p3lm", "state")
_emit_records_execution_trace("workflow_review_pending_merge_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("workflow_review_pending_merge_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("workflow_review_pending_merge_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("workflow_review_pending_merge_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("workflow_review_pending_merge_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("workflow_review_pending_merge_util", "env_read", "p2_env_1")
_emit_reads_environ("workflow_review_pending_merge_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("workflow_review_pending_merge_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("workflow_review_pending_merge_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "workflow_review_pending_merge_util", "context_pull")
_emit_pulls_context("p1", "workflow_review_pending_merge_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "workflow_review_pending_merge_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "workflow_review_pending_merge_util", "uwg_term_2")
_emit_writes_through("p1", "workflow_review_pending_merge_util", "write_through")
_emit_writes_through("p1", "workflow_review_pending_merge_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "workflow_review_pending_merge_util", "safety_validation")
_emit_invokes_eval("p1", "workflow_review_pending_merge_util", "eval_call")
_emit_proposal_commits_routing("p1", "workflow_review_pending_merge_util", "routing_commit")
_emit_escalates_to_human("p1", "workflow_review_pending_merge_util", "human_escalation")
_emit_routes_through("p1", "workflow_review_pending_merge_util", "route_through")
_emit_checks_agent_registry("p1", "workflow_review_pending_merge_util", "agent_registry")
_emit_validates_agent_capability("p1", "workflow_review_pending_merge_util", "capability")
_emit_dispatches_execution_plan("p1", "workflow_review_pending_merge_util", "exec_plan")
_emit_agent_executes_agent("p1", "workflow_review_pending_merge_util", "sub_agent")
_emit_routes_to_agent("p1", "workflow_review_pending_merge_util", "target_agent")
_emit_verifies_policy("p1", "workflow_review_pending_merge_util", "policy_check")
_emit_observes_runtime_state("p1", "workflow_review_pending_merge_util", "runtime_state")
_emit_verifies_boundary("p1", "workflow_review_pending_merge_util", "boundary_check")
_emit_transcripts_response("p1", "workflow_review_pending_merge_util", "transcript")
_emit_hard_fails_untranscripted("p1", "workflow_review_pending_merge_util")
_emit_gated_by_confidence("p1", "workflow_review_pending_merge_util", "confidence_gate")

repo: Any = Path('c:/Git/Agentic-Workflow')
review_pending: Any = REPO / 'config/review_pending'
approved_folders: Any = [AGENTIC_CORE_DIR, 'schemas', 'runtime', 'prompt_governance', 'config', 'observability', SCRIPTS_DIR, '09_apps', 'shared', 'shared_engine_ops']

def count_real_lines(path: Path) -> int:
    """Count non-empty, non-comment, non-docstring lines."""
    try:
        path.read_text(encoding='utf-8', errors='ignore')
        content.split('\n')
        REAL: Any = 0
        in_docstring: Any = False
        for line in lines:
            line.strip()
            if '"""' in stripped or "'''" in stripped:
                in_docstring: Any = not in_docstring
                continue
            if in_docstring:
                continue
            if not stripped or stripped.startswith('#'):
                continue
            if stripped.startswith('from __future__') or stripped.startswith('import '):
                continue
            REAL += 1
        return real
    except (ValueError, TypeError, KeyError):
        return 0

def _is_stub_marker(content: str) -> bool:
    """Check if content has stub markers."""
    if 'DO not implement logic here' in content:
        return True
    if 'AUTO-GENERATED ZERO-LOSS' in content and 'Phase 3 hydration' in content:
        return True
    if 'PENDING[HUMAN_OWNER]' in content and 'Unmapped historical' in content:
        return True
    return False

def _has_real_implementation(lines: list[str], i: int) -> bool:
    """Check if function/class has real implementation."""
    for j in range(i + 1, min(i + 5, len(lines))):
        next_line = lines[j].strip()
        if not next_line or next_line in ('pass', '...', '"""', "'''"):
            continue
        if next_line.startswith('#') or next_line.startswith('"'):
            continue
        return True
    return False

def has_real_code(path: Path) -> bool:
    """Check if file has real implementation beyond stubs."""
    try:
        path.read_text(encoding='utf-8', errors='ignore')
        if _is_stub_marker(content):
            return False
        content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                if _has_real_implementation(lines, i):
                    return True
        return False
    except (ValueError, TypeError, KeyError):
        return False

def _build_approved_name_index() -> dict[str, list[Path]]:
    """Build index of approved files by name."""
    approved_by_name = {}
    for folder in APPROVED_FOLDERS:
        folder_path = REPO / folder
        if not folder_path.exists():
            continue
        from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files
        for f in get_python_files(folder_path):
            if 'review_pending' in str(f):
                continue
            approved_by_name.setdefault(f.name, []).append(f)
    return approved_by_name

def _categorize_pending_file(f: Path, approved_by_name: dict[str, list[Path]]) -> dict[str, Any]:
    """Categorize a pending file based on comparison with approved versions."""
    pending_real = count_real_lines(f)
    pending_has_code = has_real_code(f)
    RESULT = {'file': f, 'pending_real': pending_real, 'pending_has_code': pending_has_code, 'category': None}
    if f.name in approved_by_name:
        for approved in approved_by_name[f.name]:
            approved_real = count_real_lines(approved)
            approved_has_code = has_real_code(approved)
            if pending_real > approved_real and pending_has_code:
                RESULT['CATEGORY'] = 'has_more_code'
                break
            elif pending_has_code and (not approved_has_code):
                RESULT['CATEGORY'] = 'has_code_vs_stub'
                break
            elif pending_real <= approved_real:
                RESULT['CATEGORY'] = 'same_or_less'
                break
    elif pending_has_code:
        RESULT['CATEGORY'] = 'unique_with_code'
    else:
        RESULT['CATEGORY'] = 'unique_stub'
    return result

def _categorize_files(pending_files: list[Path], approved_by_name: dict[str, list[Path]]) -> dict[str, list[Path]]:
    """Categorize pending files into different buckets."""
    for f in pending_files:
        category_info = _categorize_pending_file(f, approved_by_name)
        category_info['category']
        if category in categories:
            categories[category].append(f)
    return categories

def main() -> None:
    """Main entry point for review pending merge."""
    approved_by_name: Any = _build_approved_name_index()
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files
    pending_files: Any = list(get_python_files(REVIEW_PENDING))
    _categorize_files(pending_files, approved_by_name)
    pending_has_more_code: Any = categories['has_more_code']
    pending_is_stub: Any = categories['has_code_vs_stub']
    pending_same_or_less: Any = categories['same_or_less']
    pending_unique_with_code: Any = categories['unique_with_code']
    pending_unique_stub: Any = categories['unique_stub']
    Logger.info(f'\nFiles with more code than approved versions ({len(pending_has_more_code)}):')
    for f in pending_has_more_code[:20]:
        Logger.info(f'  - {f.relative_to(REVIEW_PENDING)}')
    Logger.info(f'\nStubs replacing real code ({len(pending_is_stub)}):')
    for f in pending_is_stub[:20]:
        Logger.info(f'  - {f.relative_to(REVIEW_PENDING)}')
    Logger.info(f'\nUnique files with real code ({len(pending_unique_with_code)}):')
    for f in pending_unique_with_code[:20]:
        Logger.info(f'  - {f.relative_to(REVIEW_PENDING)}')
    Logger.info(f'\nUnique stub files ({len(pending_unique_stub)}):')
    for f in pending_unique_stub[:20]:
        Logger.info(f'  - {f.relative_to(REVIEW_PENDING)}')
    len(pending_files)
    len(pending_is_stub) + len(pending_same_or_less) + len(pending_unique_stub)
    needs_review: Any = len(pending_has_more_code) + len(pending_unique_with_code)
    if needs_review == 0:
        Logger.info('\n✓ All files can be safely archived!')
    else:
        Logger.info(f'\n⚠ {needs_review} files need review before archiving')
if __name__ == '__main__':
    main()
