"""Sample memory MCP entities to judge type-hygiene."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> None:
    db = Path("artifacts/memory/knowledge_graph.sqlite")
    with sqlite3.connect(str(db)) as c:
        cols = [r[1] for r in c.execute("PRAGMA table_info(entities)")]
        print(f"entities columns: {cols}")
        print()

        order = (
            "updated_at DESC"
            if "updated_at" in cols
            else ("created_at DESC" if "created_at" in cols else "rowid DESC")
        )

        rows = c.execute(
            f"SELECT name FROM entities WHERE entity_type = 'general' ORDER BY {order} LIMIT 10"
        ).fetchall()
        print("Latest 10 'general' entities:")
        for (n,) in rows:
            print(f"  {n}")

        print()
        rows = c.execute(
            f"SELECT entity_type, name FROM entities WHERE entity_type != 'general' ORDER BY {order} LIMIT 10"
        ).fetchall()
        print("Latest 10 protected entities:")
        for et, n in rows:
            print(f"  [{et}] {n}")


if __name__ == "__main__":
    main()
