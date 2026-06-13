"""loop_metrics.py — Ledger-agnostic prediction→outcome calibration primitives.

Used by:
    - docs/archive/windsurf/legacy-tree/governance_scripts/generate_calibration_report.py (Author-Gate decision ledger)
    - ops_scripts/calibration/ledger_weekly_report.py (10 intelligence ledgers)
    - any future calibration consumer (tests, ad-hoc analysis, dashboards)

The core problem all 11 calibration loops share:
    1. Predictions are recorded with a confidence score / band / verdict.
    2. Outcomes arrive later (success | rework | rollback | undecided | unbound).
    3. We need three things from this:
        a. precedent-hit rate (how often was prediction informed by past data?)
        b. precedent × outcome correlation (does following precedent help?)
        c. calibration curve binned by confidence (are 0.85s actually 85%?)
    4. Reports must report "insufficient sample" honestly when N is too low,
       not point-estimate at 0/0 or 1/1.

This module provides:
    - Wilson score 95% confidence interval (small-N safe).
    - Histogram bucketization with insufficient-sample gating.
    - Pre-defined band layouts (CONFIDENCE_BANDS, P_BAND_LAYOUT).
    - A LedgerAdapter dataclass that lets call sites describe their ledger
      shape without subclassing — pure functional dispatch.

CONSTITUTIONAL
    - Pure stdlib (math + statistics)
    - No I/O at module scope
    - Specific exceptions only (never bare except)
    - All numeric primitives total: clamp denominators, return sentinel on n=0
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Sequence

# ---------------------------------------------------------------------------
# Constants — SSOT for thresholds; keep in sync with author-gate-decision-points.md
# ---------------------------------------------------------------------------

# Wilson score interval z-score for 95% confidence.
WILSON_Z_95 = 1.96

# Minimum sample size before a band reports a point estimate. Empirically
# chosen so a 0/2 or 2/2 result does not look like 0% or 100% with no signal.
DEFAULT_MIN_BAND_N = 5

# Confidence-score bands matching the SSOT in author-gate-decision-points.md §AG-9.
# Lower-inclusive, upper-exclusive except the last band.
CONFIDENCE_BANDS: list[tuple[str, float, float]] = [
    ("[0.72, 0.80)", 0.72, 0.80),
    ("[0.80, 0.85)", 0.80, 0.85),
    ("[0.85, 0.90)", 0.85, 0.90),
    ("[0.90, 1.00]", 0.90, 1.0001),
]

# Priority-band layout used by deferred-scope calibration ledger.
P_BAND_LAYOUT: list[tuple[str, float, float]] = [
    ("P5", 0.0, 30.0),
    ("P4", 30.0, 75.0),
    ("P3", 75.0, 150.0),
    ("P2", 150.0, 300.0),
    ("P1", 300.0, math.inf),
]


# ---------------------------------------------------------------------------
# Wilson score interval — the only stat primitive in this module
# ---------------------------------------------------------------------------


def wilson_interval(successes: int, n: int, z: float = WILSON_Z_95) -> tuple[float, float, float]:
    """Return (point_estimate, ci_low, ci_high) using the Wilson score interval.

    Wilson is preferred over the normal approximation because it
    stays inside [0,1] for any (k, n) and gives sensible answers at 0% and
    100% success rates. Returns (0.0, 0.0, 0.0) when n == 0 to avoid
    divide-by-zero — callers should treat n==0 as "insufficient sample".
    """
    if n <= 0 or successes < 0:
        return 0.0, 0.0, 0.0
    p = successes / n
    denom = 1 + (z * z) / n
    centre = (p + (z * z) / (2 * n)) / denom
    half = (z * math.sqrt((p * (1 - p) + (z * z) / (4 * n)) / n)) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


# ---------------------------------------------------------------------------
# Adapter — describes how to extract calibration signal from a ledger row
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LedgerAdapter:
    """Describes how to map an arbitrary ledger row to calibration signals.

    Each callable accepts a dict (a single SQLite row, sqlite3.Row converted
    to dict) and returns a typed primitive. All extractors must be pure
    and tolerate missing/malformed fields by returning None.

    Attributes:
        name: human-readable adapter name, used in report sections.
        get_outcome_label: returns one of {"success","rework","rollback",
            "undecided","unbound"} — "unbound" means no outcome yet.
        get_confidence: returns the prediction's confidence in [0,1]
            (None if not applicable to this ledger).
        get_precedent_verdict: returns "strong"|"suggestive"|"none"|None.
            Used for precedent-hit metrics. None for ledgers with no
            precedent retrieval (most non-Author-Gate ledgers).
        success_label: which label counts as a "success" — typically
            "success" for the Author-Gate ledger and "correct" for routing
            ledgers. Default "success".
    """

    name: str
    get_outcome_label: Callable[[Mapping], str]
    get_confidence: Callable[[Mapping], float | None] = lambda _: None
    get_precedent_verdict: Callable[[Mapping], str | None] = lambda _: None
    success_label: str = "success"


# ---------------------------------------------------------------------------
# Computed metric outputs — explicit, named, easy to render
# ---------------------------------------------------------------------------


@dataclass
class BandStat:
    """One band's calibration outcome."""

    label: str
    n: int
    successes: int
    point: float
    ci_low: float
    ci_high: float
    sufficient: bool
    band_low: float | None = None  # nominal band lower bound (for ✅/⚠️ overlap check)
    band_high: float | None = None

    @property
    def calibrated(self) -> bool | None:
        """True if the success-rate CI overlaps [band_low, band_high].

        None when band bounds are not provided OR sample is insufficient.
        ⚠️ status (False) means the band is mis-calibrated — confidence
        scores in this range don't actually succeed at the predicted rate.
        """
        if not self.sufficient or self.band_low is None or self.band_high is None:
            return None
        return (self.ci_high >= self.band_low) and (self.ci_low <= self.band_high)


