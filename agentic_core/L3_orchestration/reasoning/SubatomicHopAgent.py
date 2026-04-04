"""Subatomic Hop Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L3_orchestration.utils.subatomic_hop_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L3_orchestration.utils.subatomic_hop_util import (
    HopContext,
    SubatomicHopResult,
)
from agentic_core.L3_orchestration.utils.subatomic_hop_util import (
    create_hop_context as _create_hop_context,
)
from agentic_core.L3_orchestration.utils.subatomic_hop_util import (
    ensure_dependency as _ensure_dependency,
)
from agentic_core.L3_orchestration.utils.subatomic_hop_util import (
    run_self_tests as _run_self_tests,
)
from agentic_core.L3_orchestration.utils.subatomic_hop_util import (
    validate_dependencies as _validate_dependencies,
)


class SubatomicHopAgent(SovereignBaseAgent):
    """
    DEPRECATED: Subatomic Hop Agent - now delegates to subatomic_hop_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L3_orchestration.utils.subatomic_hop_util directly.
    """

    def __init__(
        self,
        role: str,
        config: dict,
        storage: Any | None = None,
        genealogy: Any | None = None,
        **kwargs,
    ):
        """Initialize SubatomicHopAgent (deprecated, use subatomic_hop_util instead)."""
        super().__init__(name="SubatomicHopAgent", layer="L3")

        warnings.warn(
            "SubatomicHopAgent is deprecated. Use agentic_core.L3_orchestration.utils.subatomic_hop_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.role = role
        self.config = config
        self.storage = storage
        self.genealogy = genealogy

    def validate_dependencies(self) -> SubatomicHopResult:
        """Validate that required dependencies are present."""
        return _validate_dependencies(
            role=self.role,
            config=self.config,
            storage=self.storage,
            genealogy=self.genealogy,
        )

    def create_hop_context(self) -> HopContext:
        """Create a hop context for routing."""
        return _create_hop_context(self.role, self.config)

    def run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        return _run_self_tests(self.role, self.config)

    def ensure_dep(self, dep: Any, name: str) -> Any:
        """Validate that a required dependency was injected."""
        return _ensure_dependency(dep, name)
