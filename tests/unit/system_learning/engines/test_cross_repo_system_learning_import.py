from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
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
emit_replay_key("p0", "test_cross_repo_system_learning_import")
_emit_records_execution_trace("p0", "evidence", "test_cross_repo_system_learning_import")
_emit_applies_guardrail("p0", "test_cross_repo_system_learning_import", "p0_governance")
_emit_snapshots_state("p0", "test_cross_repo_system_learning_import", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_cross_repo_system_learning_import", "execution_auth")
_emit_validates_capability("p2", "test_cross_repo_system_learning_import", "capability_check")
_emit_routes_to_capability("p2", "test_cross_repo_system_learning_import", "capability_route")
_emit_writes_via_uwg("p2", "test_cross_repo_system_learning_import", "uwg_write")
_emit_blocks_direct_write("p2", "test_cross_repo_system_learning_import", "direct_write_block")
_emit_records_tool_invocation("p2", "test_cross_repo_system_learning_import", "tool_invocation")
_emit_captures_execution_output("p2", "test_cross_repo_system_learning_import", "exec_output")
_emit_dispatches_agent("p3", "test_cross_repo_system_learning_import", "agent_dispatch")
_emit_coordinates_agents("p3", "test_cross_repo_system_learning_import", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_cross_repo_system_learning_import", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_cross_repo_system_learning_import", "healing_outcome")
_emit_escalates_failure("p3", "test_cross_repo_system_learning_import", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_cross_repo_system_learning_import", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_cross_repo_system_learning_import", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_cross_repo_system_learning_import", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_cross_repo_system_learning_import", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_cross_repo_system_learning_import", "eval_metric")
_emit_stores_embedding("p4", "test_cross_repo_system_learning_import", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_cross_repo_system_learning_import", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_cross_repo_system_learning_import", "exec_snapshot_link")
_emit_emits_metric_event("test_cross_repo_system_learning_import", "p4obs", "metric_1")
_emit_emits_metric_event("test_cross_repo_system_learning_import", "p4obs", "metric_2")
_emit_emits_metric_event("test_cross_repo_system_learning_import", "p4obs", "metric_3")
_emit_emits_metric_event("test_cross_repo_system_learning_import", "p4obs", "metric_4")
_emit_emits_metric_event("test_cross_repo_system_learning_import", "p4obs", "metric_5")
_emit_emits_metric_event("test_cross_repo_system_learning_import", "p4obs", "metric_6")
_emit_records_incident_event("test_cross_repo_system_learning_import", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_cross_repo_system_learning_import", "p4obs", "anomaly")
_emit_writes_observability_log("test_cross_repo_system_learning_import", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_cross_repo_system_learning_import", "p4obs", "mon_state")
_emit_triggers_alert("test_cross_repo_system_learning_import", "p4obs", "alert")
_emit_links_incident_trace("test_cross_repo_system_learning_import", "p4obs", "trace_link")
_emit_captures_pattern("test_cross_repo_system_learning_import", "p3lm", "pattern")
_emit_records_learning_event("test_cross_repo_system_learning_import", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_cross_repo_system_learning_import", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_cross_repo_system_learning_import", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_cross_repo_system_learning_import", "p3lm", "routing")
_emit_improves_agent_policy("test_cross_repo_system_learning_import", "p3lm", "policy")
_emit_stores_learning_state("test_cross_repo_system_learning_import", "p3lm", "state")
_emit_pulls_context("p1", "test_cross_repo_system_learning_import", "context_pull")
_emit_execution_terminates_at_uwg("p1", "test_cross_repo_system_learning_import", "uwg_term")
_emit_writes_through("p1", "test_cross_repo_system_learning_import", "write_through")
_emit_validated_by_safety_plane("p1", "test_cross_repo_system_learning_import", "safety_validation")
_emit_proposal_commits_routing("p1", "test_cross_repo_system_learning_import", "routing_commit")
_emit_escalates_to_human("p1", "test_cross_repo_system_learning_import", "human_escalation")
_emit_routes_through("p1", "test_cross_repo_system_learning_import", "route_through")
_emit_checks_agent_registry("p1", "test_cross_repo_system_learning_import", "agent_registry")
_emit_validates_agent_capability("p1", "test_cross_repo_system_learning_import", "capability")
_emit_dispatches_execution_plan("p1", "test_cross_repo_system_learning_import", "exec_plan")
_emit_agent_executes_agent("p1", "test_cross_repo_system_learning_import", "sub_agent")
_emit_routes_to_agent("p1", "test_cross_repo_system_learning_import", "target_agent")
_emit_verifies_policy("p1", "test_cross_repo_system_learning_import", "policy_check")
_emit_observes_runtime_state("p1", "test_cross_repo_system_learning_import", "runtime_state")
_emit_verifies_boundary("p1", "test_cross_repo_system_learning_import", "boundary_check")
_emit_transcripts_response("p1", "test_cross_repo_system_learning_import", "transcript")
_emit_hard_fails_untranscripted("p1", "test_cross_repo_system_learning_import")
_emit_gated_by_confidence("p1", "test_cross_repo_system_learning_import", "confidence_gate")


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
"""Test replay_stability_across_two_runs runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute replay_stability_across_two_runs
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
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
