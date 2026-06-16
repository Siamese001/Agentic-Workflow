"""Anthropic Messages API judge adapter."""

from __future__ import annotations

import json
import os
from typing import Any

from agentic_core.config.model_catalog import ANTHROPIC_LEGACY_SONNET_35_MODEL_ID
from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges._base_http_judge import (
    BaseHttpJudge,
    _HttpRequest,
)

_DEFAULT_ENDPOINT = "https://api.anthropic.com/v1/messages"
_DEFAULT_VERSION = "2023-06-01"


class AnthropicJudge(BaseHttpJudge):
    """Judge backed by Anthropic's Messages API.

    Defaults:
        model:      ``claude-3-5-sonnet-latest``
        endpoint:   ``https://api.anthropic.com/v1/messages``
        timeout:    30 s
        max_tokens: 512 — judge responses are small structured JSON

    API key resolution (in order): constructor arg > ``ANTHROPIC_API_KEY``
    env var. If neither is set, raises ``GraderError`` on first call —
    NOT on construction (so wiring code can defer the check).
    """

    def __init__(
        self,
        *,
        model: str = ANTHROPIC_LEGACY_SONNET_35_MODEL_ID,
        api_key: str | None = None,
        endpoint: str = _DEFAULT_ENDPOINT,
        anthropic_version: str = _DEFAULT_VERSION,
        timeout: float = 30.0,
        max_tokens: int = 512,
    ) -> None:
        super().__init__(model=model, timeout=timeout)
        self._api_key = api_key
        self._endpoint = endpoint
        self._version = anthropic_version
        self._max_tokens = int(max_tokens)

    def _resolve_key(self) -> str:
        key = self._api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise GraderError("AnthropicJudge: no API key — set ANTHROPIC_API_KEY or pass api_key=")
        return key

    def _build_request(self, system: str, user: str) -> _HttpRequest:
        body = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        return _HttpRequest(
            url=self._endpoint,
            method="POST",
            headers={
                "content-type": "application/json",
                "x-api-key": self._resolve_key(),
                "anthropic-version": self._version,
            },
            body=json.dumps(body).encode("utf-8"),
        )

    def _extract_text(self, response_json: Any) -> str:
        """Anthropic returns ``{"content": [{"type": "text", "text": "..."}]}``."""
        if not isinstance(response_json, dict):
            raise GraderError("Anthropic response was not an object")
        content = response_json.get("content")
        if not isinstance(content, list) or not content:
            raise GraderError("Anthropic response missing content array")
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if isinstance(text, str):
                    return text
        raise GraderError("Anthropic response had no text block")


__all__ = ["AnthropicJudge"]
