"""
SovereignBaseAgent - Sovereign Single Source of Truth (SSOT) Root.

Provides foundational capabilities for agents with sovereign authority.

PHASE 9 MIGRATION (Jan 2026):
- Global Injection of Phase 4-6 Architectures.
- Native capabilities: Config, LLM, Embedding, Healing, Validation.
- Resolves "Opt-In" drift by enforcing capabilities at the root.

L0 DNA FLATTENING:
infrastructure_mixin consolidates core capabilities (legacy).
New Mixins provide Gateway access (modern).

MRO HARDENING:
- This is the ROOT of the agent hierarchy
- infrastructure_mixin is injected HERE so all agents get full infrastructure
- Layer bases add specialized mixins BEFORE SovereignBaseAgent
- MRO Flow: Specialized -> Layer -> SovereignBaseAgent -> [Mixins] -> object
"""

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.utils.core_extensions.infrastructure_mixin import infrastructure_mixin

# [PHASE 9] Global Architecture Injection
from agentic_core.config.config_mixin import ConfigMixin
from agentic_core.L2_execution.mcp.llm_provider_mixin import LLMProviderMixin
from agentic_core.L2_execution.mcp.embedding_mixin import EmbeddingMixin
from agentic_core.L5_safety.validators.healing_strategy_mixin import HealingStrategyMixin
from agentic_core.L5_safety.validators.validator_mixin import ValidatorMixin

logger = logging.getLogger(__name__)


@dataclass
class SovereignBaseAgent(
    infrastructure_mixin,
    ConfigMixin,
    LLMProviderMixin,
    EmbeddingMixin,
    HealingStrategyMixin,
    ValidatorMixin,
):
    """
    Sovereign Single Source of Truth (SSOT) Root.

    Inheritance Chain (Phase 21.1 - Hierarchy Normalization):
    1. RedisCacheMixin (Direct Redis access - cache_get, cache_set)
    2. PineconeVectorMixin (Direct Pinecone access - vector_search)
    3. infrastructure_mixin (Legacy Safety/MCP)
    4. ConfigMixin (Phase 6 - Typed Configuration)
    5. LLMProviderMixin (Phase 4 - SovereignLLMGateway)
    6. EmbeddingMixin (Phase 4 - EmbeddingSovereignAgent)
    7. HealingStrategyMixin (Phase 5 - HealingOrchestrator)
    8. ValidatorMixin (Phase 5 - ValidatorOrchestrator)

    This ensures EVERY agent in the hierarchy has:
    - self.cache_get() / self.cache_set() (Redis capabilities)
    - self.vector_search() (Pinecone capabilities)
    - self.config (Typed Env Vars)
    - self.llm_generate() (Audited LLM calls)
    - self.get_embedding() (Cached Embeddings)
    - self.orchestrator_heal() (Strategy Dispatch)
    - self.orchestrator_validate() (Central Validation)
    """

    name: str = "SovereignAgent"

    def __post_init__(self) -> None:
        """
        Initialize sovereign agent with infrastructure.

        Triggers infrastructure_mixin gatekeeper logic via super().__init__().

        MRO AUDITOR: Sets _sovereign_initialized sentinel for propagation verification.
        """
        # 1. Cooperative super() call - triggers infrastructure_mixin.__init__()
        super().__init__()

        # 2. Set Sentinel for MRO Auditor - verifies initialization chain reached root
        self._sovereign_initialized = True

        # 3. Core sovereign initialization logic
        self._initialize_sovereign_state()

    def _initialize_sovereign_state(self) -> Any:
        """Initialize sovereign-specific state."""
        self._state: dict[str, Any] = {}
        self._authority_level = "standard"
        # Config is now provided by ConfigMixin via self.config property

    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function."""
        raise NotImplementedError("Subclasses must implement execute()")

    def get_state(self, key: str) -> Any | None:
        """Get state value."""
        return self._state.get(key)

    def set_state(self, key: str, value: Any) -> None:
        """Set state value."""
        self._state[key] = value

    def get_authority_level(self) -> str:
        """Get the agent's authority level."""
        return self._authority_level

    def elevate_authority(self, level: str) -> None:
        """Elevate the agent's authority level."""
        self._authority_level = level
        logger.info(f"Authority elevated to: {level}")

    def log_info(self, message: str) -> None:
        """Log an info message."""
        logger.info(f"[{self.name}] {message}")

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        logger.warning(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        logger.error(f"[{self.name}] {message}")

    def log_feedback(
        self, workflow_id: str, action: str, status: str, details: dict[str, Any] = None
    ) -> None:
        """Log feedback for a workflow action."""
        logger.info(f"[{self.name}] Workflow {workflow_id}: {action} - {status} - {details or {}}")

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """
        Base heal_repository implementation - ROOT termination point.

        MRO HARDENING: This is the END of the heal_repository chain.
        Subclasses should call super().heal_repository(**kwargs) which eventually
        reaches here and terminates cleanly.

        Args:
            **kwargs: Absorbs any additional keyword arguments from subclasses
        """
        # TERMINATION POINT: We absorb signals here to prevent MRO overflow into
        # InfrastructureMixins that lack healing logic.
        return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 1}


__all__ = ["SovereignBaseAgent"]
