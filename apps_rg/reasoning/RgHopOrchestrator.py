"""RgHopOrchestrator — shared-substrate entry for apps_rg resume generation.

Alternative to the imperative ``RgResumeOrchestrator.run()`` path. Uses
the shared ``HopPipelineExecutor`` to walk the 7 stages declared in
``apps_rg/config/hop_pipeline.py``.

Both orchestrators are supported:
- ``RgResumeOrchestrator.run()`` — primary runtime; Qwen gateway +
  repo signals + heal cycle + full Pydantic-typed pipeline.
- ``RgHopOrchestrator.run()`` — shared substrate; declarative walk
  across thin adapters; supports replay and seal_step.

A follow-up plan (``apps-rg-substrate-deep-migration``) will capture a
golden-parity fixture and replace the thin adapters with full
BaseModel↔dict marshaling so the substrate path can become the primary
runtime.

See plan .windsurf/plans/apps-hop-substrate-f7751b.md (Wave 3).
"""

from __future__ import annotations

from typing import Any

from apps_rg.config.hop_pipeline import REGISTRY
from apps_shared.orchestration import (
    Checkpoint,
    HopPipelineExecutor,
    HopRunRecord,
)


class RgHopOrchestrator:
    """Shared-substrate driver for the 7-stage resume-generation pipeline."""

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
        """Execute the 7-stage resume-generation pipeline declaratively."""
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


__all__ = ["RgHopOrchestrator"]
