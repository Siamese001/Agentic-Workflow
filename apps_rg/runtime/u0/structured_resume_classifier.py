"""U0-only structured source resume classifier for apps_rg.

This module is intentionally small and dependency-light. It classifies ingress
payload shape and attaches metadata; it does not rewrite resume content, call
providers, or touch retrieval/generation/runtime state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
from typing import Any

U0_STRUCTURED_RESUME_CERT_S4 = "u0-apps-rg-structured-resume-support-s4"

_STRUCTURED_SCHEMA_NAME = "source_resume_v2_structured"
_STRUCTURED_SCHEMA_VERSION = "2.0.0"
_REQUIRED_STRUCTURED_FIELDS = (
    "headline",
    "executive_summary",
    "roles",
    "competencies",
)
_OPTIONAL_SECTION_FIELDS = ("education", "certifications", "early_career")


class ResumeInputMode(str, Enum):
    STRUCTURED_SOURCE_RESUME_V2 = "STRUCTURED_SOURCE_RESUME_V2"
    LEGACY_FLAT_RESUME = "LEGACY_FLAT_RESUME"
    MISSING_OR_INVALID_RESUME = "MISSING_OR_INVALID_RESUME"


@dataclass(frozen=True)
class StructuredResumeClassification:
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
    flat_text_fallback_present: bool
    cert_ref: str = U0_STRUCTURED_RESUME_CERT_S4


def _canonical_digest(value: Any) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _structured_errors(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["structured_resume must be a dict"]

    if value.get("schema_name") != _STRUCTURED_SCHEMA_NAME:
        errors.append(
            "schema_name must be source_resume_v2_structured"
        )
    if value.get("schema_version") != _STRUCTURED_SCHEMA_VERSION:
        errors.append("schema_version must be 2.0.0")

    for field in _REQUIRED_STRUCTURED_FIELDS:
        if field not in value:
            errors.append(f"missing required field: {field}")

    roles = value.get("roles")
    if "roles" in value and not isinstance(roles, list):
        errors.append("roles must be a list")

    return errors


def _available_sections(value: dict[str, Any]) -> list[str]:
    sections: list[str] = []
    for field in (
        "headline",
        "executive_summary",
        "roles",
        "competencies",
        *_OPTIONAL_SECTION_FIELDS,
    ):
        if field in value and value.get(field):
            sections.append(field)
    return sections


def classify_resume_payload(payload: dict[str, Any]) -> StructuredResumeClassification:
    structured_present = "structured_resume" in payload
    structured = payload.get("structured_resume")
    flat_text = str(payload.get("source_resume_text") or "")
    flat_text_stripped = flat_text.strip()
    fallback_present = bool(str(payload.get("flat_text_fallback") or "").strip())

    if structured_present:
        errors = _structured_errors(structured)
        if errors:
            return StructuredResumeClassification(
                source_resume_mode=ResumeInputMode.MISSING_OR_INVALID_RESUME.value,
                source_resume_schema_version=(
                    str(structured.get("schema_name") or "")
                    if isinstance(structured, dict)
                    else ""
                ),
                source_resume_digest=(
                    _canonical_digest(structured)
                    if isinstance(structured, dict)
                    else _text_digest(str(structured))
                ),
                available_sections=[],
                role_count=0,
                has_education=False,
                has_certifications=False,
                has_early_career=False,
                structured_resume_validation_status="INVALID",
                structured_resume_validation_errors=errors,
                flat_text_fallback_present=fallback_present,
            )

        structured_dict = structured if isinstance(structured, dict) else {}
        roles = structured_dict.get("roles") or []
        return StructuredResumeClassification(
            source_resume_mode=ResumeInputMode.STRUCTURED_SOURCE_RESUME_V2.value,
            source_resume_schema_version=_STRUCTURED_SCHEMA_NAME,
            source_resume_digest=_canonical_digest(structured_dict),
            available_sections=_available_sections(structured_dict),
            role_count=len(roles) if isinstance(roles, list) else 0,
            has_education=bool(structured_dict.get("education")),
            has_certifications=bool(structured_dict.get("certifications")),
            has_early_career=bool(structured_dict.get("early_career")),
            structured_resume_validation_status="VALID",
            structured_resume_validation_errors=[],
            flat_text_fallback_present=fallback_present,
        )

    if flat_text_stripped:
        return StructuredResumeClassification(
            source_resume_mode=ResumeInputMode.LEGACY_FLAT_RESUME.value,
            source_resume_schema_version="",
            source_resume_digest=_text_digest(flat_text),
            available_sections=[],
            role_count=0,
            has_education=False,
            has_certifications=False,
            has_early_career=False,
            structured_resume_validation_status="NOT_APPLICABLE",
            structured_resume_validation_errors=[],
            flat_text_fallback_present=fallback_present,
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
        structured_resume_validation_errors=["missing source resume"],
        flat_text_fallback_present=fallback_present,
    )


def attach_structured_resume_metadata(contract: dict[str, Any]) -> dict[str, Any]:
    resume_payload = contract.setdefault("resume_payload", {})
    if not isinstance(resume_payload, dict):
        resume_payload = {}
        contract["resume_payload"] = resume_payload

    classification = classify_resume_payload(resume_payload)
    resume_payload["s4_metadata"] = asdict(classification)
    return contract
