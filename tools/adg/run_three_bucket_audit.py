#!/usr/bin/env python3
"""Refresh optional three-bucket audit artifacts on an existing ADG snapshot.

Use this instead of paying the cost on every ``generate_full_adg`` run. Typical
flows:

  # Latest snapshot — runtime view + registry + reports
  ADG_THREE_BUCKET=1 python tools/adg/run_three_bucket_audit.py

  # Reports only (snapshot already has v_runtime_proof)
  ADG_THREE_BUCKET_REPORTS=1 python tools/adg/run_three_bucket_audit.py

  # Then contract gates that read THREE_BUCKET_GAP_REPORT.json
  python ops_scripts/ci/check_three_bucket_gap_thresholds.py

Does **not** rebuild the static graph or materialized views.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate.integration.optional_three_bucket import (  # noqa: E402
    run_optional_three_bucket_enrichment,
    three_bucket_master_enabled,
)


def _latest_snapshot() -> Path:
    snaps = sorted((REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))
    if not snaps:
        raise SystemExit("ERROR: no snapshot at artifacts/adg/adg_indexed_*.sqlite")
    return snaps[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=None, help="ADG sqlite (default: latest)")
    parser.add_argument(
        "--enable-all",
        action="store_true",
        help="Set ADG_THREE_BUCKET=1 for this invocation (runtime + registry + reports)",
    )
    args = parser.parse_args()

    if args.enable_all:
        os.environ["ADG_THREE_BUCKET"] = "1"

    if not three_bucket_master_enabled() and not any(
        os.environ.get(k, "").strip().lower() in ("1", "true", "yes")
        for k in (
            "ADG_RUNTIME_VIEW",
            "ADG_REGISTRY_LIFT",
            "ADG_THREE_BUCKET_REPORTS",
            "ADG_THREE_BUCKET_SIGN",
        )
    ):
        print(
            "ERROR: no three-bucket stage enabled. Use --enable-all or set ADG_THREE_BUCKET=1.",
            file=sys.stderr,
        )
        return 2

    snapshot = args.snapshot or _latest_snapshot()
    if not snapshot.is_file():
        print(f"ERROR: snapshot not found: {snapshot}", file=sys.stderr)
        return 2

    from tools.adg.snapshot_fingerprint import snapshot_fingerprint

    fp = snapshot_fingerprint(snapshot)
    print(
        f"[three_bucket_audit] snapshot={snapshot.name} "
        f"sha256={fp['source_snapshot_sha256']} "
        f"mtime={fp['source_snapshot_mtime_iso']}"
    )
    result = run_optional_three_bucket_enrichment(snapshot)
    if result.skipped_reason:
        print(result.skipped_reason, file=sys.stderr)
        return 2
    gap_json = REPO_ROOT / "docs" / "reports" / "adg" / "THREE_BUCKET_GAP_REPORT.json"
    if gap_json.is_file():
        import json

        from tools.adg.snapshot_fingerprint import print_audit_receipt

        report = json.loads(gap_json.read_text(encoding="utf-8"))
        print_audit_receipt(report, prefix="THREE_BUCKET_AUDIT_RECEIPT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
