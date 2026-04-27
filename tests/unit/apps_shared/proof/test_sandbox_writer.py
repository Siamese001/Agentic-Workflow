"""Tests for apps_shared.proof.sandbox_writer."""

from __future__ import annotations

import json
from pathlib import Path

from apps_shared.proof.proof_contracts import (
    CLASSIFICATION_SANDBOX_OUTPUT,
    CLASSIFICATION_UWG_DURABLE,
)
from apps_shared.proof.sandbox_writer import (
    CommitRequest,
    request_uwg_commit,
    write_sandbox_artifact,
)


def test_write_sandbox_artifact_creates_file_and_classifies(tmp_path: Path):
    rec = write_sandbox_artifact(
        app_id="apps_test",
        run_id="rn",
        trace_id="tr",
        producing_span_id="sp",
        export_root=tmp_path,
        artifact_id="draft_v1",
        payload={"k": "v"},
    )
    assert rec.classification == CLASSIFICATION_SANDBOX_OUTPUT
    assert rec.durable is False
    assert (tmp_path / "sandbox" / "apps_test" / "draft_v1.json").exists()
    # content_hash is 64 hex chars
    assert len(rec.content_hash) == 64


def test_write_sandbox_artifact_path_is_relative_to_export_root(tmp_path: Path):
    rec = write_sandbox_artifact(
        app_id="apps_test",
        run_id="rn",
        trace_id="tr",
        producing_span_id="sp",
        export_root=tmp_path,
        artifact_id="x",
        payload={"a": 1},
    )
    # No backslashes in stored path (cross-platform)
    assert "\\" not in rec.path
    assert rec.path.startswith("sandbox/apps_test/")


def test_request_uwg_commit_writes_artifact_and_request(tmp_path: Path):
    rec, commit = request_uwg_commit(
        app_id="apps_test",
        run_id="rn",
        trace_id="tr",
        producing_span_id="sp",
        export_root=tmp_path,
        artifact_id="commit_v1",
        payload={"decision": "approve"},
        intent="record_decision",
    )
    assert rec.classification == CLASSIFICATION_UWG_DURABLE
    assert rec.durable is True
    assert isinstance(commit, CommitRequest)
    assert commit.write_authority == "PENDING_UWG_APPROVAL"
    # Both files exist
    artifact_path = tmp_path / "uwg_pending" / "apps_test" / "commit_v1.json"
    request_path = tmp_path / "uwg_pending" / "apps_test" / "commit_v1.commit_request.json"
    assert artifact_path.exists()
    assert request_path.exists()


def test_request_uwg_commit_request_envelope_has_intent(tmp_path: Path):
    _, commit = request_uwg_commit(
        app_id="apps_test",
        run_id="rn",
        trace_id="tr",
        producing_span_id="sp",
        export_root=tmp_path,
        artifact_id="x",
        payload={},
        intent="record_high_impact_decision",
    )
    request_path = tmp_path / "uwg_pending" / "apps_test" / "x.commit_request.json"
    data = json.loads(request_path.read_text(encoding="utf-8"))
    assert data["intent"] == "record_high_impact_decision"
    assert data["write_authority"] == "PENDING_UWG_APPROVAL"


def test_commit_request_to_dict_serializable():
    cr = CommitRequest(
        app_id="a",
        run_id="r",
        artifact_path="p",
        content_hash="h" * 64,
        write_authority="PENDING_UWG_APPROVAL",
        intent="x",
    )
    d = cr.to_dict()
    assert d["app_id"] == "a" and d["intent"] == "x"


def test_sandbox_artifact_content_hash_matches_recompute(tmp_path: Path):
    rec = write_sandbox_artifact(
        app_id="apps_test",
        run_id="rn",
        trace_id="tr",
        producing_span_id="sp",
        export_root=tmp_path,
        artifact_id="hashcheck",
        payload={"a": "b"},
    )
    # The file content hash on disk must equal the record's content_hash
    from apps_shared.proof.proof_contracts import sha256_of_file

    file_path = tmp_path / rec.path
    assert sha256_of_file(file_path) == rec.content_hash


def test_two_writes_with_same_payload_produce_same_hash(tmp_path: Path):
    rec1 = write_sandbox_artifact(
        app_id="apps_test",
        run_id="rn1",
        trace_id="tr",
        producing_span_id="sp",
        export_root=tmp_path / "a",
        artifact_id="x",
        payload={"a": 1},
    )
    rec2 = write_sandbox_artifact(
        app_id="apps_test",
        run_id="rn2",
        trace_id="tr",
        producing_span_id="sp",
        export_root=tmp_path / "b",
        artifact_id="x",
        payload={"a": 1},
    )
    assert rec1.content_hash == rec2.content_hash
