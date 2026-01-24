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
from dataclasses import dataclass, field
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
    4. ConfigMixin (Phase 6 - Typed configuration)
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

    MRO SAFETY (Jan 2026):
    - Pre-declares _state and _call_path BEFORE super().__init__() to prevent
      Mixin AttributeErrors when they access root state during initialization.
    - Delegates heal_repository entirely to HealerMixin via MRO resolution.
    """

    name: str = "SovereignAgent"

    # Defensive: Pre-declare state containers to prevent Mixin AttributeErrors
    # These are initialized as dataclass fields so they exist BEFORE __post_init__
    _state: dict[str, Any] = field(default_factory=dict)
    _call_path: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """
        Initialize sovereign agent with infrastructure.

        Triggers infrastructure_mixin gatekeeper logic via super().__init__().

        MRO AUDITOR: Sets _sovereign_initialized sentinel for propagation verification.

        CRITICAL FIX (Jan 2026): Initialize root state BEFORE propagating to Mixins.
        If Mixins (e.g. ConfigMixin) need to read self._state during their init,
        it must exist now. The dataclass fields provide the initial containers,
        but we ensure they're properly set up before super() call.
        """
        # Guard against double initialization
        if getattr(self, "_sovereign_initialized", False):
            return

        # 1. CRITICAL FIX: Initialize root state BEFORE propagating to Mixins
        self._initialize_sovereign_state()
        self._sovereign_initialized = True

        # 2. Cooperative super() call - triggers infrastructure_mixin.__init__()
        # Mixins can now safely access self._state during their initialization
        super().__init__()

    def _initialize_sovereign_state(self) -> None:
        """Initialize sovereign-specific state."""
        # Idempotent state setup - _state already exists from dataclass field
        if not self._state:
            self._state = {"status": "booting", "health": "nominal"}
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

    # REFACTOR (Jan 2026): Removed raw dict return implementation.
    # SovereignBaseAgent delegates healing entirely to HealingStrategyMixin/HealerMixin.
    # Overriding it here with a "termination point" that returns a dict
    # broke the Liskov Substitution Principle against HealerMixin's HealResult.
    #
    # The proper termination logic now resides in HealerMixin.heal_repository()
    # which handles depth limiting, cycle detection, and returns HealResult.
    # Removing this shadowing method allows proper MRO resolution to HealerMixin.


__all__ = ["SovereignBaseAgent"]
