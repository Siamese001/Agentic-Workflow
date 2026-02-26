"""
Real Healing Provider Adapters — Minimal SDK Wrappers for L2.3 Healing Tier.

These adapters perform real SDK calls but are designed to be mocked in tests.
They implement the HealingProviderInvoker Protocol with actual provider logic.

Production usage: instantiate directly with real clients.
Testing: mock the underlying SDK methods; assert adapter selection and arguments.
"""

from __future__ import annotations

import logging

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import GenerationRequest, get_llm_gateway
from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)

logger = logging.getLogger(__name__)


class OOMRetryableError(Exception):
    """Raised when OOM occurs but retry is possible through router escalation."""

    pass


class OOMEscalatedError(Exception):
    """Raised when OOM has been escalated to another tier."""

    pass


# Module-level constants for token limits
# guardian: allow-magic-config
DEFAULT_MAX_TOKENS = 2048
# guardian: allow-magic-config
DEFAULT_MAX_OUTPUT_TOKENS = 2048


# ---------------------------------------------------------------------------
# Qwen/vLLM Adapter — wraps OpenAI-compatible client
# ---------------------------------------------------------------------------


class QwenInvokerAdapter:
    """Real Qwen/vLLM provider adapter using OpenAI-compatible client."""

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        """Initialize Qwen adapter with vLLM endpoint."""
        self.base_url = base_url
        self.api_key = api_key

    async def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke Qwen model for healing task."""
        prompt = self._build_prompt(healing_input, decision, agent_name)
        gateway = get_llm_gateway()
        request = GenerationRequest(
            prompt=prompt,
            agent_id="SovereignLLMGateway",
            model=config.model_qwen_vllm_id,
            provider="openai",
            temperature=0.0,
            max_tokens=DEFAULT_MAX_TOKENS,
        )

        try:
            response = await gateway.route_generation(request, base_url=self.base_url)
            logger.info(
                "Qwen healing invoked",
                extra={
                    "model": config.model_qwen_vllm_id,
                    "agent": agent_name,
                    "trace_id": healing_input.trace_id,
                    "output_tokens": response.tokens,
                },
            )
            return InvocationRecord(
                tier=HealingTier.QWEN_VLLM,
                model_id=config.model_qwen_vllm_id,
                agent_name=agent_name,
                trace_id=healing_input.trace_id,
                heal_confidence=decision.heal_confidence,
                method_called="invoke_qwen_vllm",
            )
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
    """Real Gemini 2.5 Pro provider adapter using Google GenAI SDK."""

    def __init__(self, api_key: str) -> None:
        """Initialize Gemini adapter with API key."""
        self.api_key = api_key

    async def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke Gemini model for healing task."""
        prompt = self._build_prompt(healing_input, decision, agent_name)
        gateway = get_llm_gateway()
        request = GenerationRequest(
            prompt=prompt,
            agent_id="SovereignLLMGateway",
            model=config.model_gemini_2_5_pro_id,
            provider="google",
            temperature=0.1,
            max_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
        )

        try:
            response = await gateway.route_generation(request)
            logger.info(
                "Gemini healing invoked",
                extra={
                    "model": config.model_gemini_2_5_pro_id,
                    "agent": agent_name,
                    "trace_id": healing_input.trace_id,
                    "response_text": response.content[:200] if response.content else "",
                },
            )
            return InvocationRecord(
                tier=HealingTier.GEMINI_2_5_PRO,
                model_id=config.model_gemini_2_5_pro_id,
                agent_name=agent_name,
                trace_id=healing_input.trace_id,
                heal_confidence=decision.heal_confidence,
                method_called="invoke_gemini",
            )
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
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke local agent for healing."""
        logger.info(
            "Local healing invoked",
            extra={
                "agent": agent_name,
                "trace_id": healing_input.trace_id,
                "confidence": decision.heal_confidence,
                "failure_type": healing_input.failure_type,
            },
        )

        return InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
        )

    async def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Qwen not supported by local adapter."""
        raise NotImplementedError("invoke_qwen_vllm not supported by LocalAgentAdapter")

    async def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Gemini not supported by local adapter."""
        raise NotImplementedError("invoke_gemini not supported by LocalAgentAdapter")


__all__ = [
    "QwenInvokerAdapter",
    "GeminiInvokerAdapter",
    "LocalAgentAdapter",
]
