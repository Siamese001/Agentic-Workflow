"""
L2 Execution Agent Wrappers - Wave 3

Provides L2ExecutionAgent-compliant wrappers for existing agents
without breaking existing functionality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.contracts.l2_execution_contract import (
    L2ExecutionAgent,
    L2ExecutionContext,
    L2ExecutionPhase,
    L2PhaseResult,
)
from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
    EmbeddingSovereignAgent as _EmbeddingSovereignAgent,
)


@dataclass
class L2EmbeddingSovereignAgent(L2ExecutionAgent):
    """
    L2ExecutionAgent-compliant wrapper for EmbeddingSovereignAgent.

    Implements 4-phase contract while delegating to singleton gateway.
    """

    agent_id: str = "L2EmbeddingSovereignAgent"
    _gateway: _EmbeddingSovereignAgent | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize the wrapped gateway."""
        super().__init__(agent_id=self.agent_id)
        self._gateway = _EmbeddingSovereignAgent()

    # ========================================================================
    # L2.1: INIT - Pre-commit setup
    # ========================================================================
    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Initialize embedding operation context."""
        content = context.inputs.get("content")
        provider = context.inputs.get("provider", "bge-m3")

        if not isinstance(content, str) or not content.strip():
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                metadata={"error": "Missing or invalid content"},
            )

        return L2PhaseResult(
            phase=L2ExecutionPhase.INIT,
            success=True,
            metadata={
                "provider": provider,
                "content_length": len(content),
            },
        )

    # ========================================================================
    # L2.2: EXECUTE - Core embedding operation
    # ========================================================================
    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Execute embedding generation."""
        import asyncio

        content = context.inputs.get("content")
        provider = context.inputs.get("provider", "bge-m3")
        use_cache = context.inputs.get("use_cache", True)

        if not self._gateway:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                metadata={"error": "Gateway not initialized"},
            )

        try:
            # Run async embedding in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            embedding = loop.run_until_complete(
                self._gateway.get_embedding(content, provider, use_cache)
            )
            loop.close()

            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=True,
                output=embedding,
                metadata={
                    "provider": provider,
                    "dimensions": len(embedding) if embedding else 0,
                },
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                metadata={
                    "error": type(e).__name__,
                    "detail": str(e),
                    "recoverable": True,
                },
            )

    # ========================================================================
    # L2.3: EVALUATE/HEAL - Error recovery
    # ========================================================================
    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Evaluate and retry on failure."""
        last_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not last_result or last_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=True,
                metadata={"heal_skipped": "execute_success"},
            )

        metadata = last_result.metadata or {}
        if not metadata.get("recoverable", False):
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=False,
                metadata={"heal_skipped": "not_recoverable"},
            )

        # Retry with fallback provider
        context.retry_count += 1
        current_provider = context.inputs.get("provider", "bge-m3")
        fallback_providers = ["bge-m3", "gemini", "openai"]
        fallback = next(
            (p for p in fallback_providers if p != current_provider),
            "bge-m3"
        )
        context.inputs["provider"] = fallback

        retry_result = self.l2_execute(context)

        return L2PhaseResult(
            phase=L2ExecutionPhase.EVALUATE_HEAL,
            success=retry_result.success,
            output=retry_result.output,
            metadata={
                "heal_attempted": True,
                "fallback_provider": fallback,
                "retry_count": context.retry_count,
            },
        )

    # ========================================================================
    # L2.4: SYNTHESIZE - Result packaging
    # ========================================================================
    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Package embedding result."""
        execute_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not execute_result:
            return L2PhaseResult(
                phase=L2ExecutionPhase.SYNTHESIZE,
                success=False,
                metadata={"error": "No execute phase result"},
            )

        if not execute_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.SYNTHESIZE,
                success=False,
                output=None,
                metadata={"status": "failed"},
            )

        embedding = execute_result.output
        return L2PhaseResult(
            phase=L2ExecutionPhase.SYNTHESIZE,
            success=True,
            output=embedding,
            metadata={
                "status": "success",
                "dimensions": len(embedding) if embedding else 0,
            },
        )

    # ========================================================================
    # Convenience API
    # ========================================================================
    def get_embedding(
        self, content: str, provider: str = "bge-m3", use_cache: bool = True
    ) -> list[float] | None:
        """Synchronous wrapper for embedding generation."""
        result = self.run_l2_phases(
            inputs={"content": content, "provider": provider, "use_cache": use_cache},
            heal_enabled=True,
        )

        if result.get("success"):
            synth = result.get("phase_results", {}).get("SYNTHESIZE", {})
            return synth.get("output")
        return None
