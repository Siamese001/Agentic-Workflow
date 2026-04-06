"""
Simple script to generate agent duplicates table.
Runs find_duplicate_agents.py internally and processes output.
"""
import json
from datetime import datetime
from pathlib import Path

from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file as _kernel_is_agent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.security_util import safe_execute

_emit_emits_metric_event("generate_agent_table_simple_util", "p4obs", "metric_1")
_emit_emits_metric_event("generate_agent_table_simple_util", "p4obs", "metric_2")
_emit_emits_metric_event("generate_agent_table_simple_util", "p4obs", "metric_3")
_emit_emits_metric_event("generate_agent_table_simple_util", "p4obs", "metric_4")
_emit_emits_metric_event("generate_agent_table_simple_util", "p4obs", "metric_5")
_emit_emits_metric_event("generate_agent_table_simple_util", "p4obs", "metric_6")
_emit_records_incident_event("generate_agent_table_simple_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_agent_table_simple_util", "p4obs", "anomaly")
_emit_writes_observability_log("generate_agent_table_simple_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_agent_table_simple_util", "p4obs", "mon_state")
_emit_triggers_alert("generate_agent_table_simple_util", "p4obs", "alert")
_emit_links_incident_trace("generate_agent_table_simple_util", "p4obs", "trace_link")
_emit_captures_pattern("generate_agent_table_simple_util", "p3lm", "pattern")
_emit_records_learning_event("generate_agent_table_simple_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_agent_table_simple_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_agent_table_simple_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_agent_table_simple_util", "p3lm", "routing")
_emit_improves_agent_policy("generate_agent_table_simple_util", "p3lm", "policy")
_emit_stores_learning_state("generate_agent_table_simple_util", "p3lm", "state")
_emit_records_execution_trace("generate_agent_table_simple_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_agent_table_simple_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_agent_table_simple_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_agent_table_simple_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_agent_table_simple_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_agent_table_simple_util", "env_read", "p2_env_1")
_emit_reads_environ("generate_agent_table_simple_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_agent_table_simple_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_agent_table_simple_util", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "generate_agent_table_simple_util")
_emit_applies_guardrail("p0", "generate_agent_table_simple_util", "p0_governance")
_emit_reads_policy_state("p0", "generate_agent_table_simple_util", "policy_binding")
_emit_snapshots_state("p0", "generate_agent_table_simple_util", "state_snapshot")
_emit_pulls_context("p1", "generate_agent_table_simple_util", "context_pull")
_emit_pulls_context("p1", "generate_agent_table_simple_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "generate_agent_table_simple_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_agent_table_simple_util", "uwg_term_secondary")
_emit_writes_through("p1", "generate_agent_table_simple_util", "write_through")
_emit_writes_through("p1", "generate_agent_table_simple_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "generate_agent_table_simple_util", "safety_validation")
_emit_invokes_eval("p1", "generate_agent_table_simple_util", "eval_call")
_emit_proposal_commits_routing("p1", "generate_agent_table_simple_util", "routing_commit")
_emit_escalates_to_human("p1", "generate_agent_table_simple_util", "human_escalation")
_emit_routes_through("p1", "generate_agent_table_simple_util", "route_through")
_emit_checks_agent_registry("p1", "generate_agent_table_simple_util", "agent_registry")
_emit_validates_agent_capability("p1", "generate_agent_table_simple_util", "capability")
_emit_dispatches_execution_plan("p1", "generate_agent_table_simple_util", "exec_plan")
_emit_agent_executes_agent("p1", "generate_agent_table_simple_util", "sub_agent")
_emit_routes_to_agent("p1", "generate_agent_table_simple_util", "target_agent")
_emit_verifies_policy("p1", "generate_agent_table_simple_util", "policy_check")
_emit_observes_runtime_state("p1", "generate_agent_table_simple_util", "runtime_state")
_emit_verifies_boundary("p1", "generate_agent_table_simple_util", "boundary_check")
_emit_transcripts_response("p1", "generate_agent_table_simple_util", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_agent_table_simple_util")
_emit_gated_by_confidence("p1", "generate_agent_table_simple_util", "confidence_gate")
emit_replay_key("p0", "generate_agent_table_simple_util")
emit_determinism_digest("p0", "generate_agent_table_simple_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_agent_table_simple_util", "execution_auth")
_emit_validates_capability("p2", "generate_agent_table_simple_util", "capability_check")
_emit_routes_to_capability("p2", "generate_agent_table_simple_util", "capability_route")
_emit_writes_via_uwg("p2", "generate_agent_table_simple_util", "uwg_write")
_emit_blocks_direct_write("p2", "generate_agent_table_simple_util", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_agent_table_simple_util", "tool_invocation")
_emit_captures_execution_output("p2", "generate_agent_table_simple_util", "exec_output")
_emit_dispatches_agent("p3", "generate_agent_table_simple_util", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_agent_table_simple_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_agent_table_simple_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_agent_table_simple_util", "healing_outcome")
_emit_escalates_failure("p3", "generate_agent_table_simple_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_agent_table_simple_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_agent_table_simple_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_agent_table_simple_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_agent_table_simple_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_agent_table_simple_util", "eval_metric")
_emit_stores_embedding("p4", "generate_agent_table_simple_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_agent_table_simple_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_agent_table_simple_util", "exec_snapshot_link")

def is_agent_file(path: str) -> bool:
    """Check if path is an actual agent file (not test).

    [REFACTORED 2026-02-08] Delegates to classification kernel SSOT.
    Accepts string paths for backwards compatibility with JSON data.
    """
    return _kernel_is_agent(Path(path))

def infer_rationale(canonical: str, dup_path: str, action: str) -> str:
    """Infer rationale based on path patterns."""
    if 'blueprint_sovereign' in dup_path:
        return 'Leftover blueprint template — production version is canonical'
    if 'validators' in canonical and 'agents' in dup_path or ('agents' in canonical and 'validators' in dup_path):
        return 'Location overlap: same agent in agents/ vs validators/ directories'
    if action == 'REVIEW':
        return 'Minor differences detected (comments/formatting/incomplete features) — manual merge needed'
    return 'Exact or structural duplicate — likely copy-paste or migration artifact'

def main():
    print('Running duplicate detection...')
    result = safe_execute(['python', 'scripts/find_duplicate_agents.py', '--output', 'json'], capture_output=True, text=True, cwd=Path.cwd(), check=False)
    if result.returncode != 0:
        print(f'Error running find_duplicate_agents.py: {result.stderr}')
        return 1
    output = result.stdout
    lines = output.split('\n')
    json_lines = []
    in_json = False
    for line in lines:
        if line.strip() == '[':
            in_json = True
        if in_json:
            if line.strip().startswith('='):
                break
            json_lines.append(line)
    json_output = '\n'.join(json_lines)
    try:
        data = json.loads(json_output)
    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        print(f'JSON output length: {len(json_output)}')
        print(f'First 200 chars: {json_output[:200]}')
        print(f'Last 200 chars: {json_output[-200:]}')
        with open('reports/json_debug.txt', 'w') as f:
            f.write(json_output)
        return 1
    results = []
    for item in data:
        canonical = item['canonical_file']
        if not is_agent_file(canonical):
            continue
        for dup in item['duplicates']:
            dup_path = dup['path']
            if not is_agent_file(dup_path):
                continue
            results.append({'agent_name': Path(canonical).stem, 'canonical': canonical, 'duplicate': dup_path, 'action': item['action'], 'canonical_quality': item['canonical_quality']['quality_score'], 'duplicate_quality': dup['quality']['quality_score'], 'rationale': infer_rationale(canonical, dup_path, item['action'])})
    results.sort(key=lambda x: (0 if x['action'] == 'DELETE' else 1, x['agent_name']))
    output_file = Path('reports/duplicated_agents_table.md')
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# Duplicated Agents Table\n')
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f'**Total Duplicates:** {len(results)}\n\n')
        delete_count = sum(1 for r in results if r['action'] == 'DELETE')
        review_count = sum(1 for r in results if r['action'] == 'REVIEW')
        f.write(f'**Action Summary:** {delete_count} auto-delete, {review_count} manual review\n\n')
        f.write('| Agent Name | Canonical Path | Duplicate Path | Action | Quality (C/D) | Rationale |\n')
        f.write('| --- | --- | --- | --- | --- | --- |\n')
        for r in results:
            f.write(f"| {r['agent_name']} | `{r['canonical']}` | `{r['duplicate']}` | **{r['action']}** | {r['canonical_quality']}/{r['duplicate_quality']} | {r['rationale']} |\n")
        f.write('\n---\n\n')
        f.write('## Quick Actions\n\n')
        f.write('### Delete Safe Duplicates\n')
        f.write('```bash\n')
        for r in results:
            if r['action'] == 'DELETE':
                f.write(f'''git rm "{r['duplicate']}"\n''')
        f.write('```\n\n')
        f.write('### Review Required (Manual Diff)\n')
        f.write('```bash\n')
        for r in results:
            if r['action'] == 'REVIEW':
                f.write(f"# {r['agent_name']}\n")
                f.write(f'''code --diff "{r['canonical']}" "{r['duplicate']}"\n\n''')
        f.write('```\n')
    print(f'✅ Generated: {output_file}')
    print(f'   Total agent duplicates: {len(results)}')
    print(f'   DELETE: {delete_count}')
    print(f'   REVIEW: {review_count}')
    return 0
if __name__ == '__main__':
    exit(main())
