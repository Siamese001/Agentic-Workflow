"""ConfigStore types -- Wave 7.0.17.B.

Frozen, schema-locked artifacts for the meta-control config store.
NO file IO.  NO mutation logic.  NO automatic application.

Canonicalization policy for payload dicts:
  - Keys are sorted recursively at every nesting level.
  - List values are NOT reordered (order is semantically significant).
  - All serialization uses compact separators (",", ":").
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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "config_store_types")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

def _get_MUTABLE_COMPONENTS():
    from system_learning.types.meta_learning_types import MUTABLE_COMPONENTS

    return MUTABLE_COMPONENTS


def canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys recursively, compact separators."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def stable_sha256(text: str) -> str:
    """Deterministic SHA-256 hex digest of a UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_component_allowed(component: str) -> None:
    """Raise ValueError if *component* is not in MUTABLE_COMPONENTS (L7 SSOT)."""
    _MUTABLE_COMPONENTS = _get_MUTABLE_COMPONENTS()
    if component not in _MUTABLE_COMPONENTS:
        raise ValueError(f"COMPONENT_NOT_MUTABLE: {component!r} not in {_MUTABLE_COMPONENTS!r}")


@dataclass(frozen=True)
class ConfigSnapshotArtifact:
    """Frozen, schema-locked versioned config snapshot."""

    artifact_type: Literal["META_CONTROL_CONFIG_SNAPSHOT"]
    app_id: str
    target_component: Literal["routing_thresholds", "tool_policies", "prompt_templates"]
    config_version: int
    payload: dict[str, Any]
    semantic_clock: SemanticClockSnapshot
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "ConfigSnapshotArtifact")
        if self.artifact_type != "META_CONTROL_CONFIG_SNAPSHOT":
            raise ValueError(
                f"artifact_type must be 'META_CONTROL_CONFIG_SNAPSHOT', got {self.artifact_type!r}"
            )
        if not self.app_id:
            raise ValueError("APP_ID_EMPTY")
        validate_component_allowed(self.target_component)
        if self.config_version < 1:
            raise ValueError(f"CONFIG_VERSION_BELOW_1: {self.config_version}")

    def to_dict(self) -> dict[str, Any]:
        """Canonical, deterministic serialization."""
        return {
            "app_id": self.app_id,
            "artifact_type": self.artifact_type,
            "config_version": self.config_version,
            "payload": self.payload,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target_component": self.target_component,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string."""
        return canonical_json(self.to_dict())


def build_config_snapshot(
    *,
    app_id: str,
    target_component: str,
    config_version: int,
    payload: dict[str, Any],
    semantic_clock: SemanticClockSnapshot,
) -> ConfigSnapshotArtifact:
    """Build a ConfigSnapshotArtifact with deterministic trace_id."""
    validate_semantic_clock(semantic_clock, "build_config_snapshot")
    if not app_id:
        raise ValueError("APP_ID_EMPTY")
    validate_component_allowed(target_component)
    if config_version < 1:
        raise ValueError(f"CONFIG_VERSION_BELOW_1: {config_version}")

    canonical_payload: dict[str, Any] = json.loads(canonical_json(payload))

    temp = {
        "app_id": app_id,
        "artifact_type": "META_CONTROL_CONFIG_SNAPSHOT",
        "config_version": config_version,
        "payload": canonical_payload,
        "semantic_clock": semantic_clock.to_dict(),
        "target_component": target_component,
    }
    trace_id = stable_sha256(canonical_json(temp))

    return ConfigSnapshotArtifact(
        artifact_type="META_CONTROL_CONFIG_SNAPSHOT",
        app_id=app_id,
        target_component=target_component,
        config_version=config_version,
        payload=canonical_payload,
        semantic_clock=semantic_clock,
        trace_id=trace_id,
    )


@dataclass(frozen=True)
class ConfigDeltaArtifact:
    """Frozen, schema-locked computed diff between two config versions."""

    artifact_type: Literal["META_CONTROL_CONFIG_DELTA"]
    app_id: str
    target_component: Literal["routing_thresholds", "tool_policies", "prompt_templates"]
    from_version: int
    to_version: int
    change_spec: dict[str, Any]
    semantic_clock: SemanticClockSnapshot
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "ConfigDeltaArtifact")
        if self.artifact_type != "META_CONTROL_CONFIG_DELTA":
            raise ValueError(f"artifact_type must be 'META_CONTROL_CONFIG_DELTA', got {self.artifact_type!r}")
        if not self.app_id:
            raise ValueError("APP_ID_EMPTY")
        validate_component_allowed(self.target_component)
        if self.to_version != self.from_version + 1:
            raise ValueError(
                f"VERSION_GAP: to_version({self.to_version}) != from_version({self.from_version}) + 1"
            )

    def to_dict(self) -> dict[str, Any]:
        """Canonical, deterministic serialization."""
        return {
            "app_id": self.app_id,
            "artifact_type": self.artifact_type,
            "change_spec": self.change_spec,
            "from_version": self.from_version,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target_component": self.target_component,
            "to_version": self.to_version,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string."""
        return canonical_json(self.to_dict())


def build_config_delta(
    *,
    app_id: str,
    target_component: str,
    from_version: int,
    to_version: int,
    change_spec: dict[str, Any],
    semantic_clock: SemanticClockSnapshot,
) -> ConfigDeltaArtifact:
    """Build a ConfigDeltaArtifact with deterministic trace_id."""
    validate_semantic_clock(semantic_clock, "build_config_delta")
    if not app_id:
        raise ValueError("APP_ID_EMPTY")
    validate_component_allowed(target_component)
    if to_version != from_version + 1:
        raise ValueError(f"VERSION_GAP: to_version({to_version}) != from_version({from_version}) + 1")

    canonical_spec: dict[str, Any] = json.loads(canonical_json(change_spec))

    temp = {
        "app_id": app_id,
        "artifact_type": "META_CONTROL_CONFIG_DELTA",
        "change_spec": canonical_spec,
        "from_version": from_version,
        "semantic_clock": semantic_clock.to_dict(),
        "target_component": target_component,
        "to_version": to_version,
    }
    trace_id = stable_sha256(canonical_json(temp))

    return ConfigDeltaArtifact(
        artifact_type="META_CONTROL_CONFIG_DELTA",
        app_id=app_id,
        target_component=target_component,
        from_version=from_version,
        to_version=to_version,
        change_spec=canonical_spec,
        semantic_clock=semantic_clock,
        trace_id=trace_id,
    )
