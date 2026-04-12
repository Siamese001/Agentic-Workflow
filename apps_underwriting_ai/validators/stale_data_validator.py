"""
Stale Data Validator - Inspects document dates for staleness.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from ..types import UnderwritingRequest


@dataclass
class StaleDataResult:
    """Result of stale data validation."""

    fresh: bool = True
    staleness_score: float = 0.0
    stale_items: List[Dict[str, Any]] = field(default_factory=list)
    requires_update: bool = False


class StaleDataValidator:
    """
    Validates that documents are not stale.

    Checks:
    - Financial statement dates
    - Appraisal dates
    - Tax return dates
    - Bank statement dates
    """

    # Maximum age in days by document type
    MAX_AGE_DAYS = {
        "financial_statement": 365,
        "tax_return": 180,
        "bank_statement": 90,
        "ar_aging": 60,
        "ap_aging": 60,
        "debt_schedule": 90,
        "appraisal": 365,
        "field_exam": 180,
    }

    def validate(
        self,
        request: UnderwritingRequest,
    ) -> StaleDataResult:
        """
        Validate document freshness.

        Args:
            request: UnderwritingRequest

        Returns:
            StaleDataResult
        """
        result = StaleDataResult()

        # Check financial periods
        if request.financials.periods:
            latest = request.financials.periods[-1]
            if latest.period_end:
                self._check_date_freshness(
                    result,
                    "financial_statement",
                    latest.period_end,
                )

        # Check collateral appraisal
        if request.collateral.appraisal_date:
            self._check_date_freshness(
                result,
                "appraisal",
                request.collateral.appraisal_date,
            )

        # Check field exam
        if request.collateral.field_exam_date:
            self._check_date_freshness(
                result,
                "field_exam",
                request.collateral.field_exam_date,
            )

        # Calculate overall staleness score
        if result.stale_items:
            total_weight = sum(1.0 if item["severity"] == "critical" else 0.5 for item in result.stale_items)
            result.staleness_score = min(1.0, total_weight / 3.0)

        # Determine if update is required
        result.requires_update = any(item["severity"] == "critical" for item in result.stale_items)

        result.fresh = len(result.stale_items) == 0

        return result

    def _check_date_freshness(
        self,
        result: StaleDataResult,
        doc_type: str,
        date_str: str,
    ) -> None:
        """Check if a date is stale."""
        try:
            # Parse date
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                try:
                    doc_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    break
                except ValueError:
                    continue
            else:
                return

            # Calculate age
            age_days = (datetime.now() - doc_date).days
            max_age = self.MAX_AGE_DAYS.get(doc_type, 365)

            # Determine severity
            if age_days > max_age * 1.5:
                severity = "critical"
            elif age_days > max_age:
                severity = "warning"
            else:
                return  # Fresh enough

            result.stale_items.append(
                {
                    "document_type": doc_type,
                    "date": date_str,
                    "age_days": age_days,
                    "max_age_days": max_age,
                    "severity": severity,
                }
            )

        except Exception:
            pass  # Skip if date parsing fails
