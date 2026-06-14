#!/usr/bin/env python3
"""author_gate_calibrator.py — Fit isotonic regression over Author-Gate outcomes.

Plan: `docs/archive/windsurf/legacy-tree/plans/author-gate-hardening-a3b8f2.md` W2.P2.2 + W2.P2.3.
W4 (author-gate-feedback-loop-d4e8f1): degenerate-label NOOP, disputed-derived-row
exclusion, snapshot lineage, optional strict outcome-schema guard.

Reads (decision, outcome) pairs from `refactor_decision_ledger.sqlite` grouped
by `decision_type`. For each class with ≥30 closed outcomes, fits an isotonic
regression (Pool-Adjacent-Violators algorithm, hand-rolled — no sklearn) mapping
`confidence_top` → observed success rate. Writes:

1. `decisions.confidence_calibrated` — per-row calibrated score
2. `decisions.calibrator_version` — stamp for the fit that produced it
3. `decision_calibration_snapshots` — one row per (decision_type, fit version)
   carrying Brier score, ECE (10-bin), reliability diagram, isotonic points
4. `artifacts/author_gate/reliability_<YYYY-Www>.json` — human-readable report

Success metric:
    outcome_success = 1 if (promote_to_pattern = 1 AND rollback_required = 0
                            AND regression_found = 0)
                      else 0

Cold-start: classes with <30 closed outcomes get NO fit; their decisions keep
NULL `confidence_calibrated` and carry a COLD_START tag in the snapshot.

Degenerate labels (W4): all-success or all-failure (or below min positive/negative
counts) → ``NOOP_DEGENERATE_LABELS`` — no isotonic fit, no persistence of fake
calibrated scores. Rows with ``bind_disputed`` or ``outcome_bind_tier='disputed_bind'``
are excluded from the training set when those columns exist.

Usage:
    python ops_scripts/calibration/author_gate_calibrator.py --dry-run
    python ops_scripts/calibration/author_gate_calibrator.py --apply
    python ops_scripts/calibration/author_gate_calibrator.py --apply --min-n 10   # override threshold

Fail policy: SOFT — per-class failures emit WARN and continue; exit 1 only when
ALL classes fail or DB is unreadable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REFACTOR_DECISION_LEDGER_DB
REPORT_DIR = REPO_ROOT / "artifacts" / "author_gate"

DEFAULT_MIN_N = 30
DEFAULT_CALIBRATOR_PREFIX = "iso_v1"

# W4: bump when training policy / exclusions / lineage contract changes.
CALIBRATOR_POLICY_VERSION = "author-gate-calibrator-w4-20260517"

NOOP_DEGENERATE_LABELS = "NOOP_DEGENERATE_LABELS"
NOOP_STALE_SCHEMA = "NOOP_STALE_SCHEMA"

_REQUIRED_OUTCOME_COLUMNS = frozenset(
    {"decision_id", "promote_to_pattern", "rollback_required", "regression_found"}
)


# --------------------------------------------------------------------------
# Isotonic regression — Pool-Adjacent-Violators (PAV)
# --------------------------------------------------------------------------


def isotonic_fit(
    xs: Sequence[float], ys: Sequence[float]
) -> list[tuple[float, float]]:
    """Fit a non-decreasing step function y = f(x) via PAV.

    Returns a list of (x, y) anchor points sorted by x. Interpolation between
    anchors is piecewise linear (see ``isotonic_apply``).

    Handles:
      - duplicate x values (averages ys at the same x first)
      - empty / single-point inputs (returns the input as-is)

    Algorithm: classic Pool-Adjacent-Violators — O(n) after sort.
    """
    if not xs:
        return []
    pairs = sorted(zip(xs, ys), key=lambda p: p[0])
    # Collapse duplicate xs by averaging their ys (standard isotonic input prep).
    collapsed: list[tuple[float, float, int]] = []  # (x, y_sum, count)
    for x, y in pairs:
        if collapsed and abs(collapsed[-1][0] - x) < 1e-12:
            _, ys_sum, cnt = collapsed[-1]
            collapsed[-1] = (x, ys_sum + y, cnt + 1)
        else:
            collapsed.append((x, float(y), 1))
    # Convert to (x, y_mean, weight)
    blocks: list[list[float]] = [[x, ys_sum / cnt, float(cnt)] for x, ys_sum, cnt in collapsed]

    # PAV: iterate, merging any block with its predecessor when monotonicity fails.
    i = 1
    while i < len(blocks):
        if blocks[i][1] < blocks[i - 1][1]:
            # Merge i and i-1 weighted by count
            w1 = blocks[i - 1][2]
            w2 = blocks[i][2]
            merged_y = (blocks[i - 1][1] * w1 + blocks[i][1] * w2) / (w1 + w2)
            merged_x = (blocks[i - 1][0] * w1 + blocks[i][0] * w2) / (w1 + w2)
            blocks[i - 1] = [merged_x, merged_y, w1 + w2]
            blocks.pop(i)
            if i > 1:
                i -= 1
        else:
            i += 1
    return [(round(b[0], 6), round(b[1], 6)) for b in blocks]


def isotonic_apply(points: list[tuple[float, float]], x: float) -> float:
    """Apply a fit to a new x via piecewise-linear interpolation + clipping."""
    if not points:
        return x  # identity fallback
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    for i in range(1, len(points)):
        xi, yi = points[i]
        if x <= xi:
            xp, yp = points[i - 1]
            if xi == xp:
                return yi
            t = (x - xp) / (xi - xp)
            return yp + t * (yi - yp)
    return points[-1][1]


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------


def brier_score(scores: Sequence[float], outcomes: Sequence[int]) -> float:
    """Mean squared error between calibrated score and binary outcome."""
    if not scores:
        return 0.0
    return sum((s - o) ** 2 for s, o in zip(scores, outcomes)) / len(scores)


def expected_calibration_error(
    scores: Sequence[float], outcomes: Sequence[int], n_bins: int = 10
) -> tuple[float, list[dict[str, float]]]:
    """ECE + the reliability-diagram bins.

    Each bin carries: lo, hi, n, mean_score, success_rate, gap_abs.
    ECE is Σ (n_bin / N) × |mean_score_bin − success_rate_bin|.
    """
    if not scores:
        return 0.0, []
    bins: list[dict[str, float]] = []
    total = len(scores)
    for b in range(n_bins):
        lo = b / n_bins
        hi = (b + 1) / n_bins
        idx = [i for i, s in enumerate(scores) if (lo <= s < hi) or (hi == 1.0 and s == 1.0)]
        if not idx:
            bins.append(
                {"lo": round(lo, 4), "hi": round(hi, 4), "n": 0, "mean_score": 0.0,
                 "success_rate": 0.0, "gap_abs": 0.0}
            )
            continue
        bin_scores = [scores[i] for i in idx]
        bin_outcomes = [outcomes[i] for i in idx]
        mean_s = sum(bin_scores) / len(bin_scores)
        sr = sum(bin_outcomes) / len(bin_outcomes)
        bins.append(
            {"lo": round(lo, 4), "hi": round(hi, 4), "n": len(idx),
             "mean_score": round(mean_s, 4), "success_rate": round(sr, 4),
             "gap_abs": round(abs(mean_s - sr), 4)}
        )
    ece = sum((b["n"] / total) * b["gap_abs"] for b in bins if b["n"])
    return round(ece, 4), bins


# --------------------------------------------------------------------------
# Data access
# --------------------------------------------------------------------------


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def _outcomes_schema_ready(conn: sqlite3.Connection) -> bool:
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(decision_outcomes)").fetchall()}
    except sqlite3.Error:
        return False
    return _REQUIRED_OUTCOME_COLUMNS <= cols


def _outcome_dispute_exclusion_sql(conn: sqlite3.Connection) -> str:
    """Exclude disputed binds from calibration training when columns exist."""
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(decision_outcomes)").fetchall()}
    except sqlite3.Error:
        return ""
    parts: list[str] = []
    if "bind_disputed" in cols:
        parts.append("COALESCE(o.bind_disputed, 0) = 0")
    if "outcome_bind_tier" in cols:
        parts.append("LOWER(COALESCE(o.outcome_bind_tier, '')) != 'disputed_bind'")
    if not parts:
        return ""
    return " AND " + " AND ".join(parts)


def _maybe_add_lineage_column(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "decision_calibration_snapshots"):
        return
    names = {r[1] for r in conn.execute("PRAGMA table_info(decision_calibration_snapshots)").fetchall()}
    if "lineage_json" in names:
        return
    try:
        conn.execute("ALTER TABLE decision_calibration_snapshots ADD COLUMN lineage_json TEXT")
        conn.commit()
    except sqlite3.Error:
        pass


def _git_sha_short() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=6,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.strip()[:12]
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def _dataset_digest(pairs: list[tuple[str, float, int]]) -> str:
    body = "\n".join(f"{did}\t{x}\t{y}" for did, x, y in sorted(pairs, key=lambda p: p[0]))
    return hashlib.sha256(body.encode()).hexdigest()[:16]


def _build_lineage_json(
    pairs: list[tuple[str, float, int]],
    *,
    decision_type: str,
    min_positive: int,
    min_negative: int,
    dispute_filter_active: bool,
) -> str:
    ys = [p[2] for p in pairs]
    payload = {
        "policy_version": CALIBRATOR_POLICY_VERSION,
        "dataset_digest_sha256_16": _dataset_digest(pairs),
        "code_version_git": _git_sha_short(),
        "utc_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "decision_type": decision_type,
        "n_rows": len(pairs),
        "label_mean": round(sum(ys) / len(ys), 6) if pairs else None,
        "min_positive_labels": min_positive,
        "min_negative_labels": min_negative,
        "split_policy": "full_dataset_isotonic_v1",
        "leakage_guard": {
            "method": "none",
            "note": "No temporal holdout in v1; advisory / analytics-only calibration.",
        },
        "disputed_training_rows_excluded": dispute_filter_active,
    }
    return json.dumps(payload, sort_keys=True)


def _load_closed_outcomes(conn: sqlite3.Connection, decision_type: str) -> list[tuple[str, float, int]]:
    """Return [(decision_id, confidence_top, success_0_or_1), ...].

    Success = promote_to_pattern=1 AND rollback_required=0 AND regression_found=0.
    """
    filt = _outcome_dispute_exclusion_sql(conn)
    rows = conn.execute(
        f"""
        SELECT d.decision_id, d.confidence_top,
               COALESCE(o.promote_to_pattern, 0) AS prom,
               COALESCE(o.rollback_required, 0) AS roll,
               COALESCE(o.regression_found, 0) AS reg
          FROM decisions d
          JOIN decision_outcomes o USING (decision_id)
         WHERE d.decision_type = ?
           AND d.confidence_top IS NOT NULL
           {filt}
        """,
        (decision_type,),
    ).fetchall()
    pairs: list[tuple[str, float, int]] = []
    for did, ctop, prom, roll, reg in rows:
        if ctop is None:
            continue
        success = 1 if (prom == 1 and roll == 0 and reg == 0) else 0
        pairs.append((did, float(ctop), success))
    return pairs


def _distinct_decision_types(conn: sqlite3.Connection) -> list[str]:
    return [r[0] for r in conn.execute(
        "SELECT DISTINCT decision_type FROM decisions WHERE decision_type IS NOT NULL"
    ).fetchall()]


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def _make_version() -> str:
    d = datetime.now(timezone.utc)
    yw = d.strftime("%Yw%V")
    return f"{DEFAULT_CALIBRATOR_PREFIX}_{yw}"


def fit_class(
    conn: sqlite3.Connection,
    decision_type: str,
    version: str,
    min_n: int,
    *,
    apply: bool,
    min_positive: int,
    min_negative: int,
    strict_schema: bool,
) -> dict[str, object]:
    """Fit one decision_type. Returns a summary dict for the report."""
    dispute_sql = _outcome_dispute_exclusion_sql(conn)
    dispute_active = bool(dispute_sql)
    schema_ok = _outcomes_schema_ready(conn)

    summary: dict[str, object] = {
        "decision_type": decision_type,
        "n_outcomes": 0,
        "version": version,
        "fitted": False,
        "cold_start": False,
    }

    if strict_schema and not schema_ok:
        summary["noop_reason"] = NOOP_STALE_SCHEMA
        summary["reason"] = "required decision_outcomes columns missing (--strict-schema)"
        return summary

    data = _load_closed_outcomes(conn, decision_type)
    n = len(data)
    summary["n_outcomes"] = n
    summary["calibrator_policy_version"] = CALIBRATOR_POLICY_VERSION

    if n < min_n:
        summary["cold_start"] = True
        summary["reason"] = f"insufficient_outcomes (n={n} < min_n={min_n})"
        return summary

    ys = [p[2] for p in data]
    n_succ = int(sum(ys))
    n_fail = n - n_succ
    if n_succ < min_positive or n_fail < min_negative:
        summary["noop_reason"] = NOOP_DEGENERATE_LABELS
        summary["reason"] = (
            f"degenerate_binary_labels (success={n_succ}, failure={n_fail}; "
            f"need min_positive={min_positive}, min_negative={min_negative})"
        )
        summary["n_success_labels"] = n_succ
        summary["n_failure_labels"] = n_fail
        return summary

    xs = [p[1] for p in data]
    points = isotonic_fit(xs, ys)
    calibrated = [isotonic_apply(points, x) for x in xs]
    brier = round(brier_score(calibrated, ys), 4)
    ece, bins = expected_calibration_error(calibrated, ys, n_bins=10)
    lineage_json = _build_lineage_json(
        data,
        decision_type=decision_type,
        min_positive=min_positive,
        min_negative=min_negative,
        dispute_filter_active=dispute_active,
    )
    summary.update({
        "fitted": True,
        "brier": brier,
        "ece": ece,
        "n_anchors": len(points),
        "reliability_bins": len(bins),
        "n_success_labels": n_succ,
        "n_failure_labels": n_fail,
        "lineage_json": lineage_json,
    })

    if not apply:
        return summary

    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        conn.execute(
            """INSERT INTO decision_calibration_snapshots
                   (created_at, calibrator_version, decision_type, n_outcomes,
                    brier_score, ece_score, reliability_json, isotonic_points_json,
                    lineage_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                created,
                version,
                decision_type,
                n,
                brier,
                ece,
                json.dumps(bins),
                json.dumps(points),
                lineage_json,
            ),
        )
    except sqlite3.OperationalError:
        conn.execute(
            """INSERT INTO decision_calibration_snapshots
                   (created_at, calibrator_version, decision_type, n_outcomes,
                    brier_score, ece_score, reliability_json, isotonic_points_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                created,
                version,
                decision_type,
                n,
                brier,
                ece,
                json.dumps(bins),
                json.dumps(points),
            ),
        )

    updates = [
        (round(cal, 4), version, did)
        for (did, _x, _y), cal in zip(data, calibrated)
    ]
    for i in range(0, len(updates), 500):
        batch = updates[i : i + 500]
        conn.executemany(
            "UPDATE decisions SET confidence_calibrated = ?, calibrator_version = ? "
            "WHERE decision_id = ?",
            batch,
        )
    conn.commit()
    return summary


def _class_terminal_ok(s: dict[str, object]) -> bool:
    return bool(
        s.get("fitted")
        or s.get("cold_start")
        or s.get("noop_reason") in (NOOP_DEGENERATE_LABELS, NOOP_STALE_SCHEMA)
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--db", default=str(DB_PATH))
    p.add_argument("--apply", action="store_true", help="Persist results; without this, dry-run")
    p.add_argument("--dry-run", action="store_true", help="(default) compute but do not persist")
    p.add_argument("--min-n", type=int, default=DEFAULT_MIN_N)
    p.add_argument("--min-positive", type=int, default=1, help="Minimum success labels per class")
    p.add_argument("--min-negative", type=int, default=1, help="Minimum failure labels per class")
    p.add_argument(
        "--strict-schema",
        action="store_true",
        help="NOOP classes when decision_outcomes is missing required columns",
    )
    p.add_argument("--version", default=None, help="Calibrator version stamp (default: iso_v1_<YYYYwWW>)")
    args = p.parse_args(argv)

    if args.apply and args.dry_run:
        print("[calibrator] error: --apply and --dry-run are mutually exclusive", file=sys.stderr)
        return 2
    apply = args.apply and not args.dry_run
    if args.min_positive < 1 or args.min_negative < 1:
        print("[calibrator] error: --min-positive and --min-negative must be >= 1", file=sys.stderr)
        return 2

    db = Path(args.db)
    if not db.exists():
        print(f"[calibrator] ledger not found: {db}", file=sys.stderr)
        return 2

    version = args.version or _make_version()

    conn = sqlite3.connect(str(db), timeout=15)
    try:
        if apply:
            _maybe_add_lineage_column(conn)
        classes = _distinct_decision_types(conn)
        summaries: list[dict[str, object]] = []
        for dt in classes:
            summaries.append(
                fit_class(
                    conn,
                    dt,
                    version,
                    args.min_n,
                    apply=apply,
                    min_positive=args.min_positive,
                    min_negative=args.min_negative,
                    strict_schema=args.strict_schema,
                )
            )
    finally:
        conn.close()

    # Write weekly report artifact
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    yw = datetime.now(timezone.utc).strftime("%Yw%V")
    out_path = REPORT_DIR / f"reliability_{yw}.json"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "calibrator_policy_version": CALIBRATOR_POLICY_VERSION,
        "version": version,
        "apply": apply,
        "min_n": args.min_n,
        "min_positive": args.min_positive,
        "min_negative": args.min_negative,
        "strict_schema": args.strict_schema,
        "classes": summaries,
    }
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(out_path), "applied": apply, "classes": len(summaries)}))
    fitted_any = any(s.get("fitted") for s in summaries)
    if not fitted_any and not all(_class_terminal_ok(s) for s in summaries):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
