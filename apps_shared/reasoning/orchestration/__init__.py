"""apps_shared.orchestration — shared inner-DAG substrate for apps_*.

Canonical home for the per-app HOP pipeline executor that consumers in
``apps_rg``, ``apps_lic``, ``apps_underwriting_ai`` (and future multi-hop
apps) delegate to instead of re-inventing orchestration plumbing.

See: .windsurf/plans/apps-hop-substrate-f7751b.md (Wave 1).
"""

from __future__ import annotations

from apps_shared.reasoning.orchestration.hop_pipeline import (
    Checkpoint,
    HopPipelineExecutor,
    HopRegistry,
    HopRegistryValidationError,
    HopRunRecord,
    HopStageSpec,
    StageStatus,
)

__all__ = [
    "Checkpoint",
    "HopPipelineExecutor",
    "HopRegistry",
    "HopRegistryValidationError",
    "HopRunRecord",
    "HopStageSpec",
    "StageStatus",
]
