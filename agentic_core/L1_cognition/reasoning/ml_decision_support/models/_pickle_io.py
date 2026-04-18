"""Safe pickle IO helpers for ML model artifacts."""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

_MAX_PICKLE_BYTES = 100 * 1024 * 1024
_ALLOWED_SUFFIXES = {".pkl", ".pickle"}


def _normalize_pickle_path(path: Path | str) -> Path:
    normalized = Path(path).expanduser()
    if normalized.suffix.lower() not in _ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported model artifact suffix: {normalized.suffix}")
    return normalized


def safe_pickle_load(path: Path | str, *, max_bytes: int = _MAX_PICKLE_BYTES) -> Any:
    normalized = _normalize_pickle_path(path)
    resolved = normalized.resolve(strict=True)
    size = resolved.stat().st_size
    if size > max_bytes:
        raise ValueError(f"Model artifact exceeds maximum allowed size ({size} > {max_bytes} bytes)")
    with resolved.open("rb") as handle:
        return pickle.load(handle)


def safe_pickle_dump(payload: Any, path: Path | str) -> Path:
    normalized = _normalize_pickle_path(path)
    normalized.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("wb", dir=normalized.parent, delete=False) as handle:
        tmp_path = Path(handle.name)
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
    try:
        os.replace(tmp_path, normalized)
    except OSError:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise
    return normalized
