"""
DS-1: Real Gemini SDK Wiring
Google Gemini API provider implementation for SovereignLLMGateway.
"""
import os
import json
import hashlib
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass

# Gemini API configuration
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_DEFAULT_MODEL = "gemini-1.5-flash"
GEMINI_TIMEOUT_SECONDS = 60


class GeminiError(Exception):
    """Base exception for Gemini provider errors."""
    pass


class GeminiAPIKeyMissing(GeminiError):
    """Raised when GEMINI_API_KEY environment variable is not set."""
    pass


class GeminiAPIError(GeminiError):
    """Raised when Gemini API returns an error."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


@dataclass(frozen=True)
class GeminiResponse:
    """Structured response from Gemini API."""
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    finish_reason: str = "stop"
    safety_ratings: Optional[List[Dict]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "finish_reason": self.finish_reason,
            "safety_ratings": self.safety_ratings,
        }


def _get_api_key() -> str:
    """Get Google AI API key from environment (``GOOGLE_API_KEY`` canonical)."""
    from agentic_core.config.google_ai_env import GOOGLE_API_KEY, google_api_key

    api_key, _ = google_api_key()
    if not api_key:
        raise GeminiAPIKeyMissing(
            f"{GOOGLE_API_KEY} environment variable not set. "
            "Set it to your Google AI Studio API key."
        )
    return api_key


def _estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars per token for English)."""
    return len(text) // 4


def _generate_content(
    prompt: str,
    model: str = GEMINI_DEFAULT_MODEL,
    temperature: float = 0.7,
    max_output_tokens: int = 4096,
    streaming: bool = False,
) -> GeminiResponse:
    """
    Generate content using Gemini API.
    
    This is the core implementation. In production, this would use the
    official google-generativeai SDK. For now, we use httpx for
    the HTTP implementation to avoid adding heavy dependencies.
    """
    import time
    
    try:
        import httpx
    except ImportError:
        # Fallback to stub if httpx not available
        return GeminiResponse(
            text="[GEMINI_STUB: httpx not installed]",
            model=model,
            input_tokens=_estimate_tokens(prompt),
            output_tokens=0,
            latency_ms=0.0,
            finish_reason="error",
        )
    
    api_key = _get_api_key()
    
    url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        }
    }
    
    start_time = time.time()
    
    try:
        response = httpx.post(
            url,
            json=payload,
            timeout=GEMINI_TIMEOUT_SECONDS,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract text from response
        candidates = data.get("candidates", [])
        if not candidates:
            raise GeminiAPIError("No candidates in response")
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text = "".join(part.get("text", "") for part in parts)
        
        finish_reason = candidates[0].get("finishReason", "stop")
        safety_ratings = candidates[0].get("safetyRatings", [])
        
        # Token counting (Gemini doesn't always return this)
        usage = data.get("usageMetadata", {})
        input_tokens = usage.get("promptTokenCount", _estimate_tokens(prompt))
        output_tokens = usage.get("candidatesTokenCount", _estimate_tokens(text))
        
        return GeminiResponse(
            text=text,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            finish_reason=finish_reason,
            safety_ratings=safety_ratings,
        )
        
    except httpx.HTTPStatusError as e:
        latency_ms = (time.time() - start_time) * 1000
        raise GeminiAPIError(
            f"HTTP error {e.response.status_code}: {e.response.text}",
            status_code=e.response.status_code,
            response_body=e.response.text,
        )
    except Exception as e:  # guardian: allow-exception-type-erasure -- P1 ADG burndown  # guardian: allow-broad-exception -- P1 ADG burndown
        latency_ms = (time.time() - start_time) * 1000
        raise GeminiAPIError(f"Request failed: {e}")


class GeminiProvider:
    """
    SovereignLLMGateway-compatible Gemini provider.
    
    This class implements the provider interface expected by the gateway,
    allowing Gemini to be used as a provider option.
    """
    
    PROVIDER_NAME = "gemini"
    DEFAULT_MODEL = GEMINI_DEFAULT_MODEL
    SUPPORTED_MODELS = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        from agentic_core.config.google_ai_env import google_api_key

        resolved_key, _ = google_api_key()
        self._api_key = api_key or resolved_key
    
    def is_available(self) -> bool:
        """Check if Gemini provider is available (API key set)."""
        return self._api_key is not None and len(self._api_key) > 0
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content through Gemini.
        
        Returns dict compatible with SovereignLLMGateway response format.
        """
        if not self.is_available():
            raise GeminiAPIKeyMissing("Gemini provider not available - no API key")
        
        selected_model = model or self.DEFAULT_MODEL
        
        response = _generate_content(
            prompt=prompt,
            model=selected_model,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        return {
            "provider": self.PROVIDER_NAME,
            "model": response.model,
            "content": response.text,
            "usage": {
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "total_tokens": response.input_tokens + response.output_tokens,
            },
            "latency_ms": response.latency_ms,
            "finish_reason": response.finish_reason,
            "metadata": {
                "safety_ratings": response.safety_ratings,
            }
        }
    
    def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream generate content through Gemini.
        
        Yields text chunks as they arrive.
        """
        # Streaming implementation would use Gemini's streamGenerateContent endpoint
        # For now, fall back to non-streaming and yield full response
        response = self.generate(prompt, model, temperature, max_tokens, **kwargs)
        yield response["content"]


def create_gemini_provider(config: Optional[Dict] = None) -> GeminiProvider:
    """
    Factory function to create a Gemini provider.
    
    This is the entry point used by SovereignLLMGateway.
    """
    config = config or {}
    from agentic_core.config.google_ai_env import google_api_key

    resolved_key, _ = google_api_key()
    api_key = config.get("api_key") or resolved_key
    return GeminiProvider(api_key=api_key)
