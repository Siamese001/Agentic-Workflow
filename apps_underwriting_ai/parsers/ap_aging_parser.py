"""
AP Aging Parser - Parses accounts payable aging schedules.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class APBucket:
    """Single AP aging bucket."""

    bucket_name: str
    amount: Optional[float] = None


@dataclass
class ParsedAPAging:
    """Result of parsing AP aging schedule."""

    buckets: List[APBucket] = field(default_factory=list)
    total_ap: Optional[float] = None
    days_payable_outstanding: Optional[int] = None
    confidence: float = 0.0


class APAgingParser:
    """
    Parses accounts payable aging schedules.
    """

    def parse(self, file_path: Path, text_content: Optional[str] = None) -> ParsedAPAging:
        """Parse AP aging document."""
        result = ParsedAPAging()

        if text_content is None:
            text_content = self._extract_text(file_path)

        if not text_content:
            return result

        # Extract AP buckets
        result.buckets = self._extract_buckets(text_content)
        result.total_ap = self._extract_total_ap(text_content)

        result.confidence = min(1.0, len(result.buckets) * 0.2) if result.buckets else 0.0

        return result

    def _extract_text(self, file_path: Path) -> Optional[str]:
        """Extract text from document."""
        return None

    def _extract_buckets(self, text: str) -> List[APBucket]:
        """Extract aging buckets."""
        buckets = []

        bucket_patterns = [
            (r"(?:Current|0-30)[\s:]*[$]?([\d,\.]+)", "Current"),
            (r"(?:31-60|31\s*-\s*60)[\s:]*[$]?([\d,\.]+)", "31-60"),
            (r"(?:61-90|61\s*-\s*90)[\s:]*[$]?([\d,\.]+)", "61-90"),
            (r"(?:90\+|Over\s*90)[\s:]*[$]?([\d,\.]+)", "90+"),
        ]

        for pattern, bucket_name in bucket_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(",", ""))
                    buckets.append(APBucket(bucket_name=bucket_name, amount=amount))
                except ValueError:
                    continue

        return buckets

    def _extract_total_ap(self, text: str) -> Optional[float]:
        """Extract total AP."""
        patterns = [
            r"(?:Total Accounts Payable|Total A/P|Grand Total)[\s:]*[$]?([\d,\.]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(",", ""))
                except ValueError:
                    continue
        return None
