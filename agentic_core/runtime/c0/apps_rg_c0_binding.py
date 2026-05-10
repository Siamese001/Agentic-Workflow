"""C0 grounding-retrieval binding for apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P4 (initial)
+   plan apps-rg-app-payload-consumption-wiring-b3a449 W4 (AG-2 — signature
   change to accept ValidatedRequest; reads jd/resume content from
   ValidatedRequest.app_payload, NOT from legacy AppsRgIngressPayload).

C0 is the FOURTH stage (CONDITIONAL — fires only when route.grounding_required=True).
Its job is to gather the evidence needed for prompt assembly:
- The JD (job description) — read from app_payload["jd_payload"]["jd_text"]
  (preferred) or the legacy ref-path fallback for back-compat with file-based
  callers. AG-2 invariant: never reads from envelope.payload.
- The source resume — read from app_payload["resume_payload"]
- The manual brief — referenced by path through L1.policy_refs (future)

Per AG-RGGOV-5, ONLY core C0 may emit FinalEvidenceContract — apps_rg.cert
is quarantined for FEC emission. This binding lives in agentic_core/ ✅.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    ValidatedRequest,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_RG_C0_CERT_REF: str = "c0-apps-rg-resume-generation-app-payload-b3a449"

_DOCX_EXTENSIONS: frozenset[str] = frozenset({".docx"})
_PDF_EXTENSIONS: frozenset[str] = frozenset({".pdf"})
_JSON_EXTENSIONS: frozenset[str] = frozenset({".json"})


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _read_json_evidence(
    relpath: str | None,
    source_label: str,
    timestamp_iso: str,
    repo_root: Path,
) -> EvidenceItem | None:
    """Read a JSON file as text evidence; return None if missing."""
    if not relpath:
        return None
    abs_path = (repo_root / relpath).resolve() if not Path(relpath).is_absolute() else Path(relpath)
    if not abs_path.exists() or not abs_path.is_file():
        return None
    try:
        content_bytes = abs_path.read_bytes()
        # Validate it's actually JSON
        json.loads(content_bytes.decode("utf-8"))
        content_text = content_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return EvidenceItem(
        source=f"{source_label}:{relpath}",
        content=content_text,
        content_type="json",
        retrieval_timestamp=timestamp_iso,
        confidence_score=1.0,  # direct file read, fully trusted
    )


def _extract_docx_text(path: Path) -> str | None:
    """Extract plain text from a .docx file using python-docx."""
    try:
        import docx  # python-docx
        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs) if paragraphs else None
    except (ImportError, Exception):
        return None


def _extract_pdf_text(path: Path) -> str | None:
    """Extract plain text from a .pdf file using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(p for p in pages if p.strip())
        return text if text.strip() else None
    except (ImportError, Exception):
        return None


def _read_file_evidence(
    relpath: str | None,
    source_label: str,
    timestamp_iso: str,
    repo_root: Path,
) -> EvidenceItem | None:
    """Read a file as text evidence, handling JSON, DOCX, PDF, and plain text."""
    if not relpath:
        return None
    abs_path = (
        (repo_root / relpath).resolve()
        if not Path(relpath).is_absolute()
        else Path(relpath)
    )
    if not abs_path.exists() or not abs_path.is_file():
        return None

    suffix = abs_path.suffix.lower()
    content: str | None = None
    content_type = "text"

    if suffix in _JSON_EXTENSIONS:
        try:
            raw = abs_path.read_bytes().decode("utf-8")
            json.loads(raw)  # validate
            content = raw
            content_type = "json"
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            content = None
    elif suffix in _DOCX_EXTENSIONS:
        content = _extract_docx_text(abs_path)
        content_type = "docx_text"
    elif suffix in _PDF_EXTENSIONS:
        content = _extract_pdf_text(abs_path)
        content_type = "pdf_text"
    else:
        try:
            content = abs_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            content = None

    if not content or not content.strip():
        return None

    return EvidenceItem(
        source=f"{source_label}:{relpath}",
        content=content,
        content_type=content_type,
        retrieval_timestamp=timestamp_iso,
        confidence_score=1.0,
    )


