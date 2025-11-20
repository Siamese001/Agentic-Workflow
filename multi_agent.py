# FILE: 10_10/multi_agent.py
"""
Deprecated Multi-Agent Layer (v10_10)
=====================================

The multi-agent graph, council, committee, and coordination patterns
from v10_7–v10_9 are **not part of the v10_10 runtime architecture**.

In v10_10:

    • L1 handles planning ONLY.
    • L2 handles ALL cognition (Strategy, Drafting, QA, Safety).
    • L3 handles the DAG + retries.
    • L4 handles deterministic state patches.
    • L5 handles final safety gating.

No multi-agent arbitration, council voting, committee formation,
delegation routing, graph topologies, or meta-layer simulations are
permitted inside a v10_10 runtime.

This module exists *ONLY* to prevent import failures for legacy code.
All multi-agent logic has been removed by design.

If you see any imports like:

    from multi_agent import MultiAgentCoordinator
    from multi_agent import build_council

You MUST remove or refactor those call sites. The 10_10 architecture
provides no runtime multi-agent layer.

This file intentionally exposes nothing.
"""

from __future__ import annotations


__all__: list[str] = []


def __getattr__(name: str):
    """
    Legacy guard: if older code tries to access multi-agent constructs,
    raise a clear, explicit error.
    """
    raise AttributeError(
        f"'multi_agent' is deprecated in v10_10. "
        f"The multi-agent coordination layer was removed. "
        f"All cognition is handled by L2 cognitive agents, and all "
        f"orchestration by L3 DAG. '{name}' does not exist in v10_10."
    )
