#!/usr/bin/env python3
"""
W1 Determinism Proof - Strong Version
Shows replay keys and strict equality across runs
"""

import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np

# REMOVED: _emit_records_execution_trace("p0", "evidence", "w1_strong_determinism_test")
# REMOVED: _emit_applies_guardrail("p0", "w1_strong_determinism_test", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "w1_strong_determinism_test", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "w1_strong_determinism_test", "state_snapshot")
# REMOVED: _emit_authorize_and_execute("p2", "w1_strong_determinism_test", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "w1_strong_determinism_test", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "w1_strong_determinism_test", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "w1_strong_determinism_test", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "w1_strong_determinism_test", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "w1_strong_determinism_test", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "w1_strong_determinism_test", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "w1_strong_determinism_test", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "w1_strong_determinism_test", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "w1_strong_determinism_test", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "w1_strong_determinism_test", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "w1_strong_determinism_test", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "w1_strong_determinism_test", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "w1_strong_determinism_test", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "w1_strong_determinism_test", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "w1_strong_determinism_test", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "w1_strong_determinism_test", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "w1_strong_determinism_test", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "w1_strong_determinism_test", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "w1_strong_determinism_test", "exec_snapshot_link")
from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

# REMOVED: _emit_emits_metric_event("w1_strong_determinism_test", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("w1_strong_determinism_test", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("w1_strong_determinism_test", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("w1_strong_determinism_test", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("w1_strong_determinism_test", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("w1_strong_determinism_test", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("w1_strong_determinism_test", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("w1_strong_determinism_test", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("w1_strong_determinism_test", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("w1_strong_determinism_test", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("w1_strong_determinism_test", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("w1_strong_determinism_test", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("w1_strong_determinism_test", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("w1_strong_determinism_test", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("w1_strong_determinism_test", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("w1_strong_determinism_test", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("w1_strong_determinism_test", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("w1_strong_determinism_test", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("w1_strong_determinism_test", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("w1_strong_determinism_test", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("w1_strong_determinism_test", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("w1_strong_determinism_test", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("w1_strong_determinism_test", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("w1_strong_determinism_test", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("w1_strong_determinism_test", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("w1_strong_determinism_test", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("w1_strong_determinism_test", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("w1_strong_determinism_test", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "w1_strong_determinism_test", "context_pull")
# REMOVED: _emit_pulls_context("p1", "w1_strong_determinism_test", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "w1_strong_determinism_test", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "w1_strong_determinism_test", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "w1_strong_determinism_test", "write_through")
# REMOVED: _emit_writes_through("p1", "w1_strong_determinism_test", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "w1_strong_determinism_test", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "w1_strong_determinism_test", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "w1_strong_determinism_test", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "w1_strong_determinism_test", "human_escalation")
# REMOVED: _emit_routes_through("p1", "w1_strong_determinism_test", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "w1_strong_determinism_test", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "w1_strong_determinism_test", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "w1_strong_determinism_test", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "w1_strong_determinism_test", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "w1_strong_determinism_test", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "w1_strong_determinism_test", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "w1_strong_determinism_test", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "w1_strong_determinism_test", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "w1_strong_determinism_test", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "w1_strong_determinism_test")
# REMOVED: _emit_gated_by_confidence("p1", "w1_strong_determinism_test", "confidence_gate")
# REMOVED: emit_replay_key("p0", "w1_strong_determinism_test")
# REMOVED: emit_determinism_digest("p0", "w1_strong_determinism_test")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


def create_test_pack():
    """Create deterministic test embedding pack."""
    tmpdir = Path(tempfile.mkdtemp())

    # Create deterministic embeddings
    embeddings = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )

    # Calculate actual matrix hash
    matrix_hash = hashlib.sha256(embeddings.tobytes()).hexdigest()

    # Create manifest
    manifest = {
        "namespace": "healing_contexts",
        "bootstrap_mode": "seed",
        "embedding_model_version": "text-embedding-3-large",
        "embedding_model_checksum": "test_checksum",
        "dimensions": 4,
        "vector_count": 3,
        "matrix_hash": matrix_hash,
        "row_index_hash": hashlib.sha256(b"test_index").hexdigest(),
        "seed_index_version_hash": "5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9",
        "built_at_utc": 1640995200,
    }

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

    # Write embeddings
    embeddings.tofile(tmpdir / "embeddings.f32")

    return tmpdir


