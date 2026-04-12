"""
L2 Execution Agent Wrappers - Wave 3

Provides L2ExecutionAgent-compliant wrappers for existing agents
without breaking existing functionality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# Import underlying agents
from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
    EmbeddingSovereignAgent as _EmbeddingSovereignAgent,
)
from agentic_core.L2_execution.reasoning.RedisSovereignAgent import (
    RedisSovereignAgent as _RedisSovereignAgent,
)
from agentic_core.L2_execution.reasoning.SovereignMCPGatewayAgent import (
    SovereignMCPGateway as _SovereignMCPGatewayAgent,
)
from agentic_core.L2_execution.reasoning.StructuredEngineAgent import (
    StructuredEngineAgent as _StructuredEngineAgent,
)
from agentic_core.L2_execution.reasoning.SubAtomicRegistryAgent import (
    SubAtomicRegistryAgent as _SubAtomicRegistryAgent,
)
from agentic_core.L2_execution.types.l2_execution_contract import (
    L2ExecutionAgent,
    L2ExecutionContext,
    L2ExecutionPhase,
    L2PhaseResult,
)

# =============================================================================
# L2EmbeddingSovereignAgent
# =============================================================================


@dataclass
class L2EmbeddingSovereignAgent(L2ExecutionAgent):
    """L2ExecutionAgent-compliant wrapper for EmbeddingSovereignAgent."""

    agent_id: str = "L2EmbeddingSovereignAgent"
    _gateway: _EmbeddingSovereignAgent | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        super().__init__(agent_id=self.agent_id)
        self._gateway = _EmbeddingSovereignAgent()

    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Initialize embedding operation context.

        Validates content input and prepares for embedding generation.
        """
        try:
            content = context.inputs.get("content")
            if not isinstance(content, str) or not content.strip():
                return L2PhaseResult(
                    phase=L2ExecutionPhase.INIT,
                    success=False,
                    metadata={"error": "Missing or invalid content"},
                )
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=True,
                metadata={"content_length": len(content)},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                metadata={"error": f"INIT failed: {type(e).__name__}: {e}"},
            )

    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Execute embedding generation.

        Runs async embedding generation and handles exceptions.
        """
        import asyncio

        content = context.inputs.get("content")
        provider = context.inputs.get("provider", "bge-m3")

        if not self._gateway:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                metadata={"error": "Gateway not initialized"},
            )

        try:
            if not self._gateway:
                raise RuntimeError("Gateway not initialized")

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            embedding = loop.run_until_complete(
                self._gateway.get_embedding(content, provider),
            )
            loop.close()

            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=True,
                output=embedding,
                metadata={"dimensions": len(embedding) if embedding else 0},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                metadata={"error": f"Execute failed: {type(e).__name__}: {e}"},
            )

    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        """
        Evaluate execution result and apply healing if needed.

        If the previous execution failed, attempt to heal by retrying with a fallback provider.

        Args:
            context (L2ExecutionContext): The execution context.

        Returns:
            L2PhaseResult: The result of the evaluation and healing phase.
        """
        last_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not last_result or last_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=True,
                metadata={"heal_skipped": "execute_success"},
            )

        try:
            context.retry_count += 1
            fallback = "bge-m3" if context.inputs.get("provider") != "bge-m3" else "gemini"
            context.inputs["provider"] = fallback
            retry_result = self.l2_execute(context)

            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=retry_result.success,
                output=retry_result.output,
                metadata={"heal_attempted": True, "fallback_provider": fallback},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=False,
                metadata={"error": f"Heal failed: {type(e).__name__}: {e}"},
            )

    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        """
        Synthesize the final result.

        If the execution was successful, return the output. Otherwise, return an error.

        Args:
            context (L2ExecutionContext): The execution context.

        Returns:
            L2PhaseResult: The final result of the synthesis phase.
        """
        execute_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not execute_result or not execute_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.SYNTHESIZE,
                success=False,
                metadata={"status": "failed"},
            )

        return L2PhaseResult(
            phase=L2ExecutionPhase.SYNTHESIZE,
            success=True,
            output=execute_result.output,
            metadata={"status": "success"},
        )


# =============================================================================
# L2RedisSovereignAgent
# =============================================================================


@dataclass
class L2RedisSovereignAgent(L2ExecutionAgent):
    """L2ExecutionAgent-compliant wrapper for RedisSovereignAgent."""

    agent_id: str = "L2RedisSovereignAgent"
    _agent: _RedisSovereignAgent | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        super().__init__(agent_id=self.agent_id)
        self._agent = _RedisSovereignAgent(project_root=Path("."))

    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Initialize Redis operation context.

        Validates operation type and prepares for cache operations.
        """
        try:
            operation = context.inputs.get("operation")
            if operation not in ["get", "set", "delete", "exists"]:
                return L2PhaseResult(
                    phase=L2ExecutionPhase.INIT,
                    success=False,
                    metadata={"error": f"Invalid operation: {operation}"},
                )
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=True,
                metadata={"operation": operation},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                metadata={"error": f"INIT failed: {type(e).__name__}: {e}"},
            )

    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        operation = context.inputs.get("operation")
        key = context.inputs.get("key")
        value = context.inputs.get("value")

        try:
            if not self._agent:
                raise RuntimeError("Agent not initialized")

            result = None
            if operation == "get":
                result = self._agent.get(key)
            elif operation == "set":
                result = self._agent.set(key, value)
            elif operation == "delete":
                result = self._agent.delete(key)
            elif operation == "exists":
                result = self._agent.exists(key)

            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=True,
                output=result,
                metadata={"operation": operation},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                metadata={"error": type(e).__name__, "recoverable": True},
            )

    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        last_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not last_result or last_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=True,
                metadata={"heal_skipped": "execute_success"},
            )

        context.retry_count += 1
        retry_result = self.l2_execute(context)

        return L2PhaseResult(
            phase=L2ExecutionPhase.EVALUATE_HEAL,
            success=retry_result.success,
            output=retry_result.output,
            metadata={"heal_attempted": True, "retry_count": context.retry_count},
        )

    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        execute_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        return L2PhaseResult(
            phase=L2ExecutionPhase.SYNTHESIZE,
            success=execute_result.success if execute_result else False,
            output=execute_result.output if execute_result else None,
            metadata={"status": "success" if execute_result and execute_result.success else "failed"},
        )


