#!/usr/bin/env python3
"""post_weekly_summary.py — Build a compact Notion-ready writeback payload (W4.2).

This module produces the JSON shape Cursor Agent pastes into a Notion `API-post-page`
or `API-patch-page` call. It does NOT make the Notion call itself — that is
deliberate, because:

  1. MCP serialization rules (constitutional §25) require Notion calls to be
     issued ONE PER CASCADE RESPONSE with no sibling tool calls. A scripted
     Python file invoking notion-mcp would bypass the harness's serialization
     audit. The right pattern is: this script emits the payload to disk, and
     Cursor Agent picks it up next session and dispatches it as the sole tool call.

  2. The auto-router is documented in AGENTS.md "Auto-Routing Rules" — when
     the weekly report changes, Cursor Agent should post the dashboard summary to
     the MCP Registry Notes field on the affected ledger rows. This script
     shapes the payload; the routing decision belongs to Cursor Agent.

Output:
    artifacts/calibration/weekly_summary_<YYYY-Www>.json — bounded to ~5KB,
    contains: {iso_week, summary_text, dashboard_table, dashboard_md,
               ledgers_with_signal: [...], generated_at}

CONSTITUTIONAL
    - Pure stdlib
    - UTF-8 I/O
    - Specific exceptions only
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.calibration.loop_metrics import (  # noqa: E402
    EVENTS_ADAPTER,
    compute_metrics as _lib_compute_metrics,
)
from tools.ledgers.schema_registry import LEDGER_REGISTRY  # noqa: E402

OUT_DIR = REPO_ROOT / "artifacts" / "calibration"
REPORTS_DIR = REPO_ROOT / "docs" / "reports" / "calibration"

_DEFAULT_BANDS: list[tuple[str, float, float]] = [
    ("[0.0, 0.2)", 0.0, 0.2),
    ("[0.2, 0.4)", 0.2, 0.4),
    ("[0.4, 0.6)", 0.4, 0.6),
    ("[0.6, 0.8)", 0.6, 0.8),
    ("[0.8, 1.0]", 0.8, 1.0001),
]


def _iso_week(dt: datetime) -> str:
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def _ledger_signal(spec) -> dict | None:
    """Return calibration signal dict for one ledger, or None when no data.

    Includes only the fields a Notion summary actually needs.
    """
    if not spec.db_path.exists():
        return None
    try:
        conn = sqlite3.connect(str(spec.db_path), timeout=5)
        try:
            conn.row_factory = sqlite3.Row
            rows = [
                dict(r)
                for r in conn.execute(
                    "SELECT status, score_band, score_numeric, prediction_json, "
                    "outcome_json, metadata_json FROM events"
                ).fetchall()
            ]
        finally:
            conn.close()
    except sqlite3.Error:
        return None
    if not rows:
        return None
    try:
        m = _lib_compute_metrics(rows, EVENTS_ADAPTER, bands=_DEFAULT_BANDS, ledger_name=spec.name)
    except (ValueError, TypeError, KeyError):
        return None
    miscal_bands = [
        {
            "band": b.label,
            "n": b.n,
            "rate": round(b.point, 3),
            "ci": [round(b.ci_low, 3), round(b.ci_high, 3)],
        }
        for b in m.calibration_curve
        if b.calibrated is False
    ]
    if m.bound_rows == 0 and not miscal_bands:
        return None
    return {
        "name": spec.name,
        "wave": spec.wave,
        "purpose": spec.purpose,
        "total_rows": m.total_rows,
        "bound_rows": m.bound_rows,
        "verdict_count": m.total_rows - m.unknown_precedent,
        "hit_count": m.precedent_hit_count,
        "miscalibrated_bands": miscal_bands,
        "sufficient_band_count": sum(1 for b in m.calibration_curve if b.sufficient),
    }


def _build_payload(now: datetime) -> dict:
    week = _iso_week(now)
    signals = [s for s in (_ledger_signal(spec) for spec in LEDGER_REGISTRY) if s is not None]

    # Compact summary text (≤500 chars) suitable for a Notion property.
    if not signals:
        summary_text = (
            f"Week {week}: no ledgers have bound rows yet. "
            "Calibration report rendered, awaiting first outcome bindings."
        )
    else:
        miscal_total = sum(len(s["miscalibrated_bands"]) for s in signals)
        if miscal_total == 0:
            health_phrase = "All ledgers calibrated within sample bounds."
        else:
            mc_names = sorted({s["name"] for s in signals if s["miscalibrated_bands"]})
            health_phrase = (
                f"{miscal_total} mis-calibrated band(s) across "
                f"{len(mc_names)} ledger(s): {', '.join(mc_names)}."
            )
        summary_text = (
            f"Week {week}: {len(signals)} ledger(s) reported. "
            f"{health_phrase} See docs/reports/calibration/{week}.md."
        )

    # Build dashboard markdown extract from latest weekly report if it exists.
    dashboard_md = ""
    report_path = REPORTS_DIR / f"{week}.md"
    if report_path.exists():
        try:
            content = report_path.read_text(encoding="utf-8")
            # Extract the Cross-Ledger Calibration Dashboard section only.
            match = re.search(
                r"(## Cross-Ledger Calibration Dashboard.*?)(?=^## )",
                content,
                re.DOTALL | re.MULTILINE,
            )
            if match:
                dashboard_md = match.group(1).strip()
        except OSError:
            pass

    return {
        "iso_week": week,
        "generated_at": now.isoformat(timespec="seconds"),
        "summary_text": summary_text[:500],
        "dashboard_md": dashboard_md,
        "ledgers_with_signal": signals,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None, help="Override output path")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    payload = _build_payload(now)

    out_path = Path(args.out) if args.out else OUT_DIR / f"weekly_summary_{payload['iso_week']}.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"[post_weekly_summary] wrote {out_path.relative_to(REPO_ROOT)} ({len(payload['ledgers_with_signal'])} ledgers w/ signal)"
    )
    print(f"  summary: {payload['summary_text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