@dataclass
class PrecedentCorrelation:
    """One verdict's outcome breakdown."""

    verdict: str
    n: int
    by_outcome: Counter
    success_rate: float
    ci_low: float
    ci_high: float
    sufficient: bool


@dataclass
class CalibrationMetrics:
    """Top-level result for a ledger / window."""

    ledger_name: str = ""
    total_rows: int = 0
    bound_rows: int = 0
    unknown_precedent: int = 0  # rows where verdict could not be extracted

    # Precedent-hit metrics
    precedent_hit_count: int = 0  # verdicts ∈ {strong, suggestive}
    precedent_by_verdict: Counter = field(default_factory=Counter)

    # Precedent × outcome correlation
    precedent_correlation: list[PrecedentCorrelation] = field(default_factory=list)

    # Per-band calibration curve
    calibration_curve: list[BandStat] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Computation — pure functions over (rows, adapter, bands)
# ---------------------------------------------------------------------------


def _bucket_index(value: float, bands: Sequence[tuple[str, float, float]]) -> int | None:
    for i, (_, lo, hi) in enumerate(bands):
        if lo <= value < hi:
            return i
    return None


def compute_metrics(
    rows: Iterable[Mapping],
    adapter: LedgerAdapter,
    bands: Sequence[tuple[str, float, float]] | None = None,
    min_band_n: int = DEFAULT_MIN_BAND_N,
    ledger_name: str | None = None,
) -> CalibrationMetrics:
    """Compute calibration metrics over an iterable of ledger rows.

    Single-pass: each row is inspected once. Rows with missing extractors
    are gracefully excluded from the relevant metric only — they still
    count toward total_rows.
    """
    if bands is None:
        bands = CONFIDENCE_BANDS
    out = CalibrationMetrics(ledger_name=ledger_name or adapter.name)
    band_buckets: list[list[int]] = [[0, 0] for _ in bands]  # [n, succ] per band
    verdict_outcome: dict[str, Counter] = {}

    for row in rows:
        out.total_rows += 1
        outcome_label = adapter.get_outcome_label(row)
        if outcome_label and outcome_label != "unbound":
            out.bound_rows += 1

        # Precedent verdict
        verdict_raw = adapter.get_precedent_verdict(row)
        verdict = verdict_raw.strip().lower() if isinstance(verdict_raw, str) else None
        if verdict is None:
            out.unknown_precedent += 1
        else:
            out.precedent_by_verdict[verdict] += 1
            if verdict in ("strong", "suggestive"):
                out.precedent_hit_count += 1

        # Precedent × outcome — only counted when both signals present
        if verdict is not None and outcome_label and outcome_label != "unbound":
            verdict_outcome.setdefault(verdict, Counter())[outcome_label] += 1

        # Per-band calibration — only counted when both confidence and outcome present
        confidence = adapter.get_confidence(row)
        if isinstance(confidence, (int, float)) and outcome_label and outcome_label != "unbound":
            idx = _bucket_index(float(confidence), bands)
            if idx is not None:
                band_buckets[idx][0] += 1
                if outcome_label == adapter.success_label:
                    band_buckets[idx][1] += 1

    # Materialize precedent correlation
    for verdict in ("strong", "suggestive", "none"):
        ctr = verdict_outcome.get(verdict)
        if not ctr:
            continue
        n_v = sum(ctr.values())
        succ_v = ctr.get(adapter.success_label, 0)
        point, low, high = wilson_interval(succ_v, n_v)
        out.precedent_correlation.append(
            PrecedentCorrelation(
                verdict=verdict,
                n=n_v,
                by_outcome=ctr,
                success_rate=point,
                ci_low=low,
                ci_high=high,
                sufficient=n_v >= min_band_n,
            )
        )

    # Materialize calibration curve
    for i, (label, lo, hi) in enumerate(bands):
        n_band, succ_band = band_buckets[i]
        point, ci_low, ci_high = wilson_interval(succ_band, n_band)
        # Treat the open-ended last bucket's high as 1.0 for the overlap check.
        nominal_high = hi if hi <= 1.0 else 1.0
        out.calibration_curve.append(
            BandStat(
                label=label,
                n=n_band,
                successes=succ_band,
                point=point,
                ci_low=ci_low,
                ci_high=ci_high,
                sufficient=n_band >= min_band_n,
                band_low=lo,
                band_high=nominal_high,
            )
        )

    return out


