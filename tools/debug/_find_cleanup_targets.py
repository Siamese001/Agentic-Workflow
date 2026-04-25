"""Identify the exact page IDs for:
1. Completion targets: rows related to L1 reasoning best-practices (planner_budget, planner_overhead_metric, prompt_envelope, thought_redactor)
2. Duplicate targets: W8 P2 duplicate, E.F3 P3 unscored duplicate, E.F2 P4 duplicate
3. AGG meta-rows: all 7 GAP-AGG rows
"""

import json

rows = json.load(open("artifacts/notion/open_rows_with_ids.json", encoding="utf-8"))

print("=" * 80)
print("COMPLETION CANDIDATES (L1 reasoning best-practices)")
print("=" * 80)
keywords = [
    "planner_budget",
    "planner_overhead",
    "prompt_envelope",
    "thought_redactor",
    "l1-reasoning",
    "L1 reasoning",
    "reasoning best",
    "best-practice",
]
for r in rows:
    t = (r["title"] + " " + r["blocking"] + " " + r["plan_file"]).lower()
    if any(k.lower() in t for k in keywords):
        print(f"  [{r['band']:<9}] {r['wave']:<12} {r['phase']:<20} {r['title'][:80]}")
        print(f"    id={r['id']} plan_file={r['plan_file']}")

print()
print("=" * 80)
print("DUPLICATES")
print("=" * 80)
# W8 duplicates
w8 = [r for r in rows if r["wave"] == "W8" and "SC" in r["title"]]
print(f"\nW8 SC-1 rows: {len(w8)}")
for r in w8:
    print(f"  [{r['band']:<9} imp={r['impact']}] id={r['id']}")
    print(f"    title={r['title'][:90]}")

# E.F2 / E.F3 duplicates
ef = [r for r in rows if r["wave"] == "E" and r["phase"] in ("E.F2", "E.F3")]
print(f"\nE.F2/E.F3 rows: {len(ef)}")
for r in ef:
    print(f"  [{r['band']:<9} imp={r['impact']}] {r['phase']} id={r['id']}")
    print(f"    title={r['title'][:90]}")

print()
print("=" * 80)
print("AGG META-ROWS")
print("=" * 80)
agg = [r for r in rows if r["wave"] == "AGG"]
for r in agg:
    print(f"  {r['phase']:<10} {r['title'][:80]}")
    print(f"    id={r['id']}")
