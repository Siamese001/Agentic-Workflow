"""Validates that an UnderwritingRequest has the required fields set.

The required-field set is configurable per product_class. Defaults cover
the universal contract (request_id / applicant_id / product_class).
"""
from __future__ import annotations

from typing import Any, Mapping

from apps_underwriting_ai.types.underwriting_types import UnderwritingRequest
from apps_underwriting_ai.validators.base_validator import (
    BaseValidator,
    ValidationResult,
)


_UNIVERSAL_REQUIRED: tuple[str, ...] = (
    "request_id",
    "applicant_id",
    "product_class",
)

_PER_PRODUCT_REQUIRED: Mapping[str, tuple[str, ...]] = {
    "auto": ("request_id", "applicant_id", "product_class"),
    "small_business_loan": ("request_id", "applicant_id", "product_class"),
}


class RequiredFieldValidator(BaseValidator):
    """Ensure an UnderwritingRequest has all required fields populated.

    ``.validate(request=<UnderwritingRequest>)`` returns:
      - ``passed=True`` when every required field is non-empty
      - ``passed=False`` otherwise, with ``context["missing"]`` listing the
        offending field names.
    """

    name = "required_field"

    def validate(self, **kwargs: Any) -> ValidationResult:
        request = kwargs.get("request")
        if not isinstance(request, UnderwritingRequest):
            return ValidationResult(
                validator=self.name,
                passed=False,
                severity="error",
                message="request keyword is not an UnderwritingRequest",
                context={"type": type(request).__name__},
            )
        required = _PER_PRODUCT_REQUIRED.get(
            request.product_class, _UNIVERSAL_REQUIRED
        )
        missing: list[str] = []
        for field_name in required:
            value = getattr(request, field_name, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field_name)
        if missing:
            return ValidationResult(
                validator=self.name,
                passed=False,
                severity="error",
                message=f"missing required field(s): {', '.join(missing)}",
                context={"missing": tuple(missing), "product_class": request.product_class},
            )
        return ValidationResult(
            validator=self.name,
            passed=True,
            severity="info",
            message="all required fields populated",
            context={"checked": required, "product_class": request.product_class},
        )
