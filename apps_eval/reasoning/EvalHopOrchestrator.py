"""EvalHopOrchestrator — shared-substrate entry for apps_eval.

Alternative to the imperative ``BaseEvalEngine``-driven path (primary
runtime lives under ``apps_eval/reasoning/EvalOrchestrator.py`` +
``evaluation_orchestrator.py`` + ``enterprise_eval_orchestrator.py``).
Uses the shared ``HopPipelineExecutor`` to walk the 6 stages declared in
``apps_eval/config/hop_pipeline.py``.

See plan .windsurf/plans/apps-hop-substrate-four-apps-b4a2c9.md (Wave 4).
"""

from __future__ import annotations

from typing import Any

from apps_eval.config.hop_pipeline import REGISTRY
from apps_shared.orchestration import (
    Checkpoint,
    HopPipelineExecutor,
    HopRunRecord,
)


class EvalHopOrchestrator:
    """Shared-substrate driver for the 6-stage evaluation pipeline."""

    def __init__(
        self,
        *,
        seal_step_provider: Any | None = None,
    ) -> None:
        self._executor = HopPipelineExecutor(
            registry=REGISTRY,
            seal_step_provider=seal_step_provider,
        )

    def run(
        self,
        context: dict[str, Any] | None = None,
        *,
        run_id: str = "",
        trace_id: str = "",
    ) -> HopRunRecord:
        """Execute the 6-stage evaluation pipeline declaratively.

        Context contract:
            - ``eval_request``: an EvalRequest-like input.

        The returned ``HopRunRecord.final_context`` carries
        ``hitl_quality_report`` (when HOP6 completed), plus the
        intermediate ``retrieved_evaluations``, ``scenario_results``,
        ``scorecard``, ``judge_verdicts``, and ``regression_result`` keys.
        """
        return self._executor.run(
            context=context, run_id=run_id, trace_id=trace_id
        )

    def replay_stage(
        self,
        stage_id: int,
        context: dict[str, Any],
        *,
        trace_id: str = "",
    ) -> Checkpoint:
        """Re-run one stage in isolation."""
        return self._executor.replay_stage(
            stage_id, context, trace_id=trace_id
        )


__all__ = ["EvalHopOrchestrator"]
