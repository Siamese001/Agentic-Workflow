from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .schemas import PromptSchema, validate_prompt


_BASE_DIR = Path(__file__).resolve().parent
_STORE_DIR = _BASE_DIR / "data"
_STORE_DIR.mkdir(parents=True, exist_ok=True)


def _path_for_id(prompt_id: str) -> Path:
    return _STORE_DIR / f"{prompt_id}.json"


def _load_all_versions(prompt_id: str) -> Dict[str, Dict[str, Any]]:
    path = _path_for_id(prompt_id)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _save_all_versions(prompt_id: str, versions: Dict[str, Dict[str, Any]]) -> None:
    path = _path_for_id(prompt_id)
    with path.open("w", encoding="utf-8") as f:
        json.dump(versions, f, indent=2, sort_keys=True)


def save_prompt_version(prompt_id: str, prompt: Dict[str, Any] | PromptSchema, metadata: Optional[Dict[str, Any]] = None) -> PromptSchema:
    """Persist a prompt version to disk.

    The version string is taken from the PromptSchema.version field.
    Additional metadata (e.g., author, timestamp) can be stored alongside
    the schema under a "meta" key.
    """

    schema = validate_prompt(prompt)
    versions = _load_all_versions(prompt_id)

    payload: Dict[str, Any] = {
        "schema": schema.model_dump(),
        "meta": metadata or {},
    }
    versions[schema.version] = payload
    _save_all_versions(prompt_id, versions)

    return schema


def get_prompt_version(prompt_id: str, version: str) -> Optional[PromptSchema]:
    versions = _load_all_versions(prompt_id)
    payload = versions.get(version)
    if not payload:
        return None
    data = payload.get("schema") or {}
    return validate_prompt(data)


def list_versions(prompt_id: str) -> List[str]:
    versions = _load_all_versions(prompt_id)
    return sorted(versions.keys())
