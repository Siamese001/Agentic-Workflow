"""Mandatory product evidence authority law for apps_rg section lanes.

Three explicit concepts (not ``proof_pool_type`` switches):

1. **evidence_authority** — claim/skills proof; product value must be ``augmented_skills_graph``.
2. **selection_scope** — SRFS slice, JD/briefing targeting; may filter facts, never proof authority.
3. **layout_context** — base resume for static anchors only; never generated story claims.

Canonical CLI ``python -m apps_rg --section <lane>`` must fail closed when law is violated.
"""
from __future__ import annotations

import re
from dataclasses import replace
from typing import TYPE_CHECKING, Any, Mapping

from apps_rg.runtime.legacy_proof_sources import FORBIDDEN_PROOF_POOL_TYPE_LABELS
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.section_cli_defaults import SectionCliConfigError
from apps_rg.runtime.validators.fact_ledger_authority import (
    BLOCKED_FACT_LEDGER_AUTHORITY,
    fact_ledger_authority_violation_reason,
)

if TYPE_CHECKING:
    from apps_rg.runtime.proof_pool_resolver import SectionProofPool

_PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH = PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH

EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH = PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH

FORBIDDEN_EVIDENCE_AUTHORITIES: frozenset[str] = frozenset(
    {
        "selected_role_fact_set",
        "base_resume_fallback",
        "broad_skills_ledger",
        "candidate_fact_ledger",
        "prompt_pool",
        "proof_pool",
        "legacy_pool",
        "fallback_pool",
        "base_resume",
        "srfs",
        "unknown",
    }
)

_LAYOUT_ANCHOR_KEYS: tuple[str, ...] = (
    "titles",
    "companies",
    "dates",
    "education",
    "certifications",
    "identity",
    "company_names",
    "locations",
)

# Prompt blocks must not label generated story evidence as base-resume authority.
_FORBIDDEN_PROMPT_STORY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pat, re.IGNORECASE)
    for pat in (
        r"base\s+resume\s+(?:as\s+)?(?:claim|story|proof)\s+authority",
        r"CLAIM\s+SUPPORT\s+POOL\s*:\s*BASE\s+RESUME",
        r"BASE_RESUME\s+AUTHORITY",
        r"story\s+evidence\s+from\s+base\s+resume",
        r"selected_role_fact_set\s+as\s+(?:claim|skills|proof)\s+authority",
        r"broad_skills_ledger\s+as\s+skills\s+SSOT",
        r"proof[\s_-]*pool\s+as\s+(?:claim|story|proof)\s+authority",
        r"prompt[\s_-]*pool\s+as\s+(?:claim|story|proof)\s+authority",
        r"CLAIM\s+SUPPORT\s+POOL\s*:\s*PROOF\s+POOL",
        r"legacy[\s_-]*pool\s+authority",
        r"fallback[\s_-]*pool\s+authority",
    )
)


class ProductEvidenceAuthorityError(SectionCliConfigError):
    """Product evidence authority law violation (CLI exit 2)."""


def build_evidence_authority(
    *,
    graph_ref: str,
    ledger_ref: str,
    graph_digest: str = "",
    ledger_digest: str = "",
    skills_authority_status: str = "PASS",
    block_reason: str = "",
) -> dict[str, Any]:
    """Canonical evidence authority block for proof_pool_metadata."""
    status = str(skills_authority_status or "").strip() or "UNKNOWN"
    return {
        "authority": EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "graph_ref": str(graph_ref or "").strip(),
        "ledger_ref": str(ledger_ref or "").strip(),
        "graph_digest": str(graph_digest or "").strip() or None,
        "ledger_digest": str(ledger_digest or "").strip() or None,
        "skills_authority_status": status,
        "block_reason": str(block_reason or "").strip() or None,
        "forbidden_as_product_authority": sorted(FORBIDDEN_EVIDENCE_AUTHORITIES),
    }


