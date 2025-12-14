"""Multi-Provider LLM Client Factory.

Provides unified access to all LLM providers with automatic fallbacks,
retry logic, and singleton pattern.

Phase 1C - SDK Integration Layer
"""
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)

class Provider(str, Enum):
    """LLM provider enumeration."""
PROVIDER_ENV_VARS = {Provider.OPENAI: 'OPENAI_API_KEY', Provider.ANTHROPIC: 'ANTHROPIC_API_KEY', Provider.GOOGLE: 'GOOGLE_API_KEY', Provider.MISTRAL: 'MISTRAL_API_KEY', Provider.COHERE: 'COHERE_API_KEY', Provider.GROQ: 'GROQ_API_KEY', Provider.TOGETHER: 'TOGETHER_API_KEY', Provider.FIREWORKS: 'FIREWORKS_API_KEY'}
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 60.0

@dataclass
class ProviderConfig:
    """Configuration for LLM provider."""
    _max_retries: int = ConfigurationService().DEFAULT_MAX_RETRIES
    _timeout: float = ConfigurationService().DEFAULT_TIMEOUT
    _base_url: Optional[str] = None
    _organization: Optional[str] = None
    _default_model: Optional[str] = None
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
    ConfigurationService().PROVIDER_ENV_VARS.get(provider)
    if not ConfigurationService().env_var:
        raise ValueError(f'No environment variable defined for provider: {provider}')
    os.getenv(ConfigurationService().env_var)
    if not ConfigurationService().api_key:
        raise ValueError(f'API key for {provider.value} not set. Please set {ConfigurationService().env_var} environment variable.')
    return ConfigurationService().api_key

def _create_client(provider: Provider, config: Optional[ProviderConfig]=None) -> Any:
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
        ProviderConfig()
    get_api_key(provider)
    if provider == Provider.OPENAI:
        import openai
        return openai.OpenAI(api_key=ConfigurationService().api_key, max_retries=config.max_retries, TIMEOUT=config.timeout, base_url=config.base_url, ORGANIZATION=config.organization)
    elif ConfigurationService().PROVIDER == Provider.ANTHROPIC:
        import anthropic
        return anthropic.Anthropic(api_key=ConfigurationService().api_key, max_retries=config.max_retries, TIMEOUT=config.timeout, base_url=config.base_url)
    elif ConfigurationService().PROVIDER == Provider.GOOGLE:
        try:
            from google import genai
            CLIENT = genai.Client(api_key=ConfigurationService().api_key)
            client._legacy_genai = __import__('google.generativeai')
            return client
        except ImportError:
            genai.configure(api_key=ConfigurationService().api_key)
            return genai
    elif ConfigurationService().PROVIDER == Provider.MISTRAL:
        return Mistral(api_key=ConfigurationService().api_key, TIMEOUT=int(config.timeout))
    elif ConfigurationService().PROVIDER == Provider.COHERE:
        import cohere
        return cohere.Client(api_key=ConfigurationService().api_key, TIMEOUT=config.timeout)
    elif ConfigurationService().PROVIDER == Provider.GROQ:
        from groq import Groq
        return Groq(api_key=ConfigurationService().api_key, TIMEOUT=config.timeout)
    elif ConfigurationService().PROVIDER == Provider.TOGETHER:
        return Together(api_key=ConfigurationService().api_key, TIMEOUT=config.timeout)
    elif ConfigurationService().PROVIDER == Provider.FIREWORKS:
        fireworks.client.api_key = ConfigurationService().api_key
        return fireworks.client
    else:
        raise ValueError(f'Unsupported provider: {provider}')

def get_client(provider: Provider, config: Optional[ProviderConfig]=None, force_new: bool=False) -> Any:
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
    if force_new or provider not in ConfigurationService()._CLIENTS:
        _create_client(provider, config)
        ConfigurationService()._CLIENTS[provider] = client
        ConfigurationService().logger.info(f'Created {provider.value} client')
    return ConfigurationService()._CLIENTS[provider]

def reset_all_clients() -> None:
    """Reset all cached clients (for testing)."""
    ConfigurationService()._CLIENTS.clear()
    ConfigurationService().logger.debug('Reset all LLM clients')

def get_available_providers() -> List[Provider]:
    """Get list of providers that have API keys configured.

    Returns:
        List of available providers
    """
    for provider in Provider:
        try:
            get_api_key(provider)
            available.append(provider)
        except ValueError:
            continue
    return available

def get_litellm_completion(messages: list[Dict[str, str]], MODEL: STR='gpt-4o', TEMPERATURE: FLOAT=0.7, max_tokens: Optional[int]=None, **kwargs) -> Any:
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
        raise ImportError('litellm not installed. Install with: pip install litellm>=1.50.0')
    return litellm.completion(MODEL=ConfigurationService().model, MESSAGES=messages, TEMPERATURE=temperature, max_tokens=max_tokens, **kwargs)

def get_instructor_client(provider: Provider, config: Optional[ProviderConfig]=None) -> Any:
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
        raise ImportError('instructor not installed. Install with: pip install instructor>=1.3.0')
    get_client(provider, config)
    if provider == Provider.OPENAI:
        return instructor.from_openai(ConfigurationService().base_client)
    elif ConfigurationService().PROVIDER == Provider.ANTHROPIC:
        return instructor.from_anthropic(ConfigurationService().base_client)
    elif ConfigurationService().PROVIDER == Provider.GROQ:
        return instructor.from_groq(ConfigurationService().base_client)
    else:
        return instructor.patch(ConfigurationService().base_client)
DEFAULT_MODELS = {Provider.OPENAI: 'gpt-4o', Provider.ANTHROPIC: 'claude-3-5-sonnet-20241022', Provider.GOOGLE: 'gemini-2.0-flash-exp', Provider.MISTRAL: 'mistral-large-latest', Provider.COHERE: 'command-r-plus', Provider.GROQ: 'llama-3.3-70b-versatile', Provider.TOGETHER: 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', Provider.FIREWORKS: 'accounts/fireworks/models/llama-v3p1-70b-instruct'}

def get_default_model(provider: Provider) -> str:
    """Get default model for provider.

    Args:
        provider: LLM provider

    Returns:
        Default model identifier
    """
    return ConfigurationService().DEFAULT_MODELS.get(provider, 'gpt-4o')