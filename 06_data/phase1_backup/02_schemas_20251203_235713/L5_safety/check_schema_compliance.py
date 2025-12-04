"""
Schema definitions for schema compliance checking and verification.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class ComplianceStandard(Enum):
    """Compliance standards for schemas."""
    ISO_19115 = "iso_19115"
    DUBLIN_CORE = "dublin_core"
    SCHEMA_ORG = "schema_org"
    CUSTOM_STANDARD = "custom_standard"


class ComplianceStatus(Enum):
    """Compliance status levels."""
    FULLY_COMPLIANT = "fully_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceRequirement:
    """Schema for individual compliance requirement."""
    requirement_id: str
    standard: ComplianceStandard
    requirement_type: str
    description: str
    mandatory: bool = True


@dataclass
class ComplianceCheck:
    """Schema for compliance check result."""
    requirement_id: str
    is_compliant: bool
    evidence: Optional[Dict[str, Any]] = None
    gaps_identified: Optional[List[str]] = None


@dataclass
class ComplianceReport:
    """Schema for complete compliance report."""
    schema_id: str
    standard: ComplianceStandard
    overall_status: ComplianceStatus
    compliance_score: float
    checks: List[ComplianceCheck]
    report_timestamp: str