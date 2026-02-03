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
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk classification per V10 Contextual Router."""

    LOW = "low"  # Blue arrow path - bypass validation
    MEDIUM = "medium"  # Standard validation path
    HIGH = "high"  # Human Review Gate required


@dataclass
class AttentionState:
    """Attention mechanism state for context window management."""

    focus_files: Set[str] = field(default_factory=set)
    focus_agents: Set[str] = field(default_factory=set)
    priority_violations: List[str] = field(default_factory=list)
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_session_id: Optional[str] = None

    # Working memory state
    _state: Dict[str, Any] = field(default_factory=dict)
    _history: List[Dict[str, Any]] = field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from session state."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value in session state with history tracking."""
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
        # Trim if over limit
        while len(self.attention.focus_files) > self.attention.max_context_items:
            self.attention.focus_files.pop()

    def add_focus_agent(self, agent_name: str) -> None:
        """Add an agent to the attention focus set."""
        self.attention.focus_agents.add(agent_name)

    def add_priority_violation(self, violation_id: str) -> None:
        """Add a violation to priority queue."""
        if violation_id not in self.attention.priority_violations:
            self.attention.priority_violations.insert(0, violation_id)
            # Trim if over limit
            self.attention.priority_violations = self.attention.priority_violations[
                : self.attention.max_context_items
            ]

    def escalate_risk(self, new_level: RiskLevel) -> None:
        """Escalate risk level (never decrease)."""
        level_order = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}
        if level_order[new_level] > level_order[self.risk_level]:
            old_level = self.risk_level
            self.risk_level = new_level
            logger.info(
                f"Session {self.session_id} risk escalated: {old_level.value} -> {new_level.value}"
            )

    def get_history(self) -> List[Dict[str, Any]]:
        """Get state change history."""
        return list(self._history)

    def to_dict(self) -> Dict[str, Any]:
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
    def from_dict(cls, data: Dict[str, Any]) -> "ContextSession":
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
        self._sessions: Dict[str, ContextSession] = {}
        self._thread_local = threading.local()
        self._session_lock = threading.RLock()

    @property
    def current_session(self) -> Optional[ContextSession]:
        """Get the current thread's active session."""
        return getattr(self._thread_local, "session", None)

    @current_session.setter
    def current_session(self, session: Optional[ContextSession]) -> None:
        """Set the current thread's active session."""
        self._thread_local.session = session

    def create_session(
        self,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        parent_session: Optional[ContextSession] = None,
        metadata: Optional[Dict[str, Any]] = None,
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
        session = ContextSession(
            risk_level=risk_level,
            parent_session_id=parent_session.session_id if parent_session else None,
            metadata=metadata or {},
        )

        # Inherit attention state from parent
        if parent_session:
            session.attention.focus_files = set(parent_session.attention.focus_files)
            session.attention.focus_agents = set(parent_session.attention.focus_agents)
            # Inherit risk level (never lower than parent)
            if parent_session.risk_level.value == "high":
                session.risk_level = RiskLevel.HIGH

        with self._session_lock:
            self._sessions[session.session_id] = session

        logger.debug(f"Created session {session.session_id} (risk={risk_level.value})")
        return session

    def get_session(self, session_id: str) -> Optional[ContextSession]:
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
        metadata: Optional[Dict[str, Any]] = None,
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
        self,
        session_id: Optional[str] = None,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
    ) -> ContextSession:
        """Get existing session or create new one."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session

        # Try current thread session
        if self.current_session:
            return self.current_session

        # Create new
        return self.create_session(risk_level)

    def get_all_sessions(self) -> Dict[str, ContextSession]:
        """Get all active sessions for monitoring."""
        with self._session_lock:
            return dict(self._sessions)

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


def get_current_session() -> Optional[ContextSession]:
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
    # High risk conditions
    if is_base_agent:
        return RiskLevel.HIGH
    if has_external_touch:
        return RiskLevel.HIGH
    if file_count > 10:
        return RiskLevel.HIGH
    if cyclomatic_complexity > 50:
        return RiskLevel.HIGH

    # Medium risk conditions
    if file_count > 3:
        return RiskLevel.MEDIUM
    if cyclomatic_complexity > 20:
        return RiskLevel.MEDIUM

    # Low risk - can bypass validation
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
