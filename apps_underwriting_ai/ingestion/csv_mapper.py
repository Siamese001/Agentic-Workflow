"""
CSV Mapper - Maps CSV data to UnderwritingRequest domain model.
"""

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..types import UnderwritingRequest
from .structured_ingestion import StructuredIngestion


@dataclass
class CSVMappingResult:
    """Result of CSV mapping."""

    request: Optional[UnderwritingRequest] = None
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)


class CSVMapper:
    """Maps CSV data to canonical UnderwritingRequest."""

    def __init__(self):
        self.structured = StructuredIngestion()

    def map_to_request(
        self,
        data: Union[str, Path],
        mapping_config: Optional[Dict[str, str]] = None,
        request_id: Optional[str] = None,
    ) -> CSVMappingResult:
        """
        Map CSV data to UnderwritingRequest.

        Args:
            data: CSV file path or string
            mapping_config: Field name mappings
            request_id: Optional request ID

        Returns:
            CSVMappingResult
        """
        result = CSVMappingResult()

        try:
            # Read CSV
            if isinstance(data, Path):
                with open(data, "r", encoding="utf-8", newline="") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
            else:
                reader = csv.DictReader(io.StringIO(data))
                rows = list(reader)

            if not rows:
                result.errors.append("CSV file is empty")
                return result

            # Flatten single row to dict
            raw_data = rows[0]

            # Apply field mappings if provided
            if mapping_config:
                mapped_data = {}
                for csv_field, value in raw_data.items():
                    canonical_field = mapping_config.get(csv_field, csv_field)
                    mapped_data[canonical_field] = value
                raw_data = mapped_data

            # Build nested structure from flat CSV
            structured_data = self._flatten_to_nested(raw_data)

            # Use JSON mapper to complete
            from .json_mapper import JSONMapper

            json_mapper = JSONMapper()
            json_result = json_mapper.map_to_request(
                structured_data,
                request_id=request_id,
            )

            result.request = json_result.request
            result.warnings = json_result.warnings
            result.errors = json_result.errors

        except Exception as e:
            result.errors.append(f"CSV mapping error: {str(e)}")

        return result

    def _flatten_to_nested(self, flat_data: Dict[str, str]) -> Dict[str, Any]:
        """Convert flat CSV fields to nested structure."""
        nested = {}

        # Simple field mappings
        direct_fields = [
            "request_id",
            "submission_ts",
            "product_type",
            "decision_type",
            "requested_amount",
            "requested_term_months",
            "legal_name",
            "entity_type",
            "industry_code",
            "industry_description",
            "years_in_business",
            "state_of_incorporation",
            "employee_count",
        ]

        for field in direct_fields:
            if field in flat_data:
                nested[field] = flat_data[field]

        # Build borrower substructure
        borrower_fields = [
            "legal_name",
            "entity_type",
            "industry_code",
            "industry_description",
            "years_in_business",
            "state_of_incorporation",
            "employee_count",
            "operating_states",
            "naics_risk_flags",
            "sanctions_or_watchlist_hits",
        ]
        nested["borrower"] = {}
        for field in borrower_fields:
            if field in flat_data:
                nested["borrower"][field] = flat_data[field]

        # Build requested structure
        if any(
            f in flat_data
            for f in ["amortization_months", "interest_type", "collateral_required", "guarantor_required"]
        ):
            nested["requested_structure"] = {}
            if "amortization_months" in flat_data:
                nested["requested_structure"]["amortization_months"] = flat_data["amortization_months"]
            if "interest_type" in flat_data:
                nested["requested_structure"]["interest_type"] = flat_data["interest_type"]
            if "collateral_required" in flat_data:
                nested["requested_structure"]["collateral_required"] = flat_data["collateral_required"]
            if "guarantor_required" in flat_data:
                nested["requested_structure"]["guarantor_required"] = flat_data["guarantor_required"]

        # Build financials (simplified single period)
        financial_fields = [
            "revenue",
            "cogs",
            "gross_profit",
            "ebitda",
            "net_income",
            "cash",
            "ar",
            "inventory",
            "ap",
            "total_assets",
            "total_debt",
            "tangible_net_worth",
            "interest_expense",
            "debt_service",
        ]
        if any(f in flat_data for f in financial_fields):
            nested["financials"] = {"periods": [{}]}
            for field in financial_fields:
                if field in flat_data:
                    nested["financials"]["periods"][0][field] = flat_data[field]
            if "period_end" in flat_data:
                nested["financials"]["periods"][0]["period_end"] = flat_data["period_end"]
            if "fiscal_type" in flat_data:
                nested["financials"]["periods"][0]["fiscal_type"] = flat_data["fiscal_type"]

        # Build collateral
        collateral_fields = [
            "collateral_type",
            "estimated_value",
            "advance_rate_pct",
            "borrowing_base_value",
            "lien_position",
            "appraisal_date",
            "field_exam_date",
        ]
        if any(f in flat_data for f in collateral_fields):
            nested["collateral"] = {}
            for field in collateral_fields:
                if field in flat_data:
                    nested["collateral"][field] = flat_data[field]

        # Build credit
        credit_fields = [
            "business_bureau_score",
            "personal_fico_scores",
            "delinquencies_24m",
            "defaults_ever",
            "bankruptcies_ever",
            "judgments_or_liens",
            "tradeline_utilization_pct",
        ]
        if any(f in flat_data for f in credit_fields):
            nested["credit"] = {}
            for field in credit_fields:
                if field in flat_data:
                    nested["credit"][field] = flat_data[field]

        # Build banking
        banking_fields = [
            "avg_monthly_deposits_12m",
            "avg_ending_balance_12m",
            "nsf_count_12m",
            "overdraft_days_12m",
            "cash_volatility_score",
            "deposit_trend",
        ]
        if any(f in flat_data for f in banking_fields):
            nested["banking"] = {}
            for field in banking_fields:
                if field in flat_data:
                    nested["banking"][field] = flat_data[field]

        return nested
