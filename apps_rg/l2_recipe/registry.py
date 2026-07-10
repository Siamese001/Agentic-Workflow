"""apps_rg L2 recipe registry — metadata for ``resolve_l2_recipe``.

``agentic_core.runtime.l2_recipe_resolver`` imports ``get_apps_rg_recipe_metadata``
lazily.  This module MUST stay free of heavy side effects at import time.
"""
from __future__ import annotations

from typing import Any

from apps_rg.l2_recipe.attempt_witness import build_runtime_execution_witness
from apps_rg.l2_recipe.steps import (
    GenerateResumeStep,
    GenerateSectionStep,
    ResumeArtifactGateStep,
)


def get_apps_rg_recipe_metadata() -> dict[str, Any]:
    """Return recipe metadata for ``apps_rg`` R4_SINGLE_ACTION L2 composition.

    Returns
    -------
    dict
        Keys: ``app_name`` (str), ``dag_id`` (str), ``steps`` (tuple of step classes).
    """
    return {
        "app_name": "apps_rg",
        "dag_id": "apps_rg_resume_r4_v1",
        "steps": (GenerateResumeStep, ResumeArtifactGateStep),
        "scope_steps": {
            "section": (GenerateSectionStep,),
        },
        "execution_witness_builder": build_runtime_execution_witness,
    }


__all__ = ["get_apps_rg_recipe_metadata"]
