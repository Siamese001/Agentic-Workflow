"""Pre-retrieval Gate.

Strict pre-filtering to prevent wasted retrieval and cross-scope contamination.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class AccessDecision(Enum):
    """Decision from pre-retrieval gate."""
    ALLOW = "allow"
    DENY = "deny"
    RESTRICTED = "restricted"
    REQUIRE_AUTH = "require_auth"


@dataclass
class FilterResult:
    """Result of filter evaluation."""
    filter_name: str
    passed: bool
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GateDecision:
    """Final gate decision."""
    decision: AccessDecision
    query_id: str
    allowed_filters: Dict[str, Any] = field(default_factory=dict)
    denied_filters: List[FilterResult] = field(default_factory=list)
    scope_metadata: Dict[str, Any] = field(default_factory=dict)
    reason: Optional[str] = None


class PreRetrievalGate:
    """Pre-retrieval gate for strict pre-filtering.

    The PreRetrievalGate enforces filters BEFORE any retrieval or cache
    lookup to prevent wasted operations and cross-scope contamination.
    """

    def __init__(self):
        """Initialize the pre-retrieval gate."""
        self._filters: Dict[str, callable] = {}
        self._setup_default_filters()
        log.info("PreRetrievalGate initialized")

    def _setup_default_filters(self):
        """Setup default security filters."""
        self._filters = {
            "tenant": self._filter_tenant,
            "acl": self._filter_acl,
            "region": self._filter_region,
            "confidentiality": self._filter_confidentiality,
            "temporal": self._filter_temporal,
            "freshness": self._filter_freshness,
        }

    def evaluate(
        self,
        query_id: str,
        query_context: Dict[str, Any],
        required_filters: Optional[List[str]] = None,
    ) -> GateDecision:
        """Evaluate query against all filters.

        Args:
            query_id: Unique query identifier
            query_context: Context with filter parameters
            required_filters: List of filter names to apply (all if None)

        Returns:
            GateDecision with access determination
        """
        trace_id = f"gate_{query_id}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "PreRetrievalGate.evaluate"
        )

        filters_to_apply = required_filters or list(self._filters.keys())

        allowed_filters: Dict[str, Any] = {}
        denied_filters: List[FilterResult] = []

        for filter_name in filters_to_apply:
            if filter_name not in self._filters:
                log.warning(f"Unknown filter: {filter_name}")
                continue

            filter_fn = self._filters[filter_name]
            result = filter_fn(query_context)

            if result.passed:
                allowed_filters[filter_name] = result.metadata
            else:
                denied_filters.append(result)

        # Determine final decision
        if denied_filters:
            decision = AccessDecision.DENY
            reason = f"Failed filters: {', '.join(d.result for d in denied_filters)}"
        else:
            decision = AccessDecision.ALLOW
            reason = None

        gate_decision = GateDecision(
            decision=decision,
            query_id=query_id,
            allowed_filters=allowed_filters,
            denied_filters=denied_filters,
            scope_metadata=allowed_filters,
            reason=reason,
        )

        _emit_records_telemetry_event(
            "pre_retrieval_gate",
            f"{decision.value}_{query_id}"
        )

        log.info(f"Gate decision for {query_id}: {decision.value}")
        return gate_decision

    def add_filter(self, name: str, filter_fn: callable) -> None:
        """Add a custom filter.

        Args:
            name: Filter name
            filter_fn: Function that takes context and returns FilterResult
        """
        self._filters[name] = filter_fn
        log.info(f"Added filter: {name}")

    def remove_filter(self, name: str) -> bool:
        """Remove a filter.

        Args:
            name: Filter name to remove

        Returns:
            True if removed, False if not found
        """
        if name in self._filters:
            del self._filters[name]
            log.info(f"Removed filter: {name}")
            return True
        return False

    def _filter_tenant(self, context: Dict[str, Any]) -> FilterResult:
        """Filter by tenant isolation."""
        tenant_id = context.get("tenant_id")
        if not tenant_id:
            return FilterResult(
                filter_name="tenant",
                passed=True,
                reason="No tenant specified (public access)",
            )

        # Check if tenant matches
        query_tenant = context.get("query_tenant")
        if query_tenant and query_tenant != tenant_id:
            return FilterResult(
                filter_name="tenant",
                passed=False,
                reason=f"Tenant mismatch: {query_tenant} != {tenant_id}",
            )

        return FilterResult(
            filter_name="tenant",
            passed=True,
            metadata={"tenant_id": tenant_id},
        )

    def _filter_acl(self, context: Dict[str, Any]) -> FilterResult:
        """Filter by access control list."""
        user_perms = context.get("user_permissions", [])
        required_perms = context.get("required_permissions", [])

        if not required_perms:
            return FilterResult(
                filter_name="acl",
                passed=True,
                reason="No permissions required",
            )

        missing = [p for p in required_perms if p not in user_perms]
        if missing:
            return FilterResult(
                filter_name="acl",
                passed=False,
                reason=f"Missing permissions: {', '.join(missing)}",
            )

        return FilterResult(
            filter_name="acl",
            passed=True,
            metadata={"permissions": user_perms},
        )

    def _filter_region(self, context: Dict[str, Any]) -> FilterResult:
        """Filter by geographic region."""
        user_region = context.get("user_region")
        allowed_regions = context.get("allowed_regions", [])

        if not allowed_regions:
            return FilterResult(
                filter_name="region",
                passed=True,
                reason="No region restrictions",
            )

        if user_region not in allowed_regions:
            return FilterResult(
                filter_name="region",
                passed=False,
                reason=f"Region {user_region} not in allowed list",
            )

        return FilterResult(
            filter_name="region",
            passed=True,
            metadata={"region": user_region},
        )

    def _filter_confidentiality(self, context: Dict[str, Any]) -> FilterResult:
        """Filter by confidentiality level."""
        user_clearance = context.get("user_clearance", "public")
        doc_classification = context.get("document_classification", "public")

        # Clearance levels (higher = more access)
        levels = ["public", "internal", "confidential", "restricted", "secret"]

        user_level = levels.index(user_clearance) if user_clearance in levels else 0
        doc_level = levels.index(doc_classification) if doc_classification in levels else 0

        if user_level < doc_level:
            return FilterResult(
                filter_name="confidentiality",
                passed=False,
                reason=f"Insufficient clearance: {user_clearance} < {doc_classification}",
            )

        return FilterResult(
            filter_name="confidentiality",
            passed=True,
            metadata={
                "user_clearance": user_clearance,
                "doc_classification": doc_classification,
            },
        )

    def _filter_temporal(self, context: Dict[str, Any]) -> FilterResult:
        """Filter by temporal constraints."""
        effective_date = context.get("effective_date")
        expiry_date = context.get("expiry_date")

        now = datetime.utcnow()

        if effective_date:
            effective = datetime.fromisoformat(effective_date) if isinstance(effective_date, str) else effective_date
            if now < effective:
                return FilterResult(
                    filter_name="temporal",
                    passed=False,
                    reason=f"Not yet effective: {effective_date}",
                )

        if expiry_date:
            expiry = datetime.fromisoformat(expiry_date) if isinstance(expiry_date, str) else expiry_date
            if now > expiry:
                return FilterResult(
                    filter_name="temporal",
                    passed=False,
                    reason=f"Expired: {expiry_date}",
                )

        return FilterResult(
            filter_name="temporal",
            passed=True,
            metadata={
                "effective": effective_date,
                "expiry": expiry_date,
            },
        )

    def _filter_freshness(self, context: Dict[str, Any]) -> FilterResult:
        """Filter by data freshness requirements."""
        freshness_band = context.get("freshness_band")  # "realtime", "hourly", "daily"
        last_updated = context.get("last_updated")

        if not freshness_band or not last_updated:
            return FilterResult(
                filter_name="freshness",
                passed=True,
                reason="No freshness requirements",
            )

        # Calculate age
        if isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated)

        age_hours = (datetime.utcnow() - last_updated).total_seconds() / 3600

        # Check against band
        band_limits = {
            "realtime": 0.083,  # 5 minutes
            "hourly": 1.0,
            "daily": 24.0,
            "weekly": 168.0,
        }

        limit = band_limits.get(freshness_band, 24.0)

        if age_hours > limit:
            return FilterResult(
                filter_name="freshness",
                passed=False,
                reason=f"Data too old: {age_hours:.1f}h > {limit}h ({freshness_band})",
            )

        return FilterResult(
            filter_name="freshness",
            passed=True,
            metadata={
                "freshness_band": freshness_band,
                "age_hours": age_hours,
            },
        )


# Global instance
_global_gate: Optional[PreRetrievalGate] = None


def get_pre_retrieval_gate() -> PreRetrievalGate:
    """Get or create the global pre-retrieval gate."""
    global _global_gate
    if _global_gate is None:
        _global_gate = PreRetrievalGate()
    return _global_gate


def check_access(
    query_id: str,
    context: Dict[str, Any],
) -> GateDecision:
    """Convenience function to check access."""
    return get_pre_retrieval_gate().evaluate(query_id, context)
