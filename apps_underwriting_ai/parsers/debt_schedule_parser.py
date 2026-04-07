"""
Debt Schedule Parser - Parses debt schedules from uploaded documents.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DebtEntry:
    """Single debt entry from schedule."""
    lender: str
    facility_type: str
    original_balance: Optional[float] = None
    current_balance: Optional[float] = None
    maturity_date: Optional[str] = None
    interest_rate: Optional[float] = None
    monthly_payment: Optional[float] = None
    secured_by: Optional[str] = None
    status: str = "current"


@dataclass
class ParsedDebtSchedule:
    """Result of parsing a debt schedule."""
    entries: List[DebtEntry] = field(default_factory=list)
    total_current_debt: Optional[float] = None
    total_monthly_debt_service: Optional[float] = None
    annual_debt_service: Optional[float] = None
    confidence: float = 0.0
    raw_excerpts: Dict[str, str] = field(default_factory=dict)


class DebtScheduleParser:
    """
    Parses debt schedule documents to extract liability information.
    """

    def parse(self, file_path: Path, text_content: Optional[str] = None) -> ParsedDebtSchedule:
        """Parse debt schedule document."""
        result = ParsedDebtSchedule()

        if text_content is None:
            text_content = self._extract_text(file_path)

        if not text_content:
            return result

        # Extract debt entries using table patterns
        result.entries = self._extract_debt_entries(text_content)

        # Calculate totals
        if result.entries:
            result.total_current_debt = sum(
                e.current_balance or 0 for e in result.entries
            )
            result.total_monthly_debt_service = sum(
                e.monthly_payment or 0 for e in result.entries
            )
            result.annual_debt_service = (result.total_monthly_debt_service or 0) * 12

        # Calculate confidence
        result.confidence = min(1.0, len(result.entries) * 0.2) if result.entries else 0.0

        return result

    def _extract_text(self, file_path: Path) -> Optional[str]:
        """Extract text from document."""
        return None

    def _extract_debt_entries(self, text: str) -> List[DebtEntry]:
        """Extract individual debt entries from text."""
        entries = []

        # Look for debt facility patterns
        # This is a simplified extraction - production would use more sophisticated parsing
        patterns = [
            r'([^\n]+?)\s+(Term Loan|Line of Credit|Revolver|Equipment Loan|Real Estate Loan)[\s\S]*?\$?([\d,\.]+)[\s\S]*?\$?([\d,\.]+)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    entry = DebtEntry(
                        lender=match.group(1).strip() if len(match.groups()) > 0 else "Unknown",
                        facility_type=match.group(2) if len(match.groups()) > 1 else "Unknown",
                        current_balance=float(match.group(3).replace(',', '')) if len(match.groups()) > 2 else None,
                    )
                    entries.append(entry)
                except (ValueError, IndexError):
                    continue

        return entries
