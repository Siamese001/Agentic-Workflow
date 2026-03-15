"""G20 (gap): Policy state observation runtime.

Tracks every policy-state and runtime-state read performed by agentic modules:
  caller → observes_policy_state → PolicyStateReader
  caller → observes_runtime_state → RuntimeStateObserver
  caller → snapshots_state → StateSnapshot

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class StateObservationKind(str, Enum):
    """Category of state being observed."""

    POLICY_STATE = "policy_state"
    RUNTIME_STATE = "runtime_state"
    GOVERNANCE_STATE = "governance_state"
    HEALTH_PROBE = "health_probe"
    SNAPSHOT = "snapshot"


class StateReadOutcome(str, Enum):
    """Outcome of a state read."""

    CURRENT = "current"
    STALE = "stale"
    UNAVAILABLE = "unavailable"
    CONFLICT = "conflict"


@dataclass
class StateObservationEvent:
    """A single state observation event."""

    event_id: str = field(default_factory=lambda: f"soe-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    run_id: str = ""
    kind: StateObservationKind = StateObservationKind.POLICY_STATE
    state_key: str = ""
    outcome: StateReadOutcome = StateReadOutcome.CURRENT
    observed_at: float = field(default_factory=time.time)
    staleness_seconds: float = 0.0
    snapshot_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "kind": self.kind.value,
            "state_key": self.state_key,
            "outcome": self.outcome.value,
            "observed_at": self.observed_at,
            "staleness_seconds": self.staleness_seconds,
            "snapshot_id": self.snapshot_id,
        }


@dataclass
class StateObservationReport:
    """Aggregated state observation report for a run."""

    agent_id: str
    run_id: str
    events: list[StateObservationEvent] = field(default_factory=list)

    @property
    def total_observations(self) -> int:
        return len(self.events)

    @property
    def policy_state_count(self) -> int:
        return sum(1 for e in self.events if e.kind == StateObservationKind.POLICY_STATE)

    @property
    def runtime_state_count(self) -> int:
        return sum(1 for e in self.events if e.kind == StateObservationKind.RUNTIME_STATE)

    @property
    def stale_count(self) -> int:
        return sum(1 for e in self.events if e.outcome == StateReadOutcome.STALE)

    @property
    def snapshot_count(self) -> int:
        return sum(1 for e in self.events if e.kind == StateObservationKind.SNAPSHOT)

    @property
    def by_kind(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "StateObservationReport.by_kind")

        result: dict[str, int] = {}
        for e in self.events:
            result[e.kind.value] = result.get(e.kind.value, 0) + 1
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_observations": self.total_observations,
            "policy_state_count": self.policy_state_count,
            "runtime_state_count": self.runtime_state_count,
            "stale_count": self.stale_count,
            "snapshot_count": self.snapshot_count,
            "by_kind": self.by_kind,
        }


class PolicyStateObserver:
    """G20 runtime observer: tracks policy-state and runtime-state reads.

    Lifecycle:
        observer = PolicyStateObserver(agent_id, run_id)
        observer.observe_policy("policy_hash_v3")
        observer.observe_runtime("agent_health_score")
        snap = observer.snapshot("before_mutation")
        report = observer.report
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = StateObservationReport(agent_id=agent_id, run_id=run_id)

    @property
    def report(self) -> StateObservationReport:
        return self._report

    def observe_policy(
        self,
        state_key: str,
        outcome: StateReadOutcome = StateReadOutcome.CURRENT,
        staleness_seconds: float = 0.0,
    ) -> StateObservationEvent:
        """Record a policy-state observation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PolicyStateObserver.observe_policy")

        event = StateObservationEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=StateObservationKind.POLICY_STATE,
            state_key=state_key,
            outcome=outcome,
            staleness_seconds=staleness_seconds,
        )
        self._report.events.append(event)
        return event

    def observe_runtime(
        self,
        state_key: str,
        outcome: StateReadOutcome = StateReadOutcome.CURRENT,
        staleness_seconds: float = 0.0,
    ) -> StateObservationEvent:
        """Record a runtime-state observation."""
        event = StateObservationEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=StateObservationKind.RUNTIME_STATE,
            state_key=state_key,
            outcome=outcome,
            staleness_seconds=staleness_seconds,
        )
        self._report.events.append(event)
        return event

    def probe_health(self, state_key: str) -> StateObservationEvent:
        """Record a health probe observation."""
        event = StateObservationEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=StateObservationKind.HEALTH_PROBE,
            state_key=state_key,
            outcome=StateReadOutcome.CURRENT,
        )
        self._report.events.append(event)
        return event

    def snapshot(self, label: str = "") -> StateObservationEvent:
        """Record a full-state snapshot event."""
        snap_id = f"snap-{uuid.uuid4().hex[:8]}"
        event = StateObservationEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=StateObservationKind.SNAPSHOT,
            state_key=label,
            outcome=StateReadOutcome.CURRENT,
            snapshot_id=snap_id,
        )
        self._report.events.append(event)
        return event
