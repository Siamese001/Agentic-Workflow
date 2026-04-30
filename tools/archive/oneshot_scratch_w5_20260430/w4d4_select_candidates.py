"""W4d-4 candidate selection: list CRITICAL rows per target surface."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

LEDGER = Path("docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv")
csv.field_size_limit(2_000_000)
rows = list(csv.DictReader(LEDGER.open("r", encoding="utf-8")))

TARGET_SURFACES = [
    "01_U0_Request_Intake",
    "00A_L5_Governance_Safety",
    "03A_C0_Context_Engine",
    "03B_PA_Prompt_Assembly",
    "04_L2_Execute",
    "05_Exit_Evaluation_and_Control",
    "00B_L4_State_Archive_and_UWG",
]

by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
for r in rows:
    if (r.get("severity_if_missing") or "").strip().upper() != "CRITICAL":
        continue
    s = r["canonical_owner_surface"]
    by_surface[s].append(r)

print("=" * 96)
print("CRITICAL rows per target surface")
print("=" * 96)
for s in TARGET_SURFACES:
    rs = by_surface.get(s, [])
    print(f"\n[{s}]   ({len(rs)} CRITICAL)")
    for r in rs:
        canon = r["canonical_requirement_statement"][:120]
        print(f"  {r['req_id']}  span={r['otel_span_expected']:<35}  canon='{canon}'")

print("\n" + "=" * 96)
print("Total CRITICAL rows:", sum(len(v) for v in by_surface.values()))
print("Surfaces with 0 CRITICAL rows:")
for s in TARGET_SURFACES:
    if not by_surface.get(s):
        print(f"  - {s}")
