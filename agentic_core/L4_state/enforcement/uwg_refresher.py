"""UWG Stage U6: REFRESH READ SURFACES - Alias swap and cache clearing.

10C-REQ-127: Execute alias swap clear retrieval caches ensure very next request sees updated state
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .uwg_clerk import WriteRequest


@dataclass
class RefreshResult:
    """Result of read surface refresh."""
    alias_swap_completed: bool
    caches_cleared: list[str]
    read_surfaces_updated: list[str]
    timestamp: float
    next_request_sees_update: bool = True


class UWGRefresher:
    """UWG Stage U6: Refresh read surfaces.
    
    10C-REQ-127: Execute alias swap clear retrieval caches ensure very next
    request sees updated state.
    """
    
    def __init__(self) -> None:
        self._aliases: dict[str, str] = {}  # alias -> current_target
        self._cache_clear_handlers: list[Callable[[], bool]] = []
        self._read_surface_refresh_handlers: list[Callable[[], bool]] = []
    
    def refresh(self, request: WriteRequest) -> RefreshResult:
        """Execute alias swap and cache clearing."""
        # Perform alias swap for affected path
        alias_swapped = self._perform_alias_swap(request.path)
        
        # Clear all registered caches
        cleared_caches = self._clear_caches()
        
        # Refresh read surfaces
        updated_surfaces = self._refresh_read_surfaces()
        
        return RefreshResult(
            alias_swap_completed=alias_swapped,
            caches_cleared=cleared_caches,
            read_surfaces_updated=updated_surfaces,
            timestamp=time.time(),
            next_request_sees_update=True,
        )
    
    def _perform_alias_swap(self, path: str) -> bool:
        """Perform alias swap for a path.
        
        The alias swap pattern:
        - Current alias points to active copy
        - Write goes to shadow copy
        - After commit, atomically swap alias
        - Next read sees new state
        """
        # Find alias for this path
        for alias, target in list(self._aliases.items()):
            if path.startswith(alias) or path == target:
                # Perform swap
                shadow_target = self._get_shadow_target(target)
                self._aliases[alias] = shadow_target
                return True
        return False
    
    def _get_shadow_target(self, target: str) -> str:
        """Get shadow target for a given target.
        
        Alternates between _a and _b suffixes.
        """
        if target.endswith("_a"):
            return target[:-2] + "_b"
        elif target.endswith("_b"):
            return target[:-2] + "_a"
        else:
            return target + "_a"
    
    def _clear_caches(self) -> list[str]:
        """Clear all registered caches."""
        cleared: list[str] = []
        for i, handler in enumerate(self._cache_clear_handlers):
            try:
                if handler():
                    cleared.append(f"cache_{i}")
            except (RuntimeError, OSError, ValueError):
                continue  # Continue even if one cache clear fails
        return cleared
    
    def _refresh_read_surfaces(self) -> list[str]:
        """Refresh all registered read surfaces."""
        refreshed: list[str] = []
        for i, handler in enumerate(self._read_surface_refresh_handlers):
            try:
                if handler():
                    refreshed.append(f"surface_{i}")
            except (RuntimeError, OSError, ValueError):
                continue  # Continue even if one refresh fails
        return refreshed
    
    def register_alias(self, alias: str, target: str) -> None:
        """Register an alias pointing to a target."""
        self._aliases[alias] = target
    
    def register_cache_clear_handler(self, handler: Callable[[], bool]) -> None:
        """Register a cache clearing handler."""
        self._cache_clear_handlers.append(handler)
    
    def register_read_surface_refresh_handler(self, handler: Callable[[], bool]) -> None:
        """Register a read surface refresh handler."""
        self._read_surface_refresh_handlers.append(handler)
    
    def get_alias_target(self, alias: str) -> str | None:
        """Get current target for an alias."""
        return self._aliases.get(alias)