# ---------------------------------------------------------------------------
# Markdown rendering — separate from computation for testability
# ---------------------------------------------------------------------------


def render_precedent_block(metrics: CalibrationMetrics, min_n: int = DEFAULT_MIN_BAND_N) -> str:
    """Render the Precedent Injection + Correlation sections in Markdown."""
    lines: list[str] = []
    bound_pre = metrics.total_rows - metrics.unknown_precedent

    lines.append("#### Precedent Injection")
    lines.append("")
    if metrics.total_rows == 0:
        lines.append("_no rows in this window_")
        lines.append("")
        return "\n".join(lines)
    if bound_pre == 0:
        lines.append(
            f"_All {metrics.total_rows} row(s) lack a captured precedent verdict "
            "(pre-migration or non-applicable). Real signal arrives once writers populate it._"
        )
        lines.append("")
        return "\n".join(lines)

    rate = metrics.precedent_hit_count / bound_pre if bound_pre else 0.0
    lines.append(f"- Verdict captured: **{bound_pre}** of {metrics.total_rows}")
    lines.append(
        f"- Real precedent-hit rate (excludes NULL): "
        f"**{metrics.precedent_hit_count}/{bound_pre} = {rate:.1%}**"
    )
    if metrics.unknown_precedent:
        lines.append(f"- Excluded (verdict NULL): {metrics.unknown_precedent}")
    lines.append("")

    if metrics.precedent_by_verdict:
        lines.append("| Verdict | Count | Share of captured |")
        lines.append("|---|---:|---:|")
        for v in ("strong", "suggestive", "none"):
            c = metrics.precedent_by_verdict.get(v, 0)
            share = c / bound_pre if bound_pre else 0.0
            lines.append(f"| `{v}` | {c} | {share:.1%} |")
        lines.append("")

    lines.append("#### Precedent × Outcome Correlation")
    lines.append("")
    lines.append(
        "_Does precedent verdict correlate with success?_ Excludes rows whose outcomes are still unbound."
    )
    lines.append("")
    if not metrics.precedent_correlation:
        lines.append("_no rows have both verdict and outcome bound_")
        lines.append("")
        return "\n".join(lines)

    outcome_labels = sorted({lab for c in metrics.precedent_correlation for lab in c.by_outcome})
    header_cells = "".join(f" {lab} |" for lab in outcome_labels)
    sep_cells = "".join("---:|" for _ in outcome_labels)
    lines.append(f"| Verdict | n |{header_cells} success rate (Wilson 95% CI) |")
    lines.append(f"|---|---:|{sep_cells}---|")
    for pc in metrics.precedent_correlation:
        cells = "".join(f" {pc.by_outcome.get(lab, 0)} |" for lab in outcome_labels)
        if not pc.sufficient:
            rate_cell = f"insufficient sample (n={pc.n}<{min_n})"
        else:
            rate_cell = f"{pc.success_rate:.0%} [{pc.ci_low:.0%}, {pc.ci_high:.0%}]"
        lines.append(f"| `{pc.verdict}` | {pc.n} |{cells} {rate_cell} |")
    lines.append("")
    return "\n".join(lines)


