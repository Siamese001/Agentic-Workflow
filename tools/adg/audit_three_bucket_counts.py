"""Extract authority distribution from the latest ADG snapshot."""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import json
import sqlite3
import sys
from pathlib import Path

snaps = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
if not snaps:
    print("NO_SNAPSHOT_FOUND", file=sys.stderr)
    sys.exit(1)
snap = snaps[-1]
print(f"snapshot={snap.name}")
con = sqlite3.connect(snap)
hist = dict(
    con.execute("SELECT COALESCE(authority,'<NULL>'), COUNT(*) FROM edges GROUP BY authority").fetchall()
)
total = sum(hist.values())
print(f"total_edges={total}")
# Map legacy → new triplet for "after" projection.
mapping = {
    "verified": ("static", "VERIFIED_MODULE", "AUTHORITATIVE"),
    "unresolved": ("static", "UNRESOLVED_MODULE", "RISK_SIGNAL_ONLY"),
    "dynamic": ("static", "UNRESOLVED_DYNAMIC", "UNKNOWN_NOT_PROOF"),
    "external": ("static", "NOT_APPLICABLE", "EXTERNAL_ONLY"),
    "test_only": ("static", "VERIFIED_MODULE", "EXCLUDED_TEST_ONLY"),
    "runtime_observed": ("runtime", "VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME"),
}
bucket_counts = {"static": 0, "runtime": 0, "registry": 0}
auth_status_counts: dict[str, int] = {}
res_counts: dict[str, int] = {}
for legacy, n in hist.items():
    if legacy == "<NULL>" or legacy not in mapping:
        continue
    bucket, res, auth = mapping[legacy]
    bucket_counts[bucket] += n
    auth_status_counts[auth] = auth_status_counts.get(auth, 0) + n
    res_counts[res] = res_counts.get(res, 0) + n

result = {
    "snapshot": snap.name,
    "total_edges": total,
    "before_legacy_authority_histogram": hist,
    "after_projected_bucket_counts": bucket_counts,
    "after_projected_authority_status_counts": auth_status_counts,
    "after_projected_resolution_status_counts": res_counts,
    "proof_count": auth_status_counts.get("AUTHORITATIVE", 0)
    + auth_status_counts.get("AUTHORITATIVE_RUNTIME", 0)
    + auth_status_counts.get("AUTHORITATIVE_REGISTRY", 0),
    "risk_count": auth_status_counts.get("RISK_SIGNAL_ONLY", 0)
    + auth_status_counts.get("UNKNOWN_NOT_PROOF", 0)
    + auth_status_counts.get("PARTIAL", 0),
    "inventory_only_count": auth_status_counts.get("EXCLUDED_TEST_ONLY", 0)
    + auth_status_counts.get("EXCLUDED_TYPE_ONLY", 0)
    + auth_status_counts.get("EXTERNAL_ONLY", 0)
    + auth_status_counts.get("NON_AUTHORITATIVE_HINT", 0),
}
out_path = Path("docs/reports/adg/before_after_adg_authority_counts.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"wrote={out_path}")
print(json.dumps(result, indent=2))
