"""OpenAI Chat Completions API judge adapter."""

from __future__ import annotations

import json
import os
from typing import Any

from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges._base_http_judge import (
    BaseHttpJudge,
    _HttpRequest,
)

_DEFAULT_ENDPOINT = "https://api.openai.com/v1/chat/completions"


class OpenAIJudge(BaseHttpJudge):
    """Judge backed by OpenAI's Chat Completions API.

    Uses `response_format={"type": "json_object"}` to bias the model
    toward well-formed JSON; our parser is still tolerant of prose wrap
    in case the model ignores the hint.

    API key resolution: constructor arg > ``OPENAI_API_KEY`` env var.
    """

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        endpoint: str = _DEFAULT_ENDPOINT,
        timeout: float = 30.0,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> None:
        super().__init__(model=model, timeout=timeout)
        self._api_key = api_key
        self._endpoint = endpoint
        self._temperature = float(temperature)
        self._max_tokens = int(max_tokens)

    def _resolve_key(self) -> str:
        key = self._api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise GraderError("OpenAIJudge: no API key — set OPENAI_API_KEY or pass api_key=")
        return key

    def _build_request(self, system: str, user: str) -> _HttpRequest:
        body = {
            "model": self._model,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        return _HttpRequest(
            url=self._endpoint,
            method="POST",
            headers={
                "content-type": "application/json",
                "authorization": f"Bearer {self._resolve_key()}",
            },
            body=json.dumps(body).encode("utf-8"),
        )

    def _extract_text(self, response_json: Any) -> str:
        """OpenAI returns ``{"choices": [{"message": {"content": "..."}}]}``."""
        if not isinstance(response_json, dict):
            raise GraderError("OpenAI response was not an object")
        choices = response_json.get("choices")
        if not isinstance(choices, list) or not choices:
            raise GraderError("OpenAI response missing choices array")
        first = choices[0]
        if not isinstance(first, dict):
            raise GraderError("OpenAI choice was not an object")
        message = first.get("message")
        if not isinstance(message, dict):
            raise GraderError("OpenAI choice missing message")
        content = message.get("content")
        if not isinstance(content, str):
            raise GraderError("OpenAI message content not string")
        return content


__all__ = ["OpenAIJudge"]
