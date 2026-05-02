"""Update operator CSV sign-off columns for a set of RTC-REQ rows.

Per operator directive 2026-05-01 15:24 UTC-04:00 — every wave MUST
update the operator CSV at
``C:\\Users\\amita\\Downloads\\runtime_certification_requirements_100_percent_hardened.csv``
on completion. This helper is the canonical mechanism so the update is:

  - **Idempotent** — safe to re-run; rewrites the same rows with the
    same values.
  - **Atomic** — writes to a temp file, then renames into place.
  - **Schema-stable** — preserves all existing columns; only updates the
    four signoff_* fields and the timestamp.
  - **Auditable** — emits a JSON receipt to
    ``artifacts/certification/csv_signoff_updates/<utc_timestamp>.json``
    so each wave's CSV update is tracked over time.

CLI usage:

  python tools/cert/update_csv_signoff.py \\
      --req-ids RTC-REQ-040,RTC-REQ-041,RTC-REQ-042 \\
      --status SIGNED_OFF \\
      --evidence-artifact artifacts/certification/foo.json \\
      --summary "Wave D: bar baz" \\
      --wave-label "Wave D — semantic cache closeout"

Library usage:

  from tools.cert.update_csv_signoff import update_signoff
  update_signoff(
      req_ids=["RTC-REQ-040", ...],
      status="SIGNED_OFF",
      evidence_artifact="artifacts/certification/foo.json",
      summary="Wave D: bar baz",
      wave_label="Wave D",
  )
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Default path; override via CLI --csv-path or env CSV_SIGNOFF_PATH.
DEFAULT_CSV_PATH = Path(
    r"C:\Users\amita\Downloads\runtime_certification_requirements_100_percent_hardened.csv"
)
RECEIPT_DIR = Path(__file__).resolve().parents[2] / "artifacts" / "certification" / "csv_signoff_updates"

VALID_STATUSES = {"SIGNED_OFF", "BLOCKED", "NOT_VERIFIED"}

REQUIRED_SIGNOFF_COLUMNS = (
    "signoff_status",
    "signoff_evidence_artifact",
    "signoff_evidence_summary",
    "signoff_checked_at_utc",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _resolve_csv_path(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    env = os.environ.get("CSV_SIGNOFF_PATH")
    if env:
        return Path(env)
    return DEFAULT_CSV_PATH


def update_signoff(
    *,
    req_ids: Iterable[str],
    status: str,
    evidence_artifact: str,
    summary: str,
    wave_label: str = "(unspecified wave)",
    csv_path: Path | None = None,
) -> dict:
    """Apply sign-off update; returns receipt dict and writes JSON receipt.

    Raises:
        ValueError: invalid status, missing required signoff columns,
            or zero req_ids matched.
        FileNotFoundError: if CSV does not exist at resolved path.
    """
    if status not in VALID_STATUSES:
        raise ValueError(
            f"invalid status {status!r}; must be one of {sorted(VALID_STATUSES)}"
        )

    target_ids = sorted({str(r).strip() for r in req_ids if str(r).strip()})
    if not target_ids:
        raise ValueError("req_ids is empty")

    path = _resolve_csv_path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

    with open(path, encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        rows = list(rdr)
        fieldnames = list(rdr.fieldnames or [])

    # Schema check — ensure signoff columns exist (don't add them here;
    # they should already exist from the initial signoff audit).
    missing_cols = [c for c in REQUIRED_SIGNOFF_COLUMNS if c not in fieldnames]
    if missing_cols:
        raise ValueError(
            f"CSV at {path} is missing required signoff columns: {missing_cols}. "
            f"Run the initial signoff audit first."
        )

    now = _utc_now()
    matched: list[str] = []
    unmatched: list[str] = []

    target_set = set(target_ids)
    for r in rows:
        if r["req_id"] in target_set:
            r["signoff_status"] = status
            r["signoff_evidence_artifact"] = evidence_artifact
            r["signoff_evidence_summary"] = summary
            r["signoff_checked_at_utc"] = now
            matched.append(r["req_id"])

    matched_set = set(matched)
    unmatched = sorted(target_set - matched_set)

    # Atomic write
    tmp_fd, tmp_path = tempfile.mkstemp(
        prefix="csv_signoff_", suffix=".csv", dir=str(path.parent)
    )
    os.close(tmp_fd)
    try:
        with open(tmp_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        shutil.move(tmp_path, path)
    except Exception:
        # Best-effort cleanup
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Sign-off rollup post-update
    counts: dict[str, int] = {"SIGNED_OFF": 0, "BLOCKED": 0, "NOT_VERIFIED": 0}
    for r in rows:
        s = r.get("signoff_status") or "(unset)"
        counts[s] = counts.get(s, 0) + 1

    receipt = {
        "tool": "tools/cert/update_csv_signoff.py",
        "wave_label": wave_label,
        "applied_at_utc": now,
        "csv_path": str(path),
        "status_set_to": status,
        "evidence_artifact": evidence_artifact,
        "summary": summary,
        "requested_req_ids": target_ids,
        "matched_req_ids": sorted(matched),
        "unmatched_req_ids": unmatched,
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "post_update_rollup": counts,
        "post_update_total_rows": len(rows),
    }

    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPT_DIR / f"{now.replace(':', '-')}_{wave_label.replace(' ', '_').replace('—', '-')[:60]}.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    return receipt


def _cli_main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0] if __doc__ else "")
    p.add_argument("--req-ids", required=True,
                   help="Comma-separated RTC-REQ ids (e.g. RTC-REQ-040,RTC-REQ-041)")
    p.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    p.add_argument("--evidence-artifact", required=True,
                   help="Path or URI to backing evidence artifact")
    p.add_argument("--summary", required=True,
                   help="One-line evidence summary")
    p.add_argument("--wave-label", default="(unspecified wave)",
                   help="Wave label for the receipt (e.g. 'Wave D — semantic cache')")
    p.add_argument("--csv-path", type=Path, default=None,
                   help="Override CSV path (defaults to operator Downloads CSV)")
    args = p.parse_args()

    req_ids = [r.strip() for r in args.req_ids.split(",") if r.strip()]
    receipt = update_signoff(
        req_ids=req_ids,
        status=args.status,
        evidence_artifact=args.evidence_artifact,
        summary=args.summary,
        wave_label=args.wave_label,
        csv_path=args.csv_path,
    )

    print(f"[update_csv_signoff] {args.wave_label}")
    print(f"  csv: {receipt['csv_path']}")
    print(f"  status_set_to: {receipt['status_set_to']}")
    print(f"  matched: {receipt['matched_count']}/{len(req_ids)} req_ids")
    if receipt["unmatched_req_ids"]:
        print(f"  WARNING: unmatched req_ids: {receipt['unmatched_req_ids']}")
    print(f"  post-update rollup: {receipt['post_update_rollup']}")
    print(f"  post-update total: {receipt['post_update_total_rows']} rows")

    if receipt["unmatched_req_ids"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_cli_main())
