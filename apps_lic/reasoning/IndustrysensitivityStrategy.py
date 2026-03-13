"""Governance Shield Types - Passive type definitions for governance bounds.

These are passive data structures (Enums, BaseModel) used by the GovernanceShieldAgent.
"""

from enum import Enum, IntEnum

from pydantic import BaseModel, Field


class IndustrySensitivity(str, Enum):
    """Industry risk sensitivity levels."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskProfile(BaseModel):
    """Risk profile for target company and role."""

    industry_sensitivity: IndustrySensitivity = Field(..., description="Industry risk level")
    compliance_keywords: list[str] = Field(default_factory=list, description="Required compliance frameworks")
    data_sensitivity: list[str] = Field(default_factory=list, description="Sensitive data types")

    @property
    def is_high_risk(self) -> bool:
        """Check if this is a high-risk profile."""
        return self.industry_sensitivity == IndustrySensitivity.HIGH


class SafetyProtocol(BaseModel):
    """Safety protocol for AI systems."""

    validation_strategy: str = Field(..., description="Model validation approach")
    data_privacy_approach: str = Field(..., description="Data privacy protection method")
    human_in_the_loop_policy: str = Field(..., description="Human oversight requirements")
    compliance_frameworks: list[str] = Field(default_factory=list, description="Compliance standards")

    @property
    def is_comprehensive(self) -> bool:
        """Check if protocol covers all major areas."""
        return all([self.validation_strategy, self.data_privacy_approach, self.human_in_the_loop_policy])


class GovernanceShieldLevel(IntEnum):
    """Risk enforcement levels for outreach governance."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
