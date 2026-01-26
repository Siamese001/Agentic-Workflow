"""
apps_lic/shared/core/agent_base.py - LIC Sovereign Bridge
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Final
from pathlib import Path

# CORE SOCKETING: Align with Phase 20 Hardened Standards
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.healer_mixin import HealerMixin
from agentic_core.base_agents.meta_learning_mixin import MetaLearningMixin


@dataclass
class LICAgentBase(MetaLearningMixin, SovereignBaseAgent, HealerMixin):
    """
    LICAgentBase: Sovereign Foundation for 'Local Intelligence' (LIC).
    """

    # Domain-specific LIC configuration
    domain_root: Path = field(default_factory=lambda: Path("apps_lic"))
    _lic_version: Final[str] = "2.5.0-hardened"

    # [PHASE 25] Infrastructure Config (STRICTER)
    _namespace: str = field(default="apps_lic", init=False)
    _similarity_threshold: float = field(default=0.92, init=False)

    def __post_init__(self) -> None:
        """
        Initialize LIC capabilities after Core hardening.
        """
        # CRITICAL: Trigger Core Security Validation
        super().__post_init__()

        # LIC Domain Integrity Check
        if not self.domain_root.exists():
            self.domain_root.mkdir(parents=True, exist_ok=True)

    def get_lic_context(self) -> dict[str, Any]:
        return {
            "domain": "apps_lic",
            "version": self._lic_version,
            "capabilities": self.get_sovereign_capabilities(),
        }
