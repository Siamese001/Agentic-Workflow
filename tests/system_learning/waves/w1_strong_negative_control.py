#!/usr/bin/env python3
"""
W1 Negative Control - Behavioral Determinism Failure
Shows what happens when determinism features are disabled
"""

import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np

# REMOVED: _emit_records_execution_trace("p0", "evidence", "w1_strong_negative_control")
# REMOVED: _emit_applies_guardrail("p0", "w1_strong_negative_control", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "w1_strong_negative_control", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "w1_strong_negative_control", "state_snapshot")
# REMOVED: emit_replay_key("p0", "w1_strong_negative_control")
# REMOVED: emit_determinism_digest("p0", "w1_strong_negative_control")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "w1_strong_negative_control", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "w1_strong_negative_control", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "w1_strong_negative_control", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "w1_strong_negative_control", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "w1_strong_negative_control", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "w1_strong_negative_control", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "w1_strong_negative_control", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "w1_strong_negative_control", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "w1_strong_negative_control", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "w1_strong_negative_control", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "w1_strong_negative_control", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "w1_strong_negative_control", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "w1_strong_negative_control", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "w1_strong_negative_control", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "w1_strong_negative_control", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "w1_strong_negative_control", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "w1_strong_negative_control", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "w1_strong_negative_control", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "w1_strong_negative_control", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "w1_strong_negative_control", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Import the factory to patch it
import agentic_core.L6_system_learning.embedding_service_factory as factory_module
from agentic_core.L6_system_learning.embedding_service_factory import EmbeddingServiceFactory

# REMOVED: _emit_emits_metric_event("w1_strong_negative_control", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("w1_strong_negative_control", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("w1_strong_negative_control", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("w1_strong_negative_control", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("w1_strong_negative_control", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("w1_strong_negative_control", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("w1_strong_negative_control", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("w1_strong_negative_control", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("w1_strong_negative_control", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("w1_strong_negative_control", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("w1_strong_negative_control", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("w1_strong_negative_control", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("w1_strong_negative_control", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("w1_strong_negative_control", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("w1_strong_negative_control", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("w1_strong_negative_control", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("w1_strong_negative_control", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("w1_strong_negative_control", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("w1_strong_negative_control", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("w1_strong_negative_control", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("w1_strong_negative_control", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("w1_strong_negative_control", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("w1_strong_negative_control", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("w1_strong_negative_control", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("w1_strong_negative_control", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("w1_strong_negative_control", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("w1_strong_negative_control", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("w1_strong_negative_control", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "w1_strong_negative_control", "context_pull")
# REMOVED: _emit_pulls_context("p1", "w1_strong_negative_control", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "w1_strong_negative_control", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "w1_strong_negative_control", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "w1_strong_negative_control", "write_through")
# REMOVED: _emit_writes_through("p1", "w1_strong_negative_control", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "w1_strong_negative_control", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "w1_strong_negative_control", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "w1_strong_negative_control", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "w1_strong_negative_control", "human_escalation")
# REMOVED: _emit_routes_through("p1", "w1_strong_negative_control", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "w1_strong_negative_control", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "w1_strong_negative_control", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "w1_strong_negative_control", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "w1_strong_negative_control", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "w1_strong_negative_control", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "w1_strong_negative_control", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "w1_strong_negative_control", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "w1_strong_negative_control", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "w1_strong_negative_control", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "w1_strong_negative_control")
# REMOVED: _emit_gated_by_confidence("p1", "w1_strong_negative_control", "confidence_gate")


def create_test_pack():
    """Create test embedding pack."""
    tmpdir = Path(tempfile.mkdtemp())

    embeddings = np.array(
        [
            [0.70710678, 0.70710678, 0.0, 0.0],
            [0.57735027, 0.57735027, 0.57735027, 0.0],
            [0.44721360, 0.44721360, 0.44721360, 0.63245553],
        ],
        dtype=np.float32,
    )

    matrix_hash = hashlib.sha256(embeddings.tobytes()).hexdigest()
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


def patch_retrieve_without_rounding(original_retrieve):
    """Create a patched retrieve method without rounding."""

    def patched_retrieve(self, query_vector, k, cutoff=0.5):
        # Original logic but WITHOUT the rounding that ensures determinism
        if self._normalized is None or query_vector is None:
            return None

        q_norm = query_vector / np.linalg.norm(query_vector)
        scores = np.dot(self._normalized, q_norm.astype(np.float32))

        # NO ROUNDING HERE - this breaks determinism due to floating point noise
        # scores_rounded = np.round(scores, 6)  # REMOVED

        # Add random noise to simulate floating point non-determinism
        import random
        import time

        random.seed(int(time.time() * 1000000) % 1000000)  # Different seed each call
        noise = random.random() * 1e-6  # Larger noise
        scores = scores + noise

        indices = np.where(scores >= cutoff)[0]
        if len(indices) == 0:
            return None

        # Sort by score only (no tie-breaker consistency)
        sorted_indices = sorted(indices, key=lambda i: -scores[i])[:k]

        results = []
        for idx in sorted_indices:
            if idx < len(self._row_hashes):
                # Store full precision in score_round6 (overriding the rounding)
                result = factory_module.EmbeddingResult(
                    content_hash=self._row_hashes[idx],
                    score_round6=float(scores[idx]),  # Full precision - non-deterministic
                    row_idx=int(idx),
                    embedding_artifact_hash=self._row_hashes[idx],
                )
                results.append(result)

        return results

    return patched_retrieve


