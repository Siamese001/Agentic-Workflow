"""W11-M4A/M4B — parity between sections SSOT and dispatch compatibility re-exports."""

from __future__ import annotations

import importlib

import pytest

from apps_rg.runtime.dispatch import prompt_trace_reasoning as dispatch_ptr
from apps_rg.runtime.sections.competencies_lane_runtime import (
    collect_employment_bullets as dispatch_collect,
)
from apps_rg.runtime.sections import prompt_trace_reasoning as sections_ptr
from apps_rg.runtime.sections.resume_employment_bullets import (
    collect_employment_bullets as sections_collect,
)

_PA_PAIRS: list[tuple[str, str, str]] = [
    ("headline_pa", "compile_headline_prompt"),
    ("competencies_pa", "compile_competencies_prompt"),
    ("ibm_bullets_pa", "compile_ibm_bullets_prompt"),
    ("ibm_narrative_pa", "compile_ibm_narrative_prompt"),
    ("unify_bullets_pa", "compile_unify_bullets_prompt"),
    ("unify_narrative_pa", "compile_unify_narrative_prompt"),
    ("executive_summary_pa", "compile_executive_summary_prompt"),
]


def test_prompt_trace_reasoning_dispatch_reexport_matches_sections() -> None:
    assert (
        dispatch_ptr.attach_reasoning_to_prompt_trace
        is sections_ptr.attach_reasoning_to_prompt_trace
    )


def test_collect_employment_bullets_dispatch_reexport_matches_sections() -> None:
    base = {
        "facts": {
            "employment": [
                {
                    "employer": "ACME",
                    "bullets": [
                        {"bullet_id": "b1", "text": "Led platform migration."},
                    ],
                }
            ]
        }
    }
    rows_a, allowed_a, lowers_a = sections_collect(base)
    rows_b, allowed_b, lowers_b = dispatch_collect(base)
    assert rows_a == rows_b
    assert allowed_a == allowed_b
    assert lowers_a == lowers_b


@pytest.mark.parametrize("module_name,symbol", _PA_PAIRS)
def test_compile_prompt_dispatch_reexport_matches_sections(
    module_name: str, symbol: str
) -> None:
    dispatch_mod = importlib.import_module(f"apps_rg.runtime.dispatch.{module_name}")
    sections_mod = importlib.import_module(f"apps_rg.runtime.sections.{module_name}")
    assert getattr(dispatch_mod, symbol) is getattr(sections_mod, symbol)


def test_competencies_lane_execution_import_surface() -> None:
    from apps_rg.runtime.sections import competencies_lane_execution as cle

    assert "run_competencies_lane_execution" in cle.__all__
    assert "run_competencies_execution" in cle.__all__


def test_ibm_narrative_lane_execution_import_surface() -> None:
    from apps_rg.runtime.sections import ibm_narrative_lane_execution as ile

    assert "run_ibm_narrative_lane_execution" in ile.__all__
    assert "run_ibm_narrative_execution" in ile.__all__


def test_dispatch_execution_reexports_lane_ssot() -> None:
    from apps_rg.runtime.dispatch import competencies_dispatch as cd
    from apps_rg.runtime.dispatch import ibm_narrative_dispatch as ind
    from apps_rg.runtime.sections import competencies_lane_execution as cle
    from apps_rg.runtime.sections import ibm_narrative_lane_execution as ile

    assert cd.run_competencies_execution is cle.run_competencies_execution
    assert cd.run_competencies_lane_execution is cle.run_competencies_lane_execution
    assert ind.run_ibm_narrative_execution is ile.run_ibm_narrative_execution
    assert ind.run_ibm_narrative_lane_execution is ile.run_ibm_narrative_lane_execution


def test_phase_d2_extracted_helpers_dispatch_reexport_is_sections_ssot() -> None:
    from apps_rg.runtime.dispatch import competencies_dispatch as cd
    from apps_rg.runtime.dispatch import ibm_narrative_dispatch as ind
    from apps_rg.runtime.exit import competencies_x3 as cx3
    from apps_rg.runtime.sections import companion_lane_context as clc
    from apps_rg.runtime.sections import competencies_lane_defaults as cld
    from apps_rg.runtime.sections import competencies_term_phrase as ctp
    from apps_rg.runtime.sections import ibm_narrative_lane_defaults as ind_def
    from apps_rg.runtime.sections import ibm_narrative_metric_trim as inmt
    from apps_rg.runtime.sections import lane_artifact_io as laio

    assert cd.sha16 is laio.sha16
    assert cd.write_json is laio.write_json
    assert ind.sha16 is laio.sha16
    assert ind.write_json is laio.write_json
    assert cd.term_phrase is ctp.term_phrase
    assert cd.load_companion_context is clc.load_companion_context
    assert cd.build_resume_support_blob is clc.build_resume_support_blob
    assert cd.build_c0_proof_support_blob is clc.build_c0_proof_support_blob
    assert cd.COMPANION_LANES is clc.COMPANION_LANES
    assert cd.clarify_x3_for_competencies_live_provider_preflight is (
        cx3.clarify_x3_for_competencies_live_provider_preflight
    )
    assert cd.PROMPT_ID is cld.PROMPT_ID
    assert cd.JD_TEXT_DEFAULT is cld.JD_TEXT_DEFAULT
    assert ind.PROMPT_ID is ind_def.PROMPT_ID
    assert ind.REPO_ROOT == ind_def.REPO_ROOT
    assert ind.collapse_narrative_sentence_for_companion_metric_budget is (
        inmt.collapse_narrative_sentence_for_companion_metric_budget
    )
    assert ind.truncate_narrative_after_first_metric_hit is inmt.truncate_narrative_after_first_metric_hit

    from apps_rg.runtime.sections import lane_base_resume as lbr

    assert cd.load_base_resume is lbr.load_base_resume
    assert ind.load_base_resume is lbr.load_base_resume
