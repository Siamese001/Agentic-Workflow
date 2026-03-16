"""
L5 CONF_CALIB Risk Gate - Structured Risk Decision Engine

Implements deterministic risk evaluation with structured RiskDecision output.
No ML, no wall-clock usage, pure deterministic rules.
"""

from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "conf_calib_gate")
emit_determinism_digest("p0", "conf_calib_gate")

_emit_dispatches_healing_run("p1", "conf_calib_gate", "L5")
_emit_routes_through("p1", "conf_calib_gate", "L5")
_emit_escalates_to_human("p1", "conf_calib_gate", "L5")
_emit_reads_policy_state("p1", "conf_calib_gate", "L5")

_emit_applies_guardrail("p0", "conf_calib_gate", "p0_governance")
_emit_snapshots_state("p0", "conf_calib_gate", "state_snapshot")


class RiskLevel(Enum):
    """Risk level enumeration for structured decision making."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class RiskDecision:
    """Structured risk decision with deterministic reasons."""

    allow: bool
    level: RiskLevel
    reasons: tuple[str, ...]


class ConfCalibRiskGate:
    """
    CONF_CALIB Risk Gate for deterministic risk evaluation.

    Evaluates payload and D0 injections to produce structured RiskDecision.
    No imports from L0/L2, no wall-clock usage.
    """

    def evaluate(self, *, payload_like: object, d0_injections: str) -> RiskDecision:
        """
        Evaluate risk for given payload and D0 injections.

        Deterministic rules (no ML, no clocks):
        - Start with LOW/allow=True
        - If payload sanitized => at least MEDIUM, reason "SANITIZED_INPUT"
        - If >=5 check_ids => at least MEDIUM, reason "MANY_CHECK_IDS"
        - If D0 contains "DENY_EXECUTION" => HIGH and allow=False, reason "D0_DENY_EXECUTION"
        - Always sort reasons lexicographically

        Args:
            payload_like: Object to evaluate (must not be mutated)
            d0_injections: D0 injection string to evaluate

        Returns:
            Structured RiskDecision with deterministic reasons
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ConfCalibRiskGate.evaluate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ConfCalibRiskGate.evaluate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        current_level = RiskLevel.LOW
        allow_execution = True
        reasons = []
        if getattr(payload_like, "sanitized", False):
            current_level = RiskLevel.MEDIUM
            reasons.append("SANITIZED_INPUT")
        check_ids = getattr(payload_like, "check_ids", ())
        if len(check_ids) >= 5:
            current_level = RiskLevel.MEDIUM
            reasons.append("MANY_CHECK_IDS")
        if "DENY_EXECUTION" in d0_injections:
            current_level = RiskLevel.HIGH
            allow_execution = False
            reasons.append("D0_DENY_EXECUTION")
        sorted_reasons = tuple(sorted(reasons))
        return RiskDecision(allow=allow_execution, level=current_level, reasons=sorted_reasons)
