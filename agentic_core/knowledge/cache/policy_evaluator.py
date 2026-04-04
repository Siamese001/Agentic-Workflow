"""Policy Evaluator.

Freshness checking, exact ACL verification, and perfect match detection.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class FreshnessCheck:
    """Result of freshness verification."""
    is_fresh: bool
    age_seconds: float
    freshness_band: str
    max_age_seconds: float
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ACCheck:
    """Result of ACL verification."""
    allowed: bool
    user_perms: list[str] = field(default_factory=list)
    required_perms: list[str] = field(default_factory=list)
    missing_perms: list[str] = field(default_factory=list)


@dataclass
class PolicyResult:
    """Result of policy evaluation."""
    can_use_cache: bool
    freshness_ok: bool
    acl_ok: bool
    exact_match: bool
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class PolicyEvaluator:
    """Evaluates cache policies for freshness, ACL, and matching.

    The PolicyEvaluator performs comprehensive checks to determine
    if cached content can be used for a given query context.
    """

    def __init__(self):
        """Initialize the policy evaluator."""
        self._freshness_bands = {
            "realtime": 300,      # 5 minutes
            "hourly": 3600,       # 1 hour
            "daily": 86400,       # 24 hours
            "weekly": 604800,     # 7 days
        }
        log.info("PolicyEvaluator initialized")

    def evaluate(
        self,
        cache_entry: dict[str, Any],
        query_context: dict[str, Any],
        scope_metadata: dict[str, Any],
    ) -> PolicyResult:
        """Evaluate if cache entry can be used.

        Args:
            cache_entry: Cached data with metadata
            query_context: Current query context
            scope_metadata: Scope metadata from gates

        Returns:
            PolicyResult with evaluation outcome
        """
        trace_id = f"policy_{hash(str(cache_entry)) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "PolicyEvaluator.evaluate"
        )

        reasons = []

        # Check freshness
        freshness_check = self.check_freshness(
            cache_entry.get("timestamp"),
            query_context.get("freshness_band", "daily"),
        )

        if not freshness_check.is_fresh:
            reasons.append(f"Data stale: {freshness_check.age_seconds}s old")

        # Check ACL
        acl_check = self.check_acl(
            scope_metadata.get("user_permissions", []),
            cache_entry.get("required_permissions", []),
        )

        if not acl_check.allowed:
            reasons.append(f"ACL denied: missing {acl_check.missing_perms}")

        # Check exact match if required
        exact_match = False
        if query_context.get("require_exact_match", False):
            exact_match = self.check_exact_match(
                query_context.get("query", ""),
                cache_entry.get("query", ""),
            )
            if not exact_match:
                reasons.append("Exact match required but not found")

        can_use = freshness_check.is_fresh and acl_check.allowed
        if query_context.get("require_exact_match", False):
            can_use = can_use and exact_match

        result = PolicyResult(
            can_use_cache=can_use,
            freshness_ok=freshness_check.is_fresh,
            acl_ok=acl_check.allowed,
            exact_match=exact_match,
            reasons=reasons,
            metadata={
                "freshness": freshness_check,
                "acl": acl_check,
            },
        )

        log.debug(f"Policy evaluation: can_use={can_use}, reasons={len(reasons)}")
        return result

    def check_freshness(
        self,
        entry_timestamp: float | None,
        freshness_band: str,
    ) -> FreshnessCheck:
        """Check if cache entry is fresh.

        Args:
            entry_timestamp: When entry was created (Unix timestamp)
            freshness_band: Required freshness band

        Returns:
            FreshnessCheck with result
        """
        if entry_timestamp is None:
            return FreshnessCheck(
                is_fresh=False,
                age_seconds=float('inf'),
                freshness_band=freshness_band,
                max_age_seconds=0,
                reason="No timestamp available",
            )

        max_age = self._freshness_bands.get(freshness_band, 86400)
        age = time.time() - entry_timestamp

        return FreshnessCheck(
            is_fresh=age <= max_age,
            age_seconds=age,
            freshness_band=freshness_band,
            max_age_seconds=max_age,
        )

    def check_acl(
        self,
        user_permissions: list[str],
        required_permissions: list[str],
    ) -> ACCheck:
        """Check if user has required permissions.

        Args:
            user_permissions: User's granted permissions
            required_permissions: Required permissions for access

        Returns:
            ACCheck with result
        """
        missing = [p for p in required_permissions if p not in user_permissions]

        return ACCheck(
            allowed=len(missing) == 0,
            user_perms=user_permissions,
            required_perms=required_permissions,
            missing_perms=missing,
        )

    def check_exact_match(self, query1: str, query2: str) -> bool:
        """Check if two queries are exact matches.

        Args:
            query1: First query
            query2: Second query

        Returns:
            True if exact match
        """
        return query1.strip().lower() == query2.strip().lower()


# Global instance
_global_evaluator: PolicyEvaluator | None = None


def get_policy_evaluator() -> PolicyEvaluator:
    """Get or create the global policy evaluator."""
    global _global_evaluator
    if _global_evaluator is None:
        _global_evaluator = PolicyEvaluator()
    return _global_evaluator
