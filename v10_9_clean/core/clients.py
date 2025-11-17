"""Async model clients for v10_7 runtime."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx

from .exceptions import ModelClientError


class BaseAsyncClient:
    """Base async LLM client with shared semantics."""

    model: str

    def __init__(self, model: str, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint

    async def _post_json(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as exc:  # noqa: BLE001
            raise ModelClientError(str(exc)) from exc

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError


class AsyncOpenAIClient(BaseAsyncClient):
    """Minimal async OpenAI client wrapper."""

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"model": self.model, "choices": [{"message": {"content": "ok", "role": "assistant"}}], "usage": {}}


class AsyncAnthropicClient(BaseAsyncClient):
    """Minimal async Anthropic client wrapper."""

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"model": self.model, "content": [{"text": "ok", "role": "assistant"}], "usage": {}}


class AsyncGeminiClient(BaseAsyncClient):
    """Minimal async Gemini client wrapper."""

    async def chat_completion_async(self, messages: Any, **kwargs: Any) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"model": self.model, "candidates": [{"content": {"parts": [{"text": "ok"}]}}], "usage": {}}


def build_client(model: str) -> BaseAsyncClient:
    """Factory to build the appropriate async client based on model hint."""

    lowered = (model or "").lower()
    if "claude" in lowered:
        return AsyncAnthropicClient(model)
    if "gemini" in lowered:
        return AsyncGeminiClient(model)
    return AsyncOpenAIClient(model)
