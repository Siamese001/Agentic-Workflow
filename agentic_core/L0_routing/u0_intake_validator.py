"""U0 Intake Validator — AG-RGGOV-W6 Core Contract

U0 validates AppsRgIngressPayload and emits ValidatedRequest.

Responsibilities:
- Validate ingress payload from apps_rg
- Ensure no forbidden authority fields present
- Emit ValidatedRequest with validation receipt

Hard Constraints:
- Core owns all validation
- apps_rg does not validate — only produces ingress payload
- Contract dataclasses are defined in runtime/contracts/, imported here
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    ValidatedRequest,
)

_logger = logging.getLogger(__name__)

_L5_CERT_REF_FAIL_CLOSED = os.getenv("L5_CERT_REF_FAIL_CLOSED", "0") == "1"


def _check_l5_cert_ref(ref: str, stage: str) -> None:
    """Fail-soft L5 cert ref verify per AG-W0-3=A_consume_entry, AG-W0-5=A_fail_soft_env_gate.

    Logs a warning when ref is empty/invalid. Raises only when
    ``L5_CERT_REF_FAIL_CLOSED=1``.
    """
    try:
        from agentic_core.L5_safety.contracts.registry import verify_certification_ref
        valid = verify_certification_ref(ref)
    except Exception as exc:  # guardian: allow-log-and-swallow -- L5 registry import must not crash pipeline; treat as unverified
        _logger.warning("L5CertRefViolation stage=%s registry_error=%s", stage, exc)
        return
    if not valid:
        msg = "L5CertRefViolation stage=%s ref=%r — missing or invalid l5_certification_ref"
        if _L5_CERT_REF_FAIL_CLOSED:
            raise ValueError(msg % (stage, ref))
        _logger.warning(msg, stage, ref)


@dataclass(frozen=True, slots=True)
class AuthorityValidationReceipt:
    """Receipt proving U0 validation occurred."""

    validation_timestamp: str
    validator_version: str = "W6.0"
    forbidden_fields_checked: tuple[str, ...] = field(default_factory=tuple)
    validation_passed: bool = True


class U0IntakeValidator:
    """U0 intake validation layer for apps_rg ingress.

    Validates AppsRgIngressPayload and emits ValidatedRequest.
    """

    FORBIDDEN_AUTHORITY_FIELDS: tuple[str, ...] = (
        "route_id",
        "execution_form",
        "provider",
        "workflow_dag",
        "llm_gateway",
        "model_endpoint",
    )

    def validate(self, ingress_payload: AppsRgIngressPayload) -> ValidatedRequest:
        """Validate ingress payload and emit ValidatedRequest.

        Args:
            ingress_payload: apps_rg ingress payload to validate

        Returns:
            ValidatedRequest with validation receipt

        Raises:
            ValueError: If forbidden authority fields detected
        """
        # Check for forbidden authority fields
        self._check_forbidden_fields(ingress_payload)

        # L1 entry: verify upstream (ingress) l5_certification_ref (AG-W0-3)
        _check_l5_cert_ref(
            getattr(ingress_payload, "l5_certification_ref", ""),
            stage="U0_intake",
        )

        # Generate trace ID
        import uuid

        trace_id = str(uuid.uuid4())

        # Build validation receipt
        receipt = AuthorityValidationReceipt(
            validation_timestamp=datetime.now(timezone.utc).isoformat(),
            validator_version="W6.0",
            forbidden_fields_checked=self.FORBIDDEN_AUTHORITY_FIELDS,
            validation_passed=True,
        )

        return ValidatedRequest(
            request_id=ingress_payload.idempotency_key or str(uuid.uuid4()),
            run_id=str(uuid.uuid4()),
            app_id=ingress_payload.app_id,
            task_class=ingress_payload.task_class,
            payload_digest=ingress_payload.payload_digest,
            authority_validation_receipt=receipt,
            trace_id=trace_id,
            l5_certification_ref=ingress_payload.l5_certification_ref,
        )

    def _check_forbidden_fields(self, payload: AppsRgIngressPayload) -> None:
        """Check for forbidden authority fields in payload."""
        # Convert payload to dict for field checking
        payload_dict = payload.__dict__ if hasattr(payload, "__dict__") else {}

        for forbidden_field in self.FORBIDDEN_AUTHORITY_FIELDS:
            if forbidden_field in payload_dict and payload_dict[forbidden_field]:
                raise ValueError(
                    f"Forbidden authority field detected in ingress: {forbidden_field}"
                )
