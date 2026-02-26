"""
Healing Provider Adapters — Environment-Independent, Replay-Deterministic.

These adapters implement the HealingProviderInvoker Protocol with:
- Explicit configuration injection (no environment variables)
- Provider configuration hashing for replay determinism
- Fixed token limits (no external config loading)
- Deterministic error handling
"""

from __future__ import annotations

import hashlib
import logging
from typing import Dict, Any

from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort
from agentic_core.agents.agent_registry import get_execution_profile
from agentic_core.L2_execution.healers.healing_tier_types import (
    InvocationRecord,
    HealingDecision,
    HealingInput,
    HealingTier,
)
from agentic_core.L2_execution.healers.healing_tier_router import HISTORICAL_DATA_HASH, _compute_replay_key

logger = logging.getLogger(__name__)


class OOMRetryableError(Exception):
    """Raised when OOM occurs but retry is possible through router escalation."""

    pass


class OOMEscalatedError(Exception):
    """Raised when OOM has been escalated to another tier."""

    pass


# ---------------------------------------------------------------------------
# Fixed constants - no environment access, no config loading
# ---------------------------------------------------------------------------

# Fixed token limits for mathematical determinism
MAX_TOKENS = 2048
MAX_OUTPUT_TOKENS = 2048

# Fixed provider configurations - compile-time frozen
QWEN_CONFIG: Dict[str, Any] = {
    "temperature": 0.0,
    "max_tokens": MAX_TOKENS,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}

GEMINI_CONFIG: Dict[str, Any] = {
    "temperature": 0.1,
    "max_tokens": MAX_OUTPUT_TOKENS,
    "top_p": 1.0,
    "top_k": 40,
}

# Pre-computed configuration hashes for replay determinism
QWEN_CONFIG_HASH = hashlib.sha256(
    '|'.join(f"{k}={v}" for k, v in sorted(QWEN_CONFIG.items())).encode()
).hexdigest()[:16]

GEMINI_CONFIG_HASH = hashlib.sha256(
    '|'.join(f"{k}={v}" for k, v in sorted(GEMINI_CONFIG.items())).encode()
).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Qwen/vLLM Adapter — wraps OpenAI-compatible client
# ---------------------------------------------------------------------------


