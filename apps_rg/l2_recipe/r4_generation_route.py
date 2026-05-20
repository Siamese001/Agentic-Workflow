"""Honest SSOT: how apps_rg **R4 integrated recipe** generates résumé body copy.

``python -m apps_rg`` (``dispatch_apps_rg_run`` → integrated R4 + apps_rg L2 recipe) is
the canonical **product** entry. **GenerateResumeStep** obtains structured JSON either via:

- **Canonical proven path (modular):** seven section-scoped provider lanes +
  deterministic merge into full ``rg_output`` (no ``run_apps_rg_l2_envelope`` for body
  generation when ``APPS_RG_R4_GENERATION_MODE=modular_section_lanes``).
- **Explicit rollback path:** ``APPS_RG_R4_GENERATION_MODE=legacy_full_resume`` keeps
  the historic **monolithic** tailor-existing CPA + single
  ``run_apps_rg_l2_envelope`` invocation.

This module declares the **recipe SSOT** after a guarded proof bundle
(``R4_MODULAR_PROOF_RUN_ID``). Runtime default mode is ``modular_section_lanes`` when
``APPS_RG_R4_GENERATION_MODE`` is unset (see ``resolve_apps_rg_r4_generation_mode``).
Set ``APPS_RG_R4_GENERATION_MODE=legacy_full_resume`` for explicit monolithic rollback;
there is **no** silent downgrade from modular to legacy.

Offline modular orchestration library: ``apps_rg.runtime.internal.lane_batch.run_orchestration`` (no module CLI)
remains a **distinct** entry surface from integrated R4 dispatch; see
``MODULAR_SECTION_ORCHESTRATOR_MODULE``.
"""

from __future__ import annotations

from typing import Final, Literal

from apps_rg.l2_recipe.r4_generation_mode import (
    MODE_LEGACY_FULL_RESUME,
    MODE_MODULAR_SECTION_LANES,
)
from apps_rg.l2_recipe.r4_modular_proof_verification import R4_RECORDED_MODULAR_PROOF_RUN_ID

R4_RECIPE_GENERATION_EXECUTION_STYLE: Literal["modular_section_lanes"] = "modular_section_lanes"

# Declared canonical proven generation route (matches execution style and env mode value).
CANONICAL_PROVEN_GENERATION_ROUTE: Final[str] = "modular_section_lanes"

# Default when ``APPS_RG_R4_GENERATION_MODE`` is unset (explicit rollback / CI determinism).
DEFAULT_RUNTIME_GENERATION_MODE: Final[str] = MODE_MODULAR_SECTION_LANES

# Integrated recipe uses full-résumé envelope CPA only for **legacy** mode — not for modular.
R4_RECIPE_USES_FULL_RESUME_ENVELOPE_CPA: bool = False

R4_RUNTIME_GENERATION_GRAIN: Final[str] = "section_lane"
R4_RUNTIME_MERGE_GRAIN: Final[str] = "full_resume"
R4_ARTIFACT_GRAIN: Final[str] = "full_resume"
R4_SECTION_GRAIN_RUNTIME_BOUND: Final[bool] = True

R4_MODULAR_PROOF_RUN_ID: Final[str] = R4_RECORDED_MODULAR_PROOF_RUN_ID

CANONICAL_INTEGRATED_PRODUCT_ENTRY_IMPORT = (
    "agentic_core.runtime.entry.apps_rg_dispatch.dispatch_apps_rg_run"
)
CANONICAL_CLI_MODULE = "apps_rg.__main__:main"

# Offline / lane-based orchestration (no agentic_core R4); modular Qwen by lane.
MODULAR_SECTION_ORCHESTRATOR_MODULE = "apps_rg.runtime.internal.lane_batch"

__all__ = [
    "CANONICAL_CLI_MODULE",
    "CANONICAL_INTEGRATED_PRODUCT_ENTRY_IMPORT",
    "CANONICAL_PROVEN_GENERATION_ROUTE",
    "DEFAULT_RUNTIME_GENERATION_MODE",
    "MODULAR_SECTION_ORCHESTRATOR_MODULE",
    "R4_ARTIFACT_GRAIN",
    "R4_MODULAR_PROOF_RUN_ID",
    "R4_RECIPE_GENERATION_EXECUTION_STYLE",
    "R4_RECIPE_USES_FULL_RESUME_ENVELOPE_CPA",
    "R4_RUNTIME_GENERATION_GRAIN",
    "R4_RUNTIME_MERGE_GRAIN",
    "R4_SECTION_GRAIN_RUNTIME_BOUND",
]
