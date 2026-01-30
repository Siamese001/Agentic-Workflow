"""
apps_rg/shared/core/agent_base.py - Resume Generation Sovereign Bridge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from agentic_core.base_agents.meta_learning_mixin import MetaLearningMixin
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


@dataclass
class RGAgentBase(MetaLearningMixin, SovereignBaseAgent):
    """
    RGAgentBase: The Sovereign Foundation for all 'Resume Generation' Agents.
    """

    # Domain-specific RG configuration
    domain_root: Path = field(default_factory=lambda: Path("apps_rg"))
    _rg_version: Final[str] = "2.5.0"

    # [PHASE 25] Infrastructure Config
    _namespace: str = field(default="apps_rg", init=False)
    _similarity_threshold: float = field(default=0.85, init=False)

    def __post_init__(self) -> None:
        """
        Initialize RG-specific capabilities after Core hardening.
        """
        # CRITICAL: Trigger Core Security Validation in SovereignBaseAgent
        super().__post_init__()

        # RG Domain Validation
        if not self.domain_root.exists():
            # Create if missing to ensure domain integrity
            self.domain_root.mkdir(parents=True, exist_ok=True)

    def get_rg_context(self) -> dict[str, Any]:
        """Return RG-specific context wrapper."""
        return {
            "domain": "apps_rg",
            "version": self._rg_version,
            "capabilities": self.get_sovereign_capabilities(),
        }
