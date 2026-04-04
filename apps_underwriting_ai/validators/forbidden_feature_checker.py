"""
Forbidden Feature Checker - Ensures prohibited attributes are not used.
"""
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field

from ..types import UnderwritingRequest, RiskFeatures


@dataclass
class ForbiddenCheckResult:
    """Result of forbidden feature check."""
    passed: bool = True
    violations: List[Dict[str, Any]] = field(default_factory=list)
    blocked_fields: List[str] = field(default_factory=list)


class ForbiddenFeatureChecker:
    """
    Validates that prohibited attributes are not used in rationale or features.

    Blocks direct or proxy use of:
    - Race
    - Religion
    - Gender
    - Marital status
    - Protected demographic proxies
    """

    # Explicitly forbidden fields
    FORBIDDEN_FIELDS: Set[str] = {
        "race",
        "ethnicity",
        "religion",
        "gender",
        "sex",
        "marital_status",
        "sexual_orientation",
        "national_origin",
        "disability_status",
        "age",  # Age at application (vs years_in_business)
        "veteran_status",
    }

    # Proxy indicators that may suggest forbidden attribute use
    PROXY_INDICATORS: Set[str] = {
        "minority_owned",
        "woman_owned",
        "veteran_owned",
        "protected_class",
        "demographic",
        "ethnic",
        "racial",
    }

    # Permitted fields that may sound similar but are allowed
    PERMITTED_FIELDS: Set[str] = {
        "years_in_business",  # Business age, not owner age
        "entity_type",  # LLC/Corp, not protected class
        "industry_code",  # NAICS, not demographic
        "industry_description",
    }

    def check_request(
        self,
        request: UnderwritingRequest
    ) -> ForbiddenCheckResult:
        """
        Check request for forbidden features.

        Args:
            request: UnderwritingRequest to validate

        Returns:
            ForbiddenCheckResult
        """
        result = ForbiddenCheckResult()

        # Check borrower profile for forbidden fields
        self._check_borrower_profile(request, result)

        # Check for proxy indicators in all text fields
        self._check_proxy_indicators(request, result)

        result.passed = len(result.violations) == 0

        return result

    def _check_borrower_profile(
        self,
        request: UnderwritingRequest,
        result: ForbiddenCheckResult
    ) -> None:
        """Check borrower profile for forbidden fields."""
        borrower = request.borrower

        # Convert to dict for checking
        borrower_dict = borrower.dict() if hasattr(borrower, 'dict') else {}

        for forbidden in self.FORBIDDEN_FIELDS:
            if forbidden in borrower_dict and borrower_dict[forbidden] is not None:
                result.violations.append({
                    "type": "forbidden_field_present",
                    "field": f"borrower.{forbidden}",
                    "severity": "blocking",
                    "message": f"Forbidden field '{forbidden}' present in borrower profile"
                })
                result.blocked_fields.append(forbidden)

    def _check_proxy_indicators(
        self,
        request: UnderwritingRequest,
        result: ForbiddenCheckResult
    ) -> None:
        """Check for proxy indicators in text fields."""
        # Check industry description
        industry_desc = request.borrower.industry_description.lower()

        for proxy in self.PROXY_INDICATORS:
            if proxy.lower() in industry_desc:
                # This is a warning, not a blocking violation
                result.violations.append({
                    "type": "proxy_indicator_detected",
                    "field": "borrower.industry_description",
                    "indicator": proxy,
                    "severity": "warning",
                    "message": f"Potential demographic proxy '{proxy}' detected in industry description"
                })

    def validate_feature_derivation(
        self,
        features: RiskFeatures,
        rationale: str
    ) -> ForbiddenCheckResult:
        """
        Validate that feature derivation rationale doesn't use forbidden logic.

        Args:
            features: Derived RiskFeatures
            rationale: Feature derivation rationale text

        Returns:
            ForbiddenCheckResult
        """
        result = ForbiddenCheckResult()

        if not rationale:
            return result

        rationale_lower = rationale.lower()

        # Check for forbidden terms in rationale
        for forbidden in self.FORBIDDEN_FIELDS:
            if forbidden in rationale_lower:
                result.violations.append({
                    "type": "forbidden_term_in_rationale",
                    "term": forbidden,
                    "severity": "blocking",
                    "message": f"Forbidden term '{forbidden}' detected in rationale"
                })

        result.passed = len(result.violations) == 0

        return result