def build_selection_scope(
    *,
    section_id: str,
    selection_method: str,
    targeting_inputs_used: Mapping[str, bool] | None = None,
    srfs_selection_id: str = "",
    srfs_ref: str = "",
    allowed_fact_ids_count: int = 0,
) -> dict[str, Any]:
    """Selection / targeting scope — not proof authority."""
    targeting = dict(targeting_inputs_used or {})
    scope: dict[str, Any] = {
        "section_id": str(section_id or "").strip(),
        "selection_method": str(selection_method or "").strip() or "graph_substrate_allocation",
        "role_target_projection": "graph_ledger_substrate_with_optional_srfs_filter",
        "jd_targeting_active": bool(targeting.get("jd_title_company")),
        "briefing_targeting_active": bool(targeting.get("briefing")),
        "jd_ref": "targeting_only",
        "briefing_ref": "targeting_only",
        "section_slice": str(section_id or "").strip() or None,
        "allowed_fact_ids_count": int(allowed_fact_ids_count),
        "is_proof_authority": False,
    }
    srfs_id = str(srfs_selection_id or "").strip()
    srfs_path = str(srfs_ref or "").strip()
    if srfs_id:
        scope["srfs_selection_id"] = srfs_id
    if srfs_path:
        scope["srfs_ref"] = srfs_path
    return scope


def build_layout_context(
    *,
    base_resume_json_ref: str,
    base_resume_json_hash: str,
    override_used: bool = False,
) -> dict[str, Any]:
    """Base resume for static layout anchors only."""
    return {
        "base_resume_ref": str(base_resume_json_ref or "").strip() or None,
        "base_resume_json_ref": str(base_resume_json_ref or "").strip(),
        "base_resume_json_hash": str(base_resume_json_hash or "").strip(),
        "override_used": bool(override_used),
        "allowed_fields": list(_LAYOUT_ANCHOR_KEYS),
        "permitted_uses": list(_LAYOUT_ANCHOR_KEYS),
        "story_claim_authority": False,
        "generated_story_claims_from_base_resume": False,
    }


def attach_product_evidence_law_to_metadata(
    meta: dict[str, Any],
    *,
    pool: "SectionProofPool",
    selection_method: str = "",
) -> dict[str, Any]:
    """Merge three-concept blocks into proof_pool_metadata; preserve legacy keys for X2."""
    m = dict(meta or {})
    graph_ref = str(
        m.get("graph_ref")
        or m.get("augmented_skills_graph_ref")
        or pool.proof_pool_ref
        or ""
    ).strip()
    ledger_ref = str(
        m.get("claim_evidence_substrate_ref")
        or m.get("candidate_fact_ledger_ref")
        or pool.broad_skills_ledger_ref
        or ""
    ).strip()
    graph_digest = str(m.get("graph_digest") or m.get("augmented_skills_graph_digest") or "").strip()
    ledger_digest = str(pool.broad_skills_ledger_digest or "").strip()
    skills_status = str(m.get("skills_authority_status") or "UNKNOWN").strip()

    sel_method = str(selection_method or m.get("selection_method") or pool.selected_fact_plan.get("selection_method") or "").strip()

    m["evidence_authority"] = build_evidence_authority(
        graph_ref=graph_ref,
        ledger_ref=ledger_ref,
        graph_digest=graph_digest,
        ledger_digest=ledger_digest,
        skills_authority_status=skills_status,
        block_reason=str(m.get("skills_authority_block_reason") or ""),
    )
    m["selection_scope"] = build_selection_scope(
        section_id=pool.section,
        selection_method=sel_method,
        targeting_inputs_used=pool.targeting_inputs_used,
        srfs_ref=str(pool.srfs_ref or "").strip(),
        allowed_fact_ids_count=len(pool.allowed_fact_ids),
    )
    m["layout_context"] = build_layout_context(
        base_resume_json_ref=pool.base_resume_json_ref,
        base_resume_json_hash=pool.base_resume_json_hash,
        override_used=pool.base_resume_override_used,
    )
    # Receipt label only — must not drive authority (see proof_pool_type_role).
    m["proof_pool_type"] = EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    m["proof_pool_type_role"] = "receipt_label_not_authority_switch"
    m["product_story_authority_modes_removed"] = sorted(FORBIDDEN_EVIDENCE_AUTHORITIES)
    m["base_resume_claim_authority"] = False
    m["graph_only_claim_authority"] = True
    m["selected_role_fact_set_used"] = False
    m["broad_skills_ledger_used_as_authority"] = False
    m["broad_skills_ledger_used"] = False
    return m


