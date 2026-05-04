"""Tests: apps_rg E5_SEAL step (W2 deferred plan).

Verifies that DocxManifestStep compiles a governed PA artifact via the
registry-aware compiler using the docx_manifest_v1 template.
"""

from __future__ import annotations

import json
from typing import Any

import pytest


def _seal_context(**overrides: Any) -> dict[str, Any]:
    """Build a minimal context for E5_SEAL step."""
    ctx: dict[str, Any] = {
        "jd_data": "Software Engineer role requiring Python expertise",
        "master_resume_data": json.dumps({"name": "Jane Doe", "skills": ["Python"]}),
        "run_id": "seal-run-1",
        "trace_id": "seal-trace-1",
    }
    ctx.update(overrides)
    return ctx


class TestDocxManifestStep:
    def test_compiles_artifact(self):
        from apps_rg.l2_recipe.steps import DocxManifestStep
        step = DocxManifestStep()
        result = step(_seal_context())
        assert result["exit_code"] == 0
        assert result["step_id"] == "docx_manifest_seal"
        art = result["compiled_prompt_artifact"]
        assert art["compile_status"] == "PA_L2_HANDOFF_READY"
        assert art["prompt_id"] == "apps_rg.docx_manifest_v1"

    def test_artifact_has_required_hashes(self):
        from apps_rg.l2_recipe.steps import DocxManifestStep
        result = DocxManifestStep()(_seal_context())
        art = result["compiled_prompt_artifact"]
        for field in (
            "prompt_bom_hash", "prompt_registry_hash", "prompt_template_hash",
            "manifest_hash", "canonical_slot_bytes_hash", "artifact_hash",
        ):
            assert art.get(field), f"Missing hash: {field}"

    def test_requires_pa_flag(self):
        from apps_rg.l2_recipe.steps import DocxManifestStep
        assert DocxManifestStep.REQUIRES_PA is True

    def test_step_id(self):
        from apps_rg.l2_recipe.steps import DocxManifestStep
        assert DocxManifestStep.STEP_ID == "docx_manifest_seal"

    def test_template_registered_as_e5_seal(self):
        """docx_manifest_v1 should be registered with allowed_stage E5_SEAL."""
        import yaml
        from pathlib import Path
        registry_path = Path("apps_rg/prompt_assembly/prompt_registry.yaml")
        with open(registry_path) as f:
            registry = yaml.safe_load(f)
        entry = registry["templates"]["docx_manifest_v1"]
        assert entry["allowed_stage"] == "E5_SEAL"

    def test_provider_messages_present(self):
        from apps_rg.l2_recipe.steps import DocxManifestStep
        result = DocxManifestStep()(_seal_context())
        art = result["compiled_prompt_artifact"]
        msgs = art.get("provider_specific_messages", [])
        assert len(msgs) >= 1, "Artifact must have provider_specific_messages"
        assert msgs[0]["role"] == "system"
