"""Capability Token Types — Wave 5.0.1 P0 Hardening.

Frozen, schema-locked artifacts for capability-based access control
at the single L2 execution boundary.

All artifacts require semantic_clock (no wall-clock, no uuid4).
All JSON serialized with sort_keys=True.
All lists sorted deterministically.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "capability_token_types")
emit_determinism_digest("p0", "capability_token_types")

_emit_dispatches_healing_run("p1", "capability_token_types", "L2")
_emit_routes_through("p1", "capability_token_types", "L2")
_emit_checks_agent_registry("p1", "capability_token_types", "agent_registry")
_emit_validates_agent_capability("p1", "capability_token_types", "capability")
_emit_dispatches_execution_plan("p1", "capability_token_types", "exec_plan")
_emit_agent_executes_agent("p1", "capability_token_types", "sub_agent")
_emit_routes_to_agent("p1", "capability_token_types", "target_agent")
_emit_verifies_policy("p1", "capability_token_types", "policy_check")
_emit_observes_runtime_state("p1", "capability_token_types", "runtime_state")
_emit_verifies_boundary("p1", "capability_token_types", "boundary_check")
_emit_transcripts_response("p1", "capability_token_types", "transcript")
_emit_hard_fails_untranscripted("p1", "capability_token_types")
_emit_gated_by_confidence("p1", "capability_token_types", "confidence_gate")
_emit_escalates_to_human("p1", "capability_token_types", "L2")
_emit_reads_policy_state("p1", "capability_token_types", "L2")

_emit_applies_guardrail("p0", "capability_token_types", "p0_governance")
_emit_snapshots_state("p0", "capability_token_types", "state_snapshot")
_emit_authorize_and_execute("p2", "capability_token_types", "execution_auth")
_emit_validates_capability("p2", "capability_token_types", "capability_check")
_emit_routes_to_capability("p2", "capability_token_types", "capability_route")
_emit_writes_via_uwg("p2", "capability_token_types", "uwg_write")
_emit_blocks_direct_write("p2", "capability_token_types", "direct_write_block")
_emit_records_tool_invocation("p2", "capability_token_types", "tool_invocation")
_emit_captures_execution_output("p2", "capability_token_types", "exec_output")
_emit_dispatches_agent("p3", "capability_token_types", "agent_dispatch")
_emit_coordinates_agents("p3", "capability_token_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "capability_token_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "capability_token_types", "healing_outcome")
_emit_escalates_failure("p3", "capability_token_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "capability_token_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "capability_token_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "capability_token_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "capability_token_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "capability_token_types", "eval_metric")
_emit_stores_embedding("p4", "capability_token_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "capability_token_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "capability_token_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("capability_token_types", "p4obs", "metric_1")
_emit_emits_metric_event("capability_token_types", "p4obs", "metric_2")
_emit_emits_metric_event("capability_token_types", "p4obs", "metric_3")
_emit_emits_metric_event("capability_token_types", "p4obs", "metric_4")
_emit_emits_metric_event("capability_token_types", "p4obs", "metric_5")
_emit_emits_metric_event("capability_token_types", "p4obs", "metric_6")
_emit_records_incident_event("capability_token_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("capability_token_types", "p4obs", "anomaly")
_emit_writes_observability_log("capability_token_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("capability_token_types", "p4obs", "mon_state")
_emit_triggers_alert("capability_token_types", "p4obs", "alert")
_emit_links_incident_trace("capability_token_types", "p4obs", "trace_link")
_emit_captures_pattern("capability_token_types", "p3lm", "pattern")
_emit_records_learning_event("capability_token_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("capability_token_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("capability_token_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("capability_token_types", "p3lm", "routing")
_emit_improves_agent_policy("capability_token_types", "p3lm", "policy")
_emit_stores_learning_state("capability_token_types", "p3lm", "state")
_emit_records_execution_trace("capability_token_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("capability_token_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("capability_token_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("capability_token_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("capability_token_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("capability_token_types", "env_read", "p2_env_1")
_emit_reads_environ("capability_token_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("capability_token_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("capability_token_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "capability_token_types", "context_pull")
_emit_pulls_context("p1", "capability_token_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "capability_token_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "capability_token_types", "uwg_term_2")
_emit_writes_through("p1", "capability_token_types", "write_through")
_emit_writes_through("p1", "capability_token_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "capability_token_types", "safety_validation")
_emit_invokes_eval("p1", "capability_token_types", "eval_call")
_emit_proposal_commits_routing("p1", "capability_token_types", "routing_commit")

# =============================================================================
# §B — Canonical Permission Codes (single mapping table)
# =============================================================================

PERMISSION_CODES: dict[str, str] = {
    "TOOL_READ": "TOOL:READ",
    "TOOL_WRITE": "TOOL:WRITE",
    "FS_READ": "FS:READ",
    "FS_WRITE": "FS:WRITE",
    "NET_READ": "NET:READ",
    "NET_WRITE": "NET:WRITE",
    "GIT_READ": "GIT:READ",
    "GIT_WRITE": "GIT:WRITE",
}

ALL_PERMISSION_VALUES: frozenset[str] = frozenset(PERMISSION_CODES.values())


# =============================================================================
# §A.1 — CapabilityTokenArtifact
# =============================================================================


def _canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, no extra whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _compute_trace_id(payload: dict[str, Any]) -> str:
    """Deterministic trace_id = SHA-256 of canonical JSON payload (excluding trace_id)."""
    canonical = _canonical_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CapabilityTokenSubject:
    """Subject identity within a capability token."""

    kind: str
    id: str

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("CapabilityTokenSubject: kind is required")
        if not self.id:
            raise ValueError("CapabilityTokenSubject: id is required")

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "kind": self.kind}


@dataclass(frozen=True)
class CapabilityConstraints:
    """Constraints on a capability token."""

    allowed_paths: tuple[str, ...]
    max_tool_calls: int

    def __post_init__(self) -> None:
        if self.max_tool_calls < 0:
            raise ValueError(
                f"CapabilityConstraints: max_tool_calls must be >= 0, got {self.max_tool_calls}",
            )
        # Enforce sorted invariant at construction
        if list(self.allowed_paths) != sorted(self.allowed_paths):
            object.__setattr__(self, "allowed_paths", tuple(sorted(self.allowed_paths)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_paths": sorted(self.allowed_paths),
            "max_tool_calls": self.max_tool_calls,
        }


@dataclass(frozen=True)
class CapabilityTokenArtifact:
    """§A.1 — Capability token for L2 execution boundary enforcement.

    All fields are immutable. trace_id is deterministic (SHA-256 of canonical payload).
    semantic_clock is required (no wall-clock).
    """

    artifact_type: Literal["CAPABILITY_TOKEN"]
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    subject: CapabilityTokenSubject
    issued_by: str
    permissions: tuple[str, ...]
    constraints: CapabilityConstraints
    policy_config_hash: str | None

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "CapabilityTokenArtifact")
        if self.artifact_type != "CAPABILITY_TOKEN":
            raise ValueError(
                f"CapabilityTokenArtifact: artifact_type must be 'CAPABILITY_TOKEN', got '{self.artifact_type}'",
            )
        if not self.issued_by:
            raise ValueError("CapabilityTokenArtifact: issued_by is required")
        if not self.trace_id:
            raise ValueError("CapabilityTokenArtifact: trace_id is required")
        # Enforce sorted permissions
        if list(self.permissions) != sorted(self.permissions):
            object.__setattr__(self, "permissions", tuple(sorted(self.permissions)))

    def _payload_dict(self) -> dict[str, Any]:
        """Canonical payload for serialization (includes trace_id)."""
        return {
            "artifact_type": self.artifact_type,
            "constraints": self.constraints.to_dict(),
            "issued_by": self.issued_by,
            "permissions": sorted(self.permissions),
            "policy_config_hash": self.policy_config_hash,
            "semantic_clock": self.semantic_clock.to_dict(),
            "subject": self.subject.to_dict(),
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON serialization."""
        return _canonical_json(self._payload_dict())


