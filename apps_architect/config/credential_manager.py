"""Credential manager — secure token/secret resolution with source ladder.

Plan: ``.windsurf/plans/apps-architect-deferred-scope-b8e3f1.md`` DW1 DS-1.

Source ladder (first match wins):
1. Explicit constructor arg
2. OS environment variable
3. .env file in repo root
4. L4 secret store (future — stub)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv() -> dict[str, str]:
    env_file = _REPO_ROOT / ".env"
    if not env_file.exists():
        return {}
    result: dict[str, str] = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip().strip('"').strip("'")
    return result


class CredentialManager:
    """Resolves secrets from a configurable source ladder."""

    def __init__(self, overrides: dict[str, str] | None = None) -> None:
        self._overrides = dict(overrides or {})
        self._dotenv: dict[str, str] | None = None

    @property
    def _env_cache(self) -> dict[str, str]:
        if self._dotenv is None:
            self._dotenv = _load_dotenv()
        return self._dotenv

    def get(self, key: str, default: str = "") -> str:
        if key in self._overrides:
            return self._overrides[key]
        val = os.environ.get(key, "")
        if val:
            return val
        val = self._env_cache.get(key, "")
        if val:
            return val
        return default

    def require(self, key: str) -> str:
        val = self.get(key)
        if not val:
            raise KeyError(
                f"Required credential '{key}' not found in overrides, "
                f"os.environ, or .env file"
            )
        return val

    def configured(self, key: str) -> bool:
        return bool(self.get(key))

    def mask(self, key: str) -> str:
        val = self.get(key)
        if not val:
            return "<unset>"
        if len(val) <= 8:
            return "*" * len(val)
        return val[:4] + "*" * (len(val) - 8) + val[-4:]


__all__ = ["CredentialManager"]