def render_calibration_curve(
    metrics: CalibrationMetrics,
    band_units_label: str = "confidence",
) -> str:
    """Render the Per-Band Calibration Curve in Markdown.

    band_units_label distinguishes "confidence" (Author-Gate) from
    "P-band" (deferred-scope) so the prose helper line stays accurate.
    """
    lines: list[str] = []
    lines.append("#### Per-Band Calibration Curve")
    lines.append("")
    lines.append(
        f"_Of rows surfaced at each {band_units_label} band, what fraction succeeded?_ "
        "If a band's success-rate CI does not overlap its nominal range, the prediction "
        "is mis-calibrated for that band."
    )
    lines.append("")

    if not any(b.sufficient for b in metrics.calibration_curve):
        lines.append(
            "_Insufficient sample in every band. Calibration curve will populate as more rows accumulate._"
        )
        lines.append("")
        return "\n".join(lines)

    lines.append("| Band | n | successes | success rate (Wilson 95% CI) | calibrated? |")
    lines.append("|---|---:|---:|---|:---:|")
    for b in metrics.calibration_curve:
        if not b.sufficient:
            rate = f"insufficient (n={b.n})"
            cal = "—"
        else:
            rate = f"{b.point:.0%} [{b.ci_low:.0%}, {b.ci_high:.0%}]"
            calibrated = b.calibrated
            cal = "—" if calibrated is None else ("✅" if calibrated else "⚠️")
        lines.append(f"| {b.label} | {b.n} | {b.successes} | {rate} | {cal} |")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Pre-built adapters for the 11 known loops
# ---------------------------------------------------------------------------


def _author_gate_outcome(row: Mapping) -> str:
    """Author-Gate decisions ledger: outcome label lives on decision_outcomes
    and is left-joined as outcome_label. Missing → 'unbound'."""
    val = row.get("outcome_label")
    return str(val) if isinstance(val, str) and val else "unbound"


def _author_gate_confidence(row: Mapping) -> float | None:
    val = row.get("confidence_top")
    return float(val) if isinstance(val, (int, float)) else None


def _author_gate_verdict(row: Mapping) -> str | None:
    val = row.get("precedent_verdict")
    return val.strip().lower() if isinstance(val, str) and val.strip() else None


AUTHOR_GATE_ADAPTER = LedgerAdapter(
    name="author_gate",
    get_outcome_label=_author_gate_outcome,
    get_confidence=_author_gate_confidence,
    get_precedent_verdict=_author_gate_verdict,
    success_label="success",
)


def _events_outcome(row: Mapping) -> str:
    """Events-ledger outcome: prefer status='bound' + score_band as label.

    Convention used by ADR-050 ledgers:
        status='predicted' → 'unbound'
        status='bound' + score_band='correct' → 'success'
        status='bound' + score_band='miss'    → 'rework'
        status='bound' + score_band='rollback'→ 'rollback'
        anything else → fall back to score_band lowercased, defaulting 'undecided'.
    """
    status = row.get("status")
    if status != "bound":
        return "unbound"
    band = row.get("score_band")
    if not isinstance(band, str):
        return "undecided"
    band = band.strip().lower()
    if band in ("correct", "success", "ok", "pass"):
        return "success"
    if band in ("miss", "rework", "wrong", "fail"):
        return "rework"
    if band in ("rollback", "reverted"):
        return "rollback"
    return band or "undecided"


def _events_confidence(row: Mapping) -> float | None:
    val = row.get("score_numeric")
    return float(val) if isinstance(val, (int, float)) else None


EVENTS_ADAPTER = LedgerAdapter(
    name="events",
    get_outcome_label=_events_outcome,
    get_confidence=_events_confidence,
    get_precedent_verdict=lambda _row: None,  # most events ledgers have no precedent retrieval
    success_label="success",
)