def validate_evidence_authority_block(ea: Mapping[str, Any], *, section_id: str = "") -> None:
    """Fail closed on evidence_authority violations."""
    label = section_id or "section"
    if not isinstance(ea, Mapping) or not ea:
        raise ProductEvidenceAuthorityError(f"{label}: missing evidence_authority block")

    authority = str(ea.get("authority") or "").strip()
    if not authority or authority == "unknown":
        raise ProductEvidenceAuthorityError(f"{label}: empty or unknown evidence_authority")
    if authority in FORBIDDEN_EVIDENCE_AUTHORITIES:
        raise ProductEvidenceAuthorityError(
            f"{label}: forbidden evidence_authority {authority!r}; "
            f"product requires {EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH!r}"
        )
    if authority != EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH:
        raise ProductEvidenceAuthorityError(
            f"{label}: evidence_authority must be {EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH!r}; got {authority!r}"
        )

    graph_ref = str(ea.get("graph_ref") or "").strip()
    ledger_ref = str(ea.get("ledger_ref") or "").strip()
    if not graph_ref:
        raise ProductEvidenceAuthorityError(f"{label}: evidence_authority.graph_ref required")
    if not ledger_ref:
        raise ProductEvidenceAuthorityError(f"{label}: evidence_authority.ledger_ref required")

    status = str(ea.get("skills_authority_status") or "").strip()
    if status != "PASS":
        reason = str(ea.get("block_reason") or "augmented_skills_graph_unavailable")
        raise ProductEvidenceAuthorityError(f"{label}: augmented skills graph BLOCKED ({reason})")


def validate_layout_context_block(lc: Mapping[str, Any], *, section_id: str = "") -> None:
    label = section_id or "section"
    if not isinstance(lc, Mapping) or not lc:
        raise ProductEvidenceAuthorityError(f"{label}: missing layout_context block")
    if lc.get("story_claim_authority") is True:
        raise ProductEvidenceAuthorityError(f"{label}: layout_context must not grant story_claim_authority")
    if lc.get("generated_story_claims_from_base_resume") is True:
        raise ProductEvidenceAuthorityError(
            f"{label}: layout_context must not allow generated_story_claims_from_base_resume"
        )


def validate_selection_scope_block(ss: Mapping[str, Any], *, section_id: str = "") -> None:
    label = section_id or "section"
    if not isinstance(ss, Mapping) or not ss:
        raise ProductEvidenceAuthorityError(f"{label}: missing selection_scope block")
    if ss.get("is_proof_authority") is True:
        raise ProductEvidenceAuthorityError(f"{label}: selection_scope must not be proof authority")


