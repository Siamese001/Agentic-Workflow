"""Graph-only story authority for generated employment lanes (no base-resume bullet paste)."""
from __future__ import annotations

import re
from typing import Any, Callable

from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    SectionProofPool,
)
from apps_rg.runtime.sections.section_spec import CANONICAL_SECTION_IDS

GRAPH_REQUIRED_SECTIONS = frozenset(CANONICAL_SECTION_IDS)

STORY_BULLET_SECTIONS = frozenset({"unify_bullets", "ibm_bullets"})

_EMPLOYMENT_FACT_ID_BY_SECTION = {
    "unify_bullets": "exp_unify_001",
    "ibm_bullets": "exp_ibm_001",
}

_FORBIDDEN_HYDRATE_OPERATIONS = frozenset(
    {
        "hydrate_unify_bullets_from_canonical_resume",
        "hydrate_ibm_bullets_from_canonical_resume",
    }
)

_TAXONOMY_PREFIX = re.compile(r"^[A-Z][A-Za-z /,&-]{3,60}:\s+")


def require_augmented_skills_graph_pool(pool: SectionProofPool, *, section_id: str = "") -> None:
    """Fail closed before L2 when graph skills authority is not active."""
    from apps_rg.runtime.product_evidence_authority import (
        ProductEvidenceAuthorityError,
        validate_proof_pool_metadata_product_law,
    )

    label = section_id or pool.section
    if label and label not in GRAPH_REQUIRED_SECTIONS:
        return
    if pool.proof_source != PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH:
        raise ValueError(
            f"{label}: product proof must be augmented_skills_graph; got {pool.proof_source!r}"
        )
    meta = pool.proof_pool_metadata if isinstance(pool.proof_pool_metadata, dict) else {}
    try:
        validate_proof_pool_metadata_product_law(
            meta,
            section_id=label,
            proof_source=pool.proof_source,
        )
    except ProductEvidenceAuthorityError as exc:
        raise ValueError(str(exc)) from exc


def _normalize_bullet_text(text: str) -> str:
    t = (text or "").strip()
    if _TAXONOMY_PREFIX.match(t) and ": " in t:
        t = t.split(": ", 1)[1].strip()
    return " ".join(t.split()).casefold()


def base_resume_employment_bullet_fingerprints(
    base_resume: dict[str, Any],
    *,
    employment_fact_id: str,
) -> frozenset[str]:
    """Normalized base-resume bullet bodies for one employment block (comparison only)."""
    facts_obj = base_resume.get("facts", base_resume)
    if not isinstance(facts_obj, dict):
        return frozenset()
    for emp in facts_obj.get("employment") or []:
        if not isinstance(emp, dict):
            continue
        if str(emp.get("fact_id") or "") != employment_fact_id:
            continue
        out: set[str] = set()
        for row in emp.get("bullets") or []:
            if not isinstance(row, dict):
                continue
            raw = str(row.get("text") or row.get("bullet_text") or "").strip()
            if raw:
                out.add(_normalize_bullet_text(raw))
        return frozenset(out)
    return frozenset()


def change_log_has_base_resume_hydration(parsed: dict[str, Any] | None) -> bool:
    if not isinstance(parsed, dict):
        return False
    for entry in parsed.get("change_log") or []:
        if isinstance(entry, dict) and str(entry.get("operation") or "") in _FORBIDDEN_HYDRATE_OPERATIONS:
            return True
    return False


def verbatim_base_resume_bullet_ids(
    parsed: dict[str, Any] | None,
    *,
    base_resume: dict[str, Any],
    section_id: str,
) -> list[str]:
    emp_id = _EMPLOYMENT_FACT_ID_BY_SECTION.get(section_id)
    if not emp_id or not isinstance(parsed, dict):
        return []
    fingerprints = base_resume_employment_bullet_fingerprints(base_resume, employment_fact_id=emp_id)
    if not fingerprints:
        return []
    hits: list[str] = []
    for row in parsed.get("bullets") or []:
        if not isinstance(row, dict):
            continue
        body = _normalize_bullet_text(str(row.get("bullet_text") or ""))
        if body and body in fingerprints:
            hits.append(str(row.get("bullet_id") or ""))
    return hits


