"""
core_v10_7.clients
-------------------

Unified async model client layer for v10.7.

This module provides:
- OpenAIAsyncClient
- AnthropicAsyncClient
- GeminiAsyncClient
- Tool-routed MCP client integration
- AsyncBaseModelClient: the base interface for all providers

Key behaviors:
- Each provider is optional; missing SDKs raise ModelAPIError only when used.
- Anthropic: prefers AsyncAnthropic, gracefully falls back to anthropic.Client.
- Gemini: uses google-generativeai GenerativeModel with MIME-based JSON mode.
- All clients integrate with:
    - CostTracker
    - ContextBudgetManager
    - MetricsCollector (via @track_metrics)
- MCP tools can override the provider path using get_tool(provider_name).
"""

from __future__ import annotations

import os
import json
import asyncio
from typing import Any, Dict, Optional, List

# --------------------------------------------------------------------
# Imports from core
# --------------------------------------------------------------------

from mcp import get_tool

from .exceptions import ModelAPIError
from .services import (
    CacheManager,
    ContextBudgetManager,
    CostTracker,
    MetricsCollector,
    track_metrics,
)
from .config import ConfigV10_7

# --------------------------------------------------------------------
# Optional provider SDKs
# --------------------------------------------------------------------

#
# Anthropic import resolution
#
_AsyncAnthropic = None
_anthropic_sync_client = None

try:
    # Preferred modern client
    from anthropic import AsyncAnthropic as _AsyncAnthropic
except Exception:
    try:
        # Legacy anthropic.Client fallback
        import anthropic as _anthropic_module
        _anthropic_sync_client = getattr(_anthropic_module, "Client", None)
    except Exception:
        _anthropic_module = None
        _anthropic_sync_client = None


#
# Gemini / Google GenerativeAI
#
try:
    import google.generativeai as genai
except Exception:
    genai = None


#
# OpenAI
#
try:
    import openai
except Exception:
    openai = None


# --------------------------------------------------------------------
# Abstract Base Client
# --------------------------------------------------------------------

