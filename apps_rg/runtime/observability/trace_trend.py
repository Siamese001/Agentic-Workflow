"""Bounded, advisory trends over completed apps_rg trace summaries."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

TRACE_TREND_SCHEMA_VERSION = "apps_rg.l6_trace_observability_trend.v1"


def build_l6_trace_observability_trend(
    summaries: Iterable[Mapping[str, Any]],
    *,
    window_size: int = 20,
    mismatch_watch_rate: float = 0.10,
    unavailable_watch_rate: float = 0.25,
) -> dict[str, Any]:
    if window_size < 1:
        raise ValueError("window_size must be >= 1")
    rows = [dict(item) for item in summaries][-window_size:]
    total = len(rows)
    unavailable = sum(1 for row in rows if row.get("trace_verdict") == "TRACE_UNAVAILABLE")
    mismatch = sum(1 for row in rows if row.get("trace_verdict") == "TRACE_MISMATCH")
    reconciled = sum(1 for row in rows if row.get("trace_verdict") == "TRACE_RECONCILED")
    provider_mismatch = sum(
        1 for row in rows if str(row.get("provider_attempt_mirror_status") or "") == "FAIL"
    )
    x3_mismatch = sum(1 for row in rows if str(row.get("x3_mirror_status") or "") == "FAIL")

    consecutive_gap_count = 0
    for row in reversed(rows):
        if row.get("trace_verdict") == "TRACE_RECONCILED":
            break
        consecutive_gap_count += 1

    mismatch_rate = mismatch / total if total else 0.0
    unavailable_rate = unavailable / total if total else 0.0
    availability_rate = (total - unavailable) / total if total else 0.0
    threshold_state = "BASELINE"
    reasons: list[str] = []
    if mismatch_rate > mismatch_watch_rate:
        threshold_state = "WATCH"
        reasons.append("trace_mismatch_rate_above_threshold")
    if unavailable_rate > unavailable_watch_rate:
        threshold_state = "WATCH"
        reasons.append("trace_unavailable_rate_above_threshold")
    if consecutive_gap_count >= 3:
        threshold_state = "WATCH"
        reasons.append("three_or_more_consecutive_trace_gaps")

    return {
        "schema_version": TRACE_TREND_SCHEMA_VERSION,
        "window_size": window_size,
        "runs_seen": total,
        "trace_reconciled_count": reconciled,
        "trace_mismatch_count": mismatch,
        "trace_unavailable_count": unavailable,
        "provider_mirror_mismatch_count": provider_mismatch,
        "x3_mirror_mismatch_count": x3_mismatch,
        "availability_rate": round(availability_rate, 6),
        "mismatch_rate": round(mismatch_rate, 6),
        "unavailable_rate": round(unavailable_rate, 6),
        "consecutive_gap_count": consecutive_gap_count,
        "threshold_state": threshold_state,
        "threshold_reasons": reasons,
        "proof_authority": "local_receipts",
        "current_run_blocking": False,
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only": True,
    }


__all__ = ["TRACE_TREND_SCHEMA_VERSION", "build_l6_trace_observability_trend"]
