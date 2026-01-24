"""
apps_rg/shared/core/agent_base.py - Red Group Sovereign Bridge
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Final
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


@dataclass
class RGAgentBase(SovereignBaseAgent):
    """
    RGAgentBase: The Sovereign Foundation for all 'Red Group' Agents.

    Enforces V2.5 Sovereign Architecture:
    1. Inherits Security Hardening from SovereignBaseAgent
    2. Inherits Self-Healing through SovereignBaseAgent -> HealingStrategyMixin
    3. Enforces Domain Isolation via 'domain_root'
    """

    # Domain-specific RG configuration
    domain_root: Path = field(default_factory=lambda: Path("apps_rg"))
    _rg_version: Final[str] = "2.5.0"

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
