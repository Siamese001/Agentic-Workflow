"""Historical research briefing prerequisite validator.

Enforces that apps_rg static DAG only executes when:
1. Historical research briefing exists for target job/company
2. Briefing is fresh (within TTL)
3. Briefing is policy compatible
4. Briefing is blueprint compatible
5. Briefing is linked to current apps_rg request scope

If any check fails, L0 must route to apps_research first.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

_logger = logging.getLogger(__name__)


class BriefingValidationResult(Enum):
    """Validation outcomes for historical research briefing."""

    VALID = "valid"  # Briefing exists and is usable
    MISSING = "missing"  # No briefing found
    STALE = "stale"  # Briefing exists but exceeds TTL
    POLICY_MISMATCH = "policy_mismatch"  # Policy hash mismatch
    BLUEPRINT_MISMATCH = "blueprint_mismatch"  # Blueprint hash mismatch
    SCOPE_MISMATCH = "scope_mismatch"  # Company/role mismatch
    INCOMPLETE = "incomplete"  # Briefing missing required fields


@dataclass(frozen=True)
class BriefingCheck:
    """Result of historical briefing prerequisite check."""

    result: BriefingValidationResult
    briefing: Optional[dict] = None
    reason: str = ""
    freshness_hours: Optional[float] = None

    @property
    def is_valid(self) -> bool:
        """True if briefing passes all prerequisite checks."""
        return self.result == BriefingValidationResult.VALID

    @property
    def requires_apps_research(self) -> bool:
        """True if apps_research must run to produce/refresh briefing."""
        return self.result in {
            BriefingValidationResult.MISSING,
            BriefingValidationResult.STALE,
            BriefingValidationResult.INCOMPLETE,
        }


class HistoricalBriefingValidator:
    """Validate historical research briefing for apps_rg routing."""

    # Default TTL: 30 days for company briefings
    DEFAULT_TTL_HOURS = 24 * 30

    def __init__(
        self,
        policy_hash: str,
        blueprint_hash: str,
        tenant_id: str = "default",
    ):
        self.policy_hash = policy_hash
        self.blueprint_hash = blueprint_hash
        self.tenant_id = tenant_id

    def validate_for_request(
        self,
        target_company: str,
        target_role: str,
        briefing_path: Optional[Path] = None,
    ) -> BriefingCheck:
        """Validate historical briefing for apps_rg request.

        This is the L0 prerequisite gate — it runs BEFORE L2 DAG execution.
        """
        # Try to load briefing
        briefing = self._load_briefing(target_company, briefing_path)

        if briefing is None:
            return BriefingCheck(
                result=BriefingValidationResult.MISSING,
                reason=f"No historical briefing found for {target_company}",
            )

        # Check scope match (company/role)
        if not self._check_scope_match(briefing, target_company, target_role):
            return BriefingCheck(
                result=BriefingValidationResult.SCOPE_MISMATCH,
                briefing=briefing,
                reason=f"Briefing scope mismatch: "
                f"company={briefing.get('company', 'unknown')}, role context mismatch",
            )

        # Check completeness
        if not self._check_completeness(briefing):
            return BriefingCheck(
                result=BriefingValidationResult.INCOMPLETE,
                briefing=briefing,
                reason="Briefing missing required fields (mission, culture, or recent news)",
            )

        # Check freshness
        freshness = self._calculate_freshness(briefing)
        if freshness > self.DEFAULT_TTL_HOURS:
            return BriefingCheck(
                result=BriefingValidationResult.STALE,
                briefing=briefing,
                reason=f"Briefing stale: {freshness:.1f}h old (TTL={self.DEFAULT_TTL_HOURS}h)",
                freshness_hours=freshness,
            )

        # Check policy compatibility
        if not self._check_policy_compatibility(briefing):
            return BriefingCheck(
                result=BriefingValidationResult.POLICY_MISMATCH,
                briefing=briefing,
                reason=f"Policy hash mismatch: briefing produced under different policy",
                freshness_hours=freshness,
            )

        # Check blueprint compatibility
        if not self._check_blueprint_compatibility(briefing):
            return BriefingCheck(
                result=BriefingValidationResult.BLUEPRINT_MISMATCH,
                briefing=briefing,
                reason=f"Blueprint hash mismatch: briefing structure changed",
                freshness_hours=freshness,
            )

        # All checks passed
        return BriefingCheck(
            result=BriefingValidationResult.VALID,
            briefing=briefing,
            reason="Historical briefing valid and compatible",
            freshness_hours=freshness,
        )

    def _load_briefing(
        self,
        target_company: str,
        explicit_path: Optional[Path] = None,
    ) -> Optional[dict]:
        """Load briefing from explicit path or lookup by company."""
        if explicit_path and explicit_path.exists():
            try:
                data = json.loads(explicit_path.read_text(encoding="utf-8"))
                return data
            except Exception as exc:  # guardian: allow-broad-exception -- load is fail-soft
                _logger.warning("Failed to load explicit briefing: %s", exc)

        # Lookup via apps_research facade (L4 cache)
        try:
            from apps_shared.adapters.research_facade import lookup_cached_brief

            return lookup_cached_brief(target_company, tenant_id=self.tenant_id)
        except ImportError:
            _logger.debug("research_facade not available for briefing lookup")
        except Exception as exc:
            _logger.debug("Briefing lookup failed: %s", exc)

        return None

    def _check_scope_match(
        self,
        briefing: dict,
        target_company: str,
        target_role: str,
    ) -> bool:
        """Check if briefing covers the target company/role."""
        # Company name match (case-insensitive, normalized)
        briefing_company = briefing.get("company", "").lower().strip()
        target_company_norm = target_company.lower().strip()

        if briefing_company != target_company_norm:
            return False

        # Role match: briefing should have relevant context for target role
        role_context = briefing.get("role_context", "")
        if role_context:
            briefing_role = str(role_context).lower()
            target_role_norm = target_role.lower()
            # Simple substring check — real impl uses semantic similarity
            return (
                target_role_norm in briefing_role
                or briefing_role in target_role_norm
                or self._role_similarity(briefing_role, target_role_norm) > 0.7
            )

        return True  # No role context in briefing = assume compatible

    def _check_completeness(self, briefing: dict) -> bool:
        """Check if briefing has all required fields."""
        required_fields = ["company", "mission", "culture"]
        for field in required_fields:
            value = briefing.get(field)
            if not value or (isinstance(value, list) and len(value) == 0):
                return False

        # Also check for recent_news or recent_developments
        news = briefing.get("recent_news") or briefing.get("recent_developments")
        if not news or (isinstance(news, list) and len(news) == 0):
            return False

        return True

    def _calculate_freshness(self, briefing: dict) -> float:
        """Calculate age of briefing in hours."""
        fetched_at_str = briefing.get("fetched_at") or briefing.get("created_at")
        if not fetched_at_str:
            return float("inf")  # Unknown age = treat as stale

        try:
            # Parse ISO timestamp
            if isinstance(fetched_at_str, str):
                # Handle various ISO formats
                fetched_at = datetime.fromisoformat(fetched_at_str.replace("Z", "+00:00"))
            elif isinstance(fetched_at_str, datetime):
                fetched_at = fetched_at_str
            else:
                return float("inf")

            # Ensure timezone-aware
            if fetched_at.tzinfo is None:
                fetched_at = fetched_at.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            age = now - fetched_at
            return age.total_seconds() / 3600
        except Exception:
            return float("inf")

    def _check_policy_compatibility(self, briefing: dict) -> bool:
        """Check if briefing was produced under compatible policy."""
        briefing_policy = briefing.get("policy_hash")
        if briefing_policy is None:
            return True  # No policy hash = assume compatible (legacy briefing)
        return briefing_policy == self.policy_hash

    def _check_blueprint_compatibility(self, briefing: dict) -> bool:
        """Check if briefing structure matches current blueprint."""
        briefing_blueprint = briefing.get("blueprint_hash")
        if briefing_blueprint is None:
            return True  # No blueprint hash = assume compatible
        return briefing_blueprint == self.blueprint_hash

    def _role_similarity(self, role1: str, role2: str) -> float:
        """Calculate similarity between two role strings."""
        # Simplified: real impl uses embedding similarity
        words1 = set(role1.split())
        words2 = set(role2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2
        if not union:
            return 0.0
        return len(intersection) / len(union)


def check_briefing_prerequisite(
    target_company: str,
    target_role: str,
    policy_hash: str,
    blueprint_hash: str,
    briefing_path: Optional[Path] = None,
    **kwargs,
) -> BriefingCheck:
    """High-level briefing prerequisite check for L0 routing."""
    validator = HistoricalBriefingValidator(
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        tenant_id=kwargs.get("tenant_id", "default"),
    )
    return validator.validate_for_request(target_company, target_role, briefing_path)


__all__ = [
    "BriefingValidationResult",
    "BriefingCheck",
    "HistoricalBriefingValidator",
    "check_briefing_prerequisite",
]
