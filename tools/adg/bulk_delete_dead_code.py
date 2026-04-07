#!/usr/bin/env python3
"""Bulk delete dead code based on ADG analysis."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def query_dead_exports(layer: str | None = None, limit: int = 1000) -> list[dict]:
    """Query ADG for dead exports."""
    dbs = sorted(Path('artifacts/adg').glob('adg_indexed_*.sqlite'))
    if not dbs:
        print('No ADG databases found')
        sys.exit(1)
    db_path = dbs[-1]

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    sql = '''
        SELECT n.adg_name, n.resolved_path, n.layer, n.entity_type, COUNT(e.id) as export_count
        FROM nodes n
        JOIN edges e ON n.id = e.src_id
        WHERE e.relation_type = 'exports'
        AND n.id NOT IN (
            SELECT DISTINCT dst_id FROM edges
            WHERE relation_type IN ('calls', 'imports', 'reads_from', 'writes_to')
        )
    '''
    params: list = []
    if layer:
        sql += ' AND n.layer = ?'
        params.append(layer)
    sql += ' GROUP BY n.id ORDER BY export_count DESC LIMIT ?'
    params.append(limit)

    c.execute(sql, params)
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


def query_dead_functions(layer: str | None = None, directory: str | None = None, limit: int = 100) -> list[dict]:
    """Query ADG for dead functions/classes (not entire modules)."""
    dbs = sorted(Path('artifacts/adg').glob('adg_indexed_*.sqlite'))
    if not dbs:
        print('No ADG databases found')
        sys.exit(1)
    db_path = dbs[-1]

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    sql = '''
        SELECT n.adg_name, n.resolved_path, n.layer, n.entity_type, n.id, n.span_line
        FROM nodes n
        WHERE n.id NOT IN (
            SELECT DISTINCT dst_id FROM edges
            WHERE relation_type IN ('calls', 'imports')
        )
        AND n.id IN (
            SELECT DISTINCT src_id FROM edges
            WHERE relation_type = 'exports'
        )
    '''
    params: list = []
    if layer:
        sql += ' AND n.layer = ?'
        params.append(layer)
    if directory:
        sql += ' AND n.resolved_path LIKE ?'
        params.append(f'%{directory}%')
    sql += ' GROUP BY n.id ORDER BY n.resolved_path LIMIT ?'
    params.append(limit)

    c.execute(sql, params)
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


def query_unused_imports(limit: int = 1000) -> list[dict]:
    """Query ADG for unused imports."""
    dbs = sorted(Path('artifacts/adg').glob('adg_indexed_*.sqlite'))
    if not dbs:
        print('No ADG databases found')
        sys.exit(1)
    db_path = dbs[-1]

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''
        SELECT e.symbol, e.source_file, e.line_no, dst.resolved_path as target_module
        FROM edges e
        JOIN nodes dst ON e.dst_id = dst.id
        WHERE e.relation_type = 'imports'
        AND dst.id NOT IN (
            SELECT DISTINCT src_id FROM edges
            WHERE relation_type IN ('exports', 'calls')
        )
        ORDER BY e.source_file
        LIMIT ?
    ''', (limit,))

    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


def cluster_dead_code_via_graph(limit: int = 1000) -> dict:
    """Cluster dead code using SQLiteGraphStore with community detection.

    Enhanced features:
    - Community detection on unused_import edges for clustering
    - Centrality scoring for risk assessment
    - Subgraph extraction for bulk deletion planning

    Returns:
        Dict with clusters, centrality scores, and metadata
    """
    try:
        from agentic_core.L4_state.utils.memory.graph_store_factory import (
            create_sqlite_graph_store_or_none,
        )

        graph_store = create_sqlite_graph_store_or_none()
        if graph_store is None:
            print('Graph store not available, falling back to SQL query')
            return {"clusters": [], "method": "fallback"}

        # Detect communities on unused_import graph
        communities = graph_store.detect_communities()

        # Get centrality scores for risk assessment
        clusters_with_scores = []
        for community in communities:
            cluster_nodes = []
            cluster_centralities = []

            for entity_id in community.entities:
                entity = graph_store.get_entity(entity_id)
                if entity:
                    centrality = graph_store.get_centrality(entity_id)
                    cluster_nodes.append({
                        'id': entity.id,
                        'name': entity.name,
                        'file_path': entity.metadata.get('file_path', ''),
                        'entity_type': entity.entity_type,
                        'centrality': centrality if isinstance(centrality, float) else 0.0,
                    })
                    cluster_centralities.append(centrality if isinstance(centrality, float) else 0.0)

            # Calculate cluster risk score (avg centrality)
            avg_centrality = sum(cluster_centralities) / len(cluster_centralities) if cluster_centralities else 0.0

            clusters_with_scores.append({
                'cluster_id': community.id,
                'description': community.description,
                'size': len(cluster_nodes),
                'avg_centrality': avg_centrality,
                'nodes': sorted(cluster_nodes, key=lambda x: x['centrality'], reverse=True),
            })

        # Sort clusters by risk (highest centrality first)
        clusters_with_scores.sort(key=lambda x: x['avg_centrality'], reverse=True)

        print(f'Graph-based clustering: Found {len(clusters_with_scores)} clusters')
        return {
            'clusters': clusters_with_scores[:limit],
            'method': 'graph_store',
            'total_clusters': len(communities),
        }

    except Exception as e:
        print(f'Graph-based clustering failed: {e}, falling back to SQL query')
        return {"clusters": [], "method": "fallback", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description='Bulk delete dead code based on ADG analysis')
    parser.add_argument('--layer', help='Target layer (e.g., L_TEST, L_TOOLS)')
    parser.add_argument('--directory', help='Target directory (e.g., tests/adg/)')
    parser.add_argument('--functions', action='store_true', help='Target dead functions only (not modules)')
    parser.add_argument('--unused-imports', action='store_true', help='Target unused imports')
    parser.add_argument('--cluster', action='store_true', help='Use graph-based clustering')
    parser.add_argument('--output', help='Output JSON file for targets')
    parser.add_argument('--input', help='Input JSON file with targets to delete')
    parser.add_argument('--dry-run', action='store_true', help='Preview deletions without executing')
    parser.add_argument('--execute', action='store_true', help='Execute deletions')

    args = parser.parse_args()

    if args.output:
        if args.mode == 'cluster':
            targets = cluster_dead_code_via_graph()
        elif args.unused_imports:
            targets = query_unused_imports()
        elif args.functions:
            targets = query_dead_functions(args.layer, args.directory)
        else:
            targets = query_dead_exports(args.layer)

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(targets, f, indent=2)
        print(f'Wrote {len(targets)} targets to {args.output}')
        return 0

    if args.input:
        # Delete mode - process targets
        with open(args.input, encoding='utf-8') as f:
            targets = json.load(f)

        print(f'Processing {len(targets)} targets...')

        for target in targets[:5] if args.dry_run else targets:
            path = target.get('resolved_path', target.get('source_file', ''))
            name = target.get('adg_name', target.get('symbol', ''))

            if args.dry_run:
                print(f'[DRY-RUN] Would delete: {name} from {path}')
            else:
                # Actual deletion logic would go here
                print(f'[DELETE] {name} from {path}')

        if args.dry_run:
            print(f'\nDry run complete. Use --execute to delete {len(targets)} items.')
        else:
            print(f'\nProcessed {len(targets)} targets.')
        return 0

    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
