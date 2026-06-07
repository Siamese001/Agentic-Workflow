"""Bridge from QwenInferenceTelemetry → CostSample iterables.

The Qwen telemetry surface tracks aggregate per-session metrics
(``total_requests``, ``successful_requests``, ``total_latency_ms``,
``tokens_used``). The cost aggregator (W4.3) consumes per-request
``CostSample`` records. This bridge reconstructs request-level samples
from session aggregates so the existing collector can feed the rollup
without each call site needing to emit a CostSample directly.

Two strategies:
  1. ``samples_from_session(session, ...)`` — synthesizes N CostSamples
     for one session by dividing aggregate fields evenly. Use this when
     the per-request granularity has been lost.
  2. ``samples_from_telemetry(telemetry, ...)`` — drains every session
     in a ``QwenInferenceTelemetry`` instance into one flat sample list.

Token-split assumption: input/output split is configurable
(``input_token_ratio``) because the upstream Qwen telemetry doesn't
distinguish them. Default 0.70 (input-heavy) reflects typical RAG / brief
generation workloads. Tune per app via the parameter.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (P3 NEXT_STEP)
"""
from __future__ import annotations

from typing import Iterable

from agentic_core.L3_orchestration.inference.qwen_vllm.config.qwen_telemetry import (
    QwenInferenceTelemetry,
    QwenSessionMetrics,
)
from tools.cost_telemetry import CostSample


def samples_from_session(
    session: QwenSessionMetrics,
    *,
    model_id: str,
    input_token_ratio: float = 0.70,
) -> list[CostSample]:
    """Synthesize per-request CostSamples from one session's aggregates.

    Args:
        session: QwenSessionMetrics aggregate to expand.
        model_id: Model identifier for the cost lookup. Required because
            QwenSessionMetrics does NOT carry per-session model_id today
            (the model is stored on individual ``QwenInferenceMetric``
            records). Caller MUST pass the model_id in.
        input_token_ratio: Fraction of ``tokens_used`` to attribute to
            input. Output gets ``1 - input_token_ratio``. Must be in
            ``[0, 1]``.

    Returns:
        List of N samples where N == session.total_requests.

    The split is deliberately simple — proportional even division. If
    a single request was very different from the session average, the
    rollup will still be correct because the aggregator re-aggregates.
    """
    if not 0.0 <= input_token_ratio <= 1.0:
        raise ValueError(
            f"input_token_ratio must be in [0, 1], got {input_token_ratio}"
        )
    if session.total_requests <= 0:
        return []

    n = session.total_requests
    avg_latency_ms = session.total_latency_ms / n if n else 0.0
    tokens_per_request = session.tokens_used // n
    input_tokens = int(tokens_per_request * input_token_ratio)
    output_tokens = tokens_per_request - input_tokens

    samples: list[CostSample] = []
    # First N - successful_requests samples are failures, the rest succeed.
    # The exact ordering doesn't matter for the rollup but this keeps the
    # output deterministic.
    n_failures = max(0, n - session.successful_requests)
    for i in range(n):
        success = i >= n_failures
        samples.append(
            CostSample(
                app=session.app_name,
                model_id=model_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=avg_latency_ms,
                success=success,
            )
        )
    return samples


def samples_from_telemetry(
    telemetry: QwenInferenceTelemetry,
    *,
    default_model_id: str = "qwen-32b",
    input_token_ratio: float = 0.70,
) -> list[CostSample]:
    """Drain every session in the telemetry collector into a flat list.

    Walks ``telemetry._sessions`` and reconstructs the model_id for each
    session from its earliest recorded ``QwenInferenceMetric``. Falls
    back to ``default_model_id`` when no metric is recorded for the
    session (rare — happens only if record_request_* was never called).
    """
    out: list[CostSample] = []
    sessions: dict[str, QwenSessionMetrics] = telemetry._sessions  # noqa: SLF001 — explicit drain
    metrics_by_session: dict[str, list] = {}
    for m in telemetry._metrics:  # noqa: SLF001 — explicit drain
        sid = m.context.get("session_id")
        if not sid:
            continue
        metrics_by_session.setdefault(sid, []).append(m)

    for session_id, session in sessions.items():
        # Reconstruct the model_id from the first recorded metric.
        recorded = metrics_by_session.get(session_id, [])
        model_id = recorded[0].model_id if recorded else default_model_id
        out.extend(
            samples_from_session(
                session,
                model_id=model_id,
                input_token_ratio=input_token_ratio,
            )
        )
    return out


def aggregate_telemetry(
    telemetry: QwenInferenceTelemetry,
    *,
    default_model_id: str = "qwen-32b",
    input_token_ratio: float = 0.70,
):
    """One-call helper: drain telemetry → aggregate → rollup.

    Convenience wrapper for the common path in apps_*/RUNBOOK code.
    """
    from tools.cost_telemetry import aggregate_by_app

    samples = samples_from_telemetry(
        telemetry,
        default_model_id=default_model_id,
        input_token_ratio=input_token_ratio,
    )
    return aggregate_by_app(samples)


__all__ = [
    "aggregate_telemetry",
    "samples_from_session",
    "samples_from_telemetry",
]
