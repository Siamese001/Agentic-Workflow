"""Canonical SDK wrapper factories for OpenAI, Anthropic, Vertex, and Gemini."""

from __future__ import annotations

import os

__all__ = [
    "create_openai_client",
    "create_openai_sync_client",
    "create_anthropic_client",
    "create_vertex_client",
    "create_gemini_model",
    "OpenAIClient",
    "AnthropicClient",
    "VertexClient",
    "OpenAIConfig",
    "AnthropicConfig",
    "VertexConfig",
]


def create_openai_client():
    """Create an async OpenAI client from ``OPENAI_API_KEY``."""
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing")
    return openai.AsyncOpenAI(api_key=api_key)


def create_openai_sync_client():
    """Create a synchronous OpenAI client for sync call sites."""
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing")
    return openai.OpenAI(api_key=api_key)


def create_anthropic_client():
    """Create an async Anthropic client from ``ANTHROPIC_API_KEY``."""
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY missing")
    return anthropic.AsyncAnthropic(api_key=api_key)


def create_vertex_client():
    """Create a configured Vertex / Gemini module handle."""
    import google.generativeai as genai

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing")
    genai.configure(api_key=api_key)
    return genai


def create_gemini_model(model_name: str):
    """Create a configured Gemini ``GenerativeModel`` instance."""
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


class OpenAIClient:
    pass


class AnthropicClient:
    pass


class VertexClient:
    pass


class OpenAIConfig:
    pass


class AnthropicConfig:
    pass


class VertexConfig:
    pass
