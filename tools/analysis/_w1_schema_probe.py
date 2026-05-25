"""Schema probe for the ADG SQLite snapshot."""

__adg_consumer_mode__ = "inventory"

import sqlite3


def main() -> None:
    with sqlite3.connect(r"artifacts/adg/adg_indexed_05052026_0722.sqlite") as conn:
        c = conn.cursor()
        print("TABLES:")
        for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            print(f"  {r[0]}")
        print()
        print("EDGES SCHEMA:")
        for r in c.execute("PRAGMA table_info(edges)"):
            print(f"  {r}")
        print()
        print("NODES SCHEMA:")
        for r in c.execute("PRAGMA table_info(nodes)"):
            print(f"  {r}")
        print()
        print("EDGE RELATION TYPES (top 25):")
        for r in c.execute(
            "SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY 2 DESC LIMIT 25"
        ):
            print(f"  {r}")


if __name__ == "__main__":
    main()
