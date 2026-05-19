"""Shared JSON base-resume loader for section lanes (neutral SSOT)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.resume_resolution import load_lane_base_resume_json


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "resume" / "base").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()


def load_base_resume(
    *,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], Path, str]:
    """Return ``(resume_dict, resolved_path, canonical_resume_digest)`` for lane consumers."""
    root = repo_root if repo_root is not None else REPO_ROOT
    return load_lane_base_resume_json(repo_root=root)
