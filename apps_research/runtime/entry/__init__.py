"""apps_research runtime entrypoints.

Contains app-specific dispatch callables for AppIngressRunner.
"""
from __future__ import annotations

from apps_research.runtime.entry.dispatch import (
    apps_research_parse,
    apps_research_dispatch,
    APPS_RESEARCH_REQUIRED_FIELDS,
)

__all__ = [
    "apps_research_parse",
    "apps_research_dispatch",
    "APPS_RESEARCH_REQUIRED_FIELDS",
]