def _record_path_only_evidence(
    path_str: str | None,
    source_label: str,
    timestamp_iso: str,
) -> EvidenceItem | None:
    """Record a path-only evidence reference (e.g. PDF that we don't parse this turn)."""
    if not path_str:
        return None
    return EvidenceItem(
        source=f"{source_label}:{path_str}",
        content=f"[path-only reference; W5 will parse]",
        content_type="path_reference",
        retrieval_timestamp=timestamp_iso,
        confidence_score=0.5,  # presence-only; content unverified
    )


def c0_retrieve_apps_rg(
    route: RouteContract,
    validated_request: ValidatedRequest,
) -> FinalEvidenceContract:
    """Gather grounding evidence for an apps_rg request.

    AG-2 (apps-rg-app-payload-consumption-wiring-b3a449 W4): signature
    changed from ``(route, payload: AppsRgIngressPayload)`` to
    ``(route, validated_request: ValidatedRequest)``. This binding now
    reads JD/resume content exclusively from
    ``validated_request.app_payload`` — never from the legacy ingress
    payload. The hard invariant is enforced by the CI gate
    ``ops_scripts/ci/check_apps_rg_app_payload_consumption.py``.

    Args:
        route: L0 routing decision (must have grounding_required=True for
               this binding to be invoked).
        validated_request: U0 output carrying app_payload — the SSOT for
                           every apps_rg ingress field beyond U0.

    Returns:
        FinalEvidenceContract with evidence_items + retrieval_sources +
        sufficiency assessment.

    Raises:
        TypeError: if route or validated_request have wrong shape.
        ValueError: if app_payload is missing the required jd_payload /
            resume_payload sections (fail-closed before evidence assembly).
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"c0_retrieve_apps_rg expected RouteContract, got {type(route).__name__}"
        )
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            "c0_retrieve_apps_rg expected ValidatedRequest, got "
            f"{type(validated_request).__name__}"
        )

    app_payload = validated_request.app_payload
    if "jd_payload" not in app_payload or "resume_payload" not in app_payload:
        raise ValueError(
            "c0_retrieve_apps_rg: app_payload missing jd_payload/resume_payload "
            "sections. The U0 reflection harness should have populated these — "
            "was apps_rg_u0_adapt skipped?"
        )

    jd_section = app_payload["jd_payload"]
    resume_section = app_payload["resume_payload"]

    timestamp_iso = datetime.now(timezone.utc).isoformat()
    repo_root = _resolve_repo_root()

    items: list[EvidenceItem] = []
    sources: list[str] = []

    # JD — read from app_payload (preferred) with optional file fallback when
    # only a ref-path was supplied (e.g. file-based callers pre-AG-1.d).
    jd_text = str(jd_section.get("jd_text", "") or "")
    jd_ref = str(jd_section.get("jd_ref", "") or "")
    # AG-4 invariant: apps_rg uses inline app_payload — no dense / sparse /
    # ChromaDB / graph retrieval surface applies.  Mark every retrieval-shaped
    # status field NOT_APPLICABLE with an explicit reason; carry source_id +
    # source_uri_or_ref + chunk_digest + retrieved_span verbatim from payload.
    _NA_REASON = (
        "apps_rg uses verbatim inline app_payload (jd + resume); no dense "
        "retrieval, no sparse retrieval, no ChromaDB collection, no ACL, no "
        "freshness, no graph expansion, and no contradiction surface applies."
    )
    if jd_text and jd_text != "<empty>":
        jd_chunk_digest = hashlib.sha256(jd_text.encode("utf-8")).hexdigest()
        items.append(EvidenceItem(
            source="jd:app_payload.jd_text",
            content=jd_text,
            content_type="text",
            retrieval_timestamp=timestamp_iso,
            confidence_score=1.0,
            # AG-4 W3: identity + provenance
            evidence_id=f"{route.run_id}:jd:app_payload",
            source_id="apps_rg.app_payload.jd_payload.jd_text",
            source_type="app_payload_inline",
            source_version=str(jd_section.get("jd_version", "") or "inline"),
            source_uri_or_ref=jd_ref or "app_payload://jd_text",
            source_owner_or_authority="user_supplied",
            retrieved_span="full",
            citation_anchor=f"jd:app_payload.jd_text:{jd_chunk_digest[:12]}",
            chunk_digest=jd_chunk_digest,
            # AG-4 W3: retrieval scores — N/A for inline path
            retrieval_method="inline",
            retrieval_run_ref=route.run_id,
            # AG-4 W3: trust + safety — explicit NOT_APPLICABLE with reason
            freshness_status="NOT_APPLICABLE",
            acl_status="NOT_APPLICABLE",
            origin_trust_label="USER",
            authority_class="PRIMARY",
            contradiction_status="NOT_APPLICABLE",
            stratum="USER_INTENT",
            # AG-4 W3: support outcome — JD is fully present, mark PASS
            support_score=1.0,
            support_status="PASS",
            evidence_digest=jd_chunk_digest,
            not_applicable_reason=_NA_REASON,
        ))
        sources.append("jd:app_payload.jd_text")
    elif jd_ref:
        jd_item = _read_json_evidence(jd_ref, "jd", timestamp_iso, repo_root)
        if jd_item:
            items.append(jd_item)
            sources.append(jd_item.source)

    # Source resume — DOCX, PDF, JSON, or plain text
    resume_text = str(resume_section.get("source_resume_text", "") or "")
    resume_ref = str(resume_section.get("source_resume_ref", "") or "")
    if resume_text:
        resume_chunk_digest = hashlib.sha256(resume_text.encode("utf-8")).hexdigest()
        items.append(EvidenceItem(
            source="resume:app_payload.source_resume_text",
            content=resume_text,
            content_type="text",
            retrieval_timestamp=timestamp_iso,
            confidence_score=1.0,
            # AG-4 W3: identity + provenance
            evidence_id=f"{route.run_id}:resume:app_payload",
            source_id="apps_rg.app_payload.resume_payload.source_resume_text",
            source_type="app_payload_inline",
            source_version=str(resume_section.get("source_resume_version", "") or "inline"),
            source_uri_or_ref=resume_ref or "app_payload://source_resume_text",
            source_owner_or_authority="user_supplied",
            retrieved_span="full",
            citation_anchor=f"resume:app_payload.source_resume_text:{resume_chunk_digest[:12]}",
            chunk_digest=resume_chunk_digest,
            retrieval_method="inline",
            retrieval_run_ref=route.run_id,
            freshness_status="NOT_APPLICABLE",
            acl_status="NOT_APPLICABLE",
            origin_trust_label="USER",
            authority_class="PRIMARY",
            contradiction_status="NOT_APPLICABLE",
            stratum="USER_INTENT",
            support_score=1.0,
            support_status="PASS",
            evidence_digest=resume_chunk_digest,
            not_applicable_reason=_NA_REASON,
        ))
        sources.append("resume:app_payload.source_resume_text")
    elif resume_ref:
        resume_item = _read_file_evidence(
            resume_ref, "resume", timestamp_iso, repo_root,
        )
        if resume_item:
            items.append(resume_item)
            sources.append(resume_item.source)

    # Sufficiency: target met if both JD and resume are present (text or JSON).
    has_jd = any(it.source.startswith("jd:") and it.content_type != "path_reference" for it in items)
    has_resume = any(
        it.source.startswith("resume:") and it.content_type != "path_reference"
        for it in items
    )
    has_brief = any(it.source.startswith("brief:") for it in items)

    target_met = has_jd and has_resume
    target_partial = has_jd or has_resume
    score = 0.0
    if has_jd:
        score += 0.45
    if has_resume:
        score += 0.45
    if has_brief:
        score += 0.10

    # compilation_hash binds the evidence content for downstream PA reference.
    canonical = json.dumps(
        [{"src": it.source, "type": it.content_type, "len": len(it.content)} for it in items],
        sort_keys=True,
    )
    compilation_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # AG-4 W2: build contract-level lineage refs.  apps_rg uses inline
    # app_payload, so dense/sparse/metadata/graph receipts are absent
    # and excluded_evidence_refs / blocked_source_refs are empty.
    citation_map = tuple(
        (it.evidence_id or it.source, it.citation_anchor)
        for it in items if it.citation_anchor
    )
    source_lineage_map = tuple(
        (it.evidence_id or it.source, it.source_id or it.source)
        for it in items
    )
    source_version_map = tuple(
        (it.source_id or it.source, it.source_version or "inline")
        for it in items if it.source_id
    )
    evidence_strata = (("USER_INTENT", tuple(it.evidence_id or it.source for it in items)),) if items else ()

    # AG-4 support_status: only PASS when both jd + resume present.
    # WEAK if only one is present.  EMPTY if none.
    if target_met:
        support_status_v2 = "PASS"
    elif target_partial:
        support_status_v2 = "WEAK"
    else:
        support_status_v2 = "EMPTY"

    final_evidence_digest = hashlib.sha256(
        (compilation_hash + "|" + "|".join(it.evidence_digest or "" for it in items)).encode("utf-8")
    ).hexdigest()

    return FinalEvidenceContract(
        request_id=route.request_id,
        run_id=route.run_id,
        app_id=route.app_id,
        trace_id=route.trace_id,
        # W1 P1.2: thread identity quad from RouteContract (D6)
        tenant_id=route.tenant_id,
        evidence_items=tuple(items),
        retrieval_sources=tuple(sources),
        support_target_met=target_met,
        support_target_partial=target_partial,
        evidence_sufficiency_score=round(score, 3),
        evidence_collection_timestamp=timestamp_iso,
        schema_version="W3.P4",
        compilation_hash=compilation_hash,
        l5_certification_ref=APPS_RG_C0_CERT_REF,
        # AG-4 W2: lineage refs
        route_contract_ref=route.compilation_hash if hasattr(route, "compilation_hash") else "",
        retrieval_plan_ref="apps_rg:inline_app_payload_only",
        # AG-4 W2: receipts — empty (no dense/sparse/graph for apps_rg)
        dense_search_refs=(),
        sparse_search_refs=(),
        metadata_filter_refs=(),
        graph_expansion_refs=(),
        # AG-4 W2: maps materialised from evidence_items
        evidence_strata=evidence_strata,
        citation_map=citation_map,
        source_lineage_map=source_lineage_map,
        source_version_map=source_version_map,
        # AG-4 W2: ACL/freshness — N/A for inline path; empty receipt tuples
        acl_verification_receipts=(),
        freshness_receipts=(),
        contradiction_report="",
        # AG-4 W2: aggregate support
        support_status=support_status_v2,
        support_score_profile=(
            ("jd_present", 1.0 if has_jd else 0.0),
            ("resume_present", 1.0 if has_resume else 0.0),
            ("brief_present", 1.0 if has_brief else 0.0),
        ),
        # AG-4 W2: exclusions / blocks — none for inline path
        excluded_evidence_refs=(),
        blocked_source_refs=(),
        weak_support_refinement_attempts=(),
        # AG-4 W2: aggregate digest
        final_evidence_digest=final_evidence_digest,
        # AG-4 W2: explicit reason if support_status is non-PASS
        unknown_reason="",
        not_applicable_reason="",
    )


__all__ = [
    "APPS_RG_C0_CERT_REF",
    "c0_retrieve_apps_rg",
]
