"""judge_calibration.py — Weekly calibration report for the Qwen judge surface.

Consumes ``JUDGE_DECISION`` markers from the capture queue at
``artifacts/capture/markers.jsonl`` (emitted by
:class:`agentic_core.L2_execution.healers.qwen_judge_gateway.QwenJudgeGateway`)
and produces a Markdown calibration report per ISO week.

Parallel in shape to the per-router calibration scripts under this folder
(see ``_router_calibration_base.py``) but reads the raw marker queue
directly because the dedicated judge SQLite ledger has not been
materialized yet. When that ledger lands, add a ``_read_ledger``
alternate source alongside :func:`_read_markers`; until then the queue
IS the source of truth.

Constitutional anchor:
  - §29 closed-loop router enforcement (judge surface analogue)
  - ``.codex/rules/judge-calibration-cadence.md`` — weekly human
    spot-check + unknown-budget watchdog.

Plan reference:
  - ``docs/archive/windsurf/legacy-tree/plans/apps-eval-qwen32b-rollout-b7c4d9.md`` Wave 1
    (P1.3).

Behavior contract:
  - Read ``artifacts/capture/markers.jsonl`` (fail-soft when missing).
  - Filter rows where ``marker_type == "JUDGE_DECISION"`` and parse the
    ``raw`` kv-payload.
  - Emit a Markdown report at
    ``docs/reports/calibration/judge/<YYYY-Www>.md`` with: total
    verdicts, acceptance rate, composite histogram (5 bins), fallback-
    reason distribution, per-app + per-rubric stats, unknown-budget
    watchdog.
  - Idempotent within a week: re-running overwrites the same ISO-week
    file.

Fail policy: exit 0 on success, 2 on internal I/O error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKERS_PATH = REPO_ROOT / "artifacts" / "capture" / "markers.jsonl"
REPORT_DIR = REPO_ROOT / "docs" / "reports" / "calibration" / "judge"

# Watchdog: when > this fraction of verdicts fall through to a fallback
# path (preflight/parse/exception), flag in the report. Per
# judge-calibration-cadence §"Unknown-budget watchdog".
UNKNOWN_BUDGET_FRACTION_CEILING: float = 0.20

# Composite histogram bin edges (5 bins over [0, 1]).
_COMPOSITE_BIN_EDGES: tuple[float, ...] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0001)

# Regex to parse the flat kv-payload inside a JUDGE_DECISION marker.
# Shape emitted by qwen_judge_gateway._emit_judge_decision_marker.
_KV_PATTERN = re.compile(r"(\w+)=([^,]+?)(?:,\s*|$)")


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass
class JudgeDecisionRow:
    """One parsed judge-decision marker row."""

    received_at: str
    app_name: str
    rubric_id: str
    rubric_hash: str
    accepted: bool
    composite: float
    model_used: str
    fallback_reason: str  # "none" when LLM call succeeded
    first_failed_gate: str  # "none" when no failure
    latency_ms: float

    @property
    def is_fallback(self) -> bool:
        """True when the verdict came from a fallback path."""
        return self.fallback_reason != "none"


@dataclass
class JudgeCalibrationSnapshot:
    """Aggregate snapshot over the filtered marker rows."""

    week: str
    total: int = 0
    accepted: int = 0
    fallback_counts: Counter[str] = field(default_factory=Counter)
    first_failed_gate_counts: Counter[str] = field(default_factory=Counter)
    composite_bins: list[int] = field(default_factory=lambda: [0] * 5)
    per_app: dict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    per_rubric: dict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    latencies_ms: list[float] = field(default_factory=list)

    @property
    def acceptance_rate(self) -> float:
        return self.accepted / self.total if self.total > 0 else 0.0

    @property
    def fallback_fraction(self) -> float:
        fallback_total = sum(
            v for k, v in self.fallback_counts.items() if k != "none"
        )
        return fallback_total / self.total if self.total > 0 else 0.0

    @property
    def unknown_budget_ok(self) -> bool:
        return self.fallback_fraction <= UNKNOWN_BUDGET_FRACTION_CEILING


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _parse_kv_payload(raw: str) -> dict[str, str]:
    """Parse the flat ``key=value, key=value`` payload of a marker line.

    The first ``JUDGE_DECISION: type=judge_decision, `` prefix is
    consumed by the marker regex upstream; by the time this helper runs,
    ``raw`` is the whole marker line. The parser tolerates the prefix
    and the trailing kv entries uniformly.
    """
    return {match.group(1): match.group(2).strip() for match in _KV_PATTERN.finditer(raw)}


def _coerce_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "accepted")


def _row_from_marker(marker_row: dict[str, Any]) -> JudgeDecisionRow | None:
    """Parse a single queue row into a :class:`JudgeDecisionRow`.

    Returns ``None`` when the row is not a ``JUDGE_DECISION`` or the
    payload is malformed.
    """
    if marker_row.get("marker_type") != "JUDGE_DECISION":
        return None
    raw = str(marker_row.get("raw", ""))
    if not raw:
        return None
    kv = _parse_kv_payload(raw)
    if kv.get("type") != "judge_decision":
        return None
    return JudgeDecisionRow(
        received_at=str(marker_row.get("received_at", "")),
        app_name=kv.get("app_name", "<unknown>"),
        rubric_id=kv.get("rubric_id", "<unknown>"),
        rubric_hash=kv.get("rubric_hash", "<unknown>"),
        accepted=_coerce_bool(kv.get("accepted", "false")),
        composite=_coerce_float(kv.get("composite", "0")),
        model_used=kv.get("model_used", "<unknown>"),
        fallback_reason=kv.get("fallback_reason", "none"),
        first_failed_gate=kv.get("first_failed_gate", "none"),
        latency_ms=_coerce_float(kv.get("latency_ms", "0")),
    )


def _read_markers(markers_path: Path) -> list[JudgeDecisionRow]:
    """Read + parse judge rows from the capture queue. Fail-soft."""
    if not markers_path.exists():
        return []
    rows: list[JudgeDecisionRow] = []
    with markers_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                marker_row = json.loads(stripped)
            except (json.JSONDecodeError, ValueError):
                continue
            parsed = _row_from_marker(marker_row)
            if parsed is not None:
                rows.append(parsed)
    return rows


def _composite_bin_index(value: float) -> int:
    """Return the histogram bin index for a composite score."""
    for idx in range(len(_COMPOSITE_BIN_EDGES) - 1):
        if _COMPOSITE_BIN_EDGES[idx] <= value < _COMPOSITE_BIN_EDGES[idx + 1]:
            return idx
    return len(_COMPOSITE_BIN_EDGES) - 2


def _aggregate(rows: list[JudgeDecisionRow], week: str) -> JudgeCalibrationSnapshot:
    """Build a calibration snapshot over a pre-filtered row list."""
    snap = JudgeCalibrationSnapshot(week=week)
    for row in rows:
        snap.total += 1
        if row.accepted:
            snap.accepted += 1
        snap.fallback_counts[row.fallback_reason] += 1
        snap.first_failed_gate_counts[row.first_failed_gate] += 1
        snap.composite_bins[_composite_bin_index(row.composite)] += 1
        snap.per_app[row.app_name][row.fallback_reason] += 1
        snap.per_rubric[row.rubric_id][row.fallback_reason] += 1
        snap.latencies_ms.append(row.latency_ms)
    return snap


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _fmt_pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(pct * (len(ordered) - 1)))))
    return ordered[idx]


def _render_report(snap: JudgeCalibrationSnapshot) -> str:
    """Render the Markdown report body."""
    lines: list[str] = []
    lines.append(f"# Judge Calibration — {snap.week}")
    lines.append("")
    lines.append(
        f"- **Total verdicts**: {snap.total}"
    )
    lines.append(
        f"- **Acceptance rate**: {_fmt_pct(snap.acceptance_rate)}"
    )
    lines.append(
        f"- **Fallback fraction**: {_fmt_pct(snap.fallback_fraction)}"
        f" (ceiling {_fmt_pct(UNKNOWN_BUDGET_FRACTION_CEILING)},"
        f" watchdog={'OK' if snap.unknown_budget_ok else 'BREACH'})"
    )
    if snap.latencies_ms:
        p50 = _percentile(snap.latencies_ms, 0.50)
        p95 = _percentile(snap.latencies_ms, 0.95)
        lines.append(f"- **Latency p50 / p95 (ms)**: {p50:.1f} / {p95:.1f}")
    lines.append("")

    lines.append("## Composite score histogram")
    lines.append("")
    lines.append("| Bin | Range | Count |")
    lines.append("|---|---|---|")
    for idx, count in enumerate(snap.composite_bins):
        lo = _COMPOSITE_BIN_EDGES[idx]
        hi = _COMPOSITE_BIN_EDGES[idx + 1]
        hi_render = "1.0" if idx == len(snap.composite_bins) - 1 else f"{hi:.2f}"
        lines.append(f"| {idx} | [{lo:.2f}, {hi_render}) | {count} |")
    lines.append("")

    lines.append("## Fallback reasons")
    lines.append("")
    if not snap.fallback_counts:
        lines.append("_No verdicts this week._")
    else:
        lines.append("| Reason | Count |")
        lines.append("|---|---|")
        for reason, count in snap.fallback_counts.most_common():
            lines.append(f"| `{reason}` | {count} |")
    lines.append("")

    lines.append("## First-failed-gate distribution")
    lines.append("")
    if not snap.first_failed_gate_counts:
        lines.append("_No verdicts this week._")
    else:
        lines.append("| Gate | Count |")
        lines.append("|---|---|")
        for gate, count in snap.first_failed_gate_counts.most_common():
            lines.append(f"| `{gate}` | {count} |")
    lines.append("")

    lines.append("## Per-app stats")
    lines.append("")
    if not snap.per_app:
        lines.append("_No verdicts this week._")
    else:
        lines.append("| App | Total | Fallbacks | Fallback % |")
        lines.append("|---|---|---|---|")
        for app, counter in sorted(snap.per_app.items()):
            app_total = sum(counter.values())
            app_fb = sum(v for k, v in counter.items() if k != "none")
            frac = (app_fb / app_total) if app_total else 0.0
            lines.append(f"| `{app}` | {app_total} | {app_fb} | {_fmt_pct(frac)} |")
    lines.append("")

    lines.append("## Per-rubric stats")
    lines.append("")
    if not snap.per_rubric:
        lines.append("_No verdicts this week._")
    else:
        lines.append("| Rubric | Total | Fallbacks | Fallback % |")
        lines.append("|---|---|---|---|")
        for rubric, counter in sorted(snap.per_rubric.items()):
            r_total = sum(counter.values())
            r_fb = sum(v for k, v in counter.items() if k != "none")
            frac = (r_fb / r_total) if r_total else 0.0
            lines.append(f"| `{rubric}` | {r_total} | {r_fb} | {_fmt_pct(frac)} |")
    lines.append("")

    lines.append("## Human spot-check sampling")
    lines.append("")
    lines.append(
        "Per ``.codex/rules/judge-calibration-cadence.md``, draw a "
        "stratified sample of 10 verdicts this week (split evenly across "
        "accepted / rejected / fallback buckets) for human verification. "
        "Record disagreements in the report's free-form notes and open a "
        "``NEXT_STEP:`` marker if the weekly human-agreement rate drops "
        "below 0.85."
    )
    lines.append("")
    lines.append("Notes: _(operator fills after spot-check)_")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def iso_week(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def _write_report(report_body: str, *, week: str, report_dir: Path) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    out_path = report_dir / f"{week}.md"
    out_path.write_text(report_body, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--markers-path",
        default=str(MARKERS_PATH),
        help="Override the markers.jsonl source path (default: artifacts/capture/markers.jsonl).",
    )
    parser.add_argument(
        "--report-dir",
        default=str(REPORT_DIR),
        help="Override the output directory (default: docs/reports/calibration/judge/).",
    )
    parser.add_argument(
        "--week",
        default=None,
        help="Override the ISO week tag (default: current UTC ISO week).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the report to stdout instead of writing a file.",
    )
    args = parser.parse_args(argv)

    try:
        rows = _read_markers(Path(args.markers_path))
    except OSError as exc:
        print(f"[judge_calibration] ERROR reading markers: {exc}", file=sys.stderr)
        return 2

    week = args.week or iso_week()
    snapshot = _aggregate(rows, week=week)
    report = _render_report(snapshot)

    if args.dry_run:
        sys.stdout.write(report)
        return 0

    try:
        out_path = _write_report(
            report, week=week, report_dir=Path(args.report_dir)
        )
    except OSError as exc:
        print(f"[judge_calibration] ERROR writing report: {exc}", file=sys.stderr)
        return 2

    print(f"[judge_calibration] wrote {out_path}")
    if not snapshot.unknown_budget_ok:
        print(
            f"[judge_calibration] WATCHDOG BREACH: fallback fraction "
            f"{snapshot.fallback_fraction:.3f} > ceiling "
            f"{UNKNOWN_BUDGET_FRACTION_CEILING:.3f}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
