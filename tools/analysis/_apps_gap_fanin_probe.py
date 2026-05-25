"""Fan-in probe for the gap items so we can decide implement-vs-remove."""

__adg_consumer_mode__ = "inventory"

import sqlite3


def main() -> None:
    with sqlite3.connect("artifacts/adg/adg_indexed_05022026_1651.sqlite") as con:
        cur = con.cursor()
        paths = [
            "apps_research/services/content_harvester_service.py",
            "apps_lic/reasoning/ExecutiveStrategyAgent.py",
            "apps_lic/reasoning/GovernanceShieldAgent.py",
            "apps_lic/outreach_engine/governed_outreach.py",
        ]
        for p in paths:
            print(f"\n== {p} ==")
            cur.execute(
                """
                SELECT n.adg_name, n.entity_type, COUNT(e.id) AS fanin
                FROM nodes n LEFT JOIN edges e ON e.dst_id=n.id
                WHERE n.resolved_path=?
                GROUP BY n.id ORDER BY fanin DESC LIMIT 8
                """,
                (p,),
            )
            for r in cur.fetchall():
                print(" ", r)


if __name__ == "__main__":
    main()
