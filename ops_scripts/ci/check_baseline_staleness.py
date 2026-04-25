#!/usr/bin/env python3
"""Gate S_STALE — baseline-age warning for ratchet JSONs.

Scans every ``wiring_*_ratchet.json`` under ``ops_scripts/ci/baselines/`` and
flags any baseline whose effective age exceeds a threshold AND whose count is
non-zero. Surfaces dormant debt — a ratchet that hasn't moved in weeks is
almost always debt nobody is touching.

Tier
    W (warn) by default — does not block CI. Use ``--strict`` to flip to
    blocking (exit 1 on any stale non-zero baseline).

Age source (most-recent wins)
    1. ``tightened_at``   — updated on each monotone auto-tighten (W1.1)
    2. ``last_run_at``    — updated on every run that writes the record
    3. ``seeded_at``      — initial seed timestamp

Usage
    python ops_scripts/ci/check_baseline_staleness.py
    python ops_scripts/ci/check_baseline_staleness.py --days 14
    python ops_scripts/ci/check_baseline_staleness.py --strict --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"

DEFAULT_STALE_DAYS = 30


def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        # Accept "YYYY-MM-DDTHH:MM:SS+00:00" or with trailing Z.
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def effective_timestamp(rec: dict[str, Any]) -> datetime | None:
    """Return the most recent ISO timestamp recorded on a baseline JSON."""
    candidates = [
        _parse_iso(rec.get("tightened_at")),
        _parse_iso(rec.get("last_run_at")),
        _parse_iso(rec.get("auto_promoted_at")),
        _parse_iso(rec.get("seeded_at")),
    ]
    valid = [c for c in candidates if c is not None]
    return max(valid) if valid else None


def collect_stale(
    baseline_dir: Path,
    *,
    threshold_days: int,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    """Return one dict per stale + non-zero baseline.

    Each row: { path, gate_id, count, age_days, effective_timestamp,
                auto_promoted_tier, tighten_count }.
    """
    now = now or datetime.now(timezone.utc)
    stale: list[dict[str, Any]] = []
    if not baseline_dir.exists():
        return stale
    for path in sorted(baseline_dir.glob("wiring_*_ratchet.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(rec, dict):
            continue
        count = int(rec.get("count", 0) or 0)
        if count <= 0:
            continue
        ts = effective_timestamp(rec)
        if ts is None:
            # Missing timestamp counts as maximally stale so it surfaces.
            age_days = 10**6
        else:
            age_days = int((now - ts).total_seconds() // 86400)
        if age_days < threshold_days:
            continue
        try:
            rel = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = path.as_posix()
        stale.append(
            {
                "path": rel,
                "gate_id": rec.get("gate_id", path.stem),
                "count": count,
                "age_days": age_days,
                "effective_timestamp": ts.isoformat() if ts else None,
                "auto_promoted_tier": rec.get("auto_promoted_tier"),
                "tighten_count": len(rec.get("tighten_history") or []),
            }
        )
    return stale


def format_human(stale: list[dict[str, Any]], threshold_days: int) -> str:
    if not stale:
        return f"[S_STALE] tier=W status=pass threshold_days={threshold_days} stale_ratchets=0"
    lines = [f"[S_STALE] tier=W status=warn threshold_days={threshold_days} stale_ratchets={len(stale)}"]
    width = max(len(r["gate_id"]) for r in stale)
    for r in sorted(stale, key=lambda x: -x["age_days"]):
        promoted = f" auto_promoted={r['auto_promoted_tier']}" if r["auto_promoted_tier"] else ""
        lines.append(
            f"  - {r['gate_id']:<{width}} "
            f"count={r['count']:<6} "
            f"age_days={r['age_days']:<4} "
            f"tightens={r['tighten_count']}"
            f"{promoted}"
        )
    lines.append(
        "REMEDIATION: investigate why these ratchets haven't moved. "
        "Either actively reduce the count (real cleanup) or document "
        "why the debt is accepted (ADR + waiver)."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_STALE_DAYS,
        help=f"stale threshold in days (default {DEFAULT_STALE_DAYS})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 on any stale non-zero baseline (default: warn, exit 0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON to stdout instead of a human summary",
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=BASELINE_DIR,
        help="override baseline directory (for tests)",
    )
    args = parser.parse_args(argv)

    stale = collect_stale(args.baseline_dir, threshold_days=args.days)
    if args.json:
        payload = {
            "gate_id": "S_STALE_baseline_age",
            "threshold_days": args.days,
            "stale_count": len(stale),
            "ratchets": stale,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(format_human(stale, args.days))

    if stale and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
