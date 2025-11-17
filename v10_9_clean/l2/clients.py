"""
Async model clients for v10_9 runtime.

Provides a unified async interface for:
    • OpenAI-compatible models
    • Anthropic Claude models
    • Google Gemini models

All LLM responses are normalized into a canonical schema:

{
    "model": "<model-name>",
    "role": "assistant",
    "content": "<text>",
    "usage": {
        "prompt_tokens": int,
        "completion_tokens": int,
        "total_tokens": int
    },
    "raw": <provider-raw-response>
}

This keeps L2 ExecutionEngine and L3 Orchestrator deterministic and provider-agnostic.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx

from ..shared.exceptions import ModelClientError


# ======================================================================
# BASE ASYNC CLIENT
# ======================================================================

class BaseAsyncClient:
    """
    Base async model client.

    Provides:
        • JSON POST helper
        • unified error handling
        • interface for chat completion
    """

    model: str

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint
        self.timeout = timeout

    async def _post_json(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as exc:  # noqa: BLE001
            raise ModelClientError(str(exc)) from exc

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        """Interface contract — must be implemented by subclasses."""
        raise NotImplementedError


# ======================================================================
# OPENAI CLIENT
# ======================================================================

class AsyncOpenAIClient(BaseAsyncClient):
    """Stubbed async OpenAI client."""

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)

        raw = {
            "model": self.model,
            "choices": [
                {"message": {"role": "assistant", "content": "ok"}}
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }

        return {
            "model": self.model,
            "role": "assistant",
            "content": raw["choices"][0]["message"]["content"],
            "usage": raw["usage"],
            "raw": raw,
        }


# ======================================================================
# ANTHROPIC CLIENT
# ======================================================================

class AsyncAnthropicClient(BaseAsyncClient):
    """Stubbed async Anthropic client."""

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)

        raw = {
            "model": self.model,
            "content": [{"role": "assistant", "text": "ok"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }

        return {
            "model": self.model,
            "role": "assistant",
            "content": raw["content"][0]["text"],
            "usage": raw["usage"],
            "raw": raw,
        }


# ======================================================================
# GEMINI CLIENT
# ======================================================================

class AsyncGeminiClient(BaseAsyncClient):
    """Stubbed async Google Gemini client."""

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)

        raw = {
            "model": self.model,
            "candidates": [
                {"content": {"parts": [{"text": "ok"}]}}
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }

        content = raw["candidates"][0]["content"]["parts"][0]["text"]

        return {
            "model": self.model,
            "role": "assistant",
            "content": content,
            "usage": raw["usage"],
            "raw": raw,
        }


# ======================================================================
# CLIENT FACTORY
# ======================================================================

def build_client(model: str) -> BaseAsyncClient:
    """
    Factory that chooses the correct async client
    based on the model string.

    Model matching is:
        • lowercase
        • substring-based
        • deterministic
    """

    lowered = (model or "").lower()

    if "claude" in lowered or "anthropic" in lowered:
        return AsyncAnthropicClient(model)

    if "gemini" in lowered or "google" in lowered:
        return AsyncGeminiClient(model)

    # Default → OpenAI-style client
    return AsyncOpenAIClient(model)
