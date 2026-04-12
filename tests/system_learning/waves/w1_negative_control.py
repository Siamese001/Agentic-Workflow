"""W1 Negative Control - Tamper with hash to cause integrity failure."""

import sys

# REMOVED: _emit_records_execution_trace("p0", "evidence", "w1_negative_control")
# REMOVED: _emit_applies_guardrail("p0", "w1_negative_control", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "w1_negative_control", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "w1_negative_control", "state_snapshot")
# REMOVED: emit_replay_key("p0", "w1_negative_control")
# REMOVED: emit_determinism_digest("p0", "w1_negative_control")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "w1_negative_control", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "w1_negative_control", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "w1_negative_control", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "w1_negative_control", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "w1_negative_control", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "w1_negative_control", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "w1_negative_control", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "w1_negative_control", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "w1_negative_control", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "w1_negative_control", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "w1_negative_control", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "w1_negative_control", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "w1_negative_control", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "w1_negative_control", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "w1_negative_control", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "w1_negative_control", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "w1_negative_control", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "w1_negative_control", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "w1_negative_control", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "w1_negative_control", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

sys.path.insert(0, ".")

import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np

from system_learning.engines.embedding_service_factory import EmbeddingIntegrityError, EmbeddingServiceFactory

# REMOVED: _emit_emits_metric_event("w1_negative_control", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("w1_negative_control", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("w1_negative_control", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("w1_negative_control", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("w1_negative_control", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("w1_negative_control", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("w1_negative_control", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("w1_negative_control", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("w1_negative_control", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("w1_negative_control", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("w1_negative_control", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("w1_negative_control", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("w1_negative_control", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("w1_negative_control", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("w1_negative_control", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("w1_negative_control", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("w1_negative_control", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("w1_negative_control", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("w1_negative_control", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("w1_negative_control", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("w1_negative_control", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("w1_negative_control", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("w1_negative_control", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("w1_negative_control", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("w1_negative_control", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("w1_negative_control", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("w1_negative_control", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("w1_negative_control", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "w1_negative_control", "context_pull")
# REMOVED: _emit_pulls_context("p1", "w1_negative_control", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "w1_negative_control", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "w1_negative_control", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "w1_negative_control", "write_through")
# REMOVED: _emit_writes_through("p1", "w1_negative_control", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "w1_negative_control", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "w1_negative_control", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "w1_negative_control", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "w1_negative_control", "human_escalation")
# REMOVED: _emit_routes_through("p1", "w1_negative_control", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "w1_negative_control", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "w1_negative_control", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "w1_negative_control", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "w1_negative_control", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "w1_negative_control", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "w1_negative_control", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "w1_negative_control", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "w1_negative_control", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "w1_negative_control", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "w1_negative_control")
# REMOVED: _emit_gated_by_confidence("p1", "w1_negative_control", "confidence_gate")


def create_test_pack():
    """Create a temporary seed pack for testing."""
    tmpdir = Path(tempfile.mkdtemp())

    # Create manifest
    manifest = {
        "namespace": "healing_contexts",
        "bootstrap_mode": "curated_seed",
        "embedding_model_version": "text-embedding-3-large",
        "embedding_model_checksum": hashlib.sha256(b"model").hexdigest(),
        "canonicalization_version": "v1",
        "dimensions": 4,
        "vector_count": 3,
        "row_index_hash": hashlib.sha256(b"rows").hexdigest(),
        "matrix_hash": hashlib.sha256(b"matrix").hexdigest(),  # Will be tampered
        "seed_index_version_hash": "5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9",
        "built_at_utc": 1640995200,
    }

    # Create embeddings file
    embeddings = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )

    # Write files
    with open(tmpdir / "seed_manifest.json", "w") as f:
        json.dump(manifest, f)

    with open(tmpdir / "row_index.jsonl", "w") as f:
        for i in range(3):
            row_data = {
                "content_hash": hashlib.sha256(f"content_{i}".encode()).hexdigest(),
                "row_idx": i,
            }
            f.write(json.dumps(row_data) + "\n")

    embeddings.tofile(tmpdir / "embeddings.f32")

    return tmpdir


def run_negative_control():
    """Run test with tampered hash to cause integrity failure."""
    # Reset singleton
    EmbeddingServiceFactory._INSTANCE = None
    EmbeddingServiceFactory._INSTANCE_IDENTITY = None

    pack_dir = create_test_pack()

    print("=== NEGATIVE CONTROL TEST ===")
    print("Manifest hash tampered - expecting EmbeddingIntegrityError")

    try:
        EmbeddingServiceFactory.get(pack_dir)
        print("FAIL: No exception raised - integrity check failed to detect tamper")
        return False
    except (
        EmbeddingIntegrityError
    ) as e:  # guardian: EmbeddingIntegrityError should be handled with specific context
        print(f"PASS: EmbeddingIntegrityError caught: {e}")
        print("This proves integrity checks are essential")
        return True
    except Exception as e:
        print(f"UNEXPECTED: Different exception: {e}")
        return False
    finally:
        # Cleanup
        import shutil

        shutil.rmtree(pack_dir, ignore_errors=True)


if __name__ == "__main__":
    print("W1 NEGATIVE CONTROL - INTEGRITY TAMPER")
    print("=" * 50)
    print("Expected: EmbeddingIntegrityError when hash doesn't match")
    print("This proves integrity validation is required")
    print()

    success = run_negative_control()

    if success:
        print("\nOVERALL: NEGATIVE CONTROL PASSED")
        print("Tampering detected and prevented - security verified")
    else:
        print("\nOVERALL: NEGATIVE CONTROL FAILED")
        print("Tampering not detected - security issue")
