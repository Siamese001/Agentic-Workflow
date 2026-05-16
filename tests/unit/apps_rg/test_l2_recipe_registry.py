"""L2 recipe registry wiring for apps_rg."""
from __future__ import annotations

from apps_rg.l2_recipe.registry import get_apps_rg_recipe_metadata


def test_get_apps_rg_recipe_metadata_shape() -> None:
    from apps_rg.l2_recipe.steps import DocxExportStep, GenerateResumeStep, ResumeArtifactGateStep

    meta = get_apps_rg_recipe_metadata()
    assert meta["app_name"] == "apps_rg"
    assert meta["dag_id"]
    assert isinstance(meta["steps"], tuple)
    assert len(meta["steps"]) == 3
    assert meta["steps"] == (GenerateResumeStep, DocxExportStep, ResumeArtifactGateStep)
