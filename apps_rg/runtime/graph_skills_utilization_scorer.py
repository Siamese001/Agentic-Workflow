"""Graph skills utilization scorer with anti-gaming rules (W8 / D8)."""
from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from apps_rg.runtime.graph_skill_phrase_capsule import collect_capsule_phrases
from apps_rg.runtime.validators.graph_skills_proof_common import (
    GraphSkillsProofError,
    assert_capsule_phrases_not_proof_authority,
)

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
RECEIPT_SCHEMA = "graph_skills_utilization_receipt_v1"

# Configured synonym map (deterministic — not LLM-judged).
SEMANTIC_VARIANT_MAP: dict[str, tuple[str, ...]] = {
    "agentic ai platform": ("agentic-ai platform", "agentic ai platforms"),
    "platform engineering": ("platform engineering", "platform-engineering"),
    "governed runtime": ("governed runtimes",),
    "insurtech": ("insurtech", "insurance technology"),
    # Enhancement #6 — Phase 1 variants: actuarial/risk terminology equivalences
    "actuarial modeling": ("actuarial analytics", "risk modeling", "risk analytics", "actuarial analysis"),
    "capital risk": ("capital modeling", "regulatory capital", "risk quantification", "risk capital"),
    "stress testing": ("stress tests", "regulatory stress test", "ccar stress", "model stress"),
    # Enhancement #6 — Phase 2 variants: data platform and cloud terminology equivalences
    "enterprise data platform": ("cloud data platform", "data and cloud", "data platform engineering"),
    "cloud data": ("cloud and data", "data cloud", "cloud data services"),
}


def _normalize_phrase(text: str) -> str:
    return " ".join(str(text or "").casefold().split())


def _phrase_variants(phrase: str, variant_map: Mapping[str, Sequence[str]] | None = None) -> list[str]:
    base = _normalize_phrase(phrase)
    if not base:
        return []
    variants = {base}
    mapping = variant_map if variant_map is not None else SEMANTIC_VARIANT_MAP
    for key, alts in mapping.items():
        nk = _normalize_phrase(key)
        if nk == base or base in {_normalize_phrase(a) for a in alts}:
            variants.add(nk)
            variants.update(_normalize_phrase(a) for a in alts)
    return sorted(variants)


def _phrase_in_text(phrase: str, text: str, *, variant_map: Mapping[str, Sequence[str]] | None = None) -> bool:
    hay = _normalize_phrase(text)
    if not hay:
        return False
    for variant in _phrase_variants(phrase, variant_map):
        if len(variant) < 4:
            if re.search(rf"\b{re.escape(variant)}\b", hay):
                return True
        elif variant in hay:
            return True
    return False


