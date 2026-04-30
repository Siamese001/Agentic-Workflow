"""Cross-app contract test framework — package marker.

Exports the registry + builders. New apps register here; cross-app tests
import from here. Single source of truth for "minimal-valid input per app."

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W4.4)
"""
from __future__ import annotations

from tests._apps_contract.fixtures import (
    APP_CONTRACT_REGISTRY,
    AppContract,
    build_config,
    build_request,
    build_result,
    import_class,
)

__all__ = [
    "APP_CONTRACT_REGISTRY",
    "AppContract",
    "build_config",
    "build_request",
    "build_result",
    "import_class",
]