class AsyncBaseModelClient:
    """
    Unified async interface for all LLM providers.

    Every provider must implement:
        async def _internal_api_call(self, messages, temperature, response_format=None)
    """

    def __init__(
        self,
        model_name: str,
        config: ConfigV10_7,
        cost_tracker: CostTracker,
        budget_manager: ContextBudgetManager,
        metrics: MetricsCollector,
        cache: CacheManager,
    ):
        self.model_name = model_name
        self.config = config
        self.cost_tracker = cost_tracker
        self.budget_manager = budget_manager
        self.metrics = metrics
        self.cache = cache

    async def call(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        response_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Common entrypoint for all providers.
        Handles caching, metrics, cost tracking, and exceptions.
        """
        cache_key = self.cache.build_key(
            provider=self.__class__.__name__,
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )

        cached = await self.cache.get(cache_key)
        if cached is not None:
            return cached

        # Budget check
        self.budget_manager.check_budget(messages)

        # Metrics wrapper
        with track_metrics(self.metrics, provider=self.__class__.__name__):
            response = await self._internal_api_call(
                messages,
                temperature=temperature,
                response_format=response_format,
            )

        # Track cost if tokens present
        self.cost_tracker.update_from_response(response)

        await self.cache.set(cache_key, response)
        return response

    async def _internal_api_call(
        self, messages, temperature: float = 0.7, response_format=None
    ):
        raise NotImplementedError


# --------------------------------------------------------------------
# OpenAI Client
# --------------------------------------------------------------------

class OpenAIAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(
        self, messages, temperature: float = 0.7, response_format=None
    ):
        if openai is None:
            raise ModelAPIError(
                "OpenAI SDK not installed. Run 'pip install openai'."
            )

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ModelAPIError("Missing OPENAI_API_KEY environment variable.")

        try:
            client = openai.AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format=(
                    {"type": "json_object"} if response_format == "json_object" else None
                ),
            )

            # Standardize into dict
            content = response.choices[0].message["content"]
            return {"content": content, "raw": response}

        except Exception as exc:
            raise ModelAPIError(f"OpenAI model call failed: {exc}")


# --------------------------------------------------------------------
# Anthropic Client
# --------------------------------------------------------------------

class AnthropicAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(
        self, messages, temperature: float = 0.7, response_format=None
    ):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ModelAPIError("Missing ANTHROPIC_API_KEY environment variable.")

        # Modern async client
        if _AsyncAnthropic is not None:
            try:
                client = _AsyncAnthropic(api_key=api_key)
                response = await client.messages.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=self.config.max_output_tokens,
                    temperature=temperature,
                )
                content = response.content[0].text
                return {"content": content, "raw": response}
            except Exception as exc:
                raise ModelAPIError(f"Anthropic async call failed: {exc}")

        # Fallback: legacy sync client wrapped in thread executor
        if _anthropic_sync_client:
            try:
                sync_client = _anthropic_sync_client(api_key=api_key)

                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: sync_client.messages.create(
                        model=self.model_name,
                        messages=messages,
                        max_tokens=self.config.max_output_tokens,
                        temperature=temperature,
                    ),
                )

                content = response["content"][0]["text"]
                return {"content": content, "raw": response}

            except Exception as exc:
                raise ModelAPIError(f"Anthropic legacy call failed: {exc}")

        raise ModelAPIError(
            "Anthropic SDK not installed. Run 'pip install anthropic'."
        )


# --------------------------------------------------------------------
# Gemini Client (Google GenerativeAI)
# --------------------------------------------------------------------

class GeminiAsyncClient(AsyncBaseModelClient):
    async def _internal_api_call(
        self, messages, temperature: float = 0.7, response_format=None
    ):
        if genai is None:
            raise ModelAPIError(
                "Google GenerativeAI library not installed. Run 'pip install google-generativeai'."
            )

        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ModelAPIError("Missing GOOGLE_API_KEY environment variable.")

        try:
            genai.configure(api_key=api_key)

            gen_config = {"temperature": temperature}
            if response_format == "json_object":
                gen_config["response_mime_type"] = "application/json"

            model = genai.GenerativeModel(self.model_name)

            text_input = "\n".join(m.get("content", "") for m in messages)

            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    text_input, generation_config=gen_config
                ),
            )

            # Normalize output
            if hasattr(result, "text"):
                out = result.text
            elif hasattr(result, "candidates") and result.candidates:
                out = result.candidates[0].content.parts[0].text
            else:
                out = str(result)

            return {"content": out, "raw": result}

        except Exception as exc:
            raise ModelAPIError(f"Gemini model call failed: {exc}")


# --------------------------------------------------------------------
# MCP Tool Routed Client
# --------------------------------------------------------------------

class MCPToolClient(AsyncBaseModelClient):
    """
    Allows MCP to override provider behavior.
    Tools are discovered dynamically via get_tool(provider).
    """

    async def _internal_api_call(
        self, messages, temperature: float = 0.7, response_format=None
    ):
        tool = get_tool(self.model_name)
        if tool is None:
            raise ModelAPIError(
                f"MCP tool not found for provider '{self.model_name}'."
            )

        try:
            result = await tool(
                messages=messages,
                temperature=temperature,
                response_format=response_format,
            )
            return result

        except Exception as exc:
            raise ModelAPIError(f"MCP tool call failed: {exc}")


# --------------------------------------------------------------------
# Provider factory
# --------------------------------------------------------------------

def make_model_client(
    provider_name: str,
    model_name: str,
    config: ConfigV10_7,
    cost: CostTracker,
    budget: ContextBudgetManager,
    metrics: MetricsCollector,
    cache: CacheManager,
) -> AsyncBaseModelClient:
    """
    Creates an async client for the specified provider.
    """

    provider = provider_name.lower()

    if provider == "openai":
        return OpenAIAsyncClient(model_name, config, cost, budget, metrics, cache)

    if provider == "anthropic":
        return AnthropicAsyncClient(model_name, config, cost, budget, metrics, cache)

    if provider == "gemini":
        return GeminiAsyncClient(model_name, config, cost, budget, metrics, cache)

    if provider == "mcp":
        return MCPToolClient(model_name, config, cost, budget, metrics, cache)

    raise ModelAPIError(f"Unknown provider: {provider_name}")