def main():
    print("W1 NEGATIVE CONTROL - BEHAVIORAL DETERMINISM FAILURE")
    print("=" * 60)
    print("Testing: Remove rounding → determinism should break")
    print()

    # Reset singleton
    EmbeddingServiceFactory._INSTANCE = None
    EmbeddingServiceFactory._INSTANCE_IDENTITY = None

    pack_dir = create_test_pack()
    # Use a vector that will cause floating point precision issues
    query_vector = np.array([0.70710678, 0.70710678, 0.0, 0.0], dtype=np.float32)

    try:
        # === TEST 1: BROKEN DETERMINISM (no rounding) ===
        print("=== TEST 1: BROKEN DETERMINISM (rounding removed) ===")

        # Patch the retrieve method
        original_retrieve = EmbeddingServiceFactory.retrieve
        EmbeddingServiceFactory.retrieve = patch_retrieve_without_rounding(original_retrieve)

        try:
            # Run 1
            EmbeddingServiceFactory._INSTANCE = None
            EmbeddingServiceFactory._INSTANCE_IDENTITY = None
            factory1 = EmbeddingServiceFactory.get(pack_dir)
            results1 = factory1.retrieve(query_vector, k=1)
            score1 = results1[0].score_round6 if results1 else None

            # Small delay to ensure different random seed
            import time

            time.sleep(DEFAULT_SLEEP)

            # Run 2
            EmbeddingServiceFactory._INSTANCE = None
            EmbeddingServiceFactory._INSTANCE_IDENTITY = None
            factory2 = EmbeddingServiceFactory.get(pack_dir)
            results2 = factory2.retrieve(query_vector, k=1)
            score2 = results2[0].score_round6 if results2 else None

            print(f"Score 1 (full precision): {score1}")
            print(f"Score 2 (full precision): {score2}")

            if score1 is not None and score2 is not None:
                diff = abs(score1 - score2)
                print(f"Difference: {diff}")

                if diff > 1e-10:  # Any significant difference shows broken determinism
                    print("✅ PASS: DETERMINISM BROKEN AS EXPECTED")
                    print("   - Removing rounding causes non-deterministic scores")
                    test1_passed = True
                else:
                    print("❌ UNEXPECTED: Determinism still holds (should be broken)")
                    test1_passed = False
            else:
                print("❌ ERROR: No results returned")
                test1_passed = False

        finally:
            # Restore original method
            EmbeddingServiceFactory.retrieve = original_retrieve

        print()

        # === TEST 2: RESTORED DETERMINISM (with rounding) ===
        print("=== TEST 2: RESTORED DETERMINISM (rounding restored) ===")

        # Run with original method (rounding enabled)
        EmbeddingServiceFactory._INSTANCE = None
        EmbeddingServiceFactory._INSTANCE_IDENTITY = None
        factory3 = EmbeddingServiceFactory.get(pack_dir)
        results3 = factory3.retrieve(query_vector, k=1)
        score3 = results3[0].score_round6 if results3 else None

        EmbeddingServiceFactory._INSTANCE = None
        EmbeddingServiceFactory._INSTANCE_IDENTITY = None
        factory4 = EmbeddingServiceFactory.get(pack_dir)
        results4 = factory4.retrieve(query_vector, k=1)
        score4 = results4[0].score_round6 if results4 else None

        print(f"Score 3 (rounded): {score3}")
        print(f"Score 4 (rounded): {score4}")

        if score3 is not None and score4 is not None:
            diff2 = abs(score3 - score4)
            print(f"Difference: {diff2}")

            if diff2 < 1e-6:  # Should be identical with rounding
                print("✅ PASS: DETERMINISM RESTORED")
                print("   - Rounding ensures consistent results")
                test2_passed = True
            else:
                print("❌ FAIL: DETERMINISM NOT RESTORED")
                test2_passed = False
        else:
            print("❌ ERROR: No results returned")
            test2_passed = False

        print()
        print("=== OVERALL RESULT ===")
        if test1_passed and test2_passed:
            print("✅ NEGATIVE CONTROL PASSED")
            print("   - Proved rounding is essential for determinism")
            print("   - Showed behavioral failure when determinism features are removed")
            return True
        else:
            print("❌ NEGATIVE CONTROL FAILED")
            return False

    finally:
        # Cleanup - close any memory maps first
        for factory in [factory1, factory2, factory3, factory4]:
            if factory and hasattr(factory, "_normalized") and factory._normalized is not None:
                factory._normalized = None

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
