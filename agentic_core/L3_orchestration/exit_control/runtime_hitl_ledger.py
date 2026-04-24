"""Runtime HITL ledger — persistent per-run state store.

Per ADR-023 G1, v1 uses a local SQLite file keyed by ``(run_id, trace_id)``.
Each row records the full lifecycle of an escalation:

    PENDING → (APPROVED | DENIED | TIMEOUT)

The ledger is the single source of truth for suspend-resume: the orchestrator
does NOT need to hold a suspended thread. On resume, the caller looks up state
by ``run_id`` and dispatches the persisted outcome.

G7 note: this ledger is self-contained; it does not require L3 orchestrator
RunState serialization. Apps that need orchestrator-level pause/resume (W5)
must additionally checkpoint their own runner state — out of W2 scope.

Hash-chain integrity (ADR-023 §5) is deferred to W7; the schema already
includes ``prev_hash`` and ``entry_hash`` columns for forward compatibility.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Mapping

from agentic_core.L2_execution.utils.write_gateway import ensure_dir
from agentic_core.L3_orchestration.exit_control.ledger_integrity import (
    AuditChain,
    AuditEventType,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass

DEFAULT_LEDGER_PATH = Path("artifacts/runtime/hitl_ledger.db")


class LedgerState(str, Enum):
    """Escalation lifecycle state."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"


_SCHEMA = """
CREATE TABLE IF NOT EXISTS hitl_ledger (
    ledger_id     TEXT PRIMARY KEY,
    run_id        TEXT NOT NULL,
    trace_id      TEXT NOT NULL,
    hitl_class    TEXT NOT NULL,
    approver_pool TEXT NOT NULL,
    timeout_s     INTEGER NOT NULL,
    policy_snapshot TEXT NOT NULL,
    envelope_json TEXT NOT NULL,
    state         TEXT NOT NULL,
    created_at    REAL NOT NULL,
    resolved_at   REAL,
    approver_id   TEXT,
    reason_code   TEXT,
    rationale     TEXT,
    prev_hash     TEXT NOT NULL,
    entry_hash    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_hitl_run ON hitl_ledger(run_id);
CREATE INDEX IF NOT EXISTS idx_hitl_state ON hitl_ledger(state);
"""


@dataclass(frozen=True)
class LedgerEntry:
    """Immutable view of a ledger row."""

    ledger_id: str
    run_id: str
    trace_id: str
    hitl_class: HitlClass
    approver_pool: str
    timeout_s: int
    policy_snapshot: str
    envelope: Mapping[str, Any]
    state: LedgerState
    created_at: float
    resolved_at: float | None = None
    approver_id: str | None = None
    reason_code: str | None = None
    rationale: str | None = None
    prev_hash: str = ""
    entry_hash: str = ""


@dataclass
class _InsertArgs:
    run_id: str
    trace_id: str
    hitl_class: HitlClass
    approver_pool: str
    timeout_s: int
    policy_snapshot: str
    envelope: Mapping[str, Any] = field(default_factory=dict)


