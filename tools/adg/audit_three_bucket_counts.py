"""Extract authority distribution from an ADG snapshot (three-bucket projection)."""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "before_after_adg_authority_counts.json"

_LEGACY_TO_TRIPLET: dict[str, tuple[str, str, str]] = {
    "verified": ("static", "VERIFIED_MODULE", "AUTHORITATIVE"),
    "unresolved": ("static", "UNRESOLVED_MODULE", "RISK_SIGNAL_ONLY"),
    "dynamic": ("static", "UNRESOLVED_DYNAMIC", "UNKNOWN_NOT_PROOF"),
    "external": ("static", "NOT_APPLICABLE", "EXTERNAL_ONLY"),
    "test_only": ("static", "VERIFIED_MODULE", "EXCLUDED_TEST_ONLY"),
    "runtime_observed": ("runtime", "VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME"),
}


def _latest_snapshot() -> Path:
    snaps = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    if not snaps:
        raise FileNotFoundError("no ADG snapshot at artifacts/adg/adg_indexed_*.sqlite")
    return snaps[-1]


def run_authority_audit(
    snapshot: Path,
    *,
    out_path: Path | None = None,
) -> dict[str, Any]:
    """Project legacy edge authority into three-bucket counts; optionally write JSON."""
    snapshot = Path(snapshot).resolve()
    con = sqlite3.connect(snapshot)
    try:
        hist = dict(
            con.execute(
                "SELECT COALESCE(authority,'<NULL>'), COUNT(*) FROM edges GROUP BY authority"
            ).fetchall()
        )
    finally:
        con.close()

    total = sum(hist.values())
    bucket_counts = {"static": 0, "runtime": 0, "registry": 0}
    auth_status_counts: dict[str, int] = {}
    res_counts: dict[str, int] = {}
    for legacy, n in hist.items():
        if legacy == "<NULL>" or legacy not in _LEGACY_TO_TRIPLET:
            continue
        bucket, res, auth = _LEGACY_TO_TRIPLET[legacy]
        bucket_counts[bucket] += n
        auth_status_counts[auth] = auth_status_counts.get(auth, 0) + n
        res_counts[res] = res_counts.get(res, 0) + n

    result: dict[str, Any] = {
        "snapshot": snapshot.name,
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

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    return result


def main() -> int:
    try:
        snap = _latest_snapshot()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"snapshot={snap.name}")
    result = run_authority_audit(snap, out_path=DEFAULT_OUT_PATH)
    print(f"total_edges={result['total_edges']}")
    print(f"wrote={DEFAULT_OUT_PATH}")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
