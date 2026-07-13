"""Executable negative controls for transactional L4 durability."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from agentic_core.L4_state.audit.sqlite_audit_ledger import SQLiteAuditLedger
from agentic_core.L4_state.contracts.records import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
    stamp_digest,
)
from agentic_core.L4_state.storage.sqlite_backend import SQLiteL4Backend
from agentic_core.L4_state.uwg.durable_write_gateway import (
    compute_state_diffs_digest,
    get_default_gateway,
    reset_default_gateway,
)
from agentic_core.L4_state.uwg.transactional_durable_write_gateway import (
    TransactionalDurableWriteGateway,
)


def _packet(*, suffix: str = "a", replay_key: str = "replay:one"):
    rollback = stamp_digest(
        RollbackPlan(
            rollback_plan_id=f"rp:{suffix}",
            blast_radius="single_surface",
            target_surfaces=("l4.test.surface",),
            before_snapshot_refs=("before",),
            rollback_operation_types=("tombstone",),
        )
    )
    diff = stamp_digest(
        StateDiff(
            state_diff_id=f"sd:{suffix}",
            target_surface="l4.test.surface",
            operation_type="append_record",
            after_candidate=f"candidate:{suffix}",
            schema_ref="schema:test@1",
            blast_radius="single_surface",
            rollback_plan_ref=rollback.rollback_plan_id,
            proposed_by_surface="Exit",
            created_at="deterministic",
        )
    )
    staged_hash = compute_state_diffs_digest([diff])
    request = stamp_digest(
        CommitRequest(
            commit_request_id=f"cr:{suffix}",
            cleared_exit_review_packet_ref=f"clearance:{suffix}",
            request_id=f"request:{suffix}",
            run_id=f"run:{suffix}",
            trace_root=f"trace:{suffix}",
            tenant_id="tenant-a",
            policy_hash="policy:test-v1",
            blueprint_hash="blueprint:test-v1",
            route_contract_ref="route:test",
            replay_key=replay_key,
            rollback_plan_ref=rollback.rollback_plan_id,
            blast_radius="single_surface",
            state_diff_refs=(diff.state_diff_id,),
            gate_verdict_refs=("gate:pass",),
            l5_certification_ref="l5:test:certified",
            affected_state_surfaces=("l4.test.surface",),
            expected_read_surface_refreshes=("test_projection",),
            registry_digest_set=("registry:test-v1",),
            capability_token_ref="capability:test:write",
            clearance_proof_id=f"clearance:{suffix}",
            validator_receipt_id=f"validator:{suffix}",
            staged_diff_hash=staged_hash,
            commit_request_signature=f"signature:{suffix}",
        )
    )
    refresh = stamp_digest(
        ReadSurfaceRefreshPlan(
            refresh_plan_id=f"refresh:{suffix}",
            source_commit_receipt_ref="<pending>",
            before_snapshot="before",
            expected_after_snapshot="after",
            stale_projection_policy="fail_closed",
            retry_policy="outbox",
            policy_hash=request.policy_hash,
            blueprint_hash=request.blueprint_hash,
            affected_surfaces=("l4.test.surface",),
            required_refreshes=("test_projection",),
            refresh_order=("test_projection",),
        )
    )
    return request, [diff], rollback, refresh


def test_atomic_commit_persists_state_audit_receipt_and_outbox(tmp_path: Path) -> None:
    backend = SQLiteL4Backend(tmp_path / "l4.sqlite3")
    gateway = TransactionalDurableWriteGateway(canonical_backend=backend)
    request, diffs, rollback, refresh = _packet()
    gateway.stage_state_payload(
        commit_request_id=request.commit_request_id,
        state_diff_id=diffs[0].state_diff_id,
        payload={"value": 42},
    )
    receipt, blocked, pending = gateway.commit(
        commit_request=request,
        state_diffs=diffs,
        rollback_plan=rollback,
        refresh_plan=refresh,
    )
    assert blocked is None
    assert receipt is not None
    assert receipt.content_hash and receipt.chain_hash
    assert pending and pending[0].status == "PENDING"
    versions = backend.get_state_versions(receipt.commit_receipt_id)
    assert versions[0]["payload"]["canonical_state"] == {"value": 42}
    tasks = backend.list_projection_tasks(
        commit_receipt_id=receipt.commit_receipt_id,
        statuses=("PENDING",),
    )
    assert len(tasks) == 1
    assert backend.reconcile_commit(receipt.commit_receipt_id)["consistent"] is False
    task = backend.claim_projection(tasks[0].projection_id)
    backend.complete_projection(
        task.projection_id,
        observed_payload_digest=task.payload_digest,
        receipt_payload={"read_after_write": "PASS"},
    )
    assert backend.reconcile_commit(receipt.commit_receipt_id)["consistent"] is True
    assert [row["event_type"] for row in backend.load_audit_records()] == [
        "commit_request_received",
        "atomic_commit_applied",
        "read_surface_refresh_completed",
    ]


def test_restart_reloads_hash_chain_and_reuses_idempotent_receipt(tmp_path: Path) -> None:
    path = tmp_path / "l4.sqlite3"
    backend = SQLiteL4Backend(path)
    gateway = TransactionalDurableWriteGateway(canonical_backend=backend)
    packet = _packet()
    first, blocked, _ = gateway.commit(
        commit_request=packet[0],
        state_diffs=packet[1],
        rollback_plan=packet[2],
        refresh_plan=packet[3],
    )
    assert first is not None and blocked is None
    restarted_backend = SQLiteL4Backend(path)
    restarted_ledger = SQLiteAuditLedger(restarted_backend)
    restarted_ledger.sequence_check()
    restarted_ledger.chain_check()
    restarted_gateway = TransactionalDurableWriteGateway(
        canonical_backend=restarted_backend
    )
    second, blocked, _ = restarted_gateway.commit(
        commit_request=packet[0],
        state_diffs=packet[1],
        rollback_plan=packet[2],
        refresh_plan=packet[3],
    )
    assert blocked is None and second is not None
    assert second.commit_receipt_id == first.commit_receipt_id
    assert second.content_hash == first.content_hash
    restored_validation = restarted_gateway.get_validation_receipt(
        second.uwg_validation_receipt_ref
    )
    assert restored_validation is not None
    assert restored_validation.validation_status == "PASS"
    events = [row["event_type"] for row in restarted_backend.load_audit_records()]
    assert events.count("atomic_commit_applied") == 1
    assert events.count("commit_request_received") == 2


def test_same_replay_key_with_different_state_fails_closed(tmp_path: Path) -> None:
    backend = SQLiteL4Backend(tmp_path / "l4.sqlite3")
    gateway = TransactionalDurableWriteGateway(canonical_backend=backend)
    first = _packet(suffix="a", replay_key="replay:conflict")
    receipt, blocked, _ = gateway.commit(
        commit_request=first[0],
        state_diffs=first[1],
        rollback_plan=first[2],
        refresh_plan=first[3],
    )
    assert receipt is not None and blocked is None
    second = _packet(suffix="b", replay_key="replay:conflict")
    receipt, blocked, _ = gateway.commit(
        commit_request=second[0],
        state_diffs=second[1],
        rollback_plan=second[2],
        refresh_plan=second[3],
    )
    assert receipt is None and blocked is not None
    assert "replay_key_conflict" in blocked.blocked_reason_codes


def test_same_replay_key_with_different_run_identity_fails_closed(
    tmp_path: Path,
) -> None:
    backend = SQLiteL4Backend(tmp_path / "l4.sqlite3")
    gateway = TransactionalDurableWriteGateway(canonical_backend=backend)
    first = _packet(suffix="a", replay_key="replay:identity-conflict")
    receipt, blocked, _ = gateway.commit(
        commit_request=first[0],
        state_diffs=first[1],
        rollback_plan=first[2],
        refresh_plan=first[3],
    )
    assert receipt is not None and blocked is None

    conflicting_request = stamp_digest(
        replace(
            first[0],
            request_id="request:other",
            run_id="run:other",
            trace_root="trace:other",
            deterministic_digest="",
        )
    )
    receipt, blocked, _ = gateway.commit(
        commit_request=conflicting_request,
        state_diffs=first[1],
        rollback_plan=first[2],
        refresh_plan=first[3],
    )
    assert receipt is None and blocked is not None
    assert "replay_key_conflict" in blocked.blocked_reason_codes


def test_lifecycle_transition_is_additive_and_uwg_authorized(tmp_path: Path) -> None:
    backend = SQLiteL4Backend(tmp_path / "l4.sqlite3")
    gateway = TransactionalDurableWriteGateway(canonical_backend=backend)
    packet = _packet()
    receipt, blocked, _ = gateway.commit(
        commit_request=packet[0],
        state_diffs=packet[1],
        rollback_plan=packet[2],
        refresh_plan=packet[3],
    )
    assert receipt is not None and blocked is None
    state = backend.get_state_versions(receipt.commit_receipt_id)[0]
    event_id = gateway.transition_state_lifecycle(
        state_version_id=state["state_version_id"],
        source_commit_receipt_id=receipt.commit_receipt_id,
        target_stage="archived",
        reason="retention policy",
    )
    assert event_id.startswith("l4life:")
    assert backend.get_state_versions(receipt.commit_receipt_id)[0][
        "lifecycle_stage"
    ] == "archived"


def test_runtime_default_audit_backend_survives_restart(
    tmp_path: Path, monkeypatch
) -> None:
    from agentic_core.L4_state.audit.audit_ledger import (
        get_default_ledger,
        reset_default_ledger,
    )
    from agentic_core.L4_state.storage.sqlite_backend import reset_default_backend

    monkeypatch.setenv("L4_STORAGE_BACKEND", "sqlite")
    monkeypatch.setenv("L4_SQLITE_PATH", str(tmp_path / "default.sqlite3"))
    reset_default_ledger()
    reset_default_backend(delete_storage=True)
    ledger = get_default_ledger()
    assert isinstance(ledger, SQLiteAuditLedger)
    ledger.append(
        event_type="runtime_default_probe",
        state_surface="l4.test.surface",
        operation_type="probe",
        tenant_id="tenant-a",
        policy_hash="policy:test-v1",
        blueprint_hash="blueprint:test-v1",
        snapshot_before="before",
        actor_surface="UWG",
        mutation_source="UWG",
    )
    reset_default_ledger()
    reset_default_backend()
    restarted = get_default_ledger()
    assert isinstance(restarted, SQLiteAuditLedger)
    assert restarted.position() == 1
    restarted.chain_check()


def test_runtime_default_gateway_uses_transactional_sqlite(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from agentic_core.L4_state.storage.sqlite_backend import reset_default_backend

    monkeypatch.setenv("L4_STORAGE_BACKEND", "sqlite")
    monkeypatch.setenv("L4_SQLITE_PATH", str(tmp_path / "default-gateway.sqlite3"))
    reset_default_gateway()
    reset_default_backend(delete_storage=True)
    try:
        gateway = get_default_gateway()
        assert isinstance(gateway, TransactionalDurableWriteGateway)
        packet = _packet(replay_key="replay:default-runtime")
        first, blocked, _ = gateway.commit(
            commit_request=packet[0],
            state_diffs=packet[1],
            rollback_plan=packet[2],
            refresh_plan=packet[3],
        )
        assert first is not None and blocked is None

        reset_default_gateway()
        reset_default_backend()
        replayed, blocked, _ = get_default_gateway().commit(
            commit_request=packet[0],
            state_diffs=packet[1],
            rollback_plan=packet[2],
            refresh_plan=packet[3],
        )
        assert replayed is not None and blocked is None
        assert replayed.commit_receipt_id == first.commit_receipt_id
    finally:
        reset_default_gateway()
        reset_default_backend(delete_storage=True)


def test_injected_commit_failure_rolls_back_all_canonical_rows(
    tmp_path: Path, monkeypatch
) -> None:
    backend = SQLiteL4Backend(tmp_path / "l4.sqlite3")
    gateway = TransactionalDurableWriteGateway(canonical_backend=backend)
    request, diffs, rollback, refresh = _packet()
    gateway.stage_state_payload(
        commit_request_id=request.commit_request_id,
        state_diff_id=diffs[0].state_diff_id,
        payload={"value": "must-not-persist"},
    )
    original = backend._append_audit_event_in_tx

    def fail_atomic_commit(conn, **kwargs):
        if kwargs.get("event_type") == "atomic_commit_applied":
            raise RuntimeError("injected failure")
        return original(conn, **kwargs)

    monkeypatch.setattr(backend, "_append_audit_event_in_tx", fail_atomic_commit)
    with pytest.raises(RuntimeError, match="injected failure"):
        gateway.commit(
            commit_request=request,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
    with backend._connect() as conn:
        assert conn.execute("SELECT count(*) FROM l4_state_versions").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM l4_commit_receipts").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM l4_projection_outbox").fetchone()[0] == 0
    assert [row["event_type"] for row in backend.load_audit_records()] == [
        "commit_request_received"
    ]


def test_projection_failure_preserves_state_and_is_retryable(tmp_path: Path) -> None:
    backend = SQLiteL4Backend(tmp_path / "l4.sqlite3")
    gateway = TransactionalDurableWriteGateway(canonical_backend=backend)
    request, diffs, rollback, refresh = _packet()
    receipt, blocked, _pending = gateway.commit(
        commit_request=request,
        state_diffs=diffs,
        rollback_plan=rollback,
        refresh_plan=refresh,
    )
    assert receipt is not None and blocked is None
    task = backend.list_projection_tasks(
        commit_receipt_id=receipt.commit_receipt_id,
        statuses=("PENDING",),
    )[0]
    backend.claim_projection(task.projection_id)
    gateway.fail_projection(task.projection_id, error="chroma unavailable")
    assert backend.get_state_versions(receipt.commit_receipt_id)
    failed = backend.list_projection_tasks(
        commit_receipt_id=receipt.commit_receipt_id,
        statuses=("FAILED",),
    )
    assert failed and failed[0].last_error == "chroma unavailable"
    assert backend.reconcile_commit(receipt.commit_receipt_id)["consistent"] is False
    retried = backend.claim_projection(task.projection_id)
    assert retried.attempt_count == 2
