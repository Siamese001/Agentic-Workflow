"""Verify the W4d-2 targeted re-routes."""
from __future__ import annotations

import csv
from pathlib import Path

LEDGER = Path("docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv")
csv.field_size_limit(2_000_000)
rows = list(csv.DictReader(LEDGER.open("r", encoding="utf-8")))
by_id = {r["req_id"]: r for r in rows}

print("=== U0 INTAKE ROUTING ===")
for rid in ["10C-REQ-049", "10C-REQ-050", "10C-REQ-051", "10C-REQ-052",
            "10C-REQ-053", "10C-REQ-054", "10C-REQ-055", "10C-REQ-168"]:
    r = by_id[rid]
    print(f"  {rid}  owner={r['canonical_owner_surface']:<40} span={r['otel_span_expected']:<35} status={r['final_acceptance_status']}")

print("\n=== PEDAGOGICAL ROWS ===")
for r in rows:
    if "PEDAGOGICAL_ROW" in r["hardening_notes"]:
        print(f"  {r['req_id']}  direct={r['direct_or_implied']:<25} status={r['final_acceptance_status']:<22} note={r['hardening_notes'][:80]}")

print("\n=== W4d REVIEW ROWS (118, 140, 194) ===")
for rid in ["10C-REQ-118", "10C-REQ-140", "10C-REQ-194"]:
    r = by_id[rid]
    print(f"  {rid}  owner={r['canonical_owner_surface']:<40} status={r['final_acceptance_status']}")
    print(f"           note={r['hardening_notes'][:120]}")

print("\n=== L5 ARTIFACT LANGUAGE (sample 3 L5 rows) ===")
l5_rows = [r for r in rows if r["canonical_owner_surface"] == "00A_L5_Governance_Safety"][:3]
for r in l5_rows:
    print(f"  {r['req_id']}: {r['runtime_artifact_expected'][:90]}")
    print(f"          span={r['otel_span_expected']}")

print("\n=== SOURCE-LOCK SAMPLE ===")
locked_count = sum(1 for r in rows if r["source_text_sha256"])
unlocked_sources = sorted({r["source_file"] for r in rows if not r["source_text_sha256"]})
print(f"  source-locked: {locked_count}/{len(rows)}")
print(f"  unlocked source files (derived/audit notes): {len(unlocked_sources)}")
for sf in unlocked_sources[:5]:
    print(f"    - {sf}")

print("\n=== EXISTENCE CHECK SAMPLE (test_file_exists) ===")
exists_counts = {"true": 0, "false": 0, "": 0}
for r in rows:
    exists_counts[r["test_file_exists"]] = exists_counts.get(r["test_file_exists"], 0) + 1
print(f"  test_file_exists: {exists_counts}")

print("\n=== NEGATIVE-CONTROL-SPECIFIC SAMPLE (3 CRITICAL rows) ===")
critical_rows = [r for r in rows if r["severity_if_missing"] == "CRITICAL"][:3]
for r in critical_rows:
    print(f"  {r['req_id']}: {r['negative_control_specific'][:130]}")