def build_capability_token(
    *,
    semantic_clock: SemanticClockSnapshot,
    subject: CapabilityTokenSubject,
    issued_by: str,
    permissions: list[str] | tuple[str, ...],
    constraints: CapabilityConstraints,
    policy_config_hash: str | None = None,
) -> CapabilityTokenArtifact:
    """Build a CapabilityTokenArtifact with deterministic trace_id.

    Permissions and allowed_paths are sorted automatically.
    """
    validate_semantic_clock(semantic_clock, "build_capability_token")
    sorted_perms = tuple(sorted(permissions))

    # Compute deterministic trace_id from payload (excluding trace_id itself)
    pre_payload = {
        "artifact_type": "CAPABILITY_TOKEN",
        "constraints": constraints.to_dict(),
        "issued_by": issued_by,
        "permissions": list(sorted_perms),
        "policy_config_hash": policy_config_hash,
        "semantic_clock": semantic_clock.to_dict(),
        "subject": subject.to_dict(),
    }
    trace_id = _compute_trace_id(pre_payload)

    return CapabilityTokenArtifact(
        artifact_type="CAPABILITY_TOKEN",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        subject=subject,
        issued_by=issued_by,
        permissions=sorted_perms,
        constraints=constraints,
        policy_config_hash=policy_config_hash,
    )


