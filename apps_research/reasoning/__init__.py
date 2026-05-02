"""
apps_research Reasoning Layer — Autonomous Research Engine Agents.

Eagerly re-exports the agent classes from their submodules. Earlier this
package used a `__getattr__` lazy-import pattern, but that pattern is
shadowed by Python's normal submodule lookup when the export name
matches the submodule filename (e.g. `KnowledgeSynthesisAgent` is both
the class AND the file `KnowledgeSynthesisAgent.py`). The shadowing
caused `from apps_research.reasoning import KnowledgeSynthesisAgent` to
return the MODULE rather than the class, breaking instantiation.

Eager imports avoid the shadowing and keep the public surface intact.
"""

from __future__ import annotations

from apps_research.reasoning.InsightExtractionAgent import InsightExtractionAgent
from apps_research.reasoning.KnowledgeSynthesisAgent import KnowledgeSynthesisAgent
from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
from apps_research.reasoning.SourceDiscoveryAgent import SourceDiscoveryAgent

__all__ = [
    "InsightExtractionAgent",
    "KnowledgeSynthesisAgent",
    "ResearchOrchestrator",
    "SourceDiscoveryAgent",
]
