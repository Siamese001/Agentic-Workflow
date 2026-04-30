"""Look up the exact source-text content for the rows the user flagged."""
from __future__ import annotations

import csv
from pathlib import Path

LEDGER = Path("docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv")
csv.field_size_limit(2_000_000)
rows = list(csv.DictReader(LEDGER.open("r", encoding="utf-8")))
by_id = {r["req_id"]: r for r in rows}

TARGETS = ["10C-REQ-011", "10C-REQ-118", "10C-REQ-140", "10C-REQ-162", "10C-REQ-168", "10C-REQ-194"]

for rid in TARGETS:
    r = by_id.get(rid)
    if r is None:
        print(f"\n=== {rid} : NOT FOUND ===")
        continue
    print(f"\n=== {rid} ===")
    print(f"  source_file       : {r['source_file']}")
    print(f"  source_section    : {r['source_section']}")
    print(f"  source_unit_type  : {r['source_unit_type']}")
    print(f"  source_text_short : {r['source_text_short']}")
    print(f"  layer_owner       : {r['layer_owner']}")
    print(f"  semantic_class    : {r['semantic_class']}")
    print(f"  severity          : {r['severity_if_missing']}")
    print(f"  direct_or_implied : {r['direct_or_implied']}")
    print(f"  current owner     : {r['canonical_owner_surface']}")
    canon = r['canonical_requirement_statement']
    print(f"  canonical (full)  : {canon[:300]}")
