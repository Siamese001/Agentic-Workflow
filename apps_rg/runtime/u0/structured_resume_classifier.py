"""S4: Structured resume classifier for apps_rg U0 ingress.

Classifies the resume payload carried by a synthesized contract dict as one of:
  - STRUCTURED_SOURCE_RESUME_V2: payload contains a valid structured resume dict
  - LEGACY_FLAT_RESUME: payload contains a flat resume text string only
  - MISSING_OR_INVALID_RESUME: no usable resume content found, or structured
    payload failed validation (and no explicit flat fallback is present)

Also extracts lightweight metadata from the structured resume for downstream
consumers without rewriting any content:
  - source_resume_schema_version
  - source_resume_digest
  - source_resume_mode
  - available_sections
  - role_count
  - has_education
  - has_certifications
  - has_early_career
  - structured_resume_validation_status
  - structured_resume_validation_errors (list, only present on validation failure)

U0 Boundary — this module:
  - DOES classify and validate
  - DOES compute a deterministic digest over the structured payload
  - DOES NOT rewrite resume content
  - DOES NOT call PA
  - DOES NOT call C0
  - DOES NOT call L2 / provider / model
  - DOES NOT call the section treatment resolver
  - DOES NOT mutate cache or write L4
  - DOES NOT route with authority

Plan: .windsurf/plans/01_apps-rg-master-governed-runtime-hardening.md (S4)
Receipt: artifacts/governance/apps_rg_resume_shipping_s4_u0_structured_resume_support.md
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from apps_rg.runtime.schemas.source_resume_schema import (
    is_structured_resume,
    validate_structured_resume,
)

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mode constants
# ---------------------------------------------------------------------------

class ResumeInputMode(str, Enum):
    """Classification of the resume payload carried into U0."""

    STRUCTURED_SOURCE_RESUME_V2 = "STRUCTURED_SOURCE_RESUME_V2"
    LEGACY_FLAT_RESUME = "LEGACY_FLAT_RESUME"
    MISSING_OR_INVALID_RESUME = "MISSING_OR_INVALID_RESUME"


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StructuredResumeClassification:
    """Output of classify_resume_payload().

    Fields
    ------
    source_resume_mode : str
        One of the ResumeInputMode values.
    source_resume_schema_version : str
        Schema version string from the structured payload, or empty string.
    source_resume_digest : str
        SHA-256 hex digest over the canonical JSON of the structured payload,
        or SHA-256 over the flat text bytes, or empty string when missing.
    available_sections : list[str]
        Top-level keys present in a valid structured payload, else [].
    role_count : int
        Number of role entries in ``roles``, or 0.
    has_education : bool
    has_certifications : bool
    has_early_career : bool
    structured_resume_validation_status : str
        "VALID", "INVALID", or "NOT_APPLICABLE".
    structured_resume_validation_errors : list[str]
        Non-empty only when status is "INVALID".
    flat_text_fallback_present : bool
        True when the payload also carries an explicit ``flat_text_fallback``
        field alongside the structured resume.
    """

    source_resume_mode: str
    source_resume_schema_version: str
    source_resume_digest: str
    available_sections: list[str]
    role_count: int
    has_education: bool
    has_certifications: bool
    has_early_career: bool
    structured_resume_validation_status: str
    structured_resume_validation_errors: list[str]
    flat_text_fallback_present: bool = False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_dict(obj: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _extract_structured_metadata(
    data: dict[str, Any],
    validation_errors: list[str],
    *,
    flat_text_fallback_present: bool = False,
) -> StructuredResumeClassification:
    """Build classification from a structured resume that passed is_structured_resume()."""
    schema_version = data.get("schema_name", "")
    digest = _sha256_dict(data)

    roles = data.get("roles", [])
    role_count = len(roles) if isinstance(roles, list) else 0

    available_sections = [k for k in data.keys() if not k.startswith("_")]

    has_education = "education" in data
    has_certifications = "certifications" in data
    has_early_career = "early_career" in data

    if validation_errors:
        return StructuredResumeClassification(
            source_resume_mode=ResumeInputMode.MISSING_OR_INVALID_RESUME.value,
            source_resume_schema_version=schema_version,
            source_resume_digest=digest,
            available_sections=available_sections,
            role_count=role_count,
            has_education=has_education,
            has_certifications=has_certifications,
            has_early_career=has_early_career,
            structured_resume_validation_status="INVALID",
            structured_resume_validation_errors=validation_errors,
            flat_text_fallback_present=flat_text_fallback_present,
        )

    return StructuredResumeClassification(
        source_resume_mode=ResumeInputMode.STRUCTURED_SOURCE_RESUME_V2.value,
        source_resume_schema_version=schema_version,
        source_resume_digest=digest,
        available_sections=available_sections,
        role_count=role_count,
        has_education=has_education,
        has_certifications=has_certifications,
        has_early_career=has_early_career,
        structured_resume_validation_status="VALID",
        structured_resume_validation_errors=[],
        flat_text_fallback_present=flat_text_fallback_present,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_resume_payload(
    resume_payload: dict[str, Any],
) -> StructuredResumeClassification:
    """Classify and inspect the resume payload dict from a synthesized contract.

    The ``resume_payload`` is the ``resume_payload`` sub-dict from the
    synthesized AppsRgIngressContractV1 shape produced by
    ``synthesize_contract_payload()``. It contains:
      - ``source_resume_text``: resolved flat text (may be empty)
      - ``source_resume_ref``: original ref path (may be empty)
      - ``resume_hash``: SHA-256 of the flat text
      - ``structured_resume``: (optional) structured resume dict from S1 schema

    Classification logic:
      1. If ``structured_resume`` key is present and ``is_structured_resume()``
         returns True → validate, then classify as STRUCTURED or INVALID.
      2. If INVALID and no explicit ``flat_text_fallback`` also present → mode
         is MISSING_OR_INVALID_RESUME (do not silently fall back to flat text).
      3. If INVALID and ``flat_text_fallback`` is also present → mode remains
         MISSING_OR_INVALID_RESUME (caller decides; both are preserved).
      4. If no ``structured_resume`` key → check ``source_resume_text``.
         Non-empty → LEGACY_FLAT_RESUME.
         Empty or missing → MISSING_OR_INVALID_RESUME.

    Args:
        resume_payload: The ``resume_payload`` sub-dict from the synthesized
            contract. Never writes to this dict.

    Returns:
        StructuredResumeClassification with all metadata populated.
    """
    structured_data = resume_payload.get("structured_resume")

    if structured_data is not None:
        if not isinstance(structured_data, dict):
            _log.warning(
                "[S4 U0] structured_resume is not a dict (type=%s) — treating as MISSING_OR_INVALID",
                type(structured_data).__name__,
            )
            return StructuredResumeClassification(
                source_resume_mode=ResumeInputMode.MISSING_OR_INVALID_RESUME.value,
                source_resume_schema_version="",
                source_resume_digest="",
                available_sections=[],
                role_count=0,
                has_education=False,
                has_certifications=False,
                has_early_career=False,
                structured_resume_validation_status="INVALID",
                structured_resume_validation_errors=["structured_resume: expected object, got " + type(structured_data).__name__],
                flat_text_fallback_present=bool(resume_payload.get("flat_text_fallback")),  # from parent
            )

        if not is_structured_resume(structured_data):
            _log.warning(
                "[S4 U0] structured_resume is not a SourceResumeV2Structured (schema_name=%r) — MISSING_OR_INVALID",
                structured_data.get("schema_name"),
            )
            return StructuredResumeClassification(
                source_resume_mode=ResumeInputMode.MISSING_OR_INVALID_RESUME.value,
                source_resume_schema_version=str(structured_data.get("schema_version", "")),
                source_resume_digest=_sha256_dict(structured_data),
                available_sections=[],
                role_count=0,
                has_education=False,
                has_certifications=False,
                has_early_career=False,
                structured_resume_validation_status="INVALID",
                structured_resume_validation_errors=[
                    f"schema_name: expected 'source_resume_v2_structured', "
                    f"got {structured_data.get('schema_name')!r}"
                ],
                flat_text_fallback_present=bool(resume_payload.get("flat_text_fallback")),  # from parent
            )

        has_flat_fallback = bool(resume_payload.get("flat_text_fallback"))
        validation_errors = validate_structured_resume(structured_data)
        result = _extract_structured_metadata(
            structured_data, validation_errors,
            flat_text_fallback_present=has_flat_fallback,
        )
        _log.info(
            "[S4 U0] structured_resume classified: mode=%s validation=%s sections=%s roles=%d",
            result.source_resume_mode,
            result.structured_resume_validation_status,
            result.available_sections,
            result.role_count,
        )
        return result

    # No structured_resume key — classify flat text
    flat_text = resume_payload.get("source_resume_text", "")
    if flat_text and isinstance(flat_text, str) and flat_text.strip():
        _log.info("[S4 U0] No structured_resume present — classified as LEGACY_FLAT_RESUME")
        return StructuredResumeClassification(
            source_resume_mode=ResumeInputMode.LEGACY_FLAT_RESUME.value,
            source_resume_schema_version="",
            source_resume_digest=_sha256_text(flat_text),
            available_sections=[],
            role_count=0,
            has_education=False,
            has_certifications=False,
            has_early_career=False,
            structured_resume_validation_status="NOT_APPLICABLE",
            structured_resume_validation_errors=[],
            flat_text_fallback_present=False,
        )

    _log.warning("[S4 U0] No usable resume content found — MISSING_OR_INVALID_RESUME")
    return StructuredResumeClassification(
        source_resume_mode=ResumeInputMode.MISSING_OR_INVALID_RESUME.value,
        source_resume_schema_version="",
        source_resume_digest="",
        available_sections=[],
        role_count=0,
        has_education=False,
        has_certifications=False,
        has_early_career=False,
        structured_resume_validation_status="NOT_APPLICABLE",
        structured_resume_validation_errors=[],
        flat_text_fallback_present=False,
    )


def attach_structured_resume_metadata(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Attach structured resume metadata to a synthesized contract dict in-place.

    Reads ``contract["resume_payload"]`` and calls ``classify_resume_payload()``.
    All metadata is written into ``contract["resume_payload"]["s4_metadata"]``
    so the existing contract shape and digest are not disturbed.

    Returns the same contract dict (mutated in-place for efficiency).

    Args:
        contract: The contract dict from ``synthesize_contract_payload()``.

    Returns:
        The same dict with ``resume_payload.s4_metadata`` populated.
    """
    resume_payload = contract.get("resume_payload", {})
    classification = classify_resume_payload(resume_payload)

    s4_meta: dict[str, Any] = {
        "source_resume_schema_version": classification.source_resume_schema_version,
        "source_resume_digest": classification.source_resume_digest,
        "source_resume_mode": classification.source_resume_mode,
        "available_sections": classification.available_sections,
        "role_count": classification.role_count,
        "has_education": classification.has_education,
        "has_certifications": classification.has_certifications,
        "has_early_career": classification.has_early_career,
        "structured_resume_validation_status": classification.structured_resume_validation_status,
        "flat_text_fallback_present": classification.flat_text_fallback_present,
    }
    if classification.structured_resume_validation_errors:
        s4_meta["structured_resume_validation_errors"] = classification.structured_resume_validation_errors

    contract["resume_payload"]["s4_metadata"] = s4_meta
    return contract


# S4 certification reference — proof this module was created and wired for S4.
U0_STRUCTURED_RESUME_CERT_S4: str = "u0-apps-rg-structured-resume-support-s4"


__all__ = [
    "ResumeInputMode",
    "StructuredResumeClassification",
    "U0_STRUCTURED_RESUME_CERT_S4",
    "attach_structured_resume_metadata",
    "classify_resume_payload",
]
