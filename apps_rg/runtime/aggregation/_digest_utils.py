"""Shared deterministic digest helpers for aggregation modules."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


def canonical_json_sorted(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_utf8(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_utf8(path.read_text(encoding="utf-8"))


def sha256_file_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_claim_text(text: str) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip().lower())
    return t


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9%$]+", normalize_claim_text(text)) if len(w) > 1]


def rel_posix(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return path.resolve().as_posix()
