"""
google_generativeai_stub – safe, offline stub for google.generativeai.

This stub:
 - does NOT shadow the real google-generativeai package
 - matches the structure expected by GeminiAsyncClient in v10.7
 - supports both result.text and result.candidates[*].content.parts[*].text
 - provides fake usage + safety fields
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------
# Fake usage + safety metadata
# ---------------------------------------------------------------------
def _fake_usage() -> Dict[str, int]:
    return {
        "prompt_token_count": 25,
        "candidates_token_count": 10,
        "total_token_count": 35,
    }


# Gemini content part stub
@dataclass
class StubContentPart:
    text: str


# Gemini content block stub
@dataclass
class StubContent:
    parts: List[StubContentPart]


# Gemini candidate stub
@dataclass
class StubCandidate:
    content: StubContent
    safety_ratings: List[Dict[str, Any]] = None


# Gemini response stub
@dataclass
class StubGenerativeResponse:
    text: str
    candidates: List[StubCandidate]
    usage_metadata: Dict[str, int]


# ---------------------------------------------------------------------
# Main Stub Model
# ---------------------------------------------------------------------
class GenerativeModel:
    def __init__(self, name: str):
        self.name = name

    async def generate_content(
        self,
        prompt: str,
        generation_config: Optional[Dict[str, Any]] = None,
        **_kwargs
    ) -> StubGenerativeResponse:
        """
        Async stub matching:
            response.text
            response.candidates[0].content.parts[0].text
            response.usage_metadata
        """

        await asyncio.sleep(0)  # maintain async contract

        text_output = f"stubbed generative output for: {prompt[:50]}..."

        part = StubContentPart(text=text_output)
        content = StubContent(parts=[part])
        candidate = StubCandidate(content=content, safety_ratings=[{"score": 0.0}])

        return StubGenerativeResponse(
            text=text_output,
            candidates=[candidate],
            usage_metadata=_fake_usage(),
        )


# ---------------------------------------------------------------------
# Configuration Stub
# ---------------------------------------------------------------------
def configure(api_key: Optional[str] = None, **_kwargs):
    """
    The real SDK accepts:
        genai.configure(api_key="...")
    Stub should silently accept and store key.
    """
    return None


__all__ = ["GenerativeModel", "configure"]
