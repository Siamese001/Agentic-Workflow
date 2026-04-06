#!/usr/bin/env python3
"""Query ADG SQLite database directly for dead code analysis."""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any


def query_adg_for_dead_code(db_path: str, target_dir: str) -> Dict[str, Any]:
    """Query ADG SQLite database for dead code signals in target directory."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = {
        'target_dir': target_dir,
        'dead_imports': [],
        'unused_imports': [],
        'unreachable_code': [],
        'duplicate_methods': [],
        'orphans': []
    }

    # Query for nodes in target directory
    cursor.execute("""
        SELECT id, adg_name, resolved_path
        FROM nodes
        WHERE resolved_path LIKE ?
    """, (f"%{target_dir}%",))

    nodes = cursor.fetchall()
    print(f"Found {len(nodes)} nodes in {target_dir}")

    # Query for dead imports (antipattern relation)
    cursor.execute("""
        SELECT src_id, dst_id, relation_type
        FROM edges
        WHERE relation_type = 'dead_imports'
    """)

    dead_import_edges = cursor.fetchall()
    print(f"Found {len(dead_import_edges)} dead_import edges")

    # Get file paths for nodes with dead imports
    node_ids_with_dead_imports = set(edge[0] for edge in dead_import_edges)

    if node_ids_with_dead_imports:
        cursor.execute("""
            SELECT id, resolved_path, adg_name
            FROM nodes
            WHERE id IN ({})
        """.format(','.join('?' for _ in node_ids_with_dead_imports)), list(node_ids_with_dead_imports))

        nodes_with_dead_imports = cursor.fetchall()

        for node_id, resolved_path, adg_name in nodes_with_dead_imports:
            if resolved_path and target_dir in resolved_path:
                results['dead_imports'].append({
                    'node_id': node_id,
                    'file_path': resolved_path,
                    'name': adg_name
                })

    # Query for unused imports
    cursor.execute("""
        SELECT src_id, dst_id, relation_type
        FROM edges
        WHERE relation_type = 'unused_import'
    """)

    unused_import_edges = cursor.fetchall()
    print(f"Found {len(unused_import_edges)} unused_import edges")

    node_ids_with_unused_imports = set(edge[0] for edge in unused_import_edges)

    if node_ids_with_unused_imports:
        cursor.execute("""
            SELECT id, resolved_path, adg_name
            FROM nodes
            WHERE id IN ({})
        """.format(','.join('?' for _ in node_ids_with_unused_imports)), list(node_ids_with_unused_imports))

        nodes_with_unused_imports = cursor.fetchall()

        for node_id, resolved_path, adg_name in nodes_with_unused_imports:
            if resolved_path and target_dir in resolved_path:
                results['unused_imports'].append({
                    'node_id': node_id,
                    'file_path': resolved_path,
                    'name': adg_name
                })

    # Query for unreachable code
    cursor.execute("""
        SELECT src_id, dst_id, relation_type
        FROM edges
        WHERE relation_type = 'unreachable_after_raise'
    """)

    unreachable_edges = cursor.fetchall()
    print(f"Found {len(unreachable_edges)} unreachable_after_raise edges")

    node_ids_unreachable = set(edge[0] for edge in unreachable_edges)

    if node_ids_unreachable:
        cursor.execute("""
            SELECT id, resolved_path, adg_name
            FROM nodes
            WHERE id IN ({})
        """.format(','.join('?' for _ in node_ids_unreachable)), list(node_ids_unreachable))

        nodes_unreachable = cursor.fetchall()

        for node_id, resolved_path, adg_name in nodes_unreachable:
            if resolved_path and target_dir in resolved_path:
                results['unreachable_code'].append({
                    'node_id': node_id,
                    'file_path': resolved_path,
                    'name': adg_name
                })

    # Query for duplicate methods
    cursor.execute("""
        SELECT src_id, dst_id, relation_type
        FROM edges
        WHERE relation_type = 'duplicate_method'
    """)

    duplicate_edges = cursor.fetchall()
    print(f"Found {len(duplicate_edges)} duplicate_method edges")

    node_ids_duplicates = set(edge[0] for edge in duplicate_edges)

    if node_ids_duplicates:
        cursor.execute("""
            SELECT id, resolved_path, adg_name
            FROM nodes
            WHERE id IN ({})
        """.format(','.join('?' for _ in node_ids_duplicates)), list(node_ids_duplicates))

        nodes_duplicates = cursor.fetchall()

        for node_id, resolved_path, adg_name in nodes_duplicates:
            if resolved_path and target_dir in resolved_path:
                results['duplicate_methods'].append({
                    'node_id': node_id,
                    'file_path': resolved_path,
                    'name': adg_name
                })

    conn.close()

    return results


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python adg_direct_query.py <adg_db_path> <target_dir> [output_file]")
        sys.exit(1)

    db_path = sys.argv[1]
    target_dir = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Querying ADG database: {db_path}")
    print(f"Target directory: {target_dir}")
    print("=" * 70)

    results = query_adg_for_dead_code(db_path, target_dir)

    print(f"\nDead Code Analysis for {target_dir}:")
    print(f"  Dead imports: {len(results['dead_imports'])}")
    print(f"  Unused imports: {len(results['unused_imports'])}")
    print(f"  Unreachable code: {len(results['unreachable_code'])}")
    print(f"  Duplicate methods: {len(results['duplicate_methods'])}")

    if results['dead_imports']:
        print(f"\nDead Imports ({len(results['dead_imports'])}):")
        for item in results['dead_imports'][:10]:  # Show first 10
            print(f"  {item['file_path']}: {item['name']}")
        if len(results['dead_imports']) > 10:
            print(f"  ... and {len(results['dead_imports']) - 10} more")

    if results['unused_imports']:
        print(f"\nUnused Imports ({len(results['unused_imports'])}):")
        for item in results['unused_imports'][:10]:
            print(f"  {item['file_path']}: {item['name']}")
        if len(results['unused_imports']) > 10:
            print(f"  ... and {len(results['unused_imports']) - 10} more")

    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        print(f"\nDetailed report saved to: {output_file}")


if __name__ == '__main__':
    main()
