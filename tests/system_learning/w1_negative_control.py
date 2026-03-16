"""W1 Negative Control - Tamper with hash to cause integrity failure."""

import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "w1_negative_control")
_emit_applies_guardrail("p0", "w1_negative_control", "p0_governance")
_emit_reads_policy_state("p0", "w1_negative_control", "policy_binding")
_emit_snapshots_state("p0", "w1_negative_control", "state_snapshot")
emit_replay_key("p0", "w1_negative_control")
emit_determinism_digest("p0", "w1_negative_control")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
    except EmbeddingIntegrityError as e:
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
