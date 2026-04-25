"""Preview impact of decay + threshold filter on the live memory DB.

Read-only: opens the store (which runs the additive migration — SAFE, no data
loss), then shows how many entities would be hidden/visible at the default
0.3 threshold. Does not mutate rows beyond the column additions.
"""

from __future__ import annotations

import time
from collections import Counter

from tools.memory.memory_decay import confidence_threshold, effective_confidence
from tools.memory.sqlite_memory_store import SqliteMemoryStore


def main() -> None:
    store = SqliteMemoryStore()
    threshold = confidence_threshold()
    now = time.time()

    with store.connection() as conn:
        rows = conn.execute("SELECT name, entity_type, confidence, last_reinforced FROM entities").fetchall()

    by_type_total: Counter[str] = Counter()
    by_type_visible: Counter[str] = Counter()
    by_type_hidden: Counter[str] = Counter()
    for r in rows:
        et = str(r["entity_type"])
        by_type_total[et] += 1
        eff = effective_confidence(
            float(r["confidence"]),
            float(r["last_reinforced"] or now),
            et,
            now=now,
        )
        if eff >= threshold:
            by_type_visible[et] += 1
        else:
            by_type_hidden[et] += 1

    print(f"Threshold: {threshold}")
    print(f"Total entities: {sum(by_type_total.values())}")
    print()
    print(f"{'entity_type':<25} {'total':>7} {'visible':>9} {'hidden':>8}")
    print("-" * 55)
    for et in sorted(by_type_total, key=lambda x: -by_type_total[x]):
        print(f"{et:<25} {by_type_total[et]:>7} {by_type_visible[et]:>9} {by_type_hidden[et]:>8}")
    print("-" * 55)
    print(
        f"{'TOTAL':<25} {sum(by_type_total.values()):>7} "
        f"{sum(by_type_visible.values()):>9} {sum(by_type_hidden.values()):>8}"
    )


if __name__ == "__main__":
    main()
