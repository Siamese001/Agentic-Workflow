"""
03_runtime/shared/clients.py
Official OpenAI SDK Client Singleton

Provides centralized, production-ready OpenAI client with:
- Lazy initialization
- Built-in retry with exponential backoff (max_retries=6)
- Configurable timeout (120s default)
- Environment variable configuration
- Thread-safe singleton pattern

Usage:
    from agentic_workflow.runtime.shared.clients import get_openai_client

    client = get_openai_client()
    response = await client.chat.completions.create(...)
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Optional

from openai import AsyncOpenAI, OpenAI


logger = logging.getLogger(__name__)

# =============================================================================
# CLIENT CONFIGURATION
# =============================================================================

# SDK Configuration Constants
OPENAI_MAX_RETRIES: int = 6  # SDK built-in retry with exponential backoff
OPENAI_TIMEOUT: float = 120.0  # seconds
OPENAI_DEFAULT_SEED: int = 42  # For deterministic outputs

# Environment variable names
ENV_OPENAI_API_KEY = "OPENAI_API_KEY"
ENV_OPENAI_BASE_URL = "OPENAI_BASE_URL"
ENV_OPENAI_ORG_ID = "OPENAI_ORG_ID"


# =============================================================================
# SINGLETON CLIENTS
# =============================================================================

_async_client: Optional[AsyncOpenAI] = None
_sync_client: Optional[OpenAI] = None
_lock = threading.Lock()


def get_openai_client() -> AsyncOpenAI:
    """
    Get the singleton AsyncOpenAI client with lazy initialization.

    The client is configured with:
    - max_retries=6 (SDK built-in exponential backoff)
    - timeout=120.0 seconds
    - API key from OPENAI_API_KEY environment variable
    - Optional base_url from OPENAI_BASE_URL
    - Optional organization from OPENAI_ORG_ID

    Returns:
        AsyncOpenAI: Configured async client instance

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    global _async_client

    if _async_client is not None:
        return _async_client

    with _lock:
        # Double-check after acquiring lock
        if _async_client is not None:
            return _async_client

        api_key = os.environ.get(ENV_OPENAI_API_KEY)
        if not api_key:
            raise ValueError(
                f"{ENV_OPENAI_API_KEY} environment variable is not set. "
                "Please set it to your OpenAI API key."
            )

        base_url = os.environ.get(ENV_OPENAI_BASE_URL)
        organization = os.environ.get(ENV_OPENAI_ORG_ID)

        client_kwargs = {
            "api_key": api_key,
            "max_retries": OPENAI_MAX_RETRIES,
            "timeout": OPENAI_TIMEOUT,
        }

        if base_url:
            client_kwargs["base_url"] = base_url
            logger.info(f"Using custom OpenAI base URL: {base_url}")

        if organization:
            client_kwargs["organization"] = organization
            logger.debug(f"Using OpenAI organization: {organization}")

        _async_client = AsyncOpenAI(**client_kwargs)

        logger.info(
            f"Initialized AsyncOpenAI client "
            f"(max_retries={OPENAI_MAX_RETRIES}, timeout={OPENAI_TIMEOUT}s)"
        )

        return _async_client


def get_openai_sync_client() -> OpenAI:
    """
    Get the singleton synchronous OpenAI client with lazy initialization.

    Use this only when async is not available. Prefer get_openai_client() for async code.

    Returns:
        OpenAI: Configured sync client instance

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    global _sync_client

    if _sync_client is not None:
        return _sync_client

    with _lock:
        if _sync_client is not None:
            return _sync_client

        api_key = os.environ.get(ENV_OPENAI_API_KEY)
        if not api_key:
            raise ValueError(
                f"{ENV_OPENAI_API_KEY} environment variable is not set. "
                "Please set it to your OpenAI API key."
            )

        base_url = os.environ.get(ENV_OPENAI_BASE_URL)
        organization = os.environ.get(ENV_OPENAI_ORG_ID)

        client_kwargs = {
            "api_key": api_key,
            "max_retries": OPENAI_MAX_RETRIES,
            "timeout": OPENAI_TIMEOUT,
        }

        if base_url:
            client_kwargs["base_url"] = base_url

        if organization:
            client_kwargs["organization"] = organization

        _sync_client = OpenAI(**client_kwargs)

        logger.info(
            f"Initialized OpenAI sync client "
            f"(max_retries={OPENAI_MAX_RETRIES}, timeout={OPENAI_TIMEOUT}s)"
        )

        return _sync_client


def reset_clients() -> None:
    """
    Reset all client singletons. Useful for testing or reconfiguration.

    Warning: This will close existing connections. Use with caution in production.
    """
    global _async_client, _sync_client

    with _lock:
        if _async_client is not None:
            logger.debug("Resetting AsyncOpenAI client")
            _async_client = None

        if _sync_client is not None:
            logger.debug("Resetting OpenAI sync client")
            _sync_client = None


def get_default_seed() -> int:
    """
    Get the default seed for deterministic outputs.

    Returns:
        int: Default seed value (42)
    """
    return OPENAI_DEFAULT_SEED


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "get_openai_client",
    "get_openai_sync_client",
    "reset_clients",
    "get_default_seed",
    "OPENAI_MAX_RETRIES",
    "OPENAI_TIMEOUT",
    "OPENAI_DEFAULT_SEED",
]
