"""Async model clients for the v10.7 runtime."""

from __future__ import annotations

import asyncio
import logging
import os
import random
from typing import Any, Dict, List, Optional

from mcp import get_tool

from .config import ConfigV10_7
from .exceptions import ModelAPIError
from .services import (
    CacheManager,
    ContextBudgetManager,
    CostTracker,
    MetricsCollector,
    track_metrics,
)

# -------------------------------------------------------------------
# Optional provider SDKs
# -------------------------------------------------------------------

# Anthropic: prefer AsyncAnthropic, fallback to legacy anthropic.Client
_AsyncAnthropic = None
_AnthropicSyncClient = None

try:  # pragma: no cover - optional provider SDKs
    from anthropic import AsyncAnthropic as _AsyncAnthropic  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - provider optional
    _AsyncAnthropic = None
    try:  # pragma: no cover - provider optional
        try:
            import anthropic
            print("[CLIENTS] Anthropic imported OK from:",
                  getattr(anthropic, "__file__", "<?>"))
        except Exception as e:
            import sys
            print("[CLIENTS.ANTHROPIC_IMPORT_ERROR]")
            print("Exception:", repr(e))
            print("sys.path =", sys.path)
            raise
        _AnthropicSyncClient = getattr(_anthropic_module, "Client", None)
    except Exception:  # pragma: no cover - provider optional
        _anthropic_module = None
        _AnthropicSyncClient = None

# Gemini / Google GenerativeAI
try:  # pragma: no cover - optional provider SDKs
    import google.generativeai as genai
except ImportError:  # pragma: no cover - provider optional
    genai = None  # type: ignore[assignment]

# OpenAI via MCP tool module (stub or real SDK wrapper)
openai_module = get_tool("openai")
AsyncOpenAI = getattr(openai_module, "AsyncOpenAI", None)

logger = logging.getLogger("core_v10_7")


# -------------------------------------------------------------------
# Base client with caching, idempotency, and metrics
# -------------------------------------------------------------------

