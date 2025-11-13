"""
anthropic_stub – safe, minimal test stub for Anthropic.

This DOES NOT override the real SDK in runtime.
It ONLY serves as an optional testing fallback.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------
# Utility: fake usage stats
# ---------------------------------------------------------------------
def _fake_usage() -> Dict[str, int]:
    return {"input_tokens": 50, "output_tokens": 15}


# ---------------------------------------------------------------------
# Synchronous stub client (rarely used)
# ---------------------------------------------------------------------
@dataclass
class Client:
    api_key: Optional[str] = None

    @property
    def messages(self) -> "Client":
        return self

    def create(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return {
            "model": model,
            "content": [{"type": "text", "text": "stubbed anthropic response"}],
            "usage": _fake_usage(),
        }


# ---------------------------------------------------------------------
# Async stub client (this is what your clients.py expects)
# ---------------------------------------------------------------------
class AsyncAnthropic:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @property
    def messages(self) -> "AsyncAnthropic":
        return self

    async def create(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0)  # maintain async contract
        return {
            "model": model,
            "content": [{"type": "text", "text": "stubbed anthropic async response"}],
            "usage": _fake_usage(),
        }


__all__ = ["Client", "AsyncAnthropic"]
