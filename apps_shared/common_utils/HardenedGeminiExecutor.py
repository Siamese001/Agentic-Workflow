"""Hardened Gemini Executor - Titanium Grade Robustness.

Military-grade reliability for Google GenAI v1beta with:
- Fault tolerance with tenacity retry
- Circuit breaker for sustained failures
- Pre-flight token governance
- Safety settings override
- Structured observability
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .agent_executor import AgentExecutor, AgentMessage
from .multi_provider_clients import Provider

logger = logging.getLogger(__name__)


# Custom Exceptions
class ContextOverflowError(Exception):
    """Raised when input exceeds context window safety threshold."""

    pass


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open due to sustained failures."""

    pass


class HardenedGeminiConfig:
    """configuration for HardenedGeminiExecutor."""

    # Model context limits (tokens)
    MODEL_LIMITS = {
        "gemini-2.5-flash": 1048576,  # 1M tokens
        "gemini-3-pro-preview": 2097152,  # 2M tokens
    }

    # Safety threshold (80% of limit)
    SAFETY_THRESHOLD_RATIO = 0.8

    def __init__(
        self,
        model: str = "gemini-3-pro-preview",
        temperature: float = 0.3,
        max_output_tokens: int = 8192,
        safety_threshold_ratio: float | None = None,
        max_retries: int = 5,
        retry_min_wait: float = 2.0,
        retry_max_wait: float = 30.0,
    ):
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.safety_threshold_ratio = safety_threshold_ratio or self.SAFETY_THRESHOLD_RATIO
        self.max_retries = max_retries
        self.retry_min_wait = retry_min_wait
        self.retry_max_wait = retry_max_wait

    @property
    def max_context_tokens(self) -> int:
        """Get maximum context tokens for the model."""
        return self.MODEL_LIMITS.get(self.model, 1048576)

    @property
    def safety_threshold_tokens(self) -> int:
        """Get safety threshold tokens."""
        return int(self.max_context_tokens * self.safety_threshold_ratio)


@dataclass
class InteractionTelemetry:
    """Telemetry data for interaction logging."""

    interaction_id: str | None
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    error: str | None = None


@dataclass
class CircuitBreakerState:
    """State tracking for circuit breaker."""

    failure_count: int = 0
    last_failure_time: float | None = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __post_init__(self):
        if self.state not in ["CLOSED", "OPEN", "HALF_OPEN"]:
            raise ValueError(f"Invalid circuit breaker state: {self.state}")


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures during sustained outages."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds to wait before trying half-open
            half_open_max_calls: Max calls in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.state = CircuitBreakerState()
        self.half_open_calls = 0

    def call_allowed(self) -> bool:
        """Check if a call is allowed through the circuit breaker."""
        now = time.time()

        if self.state.state == "CLOSED":
            return True
        elif self.state.state == "OPEN":
            # Check if recovery timeout has passed
            if now - self.state.last_failure_time >= self.recovery_timeout:
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state.state = "HALF_OPEN"
                self.half_open_calls = 0
                return True
            return False
        else:  # HALF_OPEN
            # Allow limited calls in half-open state
            return self.half_open_calls < self.half_open_max_calls

    def record_success(self):
        """Record a successful call."""
        if self.state.state == "HALF_OPEN":
            self.half_open_calls += 1
            # If we've had enough successes, close the circuit
            if self.half_open_calls >= self.half_open_max_calls:
                logger.info("Circuit breaker closing after successful recovery")
                self.state.state = "CLOSED"
                self.state.failure_count = 0
                self.half_open_calls = 0
        elif self.state.state == "CLOSED":
            # Reset failure count on success
            self.state.failure_count = 0

    def record_failure(self):
        """Record a failed call."""
        self.state.failure_count += 1
        self.state.last_failure_time = time.time()

        if self.state.state == "HALF_OPEN":
            # Immediate re-open if failure in half-open
            logger.warning("Circuit breaker re-opening after failure in HALF_OPEN")
            self.state.state = "OPEN"
            self.half_open_calls = 0
        elif self.state.state == "CLOSED":
            # Open if threshold reached
            if self.state.failure_count >= self.failure_threshold:
                logger.error(f"Circuit breaker opening after {self.state.failure_count} failures")
                self.state.state = "OPEN"

    def raise_if_open(self):
        """Raise exception if circuit breaker is open."""
        if self.state.state == "OPEN":
            raise CircuitBreakerOpenError(
                f"Circuit breaker is open. {self.failure_threshold} failures occurred. "
                f"Retry after {self.recovery_timeout} seconds."
            )


@dataclass
class InteractionTelemetry:
    """Telemetry data for interaction logging."""

    interaction_id: str | None
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    error: str | None = None


