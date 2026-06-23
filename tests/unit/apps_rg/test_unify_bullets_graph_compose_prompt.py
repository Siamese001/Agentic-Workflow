"""Unify bullets: graph-compose C0 pack and compile guards."""
from __future__ import annotations

import os
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane
from apps_rg.runtime.dispatch.unify_bullets_pa import compile_unify_bullets_prompt
from apps_rg.runtime.sections.unify_bullets_graph_evidence import (
    GRAPH_BULLET_EVIDENCE_PACK_MARKER,
    format_unify_graph_bullet_evidence_pack,
)
from apps_rg.runtime.sections.unify_bullets_pa import _legacy_i0
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)
from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets
from apps_rg.runtime.sections.unify_role_episode_evidence import (
    attach_role_episode_bundles_to_proof_pool_metadata,
    format_unify_role_episode_evidence_pack,
    resolve_unify_bullet_slot_bundle_map,
)
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)

REPO = Path(__file__).resolve().parents[3]
ANTHROPIC_JD = REPO / "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt"
ANTHROPIC_BRIEFING = (
    REPO / "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_briefing.md"
)

_FORBIDDEN_C0 = re.compile(
    r"CANONICAL UNIFY FACTS|rewrite from these",
    re.IGNORECASE,
)


@pytest.fixture(autouse=True)
def _fixture_bypass():
    os.environ.setdefault("PYTEST_CURRENT_TEST", "test_unify_bullets_graph_compose_prompt")
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _minimal_proof_metadata(*, skill_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority

    meta: dict[str, Any] = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
        "augmented_skills_graph_present": True,
        "graph_version": "test",
    }
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=str(meta["graph_ref"]),
        ledger_ref="apps_rg/fact_inventory/candidate_fact_ledger.json",
        skills_authority_status="PASS",
    )
    if skill_rows is not None:
        meta["selected_skill_rows"] = skill_rows
    return meta


def _unify_compile_proof_meta(*, skill_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=REPO,
        section_id="unify_bullets",
        target_role="SVP Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform control plane",
        briefing_text="regulated enterprise",
    )
    meta = _minimal_proof_metadata(skill_rows=skill_rows)
    meta["selected_graph_evidence_plan"] = plan
    return attach_role_episode_bundles_to_proof_pool_metadata(meta, section_id="unify_bullets")


def _unify_header() -> dict[str, str]:
    return {
        "employer": "Unify Consulting",
        "title": "SVP Engineering, Agentic AI Platforms",
        "location": "Boca Raton, FL",
        "start_date": "2023-02",
        "end_date": "present",
    }


def _six_slot_facts() -> list[dict[str, Any]]:
    return [
        {
            "fact_id": f"bul_unify_{i:03d}",
            "claim_text": f"Archive bullet prose slot {i} with governed platform delivery themes.",
            "ledger_candidate_fact_id": f"fact_engineering_platform_{i:03d}",
            "metric_raw": "six months to three weeks" if i == 4 else "",
            "technologies": ["graphrag"] if i == 1 else [],
            "role_families_supported": ["ENGINEERING_PLATFORM"],
        }
        for i in range(1, 7)
    ]


def test_graph_evidence_pack_lists_bound_skills_per_slot() -> None:
    skill_rows = [
        {
            "skill_id": "skill_governed_agentic_systems_architecture",
            "allowed_phrases": ["governed agentic systems architecture"],
            "fact_id_links": ["fact_engineering_platform_001"],
        },
    ]
    payload = {
        "selected_fact_plan": {"facts": _six_slot_facts()},
        "proof_pool_metadata": _minimal_proof_metadata(skill_rows=skill_rows),
    }
    body = format_unify_graph_bullet_evidence_pack(
        payload,
        allowed_block="ALLOWED_SOURCE_FACT_IDS: [bul_unify_001]\n",
        unify_id_hygiene="",
    )
    assert GRAPH_BULLET_EVIDENCE_PACK_MARKER in body
    assert "bound_skills" in body
    assert "skill_governed_agentic_systems_architecture" in body
    assert "compose_one_bullet_from" in body
    assert "archive_reference_only" not in body
    assert "theme:" not in body
    assert "CANONICAL UNIFY FACTS" not in body


