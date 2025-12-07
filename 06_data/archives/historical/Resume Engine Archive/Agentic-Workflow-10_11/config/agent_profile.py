from __future__ import annotations

"""Agent profile facade used by Phase-1 agent substrate.

This module re-exports AgentCard from the unified models.py so that
core.agent_router_policy and future profile tooling can depend on a
stable import path.
"""

from core.models.models import AgentCard  # noqa: F401

__all__ = ["AgentCard"]