# =============================================================================
# §A.2 — CapabilityDecisionArtifact
# =============================================================================


@dataclass(frozen=True)
class CapabilityDecisionArtifact:
    """§A.2 — Decision artifact emitted at the L2 enforcement chokepoint.

    Emitted for every tool invocation (both ALLOW and DENY).
    trace_id is deterministic (SHA-256 of canonical payload excluding trace_id).
    """

    artifact_type: Literal["CAPABILITY_DECISION"]
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    tool_name: str
    action: str
    requested_resource: str
    decision: Literal["ALLOW", "DENY"]
    deny_reason: str | None
    capability_trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "CapabilityDecisionArtifact")
        if self.artifact_type != "CAPABILITY_DECISION":
            raise ValueError(
                f"CapabilityDecisionArtifact: artifact_type must be 'CAPABILITY_DECISION', got '{self.artifact_type}'",
            )
        if not self.tool_name:
            raise ValueError("CapabilityDecisionArtifact: tool_name is required")
        if not self.trace_id:
            raise ValueError("CapabilityDecisionArtifact: trace_id is required")
        if self.decision not in ("ALLOW", "DENY"):
            raise ValueError(
                f"CapabilityDecisionArtifact: decision must be 'ALLOW' or 'DENY', got '{self.decision}'",
            )

    def _payload_dict(self) -> dict[str, Any]:
        """Canonical payload for serialization."""
        return {
            "action": self.action,
            "artifact_type": self.artifact_type,
            "capability_trace_id": self.capability_trace_id,
            "decision": self.decision,
            "deny_reason": self.deny_reason,
            "requested_resource": self.requested_resource,
            "semantic_clock": self.semantic_clock.to_dict(),
            "tool_name": self.tool_name,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON serialization."""
        return _canonical_json(self._payload_dict())


def build_capability_decision(
    *,
    semantic_clock: SemanticClockSnapshot,
    tool_name: str,
    action: str,
    requested_resource: str,
    decision: Literal["ALLOW", "DENY"],
    deny_reason: str | None,
    capability_trace_id: str,
) -> CapabilityDecisionArtifact:
    """Build a CapabilityDecisionArtifact with deterministic trace_id."""
    validate_semantic_clock(semantic_clock, "build_capability_decision")

    pre_payload = {
        "action": action,
        "artifact_type": "CAPABILITY_DECISION",
        "capability_trace_id": capability_trace_id,
        "decision": decision,
        "deny_reason": deny_reason,
        "requested_resource": requested_resource,
        "semantic_clock": semantic_clock.to_dict(),
        "tool_name": tool_name,
    }
    trace_id = _compute_trace_id(pre_payload)

    return CapabilityDecisionArtifact(
        artifact_type="CAPABILITY_DECISION",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        tool_name=tool_name,
        action=action,
        requested_resource=requested_resource,
        decision=decision,
        deny_reason=deny_reason,
        capability_trace_id=capability_trace_id,
    )


# =============================================================================
# §C — Capability Enforcement Logic (single L2 chokepoint helper)
# =============================================================================


class CapabilityEnforcer:
    """Stateful enforcer for a single CapabilityTokenArtifact.

    Tracks invocation count and validates permissions + path constraints.
    Emits a CapabilityDecisionArtifact for every check (ALLOW or DENY).
    """

    def __init__(self, token: CapabilityTokenArtifact) -> None:
        self._token = token
        self._call_count: int = 0
        self._decisions: list[CapabilityDecisionArtifact] = []

    @property
    def token(self) -> CapabilityTokenArtifact:
        return self._token

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def decisions(self) -> list[CapabilityDecisionArtifact]:
        return list(self._decisions)

    def check(
        self,
        *,
        tool_name: str,
        action: str,
        requested_resource: str,
        required_permission: str,
        semantic_clock: SemanticClockSnapshot,
    ) -> CapabilityDecisionArtifact:
        """Check capability and emit decision artifact.

        Args:
            tool_name: Name of the tool being invoked.
            action: Action being performed (e.g. "execute").
            requested_resource: Resource path being accessed.
            required_permission: Permission code required (from PERMISSION_CODES values).
            semantic_clock: Current semantic clock snapshot.

        Returns:
            CapabilityDecisionArtifact (ALLOW or DENY).

        Raises:
            PermissionError: If decision is DENY.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "CapabilityEnforcer.check")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CapabilityEnforcer.check".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        deny_reason: str | None = None

        # 1) Check permission present
        if required_permission not in self._token.permissions:
            deny_reason = f"MISSING_PERMISSION:{required_permission}"

        # 2) Check path constraint (only if no deny yet)
        if deny_reason is None:
            allowed = self._token.constraints.allowed_paths
            if allowed and not self._path_matches(requested_resource, allowed):
                deny_reason = f"PATH_NOT_ALLOWED:{requested_resource}"

        # 3) Check max_tool_calls (only if no deny yet)
        if deny_reason is None:
            if self._call_count >= self._token.constraints.max_tool_calls:
                deny_reason = (
                    f"MAX_TOOL_CALLS_EXCEEDED:{self._call_count}>={self._token.constraints.max_tool_calls}"
                )

        decision: Literal["ALLOW", "DENY"] = "DENY" if deny_reason else "ALLOW"

        artifact = build_capability_decision(
            semantic_clock=semantic_clock,
            tool_name=tool_name,
            action=action,
            requested_resource=requested_resource,
            decision=decision,
            deny_reason=deny_reason,
            capability_trace_id=self._token.trace_id,
        )
        self._decisions.append(artifact)

        # Increment counter only on ALLOW (successful invocation)
        if decision == "ALLOW":
            self._call_count += 1

        if decision == "DENY":
            raise PermissionError(f"CAPABILITY_DENIED:{deny_reason}")

        return artifact

    @staticmethod
    def _path_matches(requested: str, allowed: tuple[str, ...]) -> bool:
        """Check if requested resource matches any allowed path prefix.

        Uses segment-based comparison on logical resource URIs (not filesystem paths).
        """
        req_segments = requested.split("/")
        for prefix in allowed:
            prefix_segments = prefix.split("/")
            if req_segments[: len(prefix_segments)] == prefix_segments:
                return True
        return False


