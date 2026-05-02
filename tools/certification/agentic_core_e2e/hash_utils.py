"""Hash + path utilities for the core harness.

Intentionally duplicated from the apps_e2e helpers to enforce the
boundary invariant — the core harness does not import apps_e2e modules.
The two harnesses share NO code; they share a discipline.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_to_repo(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def write_json(path: Path, payload: dict[str, Any]) -> tuple[str, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
    path.write_bytes(data)
    return (sha256_bytes(data), len(data))


def git_head() -> tuple[str, bool]:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, shell=False, check=True,
            cwd=str(REPO_ROOT),
        ).stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return ("UNKNOWN", False)
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10, shell=False, check=True,
            cwd=str(REPO_ROOT),
        ).stdout
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return (sha, False)
    return (sha, bool(status.strip()))


__all__ = [
    "REPO_ROOT", "utc_now_iso", "sha256_file", "sha256_bytes",
    "relative_to_repo", "write_json", "git_head",
]
