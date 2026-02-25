"""W1 Determinism Test - Run twice to prove identical results."""

import sys
import os
sys.path.insert(0, '.')

import tempfile
import json
import hashlib
import numpy as np
from pathlib import Path

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
    embeddings = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
    ], dtype=np.float32)
    
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
            if (r1.content_hash != r2.content_hash or 
                r1.score_round6 != r2.score_round6 or
                r1.row_idx != r2.row_idx or
                r1.embedding_artifact_hash != r2.embedding_artifact_hash):
                match = False
                break
        
        if match:
            print("PASS: RESULTS IDENTICAL - DETERMINISM PROVEN")
        else:
            print("FAIL: RESULTS DIFFER - DETERMINISM FAILED")
    else:
        print("FAIL: NO RESULTS TO COMPARE")
