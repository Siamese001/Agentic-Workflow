"""
Meta-Learning Guardrails and Safety Checks

Prevents cache abuse, hallucination, and infinite loops in meta-learning integration.

Guardrails Implemented:
1. TTL Management - Prevents stale data poisoning
2. Similarity Thresholds - Prevents low-quality pattern matching
3. Depth Limits - Prevents infinite healing loops
4. Cache Size Limits - Prevents memory exhaustion
5. Domain Isolation - Prevents cross-domain contamination
6. Input Validation - Prevents cache poisoning attacks
7. Rate Limiting - Prevents API abuse
8. Fallback Mechanisms - Graceful degradation on failures
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class CacheGuardrails:
    """
    Cache safety and abuse prevention guardrails.

    Enforces limits on cache operations to prevent abuse and ensure system stability.
    """

    # Cache size limits (per domain)
    max_cache_entries: int = 10000
    max_entry_size_kb: int = 100  # Max 100KB per entry

    # TTL limits
    default_ttl: int = 3600  # 1 hour default
    max_ttl: int = 86400  # 24 hours max
    min_ttl: int = 60  # 1 minute min

    # Similarity thresholds
    default_similarity_threshold: float = 0.85
    min_similarity_threshold: float = 0.70

    # Healing depth limits
    max_healing_depth: int = 5
    depth_reset_timeout: int = 300  # 5 minutes

    # Rate limiting
    max_requests_per_minute: int = 1000
    max_patterns_per_minute: int = 100

    # Internal state
    _cache_sizes: dict[str, int] = field(default_factory=dict)
    _request_counts: dict[str, list[float]] = field(default_factory=dict)
    _pattern_counts: dict[str, list[float]] = field(default_factory=dict)
    _depth_trackers: dict[str, dict[str, Any]] = field(default_factory=dict)


class MetaLearningGuardrails:
    """
    Comprehensive guardrails for meta-learning operations.

    Acts as a skeptical senior developer - assumes agents will hallucinate
    or abuse the cache and implements strict validation.
    """

    def __init__(self, guardrails: CacheGuardrails | None = None):
        self.guardrails = guardrails or CacheGuardrails()
        self.logger = Logger

    def validate_cache_key(self, key: str) -> bool:
        """
        Validate cache key to prevent injection attacks.

        Args:
            key: Cache key to validate

        Returns:
            True if key is safe, False otherwise
        """
        if not key or not isinstance(key, str):
            return False

        # Key length limits
        if len(key) > 256:
            self.logger.warning(f"Cache key too long: {len(key)} chars")
            return False

        # Prevent path traversal
        if ".." in key or key.startswith("/"):
            self.logger.warning(f"Potentially unsafe cache key: {key}")
            return False

        # Only allow alphanumeric, underscores, hyphens, and colons
        import re

        if not re.match(r"^[a-zA-Z0-9_:-]+$", key):
            self.logger.warning(f"Invalid characters in cache key: {key}")
            return False

        return True

    def validate_cache_value(self, value: Any) -> bool:
        """
        Validate cache value to prevent memory exhaustion.

        Args:
            value: Cache value to validate

        Returns:
            True if value is safe, False otherwise
        """
        if value is None:
            return True

        try:
            # Check size
            value_str = json.dumps(value)
            size_kb = len(value_str.encode("utf-8")) / 1024

            if size_kb > self.guardrails.max_entry_size_kb:
                self.logger.warning(f"Cache value too large: {size_kb:.1f}KB")
                return False

            # Check for recursive structures
            if self._has_circular_refs(value):
                self.logger.warning("Circular reference detected in cache value")
                return False

            return True

        except (TypeError, ValueError) as e:
            self.logger.error(f"Cache value serialization failed: {e}")
            return False

    def _has_circular_refs(self, obj: Any, visited: list[int] | None = None) -> bool:
        """Check for circular references in object."""
        if visited is None:
            visited = []

        obj_id = id(obj)
        if obj_id in visited:
            return True

        visited.append(obj_id)

        try:
            if isinstance(obj, dict):
                for v in obj.values():
                    if self._has_circular_refs(v, visited.copy()):
                        return True
            elif isinstance(obj, (list, tuple, set)):
                for item in obj:
                    if self._has_circular_refs(item, visited.copy()):
                        return True
        except RecursionError:
            return True

        return False

    def validate_ttl(self, ttl: int | None) -> int:
        """
        Validate and normalize TTL.

        Args:
            ttl: Requested TTL in seconds

        Returns:
            Validated TTL within allowed range
        """
        if ttl is None:
            return self.guardrails.default_ttl

        if not isinstance(ttl, int) or ttl < 0:
            self.logger.warning(f"Invalid TTL: {ttl}, using default")
            return self.guardrails.default_ttl

        # Enforce limits
        if ttl > self.guardrails.max_ttl:
            self.logger.warning(f"TTL too large: {ttl}s, capping at {self.guardrails.max_ttl}s")
            return self.guardrails.max_ttl

        if ttl < self.guardrails.min_ttl:
            self.logger.warning(f"TTL too small: {ttl}s, using minimum {self.guardrails.min_ttl}s")
            return self.guardrails.min_ttl

        return ttl

    def check_cache_size_limit(self, domain: str) -> bool:
        """
        Check if domain cache size limit is reached.

        Args:
            domain: Cache domain

        Returns:
            True if cache can accept new entries, False if limit reached
        """
        current_size = self.guardrails._cache_sizes.get(domain, 0)

        if current_size >= self.guardrails.max_cache_entries:
            self.logger.warning(f"Cache size limit reached for domain: {domain}")
            return False

        return True

    def update_cache_size(self, domain: str, delta: int) -> None:
        """Update cache size tracking for domain."""
        current = self.guardrails._cache_sizes.get(domain, 0)
        self.guardrails._cache_sizes[domain] = max(0, current + delta)

    def check_rate_limit(self, domain: str, operation: str = "request") -> bool:
        """
        Check rate limits for operations.

        Args:
            domain: Operation domain
            operation: Type of operation (request, pattern)

        Returns:
            True if operation allowed, False if rate limited
        """
        now = time.time()
        one_minute_ago = now - 60

        # Choose appropriate counter and limit
        if operation == "pattern":
            counts = self.guardrails._pattern_counts
            limit = self.guardrails.max_patterns_per_minute
        else:
            counts = self.guardrails._request_counts
            limit = self.guardrails.max_requests_per_minute

        # Clean old entries
        if domain not in counts:
            counts[domain] = []

        counts[domain] = [t for t in counts[domain] if t > one_minute_ago]

        # Check limit
        if len(counts[domain]) >= limit:
            self.logger.warning(f"Rate limit exceeded for {domain} {operation}s")
            return False

        # Record this request
        counts[domain].append(now)
        return True

    def validate_similarity_threshold(self, threshold: float | None) -> float:
        """
        Validate similarity threshold for pattern matching.

        Args:
            threshold: Requested similarity threshold

        Returns:
            Validated threshold within allowed range
        """
        if threshold is None:
            return self.guardrails.default_similarity_threshold

        if not isinstance(threshold, (int, float)):
            self.logger.warning(f"Invalid similarity threshold: {threshold}")
            return self.guardrails.default_similarity_threshold

        # Enforce limits
        if threshold > 1.0:
            self.logger.warning(f"Similarity threshold > 1.0: {threshold}, using 1.0")
            return 1.0

        if threshold < self.guardrails.min_similarity_threshold:
            self.logger.warning(f"Similarity threshold too low: {threshold}, using minimum")
            return self.guardrails.min_similarity_threshold

        return float(threshold)

    def check_healing_depth(self, agent_name: str, violation_id: str) -> bool:
        """
        Check if healing depth limit is reached.

        Args:
            agent_name: Name of the healing agent
            violation_id: Unique identifier for the violation

        Returns:
            True if healing can proceed, False if depth limit reached
        """
        now = time.time()

        # Initialize tracker if needed
        if agent_name not in self.guardrails._depth_trackers:
            self.guardrails._depth_trackers[agent_name] = {}

        agent_tracker = self.guardrails._depth_trackers[agent_name]

        # Clean old entries
        agent_tracker = {
            vid: data
            for vid, data in agent_tracker.items()
            if now - data["last_reset"] < self.guardrails.depth_reset_timeout
        }
        self.guardrails._depth_trackers[agent_name] = agent_tracker

        # Check current depth
        if violation_id not in agent_tracker:
            agent_tracker[violation_id] = {"depth": 0, "last_reset": now}

        depth = agent_tracker[violation_id]["depth"]

        if depth >= self.guardrails.max_healing_depth:
            self.logger.warning(
                f"Healing depth limit reached for {agent_name}:{violation_id} "
                f"(depth={depth}, max={self.guardrails.max_healing_depth})"
            )
            return False

        return True

    def increment_healing_depth(self, agent_name: str, violation_id: str) -> int:
        """
        Increment healing depth counter.

        Args:
            agent_name: Name of the healing agent
            violation_id: Unique identifier for the violation

        Returns:
            Current depth after increment
        """
        if agent_name not in self.guardrails._depth_trackers:
            self.guardrails._depth_trackers[agent_name] = {}

        agent_tracker = self.guardrails._depth_trackers[agent_name]

        if violation_id not in agent_tracker:
            agent_tracker[violation_id] = {"depth": 0, "last_reset": time.time()}

        agent_tracker[violation_id]["depth"] += 1
        return agent_tracker[violation_id]["depth"]

    def reset_healing_depth(self, agent_name: str, violation_id: str) -> None:
        """
        Reset healing depth counter after successful healing.

        Args:
            agent_name: Name of the healing agent
            violation_id: Unique identifier for the violation
        """
        if agent_name in self.guardrails._depth_trackers:
            if violation_id in self.guardrails._depth_trackers[agent_name]:
                del self.guardrails._depth_trackers[agent_name][violation_id]

    def validate_domain_isolation(self, domain: str, pattern: dict[str, Any]) -> bool:
        """
        Validate domain isolation to prevent cross-domain contamination.

        Args:
            domain: Target domain
            pattern: Pattern to validate

        Returns:
            True if pattern is valid for domain, False otherwise
        """
        # Check pattern has domain metadata
        if "domain" in pattern and pattern["domain"] != domain:
            self.logger.warning(
                f"Cross-domain pattern rejected: pattern_domain={pattern['domain']}, "
                f"target_domain={domain}"
            )
            return False

        # Validate pattern structure
        required_fields = ["violation_type", "healing_strategy"]
        for req_field in required_fields:
            if req_field not in pattern:
                self.logger.warning(f"Pattern missing required field: {req_field}")
                return False

        return True

    def sanitize_violation_data(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize violation data to prevent cache poisoning.

        Args:
            violation: Raw violation data

        Returns:
            Sanitized violation data
        """
        # Create safe copy
        sanitized = {}

        # Only allow known safe fields
        safe_fields = {
            "type",
            "path",
            "file_path",
            "import_statement",
            "file_layer",
            "import_layer",
            "violation_type",
            "line_number",
            "message",
        }

        for key, value in violation.items():
            if key in safe_fields:
                # Sanitize string values
                if isinstance(value, str):
                    # Remove potentially dangerous content
                    value = value.replace("\x00", "")  # Null bytes
                    value = value[:1000]  # Length limit
                sanitized[key] = value

        return sanitized

    def generate_safe_cache_key(self, prefix: str, data: dict[str, Any]) -> str:
        """
        Generate safe cache key from data.

        Args:
            prefix: Key prefix
            data: Data to hash

        Returns:
            Safe cache key
        """
        # Create deterministic signature
        sorted_data = json.dumps(data, sort_keys=True, separators=(",", ":"))
        hash_digest = hashlib.sha256(sorted_data.encode()).hexdigest()[:16]

        return f"{prefix}:{hash_digest}"

    def get_stats(self) -> dict[str, Any]:
        """Get guardrails statistics."""
        return {
            "cache_sizes": self.guardrails._cache_sizes.copy(),
            "request_rates": {
                domain: len(timestamps)
                for domain, timestamps in self.guardrails._request_counts.items()
            },
            "pattern_rates": {
                domain: len(timestamps)
                for domain, timestamps in self.guardrails._pattern_counts.items()
            },
            "depth_trackers": {
                agent: len(tracker) for agent, tracker in self.guardrails._depth_trackers.items()
            },
        }


# Global guardrails instance
_guardrails_instance = None


def get_guardrails() -> MetaLearningGuardrails:
    """Get or create global guardrails instance."""
    global _guardrails_instance
    if _guardrails_instance is None:
        _guardrails_instance = MetaLearningGuardrails()
    return _guardrails_instance


def reset_guardrails() -> None:
    """Reset guardrails state (for testing)."""
    global _guardrails_instance
    _guardrails_instance = None
