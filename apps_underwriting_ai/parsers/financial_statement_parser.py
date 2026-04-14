"""
Financial Statement Parser - Parses PDF financial statements.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm


@dataclass
class ParsedFinancialStatement:
    """Result of parsing a financial statement."""

    period_end: Optional[str] = None
    revenue: Optional[float] = None
    cogs: Optional[float] = None
    gross_profit: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    cash: Optional[float] = None
    ar: Optional[float] = None
    inventory: Optional[float] = None
    ap: Optional[float] = None
    total_assets: Optional[float] = None
    total_debt: Optional[float] = None
    tangible_net_worth: Optional[float] = None
    confidence: float = 0.0
    raw_excerpts: Dict[str, str] = field(default_factory=dict)


class FinancialStatementParser:
    """
    Parses financial statement PDFs to extract structured data.

    In production, would integrate with document parsing services.
    For now, provides deterministic extraction patterns.
    """

    # Common financial statement patterns
    PATTERNS = {
        "revenue": [
            r"(?:Revenue|Sales|Total Revenue)[\s:]*[$]?([\d,\.]+)",
            r"(?:Revenue|Sales)[^\n]*?([\d,\.]{5,})",
        ],
        "cogs": [
            r"(?:Cost of Goods Sold|COGS)[\s:]*[$]?([\d,\.]+)",
        ],
        "gross_profit": [
            r"(?:Gross Profit|Gross Margin)[\s:]*[$]?([\d,\.]+)",
        ],
        "ebitda": [
            r"(?:EBITDA|Adjusted EBITDA)[\s:]*[$]?([\d,\.]+)",
            r"(?:EBITDA)[^\n]*?([\d,\.]{5,})",
        ],
        "net_income": [
            r"(?:Net Income|Net Profit|Bottom Line)[\s:]*[$]?([\d,\.]+)",
        ],
        "cash": [
            r"(?:Cash and Equivalents|Cash)[\s:]*[$]?([\d,\.]+)",
        ],
        "ar": [
            r"(?:Accounts Receivable|A\/R)[\s:]*[$]?([\d,\.]+)",
        ],
        "inventory": [
            r"(?:Inventory)[\s:]*[$]?([\d,\.]+)",
        ],
        "ap": [
            r"(?:Accounts Payable|A\/P)[\s:]*[$]?([\d,\.]+)",
        ],
        "total_assets": [
            r"(?:Total Assets)[\s:]*[$]?([\d,\.]+)",
        ],
        "total_debt": [
            r"(?:Total Debt|Total Liabilities)[\s:]*[$]?([\d,\.]+)",
        ],
    }

    def parse(self, file_path: Path, text_content: Optional[str] = None) -> ParsedFinancialStatement:
        """
        Parse a financial statement document.

        Args:
            file_path: Path to document
            text_content: Pre-extracted text content (optional)

        Returns:
            ParsedFinancialStatement with extracted fields
        """
        result = ParsedFinancialStatement()

        # Get text content
        if text_content is None:
            text_content = self._extract_text(file_path)

        if not text_content:
            return result

        # Extract period end date
        result.period_end = self._extract_period_end(text_content)

        # Extract financial values
        extracted_count = 0
        for field_name, patterns in self.PATTERNS.items():
            value = self._extract_with_patterns(text_content, patterns)
            if value is not None:
                setattr(result, field_name, value)
                extracted_count += 1
                # Store raw excerpt for evidence
                result.raw_excerpts[field_name] = self._get_excerpt(text_content, patterns[0])

        # Calculate confidence based on extraction coverage
        result.confidence = min(1.0, extracted_count / len(self.PATTERNS))

        return result

    def _extract_text(self, file_path: Path) -> Optional[str]:
        """Extract text from document."""
        # In production, would use OCR or PDF text extraction
        # For now, return placeholder
        return None

    def _extract_with_patterns(self, text: str, patterns: List[str]) -> Optional[float]:
        """Extract numeric value using regex patterns."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Clean and parse the number
                    number_str = match.group(1).replace(",", "").replace("$", "")
                    return float(number_str)
                except (ValueError, IndexError):
                    continue
        return None

    def _extract_period_end(self, text: str) -> Optional[str]:
        """Extract period end date from statement."""
        # Common patterns for period dates
        date_patterns = [
            r"(?:For the Period|Period End|Fiscal Year|Year) Ended?[:\s]+([A-Z][a-z]+ \d{1,2},? \d{4})",
            r"(?:As of|Balance Sheet)[:\s]+([A-Z][a-z]+ \d{1,2},? \d{4})",
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{1,2}/\d{1,2}/\d{4})",
        ]

        for pattern in tqdm(date_patterns, desc="Processing", unit="item"):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Normalize to YYYY-MM-DD
                try:
                    from datetime import datetime

                    for fmt in ["%B %d, %Y", "%B %d %Y", "%Y-%m-%d", "%m/%d/%Y"]:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            return dt.strftime("%Y-%m-%d")
                        except ValueError:
                            continue
                except Exception:
                    return date_str
        return None

    def _get_excerpt(self, text: str, pattern: str, context_chars: int = 100) -> str:
        """Get text excerpt around pattern match."""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)
            return text[start:end].strip()
        return ""
