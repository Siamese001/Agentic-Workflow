"""Canonical apps_rg environment bootstrap.

Loads the ``.env`` SSOT into the current Python process before any provider
readiness or credential preflight reads ``os.environ``.

Worktree resilience (multi-worktree SSOT)
-----------------------------------------
``git worktree add`` only materializes *tracked* files, and ``.env`` is
gitignored — so a fresh worktree has no repo-root ``.env`` and every provider
call fails closed on missing credentials. To make one SSOT serve every
worktree, ``.env`` is resolved in this order (first existing file wins):

1. ``$APPS_RG_DOTENV`` — explicit operator override (a single absolute path).
2. ``<repo_root>/.env`` — back-compat / intentional per-worktree override.
3. ``~/.apps_rg/.env`` — canonical relocated SSOT outside any repo (survives
   worktree reaps, re-clones, and the primary checkout moving).

``override=False`` preserves already-exported shell credentials in all cases.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from apps_rg.runtime.runtime_proof_layout import find_repo_root

#: Env var naming an explicit ``.env`` SSOT path (highest precedence).
APPS_RG_DOTENV_ENV_VAR = "APPS_RG_DOTENV"


def canonical_home_dotenv() -> Path:
    """Repo-independent SSOT default: ``~/.apps_rg/.env`` (final fallback)."""
    return Path.home() / ".apps_rg" / ".env"


@dataclass(frozen=True)
class AppsRgEnvBootstrapResult:
    repo_root: str
    dotenv_path: str
    dotenv_path_existed: bool
    dotenv_loaded: bool
    #: Which candidate supplied the file: ``env_override`` | ``repo_root`` | ``home_ssot`` | ``none``.
    dotenv_source: str = "none"


def _candidate_dotenv_paths(root: Path) -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = []
    override = os.environ.get(APPS_RG_DOTENV_ENV_VAR, "").strip()
    if override:
        candidates.append(("env_override", Path(override).expanduser()))
    candidates.append(("repo_root", root / ".env"))
    candidates.append(("home_ssot", canonical_home_dotenv()))
    return candidates


def bootstrap_apps_rg_env(
    *,
    repo_root: Path | None = None,
    override: bool = False,
) -> AppsRgEnvBootstrapResult:
    """Load the ``.env`` SSOT for process-env provider checks.

    Resolution order: ``$APPS_RG_DOTENV`` → ``<repo_root>/.env`` → ``~/.apps_rg/.env``.
    ``override=False`` preserves already-exported shell credentials, matching the
    historical CLI behavior while making that behavior available outside
    ``python -m apps_rg``.
    """
    root = (repo_root or find_repo_root()).resolve()
    chosen_path = root / ".env"
    source = "none"
    loaded = False
    existed = False
    for src, candidate in _candidate_dotenv_paths(root):
        if candidate.is_file():
            chosen_path = candidate
            source = src
            existed = True
            from dotenv import load_dotenv

            loaded = bool(load_dotenv(dotenv_path=candidate, override=override))
            break
    return AppsRgEnvBootstrapResult(
        repo_root=str(root),
        dotenv_path=str(chosen_path),
        dotenv_path_existed=existed,
        dotenv_loaded=loaded,
        dotenv_source=source,
    )


def bootstrap_process_env_if_needed(environ: object) -> AppsRgEnvBootstrapResult | None:
    """Bootstrap only for the real process env, not injected test mappings."""
    if environ is os.environ:
        return bootstrap_apps_rg_env()
    return None


__all__ = [
    "APPS_RG_DOTENV_ENV_VAR",
    "AppsRgEnvBootstrapResult",
    "bootstrap_apps_rg_env",
    "bootstrap_process_env_if_needed",
    "canonical_home_dotenv",
]
