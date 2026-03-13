"""Shim: re-exports AgentState from its canonical location.

Canonical source: agentic_core.runtime.types.state_types
"""

from agentic_core.runtime.types.state_types import AgentMessage, AgentState  # noqa: F401

__all__ = ["AgentState", "AgentMessage"]
