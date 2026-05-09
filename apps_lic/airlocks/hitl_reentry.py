"""HITL Re-Entry Airlock — isolates human-provided input when workflow resumes.

Per PROMPT_BOUNDARY_CONTRACT.md §3.4: Human edits are data until re-cleared.
They cannot directly write L4, bypass L5, bypass Runtime Gates, bypass Exit,
widen capability/sandbox scope.

This airlock coordinates with apps_lic/coordination/hitl_escalation.py and
delegates actual content validation to U0 + C0 airlocks (which are re-run
on re-entered content).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from apps_rg.prompt_assembly._pa_boundary import make_pa_boundary_receipt, PABoundaryStatus
from apps_rg.airlocks._otel_spans import airlock_span

_log = logging.getLogger(__name__)


class HITLReentryStatus(str, Enum):
    """Status of HITL re-entry validation."""

    CLEARED = "CLEARED"  # Re-entered content passed U0/C0
    QUARANTINED = "QUARANTINED"  # Flagged for further review
    REJECTED = "REJECTED"  # Failed validation, workflow abort


class HITLModificationScope(str, Enum):
    """Classification of human modification scope."""

    DATA_EDIT_ONLY = "DATA_EDIT_ONLY"  # Edits to content, not structure
    STRUCTURE_CHANGE = "STRUCTURE_CHANGE"  # Route/step/schema changes proposed
    AUTHORITY_CLAIM = "AUTHORITY_CLAIM"  # Attempt to widen authority


@dataclass(frozen=True)
class HITLReentryResult:
    """Result of HITL re-entry airlock processing."""

    modification_hash: str
    status: str
    scope_classification: str
    audit_trail: dict[str, Any]
    receipt: dict[str, Any]
    u0_result: dict[str, Any] | None  # Delegated U0 result
    c0_result: dict[str, Any] | None  # Delegated C0 result (if applicable)


class HITLReentryAirlock:
    """HITL Re-Entry Airlock.

    When human edits are re-ingested after HITL resolution, this airlock:
    1. Captures audit trail (who, when, what was modified)
    2. Classifies modification scope
    3. Delegates content validation to U0 + C0 airlocks
    4. Emits HITL_REENTRY receipt
    """

    def __init__(self):
        # Suspicious modification patterns suggesting authority claims
        self._authority_claim_patterns = [
            "bypass",
            "skip",
            "ignore",
            "override",
            "disable",
            "change route",
            "switch model",
            "different tool",
            "write directly",
            "commit now",
        ]

    def process_reentry(
        self,
        *,
        review_id: str,
        resolved_by: str,
        resolution: str,  # approved, approved_with_edits, rejected, etc.
        modifications: dict[str, Any] | None,
        original_content: str = "",
        modified_content: str = "",
        request_id: str = "",
        run_id: str = "",
        trace_id: str = "",
        route_id: str = "",
    ) -> HITLReentryResult:
        """Process HITL re-entry through airlock.

        Args:
            review_id: HITL review ID
            resolved_by: Who resolved the review
            resolution: Resolution outcome (approved, approved_with_edits, etc.)
            modifications: Dict of modifications made (if approved_with_edits)
            original_content: Original content before human edits
            modified_content: Content after human edits (for re-entry)
            request_id: Request identifier for receipt
            run_id: Run identifier for receipt
            trace_id: Trace identifier for receipt
            route_id: Route identifier for receipt

        Returns:
            HITLReentryResult with audit trail and receipt
        """
        import datetime

        modification_hash = hashlib.sha256(
            (modified_content or "").encode()
        ).hexdigest()[:16]

        # Build audit trail
        audit_trail = {
            "review_id": review_id,
            "resolved_by": resolved_by,
            "resolution": resolution,
            "reentry_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "modification_hash": modification_hash,
            "original_hash": hashlib.sha256(original_content.encode()).hexdigest()[:16] if original_content else "",
            "fields_modified": list(modifications.keys()) if modifications else [],
        }

        # Classify scope
        scope = self._classify_scope(resolution, modifications, modified_content)

        # Determine status
        if resolution in ("rejected", "deferred", "escalated"):
            status = HITLReentryStatus.REJECTED.value
            reason_codes = ["HITL_NOT_APPROVED", f"resolution={resolution}"]
        elif scope == HITLModificationScope.AUTHORITY_CLAIM.value:
            status = HITLReentryStatus.QUARANTINED.value
            reason_codes = ["AUTHORITY_CLAIM_DETECTED", "REQUIRES_REVIEW"]
        elif scope == HITLModificationScope.STRUCTURE_CHANGE.value:
            status = HITLReentryStatus.QUARANTINED.value
            reason_codes = ["STRUCTURE_CHANGE_DETECTED", "REQUIRES_REVIEW"]
        else:
            status = HITLReentryStatus.CLEARED.value
            reason_codes = ["HITL_REENTRY_CLEARED"]

        # Build receipt
        receipt = make_pa_boundary_receipt(
            request_id=request_id or "NOT_BOUND",
            run_id=run_id or "NOT_BOUND",
            trace_id=trace_id or "NOT_BOUND",
            route_id=route_id or "NOT_BOUND",
            policy_hash="hitl_reentry_airlock_v1",
            blueprint_hash=audit_trail["original_hash"],
            prompt_hash=modification_hash,
            compiled_artifact_hash="NOT_BOUND",
            bom_hash="NOT_BOUND",
            registry_hash="NOT_BOUND",
            template_hash="NOT_BOUND",
            source_refs={
                "review_id": review_id,
                "resolved_by": resolved_by,
                "resolution": resolution,
            },
            lineage_refs={
                "airlock": "HITL_REENTRY",
                "scope_classification": scope,
                "audit_trail": audit_trail["reentry_timestamp"],
            },
            status=PABoundaryStatus.PA_SECURITY_PASS if status == HITLReentryStatus.CLEARED.value else PABoundaryStatus.PA_SECURITY_GAP,
            reason_codes=reason_codes,
            unavailable_fields=["compiled_artifact_hash", "bom_hash", "registry_hash", "template_hash"],
        )

        _log.info(
            "[HITL-REENTRY] processed: review=%s status=%s scope=%s",
            review_id, status, scope,
        )

        if status == HITLReentryStatus.REJECTED.value:
            span_name = "pa.unsafe_payload_rejection"
        elif status == HITLReentryStatus.QUARANTINED.value:
            span_name = "pa.injection_neutralization"
        else:
            span_name = "pa.airlock_security_pass"
        with airlock_span(
            span_name,
            airlock="HITL_REENTRY",
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            review_id=review_id,
            resolution=resolution,
            scope_classification=scope,
        ):
            pass

        # Note: U0/C0 delegation would happen at next pipeline stage
        # This airlock captures the re-entry event; content is then
        # processed through normal U0/C0 airlocks like any input

        return HITLReentryResult(
            modification_hash=modification_hash,
            status=status,
            scope_classification=scope,
            audit_trail=audit_trail,
            receipt=receipt.to_dict(),
            u0_result=None,  # Populated by downstream processing
            c0_result=None,  # Populated by downstream processing
        )

    def _classify_scope(
        self,
        resolution: str,
        modifications: dict[str, Any] | None,
        modified_content: str,
    ) -> str:
        """Classify the scope of human modifications."""
        content_lower = modified_content.lower()

        # Check for authority claim patterns
        for pattern in self._authority_claim_patterns:
            if pattern in content_lower:
                return HITLModificationScope.AUTHORITY_CLAIM.value

        # Check modification keys for structure changes
        if modifications:
            structure_keys = ["route", "tool", "model", "provider", "schema", "policy", "capabilities"]
            for key in modifications.keys():
                if any(sk in key.lower() for sk in structure_keys):
                    return HITLModificationScope.STRUCTURE_CHANGE.value

        return HITLModificationScope.DATA_EDIT_ONLY.value


def process_hitl_reentry(
    *,
    review_id: str,
    resolved_by: str,
    resolution: str,
    modifications: dict[str, Any] | None = None,
    original_content: str = "",
    modified_content: str = "",
    request_id: str = "",
    run_id: str = "",
    trace_id: str = "",
    route_id: str = "",
) -> HITLReentryResult:
    """Convenience function for HITL re-entry airlock processing."""
    airlock = HITLReentryAirlock()
    return airlock.process_reentry(
        review_id=review_id,
        resolved_by=resolved_by,
        resolution=resolution,
        modifications=modifications,
        original_content=original_content,
        modified_content=modified_content,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        route_id=route_id,
    )


__all__ = [
    "HITLReentryAirlock",
    "HITLReentryResult",
    "HITLReentryStatus",
    "HITLModificationScope",
    "process_hitl_reentry",
]
