"""
agentic_core/interfaces/execution.py

Sovereign execution interface for apps_* consumption.

AUTHORITY CONSTRAINTS:
- ExecutionProposal is inert — identifiers only, no callables/references
- No direct CIDRegistry mutation authority
- No cycle activation authority
- All execution requires L0 routing approval
- Apps_* may propose cycles but never execute directly

USAGE (apps_*):
    from agentic_core.interfaces.execution import (
        ExecutionProposal,
        CIDRegistry,
        ExecutionCycle,
        new_execution_cycle,
    )
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle


@dataclass(frozen=True)
class ExecutionProposal:
    """
    Inert execution proposal — identifiers only.

    DELIBERATELY EXCLUDES:
    - Resolved CIDRegistry references
    - Tool instances or callables
    - Bound methods
    - Any execution authority

    Only string identifiers are permitted.
    """

    cid: str
    cycle_id: str
    proposal_type: str
    app_prefix: str


def new_execution_cycle(registry: CIDRegistry, cid: str) -> ExecutionCycle:
    """
    Create a new execution cycle via the registry.

    This is the only permitted way apps_* may interact with CIDRegistry.
    Returns an immutable ExecutionCycle — no further mutation.
    """
    return registry.new_cycle(cid)


__all__ = ["ExecutionProposal", "CIDRegistry", "ExecutionCycle", "new_execution_cycle"]
