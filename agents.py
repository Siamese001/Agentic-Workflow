# FILE: 10_10/agents.py
"""
Deprecated Multi-Agent Coordination Layer (v10_10)
==================================================

In v10_7 / v10_8 / early v10_9 designs, this module hosted
multi-agent "councils" and complex AgentGraph topologies.

In v10_10, those responsibilities have been fully and correctly
refactored into:

    • cognitive_agents.py   — Specialized LLM personas (Strategy, Drafting, QA, Safety)
    • l2.py                 — Single-pass execution using cognitive agents
    • l3.py                 — DAG orchestration + self-correction
    • self_correction.py    — Correction surfaces (pure decision logic)

This file is kept ONLY for backward compatibility with older branches
or stray imports. New code MUST NOT depend on it.

If you see any reference like:

    from agents import AgentGraph, AgentNode, MultiAgentCouncilResult

you should refactor that call site to use the new 10_10 architecture instead.
"""

from __future__ import annotations

# No runtime classes or functions are intentionally exposed from here.
# All multi-agent coordination is handled by:
#   • l3.run_dag
#   • self_correction.evaluate_all_surfaces
#   • cognitive_agents (individual LLM personas)

__all__: list[str] = []
