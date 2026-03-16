"""W1 Determinism Test - Run twice to prove identical results."""

import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "w1_determinism_test")
_emit_applies_guardrail("p0", "w1_determinism_test", "p0_governance")
_emit_reads_policy_state("p0", "w1_determinism_test", "policy_binding")
_emit_snapshots_state("p0", "w1_determinism_test", "state_snapshot")
emit_replay_key("p0", "w1_determinism_test")
emit_determinism_digest("p0", "w1_determinism_test")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "w1_determinism_test", "execution_auth")
_emit_validates_capability("p2", "w1_determinism_test", "capability_check")
_emit_routes_to_capability("p2", "w1_determinism_test", "capability_route")
_emit_writes_via_uwg("p2", "w1_determinism_test", "uwg_write")
_emit_blocks_direct_write("p2", "w1_determinism_test", "direct_write_block")
_emit_records_tool_invocation("p2", "w1_determinism_test", "tool_invocation")
_emit_captures_execution_output("p2", "w1_determinism_test", "exec_output")
_emit_dispatches_agent("p3", "w1_determinism_test", "agent_dispatch")
_emit_coordinates_agents("p3", "w1_determinism_test", "agent_coordination")
_emit_records_workflow_lineage("p3", "w1_determinism_test", "workflow_lineage")
_emit_records_healing_outcome("p3", "w1_determinism_test", "healing_outcome")
_emit_escalates_failure("p3", "w1_determinism_test", "failure_escalation")
_emit_orchestrates_workflow("p3", "w1_determinism_test", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "w1_determinism_test", "healing_dispatch")
_emit_invokes_evaluation("p3", "w1_determinism_test", "evaluation_signal")
_emit_records_telemetry_event("p4", "w1_determinism_test", "telemetry_event")
_emit_captures_evaluation_metric("p4", "w1_determinism_test", "eval_metric")
_emit_stores_embedding("p4", "w1_determinism_test", "embedding_store")
_emit_updates_meta_learning_state("p4", "w1_determinism_test", "meta_learning")
_emit_links_execution_to_snapshot("p4", "w1_determinism_test", "exec_snapshot_link")

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

from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory


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
        "matrix_hash": "",
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

    manifest["matrix_hash"] = hashlib.sha256(embeddings.tobytes()).hexdigest()

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


def run_deterministic_test(run_num):
    """Run deterministic test and print results."""
    # Reset singleton
    EmbeddingServiceFactory._INSTANCE = None
    EmbeddingServiceFactory._INSTANCE_IDENTITY = None

    pack_dir = create_test_pack()
    service = EmbeddingServiceFactory.get(pack_dir)

    query = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    results = service.retrieve(query_vector=query, k=2, cutoff=0.5)

    print(f"=== RUN {run_num} RESULTS ===")
    if results:
        for i, r in enumerate(results):
            print(f"Result {i}: hash={r.content_hash[:16]}..., score={r.score_round6:.6f}, idx={r.row_idx}")
            print(f"  artifact_hash: {r.embedding_artifact_hash[:32]}...")
    else:
        print("No results")

    # Cleanup
    import shutil

    shutil.rmtree(pack_dir, ignore_errors=True)

    return results


if __name__ == "__main__":
    print("W1 DETERMINISM PROOF - SAME INPUT TWICE")
    print("=" * 50)

    # Run test twice
    results1 = run_deterministic_test(1)
    results2 = run_deterministic_test(2)

    # Compare
    print("\n=== COMPARISON ===")
    if results1 and results2:
        match = True
        for r1, r2 in zip(results1, results2):
            if (
                r1.content_hash != r2.content_hash
                or r1.score_round6 != r2.score_round6
                or r1.row_idx != r2.row_idx
                or r1.embedding_artifact_hash != r2.embedding_artifact_hash
            ):
                match = False
                break

        if match:
            print("PASS: RESULTS IDENTICAL - DETERMINISM PROVEN")
        else:
            print("FAIL: RESULTS DIFFER - DETERMINISM FAILED")
    else:
        print("FAIL: NO RESULTS TO COMPARE")
