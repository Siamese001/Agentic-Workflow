"""
apps_lic/shared/core/agent_base.py - Linked-In Canonical Sovereign Bridge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

# CORE SOCKETING: Align with Phase 20 Hardened Standards
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

# Import mixins with fallbacks
try:
    from agentic_core.L1_cognition.thought_engine.meta_learning_mixin import MetaLearningMixin
except ImportError:

    class MetaLearningMixin:
        pass


try:
    from agentic_core.L5_safety.validators.healing_mixin import HealerMixin
except ImportError:

    class HealerMixin:
        pass


@dataclass
class LICAgentBase(MetaLearningMixin, SovereignBaseAgent, HealerMixin):
    """
    LICAgentBase: Sovereign Foundation for 'Linked-In Canonical' (LIC).
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