def test_compiled_prompt_uses_graph_compose_not_rewrite() -> None:
    payload = {
        "product_visible": False,
        "run_id": "graph_compose_ub",
        "target_title": "SVP IT Strategy & Innovation",
        "target_company": "Brown & Brown",
        "jd_text": "agentic multi-agent GraphRAG runtime platform control plane",
        "briefing": "regulated enterprise",
        "unify_header": _unify_header(),
        "selected_fact_plan": {"facts": _six_slot_facts()},
        "proof_pool_metadata": _unify_compile_proof_meta(
            skill_rows=[
                {
                    "skill_id": "skill_agentic_platform_productization",
                    "allowed_phrases": ["agentic platform productization"],
                    "fact_id_links": ["fact_engineering_platform_001"],
                }
            ]
        ),
        "allowed_fact_ids": [f"bul_unify_{i:03d}" for i in range(1, 7)],
    }
    out = compile_unify_bullets_prompt(payload, run_id="graph_compose_ub")
    content = str(out.artifact.messages[-1]["content"])
    assert GRAPH_BULLET_EVIDENCE_PACK_MARKER in content
    assert "TARGETING ONLY" in content.upper() or "targeting only" in content
    assert "jd_used_as_proof=false" in content
    assert not _FORBIDDEN_C0.search(content)
    assert "archive_reference_only" not in content
    assert "Agentic AI platform architecture" not in content


def test_legacy_i0_compose_not_rewrite() -> None:
    payload = {
        "unify_header": _unify_header(),
        "selected_fact_plan": {"facts": _six_slot_facts()[:1]},
    }
    body = _legacy_i0(payload)
    assert "Compose six" in body
    assert "Rewrite ONLY" not in body
    assert GRAPH_BULLET_EVIDENCE_PACK_MARKER in body
    assert "bullets_composed_from_graph_evidence" in body


def test_runtime_proof_pool_preserves_role_family_key_for_unify_bullets() -> None:
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    briefing = ANTHROPIC_BRIEFING.read_text(encoding="utf-8")
    args = SimpleNamespace(
        target_company="Anthropic",
        target_title="Manager of Applied AI Architecture, Partnerships",
        target_role="Manager of Applied AI Architecture, Partnerships",
        jd_text=jd_text,
        briefing=briefing,
        base_resume_ref="",
        provider="qwen_vllm",
    )
    pool, _base, _path, _hash, _front_spine = load_section_proof_for_lane(
        section_id="unify_bullets",
        args=args,
        repo_root=REPO,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    plan = pool.selected_fact_plan
    assert plan.get("role_family_key") == "PARTNER_APPLIED_AI_ARCHITECTURE"
    assert plan.get("target_role_profile") == "PARTNER_APPLIED_AI_ARCHITECTURE"

    payload = {
        "target_title": args.target_title,
        "target_role": args.target_role,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_fact_plan": plan,
        "proof_pool_metadata": pool.proof_pool_metadata,
        "allowed_fact_ids": pool.allowed_fact_ids_ordered,
    }
    body = format_unify_role_episode_evidence_pack(payload, section_id="unify_bullets")
    assert "compose_one_bullet_from" in body


def test_partner_profile_preserves_unify_metric_anchor_slots() -> None:
    slot_map = resolve_unify_bullet_slot_bundle_map(
        "PARTNER_APPLIED_AI_ARCHITECTURE",
        repo_root=REPO,
    )
    assert slot_map["bul_unify_004"] == "reb_unify_production_adoption_lifecycle"
    assert slot_map["bul_unify_006"] == "reb_unify_platform_commercialization_leadership"
    assert "reb_unify_partner_channel_cosell" in set(slot_map.values())
