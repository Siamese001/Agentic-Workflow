#!/usr/bin/env python3
"""Wiring-CI dashboard — make ratchet baselines visible in one view.

Reads every ``wiring_*_ratchet.json`` under ``ops_scripts/ci/baselines/`` and
prints a single human-readable table showing:

    gate_id                        count  delta  last_from→to   days_since_change   auto-promoted   age_days
    -----------------------------  -----  -----  -------------  ------------------  --------------  --------
    G_REACH_l0_reachability        1993   0      (none)         0                   -                0

Also emits summary stats:
    * total ratchets, how many are 0-count, how many have tighten_history
    * sum of all counts (total "debt units" in ratchet territory)
    * oldest dormant ratchet (count > 0, never tightened)
    * any auto-promoted gates

Usage:
    python ops_scripts/ci/wiring_gate_dashboard.py
    python ops_scripts/ci/wiring_gate_dashboard.py --json
    python ops_scripts/ci/wiring_gate_dashboard.py --sort age
    python ops_scripts/ci/wiring_gate_dashboard.py --sort count
    python ops_scripts/ci/wiring_gate_dashboard.py --only-nonzero
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_DIR = REPO_ROOT / "ops_scripts" / "ci" / "baselines"


def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class DashRow:
    gate_id: str
    count: int
    age_days: int | None
    last_change_days: int | None
    last_from: int | None
    last_to: int | None
    tighten_count: int
    auto_promoted_tier: str | None
    zero_streak: int
    seeded_at: str | None
    path: str
    raw: dict[str, Any] = field(repr=False, default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "count": self.count,
            "age_days": self.age_days,
            "last_change_days": self.last_change_days,
            "last_from": self.last_from,
            "last_to": self.last_to,
            "tighten_count": self.tighten_count,
            "auto_promoted_tier": self.auto_promoted_tier,
            "zero_streak": self.zero_streak,
            "seeded_at": self.seeded_at,
            "path": self.path,
        }


def _row_from_record(
    path: Path, rec: dict[str, Any], now: datetime
) -> DashRow:
    count = int(rec.get("count", 0) or 0)
    seeded = _parse_iso(rec.get("seeded_at"))
    tightened = _parse_iso(rec.get("tightened_at"))
    last_run = _parse_iso(rec.get("last_run_at"))
    effective_ts = max(
        [t for t in (seeded, tightened, last_run) if t is not None],
        default=None,
    )
    age_days = (
        int((now - seeded).total_seconds() // 86400) if seeded else None
    )
    change_ts = tightened or effective_ts
    last_change_days = (
        int((now - change_ts).total_seconds() // 86400)
        if change_ts
        else None
    )
    history = rec.get("tighten_history") or []
    if isinstance(history, list) and history:
        last_entry = history[-1] or {}
        last_from = last_entry.get("from")
        last_to = last_entry.get("to")
    else:
        last_from = last_to = None
    try:
        rel_path = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel_path = path.as_posix()
    return DashRow(
        gate_id=str(rec.get("gate_id", path.stem)),
        count=count,
        age_days=age_days,
        last_change_days=last_change_days,
        last_from=last_from if isinstance(last_from, int) else None,
        last_to=last_to if isinstance(last_to, int) else None,
        tighten_count=len(history) if isinstance(history, list) else 0,
        auto_promoted_tier=rec.get("auto_promoted_tier"),
        zero_streak=int(rec.get("zero_run_streak", 0) or 0),
        seeded_at=rec.get("seeded_at"),
        path=rel_path,
        raw=rec,
    )


def collect_rows(
    baseline_dir: Path, *, now: datetime | None = None
) -> list[DashRow]:
    now = now or datetime.now(timezone.utc)
    rows: list[DashRow] = []
    if not baseline_dir.exists():
        return rows
    for path in sorted(baseline_dir.glob("wiring_*_ratchet.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(rec, dict):
            continue
        rows.append(_row_from_record(path, rec, now))
    return rows


def _sort_rows(rows: list[DashRow], sort_key: str) -> list[DashRow]:
    if sort_key == "count":
        return sorted(rows, key=lambda r: -r.count)
    if sort_key == "age":
        return sorted(rows, key=lambda r: -(r.age_days or 0))
    if sort_key == "change":
        return sorted(
            rows, key=lambda r: -(r.last_change_days or 0)
        )
    # default: by gate_id
    return sorted(rows, key=lambda r: r.gate_id)


def format_table(rows: list[DashRow]) -> str:
    if not rows:
        return "no wiring_*_ratchet.json baselines found"
    header = (
        "gate_id", "count", "tightens", "last_change",
        "age_days", "auto_promoted",
    )
    data = [header]
    for r in rows:
        data.append((
            r.gate_id,
            str(r.count),
            f"{r.tighten_count}"
            + (
                f" ({r.last_from}->{r.last_to})"
                if r.last_from is not None else ""
            ),
            f"{r.last_change_days}d" if r.last_change_days is not None else "?",
            f"{r.age_days}d" if r.age_days is not None else "?",
            r.auto_promoted_tier or "-",
        ))
    widths = [max(len(str(row[i])) for row in data) for i in range(len(header))]
    lines = []
    for idx, row in enumerate(data):
        lines.append("  ".join(
            str(v).ljust(widths[i]) for i, v in enumerate(row)
        ))
        if idx == 0:
            lines.append("  ".join("-" * w for w in widths))
    return "\n".join(lines)


def summarize(rows: list[DashRow]) -> dict[str, Any]:
    total = sum(r.count for r in rows)
    zero_count = sum(1 for r in rows if r.count == 0)
    with_history = sum(1 for r in rows if r.tighten_count > 0)
    promoted = [r.gate_id for r in rows if r.auto_promoted_tier]
    dormant = [
        r for r in rows
        if r.count > 0 and r.tighten_count == 0
    ]
    oldest_dormant = None
    if dormant:
        oldest = max(dormant, key=lambda r: r.age_days or 0)
        oldest_dormant = {
            "gate_id": oldest.gate_id,
            "count": oldest.count,
            "age_days": oldest.age_days,
        }
    return {
        "total_ratchets": len(rows),
        "zero_count_ratchets": zero_count,
        "ratchets_with_tighten_history": with_history,
        "total_debt_units": total,
        "auto_promoted_gates": promoted,
        "oldest_dormant_ratchet": oldest_dormant,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit JSON payload to stdout instead of a human table",
    )
    parser.add_argument(
        "--sort",
        choices=("gate_id", "count", "age", "change"),
        default="count",
        help="sort key for table rows (default: count)",
    )
    parser.add_argument(
        "--only-nonzero",
        action="store_true",
        help="hide ratchets whose count is 0",
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=BASELINE_DIR,
        help="override baseline directory (for tests)",
    )
    args = parser.parse_args(argv)

    rows = collect_rows(args.baseline_dir)
    if args.only_nonzero:
        rows = [r for r in rows if r.count > 0]
    rows = _sort_rows(rows, args.sort)
    summary = summarize(rows)

    if args.json:
        payload = {
            "summary": summary,
            "rows": [r.as_dict() for r in rows],
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(format_table(rows))
    print()
    print(
        f"SUMMARY: {summary['total_ratchets']} ratchets, "
        f"{summary['zero_count_ratchets']} at 0, "
        f"{summary['ratchets_with_tighten_history']} with history, "
        f"total_debt_units={summary['total_debt_units']}"
    )
    if summary["auto_promoted_gates"]:
        print(
            "AUTO-PROMOTED GATES: "
            + ", ".join(summary["auto_promoted_gates"])
        )
    dormant = summary["oldest_dormant_ratchet"]
    if dormant:
        print(
            f"OLDEST DORMANT (never tightened): {dormant['gate_id']} "
            f"count={dormant['count']} age_days={dormant['age_days']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
