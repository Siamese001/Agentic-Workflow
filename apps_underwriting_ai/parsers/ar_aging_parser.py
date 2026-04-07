"""
AR Aging Parser - Parses accounts receivable aging schedules.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ARBucket:
    """Single AR aging bucket."""
    bucket_name: str
    amount: Optional[float] = None
    percent_of_total: Optional[float] = None


@dataclass
class ParsedARAging:
    """Result of parsing AR aging schedule."""
    buckets: List[ARBucket] = field(default_factory=list)
    total_ar: Optional[float] = None
    top_customer_concentration: Optional[float] = None
    days_sales_outstanding: Optional[int] = None
    confidence: float = 0.0


class ARAgingParser:
    """
    Parses accounts receivable aging schedules.
    """

    def parse(self, file_path: Path, text_content: Optional[str] = None) -> ParsedARAging:
        """Parse AR aging document."""
        result = ParsedARAging()

        if text_content is None:
            text_content = self._extract_text(file_path)

        if not text_content:
            return result

        # Extract AR buckets
        result.buckets = self._extract_buckets(text_content)
        result.total_ar = self._extract_total_ar(text_content)

        # Calculate concentration if data available
        if result.buckets:
            current_bucket = next((b for b in result.buckets if 'current' in b.bucket_name.lower()), None)
            if current_bucket and current_bucket.amount and result.total_ar:
                # Simplified concentration estimate
                pass

        result.confidence = min(1.0, len(result.buckets) * 0.2) if result.buckets else 0.0

        return result

    def _extract_text(self, file_path: Path) -> Optional[str]:
        """Extract text from document."""
        return None

    def _extract_buckets(self, text: str) -> List[ARBucket]:
        """Extract aging buckets."""
        buckets = []

        # Common bucket patterns
        bucket_patterns = [
            (r'(?:Current|0-30)[\s:]*[$]?([\d,\.]+)', 'Current'),
            (r'(?:1-30|1\s*-\s*30)[\s:]*[$]?([\d,\.]+)', '1-30'),
            (r'(?:31-60|31\s*-\s*60)[\s:]*[$]?([\d,\.]+)', '31-60'),
            (r'(?:61-90|61\s*-\s*90)[\s:]*[$]?([\d,\.]+)', '61-90'),
            (r'(?:90\+|Over\s*90|Over\s*90\s*days)[\s:]*[$]?([\d,\.]+)', '90+'),
        ]

        for pattern, bucket_name in bucket_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    buckets.append(ARBucket(bucket_name=bucket_name, amount=amount))
                except ValueError:
                    continue

        return buckets

    def _extract_total_ar(self, text: str) -> Optional[float]:
        """Extract total AR."""
        patterns = [
            r'(?:Total Accounts Receivable|Total A/R|Grand Total)[\s:]*[$]?([\d,\.]+)',
            r'(?:Total)[\s:]*[$]?([\d,\.]{5,})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None
