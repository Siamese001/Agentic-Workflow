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

CONFIDENCE_STRENGTH_WEIGHTS: dict[str, float] = {
    "HIGH": 0.35,
    "MEDIUM": 0.2,
    "LOW": 0.05,
    "BLOCKED": 0.0,
}

SUPPORT_STRENGTH_WEIGHTS: dict[str, float] = {
    "DIRECT_FROM_RESUME_ARCHIVE": 0.18,
    "USER_CONFIRMED_DIRECT": 0.18,
    "ACTIVE_CONFIRMED": 0.16,
    "BUNDLE_SUPPORTED": 0.14,
    "DERIVED_SUPPORTED": 0.12,
    "FACT_SUBSTRATE": 0.1,
    "USER_CONFIRMED_PENDING_SOURCE": 0.04,
}

APPROVED_POLICY_TOKENS = ("approved", "eligible", "allowed")
BLOCKING_POLICY_TOKENS = ("blocked", "forbidden", "held", "unapproved", "not claimable", "do_not_promote")
BLOCKING_STATUS_TOKENS = ("BLOCKED", "DO_NOT_PROMOTE", "FORBIDDEN", "SUPPRESSED")
PENDING_STATUS_TOKENS = ("DRAFT", "PENDING", "USER_CONFIRMED_PENDING_SOURCE")

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


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().casefold()
    return text in {"1", "true", "yes", "y", "confirmed"}


def _row_strings(row: Mapping[str, Any], keys: set[str]) -> set[str]:
    return _collect_values_for_keys([row], keys)


def _policy_has_token(text: str, tokens: Sequence[str]) -> bool:
    lowered = str(text or "").casefold()
    return any(token in lowered for token in tokens)


def _band_for_evidence_strength(score: float, *, blocked: bool) -> str:
    if blocked:
        return "BLOCKED"
    if score >= 0.75:
        return "HIGH"
    if score >= 0.45:
        return "MEDIUM"
    if score > 0:
        return "LOW"
    return "NONE"


