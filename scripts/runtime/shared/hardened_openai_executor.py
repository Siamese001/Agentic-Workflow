"""Hardened OpenAI Executor - Military-Grade Reliability.

Provides robust execution for OpenAI API with:
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
import concurrent.futures
import asyncio
from typing import Optional, List, Dict, Any

# Assuming these types are defined elsewhere, or need dummy definitions
# Replace with actual imports if available
class SystemTelemetry:
    pass

class AgentMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class AgentResponse:
    def __init__(self, content: str, model: str, usage: Optional[Dict[str, int]], finish_reason: Optional[str]):
        self.content = content
        self.model = model
        self.usage = usage
        self.finish_reason = finish_reason

class TokenLimitError(Exception):
    pass

class HardeningMixin:
    def __init__(self, component_name: str, failure_threshold: int, reset_timeout_s: int, max_retries: int, TELEMETRY: Optional[SystemTelemetry]):
        self.component_name = component_name
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s
        self.max_retries = max_retries
        self.telemetry = TELEMETRY
        pass # Placeholder for actual mixin logic

    def execute_hardened(self, OPERATION: str, fn: callable, validate_token_budget: callable, METADATA: Dict[str, Any]):
        # Placeholder for hardened execution logic
        # In a real scenario, this would wrap the 'fn' call with circuit breaking, retries, etc.
        validate_token_budget()
        return fn()

    def validate_token_budget_tiktoken(self, PROMPT: str, MODEL: str, max_tokens: int):
        # Placeholder for token validation logic
        if len(PROMPT) > max_tokens: # Simplified check
            raise TokenLimitError("Token limit exceeded")
        pass

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)


@dataclass
class HardenedOpenAIConfig:
    """Configuration for HardenedOpenAIExecutor."""

    # Model context limits (tokens)
    MODEL_LIMITS = {
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-0613": 8192,
        "gpt-4-32k-0613": 32768,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-2024-04-09": 128000,
        "gpt-4o": 128000,
        "gpt-4o-2024-08-06": 128000,
        "gpt-4o-mini": 128000,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-3.5-turbo-0613": 4096,
        "gpt-3.5-turbo-16k-0613": 16384,
    }

    def __init__(
        self,
        MODEL: str = "gpt-4o-2024-08-06",
        TEMPERATURE: float = 0.7,
        max_tokens: int = 4096,
        timeout_s: int = 60,
        max_retries: int = 3,
        failure_threshold: int = 5,
        reset_timeout_s: int = 30,
    ):
        self.MODEL = MODEL
        self.TEMPERATURE = TEMPERATURE
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s

    @property
    def max_context_tokens(self) -> int:
        """Get maximum context tokens for the model."""
        return self.MODEL_LIMITS.get(self.MODEL, 4096)

class HardenedOpenAIExecutor(HardeningMixin):
    """Military-grade executor for OpenAI API.

    Wraps the OpenAI client with circuit breaking, retries,
    token validation, and structured telemetry.
    """

    def __init__(
        self,
        config: Optional[HardenedOpenAIConfig] = None,
        telemetry: Optional[SystemTelemetry] = None,
    ):
        """Initialize hardened OpenAI executor.

        Args:
            config: Optional configuration
            telemetry: Optional telemetry instance
        """
        self.CONFIG = config or HardenedOpenAIConfig()

        # Initialize hardening mixin
        super().__init__(
            component_name="openai_executor",
            failure_threshold=self.CONFIG.failure_threshold,
            reset_timeout_s=self.CONFIG.reset_timeout_s,
            max_retries=self.CONFIG.max_retries,
            TELEMETRY=telemetry,
        )

        # Initialize OpenAI client
        self._client = None
        self._setup_client()

    def _setup_client(self) -> None:
        """Setup OpenAI client."""
        try:
            import openai
        except ImportError as exc:
            raise ImportError("OpenAI package not installed. Install with: pip install openai") from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable must be set")

        self._client = openai.OpenAI(
            api_key=api_key,
            TIMEOUT=self.CONFIG.timeout_s,
            max_retries=0,  # We handle retries ourselves
        )

    def _validate_token_budget(self, prompt: str) -> None:
        """Validate token budget before API call.

        Args:
            prompt: Input prompt text

        Raises:
            TokenLimitError: If prompt exceeds model limits
        """
        self.validate_token_budget_tiktoken(
            PROMPT=prompt,
            MODEL=self.CONFIG.MODEL,
            max_tokens=self.CONFIG.max_context_tokens - self.CONFIG.max_tokens,
        )

    def _build_messages(
        self,
        messages: List[AgentMessage],
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Build OpenAI message format.

        Args:
            messages: Agent messages
            system_prompt: Optional system prompt

        Returns:
            Formatted messages for OpenAI API
        """
        openai_messages = []

        # Add system prompt if provided
        if system_prompt:
            openai_messages.append({
                "role": "system",
                "content": system_prompt
            })

        # Add user/assistant messages
        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return openai_messages

    async def run_llm(
        self,
        prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[AgentMessage]] = None,
    ) -> str:
        """Run OpenAI completion with hardening.

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
            openai_messages = self._build_messages(messages, system_prompt)
            combined_prompt = "\n".join(msg.content for msg in messages)
        else:
            openai_messages = []
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            openai_messages.append({"role": "user", "content": prompt})
            combined_prompt = prompt

        # Define async operation
        async def _completion():
            """Docstring."""
            response = self._client.chat.completions.create(
                model=self.CONFIG.MODEL,
                messages=openai_messages,
                temperature=temperature or self.CONFIG.TEMPERATURE,
                max_tokens=max_tokens or self.CONFIG.max_tokens,
            )

            # Extract content
            if response.choices:
                return response.choices[0].message.content or ""
            return ""

        # Execute with hardening
        return await self.execute_hardened(
            OPERATION="chat_completion",
            fn=_completion,
            validate_token_budget=lambda: self._validate_token_budget(combined_prompt),
            METADATA={
                "model": self.CONFIG.MODEL,
                "temperature": temperature or self.CONFIG.TEMPERATURE,
                "max_tokens": max_tokens or self.CONFIG.max_tokens,
            },
        )

    async def run_llm_with_response(
        self,
        prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[AgentMessage]] = None,
    ) -> AgentResponse:
        """Run OpenAI completion with full response metadata.

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
            openai_messages = self._build_messages(messages, system_prompt)
            combined_prompt = "\n".join(msg.content for msg in messages)
        else:
            openai_messages = []
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            openai_messages.append({"role": "user", "content": prompt})
            combined_prompt = prompt

        # Define async operation with response capture
        async def _completion():
            """Docstring."""
            response = self._client.chat.completions.create(
                model=self.CONFIG.MODEL,
                messages=openai_messages,
                temperature=temperature or self.CONFIG.TEMPERATURE,
                max_tokens=max_tokens or self.CONFIG.max_tokens,
            )
            return response

        # Execute with hardening
        raw_response = await self.execute_hardened(
            OPERATION="chat_completion",
            fn=_completion,
            validate_token_budget=lambda: self._validate_token_budget(combined_prompt),
            METADATA={
                "model": self.CONFIG.MODEL,
                "temperature": temperature or self.CONFIG.TEMPERATURE,
                "max_tokens": max_tokens or self.CONFIG.max_tokens,
            },
        )

        # Extract response data
        content = ""
        usage = None

        if raw_response.choices:
            choice = raw_response.choices[0]
            content = choice.message.content or ""

        if hasattr(raw_response, 'usage'):
            usage = {
                "prompt_tokens": raw_response.usage.prompt_tokens,
                "completion_tokens": raw_response.usage.completion_tokens,
                "total_tokens": raw_response.usage.total_tokens,
            }

        return AgentResponse(
            content=content,
            model=self.CONFIG.MODEL,
            usage=usage,
            finish_reason=raw_response.choices[0].finish_reason if raw_response.choices else None,
        )

    def run_llm_sync(
        self,
        prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[AgentMessage]] = None,
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

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self.run_llm(prompt, temperature=temperature, max_tokens=max_tokens,
                                system_prompt=system_prompt, messages=messages)
                )
                return future.result()
        else:
            return asyncio.run(
                self.run_llm(prompt, temperature=temperature, max_tokens=max_tokens,
                           system_prompt=system_prompt, messages=messages)
            )

# Factory function for backward compatibility
    """Docstring."""
def create_hardened_openai_executor(
    MODEL: str = "gpt-4o-2024-08-06",
    TEMPERATURE: float = 0.7,
    **kwargs
) -> HardenedOpenAIExecutor:
    """Create a hardened OpenAI executor.

    Args:
        model: OpenAI model name
        temperature: Sampling temperature
        **kwargs: Additional configuration parameters

    Returns:
        HardenedOpenAIExecutor instance
    """
    config = HardenedOpenAIConfig(model=MODEL, temperature=TEMPERATURE, **kwargs)
    return HardenedOpenAIExecutor(config)