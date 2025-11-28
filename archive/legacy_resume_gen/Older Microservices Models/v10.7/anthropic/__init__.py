"""Minimal stub of the anthropic client used for tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Client:
    api_key: str | None = None

    def messages_create(self, *, model: str, messages: list[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        return {
            "model": model,
            "messages": messages,
            "content": [{"type": "text", "text": "stubbed anthropic response"}],
            "meta": kwargs,
        }


__all__ = ["Client"]
