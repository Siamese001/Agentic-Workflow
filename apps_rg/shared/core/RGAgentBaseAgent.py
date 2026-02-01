"""
apps_rg/shared/core/agent_base.py - Resume Generation Sovereign Bridge

PHASE 3 META-LEARNING (Feb 2026):
- MetaLearningClientMixin activation for RG domain
- Domain-specific healing pattern memory (similarity_threshold=0.85)
- Resume quality pattern learning and ATS compatibility memory
- Redis/Pinecone integration for content optimization
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from agentic_core.base_agents.meta_learning_mixin import MetaLearningMixin
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)


@dataclass
class RGAgentBase(MetaLearningMixin, SovereignBaseAgent):
    """
    RGAgentBase: The Sovereign Foundation for all 'Resume Generation' Agents.

    [PHASE 3] Meta-Learning Integration:
    - Inherits MetaLearningClientMixin from SovereignBaseAgent
    - Domain automatically set to 'apps_rg' for cache isolation
    - Standard similarity threshold (0.85) for pattern matching
    - Resume quality pattern learning and ATS compatibility memory
    """

    # Domain-specific RG configuration
    domain_root: Path = field(default_factory=lambda: Path("apps_rg"))
    _rg_version: Final[str] = "2.5.0"

    # [PHASE 25] Infrastructure Config
    _namespace: str = field(default="apps_rg", init=False)
    _similarity_threshold: float = field(default=0.85, init=False)

    # [PHASE 3] Meta-Learning Domain Override
    _ml_domain: str = field(default="apps_rg", init=False)

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

        Logger.debug(f"[{self.__class__.__name__}] RG Meta-Learning activated")

    def get_rg_context(self) -> dict[str, Any]:
        """Return RG-specific context wrapper."""
        return {
            "domain": "apps_rg",
            "version": self._rg_version,
            "capabilities": self.get_sovereign_capabilities(),
            "meta_learning_domain": self._ml_domain,
        }

    # ==================== RG-SPECIFIC META-LEARNING ====================

    def ml_cache_resume_quality_pattern(
        self,
        pattern_id: str,
        pattern_data: dict[str, Any],
    ) -> bool:
        """
        Cache a successful resume quality pattern for future recall.

        Args:
            pattern_id: Unique pattern identifier
            pattern_data: Quality pattern data (structure, content, etc.)

        Returns:
            True if cached successfully
        """
        cache_key = f"resume_quality:{pattern_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    def ml_recall_resume_quality_pattern(self, pattern_id: str) -> dict[str, Any] | None:
        """
        Recall a cached resume quality pattern.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Cached pattern data or None
        """
        cache_key = f"resume_quality:{pattern_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_ats_compatibility(
        self,
        ats_system: str,
        compatibility_data: dict[str, Any],
    ) -> bool:
        """
        Cache ATS compatibility requirements for future reference.

        Args:
            ats_system: ATS system identifier
            compatibility_data: Compatibility requirements and fixes

        Returns:
            True if cached successfully
        """
        cache_key = f"ats_compat:{ats_system}"
        return self.ml_cache_set(cache_key, compatibility_data)

    def ml_recall_ats_compatibility(self, ats_system: str) -> dict[str, Any] | None:
        """
        Recall cached ATS compatibility requirements.

        Args:
            ats_system: ATS system identifier

        Returns:
            Cached compatibility data or None
        """
        cache_key = f"ats_compat:{ats_system}"
        return self.ml_cache_get(cache_key)

    def ml_cache_section_balance(
        self,
        job_type: str,
        balance_data: dict[str, Any],
    ) -> bool:
        """
        Cache optimal section balance for a job type.

        Args:
            job_type: Job type identifier
            balance_data: Section balance recommendations

        Returns:
            True if cached successfully
        """
        cache_key = f"section_balance:{job_type}"
        return self.ml_cache_set(cache_key, balance_data)

    def ml_recall_section_balance(self, job_type: str) -> dict[str, Any] | None:
        """
        Recall cached section balance recommendations.

        Args:
            job_type: Job type identifier

        Returns:
            Cached balance data or None
        """
        cache_key = f"section_balance:{job_type}"
        return self.ml_cache_get(cache_key)
