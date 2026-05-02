"""ExecHopOrchestrator — shared-substrate entry for apps_exec.

Alternative to the imperative ``BaseExecEngine``-driven path. Uses the
shared ``HopPipelineExecutor`` to walk the 4 stages declared in
``apps_exec/config/hop_pipeline.py``.

See plan .windsurf/plans/apps-hop-substrate-four-apps-b4a2c9.md (Wave 3).
"""

from __future__ import annotations

from typing import Any

from apps_exec.config.hop_pipeline import REGISTRY
from apps_shared.orchestration import (
    Checkpoint,
    HopPipelineExecutor,
    HopRunRecord,
)


class ExecHopOrchestrator:
    """Shared-substrate driver for the 4-stage executive-brief pipeline."""

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
        """Execute the 4-stage exec-brief pipeline declaratively.

        Context contract:
            - ``exec_request``: an ExecRequest-like input.

        The returned ``HopRunRecord.final_context`` carries ``exec_brief``
        (when HOP4 completed), plus the intermediate ``ingested_documents``,
        ``retrieved_briefs``, and ``extracted_capabilities`` keys.
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


__all__ = ["ExecHopOrchestrator"]