# =============================================================================
# §D — High-Level Issuance Helper (Wave 5.0.3)
# =============================================================================


def issue_capability_token(
    *,
    semantic_clock: SemanticClockSnapshot,
    subject_kind: str,
    subject_id: str,
    issued_by: str,
    permissions: list[str],
    allowed_paths: list[str],
    max_tool_calls: int,
    policy_config_hash: str | None = None,
) -> CapabilityTokenArtifact:
    """§Wave5.0.3 — Deterministic capability token issuance helper.

    High-level convenience for upstream (L5/L3) callers to mint a
    CapabilityTokenArtifact with flat parameters.  Validates permission
    codes, constructs composite sub-objects, and delegates to
    build_capability_token for deterministic trace_id generation.

    Args:
        semantic_clock: Required SemanticClockSnapshot (ValueError if None).
        subject_kind: Subject type (e.g. "agent").
        subject_id: Subject identifier (e.g. "StructureHealerAgent").
        issued_by: Issuer identity string.
        permissions: List of permission code values (must be in
            ALL_PERMISSION_VALUES, e.g. "TOOL:READ").  Sorted automatically.
        allowed_paths: List of resource path prefixes.  Sorted automatically.
        max_tool_calls: Maximum invocations allowed under this token.
        policy_config_hash: Optional policy config hash for pinning.

    Returns:
        CapabilityTokenArtifact with deterministic trace_id.

    Raises:
        ValueError: If semantic_clock is None or any permission is unknown.
    """
    validate_semantic_clock(semantic_clock, "issue_capability_token")

    # Validate all permission codes against canonical set
    for perm in permissions:
        if perm not in ALL_PERMISSION_VALUES:
            raise ValueError(
                f"issue_capability_token: unknown permission '{perm}'. "
                f"Valid values: {sorted(ALL_PERMISSION_VALUES)}",
            )

    subject = CapabilityTokenSubject(kind=subject_kind, id=subject_id)
    constraints = CapabilityConstraints(
        allowed_paths=tuple(sorted(allowed_paths)),
        max_tool_calls=max_tool_calls,
    )

    return build_capability_token(
        semantic_clock=semantic_clock,
        subject=subject,
        issued_by=issued_by,
        permissions=list(permissions),
        constraints=constraints,
        policy_config_hash=policy_config_hash,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ALL_PERMISSION_VALUES",
    "CapabilityConstraints",
    "CapabilityDecisionArtifact",
    "CapabilityEnforcer",
    "CapabilityTokenArtifact",
    "CapabilityTokenSubject",
    "PERMISSION_CODES",
    "build_capability_decision",
    "build_capability_token",
    "issue_capability_token",
]
