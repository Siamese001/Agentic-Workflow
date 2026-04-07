"""
Collateral Summary Parser - Parses appraisal and collateral documents.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ParsedCollateralSummary:
    """Result of parsing collateral summary or appraisal."""
    collateral_type: Optional[str] = None
    appraised_value: Optional[float] = None
    estimated_value: Optional[float] = None
    appraisal_date: Optional[str] = None
    appraiser_name: Optional[str] = None
    lien_position: Optional[str] = None
    condition_rating: Optional[str] = None
    confidence: float = 0.0


class CollateralSummaryParser:
    """
    Parses collateral summary documents and appraisals.
    """

    def parse(self, file_path: Path, text_content: Optional[str] = None) -> ParsedCollateralSummary:
        """Parse collateral document."""
        result = ParsedCollateralSummary()

        if text_content is None:
            text_content = self._extract_text(file_path)

        if not text_content:
            return result

        # Extract values
        result.appraised_value = self._extract_appraised_value(text_content)
        result.estimated_value = result.appraised_value  # Use appraised as estimate
        result.appraisal_date = self._extract_appraisal_date(text_content)
        result.appraiser_name = self._extract_appraiser(text_content)
        result.collateral_type = self._extract_collateral_type(text_content)
        result.condition_rating = self._extract_condition_rating(text_content)

        result.confidence = 0.6 if result.appraised_value else 0.0

        return result

    def _extract_text(self, file_path: Path) -> Optional[str]:
        """Extract text from document."""
        return None

    def _extract_appraised_value(self, text: str) -> Optional[float]:
        """Extract appraised value."""
        patterns = [
            r'(?:Appraised Value|Fair Market Value|Value)[\s:]*[$]?([\d,\.]+)',
            r'(?:As of|Report Date)[^\n]*?\$?([\d,\.]{6,})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None

    def _extract_appraisal_date(self, text: str) -> Optional[str]:
        """Extract appraisal date."""
        pattern = r'(?:Appraisal Date|Report Date|Date of Value)[:\s]+([A-Z][a-z]+ \d{1,2},? \d{4}|\d{4}-\d{2}-\d{2})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _extract_appraiser(self, text: str) -> Optional[str]:
        """Extract appraiser name."""
        pattern = r'(?:Appraiser|Prepared By)[:\s]+([^\n]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_collateral_type(self, text: str) -> Optional[str]:
        """Extract collateral type."""
        types = [
            ('real estate', 'real_estate'),
            ('equipment', 'equipment'),
            ('inventory', 'inventory'),
            ('accounts receivable', 'ar'),
            ('ar', 'ar'),
        ]

        text_lower = text.lower()
        for keyword, collateral_type in types:
            if keyword in text_lower:
                return collateral_type
        return None

    def _extract_condition_rating(self, text: str) -> Optional[str]:
        """Extract condition rating."""
        pattern = r'(?:Condition|Rating)[:\s]+(Good|Fair|Poor|Excellent|New)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
