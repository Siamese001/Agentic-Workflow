"""Hardened Anthropic Executor - Military-Grade Reliability.

Provides robust execution for Anthropic Claude API with:
- Circuit breaker for fault tolerance
- Exponential backoff retry logic
- Pre-flight token budget validation
- Structured telemetry logging
- Rate limit handling

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import logging
import os
from dataclasses import dataclass

from agentic_core.L6_observability.utils.system_telemetry_util import SystemTelemetry
from agentic_core.mixins.hardening_mixin import HardeningMixin, TokenLimitError
from apps_rg.utils.agent_executor import AgentMessage, AgentResponse

logger = logging.getLogger(__name__)


@dataclass
class HardenedAnthropicConfig:
    """configuration for HardenedAnthropicExecutor."""

    # Model context limits (tokens)
    MODEL_LIMITS = {
        "claude-3-5-sonnet-20241022": 200000,
        "claude-3-5-haiku-20241022": 200000,
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
    }

    # guardian: allow-magic-config
    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        # guardian: allow-magic-config
        max_tokens: int = 4096,
        # guardian: allow-magic-config
        timeout_s: int = 60,
        # guardian: allow-magic-config
        max_retries: int = 3,
        # guardian: allow-magic-config
        failure_threshold: int = 5,
        # guardian: allow-magic-config
        reset_timeout_s: int = 30,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s

    @property
    def max_context_tokens(self) -> int:
        """Get maximum context tokens for the model."""
        return self.MODEL_LIMITS.get(self.model, 200000)


class HardenedAnthropicExecutor(HardeningMixin):
    """Military-grade executor for Anthropic Claude API.

    Wraps the Anthropic client with circuit breaking, retries,
    token validation, and structured telemetry.
    """

    def __init__(
        self,
        config: HardenedAnthropicConfig | None = None,
        telemetry: SystemTelemetry | None = None,
    ):
        """Initialize hardened Anthropic executor.

        Args:
            config: Optional configuration
            telemetry: Optional telemetry instance
        """
        self.config = config or HardenedAnthropicConfig()

        # Initialize hardening mixin
        super().__init__(
            component_name="anthropic_executor",
            failure_threshold=self.config.failure_threshold,
            reset_timeout_s=self.config.reset_timeout_s,
            max_retries=self.config.max_retries,
            telemetry=telemetry,
        )

        # Initialize Anthropic client
        self._client = None
        self._setup_client()

    def _setup_client(self) -> None:
        """Setup Anthropic client."""
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic") from exc

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable must be set")

        self._client = anthropic.Anthropic(
            api_key=api_key,
            timeout=self.config.timeout_s,
        )

    def _validate_token_budget(self, prompt: str) -> None:
        """Validate token budget before API call.

        Anthropic doesn't provide official tokenization, so we use
        a conservative estimate based on character count.

        Args:
            prompt: Input prompt text

        Raises:
            TokenLimitError: If prompt exceeds model limits
        """
        # Conservative estimate: ~4 chars per token for Claude
        estimated_tokens = len(prompt) // 4

        # Reserve space for max_tokens in response
        available_tokens = self.config.max_context_tokens - self.config.max_tokens

        if estimated_tokens > available_tokens:
            raise TokenLimitError(
                f"Prompt estimated at {estimated_tokens} tokens exceeds available budget "
                f"({available_tokens} tokens for {self.config.model})",
            )

    def _build_messages(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None = None,
    ) -> tuple[list[dict[str, str]], str | None]:
        """Build Anthropic message format.

        Args:
            messages: Agent messages
            system_prompt: Optional system prompt

        Returns:
            Tuple of (messages, system_prompt) for Anthropic API
        """
        # Anthropic uses system_prompt parameter separately
        anthropic_messages = []

        # Add user/assistant messages
        for msg in messages:
            anthropic_messages.append({"role": msg.role, "content": msg.content})

        return anthropic_messages, system_prompt

    async def run_llm(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
    ) -> str:
        """Run Anthropic completion with hardening.

        Args:
            prompt: Input prompt (used if messages not provided)
            temperature: Sampling temperature override
            max_tokens: Max tokens override
            system_prompt: Optional system prompt
            messages: Alternative to prompt - list of messages

        Returns:
            Generated text response
        """
        # Use messages or build single message from prompt
        if messages:
            anthropic_messages, sys_prompt = self._build_messages(messages, system_prompt)
            combined_prompt = "\n".join(msg.content for msg in messages)
        else:
            anthropic_messages = [{"role": "user", "content": prompt}]
            sys_prompt = system_prompt
            combined_prompt = prompt

        # Define async operation
        async def _completion():
            response = self._client.messages.create(
                model=self.config.model,
                messages=anthropic_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                system=sys_prompt,
            )

            # Extract content
            if response.content:
                return response.content[0].text
            return ""

        # Execute with hardening
        return await self.execute_hardened(
            operation="messages_create",
            fn=_completion,
            validate_token_budget=lambda: self._validate_token_budget(combined_prompt),
            metadata={
                "model": self.config.model,
                "temperature": temperature or self.config.temperature,
                "max_tokens": max_tokens or self.config.max_tokens,
                "has_system_prompt": bool(sys_prompt),
            },
        )

    async def run_llm_with_response(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
    ) -> AgentResponse:
        """Run Anthropic completion with full response metadata.

        Args:
            prompt: Input prompt (used if messages not provided)
            temperature: Sampling temperature override
            max_tokens: Max tokens override
            system_prompt: Optional system prompt
            messages: Alternative to prompt - list of messages

        Returns:
            AgentResponse with content and metadata
        """
        # Use messages or build single message from prompt
        if messages:
            anthropic_messages, sys_prompt = self._build_messages(messages, system_prompt)
            combined_prompt = "\n".join(msg.content for msg in messages)
        else:
            anthropic_messages = [{"role": "user", "content": prompt}]
            sys_prompt = system_prompt
            combined_prompt = prompt

        # Define async operation with response capture
        async def _completion():
            response = self._client.messages.create(
                model=self.config.model,
                messages=anthropic_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                system=sys_prompt,
            )
            return response

        # Execute with hardening
        raw_response = await self.execute_hardened(
            operation="messages_create",
            fn=_completion,
            validate_token_budget=lambda: self._validate_token_budget(combined_prompt),
            metadata={
                "model": self.config.model,
                "temperature": temperature or self.config.temperature,
                "max_tokens": max_tokens or self.config.max_tokens,
                "has_system_prompt": bool(sys_prompt),
            },
        )

        # Extract response data
        content = ""
        usage = None

        if raw_response.content:
            content = raw_response.content[0].text

        if hasattr(raw_response, "usage"):
            usage = {
                "prompt_tokens": raw_response.usage.input_tokens,
                "completion_tokens": raw_response.usage.output_tokens,
                "total_tokens": raw_response.usage.input_tokens + raw_response.usage.output_tokens,
            }

        return AgentResponse(
            content=content,
            model=self.config.model,
            usage=usage,
            finish_reason=raw_response.stop_reason if raw_response else None,
        )

    def run_llm_sync(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
    ) -> str:
        """Synchronous version of run_llm.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature override
            max_tokens: Max tokens override
            system_prompt: Optional system prompt
            messages: Alternative to prompt - list of messages

        Returns:
            Generated text response
        """
        import asyncio

        # Run async method in event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in event loop, use run_in_executor
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self.run_llm(
                        prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_prompt,
                        messages=messages,
                    ),
                )
                return future.result()
        else:
            return asyncio.run(
                self.run_llm(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                    messages=messages,
                ),
            )


# Factory function for backward compatibility
def create_hardened_anthropic_executor(
    model: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.7,
    **kwargs,
) -> HardenedAnthropicExecutor:
    """Create a hardened Anthropic executor.

    Args:
        model: Anthropic model name
        temperature: Sampling temperature
        **kwargs: Additional configuration parameters

    Returns:
        HardenedAnthropicExecutor instance
    """
    config = HardenedAnthropicConfig(model=model, temperature=temperature, **kwargs)
    return HardenedAnthropicExecutor(config)