class HardenedGeminiExecutor:
    """Military-grade executor for Google GenAI v1beta."""

    def __init__(self, config: HardenedGeminiConfig | None = None):
        """Initialize hardened executor.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or HardenedGeminiConfig()
        self._client = None
        self._setup_client()
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=60.0, half_open_max_calls=3
        )

    def _setup_client(self):
        """Setup Google GenAI client."""
        from .multi_provider_clients import get_client

        try:
            self._client = get_client(Provider.GOOGLE)
            if not hasattr(self._client, "interactions"):
                raise ImportError("google-genai v1beta not available")
        except Exception as e:
            logger.error(f"Failed to initialize hardened Gemini client: {e}")
            raise

    def build_safety_config(self) -> list[dict[str, str]]:
        """Build safety settings for Risk/Insurance domain.

        Returns:
            List of safety setting dictionaries.
        """
        # Try to import types from google.genai, fallback to dict format
        try:
            from google.genai import SourceDocument

            return [
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_NONE",  # Allow robust professional critique
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_MEDIUM_AND_ABOVE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_MEDIUM_AND_ABOVE"
                ),
            ]
        except ImportError:
            # Fallback for legacy or different API
            return [
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ]

    async def validate_context_budget(self, input_payload: list[dict[str, Any]]) -> int:
        """Pre-flight check to ensure payload doesn't exceed context limit.

        Args:
            input_payload: List of messages to send

        Returns:
            Number of tokens in the payload

        Raises:
            ContextOverflowError: If payload exceeds safety threshold
        """
        try:
            # Try v1beta count_tokens API
            if hasattr(self._client, "models"):
                token_resp = await self._client.aio.models.count_tokens(
                    model=self.config.model, contents=input_payload
                )
                token_count = token_resp.total_tokens
            else:
                # Fallback: estimate using tiktoken or simple heuristic
                token_count = self._estimate_tokens(input_payload)

        except Exception as e:
            logger.warning(f"Token counting failed, estimating: {e}")
            token_count = self._estimate_tokens(input_payload)

        # Check against safety threshold
        if token_count > self.config.safety_threshold_tokens:
            raise ContextOverflowError(
                f"Payload {token_count} tokens exceeds safety threshold "
                f"({self.config.safety_threshold_tokens} tokens for {self.config.model})"
            )

        return token_count

    def _estimate_tokens(self, input_payload: list[dict[str, Any]]) -> int:
        """Fallback token estimation using simple heuristic.

        Args:
            input_payload: List of messages

        Returns:
            Estimated token count
        """
        total_chars = sum(len(str(msg.get("content", ""))) for msg in input_payload)
        # Rough estimate: ~4 chars per token
        return total_chars // 4

    def _build_payload(
        self, messages: list[AgentMessage], system_prompt: str | None = None
    ) -> list[dict[str, Any]]:
        """Build payload for interactions.create.

        Args:
            messages: List of agent messages
            system_prompt: Optional system prompt

        Returns:
            Formatted payload for API
        """
        payload = []

        # Add system prompt as first user message with model acknowledgment
        if system_prompt:
            payload.append({"role": "user", "content": system_prompt})
            payload.append({"role": "model", "content": "Understood. I am ready."})

        # Add messages
        for msg in messages:
            payload.append({"role": msg.role, "content": msg.content})

        return payload

    async def _execute_with_retry(
        self,
        model: str,
        config: dict[str, Any],
        input_payload: list[dict[str, Any]],
        previous_interaction_id: str | None = None,
    ) -> Any:
        """Execute with exponential backoff retry and circuit breaker.

        Args:
            model: Model name
            config: Generation config
            input_payload: Input messages
            previous_interaction_id: For stateful continuation

        Returns:
            API response
        """
        # Check circuit breaker first
        self._circuit_breaker.raise_if_open()

        # Import errors based on available SDK
        try:
            from google.genai import errors

            retry_exception = errors.ClientError
        except ImportError:
            # Fallback to generic exception
            retry_exception = Exception

        @retry(
            retry=retry_if_exception_type(retry_exception),
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(
                multiplier=1, min=self.config.retry_min_wait, max=self.config.retry_max_wait
            ),
            before_sleep=lambda _: logger.warning("Retrying due to rate limit or server error"),
        )
        async def _execute():
            request_params = {"model": model, "input": input_payload, "config": config}

            if previous_interaction_id:
                request_params["previous_interaction_id"] = previous_interaction_id

            # Try async API first, fallback to sync
            if hasattr(self._client, "aio"):
                return await self._client.aio.interactions.create(**request_params)
            else:
                # Wrap sync call in executor to avoid blocking
                import asyncio

                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, lambda: self._client.interactions.create(**request_params)
                )

        try:
            result = await _execute()
            self._circuit_breaker.record_success()
            return result
        except Exception:
            self._circuit_breaker.record_failure()
            raise

    async def log_interaction_telemetry(self, telemetry: InteractionTelemetry):
        """Log structured telemetry for observability.

        Args:
            telemetry: Telemetry data to log
        """
        log_data = {
            "event": "llm_interaction_complete",
            "interaction_id": telemetry.interaction_id,
            "model": telemetry.model,
            "input_tokens": telemetry.input_tokens,
            "output_tokens": telemetry.output_tokens,
            "total_tokens": telemetry.total_tokens,
            "latency_ms": telemetry.latency_ms,
            "timestamp": telemetry.timestamp,
        }

        if telemetry.error:
            log_data["error"] = telemetry.error

        logger.info(log_data)

    async def execute_k_node(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None = None,
        response_schema: dict[str, Any] | None = None,
        previous_interaction_id: str | None = None,
    ) -> str:
        """Execute K-Node with hardened reliability.

        Args:
            messages: Input messages
            system_prompt: Optional system prompt
            response_schema: JSON schema for structured output
            previous_interaction_id: For stateful continuation

        Returns:
            Generated text response
        """
        start_time = time.time()

        try:
            # 1. Build Config (Typed + Safety + JSON)
            config = {
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_output_tokens,
                "safety_settings": self.build_safety_config(),
            }

            # Add JSON schema if provided
            if response_schema:
                config["response_mime_type"] = "application/json"
                config["response_schema"] = response_schema

            # 2. Construct Payload
            payload = self._build_payload(messages, system_prompt)

            # 3. Pre-Flight Check
            input_tokens = await self.validate_context_budget(payload)

            # 4. Execute with Retry
            response = self._execute_with_retry(
                self.config.model, config, payload, previous_interaction_id
            )

            # 5. Extract response
            content = ""
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    content = candidate.content.parts[0].text if candidate.content.parts else ""

            # 6. Calculate telemetry
            latency_ms = (time.time() - start_time) * 1000

            # Extract usage if available
            output_tokens = 0
            if hasattr(response, "usage_metadata"):
                output_tokens = response.usage_metadata.candidates_token_count
            else:
                # Estimate output tokens
                output_tokens = len(content) // 4

            # 7. Log telemetry
            telemetry = InteractionTelemetry(
                interaction_id=getattr(response, "id", None),
                model=self.config.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                latency_ms=latency_ms,
            )

            await self.log_interaction_telemetry(telemetry)

            return content

        except Exception as e:
            # Log error telemetry
            latency_ms = (time.time() - start_time) * 1000
            telemetry = InteractionTelemetry(
                interaction_id=None,
                model=self.config.model,
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                latency_ms=latency_ms,
                error=str(e),
            )

            await self.log_interaction_telemetry(telemetry)
            raise

    def execute_sync(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None = None,
        response_schema: dict[str, Any] | None = None,
        previous_interaction_id: str | None = None,
    ) -> str:
        """Synchronous version of execute_k_node.

        Args:
            messages: Input messages
            system_prompt: Optional system prompt
            response_schema: JSON schema for structured output
            previous_interaction_id: For stateful continuation

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
                    self.execute_k_node(
                        messages, system_prompt, response_schema, previous_interaction_id
                    ),
                )
                return future.result()
        else:
            return asyncio.run(
                self.execute_k_node(
                    messages, system_prompt, response_schema, previous_interaction_id
                )
            )


