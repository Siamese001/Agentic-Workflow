"""C0.1–C0.7 evidence-room stress calibration for a JD fixture.

Emits per-phase metrics (baseline tag-only + SVP vs hardened fact-links + JD role family).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_role_family_taxonomy
from apps_rg.fact_inventory.competencies_graph_skills_proof_pool import (
    build_competencies_graph_skills_proof_payload,
)
from apps_rg.fact_inventory.role_family_selection import infer_role_family_priorities
from apps_rg.fact_inventory.track_weighted_graph_expansion import infer_projection_role_family_key
from apps_rg.runtime.c0.c01_retrieval_plan import build_c01_retrieval_plan
from apps_rg.runtime.c0.c02_evidence_fetch import fetch_c02_evidence_atoms
from apps_rg.runtime.c0.c03_graph_expansion import (
    BINDING_MODE_FACT_LINKS_FIRST,
    BINDING_MODE_TAG_LABEL_ONLY,
    C03GraphSelectionError,
    expand_c03_graph_bindings,
)
from apps_rg.runtime.c0.c04_stratify import stratify_c04_evidence
from apps_rg.runtime.c0.c06_weak_refine import (
    finalize_c06_after_c05,
    maybe_c06_weak_refine,
)

DEFAULT_JD = REPO / "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt"
DEFAULT_BRIEF = REPO / "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md"
OUT_DIR = REPO / "artifacts/apps_rg/c0"


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _pool(payload: dict, *, target_role: str, jd_text: str) -> Any:
    from apps_rg.runtime.proof_pool_resolver import SectionProofPool

    plan = payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    allowed = {str(f.get("fact_id") or "") for f in facts if f.get("fact_id")}
    return SectionProofPool(
        section="competencies",
        proof_source="augmented_skills_graph",
        proof_pool_ref="stress",
        proof_pool_digest="stress",
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=sorted(allowed),
        allowed_fact_ids=allowed,
        bullet_rows=[],
        proof_pool_metadata={"target_role": target_role, "jd_text": jd_text},
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


def _run_phase_bundle(
    *,
    section_id: str,
    atoms: list[dict[str, Any]],
    role_family_key: str,
    binding_mode: str,
    target_role: str,
    jd_text: str,
    lane_requires_proof: bool,
    selected_graph_plan: dict[str, Any] | None,
) -> dict[str, Any]:
    # Import agentic_core-backed leaves only after ``main`` has completed the
    # package bootstrap below.  Importing C0.5 first creates a cycle through
    # agentic_core.L0_routing -> evidence_room -> C0.5 in a standalone process.
    from apps_rg.runtime.c0.c05_fec_packet import build_c05_final_evidence_contract
    from apps_rg.runtime.c0.c07_handoff_audit import audit_c07_handoff

    c01 = build_c01_retrieval_plan(
        section_id=section_id,
        target_role=target_role,
        role_family_key=role_family_key,
        jd_text=jd_text,
        route_ref="route_contract.json",
    )
    c02 = {
        "atom_count": len(atoms),
        "jd_used_as_proof": False,
        "graph_inference_performed": False,
    }
    try:
        c03 = expand_c03_graph_bindings(
            section_id=section_id,
            atoms=atoms,
            role_family_key=role_family_key,
            repo_root=REPO,
            binding_mode=binding_mode,
            run_id="c0-evidence-room-stress",
            strict_ranked_selection=False,
            selected_graph_plan=selected_graph_plan,
        )
    except C03GraphSelectionError as exc:
        # A legacy comparison phase is allowed to demonstrate that the hardened
        # C0.3 boundary now blocks it.  Preserve the fail-closed outcome in the
        # calibration report instead of aborting before the hardened phase runs.
        return {
            "c01": {
                "role_family_key": c01.get("role_family_key"),
                "primary_targets": (c01.get("retrieval_targets") or {}).get("primary_targets"),
            },
            "c02": c02,
            "c03": {
                "blocked": True,
                "block_type": type(exc).__name__,
                "block_reason": str(exc),
            },
            "c04": {"skipped": True},
            "c05": {"skipped": True},
            "c06": {"skipped": True},
            "c07": {
                "schema_version": "c07_handoff_audit_v1",
                "handoff_safe": False,
                "skipped": True,
                "violations": ["c03_graph_selection_blocked"],
            },
        }
    bindings = list(c03.get("bindings") or [])
    c04 = stratify_c04_evidence(
        section_id=section_id,
        atoms=atoms,
        graph_bindings=bindings,
        lane_requires_proof=lane_requires_proof,
    )
    allowed = list(c04.get("allowed_fact_ids") or [])
    fec, c05 = build_c05_final_evidence_contract(
        section_id=section_id,
        atoms=atoms,
        strata=c04.get("strata") or {},
        graph_bindings=bindings,
        front_spine=None,
        allowed_fact_ids=allowed,
    )
    adopted_c03, c06 = maybe_c06_weak_refine(
        section_id=section_id,
        role_family_key=role_family_key,
        route_ref="route_contract.json",
        run_id="c0-evidence-room-stress",
        atoms=atoms,
        initial_c03=c03,
        initial_c05_receipt=c05,
        selected_graph_plan=selected_graph_plan,
        repo_root=REPO,
    )
    if c06.get("attempted") and c06.get("pass"):
        c03 = adopted_c03
        bindings = list(c03.get("bindings") or [])
        c04 = stratify_c04_evidence(
            section_id=section_id,
            atoms=atoms,
            graph_bindings=bindings,
            lane_requires_proof=lane_requires_proof,
        )
        allowed = list(c04.get("allowed_fact_ids") or [])
        fec, c05 = build_c05_final_evidence_contract(
            section_id=section_id,
            atoms=atoms,
            strata=c04.get("strata") or {},
            graph_bindings=bindings,
            front_spine=None,
            allowed_fact_ids=allowed,
        )
    c06 = finalize_c06_after_c05(c06, final_c05_receipt=c05)
    if c06.get("pass"):
        c07 = audit_c07_handoff(
            fec=fec,
            c02_receipt=c02,
            c03_receipt=c03,
            graph_bindings=bindings,
            allowed_fact_ids=allowed,
            c05_receipt=c05,
            c06_receipt=c06,
        )
    else:
        c07 = {
            "schema_version": "c07_handoff_audit_v1",
            "handoff_safe": False,
            "skipped": True,
            "violations": ["c06_refinement_blocked"],
        }
    strata = c04.get("strata") or {}
    return {
        "c01": {
            "role_family_key": c01.get("role_family_key"),
            "primary_targets": (c01.get("retrieval_targets") or {}).get("primary_targets"),
        },
        "c02": c02,
        "c03": {k: v for k, v in c03.items() if k != "bindings"},
        "c04": {
            "must_use_count": len(strata.get("MUST_USE") or []),
            "supporting_count": len(strata.get("SUPPORTING") or []),
            "background_count": len(strata.get("BACKGROUND") or []),
            "excluded_count": len(strata.get("EXCLUDED") or []),
        },
        "c05": {
            "evidence_item_count": len(fec.evidence_items),
            "support_status": fec.support_status,
        },
        "c06": c06,
        "c07": c07,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="C0.1–C0.7 JD stress calibration")
    ap.add_argument("--jd", type=Path, default=DEFAULT_JD)
    ap.add_argument("--briefing", type=Path, default=DEFAULT_BRIEF)
    ap.add_argument("--target-role", default="VP, Global Head of Agentic AI Solutions")
    ap.add_argument("--out", type=Path, default=OUT_DIR / "aig_vp_c0_evidence_room_stress.json")
    args = ap.parse_args()

    # The repository's agentic_core root performs L0 reachability loading as a
    # package side effect.  Bootstrap its governed FEC contract before importing
    # the C0.5/C0.7 leaves so the standalone stress tool cannot enter that cycle.
    from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract

    del FinalEvidenceContract

    jd = _load(args.jd)
    briefing = _load(args.briefing) if args.briefing.is_file() else ""
    tax = load_master_role_family_taxonomy(repo_root=REPO)
    inferred = infer_projection_role_family_key(
        target_role=args.target_role,
        jd_text=jd,
        briefing_text=briefing,
        taxonomy=tax,
    )
    priorities = [
        {
            "role_family": p.role_family,
            "score": p.score,
            "evidence_terms": list(p.evidence_terms)[:10],
        }
        for p in infer_role_family_priorities(
            target_role=args.target_role,
            jd_text=jd,
            briefing_text=briefing,
            taxonomy=tax,
        )[:5]
    ]
    payload = build_competencies_graph_skills_proof_payload(
        repo_root=REPO,
        jd_text=jd,
        target_role=args.target_role,
        briefing_text=briefing,
    )
    from apps_rg.runtime.sections.graph_role_episode_selector import (
        build_selected_graph_evidence_plan_for_section,
    )

    selected_graph_plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=REPO,
        section_id="competencies",
        target_role=args.target_role,
        jd_text=jd,
        briefing_text=briefing,
    )
    payload = {**payload, "selected_fact_plan": selected_graph_plan}
    tw = payload.get("track_expansion") or {}
    pool = _pool(payload, target_role=args.target_role, jd_text=jd)
    atoms = list(fetch_c02_evidence_atoms(section_id="competencies", pool=pool, repo_root=REPO).get("atoms") or [])

    baseline = _run_phase_bundle(
        section_id="competencies",
        atoms=atoms,
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        binding_mode=BINDING_MODE_TAG_LABEL_ONLY,
        target_role=args.target_role,
        jd_text=jd,
        lane_requires_proof=False,
        selected_graph_plan=None,
    )
    hardened = _run_phase_bundle(
        section_id="competencies",
        atoms=atoms,
        role_family_key=inferred,
        binding_mode=BINDING_MODE_FACT_LINKS_FIRST,
        target_role=args.target_role,
        jd_text=jd,
        lane_requires_proof=False,
        selected_graph_plan=selected_graph_plan,
    )

    sample_skills = [
        {
            "skill_id": s.get("skill_id"),
            "label": s.get("label"),
            "pillar": s.get("pillar"),
            "career_track": s.get("career_track"),
        }
        for s in (payload.get("selected_skill_rows") or [])[:12]
    ]

    report: dict[str, Any] = {
        "schema_version": "c0_evidence_room_stress_v1",
        "jd_fixture": str(args.jd.resolve().relative_to(REPO.resolve())).replace("\\", "/"),
        "target_role": args.target_role,
        "role_inference": {
            "inferred_projection_role_family": inferred,
            "top_priorities": priorities,
        },
        "competencies_graph": {
            "projection_role_family_key": tw.get("projection_role_family_key"),
            "role_family_key": tw.get("role_family_key"),
            "track_weights": tw.get("track_weights"),
            "selected_skill_count": len(payload.get("selected_skill_rows") or []),
            "sample_selected_skills": sample_skills,
        },
        "baseline_bundle": baseline,
        "hardened_bundle": hardened,
        "improvement_delta": {
            "c03_direct_support": (
                (hardened.get("c03") or {}).get("binding_metrics", {}).get("direct_support_count", 0)
                - (baseline.get("c03") or {}).get("binding_metrics", {}).get("direct_support_count", 0)
            ),
            "c03_pillar_aligned": (
                (hardened.get("c03") or {}).get("binding_metrics", {}).get("pillar_aligned_direct_count", 0)
                - (baseline.get("c03") or {}).get("binding_metrics", {}).get("pillar_aligned_direct_count", 0)
            ),
            "c04_must_use": (
                (hardened.get("c04") or {}).get("must_use_count", 0)
                - (baseline.get("c04") or {}).get("must_use_count", 0)
            ),
            "c01_role_family_targets": (
                "it_strategy_innovation_facts"
                in ((hardened.get("c01") or {}).get("primary_targets") or [])
                or "enterprise_architecture_standards"
                in ((hardened.get("c01") or {}).get("primary_targets") or [])
            ),
            "c07_handoff_safe": bool((hardened.get("c07") or {}).get("handoff_safe")),
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    improved = any(v for k, v in report["improvement_delta"].items() if k != "c07_handoff_safe" and v)
    return 0 if improved and report["improvement_delta"]["c07_handoff_safe"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
