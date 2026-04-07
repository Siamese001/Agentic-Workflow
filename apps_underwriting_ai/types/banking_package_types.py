"""
Banking Package Types - Domain contracts for banking relationship data.
"""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

DepositTrend = Literal["up", "flat", "down", "unknown"]


class BankingPackage(BaseModel):
    """
    Banking relationship and deposit analysis.
    """
    avg_monthly_deposits_12m: Optional[float] = Field(None, ge=0, description="Average monthly deposits")
    avg_ending_balance_12m: Optional[float] = Field(None, description="Average ending balance")
    nsf_count_12m: Optional[int] = Field(None, ge=0, description="NSF count in last 12 months")
    overdraft_days_12m: Optional[int] = Field(None, ge=0, description="Days in overdraft")
    cash_volatility_score: Optional[float] = Field(None, description="Cash volatility score (0-1, higher=more volatile)")
    deposit_trend: DepositTrend = Field("unknown", description="Deposit trend direction")
    bank_statement_flags: List[str] = Field(default_factory=list, description="Banking flags")

    class Config:
        json_schema_extra = {
            "example": {
                "avg_monthly_deposits_12m": 980000.0,
                "avg_ending_balance_12m": 425000.0,
                "nsf_count_12m": 2,
                "overdraft_days_12m": 8,
                "cash_volatility_score": 0.23,
                "deposit_trend": "up",
                "bank_statement_flags": [],
            },
        }
