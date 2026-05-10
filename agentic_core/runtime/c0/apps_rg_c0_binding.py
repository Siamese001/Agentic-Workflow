"""C0 grounding-retrieval binding for apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P4.

C0 is the FOURTH stage (CONDITIONAL — fires only when route.grounding_required=True).
Its job is to gather the evidence needed for prompt assembly:
- The JD (job description) — structured JSON loaded from payload.job_description_ref
- The source resume — JSON loaded from payload.source_resume_ref
- The manual brief — referenced by path; PDF parsing deferred to W5

Per AG-RGGOV-5, ONLY core C0 may emit FinalEvidenceContract — apps_rg.cert
is quarantined for FEC emission. This binding lives in agentic_core/ ✅.

W3.P4 SCOPE: shape-valid FEC with real retrieval of JSON sources +
path-only references for non-JSON sources. Real PDF parsing, semantic
chunking, and similarity search land in W5 (real LLM E2E).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_RG_C0_CERT_REF: str = "c0-apps-rg-resume-generation-w3p4"

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
    payload: AppsRgIngressPayload,
) -> FinalEvidenceContract:
    """Gather grounding evidence for an apps_rg request.

    Args:
        route: L0 routing decision (must have grounding_required=True for
               this binding to be invoked).
        payload: Original ingress payload — provides JD/resume/brief refs.

    Returns:
        FinalEvidenceContract with evidence_items + retrieval_sources +
        sufficiency assessment.

    Raises:
        TypeError: if route or payload have wrong shape.
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"c0_retrieve_apps_rg expected RouteContract, got {type(route).__name__}"
        )
    if not isinstance(payload, AppsRgIngressPayload):
        raise TypeError(
            f"c0_retrieve_apps_rg expected AppsRgIngressPayload, got {type(payload).__name__}"
        )

    timestamp_iso = datetime.now(timezone.utc).isoformat()
    repo_root = _resolve_repo_root()

    items: list[EvidenceItem] = []
    sources: list[str] = []

    # JD — JSON expected
    if payload.job_description_text:
        items.append(EvidenceItem(
            source="jd:inline_text",
            content=payload.job_description_text,
            content_type="text",
            retrieval_timestamp=timestamp_iso,
            confidence_score=1.0,
        ))
        sources.append("jd:inline_text")
    else:
        jd_item = _read_json_evidence(
            payload.job_description_ref, "jd", timestamp_iso, repo_root,
        )
        if jd_item:
            items.append(jd_item)
            sources.append(jd_item.source)

    # Source resume — DOCX, PDF, JSON, or plain text
    if payload.source_resume_text:
        items.append(EvidenceItem(
            source="resume:inline_text",
            content=payload.source_resume_text,
            content_type="text",
            retrieval_timestamp=timestamp_iso,
            confidence_score=1.0,
        ))
        sources.append("resume:inline_text")
    else:
        resume_item = _read_file_evidence(
            payload.source_resume_ref, "resume", timestamp_iso, repo_root,
        )
        if resume_item:
            items.append(resume_item)
            sources.append(resume_item.source)

    # Manual brief — path-only reference (W5 will parse PDF/MD)
    brief_item = _record_path_only_evidence(
        payload.manual_brief_path, "brief", timestamp_iso,
    )
    if brief_item:
        items.append(brief_item)
        sources.append(brief_item.source)

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
    )


__all__ = [
    "APPS_RG_C0_CERT_REF",
    "c0_retrieve_apps_rg",
]
