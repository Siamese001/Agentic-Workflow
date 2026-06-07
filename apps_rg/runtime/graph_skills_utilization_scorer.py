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


def _iter_mappings(value: Any):
    if isinstance(value, Mapping):
        yield value
        for inner in value.values():
            yield from _iter_mappings(inner)
    elif isinstance(value, (list, tuple)):
        for inner in value:
            yield from _iter_mappings(inner)


def _collect_string_values(value: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(value, str):
        text = value.strip()
        if text:
            out.add(text)
    elif isinstance(value, (list, tuple, set)):
        for inner in value:
            out.update(_collect_string_values(inner))
    return out


def _collect_values_for_keys(payloads: Sequence[Any], keys: set[str]) -> set[str]:
    out: set[str] = set()
    for payload in payloads:
        for row in _iter_mappings(payload):
            for key in keys:
                if key in row:
                    out.update(_collect_string_values(row.get(key)))
    return out


def _role_episode_bundles_from_metadata(meta: Mapping[str, Any]) -> tuple[set[str], set[str], set[str]]:
    bundle_ids = _collect_values_for_keys([meta], {"role_episode_bundle_ids", "role_episode_bundle_id"})
    skill_ids = set(_collect_values_for_keys([meta], {"graph_skill_node_ids", "source_skill_ids"}))
    linked_fact_ids = set(_collect_values_for_keys([meta], {"linked_source_fact_ids", "source_fact_ids"}))
    for row in meta.get("role_episode_bundles") or []:
        if not isinstance(row, Mapping):
            continue
        bundle_ids.update(_collect_values_for_keys([row], {"role_episode_bundle_id"}))
        skill_ids.update(_collect_values_for_keys([row], {"graph_skill_node_ids", "source_skill_ids"}))
        linked_fact_ids.update(_collect_values_for_keys([row], {"linked_source_fact_ids", "source_fact_ids"}))
    return bundle_ids, skill_ids, linked_fact_ids


def build_graph_binding_materiality_summary(
    *,
    section_id: str,
    proof_pool_metadata: Mapping[str, Any] | None = None,
    candidate_output: Mapping[str, Any] | None = None,
    claim_ledger: Sequence[Mapping[str, Any]] | None = None,
    parsed_output: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compact PA/judge summary proving graph metadata is materially consumed."""
    meta = proof_pool_metadata if isinstance(proof_pool_metadata, Mapping) else {}
    candidate = candidate_output if isinstance(candidate_output, Mapping) else {}
    parsed = parsed_output if isinstance(parsed_output, Mapping) else {}
    ledger = list(claim_ledger or [])
    usage_payloads: list[Any] = [candidate, parsed, ledger]

    native = meta.get("native_c03_final_evidence")
    native_meta = meta.get("c03_pa_metadata") if isinstance(meta.get("c03_pa_metadata"), Mapping) else {}
    native_active = isinstance(native, Mapping) or str(meta.get("native_c03_status") or "") == "EMITTED"
    native_fact_ids = set()
    if isinstance(native, Mapping):
        native_fact_ids.update(_collect_values_for_keys([native], {"selected_source_fact_ids"}))
    native_fact_ids.update(_collect_values_for_keys([native_meta], {"c03_allowed_fact_ids"}))

    role_active = bool(meta.get("role_episode_bundle_consumption") or meta.get("role_episode_bundles"))
    role_bundle_ids, role_skill_ids, role_fact_ids = _role_episode_bundles_from_metadata(meta)

    used_fact_ids = _collect_values_for_keys(usage_payloads, {"source_fact_ids", "fact_ids", "cited_fact_ids"})
    used_bundle_ids = _collect_values_for_keys(
        usage_payloads, {"role_episode_bundle_id", "role_episode_bundle_ids"}
    )
    used_skill_ids = _collect_values_for_keys(
        usage_payloads, {"graph_skill_node_ids", "source_skill_ids", "skill_ids_used"}
    )

    has_candidate_material = bool(candidate or parsed or ledger)
    violations: list[dict[str, str]] = []
    native_matched = sorted(native_fact_ids & used_fact_ids)
    role_bundle_matched = sorted(role_bundle_ids & used_bundle_ids)
    role_skill_matched = sorted(role_skill_ids & used_skill_ids)
    role_fact_matched = sorted(role_fact_ids & used_fact_ids)

    if has_candidate_material:
        if native_active and native_fact_ids and not native_matched:
            violations.append(
                {
                    "reason_code": "native_c03_metadata_without_cited_fact_use",
                    "detail": "native C0.3 selected_source_fact_ids were not cited by candidate output",
                }
            )
        if role_active and role_bundle_ids and not role_bundle_matched:
            violations.append(
                {
                    "reason_code": "role_episode_metadata_without_bundle_use",
                    "detail": "role_episode_bundle_ids were not present in candidate output",
                }
            )
        if role_active and role_skill_ids and not (role_skill_matched or role_fact_matched):
            violations.append(
                {
                    "reason_code": "role_episode_metadata_without_skill_or_fact_use",
                    "detail": "role episode graph_skill_node_ids or linked_source_fact_ids were not used",
                }
            )

    if not (native_active or role_active):
        status = "NO_GRAPH_BINDING_METADATA"
    elif not has_candidate_material:
        status = "PENDING_CANDIDATE_OUTPUT"
    else:
        status = "FAIL" if violations else "PASS"

    return {
        "schema": "apps_rg_graph_binding_materiality_summary_v1",
        "section_id": section_id,
        "status": status,
        "violation_count": len(violations),
        "violations": violations,
        "native_c03_active": native_active,
        "native_c03_selected_fact_count": len(native_fact_ids),
        "native_c03_cited_fact_count": len(native_matched),
        "native_c03_cited_fact_ids": native_matched[:24],
        "role_episode_active": role_active,
        "role_episode_bundle_count": len(role_bundle_ids),
        "role_episode_bundle_intersection_count": len(role_bundle_matched),
        "role_episode_skill_intersection_count": len(role_skill_matched),
        "role_episode_fact_intersection_count": len(role_fact_matched),
        "judge_instruction": "metadata-only graph context is insufficient; require candidate citations or bindings",
    }


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


__all__ = [
    "build_graph_binding_materiality_summary",
    "PLAN_ID",
    "RECEIPT_SCHEMA",
    "SEMANTIC_VARIANT_MAP",
    "score_graph_skills_utilization",
    "validate_scorer_inputs_neg6",
]