# =============================================================================
# L2SovereignMCPGatewayAgent
# =============================================================================


@dataclass
class L2SovereignMCPGatewayAgent(L2ExecutionAgent):
    """L2ExecutionAgent-compliant wrapper for SovereignMCPGatewayAgent."""

    agent_id: str = "L2SovereignMCPGatewayAgent"
    _agent: _SovereignMCPGatewayAgent | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        super().__init__(agent_id=self.agent_id)
        self._agent = _SovereignMCPGatewayAgent()

    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Initialize MCP gateway operation context.

        Validates tool_name input and prepares for MCP tool invocation.
        """
        try:
            tool_name = context.inputs.get("tool_name")
            if not tool_name:
                return L2PhaseResult(
                    phase=L2ExecutionPhase.INIT,
                    success=False,
                    metadata={"error": "Missing tool_name"},
                )
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=True,
                metadata={"tool_name": tool_name},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                metadata={"error": f"INIT failed: {type(e).__name__}: {e}"},
            )

    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Execute MCP tool invocation.

        Invokes the specified tool with given parameters.
        """
        tool_name = context.inputs.get("tool_name")
        params = context.inputs.get("params", {})

        try:
            if not self._agent:
                raise RuntimeError("Agent not initialized")

            result = self._agent.invoke_tool(tool_name, params)

            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=True,
                output=result,
                metadata={"tool_name": tool_name},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                metadata={"error": type(e).__name__, "recoverable": True},
            )

    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        last_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not last_result or last_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=True,
                metadata={"heal_skipped": "execute_success"},
            )

        context.retry_count += 1
        retry_result = self.l2_execute(context)

        return L2PhaseResult(
            phase=L2ExecutionPhase.EVALUATE_HEAL,
            success=retry_result.success,
            output=retry_result.output,
            metadata={"heal_attempted": True, "retry_count": context.retry_count},
        )

    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        execute_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        return L2PhaseResult(
            phase=L2ExecutionPhase.SYNTHESIZE,
            success=execute_result.success if execute_result else False,
            output=execute_result.output if execute_result else None,
            metadata={"status": "success" if execute_result and execute_result.success else "failed"},
        )


# =============================================================================
# L2StructuredEngineAgent
# =============================================================================


