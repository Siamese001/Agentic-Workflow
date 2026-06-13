"""Shared graph-skills proof validation (P2-W3). Fail-closed on ledger authority and false C0.3 claims."""
from __future__ import annotations

from typing import Any, Sequence

from apps_rg.fact_inventory.augmented_skills_graph import SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.c03_graphrag_bound import FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF
from apps_rg.runtime.legacy_proof_sources import (
    FORBIDDEN_PRODUCT_PROOF_SOURCES,
    PROOF_SOURCE_BROAD_SKILLS_LEDGER,
    PROOF_SOURCE_SRFS,
)
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH, SectionProofPool
from apps_rg.runtime.validators.fact_ledger_authority import (
    BLOCKED_FACT_LEDGER_AUTHORITY,
    fact_ledger_authority_violation_reason,
)

FORBIDDEN_PROOF_SOURCES = FORBIDDEN_PRODUCT_PROOF_SOURCES

FORBIDDEN_SELECTED_FACT_PLAN_METHODS = frozenset(
    {
        "canonical_base_resume_employment_bullets",
        "hydrate_unify_bullets_from_canonical_resume",
        "hydrate_ibm_bullets_from_canonical_resume",
        "canonical_json_all_ibm_bullets",
        "base_resume_fallback",
    }
)

BLOCKED_CANDIDATE_FACT_AUTHORITY = "BLOCKED_CANDIDATE_FACT_AUTHORITY"

_CANDIDATE_FACT_AUTHORITY_LABELS = frozenset(
    {
        "candidate_fact",
        "candidate_facts",
        "candidate_fact_ledger",
        "master_candidate_skills_fact_ledger",
        "selected_role_fact_set",
        "srfs",
    }
)

_CANDIDATE_FACT_AUTHORITY_FLAGS = (
    "candidate_fact_authority",
    "candidate_fact_ledger_authority",
    "candidate_fact_ledger_used_as_authority",
    "candidate_fact_ledger_claim_authority",
    "candidate_fact_ledger_proof_authority",
    "candidate_facts_as_proof",
    "candidate_facts_used_as_authority",
    "selected_role_fact_set_used",
)

_AUTHORITY_SOURCE_FIELDS = (
    "proof_source",
    "proof_pool_type",
    "source_authority",
    "skills_source_type",
    "skills_authority_source_type",
    "claim_authority_source_type",
    "proof_authority_source_type",
)


class GraphSkillsProofError(ValueError):
    """Graph-skills proof contract violation."""


