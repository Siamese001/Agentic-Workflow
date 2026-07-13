"""Compatibility export for the app-owned Apps Research U0 binding.

TEMPORARY_THIN_ADAPTER: canonical implementation lives in
``apps_research.runtime.u0.binding``. Removal is governed by migration receipt
``20260713_issue_550_core_boundary_migration_receipt.json`` and due 2026-10-11.
"""

from __future__ import annotations

import warnings

from apps_research.runtime.u0.binding import (
    APPS_RESEARCH_TASK_CLASS as APPS_RESEARCH_TASK_CLASS,
)
from apps_research.runtime.u0.binding import (
    AppsResearchAuthorityViolation,
    AppsResearchU0ReflectionReceipt,
    _scan_for_legacy_authority,
    u0_validate_apps_research,
)

warnings.warn(
    "agentic_core.runtime.entry.u0_apps_research_binding is deprecated; "
    "import apps_research.runtime.u0.binding instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "AppsResearchAuthorityViolation",
    "AppsResearchU0ReflectionReceipt",
    "_scan_for_legacy_authority",
    "u0_validate_apps_research",
]
