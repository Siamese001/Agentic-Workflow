"""Inspect 10C ledger to enumerate all unique values needing mapping."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

LEDGER = Path("docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv")
csv.field_size_limit(2_000_000)
rows = list(csv.DictReader(LEDGER.open("r", encoding="utf-8")))

print(f"Total rows: {len(rows)}")
print()
print("=== ALL UNIQUE layer_owner VALUES ===")
for k, v in sorted(Counter(r["layer_owner"] for r in rows).items(), key=lambda x: -x[1]):
    print(f"  {v:>3}  {k}")

print()
print("=== ALL UNIQUE runtime_phase VALUES ===")
for k, v in sorted(Counter(r["runtime_phase"] for r in rows).items(), key=lambda x: -x[1]):
    print(f"  {v:>3}  {k}")

print()
print("=== ALL UNIQUE semantic_class VALUES ===")
for k, v in sorted(Counter(r["semantic_class"] for r in rows).items(), key=lambda x: -x[1]):
    print(f"  {v:>3}  {k}")

print()
print("=== ALL UNIQUE source_file VALUES ===")
for k, v in sorted(Counter(r["source_file"] for r in rows).items(), key=lambda x: -x[1]):
    print(f"  {v:>3}  {k}")
