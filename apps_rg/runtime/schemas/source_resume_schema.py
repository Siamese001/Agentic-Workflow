"""S1: Source resume v2 structured schema validation helper.

App-local schema loader and validator for SourceResumeV2Structured.
Uses Python stdlib jsonschema if available, else falls back to a
minimal structural check so the module never hard-fails on import.

No agentic_core changes. No generation behavior. Schema and validation only.
See: artifacts/governance/apps_rg_resume_shipping_s1_structured_resume_schema.md
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_SCHEMA_PATH = Path(__file__).parent / "source_resume_v2_structured.json"

_REQUIRED_TOP_LEVEL = frozenset(
    ["schema_name", "schema_version", "headline", "executive_summary", "roles", "competencies"]
)

_VERBATIM_SECTIONS = frozenset(["education", "certifications", "early_career"])


def load_schema() -> dict[str, Any]:
    """Load the JSON Schema document from disk."""
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def validate_structured_resume(data: dict[str, Any]) -> list[str]:
    """Validate a structured resume dict against SourceResumeV2Structured.

    Returns a list of validation error strings. Empty list means valid.
    Attempts jsonschema if installed; falls back to minimal structural check.
    No generation behavior — schema validation only.
    """
    errors: list[str] = []

    try:
        import jsonschema  # type: ignore[import]

        schema = load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        for err in validator.iter_errors(data):
            errors.append(f"{'.'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}")
        return errors

    except ImportError:
        return _minimal_structural_check(data)


def _minimal_structural_check(data: dict[str, Any]) -> list[str]:
    """Fallback structural check when jsonschema is not installed.

    Checks required fields, schema_version, and verbatim section shape only.
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["<root>: expected object, got " + type(data).__name__]

    for field in _REQUIRED_TOP_LEVEL:
        if field not in data:
            errors.append(f"<root>: missing required field '{field}'")

    if data.get("schema_name") != "source_resume_v2_structured":
        errors.append(
            f"schema_name: expected 'source_resume_v2_structured', "
            f"got {data.get('schema_name')!r}"
        )

    if data.get("schema_version") != "2.0.0":
        errors.append(
            f"schema_version: expected '2.0.0', "
            f"got {data.get('schema_version')!r}"
        )

    for section in _VERBATIM_SECTIONS:
        if section in data:
            sec = data[section]
            if not isinstance(sec, dict):
                errors.append(f"{section}: expected object")
            elif "entries" not in sec:
                errors.append(f"{section}: missing required field 'entries'")
            elif sec.get("preserve_verbatim") is False:
                errors.append(f"{section}: preserve_verbatim must be true for verbatim sections")

    roles = data.get("roles", [])
    if not isinstance(roles, list):
        errors.append("roles: expected array")
    else:
        for i, role in enumerate(roles):
            if not isinstance(role, dict):
                errors.append(f"roles[{i}]: expected object")
                continue
            for rf in ("employer", "title", "narrative", "bullets"):
                if rf not in role:
                    errors.append(f"roles[{i}]: missing required field '{rf}'")
            bullets = role.get("bullets", [])
            if not isinstance(bullets, list):
                errors.append(f"roles[{i}].bullets: expected array")
            else:
                for j, bullet in enumerate(bullets):
                    if not isinstance(bullet, dict):
                        errors.append(f"roles[{i}].bullets[{j}]: expected object")
                        continue
                    for bf in ("source_text", "ordinal"):
                        if bf not in bullet:
                            errors.append(f"roles[{i}].bullets[{j}]: missing required field '{bf}'")

    return errors


def is_structured_resume(data: dict[str, Any]) -> bool:
    """Return True if data looks like a SourceResumeV2Structured document."""
    return (
        isinstance(data, dict)
        and data.get("schema_name") == "source_resume_v2_structured"
    )


__all__ = [
    "load_schema",
    "validate_structured_resume",
    "is_structured_resume",
]
