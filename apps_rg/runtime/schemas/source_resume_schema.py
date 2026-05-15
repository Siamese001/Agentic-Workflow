"""apps_rg source resume schema — structured resume validation.

Validates that a dict is a well-formed structured resume matching the
master_resume schema (schema_version=master_resume_v2.*).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

__all__ = [
    "is_structured_resume",
    "load_schema",
    "validate_structured_resume",
    "StructuredResumeValidationError",
    "SCHEMA_VERSION_PREFIX",
]

SCHEMA_VERSION_PREFIX: str = "master_resume_v2"

_SCHEMA_CACHE: Optional[dict] = None

_REQUIRED_TOP_LEVEL_FIELDS = frozenset({
    "schema_version",
    "personal_info",
    "sections",
})

_REQUIRED_SECTION_IDS = frozenset({
    "headline",
    "executive_summary",
})


class StructuredResumeValidationError(ValueError):
    """Raised when a structured resume fails schema validation."""


def load_schema() -> dict[str, Any]:
    """Load the master resume JSON schema (cached).

    Falls back to a minimal embedded schema if the file is not present.
    """
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE

    candidates = [
        Path(__file__).resolve().parents[3] / "rg_output_schema.json",
        Path(__file__).resolve().parents[4] / "apps_rg" / "rg_output_schema.json",
    ]
    for path in candidates:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                _SCHEMA_CACHE = json.load(f)
                return _SCHEMA_CACHE

    _SCHEMA_CACHE = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": list(_REQUIRED_TOP_LEVEL_FIELDS),
        "properties": {
            "schema_version": {"type": "string"},
            "personal_info": {"type": "object"},
            "sections": {"type": "object"},
        },
    }
    return _SCHEMA_CACHE


def is_structured_resume(obj: Any) -> bool:
    """Return True if obj looks like a valid structured resume dict."""
    if not isinstance(obj, dict):
        return False
    if not _REQUIRED_TOP_LEVEL_FIELDS.issubset(obj.keys()):
        return False
    version = obj.get("schema_version", "")
    if not str(version).startswith(SCHEMA_VERSION_PREFIX):
        return False
    sections = obj.get("sections", {})
    if not isinstance(sections, dict):
        return False
    return True


def validate_structured_resume(
    resume: dict[str, Any],
    *,
    strict: bool = False,
) -> list[str]:
    """Validate a structured resume dict against the schema.

    Parameters
    ----------
    resume:
        Resume dict to validate.
    strict:
        If True, raise StructuredResumeValidationError on first violation.
        If False, return a list of violation strings (empty means valid).

    Returns
    -------
    list[str]
        List of validation error strings. Empty if valid.
    """
    errors: list[str] = []

    if not isinstance(resume, dict):
        errors.append("resume must be a dict")
        if strict:
            raise StructuredResumeValidationError(errors[0])
        return errors

    for field in _REQUIRED_TOP_LEVEL_FIELDS:
        if field not in resume:
            errors.append(f"missing required field: {field}")

    version = resume.get("schema_version", "")
    if not str(version).startswith(SCHEMA_VERSION_PREFIX):
        errors.append(
            f"schema_version must start with '{SCHEMA_VERSION_PREFIX}', got: {version!r}"
        )

    sections = resume.get("sections", {})
    if not isinstance(sections, dict):
        errors.append("'sections' must be a dict")
    else:
        for req_id in _REQUIRED_SECTION_IDS:
            if req_id not in sections:
                errors.append(f"missing required section: {req_id}")

    if strict and errors:
        raise StructuredResumeValidationError("; ".join(errors))

    return errors
