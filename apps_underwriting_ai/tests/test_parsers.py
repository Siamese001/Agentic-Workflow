"""Tests for apps_underwriting_ai parser components."""


from apps_underwriting_ai.parsers.bank_statement_parser import (
    BankStatementParser,
)
from apps_underwriting_ai.parsers.financial_statement_parser import (
    FinancialStatementParser,
)


class TestFinancialStatementParser:
    """Test FinancialStatementParser."""

    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = FinancialStatementParser()
        assert parser is not None

    def test_parse_empty_data(self):
        """Test parsing empty data."""
        parser = FinancialStatementParser()
        # Test with empty data - should handle gracefully
        result = parser.parse({})
        assert result is not None


class TestBankStatementParser:
    """Test BankStatementParser."""

    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = BankStatementParser()
        assert parser is not None

    def test_parse_empty_data(self):
        """Test parsing empty data."""
        parser = BankStatementParser()
        # Test with empty data - should handle gracefully
        result = parser.parse({})
        assert result is not None
