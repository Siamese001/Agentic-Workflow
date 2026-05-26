"""Prompt/code product-shape drift guard for all generated lanes."""

from __future__ import annotations

import re

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_product_shape_ssot import (
    EXEC_SUMMARY_MAX_SENTENCES,
    EXEC_SUMMARY_MAX_WORDS,
    EXEC_SUMMARY_MIN_SENTENCES,
    HEADLINE_WORD_MAX,
    HEADLINE_WORD_MIN,
    section_product_shape,
)
from apps_rg.runtime.sections.section_prompt_drift_audit import (
    audit_all_generated_lanes,
    assert_zero_drift,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MAX_SENTENCES as X2_MAX_SENT,
    EXEC_SUMMARY_MAX_WORDS as X2_MAX_WORDS,
    EXEC_SUMMARY_MIN_SENTENCES as X2_MIN_SENT,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import SC_PATH_COUNT_BY_LANE
from tests.unit.apps_rg.section_rigor.lane_registry import spec_for_lane


def test_ssot_imports_match_x2_constants() -> None:
    assert EXEC_SUMMARY_MIN_SENTENCES == X2_MIN_SENT
    assert EXEC_SUMMARY_MAX_SENTENCES == X2_MAX_SENT
    assert EXEC_SUMMARY_MAX_WORDS == X2_MAX_WORDS


def test_all_generated_lanes_have_product_shape() -> None:
    for lane in GENERATED_LANES:
        shape = section_product_shape(lane)
        assert shape.section_id == lane


def test_zero_template_drift_all_lanes() -> None:
    assert_zero_drift()


def test_drift_audit_reports_no_violations() -> None:
    violations = audit_all_generated_lanes()
    assert violations == [], "\n".join(f"{v.section_id}:{v.kind}:{v.detail}" for v in violations)


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_critical_gates_cover_ssot_product_shape(lane: str) -> None:
    shape = section_product_shape(lane)
    spec = spec_for_lane(lane)
    missing = [g for g in shape.required_gate_ids if g not in spec.critical_gates]
    assert not missing, f"{lane} missing critical gates: {missing}"


def test_unify_pool_shape_ssot() -> None:
    shape = section_product_shape("unify_bullets")
    assert str(SC_PATH_COUNT_BY_LANE["unify_bullets"]) in shape.shape_summary
    assert "Claude" in shape.shape_summary
    assert "HEAVY" not in shape.shape_summary


def test_ibm_pool_shape_ssot() -> None:
    shape = section_product_shape("ibm_bullets")
    assert str(SC_PATH_COUNT_BY_LANE["ibm_bullets"]) in shape.shape_summary
    assert "HEAVY" not in shape.shape_summary


def test_headline_word_band_ssot() -> None:
    shape = section_product_shape("headline")
    assert f"{HEADLINE_WORD_MIN}-{HEADLINE_WORD_MAX}" in shape.shape_summary


def test_product_shape_block_format() -> None:
    from apps_rg.runtime.sections.section_product_shape_ssot import format_product_shape_prompt_block

    block = format_product_shape_prompt_block("executive_summary")
    assert "PRODUCT_SHAPE" in block
    assert "Bounds gates" in block
    assert "Proof gates" in block
    assert "Style gates" in block
    assert "x2_exec_summary_sentence_count_6" in block
    assert "x2_exec_summary_paragraph_max_words" in block
    assert "fit_to_evidence" in block


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_product_shape_gate_ids_subset_of_lane_critical(lane: str) -> None:
    from apps_rg.runtime.sections.section_product_shape_ssot import product_shape_gate_ids_for_lane

    spec = spec_for_lane(lane)
    missing = product_shape_gate_ids_for_lane(lane) - spec.critical_gates
    assert not missing, f"{lane} SSOT gates not in lane_registry: {sorted(missing)}"


def test_compiled_prompt_includes_product_shape_block() -> None:
    from apps_rg.runtime.dispatch.input_authority_prompt_block import (
        augment_section_compiled_with_input_authority,
    )
    from apps_rg.prompt_assembly.contracts import CompiledPromptArtifact

    art = CompiledPromptArtifact(
        template_id="executive_summary.generate_scratch_v1",
        messages=[{"role": "user", "content": "base prompt"}],
    )
    from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt

    compiled = SectionCompiledPrompt(
        section_id="executive_summary",
        apps_rg_prompt_template_ref="apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml",
        artifact=art,
    )
    out = augment_section_compiled_with_input_authority(
        compiled,
        allowed_source_fact_ids=["bul_unify_001"],
        skills_authority_metadata={
            "evidence_authority": {
                "authority": "augmented_skills_graph",
                "graph_ref": "artifacts/adg/augmented_skills_graph.json",
                "ledger_ref": "artifacts/adg/candidate_fact_ledger.json",
                "skills_authority_status": "PASS",
            },
            "augmented_skills_graph_present": True,
            "graph_ref": "artifacts/adg/augmented_skills_graph.json",
            "graph_version": "test",
        },
    )
    content = str(out.artifact.messages[-1]["content"])
    assert "PRODUCT_SHAPE" in content
    assert "INPUT_AUTHORITY" in content
    assert re.search(r"exactly\s+6|6\s+sentences", content, re.IGNORECASE)
    assert not re.search(r"4\s*[-–]\s*5\s+dense", content, re.IGNORECASE)