@dataclass
class L2StructuredEngineAgent(L2ExecutionAgent):
    """L2ExecutionAgent-compliant wrapper for StructuredEngineAgent."""

    agent_id: str = "L2StructuredEngineAgent"
    _agent: _StructuredEngineAgent | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        super().__init__(agent_id=self.agent_id)
        self._agent = _StructuredEngineAgent()

    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Initialize structured engine operation context.

        Validates intent input for processing.
        """
        try:
            intent = context.inputs.get("intent")
            if not intent:
                return L2PhaseResult(
                    phase=L2ExecutionPhase.INIT,
                    success=False,
                    metadata={"error": "Missing intent"},
                )
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=True,
                metadata={"intent_type": type(intent).__name__},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                metadata={"error": f"INIT failed: {type(e).__name__}: {e}"},
            )

    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        intent = context.inputs.get("intent")

        try:
            if not self._agent:
                raise RuntimeError("Agent not initialized")

            result = self._agent.process_intent(intent)

            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=True,
                output=result,
                metadata={},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                metadata={"error": type(e).__name__, "recoverable": True},
            )

    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        last_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not last_result or last_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=True,
                metadata={"heal_skipped": "execute_success"},
            )

        context.retry_count += 1
        retry_result = self.l2_execute(context)

        return L2PhaseResult(
            phase=L2ExecutionPhase.EVALUATE_HEAL,
            success=retry_result.success,
            output=retry_result.output,
            metadata={"heal_attempted": True, "retry_count": context.retry_count},
        )

    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        execute_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        return L2PhaseResult(
            phase=L2ExecutionPhase.SYNTHESIZE,
            success=execute_result.success if execute_result else False,
            output=execute_result.output if execute_result else None,
            metadata={"status": "success" if execute_result and execute_result.success else "failed"},
        )


# =============================================================================
# L2SubAtomicRegistryAgent
# =============================================================================


@dataclass
class L2SubAtomicRegistryAgent(L2ExecutionAgent):
    """L2ExecutionAgent-compliant wrapper for SubAtomicRegistryAgent."""

    agent_id: str = "L2SubAtomicRegistryAgent"
    _agent: _SubAtomicRegistryAgent | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        super().__init__(agent_id=self.agent_id)
        self._agent = _SubAtomicRegistryAgent()

    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        """Initialize registry operation context.

        Validates registry operation type and prepares for execution.
        """
        try:
            registry_operation = context.inputs.get("registry_operation")
            if registry_operation not in ["register", "lookup", "unregister"]:
                return L2PhaseResult(
                    phase=L2ExecutionPhase.INIT,
                    success=False,
                    metadata={"error": f"Invalid operation: {registry_operation}"},
                )
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=True,
                metadata={"operation": registry_operation},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.INIT,
                success=False,
                metadata={"error": f"INIT failed: {type(e).__name__}: {e}"},
            )

    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        operation = context.inputs.get("registry_operation")
        component_id = context.inputs.get("component_id")
        component_data = context.inputs.get("component_data")

        try:
            if not self._agent:
                raise RuntimeError("Agent not initialized")

            result = None
            if operation == "register":
                result = self._agent.register(component_id, component_data)
            elif operation == "lookup":
                result = self._agent.lookup(component_id)
            elif operation == "unregister":
                result = self._agent.unregister(component_id)

            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=True,
                output=result,
                metadata={"operation": operation},
            )
        except Exception as e:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EXECUTE,
                success=False,
                metadata={"error": type(e).__name__, "recoverable": True},
            )

    def l2_evaluate_and_heal(self, context: L2ExecutionContext) -> L2PhaseResult:
        last_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        if not last_result or last_result.success:
            return L2PhaseResult(
                phase=L2ExecutionPhase.EVALUATE_HEAL,
                success=True,
                metadata={"heal_skipped": "execute_success"},
            )

        context.retry_count += 1
        retry_result = self.l2_execute(context)

        return L2PhaseResult(
            phase=L2ExecutionPhase.EVALUATE_HEAL,
            success=retry_result.success,
            output=retry_result.output,
            metadata={"heal_attempted": True, "retry_count": context.retry_count},
        )

    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        execute_result = context.phase_results.get(L2ExecutionPhase.EXECUTE)
        return L2PhaseResult(
            phase=L2ExecutionPhase.SYNTHESIZE,
            success=execute_result.success if execute_result else False,
            output=execute_result.output if execute_result else None,
            metadata={"status": "success" if execute_result and execute_result.success else "failed"},
        )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "L2EmbeddingSovereignAgent",
    "L2RedisSovereignAgent",
    "L2SovereignMCPGatewayAgent",
    "L2StructuredEngineAgent",
    "L2SubAtomicRegistryAgent",
]
