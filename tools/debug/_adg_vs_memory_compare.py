"""Side-by-side: static ADG vs Cursor Agent memory graph — prove they're different stores."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> None:
    print("=" * 70)
    print("STATIC ADG (AST dependency analysis)")
    print("=" * 70)
    adg_candidates = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
    adg = adg_candidates[-1]
    print(f"File:  {adg.name}")
    print(f"Size:  {adg.stat().st_size / 1024 / 1024:.0f} MB")
    with sqlite3.connect(str(adg)) as c:
        tables = [
            r[0]
            for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name LIMIT 15")
        ]
        print(f"Sample tables ({len(tables)} of many): {tables}")
        nodes = c.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edges = c.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        print(f"nodes={nodes:,}  edges={edges:,}")
        print()
        print("Example node (what it looks like):")
        cols = [r[1] for r in c.execute("PRAGMA table_info(nodes)")]
        print(f"  nodes columns: {cols[:8]}...")
        row = c.execute("SELECT * FROM nodes LIMIT 1").fetchone()
        print(f"  first row: {row[:4]}...")
        print()
        print("Example edge:")
        row = c.execute("SELECT relation_type, src_id, dst_id FROM edges LIMIT 1").fetchone()
        print(f"  relation={row[0]!r}  src={row[1]}  dst={row[2]}")

    print()
    print("=" * 70)
    print("MEMORY GRAPH (Cursor Agent persistent knowledge)")
    print("=" * 70)
    mem = Path("artifacts/memory/knowledge_graph.sqlite")
    print(f"File:  {mem.name}")
    print(f"Size:  {mem.stat().st_size / 1024:.0f} KB")
    with sqlite3.connect(str(mem)) as c:
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        print(f"Tables: {tables}")
        for t in tables:
            try:
                n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                print(f"  {t:30s}  {n:>6} rows")
            except sqlite3.Error:
                pass
        print()
        print("Example memory entity:")
        try:
            row = c.execute("SELECT name, entityType FROM entities LIMIT 1").fetchone()
            if row:
                print(f"  name={row[0]!r}  type={row[1]!r}")
        except sqlite3.Error as e:
            print(f"  (could not query entities: {e})")


if __name__ == "__main__":
    main()