class AsyncBaseModelClient:
    def __init__(
        self,
        config: ConfigV10_7,
        model_name: str,
        cache_manager: CacheManager,
        cost_tracker: CostTracker,
        metrics_collector: MetricsCollector,
        workflow_id: str,
        agent_name: str,
    ):
        self.config = config
        self.model_name = model_name
        self.cache_manager = cache_manager
        self.cost_tracker = cost_tracker
        self.metrics = metrics_collector
        self.workflow_id = workflow_id
        self.agent_name = agent_name

        # v10.7: Injected by get_model_client
        self.goal_state: str = ""
        self.top_failures: List[str] = []
        self.budget_manager: ContextBudgetManager = None  # type: ignore[assignment]

    def _get_provider_name(self) -> str:
        if "claude" in self.model_name:
            return "anthropic"
        if "gemini" in self.model_name:
            return "google"
        if "gpt-" in self.model_name:
            return "openai"
        return "unknown"

    async def _run_idempotency_check(
        self,
        cached_response: Dict[str, Any],
        messages: List[Dict[str, str]],
        temperature: float,
        response_format: Optional[str] = None,
    ):
        """v10.7 (Fix #29): Runs a 'shadow call' to check for cache drift."""
        try:
            logger.debug(f"Running Idempotency Check for {self.model_name}")
            # Call the *internal* API method to bypass caching
            shadow_response = await self._internal_api_call(
                messages, temperature, response_format
            )

            # Compare results (e.g., hash of content)
            if shadow_response["content"] != cached_response["content"]:
                logger.warning(
                    f"IDEMPOTENCY VIOLATION: {self.model_name} cache drift detected."
                )
                self.metrics.record(
                    agent_name=self.__class__.__name__,
                    task_name="idempotency_violation",
                    duration_ms=0,
                    success=True,  # Log as a successful finding
                    metadata={
                        "model": self.model_name,
                        "cached_content": cached_response["content"][:50],
                        "new_content": shadow_response["content"][:50],
                    },
                )
        except Exception as e:  # pragma: no cover - best-effort
            logger.warning(f"Idempotency check failed: {e}")

    @track_metrics(
        lambda self, *_, **__: getattr(self, "latency_task_name", self.model_name)
    )  # v10.7 (Fix #15/#45): Track latency per model
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        response_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        provider = self._get_provider_name()

        cached_response = await self.cache_manager.get_llm_cache(
            provider, self.model_name, prompt, temperature
        )

        if cached_response:
            # v10.7 (Fix #29): Idempotency Validation
            if (
                self.config.caching_config.enable_idempotency_validation
                and random.random()
                < self.config.caching_config.idempotency_validation_sample_rate
            ):
                # Don't await, run in background
                asyncio.create_task(
                    self._run_idempotency_check(
                        cached_response, messages, temperature, response_format
                    )
                )
            return cached_response

        # Cache MISS: Run the actual API call
        result = await self._internal_api_call(messages, temperature, response_format)

        await self.cache_manager.set_llm_cache(
            provider, self.model_name, prompt, temperature, result
        )
        return result

    async def _internal_api_call(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        response_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Subclasses must implement the actual API call logic here."""
        raise NotImplementedError


# -------------------------------------------------------------------
# Anthropic client (AsyncAnthropic preferred, legacy Client fallback)
# -------------------------------------------------------------------

class AnthropicAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        response_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ModelAPIError("Missing ANTHROPIC_API_KEY environment variable.")

        # Split system vs non-system messages
        system_prompt_parts = [
            m["content"] for m in messages if m.get("role") == "system"
        ]
        system_prompt = (
            "\n\n".join(system_prompt_parts) if system_prompt_parts else None
        )
        non_system_messages = [
            m for m in messages if m.get("role") != "system"
        ]

        # Preferred: AsyncAnthropic client
        if _AsyncAnthropic is not None:
            try:
                client = _AsyncAnthropic(api_key=api_key)
                response = await client.messages.create(
                    model=self.model_name,
                    max_tokens=4096,
                    temperature=temperature,
                    system=system_prompt,
                    messages=non_system_messages,
                )
                content = response.content[0].text
                result = {
                    "content": content,
                    "usage": {
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                    },
                }
                self.cost_tracker.log_cost(
                    self.workflow_id,
                    self.agent_name,
                    self.model_name,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                )
                return result
            except Exception as e:
                raise ModelAPIError(f"Anthropic async API call failed: {e}")

        # Fallback: legacy sync anthropic.Client wrapped in a thread pool
        if _AnthropicSyncClient is not None:
            try:
                sync_client = _AnthropicSyncClient(api_key=api_key)

                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: sync_client.messages.create(
                        model=self.model_name,
                        max_tokens=4096,
                        temperature=temperature,
                        system=system_prompt,
                        messages=non_system_messages,
                    ),
                )

                # Legacy response is dict-like
                content = response["content"][0]["text"]
                usage = response.get("usage", {})
                prompt_tokens = usage.get("input_tokens", 0)
                completion_tokens = usage.get("output_tokens", 0)

                result = {
                    "content": content,
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                    },
                }
                self.cost_tracker.log_cost(
                    self.workflow_id,
                    self.agent_name,
                    self.model_name,
                    prompt_tokens,
                    completion_tokens,
                )
                return result
            except Exception as e:
                raise ModelAPIError(f"Anthropic legacy API call failed: {e}")

        raise ModelAPIError(
            "Anthropic library not installed. Run 'pip install anthropic'."
        )


# -------------------------------------------------------------------
# Gemini / Google GenerativeAI client
# -------------------------------------------------------------------

class GeminiAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        response_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        if genai is None:
            raise ModelAPIError(
                "Google GenerativeAI library not installed. "
                "Run 'pip install google-generativeai'"
            )
        try:
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            gen_config: Dict[str, Any] = {"temperature": temperature}
            if response_format == "json_object":
                gen_config["response_mime_type"] = "application/json"

            model = genai.GenerativeModel(self.model_name)
            prompt_text = "\n".join(
                f"{m['role']}: {m['content']}" for m in messages
            )
            response = await asyncio.to_thread(
                model.generate_content, prompt_text, generation_config=gen_config
            )

            # Normalize result; prefer .text if present
            if hasattr(response, "text"):
                content = response.text
            elif getattr(response, "candidates", None):
                content = response.candidates[0].content.parts[0].text
            else:
                content = str(response)

            result = {"content": content, "usage": {}}
            # Gemini usage reporting is less standardized; cost tracking can be
            # handled by a separate telemetry pipeline if needed.
            return result
        except Exception as e:
            raise ModelAPIError(f"Gemini API call failed: {e}")


# -------------------------------------------------------------------
# OpenAI client (via AsyncOpenAI from MCP tool module)
# -------------------------------------------------------------------

class OpenAIAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        response_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        if AsyncOpenAI is None:
            raise ModelAPIError(
                "OpenAI library not available. "
                "Install 'openai' or ensure MCP OpenAI tool is configured."
            )
        try:
            client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            completion_kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "temperature": temperature,
                "messages": messages,
            }
            if response_format == "json_object":
                completion_kwargs["response_format"] = {"type": "json_object"}

            response = await client.chat.completions.create(**completion_kwargs)
            content = response.choices[0].message.content
            result = {
                "content": content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                },
            }
            self.cost_tracker.log_cost(
                self.workflow_id,
                self.agent_name,
                self.model_name,
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
            )
            return result
        except Exception as e:
            raise ModelAPIError(f"OpenAI API call failed: {e}")


__all__ = [
    "AsyncBaseModelClient",
    "AnthropicAsyncClient",
    "GeminiAsyncClient",
    "OpenAIAsyncClient",
]
