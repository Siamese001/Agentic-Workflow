"""Six-dimensional retrieval eval rubric (Anthropic-aligned).

Per Anthropic's "Define success criteria" guidance, retrieval/RAG quality is
not a single score — it's a tradeoff across several orthogonal axes. A change
that improves one axis can silently regress another, so evals that report
only one score (e.g., Recall@k) are insufficient.

This module defines the canonical 6-dimensional rubric for the Agentic-Workflow
retrieval stack:

    1. Relevance          — did retrieval surface the right chunks?
    2. Faithfulness       — does the answer text match the retrieved chunks
                            (no hallucinated claims)?
    3. Citation correctness — does each factual claim carry a valid citation
                            that resolves to a must-use chunk?
    4. Latency            — wall-clock time from query → final answer (p50/p95)
    5. Cost               — dollar cost per query (input + output tokens)
    6. Failure modes      — taxonomy of how the pipeline failed (abstain,
                            overflow, no-support, citation-gap, parse-failure)

Pure: no I/O, no model calls. Callers supply measurements (typically from
harness runs) and this module composes them into the ReportCard.

References:
- Anthropic API Docs. Define success criteria and build evaluations.
  https://docs.anthropic.com/en/docs/test-and-evaluate/define-success
- Plan: .windsurf/plans/anthropic-rag-gaps-7f3c2a.md (phase P3.1)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from statistics import mean
from typing import Iterable

# Failure-mode taxonomy — matches status codes emitted by W2.P2.3
# dual_pass_citation_orchestrator so runs can be categorized without
# re-interpretation.
FAILURE_ABSTAIN = "abstain"
FAILURE_OVERFLOW = "overflow"
FAILURE_WEAK_SUPPORT = "weak_support"
FAILURE_CITATION_GAP = "citation_gap"
FAILURE_JSON_PARSE = "json_parse_failed"
FAILURE_PASS1 = "pass1_failed"
FAILURE_PASS2 = "pass2_failed"
FAILURE_OTHER = "other"

# Traffic-light thresholds for each dimension. Callers can override per-run
# but these defaults align with Anthropic's stated quality bar for
# production RAG (Define-success-criteria doc).
DEFAULT_RELEVANCE_GREEN = 0.80
DEFAULT_FAITHFULNESS_GREEN = 0.90
DEFAULT_CITATION_GREEN = 0.85
DEFAULT_LATENCY_P95_YELLOW_MS = 5000.0
DEFAULT_LATENCY_P95_RED_MS = 15000.0
DEFAULT_COST_PER_QUERY_YELLOW_USD = 0.10
DEFAULT_COST_PER_QUERY_RED_USD = 1.00


@dataclass(frozen=True)
class QueryMeasurement:
    """One query's measured outcome for eval aggregation.

    All fields are OPTIONAL — callers pass what they have. Aggregators
    skip dimensions where the measurement is missing rather than
    imputing a zero or NaN.
    """

    query_id: str
    relevance_score: float | None = None  # 0.0..1.0 (e.g., ndcg@k)
    faithfulness_score: float | None = None  # 0.0..1.0 (answer vs chunks)
    citation_correctness: float | None = None  # 0.0..1.0 (P2.2 coverage_ratio)
    latency_ms: float | None = None
    cost_usd: float | None = None
    failure_mode: str | None = None  # one of FAILURE_* or None on success


@dataclass(frozen=True)
class DimensionSummary:
    """Aggregate for a single dimension across a run."""

    name: str
    sample_count: int
    mean: float | None
    p50: float | None
    p95: float | None
    status: str  # "green" | "yellow" | "red" | "unknown"


@dataclass(frozen=True)
class ReportCard:
    """Full 6-dim rubric result for a retrieval eval run.

    Attributes
    ----------
    run_id:
        Stable identifier for this eval run (caller-supplied).
    query_count:
        Total queries in the run (including failures).
    dimensions:
        Tuple of DimensionSummary for the 5 scalar dimensions (relevance,
        faithfulness, citation, latency, cost). Failure modes are reported
        separately in ``failure_mode_counts``.
    failure_mode_counts:
        Counter of failure modes across the run. Empty when no failures.
    overall_status:
        Worst status across all reported dimensions. "red" when any red,
        "yellow" when any yellow, "green" when all green.
    """

    run_id: str
    query_count: int
    dimensions: tuple[DimensionSummary, ...]
    failure_mode_counts: dict[str, int] = field(default_factory=dict)
    overall_status: str = "unknown"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _percentile(values: list[float], pct: float) -> float | None:
    """Simple percentile (no numpy dependency)."""
    if not values:
        return None
    if not 0 <= pct <= 100:
        raise ValueError(f"pct must be in [0, 100], got {pct}")
    sorted_vals = sorted(values)
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    # Linear interpolation between nearest ranks
    idx = (len(sorted_vals) - 1) * pct / 100
    lower = int(idx)
    upper = min(lower + 1, len(sorted_vals) - 1)
    frac = idx - lower
    return sorted_vals[lower] + frac * (sorted_vals[upper] - sorted_vals[lower])


def _status_from_quality(score: float | None, green_threshold: float) -> str:
    if score is None:
        return "unknown"
    if score >= green_threshold:
        return "green"
    if score >= green_threshold - 0.10:
        return "yellow"
    return "red"


def _status_from_latency(
    p95_ms: float | None,
    yellow_threshold_ms: float,
    red_threshold_ms: float,
) -> str:
    if p95_ms is None:
        return "unknown"
    if p95_ms >= red_threshold_ms:
        return "red"
    if p95_ms >= yellow_threshold_ms:
        return "yellow"
    return "green"


def _status_from_cost(
    mean_cost: float | None,
    yellow_threshold_usd: float,
    red_threshold_usd: float,
) -> str:
    if mean_cost is None:
        return "unknown"
    if mean_cost >= red_threshold_usd:
        return "red"
    if mean_cost >= yellow_threshold_usd:
        return "yellow"
    return "green"


def _summarize_quality(
    name: str,
    values: list[float],
    green_threshold: float,
) -> DimensionSummary:
    if not values:
        return DimensionSummary(name=name, sample_count=0, mean=None, p50=None, p95=None, status="unknown")
    m = mean(values)
    return DimensionSummary(
        name=name,
        sample_count=len(values),
        mean=m,
        p50=_percentile(values, 50),
        p95=_percentile(values, 95),
        status=_status_from_quality(m, green_threshold),
    )


def _summarize_latency(
    values: list[float],
    yellow_ms: float,
    red_ms: float,
) -> DimensionSummary:
    if not values:
        return DimensionSummary(name="latency_ms", sample_count=0, mean=None, p50=None, p95=None, status="unknown")
    p95 = _percentile(values, 95)
    return DimensionSummary(
        name="latency_ms",
        sample_count=len(values),
        mean=mean(values),
        p50=_percentile(values, 50),
        p95=p95,
        status=_status_from_latency(p95, yellow_ms, red_ms),
    )


def _summarize_cost(
    values: list[float],
    yellow_usd: float,
    red_usd: float,
) -> DimensionSummary:
    if not values:
        return DimensionSummary(name="cost_usd", sample_count=0, mean=None, p50=None, p95=None, status="unknown")
    m = mean(values)
    return DimensionSummary(
        name="cost_usd",
        sample_count=len(values),
        mean=m,
        p50=_percentile(values, 50),
        p95=_percentile(values, 95),
        status=_status_from_cost(m, yellow_usd, red_usd),
    )


_STATUS_RANK = {"unknown": 0, "green": 1, "yellow": 2, "red": 3}


def _worst_status(statuses: Iterable[str]) -> str:
    worst_rank = 0
    worst_name = "unknown"
    for status in statuses:
        rank = _STATUS_RANK.get(status, 0)
        if rank > worst_rank:
            worst_rank = rank
            worst_name = status
    return worst_name


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_report_card(
    run_id: str,
    measurements: list[QueryMeasurement],
    *,
    relevance_green: float = DEFAULT_RELEVANCE_GREEN,
    faithfulness_green: float = DEFAULT_FAITHFULNESS_GREEN,
    citation_green: float = DEFAULT_CITATION_GREEN,
    latency_p95_yellow_ms: float = DEFAULT_LATENCY_P95_YELLOW_MS,
    latency_p95_red_ms: float = DEFAULT_LATENCY_P95_RED_MS,
    cost_yellow_usd: float = DEFAULT_COST_PER_QUERY_YELLOW_USD,
    cost_red_usd: float = DEFAULT_COST_PER_QUERY_RED_USD,
) -> ReportCard:
    """Aggregate per-query measurements into a 6-dim ReportCard.

    Parameters
    ----------
    run_id:
        Identifier for this eval run (written to telemetry / filename).
    measurements:
        One QueryMeasurement per query in the run. Fields missing on any
        measurement are simply excluded from that dimension's aggregate.

    All keyword thresholds default to production-aligned Anthropic guidance
    but are overridable per run (e.g., dev eval can tolerate slower latency).
    """
    relevance_vals = [m.relevance_score for m in measurements if m.relevance_score is not None]
    faithfulness_vals = [m.faithfulness_score for m in measurements if m.faithfulness_score is not None]
    citation_vals = [m.citation_correctness for m in measurements if m.citation_correctness is not None]
    latency_vals = [m.latency_ms for m in measurements if m.latency_ms is not None]
    cost_vals = [m.cost_usd for m in measurements if m.cost_usd is not None]

    dimensions = (
        _summarize_quality("relevance", relevance_vals, relevance_green),
        _summarize_quality("faithfulness", faithfulness_vals, faithfulness_green),
        _summarize_quality("citation_correctness", citation_vals, citation_green),
        _summarize_latency(latency_vals, latency_p95_yellow_ms, latency_p95_red_ms),
        _summarize_cost(cost_vals, cost_yellow_usd, cost_red_usd),
    )

    failure_counts: Counter[str] = Counter()
    for m in measurements:
        if m.failure_mode:
            failure_counts[m.failure_mode] += 1

    overall = _worst_status(d.status for d in dimensions)

    return ReportCard(
        run_id=run_id,
        query_count=len(measurements),
        dimensions=dimensions,
        failure_mode_counts=dict(failure_counts),
        overall_status=overall,
    )


def report_card_to_markdown(card: ReportCard) -> str:
    """Render a ReportCard as a compact Markdown table suitable for PR comments."""
    lines = [
        f"# Retrieval Eval Report — `{card.run_id}`",
        "",
        f"- **Queries:** {card.query_count}",
        f"- **Overall status:** {card.overall_status}",
        "",
        "| Dimension | Samples | Mean | p50 | p95 | Status |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for dim in card.dimensions:
        mean_str = "—" if dim.mean is None else f"{dim.mean:.3f}"
        p50_str = "—" if dim.p50 is None else f"{dim.p50:.3f}"
        p95_str = "—" if dim.p95 is None else f"{dim.p95:.3f}"
        lines.append(
            f"| {dim.name} | {dim.sample_count} | {mean_str} | {p50_str} | {p95_str} | {dim.status} |"
        )
    if card.failure_mode_counts:
        lines += ["", "## Failure modes", ""]
        for mode, count in sorted(card.failure_mode_counts.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{mode}`: {count}")
    return "\n".join(lines)


__all__ = [
    # Failure modes
    "FAILURE_ABSTAIN",
    "FAILURE_OVERFLOW",
    "FAILURE_WEAK_SUPPORT",
    "FAILURE_CITATION_GAP",
    "FAILURE_JSON_PARSE",
    "FAILURE_PASS1",
    "FAILURE_PASS2",
    "FAILURE_OTHER",
    # Defaults
    "DEFAULT_RELEVANCE_GREEN",
    "DEFAULT_FAITHFULNESS_GREEN",
    "DEFAULT_CITATION_GREEN",
    "DEFAULT_LATENCY_P95_YELLOW_MS",
    "DEFAULT_LATENCY_P95_RED_MS",
    "DEFAULT_COST_PER_QUERY_YELLOW_USD",
    "DEFAULT_COST_PER_QUERY_RED_USD",
    # Data shapes
    "QueryMeasurement",
    "DimensionSummary",
    "ReportCard",
    # Public API
    "build_report_card",
    "report_card_to_markdown",
]
