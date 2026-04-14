"""
Structured Ingestion - Normalizes and maps structured data to canonical schema.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from tqdm import tqdm


class IngestionMode(Enum):
    """Ingestion strictness mode."""

    STRICT = "strict"  # Reject unknown critical fields
    LENIENT = "lenient"  # Warn on unknown fields but continue
    PERMISSIVE = "permissive"  # Ignore unknown fields


@dataclass
class MappingResult:
    """Result of field mapping operation."""

    data: Optional[Dict[str, Any]] = None
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    field_mapping_log: Dict[str, str] = field(default_factory=dict)


class StructuredIngestion:
    """
    Maps JSON/CSV/XLSX field names into canonical schema.

    Responsibilities:
    - Normalize field names
    - Standardize period labels
    - Normalize booleans, enums, and nulls
    - Log field-level source provenance
    """

    # Common field name mappings (source -> canonical)
    FIELD_MAPPINGS = {
        # Borrower fields
        "company_name": "legal_name",
        "entity_name": "legal_name",
        "business_name": "legal_name",
        "naics_code": "industry_code",
        "sic_code": "industry_code",
        "years_operating": "years_in_business",
        "date_founded": "years_in_business",
        # Financial fields
        "sales": "revenue",
        "total_revenue": "revenue",
        "operating_income": "ebitda",
        "adjusted_ebitda": "ebitda",
        "net_operating_income": "ebitda",
        "accounts_receivable": "ar",
        "a_r": "ar",
        "accounts_payable": "ap",
        "a_p": "ap",
        "inventory_value": "inventory",
        "cash_equivalents": "cash",
        "total_liabilities": "total_debt",
        # Request fields
        "loan_amount": "requested_amount",
        "facility_amount": "requested_amount",
        "loan_term": "requested_term_months",
        "tenor": "requested_term_months",
        "facility_type": "product_type",
        # Credit fields
        "business_score": "business_bureau_score",
        "paydex": "business_bureau_score",
        "fico_score": "personal_fico_scores",
        "delinquencies": "delinquencies_24m",
        # Collateral fields
        "collateral_value": "estimated_value",
        "appraised_value": "estimated_value",
        "advance_rate": "advance_rate_pct",
        # Banking fields
        "monthly_deposits": "avg_monthly_deposits_12m",
        "average_balance": "avg_ending_balance_12m",
        "nsf_count": "nsf_count_12m",
        # Document fields
        "financials": "financial_statements",
        "tax_return": "tax_returns",
        "bank_statement": "bank_statements",
    }

    def __init__(self, mode: IngestionMode = IngestionMode.LENIENT):
        self.mode = mode

    def normalize_field_names(
        self,
        data: Dict[str, Any],
        field_map: Optional[Dict[str, str]] = None,
    ) -> MappingResult:
        """
        Normalize field names to canonical schema.

        Args:
            data: Raw input data
            field_map: Optional additional field mappings

        Returns:
            MappingResult with normalized data
        """
        result = MappingResult()
        normalized = {}

        # Merge default and custom mappings
        mappings = {**self.FIELD_MAPPINGS}
        if field_map:
            mappings.update(field_map)

        for raw_field, value in data.items():
            # Apply mapping if exists
            canonical_field = mappings.get(raw_field.lower().replace(" ", "_"), raw_field)
            normalized[canonical_field] = value

            if raw_field != canonical_field:
                result.field_mapping_log[raw_field] = canonical_field
                result.warnings.append(
                    f"Mapped field '{raw_field}' to '{canonical_field}'",
                )

        result.data = normalized
        return result

    def normalize_booleans(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize boolean representations to Python bool."""
        bool_trues = {"yes", "true", "1", "y", "t", "on"}
        bool_falses = {"no", "false", "0", "n", "f", "off", "none", "null", ""}

        normalized = {}
        for key, value in tqdm(data.items(), desc="Processing", unit="item"):
            if isinstance(value, str):
                lower_val = value.lower().strip()
                if lower_val in bool_trues:
                    normalized[key] = True
                elif lower_val in bool_falses:
                    normalized[key] = False
                else:
                    normalized[key] = value
            elif isinstance(value, dict):
                normalized[key] = self.normalize_booleans(value)
            elif isinstance(value, list):
                normalized[key] = [
                    self.normalize_booleans(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                normalized[key] = value

        return normalized

    def standardize_periods(
        self,
        periods: list[Dict[str, Any]],
    ) -> list[Dict[str, Any]]:
        """Standardize period labels and validate dates."""
        standardized = []

        for period in tqdm(periods, desc="Processing", unit="item"):
            std_period = dict(period)

            # Standardize date format
            if "period_end" in period:
                date_val = period["period_end"]
                if isinstance(date_val, str):
                    # Try to parse and reformat
                    try:
                        # Handle various formats
                        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
                            try:
                                dt = datetime.strptime(date_val, fmt)
                                std_period["period_end"] = dt.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass  # Keep original if parsing fails

            # Standardize fiscal type
            if "fiscal_type" in period:
                ft = str(period["fiscal_type"]).lower()
                if ft in ["annual", "year", "yearly", "fy"]:
                    std_period["fiscal_type"] = "annual"
                elif ft in ["quarterly", "quarter", "q"]:
                    std_period["fiscal_type"] = "quarterly"
                elif ft in ["ttm", "trailing", "12m", "12 months"]:
                    std_period["fiscal_type"] = "ttm"

            standardized.append(std_period)

        # Sort by period_end
        return sorted(standardized, key=lambda x: x.get("period_end", ""))

    def validate_required_fields(
        self,
        data: Dict[str, Any],
        required: list[str],
    ) -> list[str]:
        """Validate that required fields are present."""
        errors = []
        for field in required:
            if field not in data or data[field] is None or data[field] == "":
                errors.append(f"Missing required field: {field}")
        return errors

    def normalize_nulls(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize null-like values to None."""
        null_values = {"null", "none", "n/a", "na", "undefined", "", "NULL", "None"}

        normalized = {}
        for key, value in tqdm(data.items(), desc="Processing", unit="item"):
            if isinstance(value, str) and value.strip().lower() in null_values:
                normalized[key] = None
            elif isinstance(value, dict):
                normalized[key] = self.normalize_nulls(value)
            elif isinstance(value, list):
                normalized[key] = [
                    self.normalize_nulls(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                normalized[key] = value

        return normalized

    def log_field_provenance(
        self,
        field_name: str,
        source_value: Any,
        normalized_value: Any,
        transformation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log field-level provenance information."""
        return {
            "field": field_name,
            "source_value": source_value,
            "normalized_value": normalized_value,
            "transformation": transformation,
            "timestamp": datetime.now().isoformat(),
        }
