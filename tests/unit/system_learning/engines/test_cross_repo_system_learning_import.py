from __future__ import annotations

import json
from pathlib import Path

import pytest
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, emit_determinism_digest

from system_learning.engines.cross_repo_system_learning_import import (
    EmbeddingImportRecord,
    _validate_embedding_dimensions,
    discover_artifacts,
    load_cross_repo_learning_context,
    run_import,
    write_run_artifacts,
)


pytestmark = pytest.mark.unit
emit_determinism_digest("p0", "test_cross_repo_system_learning_import")
_emit_records_execution_trace("p0", "evidence", "test_cross_repo_system_learning_import")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _seed_tree(root: Path) -> None:
    _write_text(root / "RepoA" / "rca" / "report_20260316.json", '{"id":"r1","type":"rca"}')
    _write_text(root / "RepoA" / "telemetry" / "events.jsonl", '{"event_type":"x","payload":{}}\n')
    _write_text(root / "RepoB" / "patterns" / "failure_pattern.md", "pattern-memory")
    _write_text(root / "RepoB" / "schemas" / "manifest_schema.json", '{"schema":"v1"}')
    _write_text(root / "RepoB" / "dupe" / "copy_a.txt", "DUPLICATE")
    _write_text(root / "RepoB" / "dupe" / "copy_b.txt", "DUPLICATE")
    _write_text(root / "RepoB" / "mystery" / "unknown.snapshot", "???")


def test_deterministic_directory_discovery_ordering(tmp_path: Path) -> None:
    git_root = tmp_path / "Git"
    _seed_tree(git_root)

    discovered = discover_artifacts(git_root)
    paths = [x.absolute_path for x in discovered]
    assert paths == sorted(paths)


def test_classifier_stability(tmp_path: Path) -> None:
    git_root = tmp_path / "Git"
    _seed_tree(git_root)

    first = run_import(git_root)
    second = run_import(git_root)
    assert first.digests.discovery_manifest_digest == second.digests.discovery_manifest_digest
    assert first.digests.accepted_manifest_digest == second.digests.accepted_manifest_digest


def test_dedupe_by_content_hash_marks_duplicate_ignore(tmp_path: Path) -> None:
    git_root = tmp_path / "Git"
    _seed_tree(git_root)

    discovered = discover_artifacts(git_root)
    dupe_rows = [x for x in discovered if "copy_" in x.absolute_path]
    assert len(dupe_rows) == 2
    assert {x.disposition for x in dupe_rows} == {"ignore", "inspect-manually"} or {x.disposition for x in dupe_rows} == {
        "ignore",
        "ingest-as-C0",
    }


def test_unsafe_artifact_rejection(tmp_path: Path) -> None:
    git_root = tmp_path / "Git"
    _seed_tree(git_root)

    result = run_import(git_root)
    unsafe = [x for x in result.unresolved_unsafe_artifacts if "unknown.snapshot" in x.absolute_path]
    assert unsafe
    assert unsafe[0].disposition == "inspect-manually"


def test_provenance_persistence_fields_exist(tmp_path: Path) -> None:
    git_root = tmp_path / "Git"
    _seed_tree(git_root)

    result = run_import(git_root)
    assert result.accepted
    first = result.accepted[0]
    assert first.source_path
    assert first.source_repo
    assert first.provenance_tag.startswith("cross_repo_import::")
    assert first.schema_version == "v1"


def test_schema_validation_failure_on_missing_manifest_field(tmp_path: Path) -> None:
    repo_root = tmp_path / "Agentic-Workflow"
    base = repo_root / "artifacts" / "system_learning" / "cross_repo_import"
    base.mkdir(parents=True, exist_ok=True)

    (base / "latest_context.json").write_text(
        json.dumps({"schema_version": "v1", "proposal_only": True}),
        encoding="utf-8",
    )
    (base / "accepted_manifest.json").write_text(
        json.dumps([
            {
                "source_path": "C:/Git/Repo/a.json",
                "source_repo": "Repo",
                "schema_version": "v1",
                "ingestion_timestamp": 0,
                "provenance_tag": "x",
                "disposition": "ingest-as-C0",
                "bucket": "RCA_SOURCE",
                "artifact_kind": "rca_artifact",
            }
        ]),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="missing fields"):
        load_cross_repo_learning_context(repo_root)


