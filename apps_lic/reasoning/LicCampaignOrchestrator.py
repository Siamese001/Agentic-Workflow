"""LicCampaignOrchestrator — thin wrapper over the shared HOP pipeline.

Delegates all walk plumbing to
``apps_shared.orchestration.HopPipelineExecutor``; apps_lic-specific
concerns (topology, engines) live in
``apps_lic.config.hop_pipeline`` and ``apps_lic/engines/*_engine.py``
respectively.

Replaces the pre-refactor ``HOPPipelineExecutor`` / ``hop_stage_registry``
pairing, whose stage handlers were stubs after the 2026-02-08
consolidation. See plan
.windsurf/plans/apps-hop-substrate-f7751b.md (Wave 2 Phase 2.3).
"""

from __future__ import annotations

from typing import Any

from apps_lic.config.hop_pipeline import REGISTRY
from apps_shared.orchestration import (
    Checkpoint,
    HopPipelineExecutor,
    HopRunRecord,
)


class LicCampaignOrchestrator:
    """apps_lic inner-DAG driver.

    Construct once per runner; call :meth:`run` per request. Thread-safety
    matches the underlying executor (stateless between runs).
    """

    def __init__(
        self,
        *,
        seal_step_provider: Any | None = None,
    ) -> None:
        self._executor = HopPipelineExecutor(
            registry=REGISTRY,
            seal_step_provider=seal_step_provider,
        )

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(
        self,
        context: dict[str, Any] | None = None,
        *,
        run_id: str = "",
        trace_id: str = "",
    ) -> HopRunRecord:
        """Execute the 9-stage apps_lic pipeline."""
        return self._executor.run(
            context=context, run_id=run_id, trace_id=trace_id
        )

    # ------------------------------------------------------------------
    # Single-stage replay (used by LicHealingOrchestrator._heal_schema)
    # ------------------------------------------------------------------

    def replay_stage(
        self,
        stage_id: int,
        context: dict[str, Any],
        *,
        trace_id: str = "",
    ) -> Checkpoint:
        """Re-run one stage in isolation — for healing / incident replay."""
        return self._executor.replay_stage(
            stage_id, context, trace_id=trace_id
        )


__all__ = ["LicCampaignOrchestrator"]
