"""Durable SQLite canonical store for L4/UWG.

The database is the canonical transaction boundary for committed state, the
append-only audit ledger, UWG receipts, durable write locks, lifecycle events,
and projection-outbox work. Filesystem and vector stores remain derived read
surfaces and are updated only from committed outbox records.
"""

from __future__ import annotations

import contextlib
import dataclasses
import json
import os
import sqlite3
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from agentic_core.L4_state.contracts.records import (
    L4_CONTRACT_SCHEMA_VERSION,
    AuditLedgerRecord,
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
    UWGCommitReceipt,
    UWGValidationReceipt,
    WriteLockReceipt,
    record_canonical_payload,
    stamp_digest,
)

SCHEMA_VERSION = "l4-sqlite-v1"
GENESIS_HASH = compute_deterministic_digest(
    {"audit_ledger_genesis": L4_CONTRACT_SCHEMA_VERSION}
)


class L4StorageError(RuntimeError):
    """Base exception for canonical L4 storage failures."""


class ReplayConflictError(L4StorageError):
    """Raised when a replay key is reused with different logical content."""


class DurableLockContentionError(L4StorageError):
    """Raised when a durable target-surface lock is held by another owner."""


class ProjectionStateError(L4StorageError):
    """Raised on an invalid projection-outbox transition."""


class LifecycleTransitionError(L4StorageError):
    """Raised on an invalid or unauthorized lifecycle transition."""


@dataclass(frozen=True)
class ProjectionTask:
    projection_id: str
    commit_receipt_id: str
    projection_type: str
    target_surface: str
    payload: dict[str, Any]
    payload_digest: str
    status: str
    attempt_count: int
    last_error: str = ""


@dataclass(frozen=True)
class AtomicCommitResult:
    commit_receipt: UWGCommitReceipt
    audit_record: AuditLedgerRecord
    audit_append_receipt: Any
    state_version_ids: tuple[str, ...]
    projection_tasks: tuple[ProjectionTask, ...]
    fencing_tokens: dict[str, int]
    logical_hash: str
    idempotent_replay: bool = False


