"""Factory for creating and managing the resilient router singleton.

Provides a global singleton instance of the HardenedRouter with default
configurations for common use cases.

Phase 2 - Resilient Routing Layer
"""

import logging


logger = logging.getLogger(__name__)


# Global singleton instance
_router_instance: HardenedRouter | None = None


def get_resilient_router() -> HardenedRouter:
    """Get or create the singleton resilient router instance.

    Returns a configured HardenedRouter with default routing tiers:
    - reasoning_tier: Primary=OpenAI (GPT-4), Backup=Anthropic (Opus)
    - speed_tier: Primary=Gemini (Flash), Backup=OpenAI (4o-mini)
    - cost_optimized_tier: Primary=OpenAI (4o-mini), Backup=Gemini
    - balanced_tier: Primary=Anthropic (Sonnet), Backup=OpenAI

    Returns:
        HardenedRouter singleton instance
    """
    global _router_instance

    if _router_instance is None:
        logger.info("Initializing resilient router with default configurations")
        _router_instance = HardenedRouter(configs=None)  # Uses DEFAULT_ROUTING_CONFIGS
        logger.info(f"Router initialized with tiers: {list(_router_instance.configs.keys())}")

    return _router_instance


def reset_router() -> None:
    """Reset the router singleton (primarily for testing).

    This will force a new router instance to be created on the next
    call to get_resilient_router().
    """
    global _router_instance

    if _router_instance is not None:
        logger.info("Resetting resilient router singleton")
        _router_instance = None


def create_custom_router(configs: dict) -> HardenedRouter:
    """Create a custom router with specific configurations.

    This does NOT affect the singleton instance returned by get_resilient_router().
    Use this when you need a router with custom routing configurations.

    Args:
        configs: Dictionary mapping tier names to RouteConfig instances

    Returns:
        New HardenedRouter instance with custom configs
    """
    logger.info(f"Creating custom router with tiers: {list(configs.keys())}")
    return HardenedRouter(configs=configs)
