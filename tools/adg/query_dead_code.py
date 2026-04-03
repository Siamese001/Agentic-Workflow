#!/usr/bin/env python3
"""Query ADG for dead code and dead imports."""

import sqlite3
import json
from pathlib import Path

def main():
    # Find latest ADG
    dbs = sorted(Path('artifacts/adg').glob('adg_indexed_*.sqlite'))
    if not dbs:
        print('No ADG databases found')
        return 1
    db_path = dbs[-1]
    print(f'ADG: {db_path.name}')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Get edge stats
    c.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type")
    print('\n=== EDGE TYPE COUNTS ===')
    for row in c.fetchall():
        print(f'  {row[0]}: {row[1]}')

    # Find exports with no consumers (dead code)
    print('\n=== DEAD CODE: exports with no consumers ===')
    c.execute('''
        SELECT n.adg_name, n.resolved_path, n.layer, COUNT(e.id) as export_count
        FROM nodes n
        JOIN edges e ON n.id = e.src_id
        WHERE e.relation_type = 'exports'
        AND n.id NOT IN (
            SELECT DISTINCT dst_id FROM edges 
            WHERE relation_type IN ('calls', 'imports', 'reads_from', 'writes_to')
        )
        GROUP BY n.id
        ORDER BY export_count DESC
        LIMIT 50
    ''')
    dead_exports = c.fetchall()
    print(f'Found {len(dead_exports)} nodes with exports but no consumers:\n')
    for r in dead_exports[:30]:
        print(f"  {r['adg_name']} in {r['resolved_path']} [{r['layer']}] - {r['export_count']} exports")

    # Find orphaned nodes (no edges at all)
    print('\n=== ORPHANED NODES (no edges) ===')
    c.execute('''
        SELECT n.adg_name, n.resolved_path, n.layer, n.entity_type
        FROM nodes n
        WHERE n.id NOT IN (SELECT DISTINCT src_id FROM edges)
        AND n.id NOT IN (SELECT DISTINCT dst_id FROM edges)
        LIMIT 30
    ''')
    orphans = c.fetchall()
    print(f'Found {len(orphans)} orphaned nodes:\n')
    for r in orphans[:20]:
        print(f"  {r['adg_name']} ({r['entity_type']}) in {r['resolved_path']} [{r['layer']}]")

    # Find imports that might be unused (dst node has no exports/calls)
    print('\n=== POTENTIALLY UNUSED IMPORTS ===')
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
        LIMIT 50
    ''')
    unused_imports = c.fetchall()
    print(f'Found {len(unused_imports)} potentially unused imports:\n')
    for r in unused_imports[:30]:
        print(f"  {r['source_file']}:{r['line_no']} imports {r['symbol']} from {r['target_module']}")

    # Summary by layer
    print('\n=== DEAD CODE BY LAYER ===')
    c.execute('''
        SELECT n.layer, COUNT(*) as count
        FROM nodes n
        JOIN edges e ON n.id = e.src_id
        WHERE e.relation_type = 'exports'
        AND n.id NOT IN (
            SELECT DISTINCT dst_id FROM edges 
            WHERE relation_type IN ('calls', 'imports', 'reads_from', 'writes_to')
        )
        GROUP BY n.layer
        ORDER BY count DESC
    ''')
    for r in c.fetchall():
        print(f"  {r['layer']}: {r['count']} dead exports")

    conn.close()
    
    # Save full results to JSON
    output = {
        'adg_database': str(db_path),
        'dead_exports': [dict(r) for r in dead_exports],
        'orphans': [dict(r) for r in orphans],
        'unused_imports': [dict(r) for r in unused_imports],
    }
    output_path = Path('artifacts/adg/dead_code_analysis.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f'\nFull results saved to: {output_path}')
    return 0

if __name__ == '__main__':
    exit(main())
