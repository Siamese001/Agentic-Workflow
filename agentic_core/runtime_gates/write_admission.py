"""Write Admission — Authority layer for resume_data mutation.

Implements WriteAdmissionReceipt and WriteAdmissionGuard. The guard evaluates
a GateBundle and determines whether to issue a writeable receipt. This is the
single point of authority for all resume_data mutations — apps_rg cannot write
directly without passing through this guard.

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W0.P3)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from agentic_core.L5_safety.runtime_gates.contracts import Result

from agentic_core.runtime_gates.definitions import (
    GateDefinition,
    GateEnforcement,
    GateVerdict,
)
from agentic_core.runtime_gates.gate_bundle import GateBundle


@dataclass(frozen=True)
class WriteAdmissionReceipt:
    """Receipt authorizing (or denying) resume_data mutation.

    Fields:
        writeable: True if mutation is authorized, False otherwise
        gate_bundle_ref: Reference to the GateBundle that produced this receipt
        timestamp_utc: ISO8601 timestamp of receipt issuance
        reason: Human-readable explanation
        reason_codes: Machine-readable codes
        receipts_digest: Hash of receipt fields for audit
        non_bypassable_gate_failed: True if a non-bypassable gate failed
    """

    writeable: bool = False
    gate_bundle_ref: str = ""
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str = ""
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    receipts_digest: str = ""
    non_bypassable_gate_failed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for outcome ledger emission."""
        return {
            "writeable": self.writeable,
            "gate_bundle_ref": self.gate_bundle_ref,
            "timestamp_utc": self.timestamp_utc,
            "reason": self.reason,
            "reason_codes": list(self.reason_codes),
            "receipts_digest": self.receipts_digest,
            "non_bypassable_gate_failed": self.non_bypassable_gate_failed,
        }


class WriteAdmissionGuard:
    """Core write admission authority.

    Evaluates GateBundles and issues WriteAdmissionReceipts. This is the
    single checkpoint for all resume_data mutations. Apps_rg cannot write
    directly without passing through this guard.
    """

    def __init__(self, gate_definitions: dict[str, GateDefinition]):
        """Initialize with gate definitions for enforcement lookup."""
        self._gate_definitions = gate_definitions

    def evaluate(
        self,
        artifact_id: str,
        gate_bundle: GateBundle,
        context: dict[str, Any] | None = None,
    ) -> WriteAdmissionReceipt:
        """Evaluate a GateBundle and return a WriteAdmissionReceipt.

        Args:
            artifact_id: Identifier for the artifact being gated (e.g., "exec_summary")
            gate_bundle: The aggregated verdicts from RuntimeGateEngine
            context: Optional runtime context (profile, strict_mode, etc.)

        Returns:
            WriteAdmissionReceipt with writeable=True only if all non-bypassable
            FAIL_CLOSED gates passed.
        """
        context = context or {}
        profile = context.get("profile", "production")  # production | draft

        # Check for critical failures
        has_critical_failure = gate_bundle.has_critical_failure(self._gate_definitions)
        failures = gate_bundle.get_failures()

        if has_critical_failure:
            # Non-bypassable gate failed — deny write
            return WriteAdmissionReceipt(
                writeable=False,
                gate_bundle_ref=f"{gate_bundle.app_id}:{gate_bundle.placement.value}",
                reason=f"Non-bypassable gate failed for {artifact_id}: {failures[0].reason if failures else 'unknown'}",
                reason_codes=(
                    "candidate_rejected_by_per_cand_gate",
                    "non_bypassable_gate_failure",
                    *(v.gate_id for v in failures),
                ),
                non_bypassable_gate_failed=True,
            )

        if gate_bundle.overall_result == Result.UNKNOWN:
            # UNKNOWN result for critical path — fail-closed
            return WriteAdmissionReceipt(
                writeable=False,
                gate_bundle_ref=f"{gate_bundle.app_id}:{gate_bundle.placement.value}",
                reason=f"UNKNOWN verdict for {artifact_id} — cannot authorize write",
                reason_codes=(
                    "unknown_verdict_blocks_write",
                    "fail_closed",
                ),
                non_bypassable_gate_failed=False,
            )

        if gate_bundle.overall_result == Result.FAIL:
            # FAIL result — check if this is a quality gate (bypassable in draft)
            non_quality_failures = [
                v for v in failures
                if self._gate_definitions.get(v.gate_id, GateDefinition("", "", GateEnforcement.FAIL_CLOSED)).enforcement
                != GateEnforcement.CONFIGURABLE
            ]
            if non_quality_failures:
                return WriteAdmissionReceipt(
                    writeable=False,
                    gate_bundle_ref=f"{gate_bundle.app_id}:{gate_bundle.placement.value}",
                    reason=f"FAIL verdict for {artifact_id}: {non_quality_failures[0].reason}",
                    reason_codes=(
                        "candidate_rejected",
                        *(v.gate_id for v in non_quality_failures),
                    ),
                    non_bypassable_gate_failed=False,
                )

        # All checks passed — authorize write
        return WriteAdmissionReceipt(
            writeable=True,
            gate_bundle_ref=f"{gate_bundle.app_id}:{gate_bundle.placement.value}",
            reason=f"Write authorized for {artifact_id}",
            reason_codes=(
                "write_authorized",
                f"result:{gate_bundle.overall_result.value}",
            ),
        )


__all__ = [
    "WriteAdmissionReceipt",
    "WriteAdmissionGuard",
]
