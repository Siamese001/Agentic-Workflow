# FILE: 10_10/agents.py
"""
Deprecated Multi-Agent Layer (v10_10)
=====================================

This file replaces the v10_9 multi-agent coordination system.

In v10_9, this module implemented:
    • AgentGraph
    • AgentNode
    • Multi-agent councils (QA, Safety, Meta)
    • MultiAgentVote / MultiAgentCouncilResult
    • Delegation graphs
    • Multi-agent scoring
    • Orchestration surfaces
    • L4 patch-ready payload emitters

NONE of this is permitted inside the v10_10 runtime.

The v10_10 L1–L5 architecture *eliminates the multi-agent layer entirely*:

    L1 = Planning
    L2 = Cognition (Strategy / Drafting / QA / Safety agents)
    L3 = DAG + Self-Correction
    L4 = State Adapter
    L5 = Safety Policy

Multi-agent arbitration is NOT part of L1–L5 and must NOT be imported by
any runtime component.

This module exists ONLY as a backward-compatibility stub so legacy imports
like:

    from agents import AgentGraph
    from agents import MultiAgentCouncilResult

do not crash older scripts or notebooks.

All such use is invalid in v10_10 and must be removed.
"""

from __future__ import annotations

__all__: list[str] = []


def __getattr__(name: str):
    """
    Intercept legacy attribute access and provide a precise upgrade error.

    Any code trying to import multi-agent constructs (AgentGraph,
    AgentNode, MultiAgentVote, MultiAgentCouncilResult, SelfCorrectionSurface)
    MUST be refactored to use the v10_10 architecture, which does not
    contain a meta-agent layer.
    """
    raise AttributeError(
        f"'agents' module is deprecated in v10_10. Multi-agent graphs, "
        f"councils, and arbitration logic were removed. Attempted access: {name!r}. "
        f"Refactor this code — no multi-agent constructs exist in v10_10."
    )
