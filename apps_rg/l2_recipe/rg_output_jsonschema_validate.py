"""Full-document validation against ``apps_rg/rg_output_schema.json`` (jsonschema, Draft 7)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "rg_output_schema.json"


@lru_cache(maxsize=1)
def _draft7_validator():
    import jsonschema

    raw = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft7Validator(raw)


def rg_output_schema_path() -> Path:
    return _SCHEMA_PATH


def validate_rg_output_object(obj: Any) -> tuple[bool, str]:
    """Return (True, \"\") if *obj* satisfies rg_output_schema.json; else (False, error)."""
    if not isinstance(obj, dict):
        return False, "candidate_not_object"
    if not _SCHEMA_PATH.is_file():
        return False, f"schema_missing:{_SCHEMA_PATH}"
    v = _draft7_validator()
    errors = sorted(v.iter_errors(obj), key=lambda e: e.path)
    if not errors:
        return True, ""
    first = errors[0]
    path = "/".join(str(p) for p in first.absolute_path)
    return False, f"{first.message} at {path or '/'}"


__all__ = ["rg_output_schema_path", "validate_rg_output_object"]
