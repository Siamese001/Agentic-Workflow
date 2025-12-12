"""Multi-Provider LLM Client Factory.

Provides unified access to all LLM providers with automatic fallbacks,
retry logic, and singleton pattern.

Phase 1C - SDK Integration Layer
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Provider(str, Enum):
    """LLM provider enumeration."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    GROQ = "groq"
    TOGETHER = "together"
    FIREWORKS = "fireworks"


# Provider environment variable mapping
PROVIDER_ENV_VARS = {
    Provider.OPENAI: "OPENAI_API_KEY",
    Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
    Provider.GOOGLE: "GOOGLE_API_KEY",
    Provider.MISTRAL: "MISTRAL_API_KEY",
    Provider.COHERE: "COHERE_API_KEY",
    Provider.GROQ: "GROQ_API_KEY",
    Provider.TOGETHER: "TOGETHER_API_KEY",
    Provider.FIREWORKS: "FIREWORKS_API_KEY",
}


DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 60.0


@dataclass
class ProviderConfig:
    """Configuration for LLM provider."""
    max_retries: int = DEFAULT_MAX_RETRIES
    timeout: float = DEFAULT_TIMEOUT
    base_url: Optional[str] = None
    organization: Optional[str] = None
    default_model: Optional[str] = None


# Singleton client cache
_CLIENTS: Dict[Provider, Any] = {}


def get_api_key(provider: Provider) -> str:
    """Get API key for provider.
    
    Args:
        provider: LLM provider
        
    Returns:
        API key string
        
    Raises:
        ValueError: If API key not found
    """
    env_var = PROVIDER_ENV_VARS.get(provider)
    if not env_var:
        raise ValueError(f"No environment variable defined for provider: {provider}")
    
    api_key = os.getenv(env_var)
    if not api_key:
        raise ValueError(
            f"API key for {provider.value} not set. "
            f"Please set {env_var} environment variable."
        )
    
    return api_key


def _create_client(provider: Provider, config: Optional[ProviderConfig] = None) -> Any:
    """Create a new client instance for provider.
    
    Args:
        provider: LLM provider
        config: Optional provider configuration
        
    Returns:
        Client instance
        
    Raises:
        ValueError: If provider not supported or API key missing
        ImportError: If provider SDK not installed
    """
    if config is None:
        config = ProviderConfig()
    
    api_key = get_api_key(provider)
    
    if provider == Provider.OPENAI:
        import openai
        return openai.OpenAI(
            api_key=api_key,
            max_retries=config.max_retries,
            timeout=config.timeout,
            base_url=config.base_url,
            organization=config.organization,
        )
    
    elif provider == Provider.ANTHROPIC:
        import anthropic
        return anthropic.Anthropic(
            api_key=api_key,
            max_retries=config.max_retries,
            timeout=config.timeout,
            base_url=config.base_url,
        )
    
    elif provider == Provider.GOOGLE:
        # Try new v1beta Interactions API first, fallback to legacy
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            # Store both client and module for compatibility
            client._legacy_genai = __import__('google.generativeai')
            return client
        except ImportError:
            # Fallback to legacy SDK
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai
    
    elif provider == Provider.MISTRAL:
        from mistralai import Mistral
        return Mistral(
            api_key=api_key,
            timeout=int(config.timeout),
        )
    
    elif provider == Provider.COHERE:
        import cohere
        return cohere.Client(
            api_key=api_key,
            timeout=config.timeout,
        )
    
    elif provider == Provider.GROQ:
        from groq import Groq
        return Groq(
            api_key=api_key,
            timeout=config.timeout,
        )
    
    elif provider == Provider.TOGETHER:
        from together import Together
        return Together(
            api_key=api_key,
            timeout=config.timeout,
        )
    
    elif provider == Provider.FIREWORKS:
        import fireworks.client
        fireworks.client.api_key = api_key
        return fireworks.client
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_client(
    provider: Provider,
    config: Optional[ProviderConfig] = None,
    force_new: bool = False,
) -> Any:
    """Get or create LLM client for provider (singleton pattern).
    
    Args:
        provider: LLM provider
        config: Optional provider configuration
        force_new: Force creation of new client
        
    Returns:
        Client instance
        
    Raises:
        ValueError: If provider not supported or API key missing
        ImportError: If provider SDK not installed
    """
    if force_new or provider not in _CLIENTS:
        client = _create_client(provider, config)
        _CLIENTS[provider] = client
        logger.info(f"Created {provider.value} client")
    
    return _CLIENTS[provider]


def reset_all_clients() -> None:
    """Reset all cached clients (for testing)."""
    _CLIENTS.clear()
    logger.debug("Reset all LLM clients")


def get_litellm_completion(
    messages: list[Dict[str, str]],
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs,
) -> Any:
    """Get completion using LiteLLM unified interface.
    
    Args:
        messages: List of message dicts
        model: Model identifier (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        **kwargs: Additional provider-specific parameters
        
    Returns:
        Completion response
        
    Raises:
        ImportError: If litellm not installed
    """
    try:
        import litellm
    except ImportError:
        raise ImportError(
            "litellm not installed. Install with: pip install litellm>=1.50.0"
        )
    
    return litellm.completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )


def get_instructor_client(
    provider: Provider,
    config: Optional[ProviderConfig] = None,
) -> Any:
    """Get Instructor-wrapped client for structured outputs.
    
    Args:
        provider: LLM provider
        config: Optional provider configuration
        
    Returns:
        Instructor-wrapped client
        
    Raises:
        ImportError: If instructor not installed
    """
    try:
        import instructor
    except ImportError:
        raise ImportError(
            "instructor not installed. Install with: pip install instructor>=1.3.0"
        )
    
    base_client = get_client(provider, config)
    
    if provider == Provider.OPENAI:
        return instructor.from_openai(base_client)
    elif provider == Provider.ANTHROPIC:
        return instructor.from_anthropic(base_client)
    elif provider == Provider.GROQ:
        return instructor.from_groq(base_client)
    else:
        return instructor.patch(base_client)


# Default model mappings
DEFAULT_MODELS = {
    Provider.OPENAI: "gpt-4o",
    Provider.ANTHROPIC: "claude-3-5-sonnet-20241022",
    Provider.GOOGLE: "gemini-2.0-flash-exp",
    Provider.MISTRAL: "mistral-large-latest",
    Provider.COHERE: "command-r-plus",
    Provider.GROQ: "llama-3.3-70b-versatile",
    Provider.TOGETHER: "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    Provider.FIREWORKS: "accounts/fireworks/models/llama-v3p1-70b-instruct",
}


def get_default_model(provider: Provider) -> str:
    """Get default model for provider.
    
    Args:
        provider: LLM provider
        
    Returns:
        Default model identifier
    """
    return DEFAULT_MODELS.get(provider, "gpt-4o")
