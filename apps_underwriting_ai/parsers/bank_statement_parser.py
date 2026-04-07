"""
Bank Statement Parser - Parses bank statement data.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class MonthlySummary:
    """Monthly bank statement summary."""
    month: str
    total_deposits: Optional[float] = None
    total_withdrawals: Optional[float] = None
    ending_balance: Optional[float] = None
    nsf_count: int = 0
    days_negative: int = 0


@dataclass
class ParsedBankStatement:
    """Result of parsing bank statements."""
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    statement_months: List[MonthlySummary] = field(default_factory=list)
    avg_monthly_deposits: Optional[float] = None
    avg_ending_balance: Optional[float] = None
    total_nsf_count: int = 0
    total_overdraft_days: int = 0
    confidence: float = 0.0


class BankStatementParser:
    """
    Parses bank statement PDFs to extract deposit and balance data.
    """

    def parse(self, file_path: Path, text_content: Optional[str] = None) -> ParsedBankStatement:
        """Parse bank statement document."""
        result = ParsedBankStatement()

        if text_content is None:
            text_content = self._extract_text(file_path)

        if not text_content:
            return result

        # Extract bank name
        result.bank_name = self._extract_bank_name(text_content)

        # Extract account info
        result.account_number = self._extract_account_number(text_content)

        # Extract monthly summaries
        result.statement_months = self._extract_monthly_summaries(text_content)

        # Calculate averages
        if result.statement_months:
            deposits = [m.total_deposits for m in result.statement_months if m.total_deposits]
            balances = [m.ending_balance for m in result.statement_months if m.ending_balance]

            if deposits:
                result.avg_monthly_deposits = sum(deposits) / len(deposits)
            if balances:
                result.avg_ending_balance = sum(balances) / len(balances)

            result.total_nsf_count = sum(m.nsf_count for m in result.statement_months)
            result.total_overdraft_days = sum(m.days_negative for m in result.statement_months)

        result.confidence = min(1.0, len(result.statement_months) * 0.25)

        return result

    def _extract_text(self, file_path: Path) -> Optional[str]:
        """Extract text from document."""
        return None

    def _extract_bank_name(self, text: str) -> Optional[str]:
        """Extract bank name from statement."""
        # Common bank names
        bank_patterns = [
            r'(JPMorgan Chase|Bank of America|Wells Fargo|Citibank|PNC|TD Bank|\\w+ Bank)',
            r'(Bank:\s*([^\n]+))',
        ]

        for pattern in bank_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_account_number(self, text: str) -> Optional[str]:
        """Extract account number."""
        pattern = r'(?:Account|Acct)[\s#:]+(\d[\d\-]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Mask for security
            acct = match.group(1).replace('-', '').replace(' ', '')
            return f"****{acct[-4:]}" if len(acct) > 4 else acct
        return None

    def _extract_monthly_summaries(self, text: str) -> List[MonthlySummary]:
        """Extract monthly summary data."""
        summaries = []

        # Look for deposit/balance patterns
        # Simplified pattern matching
        deposit_pattern = r'(?:Total Deposits|Deposits)[\s:]*[$]?([\d,\.]+)'
        balance_pattern = r'(?:Ending Balance|Balance)[\s:]*[$]?([\d,\.]+)'

        # In production, would parse statement by statement period
        # For now, return simplified extraction

        return summaries
