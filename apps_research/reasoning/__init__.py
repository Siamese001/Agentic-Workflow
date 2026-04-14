"""
apps_research Reasoning Layer — Autonomous Research Engine Agents.

Use lazy exports so package import stays safe when optional runtime dependencies
are not installed yet.
"""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "ResearchOrchestrator": "apps_research.reasoning.ResearchOrchestrator",
    "SourceDiscoveryAgent": "apps_research.reasoning.SourceDiscoveryAgent",
    "InsightExtractionAgent": "apps_research.reasoning.InsightExtractionAgent",
    "KnowledgeSynthesisAgent": "apps_research.reasoning.KnowledgeSynthesisAgent",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module 'apps_research.reasoning' has no attribute {name!r}")
    module = import_module(module_path)
    return getattr(module, name)
