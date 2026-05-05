"""Google Gemini generateContent API judge adapter.

Uses the Gemini REST API (``generativelanguage.googleapis.com``) via the
same zero-dep urllib pattern as the other judge adapters.

API key resolution (in order):
    constructor arg > ``GOOGLE_API_KEY`` env var > ``GEMINI_API_KEY`` env var
    (deprecated alias).

Model default: ``gemini-2.0-flash`` — fast and cost-effective for judge calls.
Override with ``GEMINI_MODEL`` env var or the ``model=`` constructor arg.
"""

from __future__ import annotations

import json
import os
from typing import Any

from agentic_core.L3_orchestration.exit_eval.graders.base import GraderError
from agentic_core.L3_orchestration.exit_eval.judges._base_http_judge import (
    BaseHttpJudge,
    _HttpRequest,
)

_DEFAULT_MODEL = "gemini-2.0-flash"
_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)


class GoogleJudge(BaseHttpJudge):
    """Judge backed by Google Gemini generateContent API.

    Defaults:
        model:   ``gemini-2.0-flash`` (overridable via ``GEMINI_MODEL`` env var)
        timeout: 30 s
        max_tokens: 512

    The Gemini API fuses system and user content into a single ``contents``
    array with ``role="user"`` (system prompt prepended as a preamble within
    the same turn).  The API key is embedded in the query string, not a header.
    """

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_tokens: int = 512,
    ) -> None:
        resolved_model = (
            model
            or os.environ.get("GEMINI_MODEL")
            or _DEFAULT_MODEL
        )
        super().__init__(model=resolved_model, timeout=timeout)
        self._api_key = api_key
        self._max_tokens = int(max_tokens)

    def _resolve_key(self) -> str:
        key = (
            self._api_key
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")  # deprecated alias
        )
        if not key:
            raise GraderError(
                "GoogleJudge: no API key — set GOOGLE_API_KEY or pass api_key="
            )
        return key

    def _build_request(self, system: str, user: str) -> _HttpRequest:
        key = self._resolve_key()
        url = _ENDPOINT_TEMPLATE.format(model=self._model, key=key)
        combined_text = f"{system}\n\n{user}"
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": combined_text}],
                }
            ],
            "generationConfig": {
                "maxOutputTokens": self._max_tokens,
                "temperature": 0.0,
            },
        }
        return _HttpRequest(
            url=url,
            method="POST",
            headers={"content-type": "application/json"},
            body=json.dumps(body).encode("utf-8"),
        )

    def _extract_text(self, response_json: Any) -> str:
        """Gemini returns ``{"candidates": [{"content": {"parts": [{"text": "..."}]}}]}``."""
        if not isinstance(response_json, dict):
            raise GraderError("Gemini response was not an object")
        candidates = response_json.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise GraderError("Gemini response missing candidates array")
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        for part in parts:
            if isinstance(part, dict):
                text = part.get("text", "")
                if isinstance(text, str) and text.strip():
                    return text
        raise GraderError("Gemini response had no text part")


__all__ = ["GoogleJudge"]
