"""C0.3 graph ref classes, role-family projection, and executive_summary binding compression."""

from __future__ import annotations

from typing import Any

from apps_rg.fact_inventory.track_weighted_graph_expansion import SENIOR_ROLE_TAXONOMY_IDS
from apps_rg.runtime.c0.c03_role_family import resolve_c0_pillar_hints

EXEC_SUMMARY_SECTION = "executive_summary"
MAX_CLAIM_SUPPORT_SKILLS_PER_FACT = 4
MAX_MECHANISM_SKILLS_PER_FACT = 2
MECHANISM_OVERLOAD_SKILL_COUNT = 8

MECHANISM_SKILL_MARKERS: tuple[str, ...] = (
    "deterministic_route",
    "multi_agent",
    "orchestration",
    "graphrag",
    "graph_aware",
    "runtime_gate",
    "sandboxed",
    "route_replay",
    "side_effect_bounded",
    "control_plane",
    "spine_design",
    "prompt_packaging",
    "workflow_orchestration",
    "dense_sparse",
)

# Enhancement #3 — Phase 1 skill markers for phase-diversity enforcement.
# Skills whose IDs contain these tokens are treated as Phase 1 claim candidates.
PHASE1_SKILL_MARKERS: tuple[str, ...] = (
    "actuarial",
    "derivatives",
    "capital_risk",
    "ccar",
    "basel",
    "stress_test",
    "model_risk",
    "reserving",
    "embedded_value",
    "quantitative_risk",
    "solvency",
)

EXECUTIVE_CAPABILITY_FRAMES: tuple[tuple[str, str], ...] = (
    ("governed_agentic", "governed enterprise AI platform delivery"),
    ("deterministic_route", "deterministic runtime control and routing discipline"),
    ("multi_agent", "multi-agent workflow orchestration at enterprise scale"),
    ("graph_aware", "graph-aware evidence grounding for regulated workflows"),
    ("commercialization", "AI platform commercialization and IP-led revenue growth"),
    ("basel", "regulatory data lineage and risk reporting discipline"),
    ("cloud_data", "cloud data platform engineering for enterprise programs"),
    ("workflow_adoption", "enterprise workflow adoption and operating model change"),
    # Enhancement #4 — Phase 1 executive capability frames for three-phase JDs
    ("actuarial_risk", "actuarial risk quantification and capital modeling"),
    ("ccar_stress", "regulatory stress testing and model risk governance"),
    ("derivatives_risk", "derivatives risk analytics and structured product pricing"),
)


def _is_mechanism_skill(skill_id: str) -> bool:
    low = str(skill_id or "").lower()
    return any(m in low for m in MECHANISM_SKILL_MARKERS)


def _is_phase1_skill(skill_id: str) -> bool:
    low = str(skill_id or "").lower()
    return any(m in low for m in PHASE1_SKILL_MARKERS)


def resolve_role_family_projection(
    role_family_key: str,
    *,
    repo_root: Any = None,
) -> dict[str, Any]:
    """Resolve SQLite role_family_projection or taxonomy-backed synthesis — never silent generic fallback."""
    from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
        default_graph_sqlite_path,
        open_graph_sqlite,
    )

    rf = str(role_family_key or "").strip() or "SVP_ENGINEERING_AI_PLATFORM"
    pillar_hints = resolve_c0_pillar_hints(rf, repo_root=repo_root)
    out: dict[str, Any] = {
        "role_family_key": rf,
        "pillar_hint_ids": list(pillar_hints),
        "sqlite_projection_row_found": False,
        "projection_source": "missing",
        "fallback_pillar_bridge_used": False,
        "release_eligible_targeting_proof": False,
        "targeting_degraded_explicit": False,
    }
    db = default_graph_sqlite_path(repo_root)
    if db.is_file():
        conn = open_graph_sqlite(repo_root=repo_root, db_path=db)
        try:
            row = conn.execute(
                """
                SELECT role_family_id, projection_role_family_key, track_weight_profile,
                       targeting_keywords, proof_policy_note
                FROM role_family_projection
                WHERE role_family_id = ? OR projection_role_family_key = ?
                LIMIT 1
                """,
                (rf, rf),
            ).fetchone()
        finally:
            conn.close()
        if row:
            out["sqlite_projection_row_found"] = True
            out["projection_source"] = "sqlite_role_family_projection"
            out["release_eligible_targeting_proof"] = True
            out["targeting_degraded_explicit"] = False
            return out

    if rf in SENIOR_ROLE_TAXONOMY_IDS and pillar_hints:
        out["projection_source"] = "taxonomy_pillar_hints_synthesized"
        out["targeting_degraded_explicit"] = True
        out["release_eligible_targeting_proof"] = False
        out["fallback_pillar_bridge_used"] = False
        return out

    if pillar_hints:
        out["projection_source"] = "taxonomy_pillar_hints_only"
        out["targeting_degraded_explicit"] = True
        out["release_eligible_targeting_proof"] = False
        return out

    out["projection_source"] = "missing_no_taxonomy_pillars"
    out["fallback_pillar_bridge_used"] = True
    out["targeting_degraded_explicit"] = True
    out["release_eligible_targeting_proof"] = False
    return out


