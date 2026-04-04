"""
apps_research Reasoning Layer — Autonomous Research Engine Agents.

Multi-agent ecosystem for source discovery, insight extraction, and knowledge synthesis.
"""

from apps_research.reasoning.InsightExtractionAgent import InsightExtractionAgent
from apps_research.reasoning.KnowledgeSynthesisAgent import KnowledgeSynthesisAgent
from apps_research.reasoning.ResearchOrchestrator import ResearchOrchestrator
from apps_research.reasoning.SourceDiscoveryAgent import SourceDiscoveryAgent

__all__ = [
    "ResearchOrchestrator",
    "SourceDiscoveryAgent",
    "InsightExtractionAgent",
    "KnowledgeSynthesisAgent",
]
