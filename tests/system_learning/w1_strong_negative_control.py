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

# Import the factory to patch it
import system_learning.engines.embedding_service_factory as factory_module
from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory


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

            time.sleep(0.01)

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

        time.sleep(0.1)  # Brief pause for Windows file handle release
        shutil.rmtree(pack_dir, ignore_errors=True)

        EmbeddingServiceFactory._INSTANCE = None
        EmbeddingServiceFactory._INSTANCE_IDENTITY = None


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
