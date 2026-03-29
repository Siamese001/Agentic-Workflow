"""
apps_lic domain types package.

Lead Intelligence & Campaign (LIC) domain contracts.
All types carry provenance. No silent pass — all failures recorded.
"""

from apps_lic.types.validation_result_types import (
    Draft,
    DraftPackage,
    ValidationResult,
    check_content_compliance,
    score_quality,
    validate_schema_policy,
)

__all__ = [
    "Draft",
    "DraftPackage",
    "ValidationResult",
    "check_content_compliance",
    "score_quality",
    "validate_schema_policy",
]