def _json_ready(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _json_ready(dataclasses.asdict(value))
    if isinstance(value, tuple):
        return [_json_ready(v) for v in value]
    if isinstance(value, list):
        return [_json_ready(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    return value


def _json_dumps(value: Any) -> str:
    return json.dumps(
        _json_ready(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _json_loads(value: str) -> Any:
    return json.loads(value)


def _tuple_fields(payload: Mapping[str, Any], names: Sequence[str]) -> dict[str, Any]:
    out = dict(payload)
    for name in names:
        if name in out and isinstance(out[name], list):
            out[name] = tuple(out[name])
    return out


def default_l4_sqlite_path() -> Path:
    explicit = str(os.environ.get("L4_SQLITE_PATH", "")).strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    runtime_root = Path(
        os.environ.get("AGENTIC_RUNTIME_DIR", Path.cwd() / ".runtime")
    ).expanduser()
    return (runtime_root / "l4" / "l4_state.sqlite3").resolve()


def configured_l4_backend_name() -> str:
    explicit = str(os.environ.get("L4_STORAGE_BACKEND", "")).strip().lower()
    if explicit:
        return explicit
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return "memory"
    return "sqlite"


def _logical_state_diff_payload(row: StateDiff, canonical_state: Any) -> dict[str, Any]:
    return {
        "state_diff_id": row.state_diff_id,
        "target_surface": row.target_surface,
        "operation_type": row.operation_type,
        "after_candidate": row.after_candidate,
        "schema_ref": row.schema_ref,
        "blast_radius": row.blast_radius,
        "rollback_plan_ref": row.rollback_plan_ref,
        "proposed_by_surface": row.proposed_by_surface,
        "before_ref": row.before_ref,
        "validation_rules": sorted(row.validation_rules),
        "policy_refs": sorted(row.policy_refs),
        "replay_refs": sorted(row.replay_refs),
        "audit_refs": sorted(row.audit_refs),
        "canonical_state": _json_ready(canonical_state),
    }


def logical_commit_hash(
    *,
    commit_request: CommitRequest,
    state_diffs: Sequence[StateDiff],
    rollback_plan: RollbackPlan,
    refresh_plan: ReadSurfaceRefreshPlan,
    state_payload_overrides: Mapping[str, Any] | None = None,
) -> str:
    """Hash semantic commit content, excluding UUIDs, clocks and snapshots."""

    overrides = dict(state_payload_overrides or {})
    return compute_deterministic_digest(
        {
            "tenant_id": commit_request.tenant_id,
            "policy_hash": commit_request.policy_hash,
            "blueprint_hash": commit_request.blueprint_hash,
            "registry_digest_set": sorted(commit_request.registry_digest_set),
            "replay_key": commit_request.replay_key,
            "route_contract_ref": commit_request.route_contract_ref,
            "clearance_proof_id": commit_request.clearance_proof_id,
            "cleared_exit_review_packet_ref": commit_request.cleared_exit_review_packet_ref,
            "capability_token_ref": commit_request.capability_token_ref,
            "gate_verdict_refs": sorted(commit_request.gate_verdict_refs),
            "l5_certification_ref": commit_request.l5_certification_ref,
            "l5_certification_refs": sorted(commit_request.l5_certification_refs),
            "state_diffs": [
                _logical_state_diff_payload(
                    row, overrides.get(row.state_diff_id, row.after_candidate)
                )
                for row in sorted(state_diffs, key=lambda item: item.state_diff_id)
            ],
            "rollback_plan": {
                "blast_radius": rollback_plan.blast_radius,
                "target_surfaces": sorted(rollback_plan.target_surfaces),
                "before_snapshot_refs": sorted(rollback_plan.before_snapshot_refs),
                "rollback_operation_types": sorted(rollback_plan.rollback_operation_types),
                "safety_preconditions": sorted(rollback_plan.safety_preconditions),
                "policy_refs": sorted(rollback_plan.policy_refs),
                "schema_refs": sorted(rollback_plan.schema_refs),
                "test_refs": sorted(rollback_plan.test_refs),
                "audit_refs": sorted(rollback_plan.audit_refs),
            },
            "refresh_plan": {
                "stale_projection_policy": refresh_plan.stale_projection_policy,
                "retry_policy": refresh_plan.retry_policy,
                "policy_hash": refresh_plan.policy_hash,
                "blueprint_hash": refresh_plan.blueprint_hash,
                "affected_surfaces": sorted(refresh_plan.affected_surfaces),
                "required_refreshes": list(refresh_plan.required_refreshes),
                "optional_refreshes": list(refresh_plan.optional_refreshes),
                "refresh_order": list(refresh_plan.refresh_order),
                "rollback_policy_ref": refresh_plan.rollback_policy_ref,
            },
        }
    )


class SQLiteL4Backend:
    """Canonical SQLite backend shared by UWG and the durable audit ledger."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path or default_l4_sqlite_path()).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._thread_lock = threading.RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(self.path), timeout=30.0, isolation_level=None, check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    @contextlib.contextmanager
    def transaction(self, *, immediate: bool = True) -> Iterator[sqlite3.Connection]:
        with self._thread_lock:
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _initialize(self) -> None:
        with self.transaction() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS l4_meta (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS l4_audit_ledger (
                    ledger_sequence INTEGER PRIMARY KEY,
                    audit_record_id TEXT NOT NULL UNIQUE,
                    record_json TEXT NOT NULL,
                    prev_chain_hash TEXT NOT NULL,
                    chain_hash TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS l4_validation_receipts (
                    validation_receipt_id TEXT PRIMARY KEY,
                    commit_request_id TEXT NOT NULL,
                    receipt_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS l4_commit_requests (
                    commit_request_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    replay_key TEXT NOT NULL,
                    logical_hash TEXT NOT NULL,
                    request_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS l4_commit_receipts (
                    commit_receipt_id TEXT PRIMARY KEY,
                    commit_request_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    replay_key TEXT NOT NULL,
                    logical_hash TEXT NOT NULL,
                    audit_record_id TEXT NOT NULL,
                    receipt_json TEXT NOT NULL,
                    UNIQUE (tenant_id, replay_key),
                    FOREIGN KEY (audit_record_id) REFERENCES l4_audit_ledger(audit_record_id)
                );
                CREATE TABLE IF NOT EXISTS l4_state_versions (
                    state_version_id TEXT PRIMARY KEY,
                    commit_receipt_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    state_surface TEXT NOT NULL,
                    state_diff_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    logical_hash TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    lifecycle_stage TEXT NOT NULL DEFAULT 'active',
                    created_sequence INTEGER NOT NULL,
                    UNIQUE (commit_receipt_id, state_diff_id),
                    FOREIGN KEY (commit_receipt_id) REFERENCES l4_commit_receipts(commit_receipt_id)
                );
                CREATE TABLE IF NOT EXISTS l4_projection_outbox (
                    projection_id TEXT PRIMARY KEY,
                    commit_receipt_id TEXT NOT NULL,
                    projection_type TEXT NOT NULL,
                    target_surface TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_digest TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT NOT NULL DEFAULT '',
                    created_sequence INTEGER NOT NULL,
                    completed_sequence INTEGER,
                    UNIQUE (commit_receipt_id, projection_type, target_surface),
                    FOREIGN KEY (commit_receipt_id) REFERENCES l4_commit_receipts(commit_receipt_id)
                );
                CREATE TABLE IF NOT EXISTS l4_surface_locks (
                    state_surface TEXT PRIMARY KEY,
                    lock_owner TEXT NOT NULL DEFAULT '',
                    fencing_token INTEGER NOT NULL DEFAULT 0,
                    lock_status TEXT NOT NULL DEFAULT 'RELEASED',
                    commit_request_id TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS l4_lifecycle_events (
                    lifecycle_event_id TEXT PRIMARY KEY,
                    state_version_id TEXT NOT NULL,
                    source_commit_receipt_id TEXT NOT NULL,
                    from_stage TEXT NOT NULL,
                    to_stage TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    created_sequence INTEGER NOT NULL,
                    FOREIGN KEY (state_version_id) REFERENCES l4_state_versions(state_version_id)
                );
                CREATE INDEX IF NOT EXISTS ix_l4_state_surface
                    ON l4_state_versions(tenant_id, state_surface, created_sequence);
                CREATE INDEX IF NOT EXISTS ix_l4_outbox_status
                    ON l4_projection_outbox(status, created_sequence);
                CREATE INDEX IF NOT EXISTS ix_l4_audit_record
                    ON l4_audit_ledger(audit_record_id);
                """
            )
            conn.execute(
                "INSERT OR REPLACE INTO l4_meta(key, value) VALUES('schema_version', ?)",
                (SCHEMA_VERSION,),
            )

    def health_check(self) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("PRAGMA integrity_check").fetchone()
        return {
            "backend": "sqlite",
            "path": str(self.path),
            "schema_version": SCHEMA_VERSION,
            "integrity": str(row[0] if row else "unknown"),
            "durable": True,
        }

    def _last_audit_position(self, conn: sqlite3.Connection) -> tuple[int, str]:
        row = conn.execute(
            "SELECT ledger_sequence, chain_hash FROM l4_audit_ledger "
            "ORDER BY ledger_sequence DESC LIMIT 1"
        ).fetchone()
        return (0, GENESIS_HASH) if row is None else (
            int(row["ledger_sequence"]), str(row["chain_hash"])
        )

    def _append_audit_event_in_tx(
        self,
        conn: sqlite3.Connection,
        *,
        event_type: str,
        state_surface: str,
        operation_type: str,
        tenant_id: str,
        policy_hash: str,
        blueprint_hash: str,
        snapshot_before: str,
        snapshot_after: str | None = None,
        actor_surface: str = "UWG",
        mutation_source: str = "UWG",
        request_id: str | None = None,
        run_id: str | None = None,
        trace_root: str | None = None,
        receipt_refs: Sequence[str] = (),
        state_refs: Sequence[str] = (),
        reason_codes: Sequence[str] = (),
    ) -> AuditLedgerRecord:
        last_sequence, prev_chain_hash = self._last_audit_position(conn)
        sequence = last_sequence + 1
        record = AuditLedgerRecord(
            audit_record_id=str(uuid.uuid4()),
            ledger_sequence=sequence,
            event_type=event_type,
            state_surface=state_surface,
            operation_type=operation_type,
            tenant_id=tenant_id,
            policy_hash=policy_hash,
            blueprint_hash=blueprint_hash,
            snapshot_before=snapshot_before,
            snapshot_after=snapshot_after,
            actor_surface=actor_surface,
            mutation_source=mutation_source,
            created_at=str(sequence),
            request_id=request_id,
            run_id=run_id,
            trace_root=trace_root,
            receipt_refs=tuple(receipt_refs),
            state_refs=tuple(state_refs),
            reason_codes=tuple(reason_codes),
            prev_chain_hash=prev_chain_hash,
        )
        record = stamp_digest(record)
        chain_hash = compute_deterministic_digest(
            {"prev_chain_hash": prev_chain_hash, "record_digest": record.deterministic_digest}
        )
        record = stamp_digest(
            dataclasses.replace(record, chain_hash=chain_hash, deterministic_digest="")
        )
        conn.execute(
            "INSERT INTO l4_audit_ledger "
            "(ledger_sequence, audit_record_id, record_json, prev_chain_hash, chain_hash) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                record.ledger_sequence,
                record.audit_record_id,
                _json_dumps(record),
                record.prev_chain_hash,
                record.chain_hash,
            ),
        )
        return record

    def load_audit_records(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT record_json FROM l4_audit_ledger ORDER BY ledger_sequence"
            ).fetchall()
        return [_json_loads(str(row["record_json"])) for row in rows]

    def persist_audit_record(self, record: AuditLedgerRecord) -> None:
        with self.transaction() as conn:
            last_sequence, last_hash = self._last_audit_position(conn)
            if record.ledger_sequence != last_sequence + 1:
                raise L4StorageError(
                    f"audit sequence mismatch: got={record.ledger_sequence} expected={last_sequence + 1}"
                )
            if record.prev_chain_hash != last_hash:
                raise L4StorageError("audit prev_chain_hash does not match durable head")
            conn.execute(
                "INSERT INTO l4_audit_ledger "
                "(ledger_sequence, audit_record_id, record_json, prev_chain_hash, chain_hash) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    record.ledger_sequence,
                    record.audit_record_id,
                    _json_dumps(record),
                    record.prev_chain_hash,
                    record.chain_hash,
                ),
            )

    def _acquire_surface_locks(
        self,
        conn: sqlite3.Connection,
        *,
        target_surfaces: Sequence[str],
        owner: str,
        commit_request_id: str,
    ) -> dict[str, int]:
        fencing_tokens: dict[str, int] = {}
        for surface in sorted(set(target_surfaces)):
            row = conn.execute(
                "SELECT lock_owner, lock_status, fencing_token "
                "FROM l4_surface_locks WHERE state_surface=?",
                (surface,),
            ).fetchone()
            if row is not None and str(row["lock_status"]) == "HELD" and str(
                row["lock_owner"]
            ) != owner:
                raise DurableLockContentionError(surface)
            next_token = int(row["fencing_token"] if row else 0) + 1
            conn.execute(
                "INSERT INTO l4_surface_locks "
                "(state_surface, lock_owner, fencing_token, lock_status, commit_request_id) "
                "VALUES (?, ?, ?, 'HELD', ?) "
                "ON CONFLICT(state_surface) DO UPDATE SET "
                "lock_owner=excluded.lock_owner, fencing_token=excluded.fencing_token, "
                "lock_status='HELD', commit_request_id=excluded.commit_request_id",
                (surface, owner, next_token, commit_request_id),
            )
            fencing_tokens[surface] = next_token
        return fencing_tokens

    def _release_surface_locks(
        self, conn: sqlite3.Connection, *, target_surfaces: Sequence[str], owner: str
    ) -> None:
        for surface in sorted(set(target_surfaces)):
            conn.execute(
                "UPDATE l4_surface_locks SET lock_owner='', lock_status='RELEASED' "
                "WHERE state_surface=? AND lock_owner=?",
                (surface, owner),
            )

    @staticmethod
    def _audit_record_from_payload(payload: Mapping[str, Any]) -> AuditLedgerRecord:
        return AuditLedgerRecord(
            **_tuple_fields(payload, ("receipt_refs", "state_refs", "reason_codes"))
        )

    @staticmethod
    def _commit_receipt_from_payload(payload: Mapping[str, Any]) -> UWGCommitReceipt:
        return UWGCommitReceipt(
            **_tuple_fields(
                payload,
                (
                    "state_diff_refs",
                    "affected_state_surfaces",
                    "audit_refs",
                    "gate_verdict_refs",
                    "registry_digest_set",
                ),
            )
        )

    @staticmethod
    def _projection_task_from_row(row: sqlite3.Row) -> ProjectionTask:
        return ProjectionTask(
            projection_id=str(row["projection_id"]),
            commit_receipt_id=str(row["commit_receipt_id"]),
            projection_type=str(row["projection_type"]),
            target_surface=str(row["target_surface"]),
            payload=dict(_json_loads(str(row["payload_json"]))),
            payload_digest=str(row["payload_digest"]),
            status=str(row["status"]),
            attempt_count=int(row["attempt_count"]),
            last_error=str(row["last_error"]),
        )

    def atomic_commit(
        self,
        *,
        commit_request: CommitRequest,
        state_diffs: Sequence[StateDiff],
        rollback_plan: RollbackPlan,
        refresh_plan: ReadSurfaceRefreshPlan,
        validation_receipt: UWGValidationReceipt,
        write_lock_receipt: WriteLockReceipt,
        snapshot_before: str,
        snapshot_after: str,
        state_payload_overrides: Mapping[str, Any] | None = None,
        projection_context: Mapping[str, Any] | None = None,
    ) -> AtomicCommitResult:
        if validation_receipt.validation_status != "PASS":
            raise L4StorageError("atomic_commit requires PASS validation receipt")
        target_surfaces = tuple(commit_request.affected_state_surfaces) or tuple(
            row.target_surface for row in state_diffs
        )
        owner = f"UWG::{commit_request.commit_request_id}"
        overrides = dict(state_payload_overrides or {})
        projection_ctx = dict(projection_context or {})
        logical_hash = logical_commit_hash(
            commit_request=commit_request,
            state_diffs=state_diffs,
            rollback_plan=rollback_plan,
            refresh_plan=refresh_plan,
            state_payload_overrides=overrides,
        )
        from agentic_core.L4_state.audit.audit_ledger import AuditAppendReceipt

        with self.transaction() as conn:
            existing = conn.execute(
                "SELECT receipt_json, logical_hash, audit_record_id "
                "FROM l4_commit_receipts WHERE tenant_id=? AND replay_key=?",
                (commit_request.tenant_id, commit_request.replay_key),
            ).fetchone()
            if existing is not None:
                if str(existing["logical_hash"]) != logical_hash:
                    raise ReplayConflictError(
                        f"replay_key conflict for {commit_request.tenant_id}:{commit_request.replay_key}"
                    )
                receipt = self._commit_receipt_from_payload(
                    _json_loads(str(existing["receipt_json"]))
                )
                audit_row = conn.execute(
                    "SELECT record_json FROM l4_audit_ledger WHERE audit_record_id=?",
                    (str(existing["audit_record_id"]),),
                ).fetchone()
                if audit_row is None:
                    raise L4StorageError("idempotent commit is missing durable audit record")
                audit_record = self._audit_record_from_payload(
                    _json_loads(str(audit_row["record_json"]))
                )
                audit_append_receipt = AuditAppendReceipt(
                    audit_append_receipt_id=receipt.audit_append_receipt_ref,
                    audit_record_id=audit_record.audit_record_id,
                    ledger_sequence=audit_record.ledger_sequence,
                    snapshot_position=audit_record.ledger_sequence,
                    deterministic_digest=audit_record.deterministic_digest,
                    prev_chain_hash=audit_record.prev_chain_hash,
                    chain_hash=audit_record.chain_hash,
                )
                state_rows = conn.execute(
                    "SELECT state_version_id FROM l4_state_versions "
                    "WHERE commit_receipt_id=? ORDER BY state_version_id",
                    (receipt.commit_receipt_id,),
                ).fetchall()
                task_rows = conn.execute(
                    "SELECT * FROM l4_projection_outbox WHERE commit_receipt_id=? "
                    "ORDER BY created_sequence, projection_id",
                    (receipt.commit_receipt_id,),
                ).fetchall()
                return AtomicCommitResult(
                    commit_receipt=receipt,
                    audit_record=audit_record,
                    audit_append_receipt=audit_append_receipt,
                    state_version_ids=tuple(str(row["state_version_id"]) for row in state_rows),
                    projection_tasks=tuple(
                        self._projection_task_from_row(row) for row in task_rows
                    ),
                    fencing_tokens={},
                    logical_hash=logical_hash,
                    idempotent_replay=True,
                )

            fencing_tokens = self._acquire_surface_locks(
                conn,
                target_surfaces=target_surfaces,
                owner=owner,
                commit_request_id=commit_request.commit_request_id,
            )
            commit_receipt_id = str(uuid.uuid4())
            audit_append_receipt_id = str(uuid.uuid4())
            audit_record = self._append_audit_event_in_tx(
                conn,
                event_type="atomic_commit_applied",
                state_surface=",".join(target_surfaces) if target_surfaces else "-",
                operation_type="commit",
                tenant_id=commit_request.tenant_id,
                policy_hash=commit_request.policy_hash,
                blueprint_hash=commit_request.blueprint_hash,
                snapshot_before=snapshot_before,
                snapshot_after=snapshot_after,
                request_id=commit_request.request_id,
                run_id=commit_request.run_id,
                trace_root=commit_request.trace_root,
                receipt_refs=(
                    commit_request.commit_request_id,
                    validation_receipt.uwg_validation_receipt_id,
                    write_lock_receipt.write_lock_receipt_id,
                    commit_receipt_id,
                ),
                state_refs=tuple(row.state_diff_id for row in state_diffs),
            )
            sequence = audit_record.ledger_sequence
            audit_append_receipt = AuditAppendReceipt(
                audit_append_receipt_id=audit_append_receipt_id,
                audit_record_id=audit_record.audit_record_id,
                ledger_sequence=sequence,
                snapshot_position=sequence,
                deterministic_digest=audit_record.deterministic_digest,
                prev_chain_hash=audit_record.prev_chain_hash,
                chain_hash=audit_record.chain_hash,
            )
            commit_receipt = stamp_digest(
                UWGCommitReceipt(
                    commit_receipt_id=commit_receipt_id,
                    commit_request_ref=commit_request.commit_request_id,
                    write_lock_receipt_ref=write_lock_receipt.write_lock_receipt_id,
                    uwg_validation_receipt_ref=validation_receipt.uwg_validation_receipt_id,
                    snapshot_before=snapshot_before,
                    snapshot_after=snapshot_after,
                    read_surface_refresh_plan_ref=refresh_plan.refresh_plan_id,
                    audit_append_receipt_ref=audit_append_receipt.audit_append_receipt_id,
                    committed_at=str(sequence),
                    state_diff_refs=tuple(row.state_diff_id for row in state_diffs),
                    affected_state_surfaces=target_surfaces,
                    audit_refs=tuple(commit_request.audit_refs),
                    l5_certification_ref=commit_request.l5_certification_ref,
                    source_surface=commit_request.source_surface,
                    policy_hash=commit_request.policy_hash,
                    blueprint_hash=commit_request.blueprint_hash,
                    replay_key=commit_request.replay_key,
                    gate_verdict_refs=tuple(commit_request.gate_verdict_refs),
                    cleared_exit_review_packet_ref=commit_request.cleared_exit_review_packet_ref,
                    registry_digest_set=tuple(commit_request.registry_digest_set),
                    clearance_proof_id=commit_request.clearance_proof_id,
                    staged_diff_hash=commit_request.staged_diff_hash,
                    content_hash=logical_hash,
                    prev_chain_hash=audit_record.prev_chain_hash,
                    chain_hash=audit_record.chain_hash,
                    validator_receipt_id=(
                        commit_request.validator_receipt_id
                        or validation_receipt.uwg_validation_receipt_id
                    ),
                )
            )
            conn.execute(
                "INSERT INTO l4_validation_receipts "
                "(validation_receipt_id, commit_request_id, receipt_json) VALUES (?, ?, ?)",
                (
                    validation_receipt.uwg_validation_receipt_id,
                    commit_request.commit_request_id,
                    _json_dumps(validation_receipt),
                ),
            )
            conn.execute(
                "INSERT INTO l4_commit_requests "
                "(commit_request_id, tenant_id, replay_key, logical_hash, request_json) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    commit_request.commit_request_id,
                    commit_request.tenant_id,
                    commit_request.replay_key,
                    logical_hash,
                    _json_dumps(commit_request),
                ),
            )
            conn.execute(
                "INSERT INTO l4_commit_receipts "
                "(commit_receipt_id, commit_request_id, tenant_id, replay_key, logical_hash, "
                "audit_record_id, receipt_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    commit_receipt.commit_receipt_id,
                    commit_request.commit_request_id,
                    commit_request.tenant_id,
                    commit_request.replay_key,
                    logical_hash,
                    audit_record.audit_record_id,
                    _json_dumps(commit_receipt),
                ),
            )

            state_version_ids: list[str] = []
            state_payloads: list[dict[str, Any]] = []
            for row in state_diffs:
                state_payload = overrides.get(row.state_diff_id, row.after_candidate)
                payload = {
                    "state_diff": record_canonical_payload(row),
                    "canonical_state": _json_ready(state_payload),
                }
                state_version_id = "l4sv:" + compute_deterministic_digest(
                    {
                        "tenant_id": commit_request.tenant_id,
                        "surface": row.target_surface,
                        "state_diff_id": row.state_diff_id,
                        "logical_hash": logical_hash,
                    }
                )
                conn.execute(
                    "INSERT INTO l4_state_versions "
                    "(state_version_id, commit_receipt_id, tenant_id, state_surface, "
                    "state_diff_id, operation_type, logical_hash, payload_json, "
                    "lifecycle_stage, created_sequence) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)",
                    (
                        state_version_id,
                        commit_receipt.commit_receipt_id,
                        commit_request.tenant_id,
                        row.target_surface,
                        row.state_diff_id,
                        row.operation_type,
                        logical_hash,
                        _json_dumps(payload),
                        sequence,
                    ),
                )
                state_version_ids.append(state_version_id)
                state_payloads.append(
                    {
                        "state_version_id": state_version_id,
                        "state_surface": row.target_surface,
                        "state_diff_id": row.state_diff_id,
                        "operation_type": row.operation_type,
                        "payload": payload,
                    }
                )

            projection_tasks: list[ProjectionTask] = []
            projection_types = tuple(
                dict.fromkeys(
                    (*refresh_plan.required_refreshes, *refresh_plan.optional_refreshes)
                )
            )
            for projection_type in projection_types:
                target_surface = (
                    target_surfaces[0]
                    if len(target_surfaces) == 1
                    else ",".join(target_surfaces)
                )
                payload = {
                    "schema_version": "l4_projection_task.v1",
                    "source_commit_receipt_id": commit_receipt.commit_receipt_id,
                    "source_commit_content_hash": logical_hash,
                    "policy_hash": commit_request.policy_hash,
                    "blueprint_hash": commit_request.blueprint_hash,
                    "replay_key": commit_request.replay_key,
                    "projection_type": projection_type,
                    "target_surface": target_surface,
                    "state_versions": state_payloads,
                    "projection_context": projection_ctx,
                }
                payload_digest = compute_deterministic_digest(payload)
                projection_id = "l4proj:" + compute_deterministic_digest(
                    {
                        "commit_receipt_id": commit_receipt.commit_receipt_id,
                        "projection_type": projection_type,
                        "target_surface": target_surface,
                    }
                )
                conn.execute(
                    "INSERT INTO l4_projection_outbox "
                    "(projection_id, commit_receipt_id, projection_type, target_surface, "
                    "payload_json, payload_digest, status, attempt_count, last_error, "
                    "created_sequence) VALUES (?, ?, ?, ?, ?, ?, 'PENDING', 0, '', ?)",
                    (
                        projection_id,
                        commit_receipt.commit_receipt_id,
                        projection_type,
                        target_surface,
                        _json_dumps(payload),
                        payload_digest,
                        sequence,
                    ),
                )
                projection_tasks.append(
                    ProjectionTask(
                        projection_id=projection_id,
                        commit_receipt_id=commit_receipt.commit_receipt_id,
                        projection_type=projection_type,
                        target_surface=target_surface,
                        payload=payload,
                        payload_digest=payload_digest,
                        status="PENDING",
                        attempt_count=0,
                    )
                )
            self._release_surface_locks(
                conn, target_surfaces=target_surfaces, owner=owner
            )

        return AtomicCommitResult(
            commit_receipt=commit_receipt,
            audit_record=audit_record,
            audit_append_receipt=audit_append_receipt,
            state_version_ids=tuple(state_version_ids),
            projection_tasks=tuple(projection_tasks),
            fencing_tokens=fencing_tokens,
            logical_hash=logical_hash,
            idempotent_replay=False,
        )

    def list_projection_tasks(
        self,
        *,
        commit_receipt_id: str | None = None,
        statuses: Sequence[str] = ("PENDING", "FAILED"),
    ) -> list[ProjectionTask]:
        clauses: list[str] = []
        values: list[Any] = []
        if commit_receipt_id:
            clauses.append("commit_receipt_id=?")
            values.append(commit_receipt_id)
        if statuses:
            placeholders = ",".join("?" for _ in statuses)
            clauses.append(f"status IN ({placeholders})")
            values.extend(statuses)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM l4_projection_outbox"
                + where
                + " ORDER BY created_sequence, projection_id",
                tuple(values),
            ).fetchall()
        return [self._projection_task_from_row(row) for row in rows]

    def claim_projection(self, projection_id: str) -> ProjectionTask:
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT * FROM l4_projection_outbox WHERE projection_id=?",
                (projection_id,),
            ).fetchone()
            if row is None:
                raise ProjectionStateError(f"unknown projection_id={projection_id}")
            if str(row["status"]) not in {"PENDING", "FAILED"}:
                raise ProjectionStateError(
                    f"projection {projection_id} is {row['status']}, not claimable"
                )
            conn.execute(
                "UPDATE l4_projection_outbox SET status='RUNNING', "
                "attempt_count=attempt_count+1, last_error='' WHERE projection_id=?",
                (projection_id,),
            )
            updated = conn.execute(
                "SELECT * FROM l4_projection_outbox WHERE projection_id=?",
                (projection_id,),
            ).fetchone()
            assert updated is not None
            return self._projection_task_from_row(updated)

    def _projection_context_row(
        self, conn: sqlite3.Connection, projection_id: str
    ) -> sqlite3.Row:
        row = conn.execute(
            "SELECT o.*, c.tenant_id, c.receipt_json, r.request_json "
            "FROM l4_projection_outbox o "
            "JOIN l4_commit_receipts c ON c.commit_receipt_id=o.commit_receipt_id "
            "JOIN l4_commit_requests r ON r.commit_request_id=c.commit_request_id "
            "WHERE o.projection_id=?",
            (projection_id,),
        ).fetchone()
        if row is None:
            raise ProjectionStateError(f"unknown projection_id={projection_id}")
        return row

    def complete_projection(
        self,
        projection_id: str,
        *,
        observed_payload_digest: str,
        receipt_payload: Mapping[str, Any] | None = None,
    ) -> AuditLedgerRecord:
        with self.transaction() as conn:
            row = self._projection_context_row(conn, projection_id)
            if str(row["payload_digest"]) != observed_payload_digest:
                raise ProjectionStateError("projection read-after-write digest mismatch")
            if str(row["status"]) not in {"RUNNING", "PENDING", "FAILED"}:
                raise ProjectionStateError(
                    f"projection {projection_id} cannot complete from {row['status']}"
                )
            task_payload = dict(_json_loads(str(row["payload_json"])))
            if receipt_payload:
                task_payload["projection_receipt"] = dict(receipt_payload)
            request_payload = dict(_json_loads(str(row["request_json"])))
            commit_payload = dict(_json_loads(str(row["receipt_json"])))
            audit_record = self._append_audit_event_in_tx(
                conn,
                event_type="read_surface_refresh_completed",
                state_surface=str(row["target_surface"]),
                operation_type="projection_complete",
                tenant_id=str(row["tenant_id"]),
                policy_hash=str(request_payload.get("policy_hash") or "-"),
                blueprint_hash=str(request_payload.get("blueprint_hash") or "-"),
                snapshot_before=str(commit_payload.get("snapshot_before") or "-"),
                snapshot_after=str(commit_payload.get("snapshot_after") or "-"),
                request_id=str(request_payload.get("request_id") or "") or None,
                run_id=str(request_payload.get("run_id") or "") or None,
                trace_root=str(request_payload.get("trace_root") or "") or None,
                receipt_refs=(projection_id, str(row["commit_receipt_id"])),
                state_refs=(str(row["projection_type"]),),
            )
            conn.execute(
                "UPDATE l4_projection_outbox SET status='COMPLETE', last_error='', "
                "payload_json=?, completed_sequence=? WHERE projection_id=?",
                (_json_dumps(task_payload), audit_record.ledger_sequence, projection_id),
            )
            return audit_record

    def fail_projection(self, projection_id: str, *, error: str) -> AuditLedgerRecord:
        with self.transaction() as conn:
            row = self._projection_context_row(conn, projection_id)
            request_payload = dict(_json_loads(str(row["request_json"])))
            commit_payload = dict(_json_loads(str(row["receipt_json"])))
            error_text = str(error)[:4000]
            audit_record = self._append_audit_event_in_tx(
                conn,
                event_type="read_surface_refresh_failed",
                state_surface=str(row["target_surface"]),
                operation_type="projection_failed",
                tenant_id=str(row["tenant_id"]),
                policy_hash=str(request_payload.get("policy_hash") or "-"),
                blueprint_hash=str(request_payload.get("blueprint_hash") or "-"),
                snapshot_before=str(commit_payload.get("snapshot_before") or "-"),
                snapshot_after=str(commit_payload.get("snapshot_after") or "-"),
                request_id=str(request_payload.get("request_id") or "") or None,
                run_id=str(request_payload.get("run_id") or "") or None,
                trace_root=str(request_payload.get("trace_root") or "") or None,
                receipt_refs=(projection_id, str(row["commit_receipt_id"])),
                state_refs=(str(row["projection_type"]),),
                reason_codes=("projection_failed", error_text),
            )
            conn.execute(
                "UPDATE l4_projection_outbox SET status='FAILED', last_error=? "
                "WHERE projection_id=?",
                (error_text, projection_id),
            )
            return audit_record

    def get_commit_receipt_payload(self, commit_receipt_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT receipt_json FROM l4_commit_receipts WHERE commit_receipt_id=?",
                (commit_receipt_id,),
            ).fetchone()
        return None if row is None else dict(_json_loads(str(row["receipt_json"])))

    def get_state_versions(self, commit_receipt_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM l4_state_versions WHERE commit_receipt_id=? "
                "ORDER BY state_version_id",
                (commit_receipt_id,),
            ).fetchall()
        return [
            {
                "state_version_id": str(row["state_version_id"]),
                "commit_receipt_id": str(row["commit_receipt_id"]),
                "tenant_id": str(row["tenant_id"]),
                "state_surface": str(row["state_surface"]),
                "state_diff_id": str(row["state_diff_id"]),
                "operation_type": str(row["operation_type"]),
                "logical_hash": str(row["logical_hash"]),
                "payload": _json_loads(str(row["payload_json"])),
                "lifecycle_stage": str(row["lifecycle_stage"]),
                "created_sequence": int(row["created_sequence"]),
            }
            for row in rows
        ]

    def transition_lifecycle(
        self,
        *,
        state_version_id: str,
        source_commit_receipt_id: str,
        target_stage: str,
        reason: str,
        authorized_by_uwg: bool,
    ) -> str:
        if not authorized_by_uwg:
            raise LifecycleTransitionError("lifecycle transition requires UWG authority")
        allowed = {
            "active": {"frozen", "archived"},
            "frozen": {"active", "archived"},
            "archived": {"purged"},
            "purged": set(),
        }
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT s.*, c.tenant_id, c.receipt_json, r.request_json "
                "FROM l4_state_versions s "
                "JOIN l4_commit_receipts c ON c.commit_receipt_id=s.commit_receipt_id "
                "JOIN l4_commit_requests r ON r.commit_request_id=c.commit_request_id "
                "WHERE s.state_version_id=?",
                (state_version_id,),
            ).fetchone()
            if row is None:
                raise LifecycleTransitionError(f"unknown state_version_id={state_version_id}")
            if str(row["commit_receipt_id"]) != source_commit_receipt_id:
                raise LifecycleTransitionError("source commit receipt does not own the state version")
            current = str(row["lifecycle_stage"])
            if target_stage not in allowed.get(current, set()):
                raise LifecycleTransitionError(
                    f"invalid lifecycle transition {current}->{target_stage}"
                )
            event_id = "l4life:" + compute_deterministic_digest(
                {
                    "state_version_id": state_version_id,
                    "source_commit_receipt_id": source_commit_receipt_id,
                    "from_stage": current,
                    "to_stage": target_stage,
                    "reason": reason,
                }
            )
            request_payload = dict(_json_loads(str(row["request_json"])))
            commit_payload = dict(_json_loads(str(row["receipt_json"])))
            audit_record = self._append_audit_event_in_tx(
                conn,
                event_type="state_lifecycle_transition",
                state_surface=str(row["state_surface"]),
                operation_type=f"lifecycle_{target_stage}",
                tenant_id=str(row["tenant_id"]),
                policy_hash=str(request_payload.get("policy_hash") or "-"),
                blueprint_hash=str(request_payload.get("blueprint_hash") or "-"),
                snapshot_before=str(commit_payload.get("snapshot_after") or "-"),
                snapshot_after=str(commit_payload.get("snapshot_after") or "-"),
                request_id=str(request_payload.get("request_id") or "") or None,
                run_id=str(request_payload.get("run_id") or "") or None,
                trace_root=str(request_payload.get("trace_root") or "") or None,
                receipt_refs=(event_id, source_commit_receipt_id),
                state_refs=(state_version_id,),
                reason_codes=(reason,),
            )
            event = {
                "lifecycle_event_id": event_id,
                "state_version_id": state_version_id,
                "source_commit_receipt_id": source_commit_receipt_id,
                "from_stage": current,
                "to_stage": target_stage,
                "reason": reason,
                "audit_record_id": audit_record.audit_record_id,
            }
            conn.execute(
                "UPDATE l4_state_versions SET lifecycle_stage=? WHERE state_version_id=?",
                (target_stage, state_version_id),
            )
            conn.execute(
                "INSERT INTO l4_lifecycle_events "
                "(lifecycle_event_id, state_version_id, source_commit_receipt_id, "
                "from_stage, to_stage, reason, event_json, created_sequence) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    event_id,
                    state_version_id,
                    source_commit_receipt_id,
                    current,
                    target_stage,
                    reason,
                    _json_dumps(event),
                    audit_record.ledger_sequence,
                ),
            )
            return event_id

    def reconcile_commit(self, commit_receipt_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            commit = conn.execute(
                "SELECT * FROM l4_commit_receipts WHERE commit_receipt_id=?",
                (commit_receipt_id,),
            ).fetchone()
            if commit is None:
                return {
                    "consistent": False,
                    "reason_codes": ["missing_commit_receipt"],
                    "commit_receipt_id": commit_receipt_id,
                }
            audit = conn.execute(
                "SELECT * FROM l4_audit_ledger WHERE audit_record_id=?",
                (str(commit["audit_record_id"]),),
            ).fetchone()
            states = conn.execute(
                "SELECT logical_hash FROM l4_state_versions WHERE commit_receipt_id=?",
                (commit_receipt_id,),
            ).fetchall()
            projections = conn.execute(
                "SELECT status, payload_json, payload_digest FROM l4_projection_outbox "
                "WHERE commit_receipt_id=?",
                (commit_receipt_id,),
            ).fetchall()
        reasons: list[str] = []
        logical_hash = str(commit["logical_hash"])
        if audit is None:
            reasons.append("missing_audit_record")
        if not states:
            reasons.append("missing_state_versions")
        elif any(str(row["logical_hash"]) != logical_hash for row in states):
            reasons.append("state_commit_logical_hash_mismatch")
        for row in projections:
            payload = _json_loads(str(row["payload_json"]))
            expected = compute_deterministic_digest(
                {k: v for k, v in payload.items() if k != "projection_receipt"}
            )
            if expected != str(row["payload_digest"]):
                reasons.append("projection_payload_digest_mismatch")
            if str(row["status"]) != "COMPLETE":
                reasons.append(f"projection_not_complete::{row['status']}")
        return {
            "consistent": not reasons,
            "reason_codes": list(dict.fromkeys(reasons)),
            "commit_receipt_id": commit_receipt_id,
            "logical_hash": logical_hash,
            "state_version_count": len(states),
            "projection_count": len(projections),
        }


_DEFAULT_BACKEND: SQLiteL4Backend | None = None
_DEFAULT_BACKEND_LOCK = threading.Lock()


def get_default_backend() -> SQLiteL4Backend | None:
    if configured_l4_backend_name() == "memory":
        return None
    global _DEFAULT_BACKEND  # noqa: PLW0603
    with _DEFAULT_BACKEND_LOCK:
        if _DEFAULT_BACKEND is None:
            _DEFAULT_BACKEND = SQLiteL4Backend()
        return _DEFAULT_BACKEND


def reset_default_backend(*, delete_storage: bool = False) -> None:
    global _DEFAULT_BACKEND  # noqa: PLW0603
    with _DEFAULT_BACKEND_LOCK:
        path = (
            _DEFAULT_BACKEND.path
            if _DEFAULT_BACKEND is not None
            else default_l4_sqlite_path()
        )
        _DEFAULT_BACKEND = None
        if delete_storage:
            for candidate in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm")):
                try:
                    candidate.unlink()
                except FileNotFoundError:
                    pass


__all__ = [
    "AtomicCommitResult",
    "DurableLockContentionError",
    "L4StorageError",
    "LifecycleTransitionError",
    "ProjectionStateError",
    "ProjectionTask",
    "ReplayConflictError",
    "SQLiteL4Backend",
    "configured_l4_backend_name",
    "default_l4_sqlite_path",
    "get_default_backend",
    "logical_commit_hash",
    "reset_default_backend",
]
