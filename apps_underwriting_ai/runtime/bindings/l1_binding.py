"""L1 plan binding for apps_underwriting_ai.

Thin pass-through: the underwriting domain does not require a separate
cognition/planning stage. L1 accepts the ValidatedUnderwritingRequest
from U0 and returns it wrapped in a minimal UWL1Plan that carries the
validated request forward to L0.

Pattern: pure function. No state. No I/O. No provider calls.
AppIngressRunner calls: l1_fn(validated) → l1_plan

Plan: apps-underwriting-ai-profile-migration (Bundle B).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_underwriting_ai.runtime.contracts.underwriting_ingress_payload import (
    ValidatedUnderwritingRequest,
)

UW_L1_CERT_REF: str = "l1-apps-underwriting-ai-underwriting-decision-passthrough-v1"


@dataclass
class UWL1Plan:
    """Minimal L1 plan output for underwriting — carries validated request forward.

    Underwriting has no separate cognition/planning phase. L1 is a thin
    pass-through whose sole job is to preserve the ValidatedUnderwritingRequest
    for downstream stages and emit the l5_certification_ref required by
    AppIngressRunner contracts.
    """

    validated_request: ValidatedUnderwritingRequest
    request_id: str
    applicant_id: str
    product_class: str
    task_class: str
    app_id: str
    l5_certification_ref: str
    l1_cert_ref: str = UW_L1_CERT_REF
    metadata: dict[str, Any] = field(default_factory=dict)


def l1_plan_underwriting(validated: ValidatedUnderwritingRequest) -> UWL1Plan:
    """Pass-through L1 stage for underwriting.

    Accepts the ValidatedUnderwritingRequest from U0 and returns a
    UWL1Plan carrying it forward unchanged. Called by AppIngressRunner
    as l1_fn(validated).

    Args:
        validated: U0-validated underwriting request.

    Returns:
        UWL1Plan with the validated request forwarded intact.
    """
    return UWL1Plan(
        validated_request=validated,
        request_id=validated.request_id,
        applicant_id=validated.applicant_id,
        product_class=validated.product_class,
        task_class=validated.task_class,
        app_id=validated.app_id,
        l5_certification_ref=validated.u0_cert_ref or UW_L1_CERT_REF,
    )


__all__ = [
    "UW_L1_CERT_REF",
    "UWL1Plan",
    "l1_plan_underwriting",
]
