"""
GatewayFactory - Unified Gateway Access via Composition

Phase 2 MRO Refactoring: Provides dependency injection alternative to mixin inheritance.

Instead of:
    class MyAgent(LLMProviderMixin, EmbeddingMixin, SovereignBaseAgent):
        pass

Use:
    class MyAgent(SovereignBaseAgent):
        def __post_init__(self):
            super().__post_init__()
            self.gateways = GatewayFactory.create_all()
            # or
            self.llm = GatewayFactory.get_llm_gateway()

Benefits:
- Reduces MRO depth by ~4 classes
- Explicit dependency declaration
- Easier testing with mock gateways
- Clear separation of concerns
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Type aliases
LLMProvider = Literal["openai", "anthropic", "google"]
EmbeddingProvider = Literal["gemini", "openai", "bge-m3"]


@dataclass
class GatewayBundle:
    """Bundle of all gateway instances for composition."""

    llm: Any = None
    embedding: Any = None
    validator: Any = None
    healing: Any = None

    def __post_init__(self):
        """Initialize with lazy loading markers."""
        self._llm_loaded = self.llm is not None
        self._embedding_loaded = self.embedding is not None
        self._validator_loaded = self.validator is not None
        self._healing_loaded = self.healing is not None


class GatewayFactory:
    """
    Factory for creating gateway instances via composition.

    Phase 2 MRO Refactoring: Use this instead of inheriting gateway mixins.
    """

    # Singleton instances
    _llm_gateway: Any = None
    _embedding_gateway: Any = None
    _validator_orchestrator: Any = None
    _healing_orchestrator: Any = None

    @classmethod
    def get_llm_gateway(cls) -> Any:
        """Get or create LLM gateway singleton."""
        if cls._llm_gateway is None:
            try:
                from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
                    get_llm_gateway,
                )

                cls._llm_gateway = get_llm_gateway()
            except ImportError:
                # Stub for testing or when gateway not available
                cls._llm_gateway = _StubLLMGateway()
        return cls._llm_gateway

    @classmethod
    def get_embedding_gateway(cls) -> Any:
        """Get or create embedding gateway singleton."""
        if cls._embedding_gateway is None:
            try:
                from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
                    get_embedding_gateway,
                )

                cls._embedding_gateway = get_embedding_gateway()
            except ImportError:
                # Stub for testing or when gateway not available
                cls._embedding_gateway = _StubEmbeddingGateway()
        return cls._embedding_gateway

    @classmethod
    def get_validator_orchestrator(cls) -> Any:
        """Get or create validator orchestrator singleton."""
        if cls._validator_orchestrator is None:
            try:
                from agentic_core.L5_safety.types.healing_orchestration_types import (
                    get_validator_orchestrator,
                )

                cls._validator_orchestrator = get_validator_orchestrator()
            except ImportError:
                # Stub for testing or when orchestrator not available
                cls._validator_orchestrator = _StubValidatorOrchestrator()
        return cls._validator_orchestrator

    @classmethod
    def get_healing_orchestrator(cls) -> Any:
        """Get or create healing orchestrator singleton."""
        if cls._healing_orchestrator is None:
            try:
                from agentic_core.L5_safety.types.healing_orchestration_types import (
                    get_healing_orchestrator,
                )

                cls._healing_orchestrator = get_healing_orchestrator()
            except ImportError:
                # Stub for testing or when orchestrator not available
                cls._healing_orchestrator = _StubHealingOrchestrator()
        return cls._healing_orchestrator

    @classmethod
    def create_all(cls) -> GatewayBundle:
        """Create bundle with all gateways."""
        return GatewayBundle(
            llm=cls.get_llm_gateway(),
            embedding=cls.get_embedding_gateway(),
            validator=cls.get_validator_orchestrator(),
            healing=cls.get_healing_orchestrator(),
        )

    @classmethod
    def create_minimal(cls) -> GatewayBundle:
        """Create bundle with only LLM gateway (most common use case)."""
        return GatewayBundle(llm=cls.get_llm_gateway())

    @classmethod
    def reset_all(cls) -> None:
        """Reset all singleton instances (useful for testing)."""
        cls._llm_gateway = None
        cls._embedding_gateway = None
        cls._validator_orchestrator = None
        cls._healing_orchestrator = None


# Stub implementations for testing and fallback
class _StubLLMGateway:
    """Stub LLM gateway for testing."""

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        provider: LLMProvider = "openai",
        **kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "content": f"[Stub response for: {prompt[:50]}...]",
            "model": model or "stub-model",
            "provider": provider,
            "stub": True,
        }


class _StubEmbeddingGateway:
    """Stub embedding gateway for testing."""

    async def get_embedding(
        self,
        content: str,
        provider: EmbeddingProvider = "bge-m3",
        use_cache: bool = True,
    ) -> list[float]:
        return [0.0] * 1024

    async def get_embeddings_batch(
        self,
        contents: list[str],
        provider: EmbeddingProvider = "bge-m3",
    ) -> list[list[float]]:
        return [[0.0] * 1024 for _ in contents]


class _StubValidatorOrchestrator:
    """Stub validator orchestrator for testing."""

    async def validate(self, content: Any, validator_name: str, context: dict | None = None) -> dict:
        return {
            "valid": True,
            "validator": validator_name,
            "stub": True,
        }


class _StubHealingOrchestrator:
    """Stub healing orchestrator for testing."""

    async def heal(self, violation: dict, context: dict | None = None) -> dict:
        return {
            "healed": True,
            "violation": violation,
            "stub": True,
        }


__all__ = [
    "GatewayFactory",
    "GatewayBundle",
    "LLMProvider",
    "EmbeddingProvider",
]