# Factory function for backward compatibility
def create_hardened_gemini_executor(
    model: str = "gemini-3-pro-preview", temperature: float = 0.3, **kwargs
) -> HardenedGeminiExecutor:
    """Create a hardened Gemini executor.

    Args:
        model: Model name
        temperature: Sampling temperature
        **kwargs: Additional config parameters

    Returns:
        HardenedGeminiExecutor instance
    """
    config = HardenedGeminiConfig(model=model, temperature=temperature, **kwargs)
    return HardenedGeminiExecutor(config)


# Integration with existing AgentExecutor
def create_agent_executor(
    provider: Provider = Provider.OPENAI,
    model: str | None = None,
    temperature: float = 0.7,
    hardened: bool = False,
    **kwargs,
) -> AgentExecutor | HardenedGeminiExecutor:
    """Factory function to create agent executor with optional hardening.

    Args:
        provider: LLM provider
        model: Optional model name
        temperature: Sampling temperature
        hardened: Use hardened executor for Google provider
        **kwargs: Additional configuration parameters

    Returns:
        AgentExecutor or HardenedGeminiExecutor instance
    """
    if provider == Provider.GOOGLE and hardened:
        return create_hardened_gemini_executor(
            model=model or "gemini-3-pro-preview", temperature=temperature, **kwargs
        )

    # Use standard executor for other providers
    from .agent_executor import AgentConfig

    config = AgentConfig(
        provider=provider,
        model=model,
        temperature=temperature,
        **kwargs,
    )

    return AgentExecutor(config)
