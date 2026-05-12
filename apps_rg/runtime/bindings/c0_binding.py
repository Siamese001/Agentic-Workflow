"""C0 grounding-retrieval binding for apps_rg `resume_generation` task class.

MIGRATED from agentic_core/runtime/c0/apps_rg_c0_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2C.

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
is quarantined for FEC emission.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

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
    """Best-effort repo-root resolution."""
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


def _hash_content(content: str) -> str:
    """Compute SHA-256 hash of content for evidence integrity."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


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
            f"c0_retrieve_apps_rg expected ValidatedRequest, got {type(validated_request).__name__}"
        )

    # Fail-closed: route must have grounding_required=True for C0 to fire
    if not getattr(route, "grounding_required", False):
        raise ValueError(
            "c0_retrieve_apps_rg invoked with grounding_required=False; "
            "C0 is conditional on route.grounding_required=True per AG-2"
        )

    # AG-2 invariant: read exclusively from validated_request.app_payload
    app_payload = validated_request.app_payload or {}

    # Fail-closed validation of required app_payload sections
    if "jd_payload" not in app_payload:
        raise ValueError(
            "c0_retrieve_apps_rg: app_payload missing required jd_payload section"
        )
    if "resume_payload" not in app_payload:
        raise ValueError(
            "c0_retrieve_apps_rg: app_payload missing required resume_payload section"
        )

    jd_payload = app_payload.get("jd_payload", {})
    resume_payload = app_payload.get("resume_payload", {})

    # Primary JD source: jd_text from app_payload (AG-2 preferred)
    jd_text = jd_payload.get("jd_text", "")
    jd_path = jd_payload.get("jd_path")

    # Primary resume source: resume_text or structured resume from app_payload
    resume_text = resume_payload.get("resume_text", "")
    resume_path = resume_payload.get("resume_path")
    resume_json = resume_payload.get("resume_json")

    # Build evidence items list
    evidence_items: list[EvidenceItem] = []
    retrieval_sources: list[str] = []
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    repo_root = _resolve_repo_root()

    # JD evidence (primary: inline text from app_payload)
    if jd_text and jd_text.strip():
        evidence_items.append(
            EvidenceItem(
                source="jd_payload:jd_text",
                content=jd_text,
                content_type="job_description_text",
                retrieval_timestamp=timestamp_iso,
                confidence_score=1.0,
            )
        )
        retrieval_sources.append("jd_payload:jd_text")
    elif jd_path:
        # Fallback: read from file path if provided
        jd_evidence = _read_file_evidence(
            jd_path, "jd_file", timestamp_iso, repo_root
        )
        if jd_evidence:
            evidence_items.append(jd_evidence)
            retrieval_sources.append(f"jd_file:{jd_path}")

    # Resume evidence (primary: inline from app_payload)
    if resume_text and resume_text.strip():
        evidence_items.append(
            EvidenceItem(
                source="resume_payload:resume_text",
                content=resume_text,
                content_type="resume_text",
                retrieval_timestamp=timestamp_iso,
                confidence_score=1.0,
            )
        )
        retrieval_sources.append("resume_payload:resume_text")
    elif resume_json:
        # Structured resume JSON from app_payload
        try:
            resume_json_str = (
                json.dumps(resume_json)
                if isinstance(resume_json, dict)
                else str(resume_json)
            )
            evidence_items.append(
                EvidenceItem(
                    source="resume_payload:resume_json",
                    content=resume_json_str,
                    content_type="json",
                    retrieval_timestamp=timestamp_iso,
                    confidence_score=1.0,
                )
            )
            retrieval_sources.append("resume_payload:resume_json")
        except (TypeError, ValueError):
            pass
    elif resume_path:
        # Fallback: read from file path
        resume_evidence = _read_file_evidence(
            resume_path, "resume_file", timestamp_iso, repo_root
        )
        if resume_evidence:
            evidence_items.append(resume_evidence)
            retrieval_sources.append(f"resume_file:{resume_path}")

    # Manual brief evidence (future: referenced through L1.policy_refs)
    policy_refs = app_payload.get("policy_refs", {})
    manual_brief_path = policy_refs.get("manual_brief_path")
    if manual_brief_path:
        brief_evidence = _read_file_evidence(
            manual_brief_path, "manual_brief", timestamp_iso, repo_root
        )
        if brief_evidence:
            evidence_items.append(brief_evidence)
            retrieval_sources.append(f"manual_brief:{manual_brief_path}")

    # Compute evidence digest for provenance chain
    evidence_content = "|".join(
        f"{item.source}:{item.content[:100]}" for item in evidence_items
    )
    evidence_digest = _hash_content(evidence_content)

    # Sufficiency assessment
    has_jd = any(
        item.source.startswith("jd_payload") or item.source.startswith("jd_file")
        for item in evidence_items
    )
    has_resume = any(
        item.source.startswith("resume_payload") or item.source.startswith("resume_file")
        for item in evidence_items
    )
    is_sufficient = has_jd and has_resume

    return FinalEvidenceContract(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        evidence_items=evidence_items,
        retrieval_sources=retrieval_sources,
        is_sufficient=is_sufficient,
        sufficiency_rationale=(
            "JD + resume present" if is_sufficient
            else f"missing: {'JD' if not has_jd else ''} {'resume' if not has_resume else ''}".strip()
        ),
        evidence_digest=evidence_digest,
        retrieval_timestamp=timestamp_iso,
        c0_certification_ref=APPS_RG_C0_CERT_REF,
        schema_version="AG-2.b3a449",
    )


__all__ = [
    "APPS_RG_C0_CERT_REF",
    "c0_retrieve_apps_rg",
]
