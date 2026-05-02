"""UnderwritingHopOrchestrator — shared-substrate entry for apps_underwriting_ai.

Alternative to the imperative ``UnderwritingEngine.run()`` path. Uses the
shared ``HopPipelineExecutor`` to walk the same 5 stages declared in
``apps_underwriting_ai/config/hop_pipeline.py``.

Both orchestrators are supported:
- ``UnderwritingEngine.run(request) -> UnderwritingResult`` — primary,
  imperative, matches the existing integration surface.
- ``UnderwritingHopOrchestrator.run(context) -> HopRunRecord`` — shared
  substrate, declarative, supports replay and composability.

See plan .windsurf/plans/apps-hop-substrate-f7751b.md (Wave 4.1).
"""

from __future__ import annotations

from typing import Any

from apps_shared.orchestration import (
    Checkpoint,
    HopPipelineExecutor,
    HopRunRecord,
)
from apps_underwriting_ai.config.hop_pipeline import REGISTRY


class UnderwritingHopOrchestrator:
    """Shared-substrate driver for the 5-stage underwriting pipeline."""

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
        """Execute the 5-stage underwriting pipeline declaratively.

        Context contract:
            - ``underwriting_request``: an ``UnderwritingRequest`` instance.

        The returned ``HopRunRecord.final_context`` carries
        ``decision_packet`` (when HOP5 completed), plus the intermediate
        ``evidence_register``, ``reconciliation_result``, and
        ``risk_features`` keys for inspection or downstream consumers.
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


__all__ = ["UnderwritingHopOrchestrator"]
