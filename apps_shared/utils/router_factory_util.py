"""Factory for creating and managing the resilient router singleton.

Provides a global singleton instance of the HardenedRouter with default
configurations for common use cases.

Phase 2 - Resilient Routing Layer
"""

import logging

from apps_shared.types.model_router_types import ModelRouter

logger = logging.getLogger(__name__)
_router_instance: ModelRouter | None = None


def get_resilient_router() -> ModelRouter:
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
        _router_instance = ModelRouter()
        tiers = list(_router_instance.get_stats()["available_models"].keys())
        logger.info(f"router initialized with tiers: {tiers}")
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


def create_custom_router(configs: dict) -> ModelRouter:
    """Create a custom router with specific configurations.

    This does NOT affect the singleton instance returned by get_resilient_router().
    Use this when you need a router with custom routing configurations.

    Args:
        configs: Dictionary of extra model names to ModelConfig instances

    Returns:
        New ModelRouter instance with custom models added
    """
    from apps_shared.types.model_router_types import ModelConfig  # noqa: PLC0415

    logger.info(f"Creating custom router with tiers: {list(configs.keys())}")
    router = ModelRouter()
    for name, cfg in configs.items():
        if isinstance(cfg, ModelConfig):
            router.add_model(name, cfg)
    return router
