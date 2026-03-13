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
from typing import Any

try:
    from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

    _TENACITY_AVAILABLE = True
except ImportError:
    _TENACITY_AVAILABLE = False
from agentic_core.L2_execution.healers.healing_tier_router import HISTORICAL_DATA_HASH, _compute_replay_key
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
    InvocationRecord,
)

logger = logging.getLogger(__name__)


class OOMRetryableError(Exception):
    """Raised when OOM occurs but retry is possible through router escalation."""

    pass


class OOMEscalatedError(Exception):
    """Raised when OOM has been escalated to another tier."""

    pass


MAX_TOKENS = 2048
MAX_OUTPUT_TOKENS = 2048
DEFAULT_MAX_TOKENS = MAX_TOKENS
DEFAULT_MAX_OUTPUT_TOKENS = MAX_OUTPUT_TOKENS
QWEN_CONFIG: dict[str, Any] = {
    "temperature": 0.0,
    "max_tokens": MAX_TOKENS,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}
GEMINI_CONFIG: dict[str, Any] = {
    "temperature": 0.1,
    "max_tokens": MAX_OUTPUT_TOKENS,
    "top_p": 1.0,
    "top_k": 40,
}
QWEN_CONFIG_HASH = hashlib.sha256(
    "|".join((f"{k}={v}" for k, v in sorted(QWEN_CONFIG.items()))).encode()
).hexdigest()[:16]
GEMINI_CONFIG_HASH = hashlib.sha256(
    "|".join((f"{k}={v}" for k, v in sorted(GEMINI_CONFIG.items()))).encode()
).hexdigest()[:16]


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

    def invoke_qwen_vllm(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Invoke Qwen model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig providing model IDs
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """
        model_id = config.model_qwen_vllm_id
        prompt = self._build_prompt(healing_input, decision, agent_name)
        try:
            import openai

            client = openai.OpenAI(base_url=self.base_url, api_key=self.api_key)
        except (ImportError, AttributeError) as exc:
            raise ImportError(
                "OpenAI SDK is required for Qwen vLLM adapter. Install with: pip install openai"
            ) from exc
        response_text: str | None = None
        if _TENACITY_AVAILABLE:

            @retry(
                retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                reraise=True,
            )
            def _call_vllm():
                return client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "You are a code healing assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=QWEN_CONFIG["temperature"],
                    max_tokens=DEFAULT_MAX_TOKENS,
                )

            completion = _call_vllm()
        else:
            completion = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are a code healing assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=QWEN_CONFIG["temperature"],
                max_tokens=DEFAULT_MAX_TOKENS,
            )
        if completion and completion.choices:
            response_text = completion.choices[0].message.content
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
            response_text=response_text,
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
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Local agent not supported by Qwen adapter."""
        raise NotImplementedError("invoke_local not supported by QwenInvokerAdapter")

    def invoke_gemini(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Gemini not supported by Qwen adapter."""
        raise NotImplementedError("invoke_gemini not supported by QwenInvokerAdapter")


class GeminiInvokerAdapter:
    """Gemini 2.5 Pro provider adapter with explicit configuration - no environment access."""

    def __init__(self, api_key: str) -> None:
        """Initialize Gemini adapter with explicit configuration.

        Args:
            api_key: Google API key (explicit, no environment variable)
        """
        self.api_key = api_key
        self._config_hash = GEMINI_CONFIG_HASH

    def invoke_gemini(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Invoke Gemini model with deterministic configuration.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig providing model IDs
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """
        from apps_shared.types.hardened_gemini_executor_types import (
            HardenedGeminiConfig,
            HardenedGeminiExecutor,
        )

        model_id = config.model_gemini_2_5_pro_id
        prompt = self._build_prompt(healing_input, decision, agent_name)
        hardened_config = HardenedGeminiConfig(
            model=model_id,
            temperature=GEMINI_CONFIG["temperature"],
            max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
        )
        executor = HardenedGeminiExecutor(config=hardened_config)
        response_text: str | None = None
        try:
            result = executor.invoke_prompt(prompt, api_key=self.api_key)
            if result is not None:
                try:
                    response_text = result.text
                # guardian: allow-silent-swallow
                except Exception:
                    response_text = None
        # guardian: allow-silent-swallow
        except Exception as _exc:
            _exc_name = type(_exc).__name__
            if "ContextOverflow" in _exc_name:
                logger.warning(
                    "Gemini context overflow — response_text=None",
                    extra={"model": model_id, "trace_id": healing_input.trace_id},
                )
            elif "CircuitBreakerOpen" in _exc_name:
                logger.warning(
                    "Gemini circuit breaker open — response_text=None",
                    extra={"model": model_id, "trace_id": healing_input.trace_id},
                )
            else:
                logger.error(
                    "Gemini invocation failed: %s",
                    _exc,
                    extra={"model": model_id, "trace_id": healing_input.trace_id},
                )
            response_text = None
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
            response_text=response_text,
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
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Local agent not supported by Gemini adapter."""
        raise NotImplementedError("invoke_local not supported by GeminiInvokerAdapter")

    def invoke_qwen_vllm(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Qwen not supported by Gemini adapter."""
        raise NotImplementedError("invoke_qwen_vllm not supported by GeminiInvokerAdapter")


class LocalAgentAdapter:
    """Local agent adapter for simple, deterministic healing without LLM calls."""

    def invoke_local(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Invoke local agent with deterministic record.

        Args:
            healing_input: Structured failure context
            decision: Routing decision from tier router
            config: HealingTierConfig (unused for local agent)
            agent_name: Agent making the request

        Returns:
            InvocationRecord with replay-deterministic fields
        """
        record = InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
            provider_config_hash="local",
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

    def invoke_qwen_vllm(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
    ) -> InvocationRecord:
        """Qwen not supported by local adapter."""
        raise NotImplementedError("invoke_qwen_vllm not supported by LocalAgentAdapter")

    def invoke_gemini(
        self, healing_input: HealingInput, decision: HealingDecision, config: Any, *, agent_name: str = ""
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
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_MAX_OUTPUT_TOKENS",
]