def validate_proof_pool_metadata_product_law(
    meta: Mapping[str, Any] | None,
    *,
    section_id: str = "",
    proof_source: str = "",
) -> None:
    """Validate full metadata contract for product CLI paths."""
    label = section_id or "section"
    if not isinstance(meta, Mapping) or not meta:
        raise ProductEvidenceAuthorityError(f"{label}: empty proof_pool_metadata")

    if proof_source and proof_source != _PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH:
        raise ProductEvidenceAuthorityError(
            f"{label}: proof_source must be {_PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH!r}; got {proof_source!r}"
        )

    validate_evidence_authority_block(meta.get("evidence_authority") or {}, section_id=label)
    validate_selection_scope_block(meta.get("selection_scope") or {}, section_id=label)
    validate_layout_context_block(meta.get("layout_context") or {}, section_id=label)
    _reject_fact_ledger_authority(meta, section_id=label)

    # Reject legacy authority switches on receipt fields (after EA block is valid).
    legacy_pt = str(meta.get("proof_pool_type") or "").strip()
    if legacy_pt in FORBIDDEN_EVIDENCE_AUTHORITIES or legacy_pt in FORBIDDEN_PROOF_POOL_TYPE_LABELS:
        raise ProductEvidenceAuthorityError(
            f"{label}: proof_pool_type {legacy_pt!r} is not product authority; "
            f"use evidence_authority={EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH!r}"
        )
    if legacy_pt and legacy_pt not in (
        EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "augmented_skills_graph_c03_graphrag",
    ):
        raise ProductEvidenceAuthorityError(
            f"{label}: unsupported proof_pool_type label {legacy_pt!r}"
        )
    if meta.get("selected_role_fact_set_used") is True:
        raise ProductEvidenceAuthorityError(
            f"{label}: selected_role_fact_set_used must be false on product path"
        )
    if meta.get("broad_skills_ledger_used_as_authority") is True:
        raise ProductEvidenceAuthorityError(f"{label}: broad_skills_ledger must not be authority")
    if meta.get("base_resume_claim_authority") is True:
        raise ProductEvidenceAuthorityError(f"{label}: base_resume_claim_authority forbidden")
    if meta.get("base_resume_fallback_used") is True or meta.get("fallback_used") is True:
        raise ProductEvidenceAuthorityError(f"{label}: base_resume_fallback forbidden on product path")


def scan_prompt_text_for_forbidden_story_authority(text: str) -> list[str]:
    """Return matched forbidden prompt patterns (empty if OK)."""
    body = str(text or "")
    if not body.strip():
        return []
    hits: list[str] = []
    for pat in _FORBIDDEN_PROMPT_STORY_PATTERNS:
        if pat.search(body):
            hits.append(pat.pattern)
    return hits


def validate_compiled_prompt_story_authority(*text_blocks: str, section_id: str = "") -> None:
    label = section_id or "section"
    combined = "\n".join(str(t or "") for t in text_blocks)
    hits = scan_prompt_text_for_forbidden_story_authority(combined)
    if hits:
        raise ProductEvidenceAuthorityError(
            f"{label}: prompt labels story evidence as forbidden authority: {hits[0]}"
        )


def _reject_incoming_forbidden_authority_switches(
    meta: Mapping[str, Any],
    *,
    section_id: str = "",
) -> None:
    """Fail before normalization when legacy authority switches are already set."""
    label = section_id or "section"
    if not isinstance(meta, Mapping):
        return
    _reject_fact_ledger_authority(meta, section_id=label)
    legacy_pt = str(meta.get("proof_pool_type") or "").strip()
    if legacy_pt in FORBIDDEN_EVIDENCE_AUTHORITIES or legacy_pt in FORBIDDEN_PROOF_POOL_TYPE_LABELS:
        raise ProductEvidenceAuthorityError(
            f"{label}: proof_pool_type {legacy_pt!r} is not product authority; "
            f"use evidence_authority={EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH!r}"
        )
    if legacy_pt and legacy_pt not in (
        EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "augmented_skills_graph_c03_graphrag",
    ):
        raise ProductEvidenceAuthorityError(
            f"{label}: unsupported proof_pool_type label {legacy_pt!r}"
        )
    if meta.get("selected_role_fact_set_used") is True:
        raise ProductEvidenceAuthorityError(
            f"{label}: selected_role_fact_set_used must be false on product path"
        )
    if meta.get("broad_skills_ledger_used_as_authority") is True:
        raise ProductEvidenceAuthorityError(f"{label}: broad_skills_ledger must not be authority")
    if meta.get("base_resume_claim_authority") is True:
        raise ProductEvidenceAuthorityError(f"{label}: base_resume_claim_authority forbidden")
    if meta.get("base_resume_fallback_used") is True or meta.get("fallback_used") is True:
        raise ProductEvidenceAuthorityError(f"{label}: base_resume_fallback forbidden on product path")


