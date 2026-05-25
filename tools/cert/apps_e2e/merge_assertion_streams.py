"""Merge APPS-DOM + APPS-NEG-CTRL assertion streams into the compiler's
canonical input file.

Plan: .windsurf/plans/apps-runtime-domain-enforcement-a7e9d4.md W6.P1.

Inputs (all optional — missing files are treated as empty streams):
  - certification/apps_evidence_assertions.jsonl       (existing canonical stream)
  - certification/apps_domain_evidence_assertions.jsonl (W3.P1 — 104 APPS-DOM rows)
  - certification/apps_negative_control_assertions.jsonl (W3.P2 — 16 rows)

Output:
  certification/apps_evidence_assertions.jsonl  (merged, deterministic order)

Hard rules:
  * Dedup by assertion_id — last writer wins, but ordering follows
    (req_id, control, app_name) for stable output.
  * NEVER mutate the source streams; merger is read-only on inputs.
  * Backup the prior canonical stream to certification/.bak/ before
    overwriting (preserves rollback path).

Exit codes:
  0 — merged
  2 — fatal error (e.g. unreadable source)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
from cert_paths import CERT_DATA_DIR as CERT_DIR
BACKUP_DIR = CERT_DIR / ".bak"

CANONICAL = CERT_DIR / "apps_evidence_assertions.jsonl"
DOMAIN = CERT_DIR / "apps_domain_evidence_assertions.jsonl"
NEG_CTRL = CERT_DIR / "apps_negative_control_assertions.jsonl"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    f"ERROR: {path}:{lineno} invalid JSON: {exc}"
                )
    return rows


def merge(
    canonical_path: Path = CANONICAL,
    domain_path: Path = DOMAIN,
    neg_ctrl_path: Path = NEG_CTRL,
    out_path: Path = CANONICAL,
    backup: bool = True,
) -> dict[str, int]:
    canonical_rows = _read_jsonl(canonical_path)
    domain_rows = _read_jsonl(domain_path)
    neg_ctrl_rows = _read_jsonl(neg_ctrl_path)

    # Capture pre-merge stats per source for the report
    pre_counts = {
        "canonical": len(canonical_rows),
        "apps_domain": len(domain_rows),
        "apps_negative_control": len(neg_ctrl_rows),
    }

    # Filter canonical to drop pre-existing APPS-DOM rows (stale from a prior
    # merge run) — domain & neg_ctrl files are the authority for those.
    apps_dom_prefixes = ("APPS-DOM-",)
    canonical_kept = [
        r for r in canonical_rows
        if not any(str(r.get("req_id", "")).startswith(p) for p in apps_dom_prefixes)
    ]
    canonical_dropped = len(canonical_rows) - len(canonical_kept)

    # Merge with dedup by assertion_id; later rows win on collision
    merged: dict[str, dict[str, Any]] = {}
    for source in (canonical_kept, domain_rows, neg_ctrl_rows):
        for row in source:
            aid = row.get("assertion_id")
            if not aid:
                continue
            merged[aid] = row

    # Stable output order: (req_id, control, app_name, assertion_id)
    out_rows = sorted(
        merged.values(),
        key=lambda r: (
            str(r.get("req_id", "")),
            str(r.get("control", "")),
            str(r.get("app_name") or ""),
            str(r.get("assertion_id", "")),
        ),
    )

    # Backup before overwrite
    if backup and out_path.exists() and out_path == CANONICAL:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        bak = BACKUP_DIR / f"apps_evidence_assertions.{ts}.jsonl"
        shutil.copy2(out_path, bak)

    # Write merged file deterministically
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in out_rows:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")

    return {
        "canonical_pre": pre_counts["canonical"],
        "canonical_apps_dom_dropped": canonical_dropped,
        "apps_domain_added": pre_counts["apps_domain"],
        "apps_negative_control_added": pre_counts["apps_negative_control"],
        "merged_total": len(out_rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, default=CANONICAL)
    parser.add_argument("--domain", type=Path, default=DOMAIN)
    parser.add_argument("--neg-ctrl", type=Path, default=NEG_CTRL)
    parser.add_argument("--out", type=Path, default=CANONICAL)
    parser.add_argument("--no-backup", action="store_true")
    args = parser.parse_args(argv)

    stats = merge(
        canonical_path=args.canonical,
        domain_path=args.domain,
        neg_ctrl_path=args.neg_ctrl,
        out_path=args.out,
        backup=not args.no_backup,
    )
    print("Merge stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"Wrote {args.out.relative_to(REPO_ROOT) if args.out.is_absolute() else args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
