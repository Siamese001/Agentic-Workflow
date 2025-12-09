"""
03_runtime/shared/multi_provider_clients.py
Multi-Provider LLM Client Factory

ZERO-LOSS MERGE — TOP-10 AGENTIC SDK SET
Provides centralized, production-ready clients for all supported providers:
- OpenAI (GPT-4o, o1, embeddings)
- Anthropic (Claude 3.5 Sonnet)
- Google (Gemini 2.0)
- Mistral (Mistral Large)
- Cohere (Command R+, reranking)
- Groq (ultra-fast inference)
- Together (cheap diversified access)
- Fireworks (tool-calling alternative)
- LiteLLM (unified router)
- Instructor (structured outputs)

Usage:
    from agentic_workflow.runtime.shared.multi_provider_clients import (
        get_client, Provider, get_litellm_completion
    )
    
    # Direct provider access
    client = get_client(Provider.ANTHROPIC)
    
    # Unified routing via LiteLLM
    response = await get_litellm_completion(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
        fallbacks=["claude-3-5-sonnet-20241022", "gemini-2.0-flash"]
    )
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

logger = logging.getLogger(__name__)

# =============================================================================
# PROVIDER ENUM
# =============================================================================


class Provider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    GROQ = "groq"
    TOGETHER = "together"
    FIREWORKS = "fireworks"
    LITELLM = "litellm"


# =============================================================================
# ENVIRONMENT VARIABLE MAPPING
# =============================================================================

ENV_KEYS: Dict[Provider, str] = {
    Provider.OPENAI: "OPENAI_API_KEY",
    Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
    Provider.GOOGLE: "GOOGLE_API_KEY",
    Provider.MISTRAL: "MISTRAL_API_KEY",
    Provider.COHERE: "COHERE_API_KEY",
    Provider.GROQ: "GROQ_API_KEY",
    Provider.TOGETHER: "TOGETHER_API_KEY",
    Provider.FIREWORKS: "FIREWORKS_API_KEY",
}


# =============================================================================
# CLIENT CONFIGURATION
# =============================================================================

DEFAULT_MAX_RETRIES: int = 6
DEFAULT_TIMEOUT: float = 120.0
DEFAULT_SEED: int = 42


@dataclass
class ProviderConfig:
    """Configuration for a provider client."""
    max_retries: int = DEFAULT_MAX_RETRIES
    timeout: float = DEFAULT_TIMEOUT
    seed: Optional[int] = DEFAULT_SEED


# =============================================================================
# SINGLETON CLIENT STORAGE
# =============================================================================

_clients: Dict[Provider, Any] = {}
_lock = threading.Lock()


# =============================================================================
# CLIENT FACTORY
# =============================================================================


def get_api_key(provider: Provider) -> str:
    """Get API key for provider from environment."""
    env_key = ENV_KEYS.get(provider)
    if not env_key:
        raise ValueError(f"No environment variable mapping for provider: {provider}")
    
    api_key = os.environ.get(env_key)
    if not api_key:
        raise ValueError(
            f"{env_key} environment variable is not set. "
            f"Please set it to your {provider.value} API key."
        )
    return api_key


def get_client(
    provider: Provider,
    config: Optional[ProviderConfig] = None,
    async_client: bool = True,
) -> Any:
    """
    Get a singleton client for the specified provider.
    
    Args:
        provider: The LLM provider to get a client for
        config: Optional configuration overrides
        async_client: If True, return async client (where supported)
        
    Returns:
        Configured client instance for the provider
        
    Raises:
        ValueError: If API key is not set or provider is unsupported
        ImportError: If the provider SDK is not installed
    """
    cache_key = (provider, async_client)
    
    if cache_key in _clients:
        return _clients[cache_key]
    
    with _lock:
        if cache_key in _clients:
            return _clients[cache_key]
        
        cfg = config or ProviderConfig()
        client = _create_client(provider, cfg, async_client)
        _clients[cache_key] = client
        
        logger.info(
            f"Initialized {provider.value} client "
            f"(async={async_client}, max_retries={cfg.max_retries}, timeout={cfg.timeout}s)"
        )
        
        return client


def _create_client(
    provider: Provider,
    config: ProviderConfig,
    async_client: bool,
) -> Any:
    """Create a new client instance for the provider."""
    
    if provider == Provider.OPENAI:
        from openai import AsyncOpenAI, OpenAI
        api_key = get_api_key(provider)
        ClientClass = AsyncOpenAI if async_client else OpenAI
        return ClientClass(
            api_key=api_key,
            max_retries=config.max_retries,
            timeout=config.timeout,
        )
    
    elif provider == Provider.ANTHROPIC:
        from anthropic import Anthropic, AsyncAnthropic
        api_key = get_api_key(provider)
        ClientClass = AsyncAnthropic if async_client else Anthropic
        return ClientClass(
            api_key=api_key,
            max_retries=config.max_retries,
            timeout=config.timeout,
        )
    
    elif provider == Provider.GOOGLE:
        import google.generativeai as genai
        api_key = get_api_key(provider)
        genai.configure(api_key=api_key)
        return genai  # Google SDK uses module-level configuration
    
    elif provider == Provider.MISTRAL:
        from mistralai import Mistral
        api_key = get_api_key(provider)
        return Mistral(api_key=api_key)
    
    elif provider == Provider.COHERE:
        import cohere
        api_key = get_api_key(provider)
        if async_client:
            return cohere.AsyncClientV2(api_key=api_key)
        return cohere.ClientV2(api_key=api_key)
    
    elif provider == Provider.GROQ:
        from groq import AsyncGroq, Groq
        api_key = get_api_key(provider)
        ClientClass = AsyncGroq if async_client else Groq
        return ClientClass(api_key=api_key)
    
    elif provider == Provider.TOGETHER:
        from together import Together, AsyncTogether
        api_key = get_api_key(provider)
        ClientClass = AsyncTogether if async_client else Together
        return ClientClass(api_key=api_key)
    
    elif provider == Provider.FIREWORKS:
        from fireworks.client import Fireworks, AsyncFireworks
        api_key = get_api_key(provider)
        ClientClass = AsyncFireworks if async_client else Fireworks
        return ClientClass(api_key=api_key)
    
    elif provider == Provider.LITELLM:
        import litellm
        return litellm  # LiteLLM uses module-level functions
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")


# =============================================================================
# LITELLM UNIFIED ROUTING
# =============================================================================


async def get_litellm_completion(
    model: str,
    messages: List[Dict[str, str]],
    fallbacks: Optional[List[str]] = None,
    **kwargs: Any,
) -> Any:
    """
    Get a completion using LiteLLM with optional fallback routing.
    
    Args:
        model: Primary model to use (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
        messages: List of message dicts with role and content
        fallbacks: Optional list of fallback models if primary fails
        **kwargs: Additional arguments passed to litellm.acompletion
        
    Returns:
        LiteLLM completion response
        
    Example:
        response = await get_litellm_completion(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            fallbacks=["claude-3-5-sonnet-20241022", "gemini-2.0-flash"],
            temperature=0.7,
        )
    """
    import litellm
    
    if fallbacks:
        # Use LiteLLM's router for fallback support
        from litellm import Router
        
        model_list = [{"model_name": model, "litellm_params": {"model": model}}]
        for fb in fallbacks:
            model_list.append({"model_name": fb, "litellm_params": {"model": fb}})
        
        router = Router(model_list=model_list, fallbacks=[{model: fallbacks}])
        return await router.acompletion(model=model, messages=messages, **kwargs)
    
    return await litellm.acompletion(model=model, messages=messages, **kwargs)


def get_litellm_completion_sync(
    model: str,
    messages: List[Dict[str, str]],
    fallbacks: Optional[List[str]] = None,
    **kwargs: Any,
) -> Any:
    """Synchronous version of get_litellm_completion."""
    import litellm
    
    if fallbacks:
        from litellm import Router
        
        model_list = [{"model_name": model, "litellm_params": {"model": model}}]
        for fb in fallbacks:
            model_list.append({"model_name": fb, "litellm_params": {"model": fb}})
        
        router = Router(model_list=model_list, fallbacks=[{model: fallbacks}])
        return router.completion(model=model, messages=messages, **kwargs)
    
    return litellm.completion(model=model, messages=messages, **kwargs)


# =============================================================================
# INSTRUCTOR STRUCTURED OUTPUTS
# =============================================================================

T = TypeVar("T")


def get_structured_output(
    provider: Provider,
    model: str,
    response_model: Type[T],
    messages: List[Dict[str, str]],
    **kwargs: Any,
) -> T:
    """
    Get a structured output using Instructor with any provider.
    
    Args:
        provider: The LLM provider to use
        model: Model name for the provider
        response_model: Pydantic model class for structured output
        messages: List of message dicts
        **kwargs: Additional arguments for the completion
        
    Returns:
        Instance of response_model with validated data
        
    Example:
        from pydantic import BaseModel
        
        class UserInfo(BaseModel):
            name: str
            age: int
        
        user = get_structured_output(
            provider=Provider.OPENAI,
            model="gpt-4o",
            response_model=UserInfo,
            messages=[{"role": "user", "content": "Extract: John is 25 years old"}],
        )
    """
    import instructor
    
    client = get_client(provider, async_client=False)
    
    if provider == Provider.OPENAI:
        patched = instructor.from_openai(client)
    elif provider == Provider.ANTHROPIC:
        patched = instructor.from_anthropic(client)
    elif provider == Provider.GOOGLE:
        patched = instructor.from_gemini(client)
    elif provider == Provider.MISTRAL:
        patched = instructor.from_mistral(client)
    elif provider == Provider.COHERE:
        patched = instructor.from_cohere(client)
    elif provider == Provider.GROQ:
        patched = instructor.from_groq(client)
    elif provider == Provider.TOGETHER:
        patched = instructor.from_openai(client, mode=instructor.Mode.JSON)
    elif provider == Provider.FIREWORKS:
        patched = instructor.from_openai(client, mode=instructor.Mode.JSON)
    elif provider == Provider.LITELLM:
        patched = instructor.from_litellm(client)
    else:
        raise ValueError(f"Instructor not supported for provider: {provider}")
    
    return patched.chat.completions.create(
        model=model,
        response_model=response_model,
        messages=messages,
        **kwargs,
    )


# =============================================================================
# RESET & UTILITIES
# =============================================================================


def reset_all_clients() -> None:
    """Reset all client singletons. Useful for testing or reconfiguration."""
    global _clients
    
    with _lock:
        _clients.clear()
        logger.debug("Reset all provider clients")


def get_available_providers() -> List[Provider]:
    """Get list of providers with API keys configured."""
    available = []
    for provider in Provider:
        env_key = ENV_KEYS.get(provider)
        if env_key and os.environ.get(env_key):
            available.append(provider)
    return available


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "Provider",
    # Config
    "ProviderConfig",
    "ENV_KEYS",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_TIMEOUT",
    "DEFAULT_SEED",
    # Client factory
    "get_client",
    "get_api_key",
    "reset_all_clients",
    "get_available_providers",
    # LiteLLM routing
    "get_litellm_completion",
    "get_litellm_completion_sync",
    # Instructor structured outputs
    "get_structured_output",
]
