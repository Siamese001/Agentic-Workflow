"""
Real Healing Provider Adapters — Minimal SDK Wrappers for L2.3 Healing Tier.

These adapters perform real SDK calls but are designed to be mocked in tests.
They implement the HealingProviderInvoker Protocol with actual provider logic.

Production usage: instantiate directly with real clients.
Testing: mock the underlying SDK methods; assert adapter selection and arguments.
"""

from __future__ import annotations

import logging

# Imports are lazy to avoid dependency issues in environments without SDKs
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Qwen/vLLM Adapter — wraps OpenAI-compatible client
# ---------------------------------------------------------------------------


class QwenInvokerAdapter:
    """Real Qwen/vLLM provider adapter using OpenAI-compatible client.

    Makes actual HTTP calls to vLLM endpoint in production.
    In tests, mock the client.chat.completions.create call.
    """

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        """Initialize Qwen adapter with vLLM endpoint.

        Args:
            base_url: vLLM server URL (e.g. "http://localhost:8000/v1").
            api_key: Optional API key for vLLM server.
        """
        if OpenAI is None:
            raise ImportError("openai package required for QwenInvokerAdapter")
        self.client = OpenAI(base_url=base_url, api_key=api_key or "dummy")

    def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke Qwen model for healing task.

        Args:
            healing_input: Structured failure context.
            decision: Router decision (includes confidence).
            config: Healing tier configuration.
            agent_name: Calling agent name for trace.

        Returns:
            InvocationRecord with actual model response metadata.
        """
        # Build structured prompt from healing context
        prompt = self._build_prompt(healing_input, decision, agent_name)

        try:
            response = self.client.chat.completions.create(
                model=config.model_qwen_vllm_id,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code healing assistant. Fix the reported issue with minimal, precise changes.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=2048,  # guardian: allow-magic_configuration
            )

            usage = response.usage

            logger.info(
                "Qwen healing invoked",
                extra={
                    "model": config.model_qwen_vllm_id,
                    "agent": agent_name,
                    "trace_id": healing_input.trace_id,
                    "input_tokens": usage.prompt_tokens if usage else None,
                    "output_tokens": usage.completion_tokens if usage else None,
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

        except Exception as exc:
            logger.error(
                "Qwen healing failed",
                extra={
                    "model": config.model_qwen_vllm_id,
                    "agent": agent_name,
                    "trace_id": healing_input.trace_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
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

    def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Local agent not supported by Qwen adapter."""
        raise NotImplementedError("invoke_local not supported by QwenInvokerAdapter")

    def invoke_gemini(
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
    """Real Gemini 2.5 Pro provider adapter using Google GenAI SDK.

    Makes actual API calls to Google Gemini in production.
    In tests, mock the genai.GenerativeModel call.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize Gemini adapter with API key.

        Args:
            api_key: Google AI API key for Gemini access.
        """
        if genai is None:
            raise ImportError("google-generativeai package required for GeminiInvokerAdapter")
        genai.configure(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"  # Will be overridden in invoke

    def invoke_gemini(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke Gemini model for healing task.

        Args:
            healing_input: Structured failure context.
            decision: Router decision (includes confidence).
            config: Healing tier configuration.
            agent_name: Calling agent name for trace.

        Returns:
            InvocationRecord with actual model response metadata.
        """
        # Build structured prompt from healing context
        prompt = self._build_prompt(healing_input, decision, agent_name)

        try:
            model = genai.GenerativeModel(config.model_gemini_2_5_pro_id)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=2048,  # guardian: allow-magic_configuration
                ),
            )

            logger.info(
                "Gemini healing invoked",
                extra={
                    "model": config.model_gemini_2_5_pro_id,
                    "agent": agent_name,
                    "trace_id": healing_input.trace_id,
                    "response_text": response.text[:200] + "..."
                    if len(response.text) > 200
                    else response.text,
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

        except Exception as exc:
            logger.error(
                "Gemini healing failed",
                extra={
                    "model": config.model_gemini_2_5_pro_id,
                    "agent": agent_name,
                    "trace_id": healing_input.trace_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
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

    def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Local agent not supported by Gemini adapter."""
        raise NotImplementedError("invoke_local not supported by GeminiInvokerAdapter")

    def invoke_qwen_vllm(
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
    """Local agent adapter for simple, deterministic healing without LLM calls.

    Used for high-confidence, low-complexity fixes.
    """

    def invoke_local(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Invoke local agent for healing.

        Args:
            healing_input: Structured failure context.
            decision: Router decision (includes confidence).
            config: Healing tier configuration.
            agent_name: Calling agent name for trace.

        Returns:
            InvocationRecord for local healing.
        """
        logger.info(
            "Local healing invoked",
            extra={
                "agent": agent_name,
                "trace_id": healing_input.trace_id,
                "confidence": decision.heal_confidence,
                "failure_type": healing_input.failure_type,
            },
        )

        # Local agent would implement deterministic fix logic here
        # For now, just record the invocation
        return InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
        )

    def invoke_qwen_vllm(
        self,
        healing_input: HealingInput,
        decision: HealingDecision,
        config: HealingTierConfig,
        *,
        agent_name: str = "",
    ) -> InvocationRecord:
        """Qwen not supported by local adapter."""
        raise NotImplementedError("invoke_qwen_vllm not supported by LocalAgentAdapter")

    def invoke_gemini(
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