def test_vector_dimension_validation_fails_on_mismatch() -> None:
    records = [
        EmbeddingImportRecord(
            artifact_kind="a",
            source_repo="r",
            source_path="p1",
            content_hash="h1",
            created_from_import=True,
            namespace="ns",
            target_dimension=384,
            text="x",
        ),
        EmbeddingImportRecord(
            artifact_kind="b",
            source_repo="r",
            source_path="p2",
            content_hash="h2",
            created_from_import=True,
            namespace="ns",
            target_dimension=768,
            text="y",
        ),
    ]

    with pytest.raises(RuntimeError, match="vector dimension mismatch"):
        _validate_embedding_dimensions(records)


def test_proposal_only_enforcement(tmp_path: Path) -> None:
    repo_root = tmp_path / "Agentic-Workflow"
    base = repo_root / "artifacts" / "system_learning" / "cross_repo_import"
    base.mkdir(parents=True, exist_ok=True)

    (base / "latest_context.json").write_text(
        json.dumps({"schema_version": "v1", "proposal_only": False}),
        encoding="utf-8",
    )
    (base / "accepted_manifest.json").write_text("[]", encoding="utf-8")

    with pytest.raises(RuntimeError, match="proposal_only"):
        load_cross_repo_learning_context(repo_root)


def test_no_routing_or_safety_mutation_authority_in_context(tmp_path: Path) -> None:
    git_root = tmp_path / "Git"
    repo_root = tmp_path / "Agentic-Workflow"
    _seed_tree(git_root)

    result = run_import(git_root)
    write_run_artifacts(repo_root, result)

    context = load_cross_repo_learning_context(repo_root)
    assert context["proposal_only"] is True
    for forbidden in [
        "routing_rules",
        "safety_thresholds",
        "execution_tiers",
        "prompt_authority_slots",
        "live_policy",
    ]:
        assert forbidden in context["forbidden_mutation_surfaces_blocked"]


def test_replay_stability_across_two_runs(tmp_path: Path) -> None:
    git_root = tmp_path / "Git"
    _seed_tree(git_root)

    one = run_import(git_root)
    two = run_import(git_root)

    assert one.digests.discovery_manifest_digest == two.digests.discovery_manifest_digest
    assert one.digests.accepted_manifest_digest == two.digests.accepted_manifest_digest
    assert one.digests.normalized_content_digest_set == two.digests.normalized_content_digest_set
    assert one.digests.embedding_import_digest == two.digests.embedding_import_digest
    assert one.digests.system_learning_incorporation_digest == two.digests.system_learning_incorporation_digest


def test_failure_on_malformed_utf8_for_accepted_artifact(tmp_path: Path) -> None:
    git_root = tmp_path / "Git"
    _write_bytes(git_root / "RepoA" / "telemetry" / "events.jsonl", b"\xff\xfe\xfd")

    with pytest.raises(RuntimeError, match="UTF-8 decode failed"):
        run_import(git_root)


def test_failure_on_duplicate_conflicting_manifests(tmp_path: Path) -> None:
    repo_root = tmp_path / "Agentic-Workflow"
    base = repo_root / "artifacts" / "system_learning" / "cross_repo_import"
    base.mkdir(parents=True, exist_ok=True)

    (base / "latest_context.json").write_text(
        json.dumps({"schema_version": "v1", "proposal_only": True}),
        encoding="utf-8",
    )
    (base / "accepted_manifest.json").write_text(
        json.dumps(
            [
                {
                    "source_path": "C:/Git/Repo/a.json",
                    "source_repo": "Repo",
                    "content_hash": "aaa",
                    "schema_version": "v1",
                    "ingestion_timestamp": 0,
                    "provenance_tag": "p",
                    "disposition": "ingest-as-C0",
                    "bucket": "RCA_SOURCE",
                    "artifact_kind": "rca_artifact",
                },
                {
                    "source_path": "C:/Git/Repo/a.json",
                    "source_repo": "Repo",
                    "content_hash": "bbb",
                    "schema_version": "v1",
                    "ingestion_timestamp": 0,
                    "provenance_tag": "p",
                    "disposition": "ingest-as-C0",
                    "bucket": "RCA_SOURCE",
                    "artifact_kind": "rca_artifact",
                },
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="duplicate conflicting manifests"):
        load_cross_repo_learning_context(repo_root)