def _collect_forbidden_phrases(skill_rows: Sequence[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in skill_rows:
        if not isinstance(row, dict):
            continue
        for phrase in row.get("forbidden_phrases") or []:
            text = str(phrase).strip()
            if text:
                out.append(text)
    return out


def _cited_fact_ids(text_claim_coverage: Mapping[str, Any] | None) -> set[str]:
    cov = text_claim_coverage if isinstance(text_claim_coverage, dict) else {}
    cited: set[str] = set()
    for row in cov.get("sentences") or []:
        if not isinstance(row, dict):
            continue
        for key in ("cited_fact_ids", "fact_ids", "source_fact_ids"):
            for raw in row.get(key) or []:
                text = str(raw).strip()
                if text:
                    cited.add(text)
    return cited


def _skill_rows_to_maps(
    skill_rows: Sequence[dict[str, Any]],
    *,
    suppressed_skill_ids: Sequence[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    suppressed_lookup: dict[str, str] = {}
    for entry in suppressed_skill_ids or []:
        if isinstance(entry, dict):
            sid = str(entry.get("skill_id") or "").strip()
            reason = str(entry.get("reason_code") or "").strip()
            if sid and reason:
                suppressed_lookup[sid] = reason
    eligible: list[dict[str, Any]] = []
    for row in skill_rows:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("skill_id") or "").strip()
        if not sid:
            continue
        if sid in suppressed_lookup:
            continue
        eligible.append(row)
    return eligible, suppressed_lookup


def validate_scorer_inputs_neg6(
    *,
    section_id: str,
    skill_rows: Sequence[dict[str, Any]],
    allowed_fact_ids: Sequence[str],
    proof_pool_metadata: dict[str, Any] | None = None,
    selected_fact_plan: dict[str, Any] | None = None,
) -> None:
    """NEG-6: scorer inputs must not treat capsule phrases as proof authority."""
    phrases = collect_capsule_phrases(list(skill_rows))
    assert_capsule_phrases_not_proof_authority(
        section_id=section_id,
        proof_pool_metadata=proof_pool_metadata,
        allowed_fact_ids=allowed_fact_ids,
        selected_fact_plan=selected_fact_plan,
    )
    for phrase in phrases:
        if phrase in set(allowed_fact_ids):
            raise GraphSkillsProofError(
                f"{section_id}: scorer allowed_fact_ids must not include capsule phrase {phrase!r}"
            )


def score_graph_skills_utilization(
    *,
    section_id: str,
    skill_rows: Sequence[dict[str, Any]],
    resume_display_text: str,
    text_claim_coverage: dict[str, Any] | None = None,
    allowed_fact_ids: Sequence[str] | None = None,
    suppressed_skill_ids: Sequence[dict[str, Any]] | None = None,
    variant_map: Mapping[str, Sequence[str]] | None = None,
    proof_pool_metadata: dict[str, Any] | None = None,
    selected_fact_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Score graph skill utilization per D8 anti-gaming rules."""
    allowed_facts = {str(x).strip() for x in (allowed_fact_ids or []) if str(x).strip()}
    if allowed_facts:
        validate_scorer_inputs_neg6(
            section_id=section_id,
            skill_rows=skill_rows,
            allowed_fact_ids=sorted(allowed_facts),
            proof_pool_metadata=proof_pool_metadata,
            selected_fact_plan=selected_fact_plan,
        )

    eligible_rows, suppressed_lookup = _skill_rows_to_maps(
        skill_rows, suppressed_skill_ids=suppressed_skill_ids
    )
    cited = _cited_fact_ids(text_claim_coverage)
    text = resume_display_text or ""

    selected_skill_ids = [str(r.get("skill_id") or "") for r in eligible_rows if r.get("skill_id")]
    allowed_phrases = collect_capsule_phrases(eligible_rows)
    forbidden_phrases = _collect_forbidden_phrases(skill_rows)

    used_phrases: list[str] = []
    semantic_variants_matched: list[dict[str, str]] = []
    for phrase in allowed_phrases:
        direct = _phrase_in_text(phrase, text, variant_map=variant_map)
        if direct:
            used_phrases.append(phrase)
            continue
        for variant in _phrase_variants(phrase, variant_map)[1:]:
            if _phrase_in_text(variant, text, variant_map=variant_map):
                semantic_variants_matched.append({"phrase": phrase, "matched_variant": variant})
                used_phrases.append(phrase)
                break

    cited_fact_ids = sorted(cited & allowed_facts) if allowed_facts else sorted(cited)

    used_skill_ids: list[str] = []
    unused_skill_ids: list[str] = []
    for row in eligible_rows:
        sid = str(row.get("skill_id") or "")
        links = {str(x).strip() for x in (row.get("fact_id_links") or []) if str(x).strip()}
        phrase_hit = any(_phrase_in_text(p, text, variant_map=variant_map) for p in _phrases_from_row(row))
        fact_hit = bool(links & cited)
        # D8: phrase overlap alone is insufficient — require phrase + cited fact_id.
        if phrase_hit and fact_hit:
            used_skill_ids.append(sid)
        else:
            unused_skill_ids.append(sid)

    forbidden_phrase_violations = [
        {"phrase": fp, "reason_code": "forbidden_phrase_in_output"}
        for fp in forbidden_phrases
        if _phrase_in_text(fp, text, variant_map=variant_map)
    ]

    union_allowed = {_normalize_phrase(p) for p in allowed_phrases}
    unsupported_skill_phrase_violations: list[dict[str, str]] = []
    for phrase in used_phrases:
        norm = _normalize_phrase(phrase)
        if norm not in union_allowed:
            unsupported_skill_phrase_violations.append(
                {"phrase": phrase, "reason_code": "phrase_not_in_selected_skill_row_set"}
            )

    denom = len(eligible_rows)
    score = (len(used_skill_ids) / denom) if denom else 0.0
    hard_fail = bool(forbidden_phrase_violations or unsupported_skill_phrase_violations)
    soft_fail = denom > 0 and len(used_skill_ids) == 0
    passed = not hard_fail and not soft_fail

    return {
        "schema": RECEIPT_SCHEMA,
        "plan_id": PLAN_ID,
        "section_id": section_id,
        "selected_skill_ids": selected_skill_ids,
        "allowed_phrases": allowed_phrases,
        "used_phrases": used_phrases,
        "semantic_variants_matched": semantic_variants_matched,
        "cited_fact_ids": cited_fact_ids,
        "unused_skill_ids": unused_skill_ids,
        "used_skill_ids": used_skill_ids,
        "suppressed_skill_ids": [
            {"skill_id": sid, "reason_code": reason} for sid, reason in sorted(suppressed_lookup.items())
        ],
        "forbidden_phrase_violations": forbidden_phrase_violations,
        "unsupported_skill_phrase_violations": unsupported_skill_phrase_violations,
        "utilization_score": round(score, 4),
        "eligible_skill_count": denom,
        "pass": passed,
    }


def _phrases_from_row(row: dict[str, Any]) -> list[str]:
    raw = row.get("allowed_phrases") or []
    out = [str(p).strip() for p in raw if str(p).strip()]
    if not out:
        label = str(row.get("label") or "").strip()
        if label:
            out.append(label)
    return out


def _strings(raw: Any) -> list[str]:
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return []
    return [str(x).strip() for x in raw if str(x).strip()]


def build_graph_binding_materiality_summary(
    *,
    section_id: str,
    runtime_payload: Mapping[str, Any] | None = None,
    graph_bindings: Sequence[Mapping[str, Any]] | None = None,
    max_items: int = 8,
) -> dict[str, Any]:
    """Summarize which C0.3 graph bindings materially shape a section.

    The summary is intentionally compact: it gives PA and judges the same
    graph-binding context without treating targeting-only JD or briefing text
    as claim proof.
    """
    payload = runtime_payload if isinstance(runtime_payload, Mapping) else {}
    max_n = max(1, int(max_items or 1))
    targeting = payload.get("graph_targeting_for_pa")
    targeting_map = targeting if isinstance(targeting, Mapping) else {}
    fec = payload.get("canonical_final_evidence_contract_snapshot")
    fec_map = fec if isinstance(fec, Mapping) else {}
    role_family = targeting_map.get("role_family_projection")
    role_family_map = role_family if isinstance(role_family, Mapping) else {}

    allowed_fact_ids = _strings(payload.get("allowed_fact_ids") or fec_map.get("allowed_fact_ids"))
    support_refs = _strings(targeting_map.get("claim_support_graph_refs"))
    pillar_ids = _strings(
        role_family_map.get("pillar_hint_ids") or targeting_map.get("targeting_graph_refs")
    )
    lineage_refs = _strings(targeting_map.get("receipt_only_lineage_refs"))

    binding_fact_ids: list[str] = []
    binding_skill_refs: list[str] = []
    for row in graph_bindings or ():
        if not isinstance(row, Mapping):
            continue
        fid = str(row.get("fact_id") or "").strip()
        if fid:
            binding_fact_ids.append(fid)
        binding_skill_refs.extend(_strings(row.get("claim_support_graph_refs") or row.get("graph_node_refs")))

    compressed: list[dict[str, Any]] = []
    for row in targeting_map.get("overloaded_fact_compression") or []:
        if not isinstance(row, Mapping):
            continue
        compressed.append(
            {
                "fact_id": str(row.get("fact_id") or "").strip(),
                "skill_binding_count_before": row.get("skill_binding_count_before"),
                "skill_binding_count_after": row.get("skill_binding_count_after"),
                "executive_capability_phrases": _strings(row.get("executive_capability_phrases"))[:max_n],
            }
        )
    pp_meta = payload.get("proof_pool_metadata")
    pp_meta_map = pp_meta if isinstance(pp_meta, Mapping) else {}

    return {
        "schema": "apps_rg.graph_binding_materiality_summary.v1",
        "section_id": str(section_id or payload.get("section_id") or "").strip(),
        "authority": "C0.3 graph bindings and FinalEvidenceContract only",
        "jd_and_briefing_policy": "targeting_context_only_not_claim_proof",
        "allowed_fact_ids": allowed_fact_ids[:max_n],
        "allowed_fact_count": len(allowed_fact_ids),
        "claim_support_graph_refs": (support_refs or binding_skill_refs)[:max_n],
        "claim_support_graph_ref_count": len(support_refs or binding_skill_refs),
        "pillar_hint_ids": pillar_ids[:max_n],
        "pillar_hint_count": len(pillar_ids),
        "binding_fact_ids": sorted(set(binding_fact_ids))[:max_n],
        "lineage_ref_count": len(lineage_refs),
        "overloaded_fact_compression": compressed[:max_n],
        "final_evidence_digest": str(fec_map.get("final_evidence_digest") or "").strip(),
        "proof_pool_digest": str(
            payload.get("proof_pool_digest")
            or pp_meta_map.get("proof_pool_digest")
            or ""
        ).strip(),
    }


__all__ = [
    "PLAN_ID",
    "RECEIPT_SCHEMA",
    "SEMANTIC_VARIANT_MAP",
    "build_graph_binding_materiality_summary",
    "score_graph_skills_utilization",
    "validate_scorer_inputs_neg6",
]
