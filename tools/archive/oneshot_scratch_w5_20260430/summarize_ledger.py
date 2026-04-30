"""One-shot summary of the current 10C ledger CSV."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

LEDGER = Path("docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv")
csv.field_size_limit(2_000_000)

rows = list(csv.DictReader(LEDGER.open("r", encoding="utf-8")))

print(f"=== FILE: {LEDGER} ===")
print(f"  rows: {len(rows)}")
print()

print("=== SEVERITY DISTRIBUTION ===")
sev = Counter(r["severity_if_missing"] for r in rows)
for k, v in sorted(sev.items(), key=lambda x: -x[1]):
    print(f"  {k:<10} {v:>3}")

print()
print("=== SEMANTIC CLASS DISTRIBUTION ===")
sc = Counter(r["semantic_class"] for r in rows)
for k, v in sorted(sc.items(), key=lambda x: -x[1])[:10]:
    print(f"  {k[:65]:<65} {v:>3}")

print()
print("=== LAYER OWNER DISTRIBUTION (top 12) ===")
lo = Counter(r["layer_owner"] for r in rows)
for k, v in sorted(lo.items(), key=lambda x: -x[1])[:12]:
    print(f"  {k[:40]:<40} {v:>3}")

print()
print("=== DIRECT_OR_IMPLIED ===")
doi = Counter(r["direct_or_implied"] for r in rows)
for k, v in sorted(doi.items(), key=lambda x: -x[1]):
    print(f"  {k[:45]:<45} {v:>3}")

print()
print("=== CONFIDENCE DISTRIBUTION ===")
buckets = Counter()
for r in rows:
    try:
        c = float(r["confidence_score"])
    except (ValueError, KeyError):
        buckets["(missing)"] += 1
        continue
    if c >= 0.95:
        buckets["0.95-1.00"] += 1
    elif c >= 0.85:
        buckets["0.85-0.94"] += 1
    elif c >= 0.75:
        buckets["0.75-0.84"] += 1
    else:
        buckets["<0.75"] += 1
for k, v in sorted(buckets.items()):
    print(f"  {k:<12} {v:>3}")

print()
print("=== ID RANGE ===")
ids = sorted(int(r["req_id"].split("-")[-1]) for r in rows)
print(f"  first : 10C-REQ-{ids[0]:03d}")
print(f"  last  : 10C-REQ-{ids[-1]:03d}")
id_set = set(ids)
gaps = [i for i in range(ids[0], ids[-1] + 1) if i not in id_set]
print(f"  gaps  : {len(gaps)} {gaps[:10] if gaps else '(none)'}")

print()
print("=== TOP 30 REQs BY SEVERITY (CRITICAL first) ===")
print(f"  {'req_id':<14} {'sev':<9} {'layer':<22} {'short':<60}")
print(f"  {'-'*14} {'-'*9} {'-'*22} {'-'*60}")
sev_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "": 4}
sorted_rows = sorted(
    rows,
    key=lambda r: (sev_rank.get(r["severity_if_missing"], 5), r["req_id"]),
)
for r in sorted_rows[:30]:
    short = (r["source_text_short"] or "")[:58]
    layer = (r["layer_owner"] or "")[:20]
    print(f"  {r['req_id']:<14} {r['severity_if_missing']:<9} {layer:<22} {short}")