def forbid_base_resume_bullet_hydration(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    parsed: dict[str, Any],
    base_resume: dict[str, Any],
    would_hydrate_fn: Callable[..., bool],
) -> None:
    """Raise when legacy canonical hydration would run or output copies base resume bullets."""
    if section_id not in STORY_BULLET_SECTIONS:
        return
    if would_hydrate_fn(runtime_payload, parsed):
        raise ValueError(
            f"{section_id}: graph/ledger proof pool did not satisfy structural gates; "
            "base-resume bullet hydration is forbidden — expand graph allocation or fix generation"
        )
    if change_log_has_base_resume_hydration(parsed):
        raise ValueError(
            f"{section_id}: change_log records base-resume hydration; product path is graph-only"
        )
    verbatim = verbatim_base_resume_bullet_ids(
        parsed, base_resume=base_resume, section_id=section_id
    )
    if verbatim:
        raise ValueError(
            f"{section_id}: bullet_text verbatim-matches base resume for {verbatim}; "
            "must be rewritten from ledger/graph claim_text only"
        )


def x2_gate_graph_only_proof_pool(
    proof_pool_metadata: dict[str, Any] | None,
    *,
    section_id: str = "",
) -> tuple[bool, str, Any, Any]:
    """X2 helper: product lanes must use augmented_skills_graph evidence authority."""
    from apps_rg.runtime.product_evidence_authority import (
        EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        FORBIDDEN_EVIDENCE_AUTHORITIES,
        validate_evidence_authority_block,
    )

    meta = proof_pool_metadata if isinstance(proof_pool_metadata, dict) else {}
    label = section_id or "section"
    ea_raw = meta.get("evidence_authority") if isinstance(meta.get("evidence_authority"), dict) else {}
    ea = dict(ea_raw)
    authority = str(ea.get("authority") or "").strip()
    if not authority:
        return (
            False,
            "missing",
            EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            f"{label}: missing evidence_authority",
        )
    if not ea.get("graph_ref"):
        ea["graph_ref"] = str(meta.get("graph_ref") or meta.get("augmented_skills_graph_ref") or "")
    if not ea.get("ledger_ref"):
        ea["ledger_ref"] = str(
            meta.get("claim_evidence_substrate_ref") or meta.get("candidate_fact_ledger_ref") or ""
        )
    if not ea.get("skills_authority_status"):
        ea["skills_authority_status"] = str(meta.get("skills_authority_status") or "")
    if not ea.get("authority"):
        ea["authority"] = authority
    if authority in FORBIDDEN_EVIDENCE_AUTHORITIES:
        return (
            False,
            authority,
            EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            f"{label}: forbidden evidence_authority",
        )
    if authority not in (EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH, "augmented_skills_graph_c03_graphrag"):
        return (
            False,
            authority or "missing",
            EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            f"{label}: missing or unknown evidence_authority",
        )
    try:
        validate_evidence_authority_block(ea, section_id=label)
    except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: authority validation returns structured fail
        return False, authority, EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH, str(exc)
    return True, authority, EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH, "ok"


def x2_gate_base_resume_story_forbidden(
    *,
    section_id: str,
    parsed_output: dict[str, Any] | None,
    base_resume: dict[str, Any] | None,
    runtime_payload: dict[str, Any] | None,
) -> tuple[bool, str, Any, Any]:
    """X2 helper: (pass, observed, expected, detail)."""
    if section_id not in STORY_BULLET_SECTIONS:
        return True, "n/a", "n/a", "not a story bullet lane"
    if not isinstance(parsed_output, dict):
        return False, "no parsed output", "parsed dict", "missing parsed_output"
    if change_log_has_base_resume_hydration(parsed_output):
        return False, "hydration in change_log", "absent", _FORBIDDEN_HYDRATE_OPERATIONS
    pp = (runtime_payload or {}).get("proof_pool_metadata") or {}
    if str(pp.get("proof_pool_type") or "") not in (
        "augmented_skills_graph",
        "augmented_skills_graph_c03_graphrag",
        "",
    ):
        return False, pp.get("proof_pool_type"), "augmented_skills_graph", "wrong proof_pool_type"
    if isinstance(base_resume, dict):
        verbatim = verbatim_base_resume_bullet_ids(
            parsed_output, base_resume=base_resume, section_id=section_id
        )
        if verbatim:
            return False, verbatim, [], "verbatim base resume bullet_text"
    return True, "graph_story_only", "no base hydration", "ok"


__all__ = [
    "GRAPH_REQUIRED_SECTIONS",
    "STORY_BULLET_SECTIONS",
    "base_resume_employment_bullet_fingerprints",
    "change_log_has_base_resume_hydration",
    "forbid_base_resume_bullet_hydration",
    "require_augmented_skills_graph_pool",
    "verbatim_base_resume_bullet_ids",
    "x2_gate_base_resume_story_forbidden",
    "x2_gate_graph_only_proof_pool",
]