def _executive_capability_phrases(skill_ids: list[str], *, max_phrases: int = 3) -> list[str]:
    phrases: list[str] = []
    for sid in skill_ids:
        low = sid.lower()
        for marker, phrase in EXECUTIVE_CAPABILITY_FRAMES:
            if marker in low and phrase not in phrases:
                phrases.append(phrase)
                break
        if len(phrases) >= max_phrases:
            break
    if not phrases and skill_ids:
        phrases.append("enterprise technology leadership with measurable business outcomes")
    return phrases[:max_phrases]


def compress_binding_for_executive_summary(
    binding: dict[str, Any],
    *,
    role_family_projection: dict[str, Any],
    skill_pillar_by_id: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Cap mechanism-heavy skill refs; emit executive-level capability language for PA hints."""
    out = dict(binding)
    fid = str(out.get("fact_id") or "")
    skills = list(out.get("graph_node_refs") or [])
    pillar_hints = tuple(role_family_projection.get("pillar_hint_ids") or ())
    skill_pillar_by_id = skill_pillar_by_id or {}

    def sort_key(sid: str) -> tuple[int, int, int, str]:
        mech = 1 if _is_mechanism_skill(sid) else 0
        pillar_match = 0 if skill_pillar_by_id.get(sid, "") in pillar_hints else 1
        return (mech, pillar_match, 0 if sid in skills else 1, sid)

    ranked = sorted(skills, key=sort_key)
    kept: list[str] = []
    mech_kept = 0
    for sid in ranked:
        if len(kept) >= MAX_CLAIM_SUPPORT_SKILLS_PER_FACT:
            break
        if _is_mechanism_skill(sid):
            if mech_kept >= MAX_MECHANISM_SKILLS_PER_FACT:
                continue
            mech_kept += 1
        kept.append(sid)

    # Enhancement #3 — phase-diversity slot: when no Phase 1 skill survived ranking
    # (common when all input skills are Phase 3), inject the top Phase 1 candidate
    # in place of the last kept skill. Cap at MAX_CLAIM_SUPPORT_SKILLS_PER_FACT.
    # Only applies when at least one Phase 1 candidate exists in the input set.
    p1_candidates = [s for s in skills if _is_phase1_skill(s) and s not in kept]
    if p1_candidates and not any(_is_phase1_skill(s) for s in kept):
        if len(kept) >= MAX_CLAIM_SUPPORT_SKILLS_PER_FACT:
            kept[-1] = p1_candidates[0]
        else:
            kept.append(p1_candidates[0])

    suppressed = [s for s in skills if s not in kept]
    clusters = list(out.get("skill_cluster_refs") or [])
    targeting_pillars = [p for p in clusters if str(p).startswith("pillar_") and p in pillar_hints][
        :5
    ]
    if not targeting_pillars and pillar_hints:
        targeting_pillars = list(pillar_hints)[:5]

    out["claim_support_graph_refs"] = kept
    out["targeting_graph_refs"] = targeting_pillars
    out["receipt_only_lineage_refs"] = [f"ledger:{fid}"] if fid else []
    out["graph_node_refs"] = kept
    out["suppressed_skill_refs"] = suppressed
    out["mechanism_skill_count"] = sum(1 for s in kept if _is_mechanism_skill(s))
    out["skill_binding_count_before"] = len(skills)
    out["skill_binding_count_after"] = len(kept)
    out["mechanism_overloaded"] = len(skills) >= MECHANISM_OVERLOAD_SKILL_COUNT
    out["executive_capability_phrases"] = _executive_capability_phrases(kept)
    out["pa_mechanism_terms_max_per_sentence"] = {
        "0": MAX_MECHANISM_SKILLS_PER_FACT if fid.startswith("fact_engineering_platform") else 1,
    }
    return out


def classify_binding_graph_refs(binding: dict[str, Any]) -> dict[str, Any]:
    """Normalize binding to explicit ref classes (idempotent)."""
    fid = str(binding.get("fact_id") or "")
    claim = list(
        binding.get("claim_support_graph_refs")
        or binding.get("graph_node_refs")
        or []
    )
    targeting = list(binding.get("targeting_graph_refs") or binding.get("skill_cluster_refs") or [])
    receipt = list(binding.get("receipt_only_lineage_refs") or [])
    if fid and f"ledger:{fid}" not in receipt:
        receipt = [f"ledger:{fid}", *receipt]
    return {
        "claim_support_graph_refs": claim,
        "targeting_graph_refs": [t for t in targeting if str(t).startswith("pillar_")],
        "receipt_only_lineage_refs": receipt,
    }


def collect_receipt_only_json_expansion_refs(
    graph: dict[str, Any],
    *,
    selected_fact_ids: set[str],
    max_refs: int = 64,
) -> list[str]:
    """JSON ledger neighbor edges — receipt lineage only, never PA generation authority."""
    from apps_rg.runtime.c03_graphrag_bound import _collect_graph_expansion_refs

    return list(
        _collect_graph_expansion_refs(graph, selected_fact_ids=selected_fact_ids, max_refs=max_refs)
    )


def aggregate_graph_ref_classes(
    bindings: list[dict[str, Any]],
    *,
    receipt_only_lineage_refs: list[str] | None = None,
) -> dict[str, list[str]]:
    claim: list[str] = []
    targeting: list[str] = []
    receipt: list[str] = list(receipt_only_lineage_refs or [])
    for b in bindings:
        classes = classify_binding_graph_refs(b)
        for sid in classes["claim_support_graph_refs"]:
            if sid not in claim:
                claim.append(sid)
        for p in classes["targeting_graph_refs"]:
            if p not in targeting:
                targeting.append(p)
        for r in classes["receipt_only_lineage_refs"]:
            if r not in receipt:
                receipt.append(r)
    return {
        "claim_support_graph_refs": claim,
        "targeting_graph_refs": targeting,
        "receipt_only_lineage_refs": receipt,
    }


def build_graph_targeting_for_pa(
    *,
    bindings: list[dict[str, Any]],
    role_family_projection: dict[str, Any],
    receipt_only_lineage_refs: list[str],
) -> dict[str, Any]:
    """PA-safe graph targeting block — excludes receipt-only JSON expansion refs."""
    refs = aggregate_graph_ref_classes(bindings, receipt_only_lineage_refs=receipt_only_lineage_refs)
    overloaded = [
        {
            "fact_id": b.get("fact_id"),
            "mechanism_overloaded": b.get("mechanism_overloaded"),
            "skill_binding_count_before": b.get("skill_binding_count_before"),
            "skill_binding_count_after": b.get("skill_binding_count_after"),
            "executive_capability_phrases": b.get("executive_capability_phrases"),
            "suppressed_skill_refs": (b.get("suppressed_skill_refs") or [])[:8],
            "pa_mechanism_terms_max_per_sentence": b.get("pa_mechanism_terms_max_per_sentence"),
        }
        for b in bindings
        if b.get("mechanism_overloaded") or int(b.get("skill_binding_count_before") or 0) > MAX_CLAIM_SUPPORT_SKILLS_PER_FACT
    ]
    return {
        "claim_support_graph_refs": refs["claim_support_graph_refs"],
        "targeting_graph_refs": refs["targeting_graph_refs"],
        "receipt_only_lineage_refs": refs["receipt_only_lineage_refs"],
        "receipt_only_json_expansion_excluded_from_pa": True,
        "role_family_projection": dict(role_family_projection),
        "overloaded_fact_compression": overloaded,
        "mechanism_vocabulary_cap": {
            "max_mechanism_terms_sentence_0": MAX_MECHANISM_SKILLS_PER_FACT,
            "prefer_executive_capability_phrases": True,
        },
    }


def build_c0_graph_diagnostics(
    bindings: list[dict[str, Any]],
    *,
    role_family_projection: dict[str, Any],
    resume_display_text: str = "",
) -> dict[str, Any]:
    """Diagnostics for X2 gates and repair ledgers."""
    from apps_rg.runtime.sections.executive_summary_composition import (
        is_mechanism_inventory_sentence,
        mechanism_term_hits,
        split_sentences,
    )

    dominant_fact = ""
    dominant_bindings: list[str] = []
    max_skills = 0
    for b in bindings:
        n = int(b.get("skill_binding_count_before") or len(b.get("graph_node_refs") or []))
        if n > max_skills:
            max_skills = n
            dominant_fact = str(b.get("fact_id") or "")
            dominant_bindings = list(b.get("claim_support_graph_refs") or b.get("graph_node_refs") or [])
    mech_sentence_idx: int | None = None
    mech_hits: list[str] = []
    for i, sent in enumerate(split_sentences(resume_display_text)):
        inv, _ = is_mechanism_inventory_sentence(sent)
        if inv:
            mech_sentence_idx = i
            mech_hits = mechanism_term_hits(sent)
            break
    return {
        "dominant_source_fact_id": dominant_fact,
        "dominant_claim_support_graph_refs": dominant_bindings[:12],
        "dominant_suppressed_skill_refs": list(
            (
                next((b for b in bindings if b.get("fact_id") == dominant_fact), {})
                or {}
            ).get("suppressed_skill_refs")
            or []
        )[:12],
        "role_family_projection": dict(role_family_projection),
        "mechanism_inventory_sentence_index": mech_sentence_idx,
        "mechanism_term_hits": mech_hits,
    }


def merge_graph_targeting_jd_alignment(
    jd_alignment: dict[str, Any] | None,
    *,
    role_family_projection: dict[str, Any],
) -> dict[str, Any]:
    """Extend jd_alignment with explicit graph targeting posture for X2."""
    out = dict(jd_alignment or {})
    out.setdefault("targeting_only", True)
    out.setdefault("jd_used_as_proof", False)
    out.setdefault("briefing_used_as_proof", False)
    out["graph_targeting"] = {
        "role_family_key": role_family_projection.get("role_family_key"),
        "projection_source": role_family_projection.get("projection_source"),
        "sqlite_projection_row_found": role_family_projection.get("sqlite_projection_row_found"),
        "fallback_pillar_bridge_used": role_family_projection.get("fallback_pillar_bridge_used"),
        "release_eligible_targeting_proof": role_family_projection.get(
            "release_eligible_targeting_proof"
        ),
        "targeting_degraded_explicit": role_family_projection.get("targeting_degraded_explicit"),
        "pillar_hint_ids": list(role_family_projection.get("pillar_hint_ids") or []),
    }
    return out


__all__ = [
    "MAX_CLAIM_SUPPORT_SKILLS_PER_FACT",
    "aggregate_graph_ref_classes",
    "build_c0_graph_diagnostics",
    "build_graph_targeting_for_pa",
    "classify_binding_graph_refs",
    "collect_receipt_only_json_expansion_refs",
    "compress_binding_for_executive_summary",
    "merge_graph_targeting_jd_alignment",
    "resolve_role_family_projection",
]