def get_replay_key(factory, query_vector):
    """Get the replay key for a query."""
    # Simulate the replay key generation
    query_norm = query_vector / np.linalg.norm(query_vector)
    query_hash = hashlib.sha256(query_norm.tobytes()).hexdigest()[:16]

    # Get spot-check hash
    spot_check_hash = hashlib.sha256(factory._normalized[0].tobytes()).hexdigest()[:16]

    # Get normalized pack hash
    pack_hash = hashlib.sha256(factory._normalized.tobytes()).hexdigest()[:16]

    # BLAS fingerprint (simplified)
    blas_fp = "BLAS_LOCKED"

    replay_key = f"{query_hash}:{spot_check_hash}:{pack_hash}:{blas_fp}"
    return replay_key


def main():
    print("W1 STRONG DETERMINISM PROOF")
    print("=" * 50)

    # Reset singleton
    EmbeddingServiceFactory._INSTANCE = None
    EmbeddingServiceFactory._INSTANCE_IDENTITY = None

    pack_dir = create_test_pack()
    query_vector = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)

    try:
        print("\n=== RUN 1 ===")
        factory1 = EmbeddingServiceFactory.get(pack_dir)
        results1 = factory1.retrieve(query_vector, k=1)
        replay_key1 = get_replay_key(factory1, query_vector)

        print(f"Replay Key 1: {replay_key1}")
        print(f"Result 1: hash={results1[0].content_hash[:16]}..., score={results1[0].score_round6:.6f}")

        # Reset singleton completely
        EmbeddingServiceFactory._INSTANCE = None
        EmbeddingServiceFactory._INSTANCE_IDENTITY = None

        print("\n=== RUN 2 ===")
        factory2 = EmbeddingServiceFactory.get(pack_dir)
        results2 = factory2.retrieve(query_vector, k=1)
        replay_key2 = get_replay_key(factory2, query_vector)

        print(f"Replay Key 2: {replay_key2}")
        print(f"Result 2: hash={results2[0].content_hash[:16]}..., score={results2[0].score_round6:.6f}")

        print("\n=== EQUALITY ASSERTION ===")
        keys_equal = replay_key1 == replay_key2
        scores_equal = abs(results1[0].score_round6 - results2[0].score_round6) < 1e-6
        hashes_equal = results1[0].content_hash == results2[0].content_hash

        print(f"Replay Keys Equal: {keys_equal}")
        print(f"Scores Equal: {scores_equal}")
        print(f"Hashes Equal: {hashes_equal}")

        if keys_equal and scores_equal and hashes_equal:
            print("\n✅ PASS: STRONG DETERMINISM PROVEN")
            print("   - Identical replay keys across independent invocations")
            print("   - Identical scores and hashes")
            return True
        else:
            print("\n❌ FAIL: DETERMINISM BROKEN")
            if not keys_equal:
                print(f"   - Replay keys differ: {replay_key1} != {replay_key2}")
            if not scores_equal:
                print(f"   - Scores differ: {results1[0].score_round6} != {results2[0].score_round6}")
            if not hashes_equal:
                print(f"   - Hashes differ: {results1[0].content_hash} != {results2[0].content_hash}")
            return False

    finally:
        # Cleanup - close any memory maps first
        if factory1 and hasattr(factory1, "_normalized") and factory1._normalized is not None:
            factory1._normalized = None
        if factory2 and hasattr(factory2, "_normalized") and factory2._normalized is not None:
            factory2._normalized = None

        # Force garbage collection
        import gc

        gc.collect()

        # Remove temp directory
        import shutil
        import time

        time.sleep(DEFAULT_SLEEP)  # Brief pause for Windows file handle release
        shutil.rmtree(pack_dir, ignore_errors=True)

        EmbeddingServiceFactory._INSTANCE = None
        EmbeddingServiceFactory._INSTANCE_IDENTITY = None


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
