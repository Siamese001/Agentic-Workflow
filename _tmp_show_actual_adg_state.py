#!/usr/bin/env python3
"""Show actual ADG state - what metrics exist and their counts."""

import sqlite3
from pathlib import Path
from collections import defaultdict

ADG_PATH = Path("artifacts/adg/adg_indexed_03162026_0702.sqlite")

def main():
    conn = sqlite3.connect(ADG_PATH)
    cursor = conn.cursor()
    
    # Get ALL relation types with counts (using edges_raw table directly)
    print("=" * 100)
    print("COMPLETE RELATION TYPE INVENTORY IN CURRENT ADG")
    print("=" * 100)
    cursor.execute("""
        SELECT r.name, COUNT(*) as cnt
        FROM edges_raw e
        JOIN relation_types r ON e.relation_type = r.id
        GROUP BY r.name
        ORDER BY cnt DESC
    """)
    
    all_relations = cursor.fetchall()
    
    if not all_relations:
        print("\n⚠️  NO RELATION TYPES FOUND - EDGES TABLE MAY BE EMPTY\n")
        cursor.execute("SELECT COUNT(*) FROM edges_raw")
        edge_count = cursor.fetchone()[0]
        print(f"Total edges in database: {edge_count:,}")
        return
    
    # Categorize by P-level
    p0_metrics = {
        'records_execution_trace', 'applies_guardrail', 'reads_policy_state',
        'emits_replay_key', 'emits_determinism_digest', 'signs_execution_trace',
        'snapshots_state'
    }
    
    p1_metrics = {
        'proposal_commits_routing', 'pulls_context', 'execution_terminates_at_uwg',
        'writes_through', 'validated_by_safety_plane', 'invokes_eval',
        'routes_to_agent', 'orchestrates_workflow', 'dispatches_execution_plan',
        'validates_agent_capability', 'checks_agent_registry'
    }
    
    p2_metrics = {
        'authorize_and_execute', 'validates_capability', 'routes_to_capability',
        'writes_via_uwg', 'blocks_direct_write', 'records_tool_invocation',
        'captures_execution_output', 'reads_env', 'reads_runtime_state'
    }
    
    p3_metrics = {
        'dispatches_agent', 'coordinates_agents', 'records_workflow_lineage',
        'invokes_evaluation', 'dispatches_healing_run', 'records_healing_outcome',
        'escalates_failure', 'captures_pattern', 'records_learning_event',
        'writes_learning_snapshot', 'feeds_meta_learning', 'updates_routing_strategy',
        'improves_agent_policy', 'stores_learning_state'
    }
    
    p4_metrics = {
        'records_telemetry_event', 'captures_evaluation_metric', 'stores_embedding',
        'updates_meta_learning_state', 'links_execution_to_snapshot',
        'emits_metric_event', 'records_incident_event', 'captures_runtime_anomaly',
        'writes_observability_log', 'updates_monitoring_state', 'triggers_alert',
        'links_incident_trace'
    }
    
    categorized = defaultdict(list)
    other = []
    
    for name, count in all_relations:
        if name in p0_metrics:
            categorized['P0'].append((name, count))
        elif name in p1_metrics:
            categorized['P1'].append((name, count))
        elif name in p2_metrics:
            categorized['P2'].append((name, count))
        elif name in p3_metrics:
            categorized['P3'].append((name, count))
        elif name in p4_metrics:
            categorized['P4'].append((name, count))
        else:
            other.append((name, count))
    
    # Print by category
    for level in ['P0', 'P1', 'P2', 'P3', 'P4']:
        print(f"\n{'='*100}")
        print(f"{level} RUNTIME METRICS")
        print('='*100)
        if categorized[level]:
            for name, count in sorted(categorized[level], key=lambda x: -x[1]):
                print(f"  {name:50s} {count:>10,}")
        else:
            print(f"  ❌ NO {level} METRICS FOUND IN CURRENT ADG")
    
    # Print other relation types
    print(f"\n{'='*100}")
    print("OTHER RELATION TYPES (Non-P0-P4)")
    print('='*100)
    for name, count in sorted(other, key=lambda x: -x[1])[:30]:
        print(f"  {name:50s} {count:>10,}")
    
    if len(other) > 30:
        print(f"\n  ... and {len(other) - 30} more relation types")
    
    # Summary
    cursor.execute("SELECT COUNT(*) FROM edges_raw")
    total_edges = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM nodes")
    total_nodes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT name) FROM relation_types")
    total_relation_types = cursor.fetchone()[0]
    
    print(f"\n{'='*100}")
    print("SUMMARY")
    print('='*100)
    print(f"  Total edges:          {total_edges:>10,}")
    print(f"  Total nodes:          {total_nodes:>10,}")
    print(f"  Relation types:       {total_relation_types:>10,}")
    print(f"  P0 metrics found:     {len(categorized['P0']):>10,} / 7 expected")
    print(f"  P1 metrics found:     {len(categorized['P1']):>10,} / 11 expected")
    print(f"  P2 metrics found:     {len(categorized['P2']):>10,} / 9 expected")
    print(f"  P3 metrics found:     {len(categorized['P3']):>10,} / 14 expected")
    print(f"  P4 metrics found:     {len(categorized['P4']):>10,} / 12 expected")
    print('='*100)
    
    conn.close()

if __name__ == "__main__":
    main()
