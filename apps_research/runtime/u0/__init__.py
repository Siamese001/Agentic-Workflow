"""apps_research U0 runtime adapters.

Canonical U0 validation for the governed spine lives in
``agentic_core.runtime.entry.u0_apps_research_binding`` and is wired through
``apps_research.runtime.profile_builder.build_app_runtime_contract``.

Package-driven U0 v2 validation remains in ``apps_research.runtime.u0.binding``.
"""
from __future__ import annotations

from agentic_core.runtime.entry.u0_apps_research_binding import (
    APPS_RESEARCH_TASK_CLASS,
    u0_validate_apps_research,
)
from apps_research.runtime.u0.binding import (
    u0_validate_apps_research_v2,
)

__all__ = [
    "u0_validate_apps_research",
    "u0_validate_apps_research_v2",
    "APPS_RESEARCH_TASK_CLASS",
]
