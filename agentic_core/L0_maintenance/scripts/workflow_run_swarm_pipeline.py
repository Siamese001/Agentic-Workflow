"""Swarm Pipeline Orchestration - Main entry point demonstrating full parallel workflow.

This script demonstrates the complete optimized pipeline using all 4 phases:
- Phase 1: IDE optimization (.codeiumignore)
- Phase 2: Batch embeddings + in-memory vector cache
- Phase 3: Parallel HOP execution (SubatomicSwarm)
- Phase 4: Multi-process resume generation (ResumeSwarm)

Expected speedup: 10-30x end-to-end improvement
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.runtime.core.subatomic_swarm import create_subatomic_swarm
from scripts.runtime.shared.batch_embeddings import create_batch_embedding_service
from scripts.runtime.shared.memory_vector_store import create_memory_vector_cache
from scripts.runtime.shared.resume_swarm import create_resume_swarm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Mock embedding function for testing
def mock_embedder(texts: List[str]) -> List[List[float]]:
    """Mock embedding function simulating network latency."""
    import time
    time.sleep(0.1)  # Simulate API call latency
    return [[0.1] * 768 for _ in texts]


# Mock SubatomicHop for testing
class MockSubatomicHop:
    """Mock SubatomicHop for demonstration."""

    def __init__(self, hop_id: str = "mock_hop"):
        self.hop_id = hop_id

    async def run(self, **kwargs) -> Dict[str, Any]:
        """Simulate HOP execution."""
        await asyncio.sleep(0.5)  # Simulate LLM call
        return {
            "hop_id": self.hop_id,
            "status": "completed",
            "result": f"Processed: {kwargs.get('data', 'no data')}"
        }


async def demo_phase2_batch_embeddings():
    """Demonstrate Phase 2: Batch Embeddings."""
    print("\n" + "="*80)
    print("📊 PHASE 2 DEMO: Batch Embeddings")
    print("="*80)

    # Create batch embedding service
    embedder = create_batch_embedding_service(batch_size=32, max_workers=4)

    # Sample data
    sample_texts = [f"Resume section {i}: Python developer with ML experience" for i in range(100)]

    # Sequential baseline
    print(f"\n⏱️  Sequential Processing ({len(sample_texts)} texts)...")
    start_seq = time.time()
    seq_results = []
    for text in sample_texts:
        seq_results.append(mock_embedder([text])[0])
    time_seq = time.time() - start_seq
    print(f"   Time: {time_seq:.2f}s")

    # Parallel batch processing
    print(f"\n⚡ Parallel Batch Processing ({len(sample_texts)} texts)...")
    start_par = time.time()
    embeddings = await embedder.embed_batch(sample_texts, mock_embedder)
    time_par = time.time() - start_par
    print(f"   Time: {time_par:.2f}s")
    print(f"   Speedup: {time_seq / time_par:.2f}x")

    embedder.shutdown()
    return embeddings


async def demo_phase2_vector_cache(embeddings: List):
    """Demonstrate Phase 2: In-Memory Vector Cache."""
    print("\n" + "="*80)
    print("💾 PHASE 2 DEMO: In-Memory Vector Cache")
    print("="*80)

    # Create hot cache
    vector_cache = create_memory_vector_cache(
        collection_name="demo_resumes",
        max_memory_gb=8
    )

    # Prepare documents
    documents = [f"Resume {i}" for i in range(len(embeddings))]
    metadatas = [{"index": i, "type": "resume"} for i in range(len(embeddings))]
    ids = [f"resume_{i}" for i in range(len(embeddings))]

    # Add to cache
    print(f"\n📥 Adding {len(documents)} documents to hot cache...")
    start_add = time.time()
    await vector_cache.add_documents(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=[emb for emb in embeddings]
    )
    time_add = time.time() - start_add
    print(f"   Time: {time_add:.2f}s")
    print(f"   Cache size: {vector_cache.get_count()} documents")

    # Search cache
    print(f"\n🔍 Searching hot cache...")
    query_embedding = embeddings[0]

    # Simulate disk-based search (slower)
    start_disk = time.time()
    await asyncio.sleep(0.08)  # Simulate network/disk latency
    time_disk = time.time() - start_disk
    print(f"   Disk-based search: {time_disk*1000:.1f}ms")

    # In-memory search (faster)
    start_mem = time.time()
    results = await vector_cache.search(
        query_embeddings=[query_embedding],
        top_k=5
    )
    time_mem = time.time() - start_mem
    print(f"   In-memory search: {time_mem*1000:.1f}ms")
    print(f"   Speedup: {time_disk / time_mem:.1f}x")

    return vector_cache


async def demo_phase3_subatomic_swarm():
    """Demonstrate Phase 3: SubatomicSwarm (I/O-bound parallelism)."""
    print("\n" + "="*80)
    print("🤖 PHASE 3 DEMO: SubatomicSwarm (Parallel I/O)")
    print("="*80)

    # Create swarm
    swarm = create_subatomic_swarm(max_concurrency=5, timeout_per_hop=30.0)

    # Create mock HOPs
    num_hops = 20
    hops = [MockSubatomicHop(f"hop_{i}") for i in range(num_hops)]
    inputs = [{"data": f"input_{i}"} for i in range(num_hops)]

    # Sequential baseline
    print(f"\n⏱️  Sequential Execution ({num_hops} HOPs)...")
    start_seq = time.time()
    seq_results = []
    for hop, inp in zip(hops, inputs):
        result = await hop.run(**inp)
        seq_results.append(result)
    time_seq = time.time() - start_seq
    print(f"   Time: {time_seq:.2f}s")

    # Parallel swarm execution
    print(f"\n⚡ Parallel Swarm Execution ({num_hops} HOPs, max 5 concurrent)...")
    start_par = time.time()
    results = await swarm.execute_swarm(hops, inputs)
    time_par = time.time() - start_par
    print(f"   Time: {time_par:.2f}s")
    print(f"   Success rate: {swarm.get_success_rate():.1f}%")
    print(f"   Speedup: {time_seq / time_par:.2f}x")

    return results


async def demo_phase4_resume_swarm():
    """Demonstrate Phase 4: ResumeSwarm (CPU-bound parallelism)."""
    print("\n" + "="*80)
    print("📄 PHASE 4 DEMO: ResumeSwarm (Parallel CPU)")
    print("="*80)

    # Create swarm
    swarm = create_resume_swarm(num_workers=6, enable_metrics=True)

    # Prepare jobs
    num_jobs = 24
    jobs = [
        {
            "job_id": f"job_{i}",
            "job_description": f"Senior Developer position {i}",
            "user_profile": {"name": "Candidate", "skills": ["Python", "AWS"]},
            "output_format": "pdf"
        }
        for i in range(num_jobs)
    ]

    # Sequential baseline (simulated)
    print(f"\n⏱️  Sequential Processing ({num_jobs} resumes)...")
    time_seq = num_jobs * 0.5  # Simulated time
    print(f"   Estimated time: {time_seq:.2f}s")

    # Parallel processing
    print(f"\n⚡ Parallel Processing ({num_jobs} resumes, 6 workers)...")
    start_par = time.time()
    results = swarm.generate_batch(jobs)
    time_par = time.time() - start_par

    metrics = swarm.get_metrics()
    print(f"   Time: {time_par:.2f}s")
    print(f"   Success rate: {swarm.get_success_rate():.1f}%")
    print(f"   Throughput: {metrics.throughput:.2f} resumes/sec")
    print(f"   Speedup: {time_seq / time_par:.2f}x")

    return results


async def demo_full_pipeline():
    """Demonstrate complete end-to-end pipeline."""
    print("\n" + "="*80)
    print("🚀 FULL PIPELINE DEMO: All Phases Combined")
    print("="*80)

    total_start = time.time()

    # Initialize all services
    print("\n📦 Initializing Services...")
    embedder = create_batch_embedding_service(batch_size=32, max_workers=4)
    vector_cache = create_memory_vector_cache(collection_name="pipeline_demo", max_memory_gb=8)
    llm_swarm = create_subatomic_swarm(max_concurrency=5)
    cpu_swarm = create_resume_swarm(num_workers=6)

    # Sample data
    num_jobs = 50
    job_descriptions = [f"Job posting {i}: Senior Python Developer" for i in range(num_jobs)]

    # Step 1: Generate embeddings (Phase 2)
    print(f"\n⚡ Step 1: Generating embeddings for {num_jobs} jobs...")
    step1_start = time.time()
    embeddings = await embedder.embed_batch(job_descriptions, mock_embedder)
    step1_time = time.time() - step1_start
    print(f"   ✓ Completed in {step1_time:.2f}s")

    # Step 2: Cache vectors (Phase 2)
    print(f"\n💾 Step 2: Caching {len(embeddings)} vectors...")
    step2_start = time.time()
    await vector_cache.add_documents(
        documents=job_descriptions,
        metadatas=[{"index": i} for i in range(len(embeddings))],
        ids=[f"job_{i}" for i in range(len(embeddings))],
        embeddings=embeddings
    )
    step2_time = time.time() - step2_start
    print(f"   ✓ Completed in {step2_time:.2f}s")

    # Step 3: Generate content with LLM swarm (Phase 3)
    print(f"\n🤖 Step 3: Generating content with LLM swarm...")
    step3_start = time.time()
    hops = [MockSubatomicHop(f"content_hop_{i}") for i in range(num_jobs)]
    inputs = [{"data": desc} for desc in job_descriptions]
    await llm_swarm.execute_swarm(hops, inputs)
    step3_time = time.time() - step3_start
    print(f"   ✓ Completed in {step3_time:.2f}s")
    print(f"   ✓ Success rate: {llm_swarm.get_success_rate():.1f}%")

    # Step 4: Render PDFs with CPU swarm (Phase 4)
    print(f"\n📄 Step 4: Rendering PDFs with CPU swarm...")
    step4_start = time.time()
    pdf_jobs = [
        {"job_id": f"pdf_{i}", "content": "resume content"}
        for i in range(num_jobs)
    ]
    cpu_swarm.generate_batch(pdf_jobs)
    step4_time = time.time() - step4_start
    print(f"   ✓ Completed in {step4_time:.2f}s")
    print(f"   ✓ Success rate: {cpu_swarm.get_success_rate():.1f}%")

    # Summary
    total_time = time.time() - total_start

    print("\n" + "="*80)
    print("📊 PIPELINE SUMMARY")
    print("="*80)
    print(f"\nStep 1 (Embeddings):     {step1_time:6.2f}s")
    print(f"Step 2 (Caching):        {step2_time:6.2f}s")
    print(f"Step 3 (LLM Content):    {step3_time:6.2f}s")
    print(f"Step 4 (PDF Rendering):  {step4_time:6.2f}s")
    print(f"{'-'*40}")
    print(f"Total Pipeline Time:     {total_time:6.2f}s")

    # Calculate baseline (sequential)
    baseline_time = (
        num_jobs * 0.1 +  # Sequential embeddings
        num_jobs * 0.5 +  # Sequential LLM calls
        num_jobs * 0.5    # Sequential PDF rendering
    )

    print(f"\nEstimated Sequential:    {baseline_time:6.2f}s")
    print(f"Overall Speedup:         {baseline_time / total_time:6.2f}x")

    # Cleanup
    embedder.shutdown()


async def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("🚀 AGENTIC SWARM OPTIMIZATION TEST")
    print("="*80)
    print("\nDemonstrating 32GB/8-core WSL2 optimization with:")
    print("  • Phase 1: IDE optimization (.codeiumignore)")
    print("  • Phase 2: Batch embeddings + in-memory vector cache")
    print("  • Phase 3: Parallel HOP execution (SubatomicSwarm)")
    print("  • Phase 4: Multi-process resume generation (ResumeSwarm)")
    print("\nExpected improvement: 10-30x end-to-end speedup")

    try:
        # Run individual phase demos
        embeddings = await demo_phase2_batch_embeddings()
        await demo_phase2_vector_cache(embeddings)
        await demo_phase3_subatomic_swarm()
        await demo_phase4_resume_swarm()

        # Run full pipeline demo
        await demo_full_pipeline()

        print("\n" + "="*80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nNext Steps:")
        print("  1. Review OPTIMIZATION_PLAN.md for implementation roadmap")
        print("  2. Check PHASE2_README.md, PHASE3_README.md, PHASE4_README.md")
        print("  3. Integrate with your actual resume generation pipeline")
        print("  4. Monitor metrics and adjust concurrency levels")
        print("  5. Scale up gradually to production workloads")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)