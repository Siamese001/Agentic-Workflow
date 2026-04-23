#!/usr/bin/env python3
"""CI gate: check_snapshot_has_mvs.py — ADG snapshot graph-layer completeness.

Constitutional §22 enforcement (snapshot side).

`check_graph_layer_evidence.py` enforces that T2/T3 refactoring PLANS cite
materialized views (mv_*), P-views (v_p*), and semantic edges. This gate is
the symmetric enforcement on the ARTIFACT: it fails if the latest
`adg_indexed_*.sqlite` snapshot ships without its graph-layer overlay
(MVs, P-views, infra wiring views).

Background / why this gate exists
---------------------------------
Prior to plan adg-pipeline-e2e-5287a1 W1 (commit 9fb93f698c), enrichment
(`_enrich_infra_views` + `_materialize_adg_views`) ran AFTER Tier-2 blocking
gates in `tools/generate/generate_full_adg.py`. Any sys.exit(1) from P0/P1/
dead-import gates stranded the committed snapshot without MVs, silently
breaking §22 for every downstream consumer. W1 reordered enrichment before
the gates; THIS gate (W2) ensures no future edit re-introduces the defect.

Thresholds
----------
    MIN_MV_TABLES    = 30   (Phase A..E produce 51; 30 is the floor)
    MIN_PVIEWS       = 3    (v_p0_* + v_p1_* + v_p2_* + v_p3_*; 15 today)
    MIN_INFRA_VIEWS  = 1    (v_infra_violations_summary + p-views)

Run modes
---------
    $ python ops_scripts/ci/check_snapshot_has_mvs.py
        Check the most-recent adg_indexed_*.sqlite under artifacts/adg/.

    $ python ops_scripts/ci/check_snapshot_has_mvs.py path/to/snapshot.sqlite
        Check a specific snapshot file.

    Env flags:
        ADG_SNAPSHOT_MV_GATE_WARN=1 — warn instead of fail (soft mode)

Exit codes
----------
    0 — snapshot satisfies thresholds
    1 — snapshot missing graph-layer overlay (or soft-mode warn)
    2 — runner error (no snapshot found, sqlite read error, etc.)

References
----------
    - Constitutional §22 (graph-layer evidence)
    - .windsurf/plans/adg-pipeline-e2e-5287a1.md (W1 reorder + W2 this gate)
    - .windsurf/rules/adg-graph-layer-enforcement.md
"""

from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = ROOT / "artifacts" / "adg"
LOG_DIR = ROOT / "artifacts" / "windsurf"
LOG_FILE = LOG_DIR / "snapshot_mv_violations.jsonl"

MIN_MV_TABLES = 30
MIN_PVIEWS = 3
MIN_INFRA_VIEWS = 1


def _resolve_snapshot(argv_path: str | None) -> Path:
    """Return the snapshot file to inspect.

    If argv_path is given, resolve it. Otherwise pick the most-recently
    modified adg_indexed_*.sqlite under artifacts/adg/.
    """
    if argv_path:
        p = Path(argv_path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"snapshot not found: {p}")
        return p

    pattern = str(ADG_DIR / "adg_indexed_*.sqlite")
    candidates = sorted(glob.glob(pattern), key=os.path.getmtime)
    if not candidates:
        raise FileNotFoundError(
            f"no adg_indexed_*.sqlite under {ADG_DIR}; regenerate via `python tools/generate_full_adg.py`",
        )
    return Path(candidates[-1])


def _classify_objects(snapshot: Path) -> dict[str, list[str]]:
    """Return {'mv': [...], 'pview': [...], 'infra': [...], 'base': [...]}."""
    with sqlite3.connect(str(snapshot)) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name",
        ).fetchall()
    names = [r[0] for r in rows]
    mv = sorted(n for n in names if n.startswith("mv_"))
    pview = sorted(n for n in names if n.startswith("v_p"))
    infra = sorted(
        n for n in names if ("infra" in n.lower() or "wiring" in n.lower()) and not n.startswith("mv_")
    )
    known = set(mv) | set(pview) | set(infra)
    base = sorted(n for n in names if n not in known)
    return {"mv": mv, "pview": pview, "infra": infra, "base": base}


def _log_violation(snapshot: Path, counts: dict[str, int], reasons: list[str]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    rec = {
        "snapshot": snapshot.name,
        "snapshot_path": str(snapshot),
        "counts": counts,
        "thresholds": {
            "min_mv": MIN_MV_TABLES,
            "min_pview": MIN_PVIEWS,
            "min_infra": MIN_INFRA_VIEWS,
        },
        "reasons": reasons,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def main(argv: list[str]) -> int:
    try:
        snapshot = _resolve_snapshot(argv[1] if len(argv) > 1 else None)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 2
    except (OSError, ValueError) as exc:
        print(f"[ERROR] snapshot resolve failed: {exc}")
        return 2

    try:
        groups = _classify_objects(snapshot)
    except sqlite3.Error as exc:
        print(f"[ERROR] sqlite read failed on {snapshot.name}: {exc}")
        return 2

    counts = {k: len(v) for k, v in groups.items()}
    reasons: list[str] = []
    if counts["mv"] < MIN_MV_TABLES:
        reasons.append(
            f"mv_* count {counts['mv']} < MIN_MV_TABLES={MIN_MV_TABLES}",
        )
    if counts["pview"] < MIN_PVIEWS:
        reasons.append(
            f"v_p* count {counts['pview']} < MIN_PVIEWS={MIN_PVIEWS}",
        )
    if counts["infra"] < MIN_INFRA_VIEWS:
        reasons.append(
            f"infra view count {counts['infra']} < MIN_INFRA_VIEWS={MIN_INFRA_VIEWS}",
        )

    header = "=" * 72
    print(header)
    print("ADG SNAPSHOT GRAPH-LAYER COMPLETENESS — Constitutional §22")
    print(header)
    print(f"snapshot: {snapshot.name}")
    print(f"mv_*    : {counts['mv']:>4} (min {MIN_MV_TABLES})")
    print(f"v_p*    : {counts['pview']:>4} (min {MIN_PVIEWS})")
    print(f"infra   : {counts['infra']:>4} (min {MIN_INFRA_VIEWS})")
    print(f"base    : {counts['base']:>4}")
    print(header)

    if not reasons:
        print("[PASS] snapshot contains full graph-layer overlay")
        return 0

    for r in reasons:
        print(f"[FAIL] {r}")
    print(
        "\nREMEDIATION:\n"
        "  1. Regenerate ADG: `python tools/generate_full_adg.py`\n"
        "  2. Verify `_enrich_infra_views` + `_materialize_adg_views` run\n"
        "     BEFORE P0/P1/dead-import gates in tools/generate/generate_full_adg.py\n"
        "     (plan adg-pipeline-e2e-5287a1 W1, commit 9fb93f698c).\n"
        "  3. See: .windsurf/rules/adg-graph-layer-enforcement.md\n",
    )
    print(f"Log: {LOG_FILE.relative_to(ROOT)}")
    _log_violation(snapshot, counts, reasons)

    warn_mode = os.environ.get("ADG_SNAPSHOT_MV_GATE_WARN", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if warn_mode:
        print("[WARN] ADG_SNAPSHOT_MV_GATE_WARN=1 — exiting 0 (soft mode)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
