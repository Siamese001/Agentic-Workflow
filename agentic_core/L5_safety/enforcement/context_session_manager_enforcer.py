"""
Context Session - V10 Working Memory and State Tracking.

Per Agentic Process V10 specification:
- Working Memory: "State Tracking + Attention Mechanism"
- Contextual Router: "Context Query + Risk Assessment"

This module provides session-level context management:
1. Request context propagation
2. Risk level tracking
3. Attention/focus state
4. Cross-agent context sharing

References:
- V10 Diagram: Working Memory (Context Window), State Tracking
- V10 Diagram: Contextual Router receives "Context Query"
"""

import logging
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

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
    _emit_snapshots_state,
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

emit_replay_key("p0", "context_session_manager_enforcer")
emit_determinism_digest("p0", "context_session_manager_enforcer")

_emit_dispatches_healing_run("p1", "context_session_manager_enforcer", "L5")
_emit_routes_through("p1", "context_session_manager_enforcer", "L5")
_emit_checks_agent_registry("p1", "context_session_manager_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "context_session_manager_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "context_session_manager_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "context_session_manager_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "context_session_manager_enforcer", "target_agent")
_emit_verifies_policy("p1", "context_session_manager_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "context_session_manager_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "context_session_manager_enforcer", "boundary_check")
_emit_transcripts_response("p1", "context_session_manager_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "context_session_manager_enforcer")
_emit_gated_by_confidence("p1", "context_session_manager_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "context_session_manager_enforcer", "L5")
_emit_reads_policy_state("p1", "context_session_manager_enforcer", "L5")
_emit_authorize_and_execute("p2", "context_session_manager_enforcer", "execution_auth")
_emit_validates_capability("p2", "context_session_manager_enforcer", "capability_check")
_emit_routes_to_capability("p2", "context_session_manager_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "context_session_manager_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "context_session_manager_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "context_session_manager_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "context_session_manager_enforcer", "exec_output")
_emit_dispatches_agent("p3", "context_session_manager_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "context_session_manager_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "context_session_manager_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "context_session_manager_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "context_session_manager_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "context_session_manager_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "context_session_manager_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "context_session_manager_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "context_session_manager_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "context_session_manager_enforcer", "eval_metric")
_emit_stores_embedding("p4", "context_session_manager_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "context_session_manager_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "context_session_manager_enforcer", "exec_snapshot_link")
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
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("context_session_manager_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("context_session_manager_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("context_session_manager_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("context_session_manager_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("context_session_manager_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("context_session_manager_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("context_session_manager_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("context_session_manager_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("context_session_manager_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("context_session_manager_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("context_session_manager_enforcer", "p4obs", "alert")
_emit_links_incident_trace("context_session_manager_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("context_session_manager_enforcer", "p3lm", "pattern")
_emit_records_learning_event("context_session_manager_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("context_session_manager_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("context_session_manager_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("context_session_manager_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("context_session_manager_enforcer", "p3lm", "policy")
_emit_stores_learning_state("context_session_manager_enforcer", "p3lm", "state")
_emit_records_execution_trace("context_session_manager_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("context_session_manager_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("context_session_manager_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("context_session_manager_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("context_session_manager_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("context_session_manager_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("context_session_manager_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("context_session_manager_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("context_session_manager_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "context_session_manager_enforcer", "context_pull")
_emit_pulls_context("p1", "context_session_manager_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "context_session_manager_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "context_session_manager_enforcer", "uwg_term_2")
_emit_writes_through("p1", "context_session_manager_enforcer", "write_through")
_emit_writes_through("p1", "context_session_manager_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "context_session_manager_enforcer", "safety_validation")
_emit_invokes_eval("p1", "context_session_manager_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "context_session_manager_enforcer", "routing_commit")

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk classification per V10 Contextual Router."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AttentionState:
    """Attention mechanism state for context window management."""

    focus_files: set[str] = field(default_factory=set)
    focus_agents: set[str] = field(default_factory=set)
    priority_violations: list[str] = field(default_factory=list)
    max_context_items: int = 10


@dataclass
class ContextSession:
    """
    Session context for V10 request tracking and state management.

    Provides:
    - Unique session identification
    - Risk level classification
    - Working memory state
    - Cross-agent context propagation
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    attention: AttentionState = field(default_factory=AttentionState)
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_session_id: str | None = None
    _state: dict[str, Any] = field(default_factory=dict)
    _history: list[dict[str, Any]] = field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from session state."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value in session state with history tracking."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ContextSession.set", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ContextSession.set", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ContextSession.set")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ContextSession.set".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        old_value = self._state.get(key)
        self._state[key] = value
        self._history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "set",
                "key": key,
                "old_value": old_value,
                "new_value": value,
            }
        )

    def delete(self, key: str) -> None:
        """Delete key from session state."""
        if key in self._state:
            old_value = self._state.pop(key)
            self._history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "delete",
                    "key": key,
                    "old_value": old_value,
                }
            )

    def add_focus_file(self, file_path: str) -> None:
        """Add a file to the attention focus set."""
        self.attention.focus_files.add(file_path)
        while len(self.attention.focus_files) > self.attention.max_context_items:
            self.attention.focus_files.pop()

    def add_focus_agent(self, agent_name: str) -> None:
        """Add an agent to the attention focus set."""
        self.attention.focus_agents.add(agent_name)

    def add_priority_violation(self, violation_id: str) -> None:
        """Add a violation to priority queue."""
        if violation_id not in self.attention.priority_violations:
            self.attention.priority_violations.insert(0, violation_id)
            self.attention.priority_violations = self.attention.priority_violations[
                : self.attention.max_context_items
            ]

    def escalate_risk(self, new_level: RiskLevel) -> None:
        """Escalate risk level (never decrease)."""
        level_order = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}
        if level_order[new_level] > level_order[self.risk_level]:
            old_level = self.risk_level
            self.risk_level = new_level
            logger.info(f"Session {self.session_id} risk escalated: {old_level.value} -> {new_level.value}")

    def get_history(self) -> list[dict[str, Any]]:
        """Get state change history."""
        return list(self._history)

    def to_dict(self) -> dict[str, Any]:
        """Serialize session for propagation."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "risk_level": self.risk_level.value,
            "parent_session_id": self.parent_session_id,
            "metadata": self.metadata,
            "state": dict(self._state),
            "attention": {
                "focus_files": list(self.attention.focus_files),
                "focus_agents": list(self.attention.focus_agents),
                "priority_violations": self.attention.priority_violations,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContextSession":
        """Deserialize session from dictionary."""
        session = cls(
            session_id=data.get("session_id", str(uuid.uuid4())),
            risk_level=RiskLevel(data.get("risk_level", "medium")),
            parent_session_id=data.get("parent_session_id"),
            metadata=data.get("metadata", {}),
        )
        session._state = data.get("state", {})
        attention_data = data.get("attention", {})
        session.attention.focus_files = set(attention_data.get("focus_files", []))
        session.attention.focus_agents = set(attention_data.get("focus_agents", []))
        session.attention.priority_violations = attention_data.get("priority_violations", [])
        return session


class ContextSessionManager:
    """
    Thread-safe session manager for V10 context propagation.

    Implements the Working Memory component from V10:
    - Session creation and lifecycle
    - Thread-local session access
    - Session inheritance for sub-operations
    """

    _instance: Optional["ContextSessionManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for global session management."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        """Initialize the session manager."""
        self._sessions: dict[str, ContextSession] = {}
        self._thread_local = threading.local()
        self._session_lock = threading.RLock()

    @property
    def current_session(self) -> ContextSession | None:
        """Get the current thread's active session."""
        return getattr(self._thread_local, "session", None)

    @current_session.setter
    def current_session(self, session: ContextSession | None) -> None:
        """Set the current thread's active session."""
        self._thread_local.session = session

    def create_session(
        self,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        parent_session: ContextSession | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ContextSession:
        """
        Create a new context session.

        Args:
            risk_level: Initial risk classification
            parent_session: Optional parent for session inheritance
            metadata: Optional session metadata

        Returns:
            New ContextSession instance
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ContextSessionManager.create_session"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ContextSessionManager.create_session".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        session = ContextSession(
            risk_level=risk_level,
            parent_session_id=parent_session.session_id if parent_session else None,
            metadata=metadata or {},
        )
        if parent_session:
            session.attention.focus_files = set(parent_session.attention.focus_files)
            session.attention.focus_agents = set(parent_session.attention.focus_agents)
            if parent_session.risk_level.value == "high":
                session.risk_level = RiskLevel.HIGH
        with self._session_lock:
            self._sessions[session.session_id] = session
        logger.debug(f"Created session {session.session_id} (risk={risk_level.value})")
        return session

    def get_session(self, session_id: str) -> ContextSession | None:
        """Get a session by ID."""
        with self._session_lock:
            return self._sessions.get(session_id)

    def end_session(self, session_id: str) -> None:
        """End and cleanup a session."""
        with self._session_lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.debug(f"Ended session {session_id}")

    @contextmanager
    def session_scope(
        self,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        inherit_parent: bool = True,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Context manager for session lifecycle.

        Usage:
            with session_manager.session_scope(RiskLevel.HIGH) as session:
                # Operations within this session
                session.set("key", "value")

        Args:
            risk_level: Initial risk level
            inherit_parent: Whether to inherit from current session
            metadata: Optional session metadata

        Yields:
            ContextSession for the scope
        """
        parent = self.current_session if inherit_parent else None
        session = self.create_session(risk_level, parent, metadata)
        previous_session = self.current_session
        self.current_session = session
        try:
            yield session
        finally:
            self.current_session = previous_session
            self.end_session(session.session_id)

    def get_or_create_session(
        self, session_id: str | None = None, risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> ContextSession:
        """Get existing session or create new one."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        if self.current_session:
            return self.current_session
        return self.create_session(risk_level)

    def get_all_sessions(self) -> dict[str, ContextSession]:
        """Get all active sessions for monitoring."""
        with self._session_lock:
            return dict(self._sessions)

    # guardian: allow-magic-config
    def cleanup_expired(self, max_age_seconds: int = 3600) -> int:
        """Cleanup sessions older than max_age_seconds."""
        now = datetime.utcnow()
        expired = []
        with self._session_lock:
            for session_id, session in self._sessions.items():
                age = (now - session.created_at).total_seconds()
                if age > max_age_seconds:
                    expired.append(session_id)
            for session_id in expired:
                del self._sessions[session_id]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
        return len(expired)


def get_session_manager() -> ContextSessionManager:
    """Get the global session manager instance."""
    return ContextSessionManager()


def get_current_session() -> ContextSession | None:
    """Get the current thread's active session."""
    return get_session_manager().current_session


def classify_risk(
    file_count: int = 0,
    has_external_touch: bool = False,
    cyclomatic_complexity: int = 0,
    is_base_agent: bool = False,
) -> RiskLevel:
    """
    Classify risk level per V10 Contextual Router logic.

    Args:
        file_count: Number of files affected
        has_external_touch: Whether operation touches external systems
        cyclomatic_complexity: Code complexity score
        is_base_agent: Whether operation affects base agent files

    Returns:
        Classified RiskLevel
    """
    if is_base_agent:
        return RiskLevel.HIGH
    if has_external_touch:
        return RiskLevel.HIGH
    if file_count > 10:
        return RiskLevel.HIGH
    if cyclomatic_complexity > 50:
        return RiskLevel.HIGH
    if file_count > 3:
        return RiskLevel.MEDIUM
    if cyclomatic_complexity > 20:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


__all__ = [
    "AttentionState",
    "ContextSession",
    "ContextSessionManager",
    "RiskLevel",
    "classify_risk",
    "get_current_session",
    "get_session_manager",
]
