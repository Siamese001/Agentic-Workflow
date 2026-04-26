"""Compare violations between old (0521) and new (0843) snapshots."""
import sqlite3, glob, os
from collections import Counter

# Old snapshot is 0521, new is 0843
old = "artifacts/adg/adg_indexed_04252026_0521.sqlite"
new = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
print(f"Old: {old}")
print(f"New: {new}\n")

def categorize(path):
    c = sqlite3.connect(path)
    cur = c.cursor()
    cur.execute("SELECT category, severity, evidence FROM violations WHERE disposition='untriaged'")
    rows = cur.fetchall()
    c.close()
    return rows

old_rows = categorize(old)
new_rows = categorize(new)
print(f"Old untriaged: {len(old_rows)}")
print(f"New untriaged: {len(new_rows)}")
print(f"Delta: {len(new_rows) - len(old_rows)}\n")

# By (category, severity, evidence)
old_keys = Counter((c, s, e) for c, s, e in old_rows)
new_keys = Counter((c, s, e) for c, s, e in new_rows)

# What evidence patterns are NEW in 0843?
print("NEW evidence patterns (in 0843, not in 0521):")
new_only = []
for k, n in new_keys.items():
    o = old_keys.get(k, 0)
    if n > o:
        new_only.append((k, o, n, n - o))
new_only.sort(key=lambda x: -x[3])
for (cat, sev, ev), o, n, d in new_only[:25]:
    print(f"  +{d:>4d}  [{sev}] {cat:<14} ev={(ev or '')[:50]}  (old={o}, new={n})")

# What evidence patterns SHRANK?
print("\nSHRUNK patterns (in 0521, smaller in 0843):")
shrunk = []
for k, o in old_keys.items():
    n = new_keys.get(k, 0)
    if n < o:
        shrunk.append((k, o, n, o - n))
shrunk.sort(key=lambda x: -x[3])
for (cat, sev, ev), o, n, d in shrunk[:15]:
    print(f"  -{d:>4d}  [{sev}] {cat:<14} ev={(ev or '')[:50]}  (old={o}, new={n})")

# Net change
print(f"\nNet additions: +{sum(d for _,_,_,d in new_only)}")
print(f"Net removals: -{sum(d for _,_,_,d in shrunk)}")
