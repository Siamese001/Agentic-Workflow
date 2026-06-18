"""W5: rollup drift enforcement — one PRODUCT_SHAPE block per generated lane compile."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime.dispatch.headline_pa import compile_headline_prompt
from apps_rg.runtime.dispatch.ibm_bullets_pa import compile_ibm_bullets_prompt
from apps_rg.runtime.dispatch.ibm_narrative_pa import compile_ibm_narrative_prompt
from apps_rg.runtime.dispatch.unify_bullets_pa import compile_unify_bullets_prompt
from apps_rg.runtime.dispatch.unify_narrative_pa import compile_unify_narrative_prompt
from apps_rg.runtime.product_evidence_authority import build_evidence_authority
from apps_rg.runtime.sections.competencies_pa import compile_competencies_prompt
from apps_rg.runtime.sections.competency_capability_evidence import (
    attach_competency_bundles_to_proof_pool_metadata,
)
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)
from apps_rg.runtime.sections.headline_positioning_evidence import (
    attach_headline_positioning_bundles_to_proof_pool_metadata,
)
from apps_rg.runtime.sections.unify_role_episode_evidence import (
    attach_role_episode_bundles_to_proof_pool_metadata,
)
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from tests.unit.apps_rg.prompt_assembly.core_law_drift_helpers import (
    assert_i0_segment_has_no_x2_literals,
    assert_single_product_shape_block,
    extract_i0_compiled_segment,
)

REPO_ROOT = Path(__file__).resolve().parents[4]

_W5_DRIFT_MODULES = (
    "tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py",
    "tests/unit/apps_rg/test_headline_prompt_drift_ratchet.py",
    "tests/unit/apps_rg/test_competencies_prompt_drift_ratchet.py",
    "tests/unit/apps_rg/test_unify_ibm_prompt_drift_ratchet.py",
    "tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w1.py",
)


def _minimal_proof_metadata(section_id: str | None = None) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
    }
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=str(meta["graph_ref"]),
        ledger_ref="apps_rg/fact_inventory/candidate_fact_ledger.json",
        skills_authority_status="PASS",
    )
    if section_id in {"headline", "competencies", "unify_bullets"}:
        plan, _, _ = build_selected_graph_evidence_plan_for_section(
            repo_root=REPO_ROOT,
            section_id=section_id,
            target_role="SVP Engineering",
            jd_text="agentic multi-agent GraphRAG runtime platform control plane",
            briefing_text="regulated enterprise",
        )
        meta["selected_graph_evidence_plan"] = plan
        if section_id == "headline":
            return attach_headline_positioning_bundles_to_proof_pool_metadata(
                meta,
                section_id="headline",
            )
        if section_id == "competencies":
            return attach_competency_bundles_to_proof_pool_metadata(
                meta,
                section_id="competencies",
            )
        if section_id == "unify_bullets":
            return attach_role_episode_bundles_to_proof_pool_metadata(
                meta,
                section_id="unify_bullets",
            )
    return meta


def _unify_header() -> dict[str, Any]:
    return {
        "employer": "Unify Consulting",
        "title": "SVP Engineering, Agentic AI Platforms",
        "location": "Boca Raton, FL",
        "start_date": "2023-02",
        "end_date": "present",
    }


def _ibm_header() -> dict[str, Any]:
    return {
        "employer": "IBM",
        "title": "Lead Client Partner",
        "location": "Edgewater, NJ",
        "start_date": "2017-04",
        "end_date": "2022-10",
    }


@pytest.fixture(autouse=True)
def _w5_fixture_bypass():
    os.environ.setdefault("PYTEST_CURRENT_TEST", "test_sections_pa_core_law_w5_rollup")
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


@pytest.mark.parametrize(
    ("section_id", "sample_gate_id", "x2_pattern"),
    [
        ("headline", "x2_headline_pipe_four_segments", re.compile(r"\bx2_headline_[a-z0-9_]+\b")),
        (
            "competencies",
            "x2_competencies_min_category_count",
            re.compile(r"\bx2_competenc(?:y|ies)_[a-z0-9_]+\b"),
        ),
        ("unify_bullets", "x2_unify_bullet_count_6", re.compile(r"\bx2_unify_[a-z0-9_]+\b")),
        (
            "unify_narrative",
            "x2_unify_narrative_exactly_one_sentence",
            re.compile(r"\bx2_unify_[a-z0-9_]+\b"),
        ),
        ("ibm_bullets", "x2_ibm_bullet_count_5", re.compile(r"\bx2_ibm_[a-z0-9_]+\b")),
        (
            "ibm_narrative",
            "x2_ibm_narrative_exactly_one_sentence",
            re.compile(r"\bx2_ibm_[a-z0-9_]+\b"),
        ),
    ],
)
def test_rollout_lane_single_product_shape_and_i0_without_x2_catalog(
    section_id: str,
    sample_gate_id: str,
    x2_pattern: re.Pattern[str],
) -> None:
    meta = _minimal_proof_metadata(section_id=section_id)
    base = {
        "product_visible": False,
        "run_id": f"w5_{section_id}",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI platform",
        "briefing": "regulated enterprise",
        "proof_pool_metadata": meta,
        "allowed_fact_ids": ["bul_unify_001"],
    }

    if section_id == "headline":
        payload = {
            **base,
            "selected_fact_plan": {
                "section_id": "headline",
                "selection_method": "test",
                "required_fact_ids": ["bul_unify_001"],
                "facts": [],
            },
        }
        out = compile_headline_prompt(
            payload,
            companion_context="",
            fact_lines="- bul_unify_001: Example bullet with agentic platform delivery",
            forbidden_employer_lines="- unify\n- ibm",
            run_id=payload["run_id"],
        )
    elif section_id == "competencies":
        payload = {
            **base,
            "selected_fact_plan": {
                "section_id": "competencies",
                "selection_method": "test",
                "required_fact_ids": ["bul_unify_001"],
                "facts": [],
            },
        }
        out = compile_competencies_prompt(
            payload,
            companion_context="",
            fact_lines="- bul_unify_001: Example bullet with agentic platform delivery",
            run_id=payload["run_id"],
        )
    elif section_id == "unify_bullets":
        payload = {
            **base,
            "unify_header": _unify_header(),
            "selected_fact_plan": {
                "facts": [
                    {
                        "fact_id": "bul_unify_001",
                        "claim_text": "Architected platform.",
                        "metric_raw": "",
                    }
                ]
            },
        }
        out = compile_unify_bullets_prompt(payload, run_id=payload["run_id"])
    elif section_id == "unify_narrative":
        payload = {
            **base,
            "candidate_name": "",
            "unify_header": _unify_header(),
            "selected_fact_plan": {
                "facts": [
                    {
                        "fact_id": "bul_unify_001",
                        "claim_text": "Architected platform.",
                        "metric_raw": "",
                    }
                ]
            },
            "companion_unify_bullets_status": "ACCEPTED_FINALIZED",
            "companion_unify_bullets_reason": "w5",
        }
        out = compile_unify_narrative_prompt(payload, "", run_id=payload["run_id"])
    elif section_id == "ibm_bullets":
        payload = {
            **base,
            "allowed_fact_ids": ["bul_ibm_001"],
            "ibm_header": _ibm_header(),
            "selected_fact_plan": {
                "facts": [
                    {
                        "fact_id": "bul_ibm_001",
                        "claim_text": "Cloud programs.",
                        "metric_raw": "",
                    }
                ]
            },
        }
        out = compile_ibm_bullets_prompt(payload, run_id=payload["run_id"])
    elif section_id == "ibm_narrative":
        payload = {
            **base,
            "candidate_name": "",
            "allowed_fact_ids": ["bul_ibm_001"],
            "ibm_header": _ibm_header(),
            "selected_fact_plan": {
                "facts": [
                    {
                        "fact_id": "bul_ibm_001",
                        "claim_text": "Cloud programs.",
                        "metric_raw": "",
                    }
                ]
            },
        }
        out = compile_ibm_narrative_prompt(payload, "", run_id=payload["run_id"])
    else:
        raise AssertionError(f"unknown section_id {section_id!r}")

    content = out.artifact.messages[0]["content"]
    assert out.section_id == section_id
    assert_single_product_shape_block(content, sample_gate_id=sample_gate_id)
    i0_seg = extract_i0_compiled_segment(content)
    assert_i0_segment_has_no_x2_literals(i0_seg, x2_pattern)


def test_w5_drift_module_manifest_is_stable():
    """Document the W5 pytest surface (plan gate enumeration)."""
    assert len(_W5_DRIFT_MODULES) >= 4
    for mod in _W5_DRIFT_MODULES:
        assert mod.startswith("tests/")
