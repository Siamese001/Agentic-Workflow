#!/usr/bin/env python3
"""Get detailed unused import information from ADG."""

import json
import sqlite3
from pathlib import Path


def get_unused_import_details(db_path: str, target_dir: str) -> dict:
    """Get detailed unused import information for target directory."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = {}

    # Query for unused import edges in target directory
    cursor.execute(
        """
        SELECT e.src_id, e.dst_id, e.source_file, e.line_no, e.symbol
        FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type = 'unused_import'
        AND n.resolved_path LIKE ?
        ORDER BY e.source_file, e.line_no
    """,
        (f"%{target_dir}%",),
    )

    edges = cursor.fetchall()

    for src_id, dst_id, source_file, line_no, symbol in edges:
        if source_file not in results:
            results[source_file] = []

        # Get the import name from the destination node
        cursor.execute(
            """
            SELECT adg_name, resolved_path
            FROM nodes
            WHERE id = ?
        """,
            (dst_id,),
        )

        dst_node = cursor.fetchone()

        results[source_file].append(
            {
                "line": line_no,
                "symbol": symbol,
                "import_name": dst_node[0] if dst_node else "unknown",
                "import_path": dst_node[1] if dst_node else "unknown",
            }
        )

    conn.close()

    return results


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python get_unused_import_details.py <adg_db_path> <target_dir> [output_file]")
        sys.exit(1)

    db_path = sys.argv[1]
    target_dir = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Querying ADG database: {db_path}")
    print(f"Target directory: {target_dir}")
    print("=" * 70)

    results = get_unused_import_details(db_path, target_dir)

    print(f"\nFound unused imports in {len(results)} files:")

    for file_path, imports in sorted(results.items()):
        print(f"\n{file_path} ({len(imports)} imports):")
        for imp in imports[:5]:  # Show first 5
            print(f"  Line {imp['line']}: {imp['symbol']}")
        if len(imports) > 5:
            print(f"  ... and {len(imports) - 5} more")

    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\nDetailed report saved to: {output_file}")


if __name__ == "__main__":
    main()
