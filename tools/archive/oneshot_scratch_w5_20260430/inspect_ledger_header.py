"""Quick on-disk ledger header verification."""
import csv
csv.field_size_limit(2_000_000)
rows = list(csv.DictReader(open(
    "docs/reports/design/10c_reconciliation/10c_semantic_requirement_ledger.csv",
    encoding="utf-8")))
print(f"on-disk ledger: rows={len(rows)}  columns={len(rows[0])}")
cols = set(rows[0].keys())
print("\n--- W4d-2 column presence check ---")
for c in [
    "canonical_owner_surface", "source_commit_sha", "source_text_sha256",
    "test_file_exists", "ci_gate_exists", "proof_bundle_exists",
    "last_passed_commit", "negative_control_specific",
]:
    print(f"  {c}: {c in cols}")
print("\n--- first row sample ---")
r = rows[0]
for k in ("req_id", "canonical_owner_surface", "source_text_sha256",
         "source_commit_sha", "test_file_exists"):
    val = r.get(k, "(missing)")
    print(f"  {k:<26} = {val[:60] if val else '(empty)'}")
