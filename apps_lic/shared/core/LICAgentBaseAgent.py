"""
apps_lic/shared/core/agent_base.py - Linked-In Canonical Sovereign Bridge

PHASE 3 META-LEARNING (Feb 2026):
- MetaLearningClientMixin activation for LIC domain
- Domain-specific healing pattern memory (similarity_threshold=0.92)
- Campaign pattern learning and compliance rule memory
- Redis/Pinecone integration for outreach optimization
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

# CORE SOCKETING: Align with Phase 20 Hardened Standards
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)

# Import mixins with fallbacks
try:
    from agentic_core.L1_cognition.thought_engine.meta_learning_mixin import (
        MetaLearningMixin,
    )
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

    [PHASE 3] Meta-Learning Integration:
    - Inherits MetaLearningClientMixin from SovereignBaseAgent
    - Domain automatically set to 'apps_lic' for cache isolation
    - Higher similarity threshold (0.92) for stricter pattern matching
    - Campaign pattern learning and compliance rule memory
    """

    # Domain-specific LIC configuration
    domain_root: Path = field(default_factory=lambda: Path("apps_lic"))
    _lic_version: Final[str] = "2.5.0-hardened"

    # [PHASE 25] Infrastructure Config (STRICTER)
    _namespace: str = field(default="apps_lic", init=False)
    _similarity_threshold: float = field(default=0.92, init=False)

    # [PHASE 3] Meta-Learning Domain Override
    _ml_domain: str = field(default="apps_lic", init=False)

    def __post_init__(self) -> None:
        """
        Initialize LIC capabilities after Core hardening.
        """
        # CRITICAL: Trigger Core Security Validation
        super().__post_init__()

        # LIC Domain Integrity Check
        if not self.domain_root.exists():
            self.domain_root.mkdir(parents=True, exist_ok=True)

        Logger.debug(f"[{self.__class__.__name__}] LIC Meta-Learning activated")

    def get_lic_context(self) -> dict[str, Any]:
        return {
            "domain": "apps_lic",
            "version": self._lic_version,
            "capabilities": self.get_sovereign_capabilities(),
            "meta_learning_domain": self._ml_domain,
        }

    # ==================== LIC-SPECIFIC META-LEARNING ====================

    def ml_cache_campaign_pattern(
        self,
        campaign_id: str,
        pattern_data: dict[str, Any],
    ) -> bool:
        """
        Cache a successful campaign pattern for future recall.

        Args:
            campaign_id: Unique campaign identifier
            pattern_data: Campaign pattern data (templates, timing, etc.)

        Returns:
            True if cached successfully
        """
        cache_key = f"campaign_pattern:{campaign_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    def ml_recall_campaign_pattern(self, campaign_id: str) -> dict[str, Any] | None:
        """
        Recall a cached campaign pattern.

        Args:
            campaign_id: Unique campaign identifier

        Returns:
            Cached pattern data or None
        """
        cache_key = f"campaign_pattern:{campaign_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_compliance_rule(
        self,
        rule_id: str,
        rule_data: dict[str, Any],
    ) -> bool:
        """
        Cache a compliance rule resolution for future reference.

        Args:
            rule_id: Unique rule identifier
            rule_data: Rule resolution data

        Returns:
            True if cached successfully
        """
        cache_key = f"compliance_rule:{rule_id}"
        return self.ml_cache_set(cache_key, rule_data)

    def ml_recall_compliance_rule(self, rule_id: str) -> dict[str, Any] | None:
        """
        Recall a cached compliance rule resolution.

        Args:
            rule_id: Unique rule identifier

        Returns:
            Cached rule data or None
        """
        cache_key = f"compliance_rule:{rule_id}"
        return self.ml_cache_get(cache_key)
