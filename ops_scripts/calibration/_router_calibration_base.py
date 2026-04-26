"""_router_calibration_base.py — Shared core for the 10 per-router calibration scripts.

Each per-router script (e.g. router_l0_bandit_calibration.py) is a 30-line
adapter that declares its router metadata + nominal thresholds and delegates
report generation to ``RouterCalibrationReport`` defined here.

Constitutional anchor: §28 / closed-loop-router-enforcement.md.

Behavior contract:
- Reads ``artifacts/ledgers/router_<layer>_<router>.sqlite`` if it exists.
  This file will be materialized when the 10-router ledger expansion ships
  (W2 of the closed-loop router rollout). Until then, the script gracefully
  emits an ``awaiting telemetry`` report — still satisfying the CI gate's
  freshness check.
- Output path: ``docs/reports/calibration/routers/<layer>_<router>/<YYYY-Www>.md``
- Idempotent within a week: re-running overwrites the same ISO-week file.

Fail policy: stdout-error + exit code 2 on internal errors, 0 on success.
"""

from __future__ import annotations

import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGERS_DIR = REPO_ROOT / "artifacts" / "ledgers"
REPORT_BASE_DIR = REPO_ROOT / "docs" / "reports" / "calibration" / "routers"


# ---------------------------------------------------------------------------
# Public spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouterCalibrationSpec:
    """Per-router calibration spec consumed by ``RouterCalibrationReport``."""

    layer: str  # L0..L6
    router: str  # bandit, r5, c0, cascade, shape, reroute, uwg, hitl, promo, regret
    purpose: str  # one-line description for the report header
    nominal_thresholds: dict[str, float] = field(default_factory=dict)
    """Per-router nominal floors (e.g. {'wilson_lower_min': 0.60, 'n_min': 30})."""

    @property
    def key(self) -> str:
        return f"{self.layer}_{self.router}"

    @property
    def ledger_name(self) -> str:
        return f"router_{self.layer.lower()}_{self.router}"

    @property
    def ledger_path(self) -> Path:
        return LEDGERS_DIR / f"{self.ledger_name}.sqlite"

    @property
    def report_dir(self) -> Path:
        return REPORT_BASE_DIR / self.key


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def iso_week(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def _wilson_lower(successes: int, total: int, z: float = 1.96) -> float:
    """Wilson score lower confidence bound (one-sided variant inputs)."""
    if total <= 0:
        return 0.0
    p = successes / total
    denom = 1.0 + z * z / total
    centre = p + z * z / (2.0 * total)
    margin = z * ((p * (1.0 - p) / total + z * z / (4.0 * total * total)) ** 0.5)
    bound: float = (centre - margin) / denom
    return max(0.0, bound)


# ---------------------------------------------------------------------------
# Ledger read
# ---------------------------------------------------------------------------


@dataclass
class LedgerSnapshot:
    """Lightweight snapshot of a router ledger for calibration purposes."""

    available: bool
    total_rows: int = 0
    predicted_rows: int = 0
    bound_rows: int = 0
    success_rows: int = 0  # bound rows whose outcome JSON marks success
    band_distribution: dict[str, int] = field(default_factory=dict)
    latencies_ms: list[int] = field(default_factory=list)
    error: str | None = None


def _read_ledger(spec: RouterCalibrationSpec) -> LedgerSnapshot:
    """Read the router ledger, returning a snapshot. Fail-soft."""
    if not spec.ledger_path.exists():
        return LedgerSnapshot(available=False, error="ledger file not yet materialized")
    try:
        conn = sqlite3.connect(str(spec.ledger_path), timeout=5)
        try:
            # Detect schema: every intelligence ledger uses table 'events' per
            # tools.ledgers.schema_registry. If the schema differs, treat as
            # unavailable.
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            if "events" not in tables:
                return LedgerSnapshot(
                    available=False, error="ledger present but 'events' table missing"
                )
            total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            predicted = conn.execute(
                "SELECT COUNT(*) FROM events WHERE status='predicted'"
            ).fetchone()[0]
            bound = conn.execute(
                "SELECT COUNT(*) FROM events WHERE status='bound'"
            ).fetchone()[0]
            band_rows = conn.execute(
                "SELECT score_band, COUNT(*) FROM events "
                "WHERE score_band IS NOT NULL GROUP BY score_band"
            ).fetchall()
            latency_rows = conn.execute(
                "SELECT latency_ms FROM events WHERE latency_ms IS NOT NULL"
            ).fetchall()
            success_rows = conn.execute(
                "SELECT COUNT(*) FROM events "
                "WHERE status='bound' AND COALESCE(outcome_json,'') LIKE '%\"success\": true%'"
            ).fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return LedgerSnapshot(available=False, error=f"sqlite error: {exc}")

    return LedgerSnapshot(
        available=True,
        total_rows=total,
        predicted_rows=predicted,
        bound_rows=bound,
        success_rows=success_rows,
        band_distribution={(b or "unknown"): c for b, c in band_rows},
        latencies_ms=[int(r[0]) for r in latency_rows],
    )


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def _render_thresholds(spec: RouterCalibrationSpec) -> list[str]:
    if not spec.nominal_thresholds:
        return ["_(no nominal thresholds declared for this router)_"]
    rows = ["| Threshold | Nominal floor |", "|---|---:|"]
    for k, v in spec.nominal_thresholds.items():
        rows.append(f"| `{k}` | {v} |")
    return rows


def _render_metrics(spec: RouterCalibrationSpec, snap: LedgerSnapshot) -> list[str]:
    if not snap.available:
        return [
            "## Metrics",
            "",
            f"_Awaiting telemetry: {snap.error}._",
            "",
            "When the ledger is materialized and the first router decisions",
            "land, this section will populate with Wilson lower bound,",
            "per-band calibration, latency distribution, and drift versus",
            "the prior week.",
            "",
        ]

    if snap.total_rows == 0:
        return [
            "## Metrics",
            "",
            "_Ledger present but empty — awaiting first router decisions._",
            "",
        ]

    # Compute Wilson lower bound on success rate (bound rows only).
    wilson = _wilson_lower(snap.success_rows, snap.bound_rows) if snap.bound_rows else 0.0
    success_rate = (
        (snap.success_rows / snap.bound_rows) if snap.bound_rows else 0.0
    )

    # Latency stats.
    latency_line = "n/a"
    if snap.latencies_ms:
        sorted_l = sorted(snap.latencies_ms)
        mean = sum(sorted_l) / len(sorted_l)
        idx = max(0, int(len(sorted_l) * 0.95) - 1)
        p95 = sorted_l[idx]
        latency_line = f"mean={mean:.1f}ms p95={p95}ms (n={len(sorted_l)})"

    # Band distribution.
    bands = Counter(snap.band_distribution)
    band_line = ", ".join(f"{k}={v}" for k, v in bands.most_common(5)) or "none"

    return [
        "## Metrics",
        "",
        f"- **Total rows**: {snap.total_rows} ({snap.predicted_rows} predicted-only, "
        f"{snap.bound_rows} bound)",
        f"- **Success rate**: {success_rate:.3f} ({snap.success_rows}/{snap.bound_rows})",
        f"- **Wilson lower bound** (95% one-sided, z=1.96): {wilson:.3f}",
        f"- **Latency**: {latency_line}",
        f"- **Score bands**: {band_line}",
        "",
    ]


def _render_drift(spec: RouterCalibrationSpec, current_week: str) -> list[str]:
    """Compare against the most recent prior weekly report, if one exists."""
    prior = _find_prior_report(spec, current_week)
    if prior is None:
        return [
            "## Drift",
            "",
            "_No prior weekly report on disk — drift baseline established this week._",
            "",
        ]
    return [
        "## Drift",
        "",
        f"- **Prior report**: `{prior.relative_to(REPO_ROOT).as_posix()}`",
        "- **Comparison**: see prior report's Metrics block. Drift detector",
        "  hooks under ``ops_scripts/calibration/calibration_drift_detector.py``",
        "  pick this up automatically once the ledger is populated.",
        "",
    ]


def _find_prior_report(spec: RouterCalibrationSpec, current_week: str) -> Path | None:
    if not spec.report_dir.is_dir():
        return None
    candidates = sorted(
        (p for p in spec.report_dir.glob("*.md") if p.stem != current_week),
        key=lambda p: p.stem,
    )
    return candidates[-1] if candidates else None


def render_report(spec: RouterCalibrationSpec, *, now: datetime | None = None) -> str:
    """Render a complete weekly calibration report for the given router."""
    now = now or datetime.now(timezone.utc)
    week = iso_week(now)
    snap = _read_ledger(spec)

    lines: list[str] = []
    lines.append(f"# Router Calibration — `{spec.key}` — {week}")
    lines.append("")
    lines.append(f"**Layer**: {spec.layer}  ")
    lines.append(f"**Router**: `{spec.router}`  ")
    lines.append(f"**Purpose**: {spec.purpose}  ")
    lines.append(f"**Generated**: {now.isoformat(timespec='seconds')}  ")
    lines.append(f"**Ledger**: `{spec.ledger_path.relative_to(REPO_ROOT).as_posix()}`  ")
    lines.append("")
    lines.append("Constitutional anchor: §28. Rule: `closed-loop-router-enforcement.md`.")
    lines.append("")

    lines.append("## Nominal Thresholds")
    lines.append("")
    lines.extend(_render_thresholds(spec))
    lines.append("")

    lines.extend(_render_metrics(spec, snap))
    lines.extend(_render_drift(spec, week))

    lines.append("## Sunset Tracking")
    lines.append("")
    lines.append(
        "Per-router enforcement auto-retires after 90 consecutive days of zero "
        "violations + 4 in-band weekly reports + a successor ADR. See "
        "`closed-loop-router-enforcement.md` §Sunset."
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point used by the 10 thin per-router scripts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GenerationResult:
    """Outcome of one report generation. Returned for orchestrator/test use."""

    spec_key: str
    output_path: Path
    bytes_written: int
    available: bool


def generate(spec: RouterCalibrationSpec, *, now: datetime | None = None) -> GenerationResult:
    """Render and write the report. Returns a GenerationResult."""
    now = now or datetime.now(timezone.utc)
    week = iso_week(now)
    out_dir = spec.report_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{week}.md"
    content = render_report(spec, now=now)
    out_path.write_text(content, encoding="utf-8")
    snap = _read_ledger(spec)
    return GenerationResult(
        spec_key=spec.key,
        output_path=out_path,
        bytes_written=len(content),
        available=snap.available,
    )


def cli(spec: RouterCalibrationSpec, argv: list[str] | None = None) -> int:
    """Entry point used by per-router scripts. Returns exit code."""
    _ = argv  # currently no flags; future-proofed for --week, --out
    try:
        result = generate(spec)
    except (OSError, ValueError) as exc:
        print(f"[router-calibration:{spec.key}] FAILED: {exc}", file=sys.stderr)
        return 2
    rel = result.output_path.relative_to(REPO_ROOT).as_posix()
    flag = "live" if result.available else "awaiting"
    print(
        f"[router-calibration:{spec.key}] wrote {rel} "
        f"({result.bytes_written} bytes, {flag})"
    )
    return 0
