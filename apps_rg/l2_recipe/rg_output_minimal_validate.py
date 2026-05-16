"""Minimal structural validation against ``rg_output_schema.json`` (no jsonschema dep).

Used for RAW_TEXT_JSON_UNwrap and similar honest repairs: required keys only,
no field synthesis.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "rg_output_schema.json"

_TOP_LEVEL_REQUIRED: tuple[str, ...] = (
    "schema_version",
    "candidate_name",
    "target_role",
    "target_company",
    "generated_at",
    "sections",
    "citations",
    "gaps",
    "metadata",
)

_SECTIONS_REQUIRED: tuple[str, ...] = (
    "summary",
    "experience",
    "skills",
    "education",
)


@lru_cache(maxsize=1)
def _required_top_level() -> tuple[str, ...]:
    if not _SCHEMA_PATH.is_file():
        return _TOP_LEVEL_REQUIRED
    try:
        data = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        req = data.get("required")
        if isinstance(req, list) and all(isinstance(x, str) for x in req):
            return tuple(str(x) for x in req)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        pass
    return _TOP_LEVEL_REQUIRED


@lru_cache(maxsize=1)
def _sections_required() -> tuple[str, ...]:
    if not _SCHEMA_PATH.is_file():
        return _SECTIONS_REQUIRED
    try:
        data = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        sections = (data.get("properties") or {}).get("sections") or {}
        req = sections.get("required")
        if isinstance(req, list) and all(isinstance(x, str) for x in req):
            return tuple(str(x) for x in req)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        pass
    return _SECTIONS_REQUIRED


def minimal_rg_output_valid(obj: Any) -> tuple[bool, str]:
    """Return (True, "") if *obj* satisfies required top-level + sections keys."""
    if not isinstance(obj, dict):
        return False, "not_a_json_object"
    for k in _required_top_level():
        if k not in obj:
            return False, f"missing_top_level:{k}"
    sec = obj.get("sections")
    if not isinstance(sec, dict):
        return False, "sections_not_object"
    for k in _sections_required():
        if k not in sec:
            return False, f"missing_section:{k}"
    return True, ""


__all__ = ["minimal_rg_output_valid"]