def _normalize_authority_label(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _candidate_fact_block(section_id: str, reason: str) -> GraphSkillsProofError:
    return GraphSkillsProofError(
        f"{section_id}: {BLOCKED_CANDIDATE_FACT_AUTHORITY}: {reason}"
    )


def _fact_ledger_block(section_id: str, reason: str) -> GraphSkillsProofError:
    return GraphSkillsProofError(
        f"{section_id}: {BLOCKED_FACT_LEDGER_AUTHORITY}: {reason}"
    )


def assert_fact_ledger_not_skills_metrics_authority(
    *,
    section_id: str,
    proof_pool_metadata: dict[str, Any] | None,
    selected_fact_plan: dict[str, Any] | None = None,
) -> None:
    """W2 gate: fact ledger may be lineage/substrate only, never runtime authority."""
    reason = fact_ledger_authority_violation_reason(
        proof_pool_metadata=proof_pool_metadata,
        selected_fact_plan=selected_fact_plan,
    )
    if reason:
        raise _fact_ledger_block(section_id, reason)


def assert_candidate_fact_authority_deprecated(
    *,
    section_id: str,
    proof_pool_metadata: dict[str, Any] | None,
    selected_fact_plan: dict[str, Any] | None = None,
) -> None:
    """P0 gate: candidate_fact may be lineage only, never runtime authority.

    `candidate_fact_id` compatibility aliases are allowed when the product path
    is already graph-authorized. Any field that presents candidate facts or SRFS
    as proof/skills/claim authority fails closed.
    """
    meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    plan = selected_fact_plan if isinstance(selected_fact_plan, dict) else {}

    for flag in _CANDIDATE_FACT_AUTHORITY_FLAGS:
        if meta.get(flag) is True:
            raise _candidate_fact_block(section_id, f"{flag}=true")

    for field in _AUTHORITY_SOURCE_FIELDS:
        label = _normalize_authority_label(meta.get(field))
        if label in _CANDIDATE_FACT_AUTHORITY_LABELS:
            raise _candidate_fact_block(section_id, f"{field}={label!r}")

    candidate_role = _normalize_authority_label(
        meta.get("candidate_fact_role")
        or meta.get("candidate_fact_ledger_role")
        or meta.get("candidate_facts_role")
    )
    if candidate_role in {
        "authority",
        "proof_authority",
        "claim_authority",
        "skills_authority",
    }:
        raise _candidate_fact_block(section_id, f"candidate_fact_role={candidate_role!r}")

    claim_source = _normalize_authority_label(meta.get("claim_evidence_source_type"))
    if claim_source in _CANDIDATE_FACT_AUTHORITY_LABELS:
        graph_authorized = (
            meta.get("source_authority") == SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
            and meta.get("graph_only_claim_authority") is True
        )
        if not graph_authorized:
            raise _candidate_fact_block(
                section_id,
                "candidate_fact claim substrate without GraphDB authority",
            )

    method = _normalize_authority_label(plan.get("selection_method"))
    if method in _CANDIDATE_FACT_AUTHORITY_LABELS or method.startswith("candidate_fact_ledger"):
        raise _candidate_fact_block(section_id, f"selection_method={method!r}")
    if "selected_role_fact_set" in method or method.startswith("srfs"):
        raise _candidate_fact_block(section_id, f"selection_method={method!r}")


def assert_pool_not_ledger_authority(pool: SectionProofPool) -> None:
    if pool.proof_source in FORBIDDEN_PROOF_SOURCES:
        raise GraphSkillsProofError(
            f"section {pool.section!r} proof_source={pool.proof_source!r} forbidden for product proof"
        )
    if pool.proof_source != PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH:
        raise GraphSkillsProofError(
            f"section {pool.section!r} must use augmented_skills_graph; got {pool.proof_source!r}"
        )
    meta = pool.proof_pool_metadata or {}
    for flag in (
        "broad_skills_ledger_used_as_authority",
        "broad_skills_ledger_default",
        "broad_skills_ledger_fallback",
        "broad_skills_ledger_compatibility_authority",
    ):
        if meta.get(flag) is True:
            raise GraphSkillsProofError(f"{flag} must be false for {pool.section!r}")
    if pool.fallback_used or pool.base_resume_fallback_used:
        raise GraphSkillsProofError(f"fallback flags set for {pool.section!r}")
    if pool.broad_skills_ledger_present and meta.get("broad_skills_ledger_used_as_authority") is not False:
        raise GraphSkillsProofError(f"broad_skills_ledger_present without deprecation for {pool.section!r}")
    assert_fact_ledger_not_skills_metrics_authority(
        section_id=pool.section,
        proof_pool_metadata=meta,
        selected_fact_plan=pool.selected_fact_plan,
    )
    assert_candidate_fact_authority_deprecated(
        section_id=pool.section,
        proof_pool_metadata=meta,
        selected_fact_plan=pool.selected_fact_plan,
    )


def assert_c03_bound_claim_valid(*, section_id: str, meta: dict[str, Any]) -> None:
    status = str(meta.get("c03_graph_bound_status") or meta.get("c03_graphrag_bound_status") or "")
    if status != "BOUND":
        return
    hop_count = int(meta.get("c03_graph_hop_paths_count") or 0)
    if hop_count <= 0:
        c03 = meta.get("c03_graphrag_bound")
        if isinstance(c03, dict):
            hop_count = int(c03.get("graph_hop_paths_count") or len(c03.get("graph_expansion_refs") or []))
    if hop_count <= 0:
        raise GraphSkillsProofError(
            f"{section_id}: c03_graph_bound_status=BOUND without graph_hop_paths_count"
        )
    raw_non_graph = meta.get("non_graph_evidence_items_count")
    non_graph = int(raw_non_graph) if raw_non_graph is not None else 0
    if non_graph != 0:
        raise GraphSkillsProofError(
            f"{section_id}: BOUND claim with non_graph_evidence_items_count={non_graph}"
        )
    c03 = meta.get("c03_graphrag_bound")
    if isinstance(c03, dict):
        support = str(c03.get("support_status") or "")
        if support in FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF:
            raise GraphSkillsProofError(f"{section_id}: forbidden support_status {support!r}")


def assert_skill_rows_graph_supported(skill_rows: list[dict[str, Any]]) -> None:
    for row in skill_rows:
        links = row.get("fact_id_links") or []
        hop = row.get("graph_hop_path") or []
        if not links:
            raise GraphSkillsProofError(f"skill {row.get('skill_id')!r} missing fact_id_links")
        if not hop:
            raise GraphSkillsProofError(f"skill {row.get('skill_id')!r} missing graph_hop_path")


def assert_no_non_graph_evidence(meta: dict[str, Any], *, section_id: str) -> None:
    raw = meta.get("non_graph_evidence_items_count")
    count = int(raw) if raw is not None else 0
    if count > 0:
        raise GraphSkillsProofError(f"{section_id}: non_graph_evidence_items_count={count}")


def assert_forbidden_proof_source(*, section_id: str, proof_source: str) -> None:
    """NEG-4: broad_skills_ledger / SRFS cannot be product proof authority."""
    if proof_source in FORBIDDEN_PROOF_SOURCES:
        raise GraphSkillsProofError(
            f"{section_id}: proof_source={proof_source!r} forbidden "
            f"(expected augmented_skills_graph; not {PROOF_SOURCE_BROAD_SKILLS_LEDGER!r} or {PROOF_SOURCE_SRFS!r})"
        )


def assert_capsule_phrase_cannot_satisfy_unsupported_claim(
    *,
    section_id: str,
    text_claim_coverage: dict[str, Any] | None,
    allowed_fact_ids: Sequence[str],
    capsule_phrases: Sequence[str],
) -> None:
    """NEG-2: capsule-only phrase cannot satisfy unsupported-claim coverage without allowed_fact_ids."""
    cov = text_claim_coverage if isinstance(text_claim_coverage, dict) else {}
    allowed = {str(x).strip() for x in allowed_fact_ids if str(x).strip()}
    phrases = [str(p).strip() for p in capsule_phrases if str(p).strip()]
    if not phrases:
        return
    phrase_set = {p.casefold() for p in phrases}
    for row in cov.get("sentences") or []:
        if not isinstance(row, dict):
            continue
        cited = row.get("cited_fact_ids") or row.get("fact_ids") or row.get("source_fact_ids") or []
        cited_ids = {str(x).strip() for x in cited if str(x).strip()}
        if cited_ids & allowed:
            continue
        if row.get("supported") is True or row.get("pass") is True:
            text = str(row.get("claim_text") or row.get("text") or row.get("sentence") or "").casefold()
            if any(p in text for p in phrase_set):
                raise GraphSkillsProofError(
                    f"{section_id}: capsule phrase satisfied coverage without allowed_fact_ids"
                )


def assert_hybrid_fact_ids_in_resolver_pool(
    *,
    section_id: str,
    hybrid_suggested_fact_ids: Sequence[str],
    resolver_allowed_fact_ids: Sequence[str],
) -> list[dict[str, str]]:
    """NEG-3: hybrid reorder must not widen pool — out-of-pool ids fail closed."""
    allowed = {str(x).strip() for x in resolver_allowed_fact_ids if str(x).strip()}
    rejected: list[dict[str, str]] = []
    for raw in hybrid_suggested_fact_ids:
        fid = str(raw).strip()
        if not fid:
            continue
        if fid not in allowed:
            rejected.append({"fact_id": fid, "reason": "outside_resolver_pool"})
    if rejected:
        raise GraphSkillsProofError(
            f"{section_id}: hybrid suggested fact_ids outside resolver pool: {rejected!r}"
        )
    return rejected


def assert_selected_fact_plan_not_base_resume_authority(
    *,
    section_id: str,
    proof_pool_metadata: dict[str, Any] | None,
    selected_fact_plan: dict[str, Any] | None,
) -> None:
    """NEG-5: base-resume hydration cannot become selected_fact_plan authority."""
    meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    if meta.get("base_resume_claim_authority") is True:
        raise GraphSkillsProofError(f"{section_id}: base_resume_claim_authority forbidden")
    if meta.get("base_resume_fallback_used") is True or meta.get("fallback_used") is True:
        raise GraphSkillsProofError(f"{section_id}: base_resume fallback cannot be plan authority")
    plan = selected_fact_plan if isinstance(selected_fact_plan, dict) else {}
    method = str(plan.get("selection_method") or meta.get("selection_method") or "").strip()
    facts = plan.get("facts") or []
    if method in FORBIDDEN_SELECTED_FACT_PLAN_METHODS and facts:
        raise GraphSkillsProofError(
            f"{section_id}: selection_method {method!r} cannot author selected_fact_plan facts"
        )
    if "base_resume" in method.casefold() and facts and meta.get("graph_only_claim_authority") is not True:
        raise GraphSkillsProofError(
            f"{section_id}: base_resume selection_method {method!r} without graph_only_claim_authority"
        )


def assert_capsule_phrases_not_proof_authority(
    *,
    section_id: str,
    proof_pool_metadata: dict[str, Any] | None,
    allowed_fact_ids: Sequence[str],
    selected_fact_plan: dict[str, Any] | None,
) -> None:
    """NEG-6: allowed_phrases / capsule text must not appear as proof authority."""
    meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    allowed = {str(x).strip() for x in allowed_fact_ids if str(x).strip()}
    phrases: list[str] = []
    for row in meta.get("selected_skill_rows") or []:
        if isinstance(row, dict):
            phrases.extend(str(p).strip() for p in (row.get("allowed_phrases") or []) if str(p).strip())
            label = str(row.get("label") or "").strip()
            if label:
                phrases.append(label)
    for phrase in phrases:
        if phrase in allowed:
            raise GraphSkillsProofError(
                f"{section_id}: capsule phrase {phrase!r} must not equal allowed_fact_id"
            )
    if meta.get("allowed_fact_ids") and isinstance(meta.get("allowed_fact_ids"), list):
        for entry in meta["allowed_fact_ids"]:
            text = str(entry).strip()
            if text and text not in allowed and not text.startswith(("bul_", "fact_", "met_")):
                if any(text.lower() == p.lower() for p in phrases):
                    raise GraphSkillsProofError(
                        f"{section_id}: proof_pool_metadata.allowed_fact_ids leaks capsule phrase"
                    )
    plan = selected_fact_plan if isinstance(selected_fact_plan, dict) else {}
    for fact in plan.get("facts") or []:
        if not isinstance(fact, dict):
            continue
        fid = str(fact.get("fact_id") or "").strip()
        for phrase in phrases:
            if fid.lower() == phrase.lower():
                raise GraphSkillsProofError(
                    f"{section_id}: fact_id must not be capsule phrase {phrase!r}"
                )


def validate_section_graph_pool(pool: SectionProofPool) -> dict[str, Any]:
    """Validate a resolved section pool; return summary dict."""
    assert_pool_not_ledger_authority(pool)
    meta = dict(pool.proof_pool_metadata or {})
    assert_c03_bound_claim_valid(section_id=pool.section, meta=meta)
    assert_no_non_graph_evidence(meta, section_id=pool.section)
    skill_rows = meta.get("selected_skill_rows") or []
    if skill_rows:
        assert_skill_rows_graph_supported(list(skill_rows))
    return {
        "section": pool.section,
        "proof_source": pool.proof_source,
        "c03_graph_bound_status": meta.get("c03_graph_bound_status"),
        "broad_skills_ledger_used_as_authority": meta.get("broad_skills_ledger_used_as_authority", False),
        "selection_method": meta.get("selection_method") or pool.selected_fact_plan.get("selection_method"),
    }


__all__ = [
    "BLOCKED_CANDIDATE_FACT_AUTHORITY",
    "BLOCKED_FACT_LEDGER_AUTHORITY",
    "GraphSkillsProofError",
    "FORBIDDEN_SELECTED_FACT_PLAN_METHODS",
    "assert_candidate_fact_authority_deprecated",
    "assert_fact_ledger_not_skills_metrics_authority",
    "assert_capsule_phrase_cannot_satisfy_unsupported_claim",
    "assert_capsule_phrases_not_proof_authority",
    "assert_forbidden_proof_source",
    "assert_hybrid_fact_ids_in_resolver_pool",
    "assert_selected_fact_plan_not_base_resume_authority",
    "assert_c03_bound_claim_valid",
    "assert_no_non_graph_evidence",
    "assert_pool_not_ledger_authority",
    "assert_skill_rows_graph_supported",
    "validate_section_graph_pool",
]
