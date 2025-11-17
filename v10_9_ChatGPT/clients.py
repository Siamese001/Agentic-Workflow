"""Async model client shims for the consolidated runtime."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

from .constants import DEFAULT_MODEL_NAME, DEFAULT_TEMPERATURE, MAX_TOKENS


class AsyncBaseModelClient:
    def __init__(self, model: str | None = None, temperature: float | None = None, max_tokens: int | None = None) -> None:
        self.model = model or DEFAULT_MODEL_NAME
        self.temperature = temperature or DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens or MAX_TOKENS

    async def generate(self, prompt: str, **_: Any) -> str:
        await asyncio.sleep(0)
        return f"[{self.model}] {prompt[: self.max_tokens]}"


class AsyncEmbeddingClient(AsyncBaseModelClient):
    async def embed(self, text: str) -> list[float]:
        await asyncio.sleep(0)
        return [float(len(text))]


class AsyncVisionClient(AsyncBaseModelClient):
    async def describe(self, image_bytes: bytes) -> str:
        await asyncio.sleep(0)
        return f"vision({len(image_bytes)} bytes)"


__all__ = [
    "AsyncBaseModelClient",
    "AsyncEmbeddingClient",
    "AsyncVisionClient",
]
