#!/usr/bin/env python3
"""Query ADG for dead functions in specific layers (L_APP, L_OPS)."""

import argparse
import json
import sqlite3
from pathlib import Path


def query_dead_functions_by_layer(layer: str, limit: int = 100) -> list[dict]:
    """Query ADG for dead functions in a specific layer."""
    dbs = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
    if not dbs:
        print("No ADG databases found")
        return []

    db_path = dbs[-1]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Query for functions/classes that export but have no fan-in edges at all
    c.execute(
        """
        SELECT n.adg_name, n.resolved_path, n.entity_type, n.span_line, n.id
        FROM nodes n
        WHERE n.layer = ?
        AND n.id IN (
            SELECT DISTINCT src_id FROM edges
            WHERE relation_type = 'exports'
        )
        AND n.id NOT IN (
            SELECT DISTINCT dst_id FROM edges
            WHERE relation_type IN ('calls', 'imports', 'uses', 'reads_from', 'writes_to')
        )
        ORDER BY n.resolved_path
        LIMIT ?
    """,
        (layer, limit),
    )

    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


def main():
    parser = argparse.ArgumentParser(description="Query dead functions by layer")
    parser.add_argument("--layer", required=True, help="Layer to query (L_APP, L_OPS)")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", required=True, help="Output JSON file")

    args = parser.parse_args()

    dbs = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
    if not dbs:
        print("No ADG databases found")
        return 1

    adg_db = dbs[-1]
    print(f"Using ADG: {adg_db}")

    dead_funcs = query_dead_functions_by_layer(args.layer, args.limit)

    print(f"\nFound {len(dead_funcs)} dead functions in {args.layer}:")
    for func in dead_funcs[:20]:
        print(f"  {func['resolved_path']}:{func.get('span_line', '?')} - {func['adg_name']}")

    if len(dead_funcs) > 20:
        print(f"  ... and {len(dead_funcs) - 20} more")

    output = {
        "adg_database": str(adg_db),
        "layer": args.layer,
        "dead_functions": dead_funcs,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