def _reject_fact_ledger_authority(
    meta: Mapping[str, Any],
    *,
    section_id: str,
    selected_fact_plan: Mapping[str, Any] | None = None,
) -> None:
    reason = fact_ledger_authority_violation_reason(
        proof_pool_metadata=meta,
        selected_fact_plan=selected_fact_plan,
    )
    if reason:
        raise ProductEvidenceAuthorityError(
            f"{section_id}: {BLOCKED_FACT_LEDGER_AUTHORITY}: {reason}"
        )


def finalize_product_section_proof_pool(pool: "SectionProofPool") -> "SectionProofPool":
    """Attach three-concept metadata and validate product law."""
    incoming = dict(pool.proof_pool_metadata or {})
    _reject_incoming_forbidden_authority_switches(incoming, section_id=pool.section)
    _reject_fact_ledger_authority(
        incoming,
        section_id=pool.section,
        selected_fact_plan=pool.selected_fact_plan,
    )
    meta = attach_product_evidence_law_to_metadata(incoming, pool=pool)
    validate_proof_pool_metadata_product_law(
        meta,
        section_id=pool.section,
        proof_source=pool.proof_source,
    )
    return replace(pool, proof_pool_metadata=meta)


def is_product_evidence_authority_active(meta: Mapping[str, Any] | None) -> bool:
    """True when ``evidence_authority`` is present and PASS (X2 pool gates may run)."""
    if not isinstance(meta, Mapping):
        return False
    ea = meta.get("evidence_authority")
    if not isinstance(ea, Mapping):
        return False
    return (
        str(ea.get("authority") or "") == EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
        and str(ea.get("skills_authority_status") or "") == "PASS"
    )


def proof_source_from_product_metadata(metadata: Mapping[str, Any] | None) -> str:
    """Resolve claim proof source from ``evidence_authority`` (not ``proof_pool_type``)."""
    meta = metadata if isinstance(metadata, Mapping) else {}
    ea = meta.get("evidence_authority")
    if isinstance(ea, Mapping):
        authority = str(ea.get("authority") or "").strip()
        if authority in FORBIDDEN_EVIDENCE_AUTHORITIES:
            raise ProductEvidenceAuthorityError(
                f"forbidden evidence_authority {authority!r} in proof_pool_metadata"
            )
        if authority == EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH:
            return _PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
        if authority:
            raise ProductEvidenceAuthorityError(
                f"unsupported evidence_authority {authority!r}; "
                f"expected {EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH!r}"
            )
    pt = str(meta.get("proof_pool_type") or "").strip()
    if pt in FORBIDDEN_EVIDENCE_AUTHORITIES or pt in FORBIDDEN_PROOF_POOL_TYPE_LABELS:
        raise ProductEvidenceAuthorityError(
            f"proof_pool_type {pt!r} is not product authority; attach evidence_authority first"
        )
    raise ProductEvidenceAuthorityError(
        "missing evidence_authority; product lanes require augmented_skills_graph + ledger"
    )


def x2_proof_pool_gate_flags(
    metadata: Mapping[str, Any] | None,
) -> tuple[bool, bool]:
    """Return ``(active_proof_pool_gate, srfs_slice_gate)`` for X2 validators.

    Product path: active pool gate on PASS ``evidence_authority``; SRFS slice gate always off.
    """
    if is_product_evidence_authority_active(metadata):
        return True, False
    return False, False


