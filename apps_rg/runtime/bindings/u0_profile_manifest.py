"""L1 planning profile manifest helpers for apps_rg U0 (p3.1 W2).

Repo-local digest computation for ``rg_planning_profile.yaml``. Keeps
``u0_binding`` import-cycle free from hashing details.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Final

_L1_PLANNING_PROFILE_RELPATH: Final[str] = "apps_rg/profiles/rg_planning_profile.yaml"


class ProfileManifestError(RuntimeError):
    """Raised when the L1 planning profile file is missing or unreadable."""


def repo_root() -> Path:
    """Resolve repository root (directory containing ``pyproject.toml``)."""

    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise ProfileManifestError("Cannot locate repository root (pyproject.toml).")


def l1_planning_profile_digest(*, allow_missing: bool = False) -> str:
    """SHA-256 digest (64-char hex) of ``apps_rg/profiles/rg_planning_profile.yaml``.

    Parameters
    ----------
    allow_missing:
        If True, returns ``\"\"`` when the file is missing (tests without a
        full checkout layout). Runtime callers must pass ``False``.
    """

    path = repo_root() / _L1_PLANNING_PROFILE_RELPATH
    if not path.is_file():
        if allow_missing:
            return ""
        raise ProfileManifestError(
            f"L1 planning profile not found at {path}. "
            "Pass allow_missing_profiles=True only in tests without repo files."
        )
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        if allow_missing:
            return ""
        raise ProfileManifestError(
            f"L1 planning profile unreadable at {path}: {exc}"
        ) from exc


def l1_planning_profile_ref() -> str:
    """Canonical repo-relative path string for the L1 planning profile."""

    return _L1_PLANNING_PROFILE_RELPATH


__all__ = [
    "ProfileManifestError",
    "l1_planning_profile_digest",
    "l1_planning_profile_ref",
    "repo_root",
]
