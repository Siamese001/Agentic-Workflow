"""Shared JSON artifact writers for section lanes (W11-M4A helper extraction)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
