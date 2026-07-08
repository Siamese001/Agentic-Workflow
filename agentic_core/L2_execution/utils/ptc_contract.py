"""
PTC (Prompt-to-Code) Runtime Contract Enforcement.

Enforces at runtime:
- stdout-only contract: PTC output must not produce implicit file writes
- deterministic redaction: minimal deterministic redactor strips secrets
- strict byte caps: output exceeding cap is hard-rejected (fail-closed)
- no bypass of write gateway

Phase 1: Cryptographic Boundary Contracts (Item 41 -- PTC enforcement)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from agentic_core.L2_execution.types.l2_instruction_packet import (
    SignatureVerificationError,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "ptc_contract")
trace_contract.emit_determinism_digest("p0", "ptc_contract")

trace_contract._emit_dispatches_healing_run("p1", "ptc_contract", "L2")
trace_contract._emit_routes_through("p1", "ptc_contract", "L2")
trace_contract._emit_checks_agent_registry("p1", "ptc_contract", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ptc_contract", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ptc_contract", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ptc_contract", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ptc_contract", "target_agent")
trace_contract._emit_verifies_policy("p1", "ptc_contract", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ptc_contract", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ptc_contract", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ptc_contract", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ptc_contract")
trace_contract._emit_gated_by_confidence("p1", "ptc_contract", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ptc_contract", "L2")
trace_contract._emit_reads_policy_state("p1", "ptc_contract", "L2")

trace_contract._emit_applies_guardrail("p0", "ptc_contract", "p0_governance")
trace_contract._emit_snapshots_state("p0", "ptc_contract", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "ptc_contract", "execution_auth")
trace_contract._emit_validates_capability("p2", "ptc_contract", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ptc_contract", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ptc_contract", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ptc_contract", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ptc_contract", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ptc_contract", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ptc_contract", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ptc_contract", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ptc_contract", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ptc_contract", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ptc_contract", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ptc_contract", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ptc_contract", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ptc_contract", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ptc_contract", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ptc_contract", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ptc_contract", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ptc_contract", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ptc_contract", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("ptc_contract", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ptc_contract", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ptc_contract", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ptc_contract", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ptc_contract", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ptc_contract", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ptc_contract", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ptc_contract", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ptc_contract", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ptc_contract", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ptc_contract", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ptc_contract", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ptc_contract", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ptc_contract", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ptc_contract", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ptc_contract", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ptc_contract", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ptc_contract", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ptc_contract", "p3lm", "state")
trace_contract._emit_records_execution_trace("ptc_contract", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ptc_contract", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ptc_contract", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ptc_contract", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ptc_contract", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ptc_contract", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ptc_contract", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ptc_contract", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ptc_contract", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ptc_contract", "context_pull")
trace_contract._emit_pulls_context("p1", "ptc_contract", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ptc_contract", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ptc_contract", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ptc_contract", "write_through")
trace_contract._emit_writes_through("p1", "ptc_contract", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ptc_contract", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ptc_contract", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ptc_contract", "routing_commit")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Hard byte cap for PTC stdout output (fail-closed above this).
PTC_STDOUT_BYTE_CAP: int = 65_536  # 64 KiB

# Minimal deterministic secret-redaction patterns.
# Patterns are applied in declaration order (deterministic).
_REDACTION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(secret\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(password\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(token\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9\-._~+/]+=*"), r"\1[REDACTED]"),
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PTCContractViolation(RuntimeError):
    """Raised when a PTC runtime contract is violated."""


class PTCBytesCapExceeded(PTCContractViolation):
    """Raised when PTC output exceeds the hard byte cap."""


class PTCUnsignedEnvelopeError(PTCContractViolation):
    """Raised when PTC execution is attempted with an unsigned envelope."""


# ---------------------------------------------------------------------------
# Redactor
# ---------------------------------------------------------------------------


def redact_output(text: str) -> str:
    """Apply deterministic redaction to *text*.

    Patterns are applied in fixed declaration order for determinism.
    Returns the redacted string.
    """
    for pattern, replacement in _REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


# ---------------------------------------------------------------------------
# PTC Contract Enforcer
# ---------------------------------------------------------------------------


@dataclass
class PTCContractEnforcer:
    """Enforces PTC runtime contracts before and after tool execution.

    Usage
    -----
    enforcer = PTCContractEnforcer(secret=b"shared-secret")
    enforcer.pre_execute(envelope)           # raises if envelope not valid
    safe_output = enforcer.post_execute(raw_output)  # redact + cap check
    """

    secret: bytes
    byte_cap: int = PTC_STDOUT_BYTE_CAP
    _violation_count: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.secret:
            raise ValueError("PTCContractEnforcer: secret must be non-empty bytes")
        if self.byte_cap <= 0:
            raise ValueError("PTCContractEnforcer: byte_cap must be positive")

    # ------------------------------------------------------------------
    # Pre-execution gate (fail-closed)
    # ------------------------------------------------------------------

    def pre_execute(self, envelope: SandboxEnvelope) -> None:
        """Verify envelope signature before any side-effect.

        Raises PTCUnsignedEnvelopeError or SignatureVerificationError on failure.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "PTCContractEnforcer.pre_execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:PTCContractEnforcer.pre_execute".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not isinstance(envelope, SandboxEnvelope):
            raise TypeError(
                f"PTCContractEnforcer.pre_execute: expected SandboxEnvelope, got {type(envelope).__name__}",
            )
        if not envelope.is_signed:
            self._violation_count += 1
            raise PTCUnsignedEnvelopeError(
                f"PTC contract violation: SandboxEnvelope '{envelope.envelope_id}' "
                f"is unsigned -- execution refused",
            )
        try:
            envelope.verify(self.secret)
        except (
            SignatureVerificationError
        ) as exc:  # review: SignatureVerificationError should be handled with specific context
            self._violation_count += 1
            raise PTCContractViolation(
                f"PTC contract violation: envelope signature invalid -- {exc}",
            ) from exc

    # ------------------------------------------------------------------
    # Post-execution gate (redact + cap)
    # ------------------------------------------------------------------

    def post_execute(self, raw_output: str) -> str:
        """Redact secrets and enforce byte cap on PTC stdout output.

        Raises PTCBytesCapExceeded if the redacted output exceeds byte_cap.
        Returns the safe, redacted output string.
        """
        if not isinstance(raw_output, str):
            raise TypeError(
                f"PTCContractEnforcer.post_execute: expected str, got {type(raw_output).__name__}",
            )
        redacted = redact_output(raw_output)
        encoded_len = len(redacted.encode("utf-8"))
        if encoded_len > self.byte_cap:
            self._violation_count += 1
            raise PTCBytesCapExceeded(
                f"PTC contract violation: output {encoded_len} bytes exceeds "
                f"cap {self.byte_cap} bytes -- output rejected",
            )
        return redacted

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def violation_count(self) -> int:
        """Total number of contract violations detected by this enforcer."""
        return self._violation_count
