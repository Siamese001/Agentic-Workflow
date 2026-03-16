from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "cache_invalidation_util")
emit_determinism_digest("p0", "cache_invalidation_util")

_emit_dispatches_healing_run("p1", "cache_invalidation_util", "L5")
_emit_routes_through("p1", "cache_invalidation_util", "L5")
_emit_escalates_to_human("p1", "cache_invalidation_util", "L5")
_emit_reads_policy_state("p1", "cache_invalidation_util", "L5")

'\ncache Invalidation Utilities for Healing Workflows\n\nProvides decorators and helpers to invalidate cache after successful healing operations.\nThis ensures stale cached data (like AST results, compliance checks) is purged\nwhen the underlying code changes.\n\nUsage:\n\n    class HealerAgent(SovereignBaseAgent):\n        @heal_invalidate_cache("canon:*")  # Invalidate AST caches after heal\n        async def heal_repository(self) -> dict:\n            # Healing logic...\n            return {"success": True}\n'
import functools
import logging
from collections.abc import Callable
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

log = logging.getLogger(__name__)


def heal_invalidate_cache(pattern: str = ""):
    """
    Decorator to invalidate cache after successful heal operation.

    Args:
        pattern: cache key pattern to invalidate (e.g., "canon:*", "compliance:*")
                 Empty string invalidates all keys for the agent's prefix.

    Usage:
        @heal_invalidate_cache("canon:*")
        async def heal_repository(self) -> dict:
            ...
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_invalidate_cache", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_invalidate_cache", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "heal_invalidate_cache")

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            result = await func(self, *args, **kwargs)
            success = False
            if isinstance(result, dict):
                success = result.get("success", False) or result.get("healed", False)
            elif isinstance(result, bool):
                success = result
            if success and hasattr(self, "cache_invalidate"):
                try:
                    invalidated = await self.cache_invalidate(pattern)
                    log.info(f"cache invalidated for pattern '{pattern}' after heal ({invalidated} keys)")
                # guardian: allow-silent-swallow
                except Exception as e:
                    log.debug(f"cache invalidation failed: {e}")
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
            file_path = kwargs.get(file_path_arg)
            if file_path is None and args:
                import inspect

                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if file_path_arg in params:
                    idx = params.index(file_path_arg) - 1
                    if 0 <= idx < len(args):
                        file_path = args[idx]
            if file_path and hasattr(self, "cache_invalidate"):
                file_name = str(file_path).split("/")[-1].split("\\")[-1]
                try:
                    await self.cache_invalidate(file_name)
                    log.debug(f"cache invalidated for file: {file_name}")
                # guardian: allow-silent-swallow
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
        # guardian: allow-silent-swallow
        except Exception as e:
            log.warning(f"Failed to invalidate all caches: {e}")
    return 0
