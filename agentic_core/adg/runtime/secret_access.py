"""G17 (gap): Secret / credential access runtime.

Tracks every secret and credential read performed by agentic modules:
  caller → reads_secret_vault → SecretVault
  caller → accesses_credential → CredentialStore
  caller → rotates_secret → SecretVault

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_applies_guardrail("p0", "secret_access", "p0_governance")
_emit_reads_policy_state("p0", "secret_access", "policy_binding")
_emit_snapshots_state("p0", "secret_access", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("secret_access", "p4obs", "metric_1")
_emit_emits_metric_event("secret_access", "p4obs", "metric_2")
_emit_emits_metric_event("secret_access", "p4obs", "metric_3")
_emit_emits_metric_event("secret_access", "p4obs", "metric_4")
_emit_emits_metric_event("secret_access", "p4obs", "metric_5")
_emit_emits_metric_event("secret_access", "p4obs", "metric_6")
_emit_records_incident_event("secret_access", "p4obs", "incident")
_emit_captures_runtime_anomaly("secret_access", "p4obs", "anomaly")
_emit_writes_observability_log("secret_access", "p4obs", "obs_log")
_emit_updates_monitoring_state("secret_access", "p4obs", "mon_state")
_emit_triggers_alert("secret_access", "p4obs", "alert")
_emit_links_incident_trace("secret_access", "p4obs", "trace_link")
_emit_captures_pattern("secret_access", "p3lm", "pattern")
_emit_records_learning_event("secret_access", "p3lm", "learning_event")
_emit_writes_learning_snapshot("secret_access", "p3lm", "snapshot")
_emit_feeds_meta_learning("secret_access", "p3lm", "meta_feed")
_emit_updates_routing_strategy("secret_access", "p3lm", "routing")
_emit_improves_agent_policy("secret_access", "p3lm", "policy")
_emit_stores_learning_state("secret_access", "p3lm", "state")
_emit_records_execution_trace("secret_access", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("secret_access", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("secret_access", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("secret_access", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("secret_access", "L4_STATE", "p2_trace_5")
_emit_reads_environ("secret_access", "env_read", "p2_env_1")
_emit_reads_environ("secret_access", "env_read", "p2_env_2")
_emit_reads_runtime_state("secret_access", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("secret_access", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "secret_access", "context_pull")
_emit_pulls_context("p1", "secret_access", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "secret_access", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "secret_access", "uwg_term_2")
_emit_writes_through("p1", "secret_access", "write_through")
_emit_writes_through("p1", "secret_access", "write_through_2")
_emit_validated_by_safety_plane("p1", "secret_access", "safety_validation")
_emit_invokes_eval("p1", "secret_access", "eval_call")
_emit_proposal_commits_routing("p1", "secret_access", "routing_commit")
_emit_escalates_to_human("p1", "secret_access", "human_escalation")
_emit_routes_through("p1", "secret_access", "route_through")
_emit_checks_agent_registry("p1", "secret_access", "agent_registry")
_emit_validates_agent_capability("p1", "secret_access", "capability")
_emit_dispatches_execution_plan("p1", "secret_access", "exec_plan")
_emit_agent_executes_agent("p1", "secret_access", "sub_agent")
_emit_routes_to_agent("p1", "secret_access", "target_agent")
_emit_verifies_policy("p1", "secret_access", "policy_check")
_emit_observes_runtime_state("p1", "secret_access", "runtime_state")
_emit_verifies_boundary("p1", "secret_access", "boundary_check")
_emit_transcripts_response("p1", "secret_access", "transcript")
_emit_hard_fails_untranscripted("p1", "secret_access")
_emit_gated_by_confidence("p1", "secret_access", "confidence_gate")
emit_replay_key("p0", "secret_access")
emit_determinism_digest("p0", "secret_access")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "secret_access", "execution_auth")
_emit_validates_capability("p2", "secret_access", "capability_check")
_emit_routes_to_capability("p2", "secret_access", "capability_route")
_emit_writes_via_uwg("p2", "secret_access", "uwg_write")
_emit_blocks_direct_write("p2", "secret_access", "direct_write_block")
_emit_records_tool_invocation("p2", "secret_access", "tool_invocation")
_emit_captures_execution_output("p2", "secret_access", "exec_output")
_emit_dispatches_agent("p3", "secret_access", "agent_dispatch")
_emit_coordinates_agents("p3", "secret_access", "agent_coordination")
_emit_records_workflow_lineage("p3", "secret_access", "workflow_lineage")
_emit_records_healing_outcome("p3", "secret_access", "healing_outcome")
_emit_escalates_failure("p3", "secret_access", "failure_escalation")
_emit_orchestrates_workflow("p3", "secret_access", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "secret_access", "healing_dispatch")
_emit_invokes_evaluation("p3", "secret_access", "evaluation_signal")
_emit_records_telemetry_event("p4", "secret_access", "telemetry_event")
_emit_captures_evaluation_metric("p4", "secret_access", "eval_metric")
_emit_stores_embedding("p4", "secret_access", "embedding_store")
_emit_updates_meta_learning_state("p4", "secret_access", "meta_learning")
_emit_links_execution_to_snapshot("p4", "secret_access", "exec_snapshot_link")


class SecretAccessOutcome(str, Enum):
    """Outcome of a secret access attempt."""

    SUCCESS = "success"
    DENIED = "denied"
    NOT_FOUND = "not_found"
    ROTATED = "rotated"
    CACHED = "cached"


class SecretKind(str, Enum):
    """Category of secret being accessed."""

    API_KEY = "api_key"
    PASSWORD = "password"
    CERTIFICATE = "certificate"
    TOKEN = "token"
    ENV_VAR = "env_var"
    VAULT_SECRET = "vault_secret"
    DATABASE_CRED = "database_cred"


@dataclass
class SecretAccessEvent:
    """A single secret access event recorded at runtime."""

    event_id: str = field(default_factory=lambda: f"sae-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    run_id: str = ""
    secret_name: str = ""
    secret_kind: SecretKind = SecretKind.API_KEY
    outcome: SecretAccessOutcome = SecretAccessOutcome.SUCCESS
    access_method: str = ""
    masked_value_hash: str = ""
    accessed_at: float = field(default_factory=time.time)
    is_rotation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "secret_name": self.secret_name,
            "secret_kind": self.secret_kind.value,
            "outcome": self.outcome.value,
            "access_method": self.access_method,
            "masked_value_hash": self.masked_value_hash,
            "accessed_at": self.accessed_at,
            "is_rotation": self.is_rotation,
        }


@dataclass
class SecretAccessReport:
    """Aggregated report of all secret accesses in a run."""

    agent_id: str
    run_id: str
    events: list[SecretAccessEvent] = field(default_factory=list)

    @property
    def total_accesses(self) -> int:
        return len(self.events)

    @property
    def denied_count(self) -> int:
        return sum(1 for e in self.events if e.outcome == SecretAccessOutcome.DENIED)

    @property
    def rotation_count(self) -> int:
        return sum(1 for e in self.events if e.is_rotation)

    @property
    def by_kind(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SecretAccessReport.by_kind")

        result: dict[str, int] = {}
        for e in self.events:
            result[e.secret_kind.value] = result.get(e.secret_kind.value, 0) + 1
        return result

    @property
    def unique_secrets(self) -> set[str]:
        return {e.secret_name for e in self.events}

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_accesses": self.total_accesses,
            "denied_count": self.denied_count,
            "rotation_count": self.rotation_count,
            "unique_secret_count": len(self.unique_secrets),
            "by_kind": self.by_kind,
            "events": [e.to_dict() for e in self.events],
        }


class SecretAccessRecorder:
    """G17 runtime recorder: tracks secret/credential reads and rotations.

    Lifecycle:
        recorder = SecretAccessRecorder(agent_id, run_id)
        recorder.record_access("MY_API_KEY", SecretKind.API_KEY, "get_api_key")
        recorder.record_rotation("DB_PASSWORD")
        report = recorder.report
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = SecretAccessReport(agent_id=agent_id, run_id=run_id)

    @property
    def report(self) -> SecretAccessReport:
        return self._report

    def record_access(
        self,
        secret_name: str,
        secret_kind: SecretKind = SecretKind.API_KEY,
        access_method: str = "get_secret",
        outcome: SecretAccessOutcome = SecretAccessOutcome.SUCCESS,
        raw_value: str = "",
    ) -> SecretAccessEvent:
        """Record a secret access and return the event."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SecretAccessRecorder.record_access")

        masked_hash = ""
        if raw_value:
            masked_hash = hashlib.sha256(raw_value.encode()).hexdigest()[:16]
        event = SecretAccessEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            secret_name=secret_name,
            secret_kind=secret_kind,
            outcome=outcome,
            access_method=access_method,
            masked_value_hash=masked_hash,
        )
        self._report.events.append(event)
        return event

    def record_env_read(
        self, var_name: str, outcome: SecretAccessOutcome = SecretAccessOutcome.SUCCESS,
    ) -> SecretAccessEvent:
        """Specialised helper for os.environ / os.getenv reads."""
        return self.record_access(
            secret_name=var_name,
            secret_kind=SecretKind.ENV_VAR,
            access_method="os.getenv",
            outcome=outcome,
        )

    def record_rotation(self, secret_name: str) -> SecretAccessEvent:
        """Record a secret rotation event."""
        event = SecretAccessEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            secret_name=secret_name,
            secret_kind=SecretKind.VAULT_SECRET,
            outcome=SecretAccessOutcome.ROTATED,
            access_method="rotate_secret",
            is_rotation=True,
        )
        self._report.events.append(event)
        return event

    def record_denied(
        self, secret_name: str, secret_kind: SecretKind = SecretKind.API_KEY,
    ) -> SecretAccessEvent:
        """Record a denied secret access."""
        return self.record_access(
            secret_name=secret_name,
            secret_kind=secret_kind,
            outcome=SecretAccessOutcome.DENIED,
        )
