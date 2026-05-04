"""Tests: apps_rg E4_HEAL steps (W2 deferred plan).

Verifies that FactCheckStep, ClaimOmissionStep, and BulletDiversityRepairStep
compile governed PA artifacts via the registry-aware compiler.
"""

from __future__ import annotations

import json
from typing import Any

import pytest


def _heal_context(**overrides: Any) -> dict[str, Any]:
    """Build a minimal context for E4_HEAL steps."""
    ctx: dict[str, Any] = {
        "jd_data": "Software Engineer role requiring Python expertise",
        "master_resume_data": json.dumps({"name": "Jane Doe", "skills": ["Python"]}),
        "claim_source_refs": "ref-1,ref-2",
        "unsupported_claims": "claim-A,claim-B",
        "run_id": "heal-run-1",
        "trace_id": "heal-trace-1",
    }
    ctx.update(overrides)
    return ctx


# ---------------------------------------------------------------------------
# FactCheckStep
# ---------------------------------------------------------------------------

class TestFactCheckStep:
    def test_compiles_artifact(self):
        from apps_rg.l2_recipe.steps import FactCheckStep
        step = FactCheckStep()
        result = step(_heal_context())
        assert result["exit_code"] == 0
        assert result["step_id"] == "fact_check_generated_resume"
        art = result["compiled_prompt_artifact"]
        assert art["compile_status"] == "PA_L2_HANDOFF_READY"
        assert art["prompt_id"] == "apps_rg.resume_fact_check_v1"

    def test_artifact_has_required_hashes(self):
        from apps_rg.l2_recipe.steps import FactCheckStep
        result = FactCheckStep()(_heal_context())
        art = result["compiled_prompt_artifact"]
        for field in (
            "prompt_bom_hash", "prompt_registry_hash", "prompt_template_hash",
            "manifest_hash", "canonical_slot_bytes_hash", "artifact_hash",
        ):
            assert art.get(field), f"Missing hash: {field}"

    def test_requires_pa_flag(self):
        from apps_rg.l2_recipe.steps import FactCheckStep
        assert FactCheckStep.REQUIRES_PA is True

    def test_step_id_matches_registry(self):
        from apps_rg.l2_recipe.steps import FactCheckStep
        assert FactCheckStep.STEP_ID == "fact_check_generated_resume"


# ---------------------------------------------------------------------------
# ClaimOmissionStep
# ---------------------------------------------------------------------------

class TestClaimOmissionStep:
    def test_compiles_artifact(self):
        from apps_rg.l2_recipe.steps import ClaimOmissionStep
        step = ClaimOmissionStep()
        result = step(_heal_context())
        assert result["exit_code"] == 0
        assert result["step_id"] == "omit_unsupported_resume_claims"
        art = result["compiled_prompt_artifact"]
        assert art["compile_status"] == "PA_L2_HANDOFF_READY"
        assert art["prompt_id"] == "apps_rg.unsupported_claim_omission_v1"

    def test_artifact_has_required_hashes(self):
        from apps_rg.l2_recipe.steps import ClaimOmissionStep
        result = ClaimOmissionStep()(_heal_context())
        art = result["compiled_prompt_artifact"]
        for field in (
            "prompt_bom_hash", "prompt_registry_hash", "prompt_template_hash",
            "manifest_hash", "canonical_slot_bytes_hash", "artifact_hash",
        ):
            assert art.get(field), f"Missing hash: {field}"

    def test_requires_pa_flag(self):
        from apps_rg.l2_recipe.steps import ClaimOmissionStep
        assert ClaimOmissionStep.REQUIRES_PA is True

    def test_step_id_matches_registry(self):
        from apps_rg.l2_recipe.steps import ClaimOmissionStep
        assert ClaimOmissionStep.STEP_ID == "omit_unsupported_resume_claims"


# ---------------------------------------------------------------------------
# BulletDiversityRepairStep
# ---------------------------------------------------------------------------

class TestBulletDiversityRepairStep:
    def test_compiles_artifact(self):
        from apps_rg.l2_recipe.steps import BulletDiversityRepairStep
        step = BulletDiversityRepairStep()
        result = step(_heal_context())
        assert result["exit_code"] == 0
        assert result["step_id"] == "repair_bullet_diversity"
        art = result["compiled_prompt_artifact"]
        assert art["compile_status"] == "PA_L2_HANDOFF_READY"
        assert art["prompt_id"] == "apps_rg.bullet_diversity_repair_v1"

    def test_artifact_has_required_hashes(self):
        from apps_rg.l2_recipe.steps import BulletDiversityRepairStep
        result = BulletDiversityRepairStep()(_heal_context())
        art = result["compiled_prompt_artifact"]
        for field in (
            "prompt_bom_hash", "prompt_registry_hash", "prompt_template_hash",
            "manifest_hash", "canonical_slot_bytes_hash", "artifact_hash",
        ):
            assert art.get(field), f"Missing hash: {field}"

    def test_requires_pa_flag(self):
        from apps_rg.l2_recipe.steps import BulletDiversityRepairStep
        assert BulletDiversityRepairStep.REQUIRES_PA is True

    def test_step_id_matches_registry(self):
        from apps_rg.l2_recipe.steps import BulletDiversityRepairStep
        assert BulletDiversityRepairStep.STEP_ID == "repair_bullet_diversity"


# ---------------------------------------------------------------------------
# Cross-step: all E4_HEAL steps produce distinct template_ids
# ---------------------------------------------------------------------------

class TestE4HealStepDistinctness:
    def test_distinct_template_ids(self):
        from apps_rg.l2_recipe.steps import (
            FactCheckStep, ClaimOmissionStep, BulletDiversityRepairStep,
        )
        ctx = _heal_context()
        ids = set()
        for StepCls in (FactCheckStep, ClaimOmissionStep, BulletDiversityRepairStep):
            result = StepCls()(ctx)
            ids.add(result["compiled_prompt_artifact"]["template_id"])
        assert len(ids) == 3

    def test_all_use_e4_heal_stage(self):
        """All E4_HEAL templates should be registered with allowed_stage E4_HEAL."""
        import yaml
        from pathlib import Path
        registry_path = Path("apps_rg/prompt_assembly/prompt_registry.yaml")
        with open(registry_path) as f:
            registry = yaml.safe_load(f)
        e4_templates = [
            "resume_fact_check_v1",
            "unsupported_claim_omission_v1",
            "bullet_diversity_repair_v1",
        ]
        for tid in e4_templates:
            entry = registry["templates"][tid]
            assert entry["allowed_stage"] == "E4_HEAL", f"{tid} stage != E4_HEAL"
