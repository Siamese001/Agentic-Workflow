"""W0 red-before-green tests for prompt-judge-x2-alignment-closeout-c8e4a2.

These encode known defects; they must turn green in the same PR as W1 fixes.
Do not merge this file alone with failing tests on the default branch.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from apps_rg.runtime.judges.executive_summary_x1d import RUBRIC, _build_judge_user_prompt
from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
    EXEC_SUMMARY_RUBRIC_DIMENSION_IDS,
)
from apps_rg.runtime.sections.competencies_pa import build_competencies_assembly_input
from apps_rg.runtime.sections.executive_summary_pa import (
    format_graph_only_quality_guardrails_block,
)
from apps_rg.runtime.sections.section_prompt_authority_ssot import (
    P0_ALIGNMENT_LANES,
    assert_p0_lanes_executable_corpus_non_empty,
    collect_executable_prompt_corpus,
    resolve_repo_template_path,
)
from apps_rg.runtime.sections.section_prompt_drift_audit import _repo_path


def _rubric_dimension_ids(rubric: str) -> set[str]:
    return set(re.findall(r"^\s*\d+\.\s*([\w]+):", rubric, flags=re.MULTILINE))


def test_exec_summary_x1d_rubric_lists_all_ssot_dimensions() -> None:
    """Live judge RUBRIC must list every EXEC_SUMMARY_RUBRIC_DIMENSION_IDS entry."""
    listed = _rubric_dimension_ids(RUBRIC)
    missing = set(EXEC_SUMMARY_RUBRIC_DIMENSION_IDS) - listed
    assert not missing, (
        f"executive_summary_x1d.RUBRIC missing dimensions: {sorted(missing)}; "
        f"listed={sorted(listed)}"
    )
    user_prompt = _build_judge_user_prompt("Six sentence stub.", [])
    for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS:
        assert dim in user_prompt, f"dimension {dim!r} absent from _build_judge_user_prompt corpus"


def test_exec_summary_pa_claim_ledger_guidance_consistent() -> None:
    """u0 and graph-only guard must not contradict on one-row-per-sentence vs 3-6 rows."""
    from apps_rg.runtime.sections.executive_summary_pa import build_executive_summary_assembly_input

    stub_payload = {
        "target_title": "SVP Engineering",
        "target_company": "Example",
        "jd_text": "",
        "briefing": "",
        "product_visible": False,
        "allowed_fact_ids": ["bul_unify_001"],
        "selected_fact_plan": {
            "facts": [{"fact_id": "bul_unify_001", "claim_text": "delivery"}],
        },
    }
    assembly = build_executive_summary_assembly_input(
        stub_payload,
        request_id="w0",
        run_id="w0",
        trace_root="executive_summary:w0",
    )
    u0 = str(assembly.u0_user_task or "")
    graph_guard = format_graph_only_quality_guardrails_block()
    guard_lower = graph_guard.lower()
    u0_lower = u0.lower()
    assert "do not default to one row per sentence" in guard_lower
    assert "3-6" in graph_guard or "3–6" in graph_guard
    assert "one claim_ledger row per sentence" not in guard_lower
    assert "one claim_ledger row per sentence" not in u0_lower
    assert "not one sentence per brushstroke" in u0_lower


def test_competencies_u0_schema_matches_x2() -> None:
    """U0 must teach categories/text keys, not competencies/term-only contract."""
    assembly = build_competencies_assembly_input(
        {
            "target_title": "SVP",
            "target_company": "Co",
            "jd_text": "",
            "briefing": "",
            "product_visible": False,
            "allowed_fact_ids": ["bul_unify_001"],
            "canonical_final_evidence_contract": {"allowed_fact_ids": ["bul_unify_001"]},
            "proof_pool_metadata": {},
            "selected_fact_plan": {
                "section_id": "competencies",
                "selection_method": "canonical_base_resume_employment_bullets",
                "required_fact_ids": [],
            },
        },
        "- bul_unify_001: x\n",
        request_id="w0",
        run_id="w0",
        trace_root="competencies:w0",
    )
    u0 = str(assembly.u0_user_task or "")
    assert "categories" in u0
    assert '"text"' in u0 or "'text'" in u0
    assert "- competencies: array" not in u0


def test_resolve_repo_template_path_safe() -> None:
    """Safe resolver (W1.4 target) rejects absolute and traversal refs."""
    ref = "apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml"
    path = resolve_repo_template_path(ref)
    assert path.is_file()
    with pytest.raises(ValueError, match="absolute"):
        resolve_repo_template_path("/etc/passwd")
    with pytest.raises(ValueError, match="traversal"):
        resolve_repo_template_path("apps_rg/../../../outside.txt")


def test_drift_audit_repo_path_rejects_absolute_and_traversal() -> None:
    """Drift audit _repo_path must use safe resolution (W1.4 — red until wired)."""
    with pytest.raises((ValueError, OSError)):
        _repo_path("/etc/passwd")
    with pytest.raises((ValueError, OSError)):
        _repo_path("apps_rg/../../../outside.txt")
    resolved = _repo_path("apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml")
    assert resolved.is_file()


def test_prompt_authority_executable_corpus_non_empty() -> None:
    assert P0_ALIGNMENT_LANES.issubset(
        frozenset(
            {
                "executive_summary",
                "competencies",
                "unify_bullets",
                "ibm_bullets",
                "unify_narrative",
                "ibm_narrative",
            }
        )
    )
    assert_p0_lanes_executable_corpus_non_empty()
    for section_id in sorted(P0_ALIGNMENT_LANES):
        corpus = collect_executable_prompt_corpus(section_id)
        assert len(corpus) > 200, section_id
