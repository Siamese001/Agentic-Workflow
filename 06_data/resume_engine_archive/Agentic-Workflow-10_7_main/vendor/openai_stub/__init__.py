"""
openai_stub – safe test stub for AsyncOpenAI.

This is *not* the real OpenAI SDK.
It mimics just enough of the API so unit tests can run offline.

Does NOT shadow the real OpenAI library if placed in vendor/openai_stub.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------
# Fake usage statistics
# ---------------------------------------------------------------------
def _fake_usage() -> Dict[str, int]:
    return {
        "prompt_tokens": 30,
        "completion_tokens": 10,
        "total_tokens": 40,
    }


# ---------------------------------------------------------------------
# Stub completion chunk
# ---------------------------------------------------------------------
@dataclass
class StubMessage:
    role: str = "assistant"
    content: str = "stubbed openai response"


@dataclass
class StubChoice:
    index: int = 0
    message: StubMessage = StubMessage()


@dataclass
class StubUsage:
    prompt_tokens: int = 30
    completion_tokens: int = 10
    total_tokens: int = 40


@dataclass
class StubChatCompletion:
    choices: List[StubChoice]
    usage: StubUsage


# ---------------------------------------------------------------------
# Stub AsyncOpenAI – this mimics the real client shape
# ---------------------------------------------------------------------
class AsyncOpenAI:
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key

    @property
    def chat(self) -> "AsyncOpenAI":
        """Return object with .completions.create()"""
        return self

    @property
    def completions(self) -> "AsyncOpenAI":
        return self

    async def create(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        response_format: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> StubChatCompletion:
        """
        Async stubbed create() call.
        Returns minimal object compatible with:
            response.choices[0].message.content
            response.usage.prompt_tokens
            response.usage.completion_tokens
        """
        await asyncio.sleep(0)  # maintain async contract

        msg = StubMessage(content="stubbed openai async response")
        choice = StubChoice(message=msg)
        usage = StubUsage(**_fake_usage())

        return StubChatCompletion(choices=[choice], usage=usage)


__all__ = ["AsyncOpenAI"]