class RuntimeHitlLedger:
    """SQLite-backed runtime HITL ledger.

    Concurrency: each instance holds one connection. Callers that share across
    threads must create per-thread instances or add external locking.
    """

    def __init__(
        self,
        path: Path | str | None = None,
        *,
        now: Callable[[], float] | None = None,
        audit_chain: AuditChain | None = None,
    ) -> None:
        self._path = Path(path) if path is not None else DEFAULT_LEDGER_PATH
        ensure_dir(self._path.parent)
        self._now = now or time.time
        self._conn = sqlite3.connect(str(self._path), isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._audit_chain = audit_chain

    # -- lifecycle -------------------------------------------------------

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "RuntimeHitlLedger":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()

    # -- writes ----------------------------------------------------------

    def record_escalation(
        self,
        *,
        run_id: str,
        trace_id: str,
        hitl_class: HitlClass,
        approver_pool: str,
        timeout_s: int,
        policy_snapshot: str,
        envelope: Mapping[str, Any] | None = None,
    ) -> LedgerEntry:
        """Create a PENDING escalation row. Returns the persisted entry."""
        args = _InsertArgs(
            run_id=run_id,
            trace_id=trace_id,
            hitl_class=hitl_class,
            approver_pool=approver_pool,
            timeout_s=timeout_s,
            policy_snapshot=policy_snapshot,
            envelope=envelope or {},
        )
        ledger_id = uuid.uuid4().hex
        created_at = self._now()
        prev_hash = self._latest_hash(run_id)
        payload = {
            "ledger_id": ledger_id,
            "run_id": args.run_id,
            "trace_id": args.trace_id,
            "hitl_class": args.hitl_class.value,
            "approver_pool": args.approver_pool,
            "timeout_s": args.timeout_s,
            "policy_snapshot": args.policy_snapshot,
            "envelope": dict(args.envelope),
            "state": LedgerState.PENDING.value,
            "created_at": created_at,
            "prev_hash": prev_hash,
        }
        entry_hash = _hash_payload(payload)
        envelope_json = json.dumps(payload["envelope"], sort_keys=True)
        self._conn.execute(
            """INSERT INTO hitl_ledger (
                ledger_id, run_id, trace_id, hitl_class, approver_pool,
                timeout_s, policy_snapshot, envelope_json, state, created_at,
                prev_hash, entry_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ledger_id,
                args.run_id,
                args.trace_id,
                args.hitl_class.value,
                args.approver_pool,
                args.timeout_s,
                args.policy_snapshot,
                envelope_json,
                LedgerState.PENDING.value,
                created_at,
                prev_hash,
                entry_hash,
            ),
        )
        self._emit_audit(
            ledger_id=ledger_id,
            run_id=args.run_id,
            event_type=AuditEventType.CREATED,
            payload={
                "hitl_class": args.hitl_class.value,
                "approver_pool": args.approver_pool,
                "timeout_s": args.timeout_s,
                "policy_snapshot": args.policy_snapshot,
                "trace_id": args.trace_id,
            },
            event_ts=created_at,
        )
        return self._get_entry(ledger_id)

    def record_approved(
        self,
        ledger_id: str,
        *,
        approver_id: str,
        rationale: str | None = None,
    ) -> LedgerEntry:
        return self._resolve(
            ledger_id,
            LedgerState.APPROVED,
            approver_id=approver_id,
            rationale=rationale,
        )

    def record_denied(
        self,
        ledger_id: str,
        *,
        approver_id: str,
        reason_code: str,
        rationale: str | None = None,
    ) -> LedgerEntry:
        return self._resolve(
            ledger_id,
            LedgerState.DENIED,
            approver_id=approver_id,
            reason_code=reason_code,
            rationale=rationale,
        )

    def record_timeout(self, ledger_id: str, *, reason_code: str = "TIMEOUT") -> LedgerEntry:
        return self._resolve(ledger_id, LedgerState.TIMEOUT, reason_code=reason_code)

    # -- reads -----------------------------------------------------------

    def get(self, ledger_id: str) -> LedgerEntry | None:
        row = self._conn.execute("SELECT * FROM hitl_ledger WHERE ledger_id = ?", (ledger_id,)).fetchone()
        return _row_to_entry(row) if row else None

    def list_by_run(self, run_id: str) -> list[LedgerEntry]:
        rows = self._conn.execute(
            "SELECT * FROM hitl_ledger WHERE run_id = ? ORDER BY created_at ASC",
            (run_id,),
        ).fetchall()
        return [_row_to_entry(r) for r in rows]

    def list_pending(self) -> list[LedgerEntry]:
        rows = self._conn.execute(
            "SELECT * FROM hitl_ledger WHERE state = ? ORDER BY created_at ASC",
            (LedgerState.PENDING.value,),
        ).fetchall()
        return [_row_to_entry(r) for r in rows]

    # -- internals -------------------------------------------------------

    def _resolve(
        self,
        ledger_id: str,
        new_state: LedgerState,
        *,
        approver_id: str | None = None,
        reason_code: str | None = None,
        rationale: str | None = None,
    ) -> LedgerEntry:
        current = self.get(ledger_id)
        if current is None:
            raise KeyError(f"ledger entry not found: {ledger_id}")
        if current.state is not LedgerState.PENDING:
            raise ValueError(f"ledger entry {ledger_id} already resolved as {current.state.value}")
        resolved_at = self._now()
        self._conn.execute(
            """UPDATE hitl_ledger
               SET state = ?, resolved_at = ?, approver_id = ?,
                   reason_code = ?, rationale = ?
               WHERE ledger_id = ?""",
            (new_state.value, resolved_at, approver_id, reason_code, rationale, ledger_id),
        )
        self._emit_audit(
            ledger_id=ledger_id,
            run_id=current.run_id,
            event_type=_STATE_TO_EVENT[new_state],
            payload={
                "approver_id": approver_id,
                "reason_code": reason_code,
                "rationale": rationale,
            },
            event_ts=resolved_at,
        )
        return self._get_entry(ledger_id)

    def _emit_audit(
        self,
        *,
        ledger_id: str,
        run_id: str,
        event_type: AuditEventType,
        payload: Mapping[str, Any],
        event_ts: float,
    ) -> None:
        if self._audit_chain is None:
            return
        self._audit_chain.append(
            ledger_id=ledger_id,
            run_id=run_id,
            event_type=event_type,
            payload=payload,
            event_ts=event_ts,
        )

    def _get_entry(self, ledger_id: str) -> LedgerEntry:
        entry = self.get(ledger_id)
        if entry is None:  # pragma: no cover — defensive, insert just happened
            raise RuntimeError(f"ledger entry vanished after write: {ledger_id}")
        return entry

    def _latest_hash(self, run_id: str) -> str:
        row = self._conn.execute(
            """SELECT entry_hash FROM hitl_ledger
               WHERE run_id = ? ORDER BY created_at DESC LIMIT 1""",
            (run_id,),
        ).fetchone()
        return row["entry_hash"] if row else ""


def _row_to_entry(row: sqlite3.Row) -> LedgerEntry:
    envelope = json.loads(row["envelope_json"]) if row["envelope_json"] else {}
    return LedgerEntry(
        ledger_id=row["ledger_id"],
        run_id=row["run_id"],
        trace_id=row["trace_id"],
        hitl_class=HitlClass(row["hitl_class"]),
        approver_pool=row["approver_pool"],
        timeout_s=int(row["timeout_s"]),
        policy_snapshot=row["policy_snapshot"],
        envelope=envelope,
        state=LedgerState(row["state"]),
        created_at=float(row["created_at"]),
        resolved_at=float(row["resolved_at"]) if row["resolved_at"] is not None else None,
        approver_id=row["approver_id"],
        reason_code=row["reason_code"],
        rationale=row["rationale"],
        prev_hash=row["prev_hash"] or "",
        entry_hash=row["entry_hash"] or "",
    )


def _hash_payload(payload: Mapping[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return sha256(blob).hexdigest()


_STATE_TO_EVENT: dict["LedgerState", AuditEventType] = {
    LedgerState.APPROVED: AuditEventType.APPROVED,
    LedgerState.DENIED: AuditEventType.DENIED,
    LedgerState.TIMEOUT: AuditEventType.TIMEOUT,
}


__all__ = [
    "DEFAULT_LEDGER_PATH",
    "LedgerEntry",
    "LedgerState",
    "RuntimeHitlLedger",
]
