from __future__ import annotations

from typing import Any, Optional

from core.models.models import RetrievalConfig
from meta.cache.redis_cache import init_redis_client, get_llm_cache, set_llm_cache


def read_semantic_cache(key: str, cfg: RetrievalConfig) -> Optional[Any]:
    """Read a value from the semantic cache if enabled.

    Currently this delegates to the generic Redis cache using the
    RetrievalConfig.redis_cache settings.
    """

    redis_cfg = getattr(cfg, "redis_cache", None)
    if not redis_cfg or not redis_cfg.enabled:
        return None

    client = init_redis_client(url=redis_cfg.url)
    return get_llm_cache(client, key)


def write_semantic_cache(key: str, value: Any, cfg: RetrievalConfig) -> None:
    """Write a value to the semantic cache if enabled."""

    redis_cfg = getattr(cfg, "redis_cache", None)
    if not redis_cfg or not redis_cfg.enabled:
        return

    client = init_redis_client(url=redis_cfg.url)
    set_llm_cache(client, key, value, ttl_s=redis_cfg.ttl_s)




