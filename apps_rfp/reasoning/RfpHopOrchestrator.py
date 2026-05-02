"""RfpHopOrchestrator — shared-substrate entry for apps_rfp.

Alternative to the imperative ``BaseRfpEngine``-driven path. Uses the
shared ``HopPipelineExecutor`` to walk the 3 stages declared in
``apps_rfp/config/hop_pipeline.py``.

See plan .windsurf/plans/apps-hop-substrate-four-apps-b4a2c9.md (Wave 2).
"""

from __future__ import annotations

from typing import Any

from apps_rfp.config.hop_pipeline import REGISTRY
from apps_shared.orchestration import (
    Checkpoint,
    HopPipelineExecutor,
    HopRunRecord,
)


class RfpHopOrchestrator:
    """Shared-substrate driver for the 3-stage RFP pipeline."""

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
        """Execute the 3-stage RFP pipeline declaratively.

        Context contract:
            - ``rfp_request``: an RfpRequest-like input.

        The returned ``HopRunRecord.final_context`` carries ``proposal``
        (when HOP3 completed), plus the intermediate ``ingested_rfp`` and
        ``retrieved_proposals`` keys.
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


__all__ = ["RfpHopOrchestrator"]
