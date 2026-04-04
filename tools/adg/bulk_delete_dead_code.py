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


def main():
    parser = argparse.ArgumentParser(description='Bulk delete dead code based on ADG analysis')
    parser.add_argument('--layer', help='Target layer (e.g., L_TEST, L_TOOLS)')
    parser.add_argument('--directory', help='Target directory (e.g., tests/adg/)')
    parser.add_argument('--functions', action='store_true', help='Target dead functions only (not modules)')
    parser.add_argument('--unused-imports', action='store_true', help='Target unused imports')
    parser.add_argument('--output', help='Output JSON file for targets')
    parser.add_argument('--input', help='Input JSON file with targets to delete')
    parser.add_argument('--dry-run', action='store_true', help='Preview deletions without executing')
    parser.add_argument('--execute', action='store_true', help='Execute deletions')

    args = parser.parse_args()

    if args.output:
        # Query mode - generate targets
        if args.unused_imports:
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
