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
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


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
        self, var_name: str, outcome: SecretAccessOutcome = SecretAccessOutcome.SUCCESS
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
        self, secret_name: str, secret_kind: SecretKind = SecretKind.API_KEY
    ) -> SecretAccessEvent:
        """Record a denied secret access."""
        return self.record_access(
            secret_name=secret_name,
            secret_kind=secret_kind,
            outcome=SecretAccessOutcome.DENIED,
        )
