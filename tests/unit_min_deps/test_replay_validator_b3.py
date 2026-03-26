"""Tests for ReplayValidator (Plan B Phase 3).

Comprehensive test suite covering seed pack validation, embedding artifact validation,
and determinism stability enforcement.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_authorize_and_execute("p2", "test_replay_validator_b3", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_replay_validator_b3", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_replay_validator_b3", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_replay_validator_b3", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_replay_validator_b3", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_replay_validator_b3", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_replay_validator_b3", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_replay_validator_b3", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_replay_validator_b3", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_replay_validator_b3", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_replay_validator_b3", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_replay_validator_b3", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_replay_validator_b3", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_replay_validator_b3", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_replay_validator_b3", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_replay_validator_b3", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_replay_validator_b3", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_replay_validator_b3", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_replay_validator_b3", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_replay_validator_b3", "exec_snapshot_link")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
#  # MOVED: from system_learning.engines.replay_validator import DeterminismViolationError, ReplayValidator
#  # MOVED: from system_learning.engines.seed_embedding_pack_builder import (
    DeterministicHashEmbedder,
    build_seed_embedding_pack,
)
#  # MOVED: from system_learning.types.embedding_artifact import EmbeddingArtifact
#  # MOVED: from system_learning.types.seed_embedding_pack_types import SeedEmbeddingPackConfig

# REMOVED: _emit_emits_metric_event("test_replay_validator_b3", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_replay_validator_b3", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_replay_validator_b3", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_replay_validator_b3", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_replay_validator_b3", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_replay_validator_b3", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_replay_validator_b3", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_replay_validator_b3", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_replay_validator_b3", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_replay_validator_b3", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_replay_validator_b3", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_replay_validator_b3", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_replay_validator_b3", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_replay_validator_b3", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_replay_validator_b3", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_replay_validator_b3", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_replay_validator_b3", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_replay_validator_b3", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_replay_validator_b3", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_replay_validator_b3", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_replay_validator_b3", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_replay_validator_b3", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_replay_validator_b3", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_replay_validator_b3", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_replay_validator_b3", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_replay_validator_b3", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_replay_validator_b3", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_replay_validator_b3", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_replay_validator_b3")
# REMOVED: _emit_applies_guardrail("p0", "test_replay_validator_b3", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_replay_validator_b3", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_replay_validator_b3", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_replay_validator_b3", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_replay_validator_b3", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_replay_validator_b3", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_replay_validator_b3", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_replay_validator_b3", "write_through")
# REMOVED: _emit_writes_through("p1", "test_replay_validator_b3", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_replay_validator_b3", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_replay_validator_b3", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_replay_validator_b3", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_replay_validator_b3", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_replay_validator_b3", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_replay_validator_b3", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_replay_validator_b3", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_replay_validator_b3", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_replay_validator_b3", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_replay_validator_b3", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_replay_validator_b3", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_replay_validator_b3", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_replay_validator_b3", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_replay_validator_b3", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_replay_validator_b3")
# REMOVED: _emit_gated_by_confidence("p1", "test_replay_validator_b3", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_replay_validator_b3")
# REMOVED: emit_determinism_digest("p0", "test_replay_validator_b3")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestReplayValidatorSeedPack:
    """Test seed pack validation functionality."""

    def test_validate_seed_pack_success(self):
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        from system_learning.engines.replay_validator import DeterminismViolationError, ReplayValidator
        from system_learning.engines.seed_embedding_pack_builder import (
        from system_learning.types.embedding_artifact import EmbeddingArtifact
        from system_learning.types.seed_embedding_pack_types import SeedEmbeddingPackConfig
    """Test validate_seed_pack_success contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
                {
                    "content_hash": "h2" * 32,
                    "trace_id": "t2",
                    "namespace": "test_ns",
                    "created_utc": 1234567891,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Should validate successfully
            validator.validate_seed_pack(
                base_path=str(base_path),
                namespace="test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
            )
        finally:
            shutil.rmtree(base_path)

    def test_validate_seed_pack_missing_files(self):
    """Test validate_seed_pack_missing_files contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
                "matrix_hash": "efgh",
            }
            with open(pack_dir / "seed_manifest.json", "w") as f:
                json.dump(manifest, f)

            with pytest.raises(DeterminismViolationError, match="Missing required files"):
                validator.validate_seed_pack(
                    base_path=str(base_path),
                    namespace="test_ns",
                    seed_index_version_hash="test_hash_123",
                )
        finally:
            shutil.rmtree(base_path)

    def test_validate_seed_pack_hash_mismatch_negative_control(self):
    """Test validate_seed_pack_hash_mismatch_negative_control contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Tamper with row_index.jsonl
            pack_dir = base_path / "seed_packs" / "test_ns" / manifest.seed_index_version_hash
            row_index_path = pack_dir / "row_index.jsonl"
            with open(row_index_path, "r+b") as f:
                # Flip one byte
                f.seek(10)
                f.write(b"X")

            with pytest.raises(DeterminismViolationError, match="Row index hash mismatch"):
                validator.validate_seed_pack(
                    base_path=str(base_path),
                    namespace="test_ns",
                    seed_index_version_hash=manifest.seed_index_version_hash,
                )
        finally:
            shutil.rmtree(base_path)

    def test_validate_seed_pack_embeddings_tampered_negative_control(self):
    """Test validate_seed_pack_embeddings_tampered_negative_control contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Tamper with embeddings.f32
            pack_dir = base_path / "seed_packs" / "test_ns" / manifest.seed_index_version_hash
            embeddings_path = pack_dir / "embeddings.f32"
            with open(embeddings_path, "r+b") as f:
                # Flip one byte
                f.seek(5)
                f.write(b"X")

            with pytest.raises(DeterminismViolationError, match="Embeddings hash mismatch"):
                validator.validate_seed_pack(
                    base_path=str(base_path),
                    namespace="test_ns",
                    seed_index_version_hash=manifest.seed_index_version_hash,
                )
        finally:
            shutil.rmtree(base_path)

    def test_validate_seed_pack_version_hash_mismatch(self):
    """Test validate_seed_pack_version_hash_mismatch contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Try to validate with wrong hash - directory doesn't exist
            with pytest.raises(DeterminismViolationError, match="Seed pack directory does not exist"):
                validator.validate_seed_pack(
                    base_path=str(base_path),
                    namespace="test_ns",
                    seed_index_version_hash="wrong_hash",
                )
        finally:
            shutil.rmtree(base_path)


class TestReplayValidatorEmbeddingArtifact:
    """Test embedding artifact validation functionality."""

    def test_validate_embedding_artifact_success(self):
    """Test validate_embedding_artifact_success contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
        validator.validate_embedding_artifact(
            artifact=artifact,
            expected_seed_index_version_hash="hash123",
        )

    def test_validate_embedding_artifact_with_reference_hash(self):
    """Test validate_embedding_artifact_with_reference_hash contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"

        # Should validate successfully
        validator.validate_embedding_artifact(
            artifact=artifact,
            expected_seed_index_version_hash="hash123",
            reference_artifact_hash=reference_hash,
        )

    def test_validate_embedding_artifact_wrong_type(self):
    """Test validate_embedding_artifact_wrong_type contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    """Test validate_embedding_artifact_seed_hash_mismatch_negative_control contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
            validator.validate_embedding_artifact(
                artifact=artifact,
                expected_seed_index_version_hash="wrong_hash",
            )

    def test_validate_embedding_artifact_reference_hash_mismatch(self):
    """Test validate_embedding_artifact_reference_hash_mismatch contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
            validator.validate_embedding_artifact(
                artifact=artifact,
                expected_seed_index_version_hash="hash123",
                reference_artifact_hash="wrong_hash",
            )

    def test_validate_embedding_artifact_empty_trace_ids(self):
    """Test validate_embedding_artifact_empty_trace_ids contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
            validator.validate_embedding_artifact(
                artifact=artifact,
                expected_seed_index_version_hash="hash123",
            )

    def test_validate_embedding_artifact_duplicate_trace_ids(self):
    """Test validate_embedding_artifact_duplicate_trace_ids contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
            validator.validate_embedding_artifact(
                artifact=artifact,
                expected_seed_index_version_hash="hash123",
            )

    def test_validate_embedding_artifact_empty_strings_negative_control(self):
    """Test validate_embedding_artifact_empty_strings_negative_control contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
            validator.validate_embedding_artifact(
                artifact=artifact,
                expected_seed_index_version_hash="hash123",
            )

    def test_validate_embedding_artifact_k_mismatch(self):
    """Test validate_embedding_artifact_k_mismatch contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
            DeterminismViolationError, match="k \\(5\\) does not match number of trace IDs \\(2\\)"
        ):
            validator.validate_embedding_artifact(
                artifact=artifact,
                expected_seed_index_version_hash="hash123",
            )

    def test_validate_embedding_artifact_wrong_order_negative_control(self):
    """Test validate_embedding_artifact_wrong_order_negative_control contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"

        # This should actually pass since EmbeddingArtifact auto-sorts
        validator.validate_embedding_artifact(
            artifact=artifact,
            expected_seed_index_version_hash="hash123",
        )

        # But if we manually create an artifact with wrong order (bypassing __post_init__)
        # This would require direct manipulation, which is prevented by frozen dataclass


class TestDeterminismStability:
    """Test determinism stability across multiple operations."""

    def test_seed_pack_artifact_hash_stability(self):
        """Mandatory: Test artifact hash stability across retrievals."""
        validator = ReplayValidator()

        base_path = Path(tempfile.mkdtemp())

        try:
            # Build seed pack via B0 builder
            embedder = DeterministicHashEmbedder(dimensions=4)
            config = SeedEmbeddingPackConfig(
                namespace="test_ns",
                bootstrap_mode="minimal_seed",
                minimal_seed_count=3,
            )
            corpus_rows = [
                {
                    "content_hash": "h1" * 32,
                    "trace_id": "t1",
                    "namespace": "test_ns",
                    "created_utc": 1234567890,
                },
                {
                    "content_hash": "h2" * 32,
                    "trace_id": "t2",
                    "namespace": "test_ns",
                    "created_utc": 1234567891,
                },
                {
                    "content_hash": "h3" * 32,
                    "trace_id": "t3",
                    "namespace": "test_ns",
                    "created_utc": 1234567892,
                },
            ]

            manifest = build_seed_embedding_pack(
                base_path=base_path,
                config=config,
                corpus_rows=corpus_rows,
                embedder=embedder,
                built_at_utc=1234567890,
            )

            # Create embedding artifact
            artifact1 = EmbeddingArtifact(
                namespace="test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
                supporting_trace_ids=["t1", "t2", "t3"],
                supporting_content_hashes=["h1" * 32, "h2" * 32, "h3" * 32],
                k=3,
                similarity_metric="cosine",
                embedding_model_version="v1.0",
            )

            # Capture artifact hash
            artifact_hash1 = artifact1.artifact_hash()

            # Re-create same artifact (simulating retrieval)
            artifact2 = EmbeddingArtifact(
                namespace="test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
                supporting_trace_ids=["t1", "t2", "t3"],
                supporting_content_hashes=["h1" * 32, "h2" * 32, "h3" * 32],
                k=3,
                similarity_metric="cosine",
                embedding_model_version="v1.0",
            )

            # Validate hash stability
            artifact_hash2 = artifact2.artifact_hash()
            assert artifact_hash1 == artifact_hash2, "Artifact hash should be stable"

            # Validate both artifacts
            validator.validate_embedding_artifact(
                artifact=artifact1,
                expected_seed_index_version_hash=manifest.seed_index_version_hash,
                reference_artifact_hash=artifact_hash1,
            )

            validator.validate_embedding_artifact(
                artifact=artifact2,
                expected_seed_index_version_hash=manifest.seed_index_version_hash,
                reference_artifact_hash=artifact_hash1,
            )

            # Validate seed pack
            validator.validate_seed_pack(
                base_path=str(base_path),
                namespace="test_ns",
                seed_index_version_hash=manifest.seed_index_version_hash,
            )
        finally:
            shutil.rmtree(base_path)
