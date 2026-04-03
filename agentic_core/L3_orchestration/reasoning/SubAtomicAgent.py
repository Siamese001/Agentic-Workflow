"""SubAtomic Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L3_orchestration.utils.subatomic_agent_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L3_orchestration.utils.subatomic_agent_util import (
    heal_violation as _heal_violation,
    heal_repository as _heal_repository,
    create_subatomic_impl as _create_subatomic_impl,
    SubAtomicResult,
    SubAtomicImpl,
)


class SubAtomicAgent(SovereignBaseAgent):
    """
    DEPRECATED: SubAtomic Agent - now delegates to subatomic_agent_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L3_orchestration.utils.subatomic_agent_util directly.
    """

    def __init__(self):
        """Initialize SubAtomicAgent (deprecated, use subatomic_agent_util instead)."""
        super().__init__(name="SubAtomicAgent", layer="L3")

        warnings.warn(
            "SubAtomicAgent is deprecated. Use agentic_core.L3_orchestration.utils.subatomic_agent_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def heal(self, violation: dict[str, Any]) -> SubAtomicResult:
        """Heal violations in subatomic agent logic."""
        return _heal_violation(violation)

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int | bool]:
        """L1 cognition - operational only."""
        return _heal_repository(dry_run, execute, depth, max_depth, _call_path)

    def create_impl(self, ctx: Any, name: str) -> SubAtomicImpl:
        """Create SubAtomic implementation."""
        return _create_subatomic_impl(ctx, name)
