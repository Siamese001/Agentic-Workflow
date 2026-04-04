"""
Financial Package Types - Domain contracts for financial statement data.
"""
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


FiscalType = Literal["annual", "quarterly", "ttm"]


class FinancialPeriod(BaseModel):
    """Single period financial statement data."""
    period_end: str = Field(..., description="Period end date (YYYY-MM-DD)")
    fiscal_type: FiscalType = Field(..., description="Annual, quarterly, or trailing twelve months")
    revenue: float = Field(..., description="Revenue for period")
    cogs: Optional[float] = Field(None, description="Cost of goods sold")
    gross_profit: Optional[float] = Field(None, description="Gross profit")
    ebitda: Optional[float] = Field(None, description="EBITDA")
    net_income: Optional[float] = Field(None, description="Net income")
    cash: Optional[float] = Field(None, description="Cash and equivalents")
    ar: Optional[float] = Field(None, description="Accounts receivable")
    inventory: Optional[float] = Field(None, description="Inventory")
    ap: Optional[float] = Field(None, description="Accounts payable")
    total_assets: Optional[float] = Field(None, description="Total assets")
    total_debt: Optional[float] = Field(None, description="Total debt")
    tangible_net_worth: Optional[float] = Field(None, description="Tangible net worth")
    interest_expense: Optional[float] = Field(None, description="Interest expense")
    debt_service: Optional[float] = Field(None, description="Annual debt service")


class CalculatedMetrics(BaseModel):
    """Derived financial metrics calculated from periods."""
    revenue_cagr_2y: Optional[float] = Field(None, description="2-year revenue CAGR")
    ebitda_margin_ttm: Optional[float] = Field(None, description="TTM EBITDA margin")
    debt_to_ebitda_ttm: Optional[float] = Field(None, description="TTM Debt/EBITDA")
    dscr_ttm: Optional[float] = Field(None, description="TTM DSCR")
    current_ratio: Optional[float] = Field(None, description="Current ratio")
    quick_ratio: Optional[float] = Field(None, description="Quick ratio")
    debt_to_tnw: Optional[float] = Field(None, description="Debt to tangible net worth")


class FinancialPackage(BaseModel):
    """
    Complete financial package with periods and calculated metrics.
    """
    periods: List[FinancialPeriod] = Field(default_factory=list, description="Financial periods")
    calculated_metrics: CalculatedMetrics = Field(default_factory=CalculatedMetrics, description="Derived metrics")
    quality_flags: List[str] = Field(default_factory=list, description="Data quality flags")

    @validator('periods')
    def validate_periods(cls, v):
        """Ensure at least one period if not empty."""
        if not v:
            return v
        # Sort by period_end
        return sorted(v, key=lambda x: x.period_end)

    class Config:
        json_schema_extra = {
            "example": {
                "periods": [
                    {
                        "period_end": "2023-12-31",
                        "fiscal_type": "annual",
                        "revenue": 12500000.0,
                        "ebitda": 1875000.0,
                        "total_debt": 3500000.0,
                        "debt_service": 525000.0,
                        "cash": 850000.0,
                        "ar": 2100000.0,
                        "ap": 950000.0
                    },
                    {
                        "period_end": "2022-12-31",
                        "fiscal_type": "annual",
                        "revenue": 11000000.0,
                        "ebitda": 1540000.0
                    }
                ],
                "calculated_metrics": {
                    "revenue_cagr_2y": 0.136,
                    "ebitda_margin_ttm": 0.15,
                    "debt_to_ebitda_ttm": 1.87,
                    "dscr_ttm": 3.57
                },
                "quality_flags": []
            }
        }
