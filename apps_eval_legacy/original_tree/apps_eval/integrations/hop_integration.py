"""apps_eval HOP integration helper (Wave 5 — plan apps-hop-substrate-four-apps-b4a2c9).

apps_eval does not use the ``GovernedAppRunner`` substrate (it has its own
ingress runner + promotion loop architecture). This module provides a
standalone helper so callers that want the HOP pipeline's 6-stage walk
can invoke it without forcing a substrate migration.

Mirrors the ``_run_hop_pipeline`` pattern from ``apps_lic`` Wave 2.5 but
lifted out of a runner class because apps_eval's entry points are not
class-based.

Usage::

    from apps_eval.integrations.hop_integration import run_eval_hop_pipeline

    result = run_eval_hop_pipeline(request=eval_request, run_id="...", trace_id="...")
    # result["checkpoints"]       -> tuple[dict, ...]
    # result["terminal_error"]    -> str
"""

from __future__ import annotations

from typing import Any


def run_eval_hop_pipeline(
    *,
    request: Any,
    run_id: str = "",
    trace_id: str = "",
) -> dict[str, Any]:
    """Execute the 6-stage apps_eval HOP pipeline.

    Isolated helper so inner-DAG failures cannot take down the caller —
    any exception inside the HOP pipeline is captured and surfaced via
    ``terminal_error`` instead of propagating.

    Parameters
    ----------
    request:
        An EvalRequest-like object. Passed to the orchestrator as
        ``context["eval_request"]``; adapter engines use method-discovery
        fallbacks to tolerate signature variance across concrete engines.
    run_id, trace_id:
        Correlation keys forwarded to the HOP executor.

    Returns
    -------
    dict with keys:
        - ``checkpoints``: tuple of per-stage checkpoint dicts
          (``stage_id``/``stage_name``/``status``/``duration_ms``/``error``)
        - ``terminal_error``: non-empty when the run halted on FAILED/GATED
          or when the orchestrator itself raised.
    """
    try:
        # Lazy import keeps the apps_eval integration surface import-clean
        # for callers that don't exercise the inner DAG.
        from apps_eval.reasoning.EvalHopOrchestrator import (  # noqa: PLC0415
            EvalHopOrchestrator,
        )

        orchestrator = EvalHopOrchestrator()
        record = orchestrator.run(
            context={"eval_request": request},
            run_id=run_id,
            trace_id=trace_id,
        )
        checkpoints = tuple(
            {
                "stage_id": cp.stage_id,
                "stage_name": cp.stage_name,
                "status": cp.status.value,
                "duration_ms": cp.duration_ms,
                "error": cp.error,
            }
            for cp in record.checkpoints
        )
        return {
            "checkpoints": checkpoints,
            "terminal_error": record.terminal_error,
        }
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError, ImportError) as exc:
        # guardian: allow-broad-exception -- inner-DAG failures must not
        # propagate to callers; surface as terminal_error.
        return {
            "checkpoints": (),
            "terminal_error": f"hop_pipeline_error: {type(exc).__name__}: {exc}",
        }


__all__ = ["run_eval_hop_pipeline"]
