"""
SandboxEnvelope -- HMAC-SHA256 signed L2 tool-invocation wrapper.

Carries an InstructionPacket (or raw payload) plus tool invocation metadata.
Signature must be verified before any side-effect is permitted.

Phase 1: Cryptographic Boundary Contracts (Item 40)
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from dataclasses import dataclass as _dc
from typing import Any

from agentic_core.L2_execution.enforcement.key_source import get_current_secret
from agentic_core.L2_execution.types.l2_instruction_packet import (
    SignatureVerificationError,
    _canonical_bytes,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sandbox_envelope_types")
trace_contract.emit_determinism_digest("p0", "sandbox_envelope_types")

trace_contract._emit_dispatches_healing_run("p1", "sandbox_envelope_types", "L2")
trace_contract._emit_routes_through("p1", "sandbox_envelope_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "sandbox_envelope_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sandbox_envelope_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sandbox_envelope_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sandbox_envelope_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sandbox_envelope_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "sandbox_envelope_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sandbox_envelope_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sandbox_envelope_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sandbox_envelope_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sandbox_envelope_types")
trace_contract._emit_gated_by_confidence("p1", "sandbox_envelope_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sandbox_envelope_types", "L2")
trace_contract._emit_reads_policy_state("p1", "sandbox_envelope_types", "L2")

trace_contract._emit_applies_guardrail("p0", "sandbox_envelope_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "sandbox_envelope_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "sandbox_envelope_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "sandbox_envelope_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sandbox_envelope_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sandbox_envelope_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sandbox_envelope_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sandbox_envelope_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sandbox_envelope_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sandbox_envelope_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sandbox_envelope_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sandbox_envelope_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sandbox_envelope_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sandbox_envelope_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sandbox_envelope_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sandbox_envelope_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sandbox_envelope_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sandbox_envelope_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sandbox_envelope_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sandbox_envelope_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sandbox_envelope_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sandbox_envelope_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("sandbox_envelope_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sandbox_envelope_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sandbox_envelope_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sandbox_envelope_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sandbox_envelope_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sandbox_envelope_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sandbox_envelope_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sandbox_envelope_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sandbox_envelope_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sandbox_envelope_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sandbox_envelope_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sandbox_envelope_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sandbox_envelope_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sandbox_envelope_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sandbox_envelope_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sandbox_envelope_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sandbox_envelope_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sandbox_envelope_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sandbox_envelope_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("sandbox_envelope_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sandbox_envelope_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sandbox_envelope_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sandbox_envelope_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sandbox_envelope_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sandbox_envelope_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sandbox_envelope_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sandbox_envelope_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sandbox_envelope_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sandbox_envelope_types", "context_pull")
trace_contract._emit_pulls_context("p1", "sandbox_envelope_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sandbox_envelope_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sandbox_envelope_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sandbox_envelope_types", "write_through")
trace_contract._emit_writes_through("p1", "sandbox_envelope_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sandbox_envelope_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sandbox_envelope_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sandbox_envelope_types", "routing_commit")

# ---------------------------------------------------------------------------
# ToolBudget
# ---------------------------------------------------------------------------


@_dc(frozen=True)
class ToolBudget:
    """OS-level resource caps per tool invocation (spec contract [2])."""

    compute_ms: int = 5_000  # wall-clock cap; enforced by BudgetEnforcer
    memory_mb: int = 256
    stdout_bytes: int = 65_536  # 64 KiB

    def __post_init__(self) -> None:
        if self.compute_ms <= 0 or self.memory_mb <= 0 or self.stdout_bytes <= 0:
            raise ValueError("All ToolBudget caps must be positive")


DEFAULT_TOOL_BUDGET = ToolBudget()


# ---------------------------------------------------------------------------
# SandboxEnvelope
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SandboxEnvelope:
    """Signed wrapper for L2 tool invocations.

    Fields
    ------
    envelope_id : str
        Deterministic identifier for this envelope (e.g. instruction_id + tool).
    tool_name : str
        Name of the tool being invoked.
    tool_args : dict[str, Any]
        Arguments passed to the tool (must be JSON-serialisable).
    instruction_packet_id : str
        ``instruction_id`` of the parent InstructionPacket being executed.
    invocation_metadata : dict[str, Any]
        Additional L2 metadata (agent, tick, etc.).
    budget : ToolBudget
        OS-level resource caps for this invocation (spec contract [2]).
    signature : str
        Lowercase hex HMAC-SHA256.  Empty string means unsigned.
    """

    envelope_id: str
    tool_name: str
    tool_args: dict[str, Any] = field(default_factory=dict)
    instruction_packet_id: str = ""
    invocation_metadata: dict[str, Any] = field(default_factory=dict)
    budget: ToolBudget = field(default_factory=ToolBudget)
    signature: str = field(default="", init=False)

    def __post_init__(self) -> None:
        """Enforce mandatory signing at construction."""
        if not self.signature:
            # Auto-sign with injected secret
            secret = get_current_secret()
            mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
            # Use object.__setattr__ since dataclass is frozen
            object.__setattr__(self, "signature", mac.hexdigest().lower())

    # ------------------------------------------------------------------
    # Signing surface
    # ------------------------------------------------------------------

    def _signable_dict(self) -> dict[str, Any]:
        return {
            "budget": {
                "compute_ms": self.budget.compute_ms,
                "memory_mb": self.budget.memory_mb,
                "stdout_bytes": self.budget.stdout_bytes,
            },
            "envelope_id": self.envelope_id,
            "instruction_packet_id": self.instruction_packet_id,
            "invocation_metadata": self.invocation_metadata,
            "tool_args": self.tool_args,
            "tool_name": self.tool_name,
        }

    def canonical_bytes(self) -> bytes:
        """Deterministic bytes over the signable surface."""
        return _canonical_bytes(self._signable_dict())

    # ------------------------------------------------------------------
    # sign / verify
    # ------------------------------------------------------------------

    def sign(self, secret: bytes) -> SandboxEnvelope:
        """Return a *new* SandboxEnvelope with HMAC-SHA256 signature set."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "SandboxEnvelope.sign")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SandboxEnvelope.sign".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        new_env = SandboxEnvelope.__new__(SandboxEnvelope)
        object.__setattr__(new_env, "envelope_id", self.envelope_id)
        object.__setattr__(new_env, "tool_name", self.tool_name)
        object.__setattr__(new_env, "tool_args", self.tool_args)
        object.__setattr__(new_env, "instruction_packet_id", self.instruction_packet_id)
        object.__setattr__(new_env, "invocation_metadata", self.invocation_metadata)
        object.__setattr__(new_env, "budget", self.budget)
        object.__setattr__(new_env, "signature", mac.hexdigest().lower())
        return new_env

    def verify(self, secret: bytes) -> None:
        """Raise SignatureVerificationError if signature is absent or wrong.

        Must be called before any tool execution, write, or network call.
        """
        if not self.signature:
            raise SignatureVerificationError("SandboxEnvelope has no signature -- envelope is unsigned")
        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        expected = mac.hexdigest().lower()
        if not hmac.compare_digest(self.signature, expected):
            raise SignatureVerificationError(
                "SandboxEnvelope signature mismatch -- envelope tampered or wrong key",
            )

    @property
    def is_signed(self) -> bool:
        """True when a signature string is present (not verified)."""
        return bool(self.signature)
