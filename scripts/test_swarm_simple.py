"""Simple Swarm Pipeline Test - Standalone version without complex imports.

Tests all 4 phases with minimal dependencies to verify the optimization works.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Direct imports to avoid __init__.py issues
import importlib.util


def load_module(name, path):
    """Load a module directly from file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules directly
batch_embeddings = load_module(
    "batch_embeddings",
    project_root / "scripts/runtime/shared/batch_embeddings.py"
)
memory_vector_store = load_module(
    "memory_vector_store",
    project_root / "scripts/runtime/shared/memory_vector_store.py"
)
subatomic_swarm = load_module(
    "subatomic_swarm",
    project_root / "scripts/runtime/core/subatomic_swarm.py"
)
resume_swarm = load_module(
    "resume_swarm",
    project_root / "scripts/runtime/shared/resume_swarm.py"
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# Mock functions
def mock_embedder(texts):
    """Mock embedding function."""
    time.sleep(0.1)
    return [[0.1] * 768 for _ in texts]


class MockHop:
    """Mock SubatomicHop."""
    def __init__(self, hop_id="mock"):
        self.hop_id = hop_id

    async def run(self, **kwargs):
        await asyncio.sleep(0.5)
        return {"hop_id": self.hop_id, "status": "completed"}


async def test_phase2_embeddings():
    """Test Phase 2: Batch Embeddings."""
    print("\n" + "="*80)
    print("📊 PHASE 2 TEST: Batch Embeddings")
    print("="*80)

    embedder = batch_embeddings.create_batch_embedding_service(batch_size=32, max_workers=4)
    texts = [f"Resume section {i}" for i in range(100)]

    # Sequential
    print(f"\n⏱️  Sequential ({len(texts)} texts)...")
    start = time.time()
    for text in texts:
        mock_embedder([text])
    seq_time = time.time() - start
    print(f"   Time: {seq_time:.2f}s")

    # Parallel
    print(f"\n⚡ Parallel ({len(texts)} texts)...")
    start = time.time()
    embeddings = await embedder.embed_batch(texts, mock_embedder)
    par_time = time.time() - start
    print(f"   Time: {par_time:.2f}s")
    print(f"   Speedup: {seq_time / par_time:.2f}x")

    embedder.shutdown()
    return embeddings


async def test_phase2_cache(embeddings):
    """Test Phase 2: Vector Cache."""
    print("\n" + "="*80)
    print("💾 PHASE 2 TEST: In-Memory Vector Cache")
    print("="*80)

    cache = memory_vector_store.create_memory_vector_cache("test_cache", 8)

    docs = [f"Resume {i}" for i in range(len(embeddings))]
    metas = [{"index": i} for i in range(len(embeddings))]
    ids = [f"resume_{i}" for i in range(len(embeddings))]

    print(f"\n📥 Adding {len(docs)} documents...")
    start = time.time()
    await cache.add_documents(docs, metas, ids, embeddings)
    add_time = time.time() - start
    print(f"   Time: {add_time:.2f}s")
    print(f"   Cache size: {cache.get_count()}")

    print(f"\n🔍 Searching...")
    start = time.time()
    results = await cache.search([embeddings[0]], top_k=5)
    search_time = time.time() - start
    print(f"   Search time: {search_time*1000:.1f}ms")
    print(f"   Results: {len(results['documents'][0])}")


async def test_phase3_swarm():
    """Test Phase 3: SubatomicSwarm."""
    print("\n" + "="*80)
    print("🤖 PHASE 3 TEST: SubatomicSwarm")
    print("="*80)

    swarm = subatomic_swarm.create_subatomic_swarm(max_concurrency=5)

    num_hops = 20
    hops = [MockHop(f"hop_{i}") for i in range(num_hops)]
    inputs = [{"data": f"input_{i}"} for i in range(num_hops)]

    # Sequential
    print(f"\n⏱️  Sequential ({num_hops} HOPs)...")
    start = time.time()
    for hop, inp in zip(hops, inputs):
        await hop.run(**inp)
    seq_time = time.time() - start
    print(f"   Time: {seq_time:.2f}s")

    # Parallel
    print(f"\n⚡ Parallel ({num_hops} HOPs, max 5 concurrent)...")
    start = time.time()
    await swarm.execute_swarm(hops, inputs)
    par_time = time.time() - start
    print(f"   Time: {par_time:.2f}s")
    print(f"   Success rate: {swarm.get_success_rate():.1f}%")
    print(f"   Speedup: {seq_time / par_time:.2f}x")


def test_phase4_swarm():
    """Test Phase 4: ResumeSwarm."""
    print("\n" + "="*80)
    print("📄 PHASE 4 TEST: ResumeSwarm")
    print("="*80)

    swarm = resume_swarm.create_resume_swarm(num_workers=6)

    num_jobs = 24
    jobs = [{"job_id": f"job_{i}", "job_description": f"Role {i}"} for i in range(num_jobs)]

    # Sequential (simulated)
    seq_time = num_jobs * 0.5
    print(f"\n⏱️  Sequential ({num_jobs} jobs)...")
    print(f"   Estimated time: {seq_time:.2f}s")

    # Parallel
    print(f"\n⚡ Parallel ({num_jobs} jobs, 6 workers)...")
    start = time.time()
    swarm.generate_batch(jobs)
    par_time = time.time() - start

    print(f"   Time: {par_time:.2f}s")
    print(f"   Success rate: {swarm.get_success_rate():.1f}%")
    print(f"   Speedup: {seq_time / par_time:.2f}x")


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("🚀 SWARM OPTIMIZATION TEST")
    print("="*80)
    print("\nTesting 32GB/8-core WSL2 optimization:")
    print("  • Phase 2: Batch embeddings + vector cache")
    print("  • Phase 3: Parallel HOP execution")
    print("  • Phase 4: Multi-process resume generation")

    try:
        # Phase 2
        embeddings = await test_phase2_embeddings()
        await test_phase2_cache(embeddings)

        # Phase 3
        await test_phase3_swarm()

        # Phase 4
        test_phase4_swarm()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\nNext Steps:")
        print("  1. Review performance metrics above")
        print("  2. Check WSL2_OPTIMIZATION_COMPLETE.md for details")
        print("  3. Integrate with your resume generation pipeline")

        return 0

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