def product_authority_reporting_fields(
    *,
    section_id: str,
    proof_pool_metadata: Mapping[str, Any],
    allowed_fact_ids_count: int = 0,
    required_fact_ids_count: int = 0,
) -> dict[str, Any]:
    """Flat audit fields for receipts — never marks SRFS/ledger/resume as proof authority."""
    pp = dict(proof_pool_metadata)
    ea = pp.get("evidence_authority") if isinstance(pp.get("evidence_authority"), dict) else {}
    ss = pp.get("selection_scope") if isinstance(pp.get("selection_scope"), dict) else {}
    return {
        "proof_pool_type": PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        "proof_pool_type_role": pp.get("proof_pool_type_role") or "receipt_label_not_authority_switch",
        "evidence_authority": dict(ea),
        "selection_scope": dict(ss),
        "selected_role_fact_set_used": False,
        "broad_skills_ledger_used_as_authority": False,
        "base_resume_claim_authority": False,
        "srfs_section_id": section_id,
        "candidate_fact_pool_count": int(pp.get("candidate_fact_pool_count") or 0),
        "allowed_fact_ids_count": int(allowed_fact_ids_count or pp.get("allowed_fact_ids_count") or 0),
        "required_fact_ids_count": int(required_fact_ids_count),
        "fallback_used": False,
        "fallback_reason": "",
        "x2_srfs_gate_status": "NOT_APPLICABLE",
        "srfs_allowed_fact_ids_count": 0,
        "full_resume_srfs_supported": False,
        "out_of_slice_fact_ids": [],
    }


def product_section_receipt_authority(meta: Mapping[str, Any] | None) -> dict[str, Any]:
    """Receipt-facing authority/scope/layout summary (no forbidden authority labels)."""
    pp = meta if isinstance(meta, Mapping) else {}
    ea = pp.get("evidence_authority") if isinstance(pp.get("evidence_authority"), dict) else {}
    ss = pp.get("selection_scope") if isinstance(pp.get("selection_scope"), dict) else {}
    lc = pp.get("layout_context") if isinstance(pp.get("layout_context"), dict) else {}
    graph_ref = str(ea.get("graph_ref") or "").strip()
    ledger_ref = str(ea.get("ledger_ref") or "").strip()
    receipt: dict[str, Any] = {
        "evidence_authority": {
            "type": EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "graph_ref": "present" if graph_ref else "missing",
            "ledger_ref": "present" if ledger_ref else "missing",
        },
    }
    if ss:
        receipt["selection_scope"] = {
            k: v
            for k, v in ss.items()
            if k != "is_proof_authority"
        }
    if lc:
        receipt["layout_context"] = {
            "base_resume_ref": (
                "present"
                if str(lc.get("base_resume_ref") or lc.get("base_resume_json_ref") or "").strip()
                else None
            ),
            "allowed_fields": list(lc.get("allowed_fields") or lc.get("permitted_uses") or []),
        }
    return receipt


def enforce_product_evidence_authority_for_cli(pool: "SectionProofPool") -> "SectionProofPool":
    """Canonical CLI seam: graph+ledger law before lane L2."""
    if pool.proof_source != _PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH:
        raise ProductEvidenceAuthorityError(
            f"{pool.section}: product CLI requires proof_source="
            f"{_PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH!r}"
        )
    return finalize_product_section_proof_pool(pool)


__all__ = [
    "EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH",
    "FORBIDDEN_EVIDENCE_AUTHORITIES",
    "ProductEvidenceAuthorityError",
    "attach_product_evidence_law_to_metadata",
    "build_evidence_authority",
    "build_layout_context",
    "build_selection_scope",
    "enforce_product_evidence_authority_for_cli",
    "finalize_product_section_proof_pool",
    "is_product_evidence_authority_active",
    "product_authority_reporting_fields",
    "product_section_receipt_authority",
    "proof_source_from_product_metadata",
    "scan_prompt_text_for_forbidden_story_authority",
    "validate_compiled_prompt_story_authority",
    "validate_evidence_authority_block",
    "validate_proof_pool_metadata_product_law",
    "x2_proof_pool_gate_flags",
]
