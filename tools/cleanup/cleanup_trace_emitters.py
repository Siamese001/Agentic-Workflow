#!/usr/bin/env python3
"""
Trace Emitter Cleanup Tool

Removes repetitive lifecycle trace emitters from Python files while preserving:
- Unique/semantic emitters with meaningful context
- Emitters inside functions (not module-level spam)
- Import statements for the lifecycle_trace_contract

Usage:
    python tools/cleanup_trace_emitters.py --file <path> [--dry-run]
    python tools/cleanup_trace_emitters.py --layer L0_routing [--batch-size 50]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# Patterns to remove (repetitive module-level emitters)
REPETITIVE_PATTERNS = [
    # _emit_reads_through with sequential numbering: _emit_reads_through("l4", "filename", "urg_read_NNN")
    (r'^_emit_reads_through\([^)]+,\s*"[^"]+",\s*"urg_read_\d+"\)\s*\n', ''),
    # Sequential emitters with just different IDs but same semantic meaning
    (r'^_emit_emits_metric_event\("[^"]+",\s*"[^"]+",\s*"metric_\d+"\)\s*\n', ''),
    (r'^_emit_records_execution_trace\("[^"]+",\s*"[^"]+",\s*"p\d+_trace_\d+"\)\s*\n', ''),
    (r'^_emit_reads_environ\("[^"]+",\s*"[^"]+",\s*"p\d+_env_\d+"\)\s*\n', ''),
    (r'^_emit_reads_runtime_state\("[^"]+",\s*"[^"]+",\s*"p\d+_rt_\d+"\)\s*\n', ''),
    # P0-P4 lifecycle emitters with generic IDs
    (r'^_emit_applies_guardrail\("[^"]+",\s*"[^"]+",\s*"p\d+_governance"\)\s*\n', ''),
    (r'^_emit_snapshots_state\("[^"]+",\s*"[^"]+",\s*"state_snapshot"\)\s*\n', ''),
    (r'^_emit_signs_execution_trace\([^)]+\)\s*\n', ''),
    (r'^_emit_pulls_context\("p\d+",\s*"[^"]+",\s*"context_pull(_\w+)?"\)\s*\n', ''),
    (r'^_emit_execution_terminates_at_uwg\("p\d+",\s*"[^"]+",\s*"uwg_term(_\w+)?"\)\s*\n', ''),
    (r'^_emit_writes_through\("p\d+",\s*"[^"]+",\s*"write_through(_\w+)?"\)\s*\n', ''),
    (r'^_emit_validated_by_safety_plane\("p\d+",\s*"[^"]+",\s*"safety_validation"\)\s*\n', ''),
    (r'^_emit_invokes_eval\("p\d+",\s*"[^"]+",\s*"eval_call"\)\s*\n', ''),
    (r'^_emit_proposal_commits_routing\("p\d+",\s*"[^"]+",\s*"routing_commit"\)\s*\n', ''),
    (r'^_emit_authorize_and_execute\("p\d+",\s*"[^"]+",\s*"execution_auth"\)\s*\n', ''),
    (r'^_emit_validates_capability\("p\d+",\s*"[^"]+",\s*"capability_check"\)\s*\n', ''),
    (r'^_emit_routes_to_capability\("p\d+",\s*"[^"]+",\s*"capability_route"\)\s*\n', ''),
    (r'^_emit_writes_via_uwg\("p\d+",\s*"[^"]+",\s*"uwg_write"\)\s*\n', ''),
    (r'^_emit_blocks_direct_write\("p\d+",\s*"[^"]+",\s*"direct_write_block"\)\s*\n', ''),
    (r'^_emit_records_tool_invocation\("p\d+",\s*"[^"]+",\s*"tool_invocation"\)\s*\n', ''),
    (r'^_emit_captures_execution_output\("p\d+",\s*"[^"]+",\s*"exec_output"\)\s*\n', ''),
    (r'^_emit_dispatches_agent\("p\d+",\s*"[^"]+",\s*"agent_dispatch"\)\s*\n', ''),
    (r'^_emit_coordinates_agents\("p\d+",\s*"[^"]+",\s*"agent_coordination"\)\s*\n', ''),
    (r'^_emit_records_workflow_lineage\("p\d+",\s*"[^"]+",\s*"workflow_lineage"\)\s*\n', ''),
    (r'^_emit_records_healing_outcome\("p\d+",\s*"[^"]+",\s*"healing_outcome"\)\s*\n', ''),
    (r'^_emit_escalates_failure\("p\d+",\s*"[^"]+",\s*"failure_escalation"\)\s*\n', ''),
    (r'^_emit_orchestrates_workflow\("p\d+",\s*"[^"]+",\s*"workflow_orchestration"\)\s*\n', ''),
    (r'^_emit_dispatches_healing_run\("p\d+",\s*"[^"]+",\s*"(healing_dispatch|L\d+)"\)\s*\n', ''),
    (r'^_emit_invokes_evaluation\("p\d+",\s*"[^"]+",\s*"evaluation_signal"\)\s*\n', ''),
    (r'^_emit_records_telemetry_event\("p\d+",\s*"[^"]+",\s*"telemetry_event"\)\s*\n', ''),
    (r'^_emit_captures_evaluation_metric\("p\d+",\s*"[^"]+",\s*"eval_metric"\)\s*\n', ''),
    (r'^_emit_stores_embedding\("p\d+",\s*"[^"]+",\s*"embedding_store"\)\s*\n', ''),
    (r'^_emit_updates_meta_learning_state\("p\d+",\s*"[^"]+",\s*"meta_learning"\)\s*\n', ''),
    (r'^_emit_links_execution_to_snapshot\("p\d+",\s*"[^"]+",\s*"exec_snapshot_link"\)\s*\n', ''),
    (r'^_emit_records_incident_event\("[^"]+",\s*"[^"]+",\s*"incident"\)\s*\n', ''),
    (r'^_emit_captures_runtime_anomaly\("[^"]+",\s*"[^"]+",\s*"anomaly"\)\s*\n', ''),
    (r'^_emit_writes_observability_log\("[^"]+",\s*"[^"]+",\s*"obs_log"\)\s*\n', ''),
    (r'^_emit_updates_monitoring_state\("[^"]+",\s*"[^"]+",\s*"mon_state"\)\s*\n', ''),
    (r'^_emit_triggers_alert\("[^"]+",\s*"[^"]+",\s*"alert"\)\s*\n', ''),
    (r'^_emit_links_incident_trace\("[^"]+",\s*"[^"]+",\s*"trace_link"\)\s*\n', ''),
    (r'^_emit_captures_pattern\("[^"]+",\s*"[^"]+",\s*"pattern"\)\s*\n', ''),
    (r'^_emit_records_learning_event\("[^"]+",\s*"[^"]+",\s*"learning_event"\)\s*\n', ''),
    (r'^_emit_writes_learning_snapshot\("[^"]+",\s*"[^"]+",\s*"snapshot"\)\s*\n', ''),
    (r'^_emit_feeds_meta_learning\("[^"]+",\s*"[^"]+",\s*"meta_feed"\)\s*\n', ''),
    (r'^_emit_updates_routing_strategy\("[^"]+",\s*"[^"]+",\s*"routing"\)\s*\n', ''),
    (r'^_emit_improves_agent_policy\("[^"]+",\s*"[^"]+",\s*"policy"\)\s*\n', ''),
    (r'^_emit_stores_learning_state\("[^"]+",\s*"[^"]+",\s*"state"\)\s*\n', ''),
    # P1 governance emitters
    (r'^_emit_reads_policy_state\("p\d+",\s*"[^"]+",\s*"L\d+"\)\s*\n', ''),
    (r'^_emit_escalates_to_human\("p\d+",\s*"[^"]+",\s*"L\d+"\)\s*\n', ''),
    (r'^_emit_routes_through\("p\d+",\s*"[^"]+",\s*"L\d+"\)\s*\n', ''),
    (r'^_emit_checks_agent_registry\("p\d+",\s*"[^"]+",\s*"agent_registry"\)\s*\n', ''),
    (r'^_emit_validates_agent_capability\("p\d+",\s*"[^"]+",\s*"capability"\)\s*\n', ''),
    (r'^_emit_dispatches_execution_plan\("p\d+",\s*"[^"]+",\s*"exec_plan"\)\s*\n', ''),
    (r'^_emit_agent_executes_agent\("p\d+",\s*"[^"]+",\s*"sub_agent"\)\s*\n', ''),
    (r'^_emit_routes_to_agent\("p\d+",\s*"[^"]+",\s*"target_agent"\)\s*\n', ''),
    (r'^_emit_verifies_policy\("p\d+",\s*"[^"]+",\s*"policy_check"\)\s*\n', ''),
    (r'^_emit_observes_runtime_state\("p\d+",\s*"[^"]+",\s*"runtime_state"\)\s*\n', ''),
    (r'^_emit_verifies_boundary\("p\d+",\s*"[^"]+",\s*"boundary_check"\)\s*\n', ''),
    (r'^_emit_transcripts_response\("p\d+",\s*"[^"]+",\s*"transcript"\)\s*\n', ''),
    (r'^_emit_hard_fails_untranscripted\("p\d+",\s*"[^"]+"\)\s*\n', ''),
    (r'^_emit_gated_by_confidence\("p\d+",\s*"[^"]+",\s*"confidence_gate"\)\s*\n', ''),
    (r'^_emit_escalates_to_human\("p\d+",\s*"[^"]+",\s*"[^"]+"\)\s*\n', ''),
    # P0 emitters with generic IDs
    (r'^emit_replay_key\("p\d+",\s*"[^"]+"\)\s*\n', ''),
    (r'^emit_determinism_digest\("p\d+",\s*"[^"]+"\)\s*\n', ''),
]

def count_emitters(content: str) -> int:
    """Count total _emit_* calls in content."""
    return len(re.findall(r'^_emit_\w+\(', content, re.MULTILINE))

def cleanup_file(filepath: Path, dry_run: bool = False) -> dict:
    """Clean up trace emitters in a single file."""
    original_content = filepath.read_text(encoding='utf-8')
    original_count = count_emitters(original_content)

    modified_content = original_content
    removed_count = 0

    for pattern, replacement in REPETITIVE_PATTERNS:
        matches = len(re.findall(pattern, modified_content, re.MULTILINE))
        removed_count += matches
        modified_content = re.sub(pattern, replacement, modified_content, flags=re.MULTILINE)

    # Clean up excess blank lines (more than 2 consecutive)
    modified_content = re.sub(r'\n{4,}', '\n\n\n', modified_content)

    new_count = count_emitters(modified_content)

    result = {
        'file': str(filepath),
        'original_count': original_count,
        'removed_count': removed_count,
        'new_count': new_count,
        'changed': original_content != modified_content,
    }

    if not dry_run and result['changed']:
        filepath.write_text(modified_content, encoding='utf-8')

    return result

def cleanup_layer(layer_path: Path, batch_size: Optional[int] = None, dry_run: bool = False) -> list:
    """Clean up all Python files in a layer."""
    results = []
    files = list(layer_path.rglob('*.py'))

    for i, filepath in enumerate(files):
        if batch_size and i >= batch_size:
            break
        try:
            result = cleanup_file(filepath, dry_run)
            if result['changed'] or result['original_count'] > 0:
                results.append(result)
        except Exception as e:  # guardian: allow-broad-exception -- teardown/cleanup context -- swallow is conventional in resource-release paths
            results.append({
                'file': str(filepath),
                'error': str(e),
            })

    return results

def main():
    parser = argparse.ArgumentParser(description='Cleanup trace emitters')
    parser.add_argument('--file', help='Single file to clean')
    parser.add_argument('--layer', help='Layer directory to clean (e.g., L0_routing)')
    parser.add_argument('--batch-size', type=int, help='Limit number of files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--output', help='JSON output file for results')

    args = parser.parse_args()

    if args.file:
        filepath = Path(args.file)
        result = cleanup_file(filepath, args.dry_run)
        print(json.dumps(result, indent=2))
    elif args.layer:
        layer_path = Path('agentic_core') / args.layer
        if not layer_path.exists():
            print(f"Layer not found: {layer_path}", file=sys.stderr)
            sys.exit(1)

        results = cleanup_layer(layer_path, args.batch_size, args.dry_run)

        total_original = sum(r.get('original_count', 0) for r in results)
        total_removed = sum(r.get('removed_count', 0) for r in results)
        total_new = sum(r.get('new_count', 0) for r in results)

        summary = {
            'files_processed': len(results),
            'total_original': total_original,
            'total_removed': total_removed,
            'total_new': total_new,
            'results': results,
        }

        if args.output:
            Path(args.output).write_text(json.dumps(summary, indent=2), encoding='utf-8')

        print(json.dumps(summary, indent=2))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
