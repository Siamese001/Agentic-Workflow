"""Partner ADE calibration — C0.3 skills graph stress point (one JD fixture).

Compares legacy tag-only + SVP default role family vs hardened fact-links-first + JD-aware
projection. Emits metrics JSON under artifacts/apps_rg/c0/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_role_family_taxonomy
from apps_rg.fact_inventory.competencies_graph_skills_proof_pool import (
    build_competencies_graph_skills_proof_payload,
)
from apps_rg.fact_inventory.selected_role_fact_set import infer_role_family_priorities
from apps_rg.fact_inventory.track_weighted_graph_expansion import infer_projection_role_family_key
from apps_rg.runtime.c0.c02_evidence_fetch import fetch_c02_evidence_atoms
from apps_rg.runtime.c0.c03_graph_expansion import (
    BINDING_MODE_FACT_LINKS_FIRST,
    BINDING_MODE_TAG_LABEL_ONLY,
    expand_c03_graph_bindings,
)
from apps_rg.runtime.proof_pool_resolver import SectionProofPool

JD_PATH = REPO / "apps_rg/config/targeting/openai_partner_ade_jd.txt"
BRIEF_PATH = REPO / "apps_rg/config/targeting/openai_partner_ade_briefing.txt"
OUT_DIR = REPO / "artifacts/apps_rg/c0"
OUT_JSON = OUT_DIR / "partner_ade_c03_calibration.json"


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _pool_from_competencies_payload(payload: dict) -> SectionProofPool:
    plan = payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    allowed = {str(f.get("fact_id") or f.get("candidate_fact_id") or "") for f in facts}
    allowed.discard("")
    return SectionProofPool(
        section="competencies",
        proof_source="augmented_skills_graph",
        proof_pool_ref=str(payload.get("proof_pool_ref") or "competencies_graph_proof_pool.json"),
        proof_pool_digest=str(payload.get("proof_pool_digest") or ""),
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=sorted(allowed),
        allowed_fact_ids=allowed,
        bullet_rows=[],
        proof_pool_metadata={
            "target_role": "Partner ADE",
            "jd_text": payload.get("jd_text") or "",
            "track_weighted_graph_expansion": payload.get("track_weighted_graph_expansion"),
        },
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="",
        base_resume_json_hash="",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )


def _c03_metrics(c03: dict) -> dict:
    m = dict(c03.get("binding_metrics") or {})
    skills = []
    tw = {}
    return {
        "role_family_key": c03.get("role_family_key"),
        "binding_mode": c03.get("binding_mode"),
        **m,
    }


def _role_inference(jd: str, briefing: str, taxonomy: dict) -> dict:
    target_role = "Partner ADE — AI Deployment Engineering"
    legacy_key = "SVP_ENGINEERING_AI_PLATFORM"
    inferred = infer_projection_role_family_key(
        target_role=target_role,
        jd_text=jd,
        briefing_text=briefing,
        taxonomy=taxonomy,
    )
    priorities = infer_role_family_priorities(
        target_role=target_role,
        jd_text=jd,
        briefing_text=briefing,
        taxonomy=taxonomy,
    )
    top3 = [
        {
            "role_family": p.role_family,
            "score": p.score,
            "evidence_terms": list(p.evidence_terms)[:8],
        }
        for p in priorities[:3]
    ]
    return {
        "target_role": target_role,
        "legacy_default_role_family": legacy_key,
        "inferred_projection_role_family": inferred,
        "top_role_family_priorities": top3,
    }


def main() -> int:
    jd = _load_text(JD_PATH)
    briefing = _load_text(BRIEF_PATH)
    taxonomy = load_master_role_family_taxonomy(repo_root=REPO)
    role_block = _role_inference(jd, briefing, taxonomy)

    payload = build_competencies_graph_skills_proof_payload(
        repo_root=REPO,
        jd_text=jd,
        target_role="Partner ADE — AI Deployment Engineering",
        briefing_text=briefing,
    )
    pool = _pool_from_competencies_payload(payload)
    c02 = fetch_c02_evidence_atoms(section_id="competencies", pool=pool, repo_root=REPO)
    atoms = list(c02.get("atoms") or [])

    legacy_rf = "SVP_ENGINEERING_AI_PLATFORM"
    hardened_rf = role_block["inferred_projection_role_family"]

    baseline_c03 = expand_c03_graph_bindings(
        section_id="competencies",
        atoms=atoms,
        role_family_key=legacy_rf,
        repo_root=REPO,
        binding_mode=BINDING_MODE_TAG_LABEL_ONLY,
    )
    hardened_c03 = expand_c03_graph_bindings(
        section_id="competencies",
        atoms=atoms,
        role_family_key=hardened_rf,
        repo_root=REPO,
        binding_mode=BINDING_MODE_FACT_LINKS_FIRST,
    )

    tw = payload.get("track_weighted_graph_expansion") or {}
    selected_skills = [
        {
            "skill_id": s.get("skill_id"),
            "label": s.get("label"),
            "career_track": s.get("career_track"),
            "pillar": s.get("pillar"),
        }
        for s in (payload.get("selected_skill_rows") or [])[:12]
    ]

    report = {
        "schema_version": "partner_ade_c03_calibration_v1",
        "jd_fixture": str(JD_PATH.relative_to(REPO)).replace("\\", "/"),
        "role_inference": role_block,
        "competencies_graph": {
            "projection_role_family_key": tw.get("projection_role_family_key"),
            "selected_skill_count": len(payload.get("selected_skill_rows") or []),
            "selected_fact_count": len((tw.get("selected_facts") or [])),
            "sample_selected_skills": selected_skills,
        },
        "c03_baseline": _c03_metrics(baseline_c03),
        "c03_hardened": _c03_metrics(hardened_c03),
        "improvement_delta": {
            "direct_support_count": (
                _c03_metrics(hardened_c03).get("direct_support_count", 0)
                - _c03_metrics(baseline_c03).get("direct_support_count", 0)
            ),
            "skill_fact_link_direct_count": (
                _c03_metrics(hardened_c03).get("skill_fact_link_direct_count", 0)
                - _c03_metrics(baseline_c03).get("skill_fact_link_direct_count", 0)
            ),
            "adjacent_only_count": (
                _c03_metrics(baseline_c03).get("adjacent_only_count", 0)
                - _c03_metrics(hardened_c03).get("adjacent_only_count", 0)
            ),
            "role_family_changed": legacy_rf != hardened_rf,
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    improved = (
        report["improvement_delta"]["direct_support_count"] > 0
        or report["improvement_delta"]["skill_fact_link_direct_count"] > 0
        or report["improvement_delta"]["role_family_changed"]
    )
    return 0 if improved else 1


if __name__ == "__main__":
    raise SystemExit(main())