def score_evidence_strength_for_skill_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Derive local evidence strength from existing graph-skill metadata.

    This score is report-only metadata. It does not create proof authority and
    does not make skill ids, capsule phrases, or JD text claim evidence.
    """
    skill_id = str(row.get("skill_id") or row.get("node_id") or "").strip()
    confidence = str(
        row.get("confidence_grade") or row.get("confidence") or row.get("evidence_confidence") or ""
    ).strip().upper()
    support = str(row.get("support_level") or "").strip().upper()
    activation = str(row.get("activation_status") or "").strip().upper()
    external_policy = str(row.get("external_claim_policy") or row.get("claim_verification_policy") or "")

    fact_ids = _row_strings(row, {"fact_id_links", "linked_source_fact_ids", "source_fact_ids", "fact_ids"})
    metric_ids = _row_strings(
        row,
        {
            "linked_metric_outcome_ids",
            "metric_outcome_ids",
            "approved_metric_outcome_ids",
            "metric_ids",
        },
    )
    source_refs = _row_strings(
        row,
        {
            "source_trace",
            "archive_trace",
            "source_resume_files",
            "source_evidence",
            "source_fact_ids",
            "linked_source_fact_ids",
        },
    )

    components = {
        "confidence": CONFIDENCE_STRENGTH_WEIGHTS.get(confidence, 0.0),
        "support": SUPPORT_STRENGTH_WEIGHTS.get(support, 0.0),
        "fact_links": 0.0,
        "metric_outcomes": 0.0,
        "source_confirmation": 0.0,
        "claim_policy": 0.0,
    }
    if fact_ids:
        components["fact_links"] = 0.18 + min(0.06, 0.01 * len(fact_ids))
    if metric_ids:
        components["metric_outcomes"] = 0.14 + min(0.06, 0.02 * len(metric_ids))
    if source_refs or _truthy(row.get("human_confirmed")) or _truthy(row.get("human_confirmed_archive_promotion")):
        components["source_confirmation"] = 0.05
    policy_blocked = _policy_has_token(external_policy, BLOCKING_POLICY_TOKENS)
    if not policy_blocked and (
        _policy_has_token(external_policy, APPROVED_POLICY_TOKENS) or _truthy(row.get("external_eligible"))
    ):
        components["claim_policy"] = 0.07

    penalties: dict[str, float] = {}
    status_blob = " ".join(x for x in (confidence, support, activation) if x)
    if any(token in status_blob for token in BLOCKING_STATUS_TOKENS):
        penalties["blocked_or_suppressed_status"] = 0.5
    elif any(token in status_blob for token in PENDING_STATUS_TOKENS):
        penalties["pending_or_draft_status"] = 0.18
    if policy_blocked:
        penalties["blocking_claim_policy"] = 0.25
    if not fact_ids and not metric_ids:
        penalties["no_fact_or_metric_links"] = 0.12

    raw_score = sum(components.values()) - sum(penalties.values())
    score = round(max(0.0, min(1.0, raw_score)), 4)
    blocked = bool(
        penalties.get("blocked_or_suppressed_status")
        or penalties.get("blocking_claim_policy")
        or confidence == "BLOCKED"
    )
    return {
        "skill_id": skill_id,
        "evidence_strength_score": score,
        "evidence_strength_band": _band_for_evidence_strength(score, blocked=blocked),
        "confidence_grade": confidence,
        "support_level": support,
        "fact_id_count": len(fact_ids),
        "metric_outcome_id_count": len(metric_ids),
        "components": {k: round(v, 4) for k, v in components.items() if v},
        "penalties": {k: round(v, 4) for k, v in penalties.items() if v},
        "authority_note": "derived_score_only_not_claim_proof",
    }


def summarize_evidence_strength(skill_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [score_evidence_strength_for_skill_row(row) for row in skill_rows if isinstance(row, Mapping)]
    rows.sort(key=lambda r: (-float(r["evidence_strength_score"]), str(r.get("skill_id") or "")))
    band_counts: dict[str, int] = {}
    for row in rows:
        band = str(row.get("evidence_strength_band") or "NONE")
        band_counts[band] = band_counts.get(band, 0) + 1
    average = round(
        sum(float(row["evidence_strength_score"]) for row in rows) / len(rows), 4
    ) if rows else 0.0
    return {
        "schema": "apps_rg_evidence_strength_summary_v1",
        "scoring_mode": "derived_report_only_no_claim_authority",
        "eligible_skill_count": len(rows),
        "average_score": average,
        "band_counts": band_counts,
        "top_skill_strength": rows[:12],
    }


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


def _build_proof_pool_graph_binding_materiality_summary(
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
    evidence_strength = summarize_evidence_strength(eligible_rows)
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
        "evidence_strength": evidence_strength,
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
    proof_pool_metadata: Mapping[str, Any] | None = None,
    candidate_output: Mapping[str, Any] | None = None,
    claim_ledger: Sequence[Mapping[str, Any]] | None = None,
    parsed_output: Mapping[str, Any] | None = None,
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
    payload_pp_meta = payload.get("proof_pool_metadata")
    pp_meta = (
        proof_pool_metadata
        if isinstance(proof_pool_metadata, Mapping)
        else payload_pp_meta
        if isinstance(payload_pp_meta, Mapping)
        else None
    )
    legacy_summary: dict[str, Any] = {}
    if (
        pp_meta is not None
        or candidate_output is not None
        or claim_ledger is not None
        or parsed_output is not None
    ):
        legacy_summary = _build_proof_pool_graph_binding_materiality_summary(
            section_id=section_id,
            proof_pool_metadata=pp_meta,
            candidate_output=candidate_output,
            claim_ledger=claim_ledger,
            parsed_output=parsed_output,
        )

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
    pp_meta_map = pp_meta if isinstance(pp_meta, Mapping) else {}

    graph_context_present = bool(
        allowed_fact_ids
        or support_refs
        or binding_skill_refs
        or pillar_ids
        or lineage_refs
        or compressed
        or str(fec_map.get("final_evidence_digest") or "").strip()
        or str(payload.get("proof_pool_digest") or pp_meta_map.get("proof_pool_digest") or "").strip()
    )

    graph_summary = {
        "schema": "apps_rg.graph_binding_materiality_summary.v1",
        "section_id": str(section_id or payload.get("section_id") or "").strip(),
        "authority": "C0.3 graph bindings and FinalEvidenceContract only",
        "jd_and_briefing_policy": "targeting_context_only_not_claim_proof",
        "graph_context_present": graph_context_present,
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
    if legacy_summary:
        merged = dict(legacy_summary)
        merged.update(graph_summary)
        if str(legacy_summary.get("status") or "") == "NO_GRAPH_BINDING_METADATA" and graph_context_present:
            merged["status"] = "GRAPH_CONTEXT_PRESENT"
            merged["judge_instruction"] = (
                "graph context is available for PA/judge parity; candidate output still must cite "
                "source facts or graph bindings when making claims"
            )
        return merged
    return graph_summary


__all__ = [
    "build_graph_binding_materiality_summary",
    "PLAN_ID",
    "RECEIPT_SCHEMA",
    "SEMANTIC_VARIANT_MAP",
    "score_graph_skills_utilization",
    "score_evidence_strength_for_skill_row",
    "summarize_evidence_strength",
    "validate_scorer_inputs_neg6",
]
