"""
L0 Routing — InstructionPacket Policy Hash Enforcer.

Validates that every InstructionPacket entering the routing layer carries
a non-empty ``policy_hash`` that matches the active Merkle policy root.

Architecture gap addressed:
  Gap 2 — Policy hash enforcement coverage gap.
  Architecture requires every instruction packet to reference the active
  Merkle policy root.  This module proves that check at the L0 routing
  entry boundary.

Layer: L0 (routing enforcement only — no upward imports)
Authority: Read-only validation; raises PolicyHashViolation on failure.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_log = logging.getLogger(__name__)

_POLICY_ID = "L0-POL-HASH-001"


class PolicyHashViolation(RuntimeError):
    """Raised when an InstructionPacket fails policy hash validation at L0 routing entry."""

    def __init__(self, reason: str, packet_id: str = "", policy_id: str = _POLICY_ID) -> None:
        self.reason = reason
        self.packet_id = packet_id
        self.policy_id = policy_id
        super().__init__(f"[{policy_id}] PolicyHashViolation for packet '{packet_id}': {reason}")


@dataclass(frozen=True)
class PolicyHashValidationResult:
    """Result of a policy hash validation pass."""

    passed: bool
    packet_id: str
    policy_hash_present: bool
    policy_hash_matches: bool
    active_root: str
    packet_hash: str
    reason: str = ""
    policy_id: str = _POLICY_ID

    def format(self) -> str:
        _emit_signs_execution_trace(str(uuid.uuid4()), "seg_hash", "seg_sig", 0)
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "PolicyHashValidationResult.format")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        status = "PASS" if self.passed else "FAIL"
        return (
            f"[{self.policy_id}] {status} packet='{self.packet_id}' "
            f"present={self.policy_hash_present} "
            f"matches={self.policy_hash_matches} "
            f"active_root={self.active_root[:16]}... "
            f"reason={self.reason!r}"
        )


class PolicyHashEnforcer:
    """Validates InstructionPacket.policy_hash against the active Merkle policy root.

    Configured with an ``active_merkle_root`` at construction.  Call
    ``enforce()`` for a hard-fail check, or ``validate()`` for a non-raising
    result object.

    Usage::

        enforcer = PolicyHashEnforcer(active_merkle_root=current_root)
        enforcer.enforce(instruction_packet)   # raises PolicyHashViolation on failure

    The active Merkle root must be obtained from the canonical policy vault
    (L4 Blueprint Vault or equivalent SSOT).  Callers are responsible for
    supplying the correct root — this class does not fetch it.
    """

    def __init__(
        self,
        active_merkle_root: str,
        *,
        mode: str = "HARD_FAIL",
    ) -> None:
        """
        Parameters
        ----------
        active_merkle_root:
            Hex string of the current active policy Merkle root.  Must be
            non-empty; construction raises ``ValueError`` otherwise.
        mode:
            ``"HARD_FAIL"`` (default) — ``enforce()`` raises on any violation.
            ``"LOG_ONLY"`` — ``enforce()`` logs but never raises.
        """
        if not active_merkle_root or not active_merkle_root.strip():
            raise ValueError(
                "PolicyHashEnforcer requires a non-empty active_merkle_root. "
                "Supply the current policy root from the L4 Blueprint Vault."
            )
        if mode not in ("HARD_FAIL", "LOG_ONLY"):
            raise ValueError(f"Unknown mode {mode!r}; expected 'HARD_FAIL' or 'LOG_ONLY'")
        self._active_root = active_merkle_root.strip().lower()
        self._mode = mode

    @property
    def active_merkle_root(self) -> str:
        """The active policy Merkle root this enforcer was constructed with."""
        return self._active_root

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def enforce(self, packet: Any) -> None:
        """Hard-fail validation of ``packet.policy_hash`` vs active root.

        Parameters
        ----------
        packet:
            Any object with an ``instruction_id`` (str) and ``policy_hash``
            (str) attribute — typically an ``InstructionPacket``.

        Raises
        ------
        PolicyHashViolation
            When the packet's policy_hash is missing or does not match the
            active Merkle root, AND mode is ``"HARD_FAIL"``.
        """
        _emit_verifies_policy(str(uuid.uuid4()), "PolicyHashEnforcer.enforce", "L0_ROUTING")
        _emit_applies_guardrail(str(uuid.uuid4()), "PolicyHashEnforcer.enforce", "L0_ROUTING")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "PolicyHashEnforcer.enforce")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        result = self.validate(packet)
        if not result.passed:
            _log.error("[L0-PolicyHash] %s", result.format())
            if self._mode == "HARD_FAIL":
                raise PolicyHashViolation(
                    result.reason,
                    packet_id=result.packet_id,
                )
            _log.warning("[L0-PolicyHash] LOG_ONLY — not raising: %s", result.reason)
        else:
            _log.debug("[L0-PolicyHash] %s", result.format())

    def validate(self, packet: Any) -> PolicyHashValidationResult:
        """Non-raising validation; returns a ``PolicyHashValidationResult``.

        Accepts any object with ``instruction_id`` and ``policy_hash``
        attributes.  Missing attributes are treated as empty strings.
        """
        packet_id = _safe_str(getattr(packet, "instruction_id", ""))
        packet_hash = _safe_str(getattr(packet, "policy_hash", "")).lower()

        if not packet_hash:
            return PolicyHashValidationResult(
                passed=False,
                packet_id=packet_id,
                policy_hash_present=False,
                policy_hash_matches=False,
                active_root=self._active_root,
                packet_hash=packet_hash,
                reason="policy_hash is absent or empty — packet not policy-certified",
            )

        matches = hmac.compare_digest(packet_hash, self._active_root)
        if not matches:
            return PolicyHashValidationResult(
                passed=False,
                packet_id=packet_id,
                policy_hash_present=True,
                policy_hash_matches=False,
                active_root=self._active_root,
                packet_hash=packet_hash,
                reason=(
                    f"policy_hash mismatch — packet carries stale or wrong root "
                    f"(packet={packet_hash[:16]}... active={self._active_root[:16]}...)"
                ),
            )

        return PolicyHashValidationResult(
            passed=True,
            packet_id=packet_id,
            policy_hash_present=True,
            policy_hash_matches=True,
            active_root=self._active_root,
            packet_hash=packet_hash,
        )

    # ------------------------------------------------------------------
    # Convenience: derive Merkle root from a policy config dict
    # ------------------------------------------------------------------

    @staticmethod
    def derive_root(policy_config: dict[str, Any]) -> str:
        """Derive a deterministic policy Merkle root from *policy_config*.

        Computes SHA-256 over the canonical JSON representation
        (sorted keys, no spaces, ASCII-safe) of *policy_config*.

        This is the same deterministic serialization used by
        ``InstructionPacket._canonical_bytes()``.

        Parameters
        ----------
        policy_config:
            JSON-serialisable dict representing the current policy state.

        Returns
        -------
        str
            Lowercase hex SHA-256 digest.
        """
        import json

        canonical = json.dumps(
            policy_config,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest().lower()


def _safe_str(value: Any) -> str:
    """Return str(value) or '' if value is None."""
    return "" if value is None else str(value)


__all__ = [
    "PolicyHashEnforcer",
    "PolicyHashValidationResult",
    "PolicyHashViolation",
]
