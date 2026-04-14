"""
Stale Data Validator - Inspects document dates for staleness.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional

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

    def __init__(self, now_provider: Optional[Callable[[], datetime]] = None):
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def validate(
        self,
        request: UnderwritingRequest | Mapping[str, Any],
    ) -> StaleDataResult:
        """
        Validate document freshness.

        Args:
            request: UnderwritingRequest

        Returns:
            StaleDataResult
        """
        result = StaleDataResult()

        if isinstance(request, Mapping):
            self._validate_mapping_payload(result, request)
        else:
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

    def _validate_mapping_payload(
        self,
        result: StaleDataResult,
        payload: Mapping[str, Any],
    ) -> None:
        """Support lightweight dict payloads used in smoke tests and adapters."""
        timestamp = payload.get("timestamp")
        if timestamp is not None:
            doc_dt = self._parse_timestamp(timestamp)
            if doc_dt is not None:
                age_days = (self._now_provider() - doc_dt).days
                if age_days > 1:
                    result.stale_items.append(
                        {
                            "document_type": "timestamp",
                            "date": doc_dt.isoformat(),
                            "age_days": age_days,
                            "max_age_days": 1,
                            "severity": "critical" if age_days > 2 else "warning",
                        }
                    )

        for field_name, doc_type in (("appraisal_date", "appraisal"), ("field_exam_date", "field_exam")):
            date_value = payload.get(field_name)
            if isinstance(date_value, str):
                self._check_date_freshness(result, doc_type, date_value)

    def _check_date_freshness(
        self,
        result: StaleDataResult,
        doc_type: str,
        date_str: str,
    ) -> None:
        """Check if a date is stale."""
        doc_date = self._parse_date(date_str)
        if doc_date is None:
            return

        age_days = (self._now_provider() - doc_date).days
        max_age = self.MAX_AGE_DAYS.get(doc_type, 365)

        if age_days > max_age * 1.5:
            severity = "critical"
        elif age_days > max_age:
            severity = "warning"
        else:
            return

        result.stale_items.append(
            {
                "document_type": doc_type,
                "date": date_str,
                "age_days": age_days,
                "max_age_days": max_age,
                "severity": severity,
            }
        )

    @staticmethod
    def _parse_timestamp(timestamp_value: Any) -> Optional[datetime]:
        """Parse unix timestamps or ISO strings into timezone-aware datetimes."""
        if isinstance(timestamp_value, (int, float)):
            return datetime.fromtimestamp(timestamp_value, tz=timezone.utc)
        if isinstance(timestamp_value, str):
            return StaleDataValidator._parse_date(timestamp_value)
        return None

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """Parse supported date formats into timezone-aware datetimes."""
        candidate = (date_str or "").strip()
        if not candidate:
            return None
        normalized = candidate.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            try:
                parsed = datetime.strptime(candidate[:10], "%Y-%m-%d")
            except ValueError:
                return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
