from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Reasoning Path Caching Module

Implements memoization for reasoning paths to reduce redundant LLM calls
and improve latency on repeated sub-problems.
"""


import functools
import hashlib
import json
from collections import OrderedDict
from typing import Any


class ReasoningCache:
    """LRU cache for reasoning paths."""

    def __init__(self, maxsize: int = 10000):
        """Initialize reasoning cache."""
        self.maxsize = maxsize
        self.cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _make_key(self, problem: str, context: dict[str, Any], params: tuple) -> str:
        """
        Create cache key from problem, context, and parameters.

        Args:
            problem: Problem statement
            context: Context dictionary
            params: Parameter tuple (temperature, model, etc.)

        Returns:
            Stable hash key
        """
        # Create stable representation
        context_str = json.dumps(context, sort_keys=True, default=str)
        params_str = json.dumps(params, sort_keys=True, default=str)

        key_input = f"{problem}|{context_str}|{params_str}"
        return hashlib.sha256(key_input.encode()).hexdigest()

    def get(self, problem: str, context: dict[str, Any], params: tuple) -> dict[str, Any] | None:
        """
        Get cached reasoning result.

        Args:
            problem: Problem statement
            context: Context dictionary
            params: Parameter tuple

        Returns:
            Cached result or None
        """
        key = self._make_key(problem, context, params)

        if key in self.cache:
            # Move to end (LRU)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return None

    def put(self, problem: str, context: dict[str, Any], params: tuple, result: dict[str, Any]) -> None:
        """
        cache reasoning result.

        Args:
            problem: Problem statement
            context: Context dictionary
            params: Parameter tuple
            result: Reasoning result to cache
        """
        key = self._make_key(problem, context, params)

        # Remove oldest if at capacity
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)

        self.cache[key] = result

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total,
        }


class ObservationCache:
    """cache for ReAct observations to avoid redundant tool calls."""

    def __init__(self, maxsize: int = 5000):
        """Initialize observation cache."""
        self.maxsize = maxsize
        self.cache: OrderedDict[str, str] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _make_key(self, action: str, context_hash: str) -> str:
        """
        Create cache key from action and context.

        Args:
            action: Action to execute
            context_hash: Hash of context

        Returns:
            cache key
        """
        key_input = f"{action}|{context_hash}"
        return hashlib.sha256(key_input.encode()).hexdigest()

    def get(self, action: str, context_hash: str) -> str | None:
        """
        Get cached observation.

        Args:
            action: Action to execute
            context_hash: Hash of context

        Returns:
            Cached observation or None
        """
        key = self._make_key(action, context_hash)

        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return None

    def put(self, action: str, context_hash: str, observation: str) -> None:
        """
        cache observation.

        Args:
            action: Action executed
            context_hash: Hash of context
            observation: Observation result
        """
        key = self._make_key(action, context_hash)

        if len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)

        self.cache[key] = observation

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total,
        }


# Global cache instances
reasoning_cache = ReasoningCache(maxsize=10000)
observation_cache = ObservationCache(maxsize=5000)


def cached_reasoning(func):
    """Decorator for caching reasoning results."""

    @functools.wraps(func)
    def wrapper(self, problem: str, context: dict[str, Any], *args, **kwargs):
        # Create parameter tuple
        params = (
            context.get("temperature", 0.7),
            context.get("model", "default"),
            context.get("max_steps", 8),
        )

        # Check cache
        cached_result = reasoning_cache.get(problem, context, params)
        if cached_result is not None:
            print(f"[CACHE HIT] Problem: {problem[:50]}...")
            return cached_result

        # cache miss - execute function
        print(f"[CACHE MISS] Problem: {problem[:50]}...")
        result = func(self, problem, context, *args, **kwargs)

        # Store in cache
        reasoning_cache.put(problem, context, params, result)

        return result

    return wrapper


def cached_observation(func):
    """Decorator for caching observations."""

    @functools.wraps(func)
    def wrapper(self, action: str, context: dict[str, Any], *args, **kwargs):
        # Create context hash
        context_str = json.dumps(context, sort_keys=True, default=str)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()

        # Check cache
        cached_result = observation_cache.get(action, context_hash)
        if cached_result is not None:
            print(f"[OBS CACHE HIT] Action: {action[:50]}...")
            return cached_result

        # cache miss - execute function
        print(f"[OBS CACHE MISS] Action: {action[:50]}...")
        result = func(self, action, context, *args, **kwargs)

        # Store in cache
        observation_cache.put(action, context_hash, result)

        return result

    return wrapper
