"""Drift ratchet: Unify/IBM lanes must not restate X2 gate catalogs in runtime I0."""

from __future__ import annotations

import os
import re
from pathlib import Path

from apps_rg.runtime.dispatch.ibm_bullets_pa import compile_ibm_bullets_prompt
from apps_rg.runtime.dispatch.ibm_narrative_pa import compile_ibm_narrative_prompt
from apps_rg.runtime.dispatch.unify_bullets_pa import compile_unify_bullets_prompt
from apps_rg.runtime.dispatch.unify_narrative_pa import compile_unify_narrative_prompt
from apps_rg.runtime.sections.ibm_bullets_pa import _legacy_i0 as ibm_bullets_i0
from apps_rg.runtime.sections.unify_bullets_pa import _legacy_i0 as unify_bullets_i0

REPO = Path(__file__).resolve().parents[3]

_X2_UNIFY = re.compile(r"\bx2_unify_[a-z0-9_]+\b")
_X2_IBM = re.compile(r"\bx2_ibm_[a-z0-9_]+\b")
_X2_SHARED = re.compile(r"\bx2_claim_ledger_[a-z0-9_]+\b")


def _minimal_proof_metadata() -> dict:
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority

    meta = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
    }
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=str(meta["graph_ref"]),
        ledger_ref="apps_rg/fact_inventory/candidate_fact_ledger.json",
        skills_authority_status="PASS",
    )
    return meta


def _unify_header() -> dict:
    return {
        "employer": "Unify Consulting",
        "title": "SVP Engineering, Agentic AI Platforms",
        "location": "Boca Raton, FL",
        "start_date": "2023-02",
        "end_date": "present",
    }


def _ibm_header() -> dict:
    return {
        "employer": "IBM",
        "title": "Lead Client Partner",
        "location": "Edgewater, NJ",
        "start_date": "2017-04",
        "end_date": "2022-10",
    }


def test_runtime_i0_modules_contain_core_law_marker_no_x2_literals():
    payload_ub = {
        "unify_header": _unify_header(),
        "selected_fact_plan": {"facts": [{"fact_id": "bul_unify_001", "claim_text": "x"}]},
    }
    payload_ib = {
        "ibm_header": _ibm_header(),
        "selected_fact_plan": {"facts": [{"fact_id": "bul_ibm_001", "claim_text": "x"}]},
    }
    for body in (unify_bullets_i0(payload_ub), ibm_bullets_i0(payload_ib)):
        assert "UNIFY_IBM_PROMPT_CORE_LAW_V3" in body
        assert "pa_core_law_v1.yaml" in body
        assert not _X2_UNIFY.search(body)
        assert not _X2_IBM.search(body)
        assert not _X2_SHARED.search(body)


def test_yaml_specs_trimmed_sovereign_oath_no_x2_in_oath_block():
    for name in (
        "unify_bullet_tailor_v1.yaml",
        "unify_position_narrative_v1.yaml",
        "ibm_bullet_tailor_v1.yaml",
        "ibm_position_narrative_v1.yaml",
    ):
        raw = (REPO / "apps_rg/prompt_assembly/templates" / name).read_text(encoding="utf-8")
        assert "UNIFY_IBM_PROMPT_CORE_LAW_V3" in raw
        assert "pa_core_law_v1.yaml" in raw
        oath_start = raw.find("sovereign_oath:")
        assert oath_start >= 0
        oath_block = raw[oath_start : oath_start + 1200]
        assert not _X2_UNIFY.search(oath_block)
        assert not _X2_IBM.search(oath_block)


def test_compiled_unify_bullets_lists_x2_only_under_product_shape():
    from apps_rg.runtime.spine.front_contracts import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    os.environ.setdefault("PYTEST_CURRENT_TEST", "test_unify_ibm_prompt_drift_ratchet")
    activate_fixture_dev_bypass(non_product_certified=True)
    payload = {
        "product_visible": False,
        "run_id": "w4_ub",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "unify_header": _unify_header(),
        "selected_fact_plan": {
            "facts": [{"fact_id": "bul_unify_001", "claim_text": "Architected platform.", "metric_raw": ""}]
        },
        "proof_pool_metadata": _minimal_proof_metadata(),
        "allowed_fact_ids": ["bul_unify_001"],
    }
    out = compile_unify_bullets_prompt(payload, run_id="w4_ub")
    content = out.artifact.messages[0]["content"]
    assert "PRODUCT_SHAPE" in content
    ps = content.index("PRODUCT_SHAPE")
    i0_idx = content.find("<!-- SLOT: I0 -->")
    i0_end = content.find("<!-- SLOT: C0 -->", i0_idx)
    i0_seg = content[i0_idx:i0_end] if i0_idx >= 0 and i0_end > i0_idx else ""
    assert not _X2_UNIFY.search(i0_seg)
    assert "x2_unify_bullet_count_6" in content[ps:]
    deactivate_fixture_dev_bypass()


def test_compiled_ibm_narrative_core_law_and_product_shape():
    from apps_rg.runtime.spine.front_contracts import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    os.environ.setdefault("PYTEST_CURRENT_TEST", "test_unify_ibm_prompt_drift_ratchet")
    activate_fixture_dev_bypass(non_product_certified=True)
    payload = {
        "product_visible": False,
        "run_id": "w4_in",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI",
        "briefing": "regulated",
        "candidate_name": "",
        "ibm_header": _ibm_header(),
        "selected_fact_plan": {"facts": [{"fact_id": "bul_ibm_001", "claim_text": "Cloud programs."}]},
        "allowed_fact_ids": ["bul_ibm_001"],
        "proof_pool_metadata": _minimal_proof_metadata(),
    }
    out = compile_ibm_narrative_prompt(payload, "", run_id="w4_in")
    content = out.artifact.messages[0]["content"]
    assert "UNIFY_IBM_PROMPT_CORE_LAW_V3" in content
    assert "PRODUCT_SHAPE" in content
    assert "x2_ibm_narrative_exactly_one_sentence" in content
    deactivate_fixture_dev_bypass()
