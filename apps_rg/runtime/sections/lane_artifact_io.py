"""Shared JSON artifact writers for section lanes (W11-M4A helper extraction)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def runtime_payload_for_json(payload: dict[str, Any]) -> dict[str, Any]:
    """Drop in-process-only keys before hashing or persisting ``runtime_payload.json``."""
    return {k: v for k, v in payload.items() if not str(k).startswith("_")}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
