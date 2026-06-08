"""Canonical apps_rg environment bootstrap.

Loads the repository-root ``.env`` into the current Python process before any
provider readiness or credential preflight reads ``os.environ``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from apps_rg.runtime.runtime_proof_layout import find_repo_root


@dataclass(frozen=True)
class AppsRgEnvBootstrapResult:
    repo_root: str
    dotenv_path: str
    dotenv_path_existed: bool
    dotenv_loaded: bool


def bootstrap_apps_rg_env(
    *,
    repo_root: Path | None = None,
    override: bool = False,
) -> AppsRgEnvBootstrapResult:
    """Load repo-root ``.env`` for process-env provider checks.

    ``override=False`` preserves already-exported shell credentials, matching the
    historical CLI behavior while making that behavior available outside
    ``python -m apps_rg``.
    """
    root = (repo_root or find_repo_root()).resolve()
    env_path = root / ".env"
    loaded = False
    if env_path.is_file():
        from dotenv import load_dotenv

        loaded = bool(load_dotenv(dotenv_path=env_path, override=override))
    return AppsRgEnvBootstrapResult(
        repo_root=str(root),
        dotenv_path=str(env_path),
        dotenv_path_existed=env_path.is_file(),
        dotenv_loaded=loaded,
    )


def bootstrap_process_env_if_needed(environ: object) -> AppsRgEnvBootstrapResult | None:
    """Bootstrap only for the real process env, not injected test mappings."""
    if environ is os.environ:
        return bootstrap_apps_rg_env()
    return None


__all__ = [
    "AppsRgEnvBootstrapResult",
    "bootstrap_apps_rg_env",
    "bootstrap_process_env_if_needed",
]
