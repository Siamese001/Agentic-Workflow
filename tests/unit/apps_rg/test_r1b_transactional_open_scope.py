"""R1B canonical transaction and recoverable projection contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import apps_rg.cache.r1b_chroma_read_surface_projection as chroma_projection
from agentic_core.L4_state.storage.sqlite_backend import SQLiteL4Backend
from apps_rg.cache.r1b_strict_gateway import R1BStrictUWGGateway
from apps_rg.cache.r1b_transactional_promotion import promote_r1b_transactionally
from apps_rg.cache.r1b_uwg_promotion import build_r1b_promotion_candidate
from tests.unit.apps_rg.r1b_fixture_builders import (
    build_admissible_intent_record,
    build_admissible_output_chunks,
    build_post_exit_eligibility,
    r1b_match_request,
    write_post_exit_artifacts,
)


@dataclass
class _FakeChromaOutcome:
    refresh_status: str = "COMPLETE"
    read_surface_refresh_status: str = "COMPLETE"
    chroma_projection_status: str = "COMPLETE"
    read_surface_refresh_complete: bool = True
    chroma_projection_complete: bool = True
    reason: str = ""
    artifacts_written: list[str] | None = None

    def to_dict(self):
        return {
            "refresh_status": self.refresh_status,
            "read_surface_refresh_status": self.read_surface_refresh_status,
            "chroma_projection_status": self.chroma_projection_status,
            "read_surface_refresh_complete": self.read_surface_refresh_complete,
            "chroma_projection_complete": self.chroma_projection_complete,
            "reason": self.reason,
            "artifacts_written": list(self.artifacts_written or []),
        }


def _fake_chroma(**kwargs):
    artifact_dir = Path(kwargs["artifact_dir"])
    record = kwargs["record"]
    (artifact_dir / "chroma_collection_index_ref.json").write_text(
        json.dumps({"payload": {"record_id": record.record_id}}),
        encoding="utf-8",
    )
    (artifact_dir / "chroma_read_after_write_receipt.json").write_text(
        json.dumps({"payload": {"read_after_write_status": "PASS"}}),
        encoding="utf-8",
    )
    return _FakeChromaOutcome()


def _candidate(run_dir: Path):
    record = build_admissible_intent_record(
        record_id="hir_transactional",
        source_run_id="run_transactional",
    )
    chunks = build_admissible_output_chunks(record.record_id)
    write_post_exit_artifacts(run_dir, record)
    return build_r1b_promotion_candidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=build_post_exit_eligibility(record, chunks),
        run_dir=run_dir,
    )


def test_r1b_commit_state_audit_and_outbox_share_canonical_transaction(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        chroma_projection,
        "project_governed_chroma_read_surface",
        _fake_chroma,
    )
    run_dir = tmp_path / "run"
    projection_root = tmp_path / "projection"
    backend = SQLiteL4Backend(tmp_path / "l4.sqlite3")
    gateway = R1BStrictUWGGateway(canonical_backend=backend)
    candidate = _candidate(run_dir)
    result = promote_r1b_transactionally(
        candidate=candidate,
        projection_root=projection_root,
        artifact_dir=run_dir,
        section_id="integrated_whole_run",
        run_id=candidate.source_run_id,
        raw_request=r1b_match_request(),
        gateway=gateway,
    )
    assert result.complete is True
    receipt_id = result.promotion.uwg_commit_receipt_id
    state = backend.get_state_versions(receipt_id)
    assert state[0]["payload"]["canonical_state"]["record"]["record_id"] == (
        candidate.record.record_id
    )
    tasks = backend.list_projection_tasks(
        commit_receipt_id=receipt_id,
        statuses=("COMPLETE",),
    )
    assert len(tasks) == 1
    assert backend.reconcile_commit(receipt_id)["consistent"] is True
    bundle = json.loads(
        (
            projection_root
            / "durable"
            / "uwg_admitted"
            / "intents"
            / f"{candidate.record.record_id}.json"
        ).read_text(encoding="utf-8")
    )
    assert bundle["source_commit_receipt_ref"] == receipt_id
    assert bundle["read_surface_role"] == "projection_not_truth"
    assert bundle["outbox_payload_digest"]


def test_r1b_replay_is_idempotent_and_does_not_duplicate_audit(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        chroma_projection,
        "project_governed_chroma_read_surface",
        _fake_chroma,
    )
    run_dir = tmp_path / "run"
    projection_root = tmp_path / "projection"
    backend = SQLiteL4Backend(tmp_path / "l4.sqlite3")
    gateway = R1BStrictUWGGateway(canonical_backend=backend)
    candidate = _candidate(run_dir)
    first = promote_r1b_transactionally(
        candidate=candidate,
        projection_root=projection_root,
        artifact_dir=run_dir,
        raw_request=r1b_match_request(),
        gateway=gateway,
    )
    second = promote_r1b_transactionally(
        candidate=candidate,
        projection_root=projection_root,
        artifact_dir=run_dir,
        raw_request=r1b_match_request(),
        gateway=gateway,
    )
    assert first.promotion.uwg_commit_receipt_id == second.promotion.uwg_commit_receipt_id
    events = [row["event_type"] for row in backend.load_audit_records()]
    assert events.count("atomic_commit_applied") == 1
    assert events.count("read_surface_refresh_completed") == 1
    assert events.count("commit_request_received") == 2
    assert second.projection is not None
    assert second.projection.reason == "idempotent_projection_replay"