class QwenInvokerAdapter:
    """Qwen/vLLM provider adapter with explicit configuration - no environment access."""

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        """Initialize Qwen adapter with explicit configuration.

        Args:
            base_url: vLLM endpoint URL (explicit, no environment variable)
            api_key: API key (explicit, no environment variable)
        """
        self.base_url = base_url
        self.api_key = api_key
        self._config_hash = QWEN_CONFIG_HASH

    async def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        model_id: str = "qwen-vllm",
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke Qwen model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            model_id: Model identifier (explicit, no config loading)
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """
        prompt = self._build_prompt(healing_input, decision, agent_name)
        gateway = get_llm_gateway()

        # Explicit configuration - no environment access
        request = GenerationRequest(
            prompt=prompt,
            agent_id="SovereignLLMGateway",
            model=model_id,
            provider="openai",
            **QWEN_CONFIG  # Unpack frozen config
        )

        try:
            response = await gateway.route_generation(request, base_url=self.base_url)

            # Create replay-deterministic record
            record = InvocationRecord(
                tier=HealingTier.QWEN_VLLM,
                model_id=model_id,
                agent_name=agent_name,
                trace_id=healing_input.trace_id,
                heal_confidence=decision.heal_confidence,
                method_called="invoke_qwen_vllm",
                provider_config_hash=self._config_hash,
                historical_data_hash=HISTORICAL_DATA_HASH,
                replay_key=_compute_replay_key(healing_input, decision),
            )

            logger.info(
                "Qwen healing invoked with deterministic config",
                extra={
                    "model": model_id,
                    "agent": agent_name,
                    "trace_id": healing_input.trace_id,
                    "config_hash": self._config_hash,
                    "replay_key": record.replay_key,
                },
            )

            return record

        except Exception:
            logger.error("Qwen healing failed", exc_info=True)
            raise

    def _build_prompt(self, healing_input: HealingInput, decision: HealingDecision, agent_name: str) -> str:
        """Build structured prompt from healing context."""
        parts = [
            f"Healing Request from {agent_name}",
            f"Failure Type: {healing_input.failure_type}",
            f"Error Signature: {healing_input.error_signature}",
            f"Retry Count: {healing_input.retry_count}",
            f"Blast Radius Estimate: {healing_input.blast_radius_estimate:.2f}",
        ]
        if healing_input.required_tools:
            parts.append(f"Required Tools: {', '.join(healing_input.required_tools)}")
        if healing_input.violation_metadata_refs:
            parts.append(f"Context Files: {', '.join(healing_input.violation_metadata_refs)}")
        parts.append(f"Router Confidence: {decision.heal_confidence:.2f}")
        parts.append(f"Reason Codes: {', '.join(decision.reason_codes)}")
        parts.append("\nPlease provide a minimal fix for this issue.")
        return "\n".join(parts)

    async def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Local agent not supported by Qwen adapter."""
        raise NotImplementedError("invoke_local not supported by QwenInvokerAdapter")

    async def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Gemini not supported by Qwen adapter."""
        raise NotImplementedError("invoke_gemini not supported by QwenInvokerAdapter")


# ---------------------------------------------------------------------------
# Gemini Adapter — wraps Google GenerativeAI SDK
# ---------------------------------------------------------------------------


class GeminiInvokerAdapter:
    """Gemini 2.5 Pro provider adapter with explicit configuration - no environment access."""

    def __init__(self, api_key: str) -> None:
        """Initialize Gemini adapter with explicit configuration.

        Args:
            api_key: Google API key (explicit, no environment variable)
        """
        self.api_key = api_key
        self._config_hash = GEMINI_CONFIG_HASH

    async def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        model_id: str = "gemini-2.5-pro",
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke Gemini model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            model_id: Model identifier (explicit, no config loading)
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """
        prompt = self._build_prompt(healing_input, decision, agent_name)
        gateway = get_llm_gateway()

        # Explicit configuration - no environment access
        request = GenerationRequest(
            prompt=prompt,
            agent_id="SovereignLLMGateway",
            model=model_id,
            provider="google",
            **GEMINI_CONFIG  # Unpack frozen config
        )

        try:
            response = await gateway.route_generation(request)

            # Create replay-deterministic record
            record = InvocationRecord(
                tier=HealingTier.GEMINI_2_5_PRO,
                model_id=model_id,
                agent_name=agent_name,
                trace_id=healing_input.trace_id,
                heal_confidence=decision.heal_confidence,
                method_called="invoke_gemini",
                provider_config_hash=self._config_hash,
                historical_data_hash=HISTORICAL_DATA_HASH,
                replay_key=_compute_replay_key(healing_input, decision),
            )

            logger.info(
                "Gemini healing invoked with deterministic config",
                extra={
                    "model": model_id,
                    "agent": agent_name,
                    "trace_id": healing_input.trace_id,
                    "config_hash": self._config_hash,
                    "replay_key": record.replay_key,
                },
            )

            return record

        except Exception:
            logger.error("Gemini healing failed", exc_info=True)
            raise

    def _build_prompt(self, healing_input: HealingInput, decision: HealingDecision, agent_name: str) -> str:
        """Build structured prompt from healing context."""
        parts = [
            f"Healing Request from {agent_name}",
            f"Failure Type: {healing_input.failure_type}",
            f"Error Signature: {healing_input.error_signature}",
            f"Retry Count: {healing_input.retry_count}",
            f"Blast Radius Estimate: {healing_input.blast_radius_estimate:.2f}",
        ]
        if healing_input.required_tools:
            parts.append(f"Required Tools: {', '.join(healing_input.required_tools)}")
        if healing_input.violation_metadata_refs:
            parts.append(f"Context Files: {', '.join(healing_input.violation_metadata_refs)}")
        parts.append(f"Router Confidence: {decision.heal_confidence:.2f}")
        parts.append(f"Reason Codes: {', '.join(decision.reason_codes)}")
        parts.append("\nPlease provide a minimal fix for this issue.")
        return "\n".join(parts)

    async def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Local agent not supported by Gemini adapter."""
        raise NotImplementedError("invoke_local not supported by GeminiInvokerAdapter")

    async def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Qwen not supported by Gemini adapter."""
        raise NotImplementedError("invoke_qwen_vllm not supported by GeminiInvokerAdapter")


# ---------------------------------------------------------------------------
# Local Agent Adapter — in-memory healing
# ---------------------------------------------------------------------------


class LocalAgentAdapter:
    """Local agent adapter for simple, deterministic healing without LLM calls."""

    async def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        model_id: str = "local",
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke local agent with deterministic record.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            model_id: Model identifier (defaults to "local")
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """
        # Create replay-deterministic record
        record = InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id=model_id,
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
            provider_config_hash="local",  # No config for local agent
            historical_data_hash=HISTORICAL_DATA_HASH,
            replay_key=_compute_replay_key(healing_input, decision),
        )

        logger.info(
            "Local healing invoked with deterministic record",
            extra={
                "agent": agent_name,
                "trace_id": healing_input.trace_id,
                "confidence": decision.heal_confidence,
                "failure_type": healing_input.failure_type,
                "replay_key": record.replay_key,
            },
        )

        return record

    async def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        model_id: str = "qwen-vllm",
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Qwen not supported by local adapter."""
        raise NotImplementedError("invoke_qwen_vllm not supported by LocalAgentAdapter")

    async def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        model_id: str = "gemini-2.5-pro",
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Gemini not supported by local adapter."""
        raise NotImplementedError("invoke_gemini not supported by LocalAgentAdapter")


__all__ = [
    "QwenInvokerAdapter",
    "GeminiInvokerAdapter",
    "LocalAgentAdapter",
    "QWEN_CONFIG_HASH",
    "GEMINI_CONFIG_HASH",
    "MAX_TOKENS",
    "MAX_OUTPUT_TOKENS",
]
