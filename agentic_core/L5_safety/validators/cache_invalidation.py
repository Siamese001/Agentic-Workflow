"""
Cache Invalidation Utilities for Healing Workflows

Provides decorators and helpers to invalidate cache after successful healing operations.
This ensures stale cached data (like AST results, compliance checks) is purged
when the underlying code changes.

Usage:

    class HealerAgent(L2ExecutionBaseAgent):
        @heal_invalidate_cache("canon:*")  # Invalidate AST caches after heal
        async def heal_repository(self) -> dict:
            # Healing logic...
            return {"success": True}
"""
from __future__ import annotations
import functools
import logging
from typing import Callable, Any

log = logging.getLogger(__name__)


def heal_invalidate_cache(pattern: str = ""):
    """
    Decorator to invalidate cache after successful heal operation.

    Args:
        pattern: Cache key pattern to invalidate (e.g., "canon:*", "compliance:*")
                 Empty string invalidates all keys for the agent's prefix.

    Usage:
        @heal_invalidate_cache("canon:*")
        async def heal_repository(self) -> dict:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            result = await func(self, *args, **kwargs)

            # Check for success and cache_invalidate capability
            success = False
            if isinstance(result, dict):
                success = result.get("success", False) or result.get("healed", False)
            elif isinstance(result, bool):
                success = result

            if success and hasattr(self, "cache_invalidate"):
                try:
                    invalidated = await self.cache_invalidate(pattern)
                    log.info(f"Cache invalidated for pattern '{pattern}' after heal ({invalidated} keys)")
                except Exception as e:
                    log.debug(f"Cache invalidation failed: {e}")

            return result
        return wrapper
    return decorator


def invalidate_on_file_change(file_path_arg: str = "file_path"):
    """
    Decorator to invalidate cache entries related to a specific file after modification.

    Args:
        file_path_arg: Name of the argument containing the file path

    Usage:
        @invalidate_on_file_change("file_path")
        async def modify_file(self, file_path: Path) -> dict:
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            result = await func(self, *args, **kwargs)

            # Extract file path from args/kwargs
            file_path = kwargs.get(file_path_arg)
            if file_path is None and args:
                # Try to get from positional args based on function signature
                import inspect
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if file_path_arg in params:
                    idx = params.index(file_path_arg) - 1  # -1 for self
                    if 0 <= idx < len(args):
                        file_path = args[idx]

            if file_path and hasattr(self, "cache_invalidate"):
                # Invalidate cache entries containing this file's name
                file_name = str(file_path).split("/")[-1].split("\\")[-1]
                try:
                    await self.cache_invalidate(file_name)
                    log.debug(f"Cache invalidated for file: {file_name}")
                except Exception as e:
                    log.debug(f"File cache invalidation failed: {e}")

            return result
        return wrapper
    return decorator


async def invalidate_all_caches(agent) -> int:
    """
    Utility to invalidate all caches for an agent.

    Args:
        agent: Agent instance with cache_invalidate method

    Returns:
        Number of keys invalidated
    """
    if hasattr(agent, "cache_invalidate"):
        try:
            return await agent.cache_invalidate("")
        except Exception as e:
            log.warning(f"Failed to invalidate all caches: {e}")
    return 0
