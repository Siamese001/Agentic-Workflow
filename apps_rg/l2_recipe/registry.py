"""apps_rg L2 recipe registration metadata.

This module exposes recipe metadata and step classes for the apps_rg
deterministic resume-generation pipeline.  It is **imported by
agentic_core** (via ``l2_recipe_resolver``) — NEVER by
``apps_rg.__main__``.

The registry metadata maps:
    app_name  →  DAG ID  →  ordered step classes  →  route binding
"""

from __future__ import annotations

from apps_rg.l2_recipe.steps import (
    DocxExportStep,
    GenerateResumeStep,
    NarrativePassStep,
)

APPS_RG_DAG_ID = "apps_rg.resume_generation_v1.static_dag"
APPS_RG_ROUTE_BINDING = "apps_rg.resume_generation_v1"
APPS_RG_ROUTE_FAMILY = "R4_SINGLE_ACTION"
APPS_RG_APP_NAME = "apps_rg"

APPS_RG_L2_STEPS: tuple[type, ...] = (
    GenerateResumeStep,
    NarrativePassStep,
    DocxExportStep,
)


def get_apps_rg_recipe_metadata() -> dict:
    """Return recipe registration metadata for the apps_rg L2 recipe.

    This is consumed by ``agentic_core.runtime.l2_recipe_resolver`` to
    build the executable L2 callable inside agentic_core.
    """
    return {
        "app_name": APPS_RG_APP_NAME,
        "dag_id": APPS_RG_DAG_ID,
        "route_binding": APPS_RG_ROUTE_BINDING,
        "route_family": APPS_RG_ROUTE_FAMILY,
        "steps": APPS_RG_L2_STEPS,
        "step_ids": tuple(s.STEP_ID for s in APPS_RG_L2_STEPS),
    }
