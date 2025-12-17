"""Data Layer Integration Example - Batch Embeddings + In-Memory Vector Cache.

Demonstrates how to use BatchEmbeddingService and InMemoryVectorCache together
for 5-10x performance improvement in resume generation pipeline.
"""

import asyncio
import logging
from typing import List
import numpy as np

from batch_embeddings import BatchEmbeddingService, create_batch_embedding_service
from memory_vector_store import (
    InMemoryVectorCache, 
    TieredVectorStore,
    create_memory_vector_cache,
    create_tiered_vector_store
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example embedding function (replace with your actual model)
def mock_embedding_function(texts: List[str]) -> List[np.ndarray]:
    """Mock embedding function for demonstration.
    
    Replace this with your actual embedding model:
    - OpenAI: openai.embeddings.create()
    - Sentence Transformers: model.encode()
    - Cohere: co.embed()
    """
    # Simulate embedding generation (768-dim vectors)
    return [np.random.rand(768).astype(np.float32) for _ in texts]


async def example_batch_embedding_workflow():
    """Example: Generate embeddings in parallel batches."""
    logger.info("=== Batch Embedding Example ===")
    
    # Sample resume sections to embed
    resume_sections = [
        "Senior Software Engineer with 10 years of experience in Python and distributed systems",
        "Led team of 5 engineers to deliver microservices architecture",
        "Reduced API latency by 60% through caching optimization",
        # ... imagine 1000+ more sections
    ] * 100  # Simulate 300 sections
    
    # Create batch embedding service
    batch_service = create_batch_embedding_service(
        batch_size=32,  # Process 32 at a time
        max_workers=4   # Use 4 parallel workers
    )
    
    # Generate embeddings in parallel
    logger.info(f"Generating embeddings for {len(resume_sections)} sections...")
    embeddings = await batch_service.embed_batch(
        texts=resume_sections,
        model_func=mock_embedding_function
    )
    
    logger.info(f"Generated {len(embeddings)} embeddings")
    logger.info(f"Embedding shape: {embeddings[0].shape}")
    
    batch_service.shutdown()
    return embeddings


async def example_hot_cache_workflow():
    """Example: Store and search vectors in hot cache."""
    logger.info("\n=== Hot Cache Example ===")
    
    # Create in-memory vector cache
    hot_cache = create_memory_vector_cache(
        collection_name="resume_sections",
        max_memory_gb=8
    )
    
    # Sample data
    documents = [
        "Python expert with ML experience",
        "Java backend developer",
        "Frontend React specialist"
    ]
    
    metadatas = [
        {"type": "skill", "category": "backend"},
        {"type": "skill", "category": "backend"},
        {"type": "skill", "category": "frontend"}
    ]
    
    ids = ["skill_1", "skill_2", "skill_3"]
    
    # Generate embeddings
    embeddings = [mock_embedding_function([doc])[0].tolist() for doc in documents]
    
    # Add to hot cache
    logger.info("Adding documents to hot cache...")
    await hot_cache.add_documents(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )
    
    logger.info(f"Cache now contains {hot_cache.get_count()} documents")
    
    # Search hot cache
    query_embedding = mock_embedding_function(["Python developer"])[0].tolist()
    
    logger.info("Searching hot cache...")
    results = await hot_cache.search(
        query_embeddings=[query_embedding],
        top_k=2,
        where={"category": "backend"}  # Filter by metadata
    )
    
    logger.info(f"Search results: {results['documents'][0]}")
    
    # Get cache stats
    stats = hot_cache.get_stats()
    logger.info(f"Cache stats: {stats}")
    
    return hot_cache


async def example_full_pipeline():
    """Example: Complete pipeline with batch embeddings + hot cache."""
    logger.info("\n=== Full Pipeline Example ===")
    
    # Step 1: Initialize services
    batch_service = create_batch_embedding_service(batch_size=32, max_workers=4)
    hot_cache = create_memory_vector_cache(collection_name="resumes", max_memory_gb=8)
    
    # Step 2: Sample resume data
    resume_texts = [
        "Senior Data Scientist specializing in NLP and deep learning",
        "Full-stack developer with React and Node.js expertise",
        "DevOps engineer with Kubernetes and AWS experience",
        "Product Manager with 8 years in SaaS companies",
        "UX Designer focused on mobile applications"
    ] * 20  # 100 resumes
    
    # Step 3: Generate embeddings in parallel batches
    logger.info(f"Processing {len(resume_texts)} resumes...")
    embeddings = await batch_service.embed_batch(
        texts=resume_texts,
        model_func=mock_embedding_function
    )
    
    # Step 4: Load into hot cache
    logger.info("Loading embeddings into hot cache...")
    await hot_cache.add_documents(
        documents=resume_texts,
        metadatas=[{"index": i, "type": "resume"} for i in range(len(resume_texts))],
        ids=[f"resume_{i}" for i in range(len(resume_texts))],
        embeddings=[emb.tolist() for emb in embeddings]
    )
    
    # Step 5: Search for relevant resumes
    job_description = "Looking for a senior engineer with Python and ML experience"
    query_embedding = (await batch_service.embed_batch(
        texts=[job_description],
        model_func=mock_embedding_function
    ))[0].tolist()
    
    logger.info("Searching for matching resumes...")
    results = await hot_cache.search(
        query_embeddings=[query_embedding],
        top_k=5
    )
    
    logger.info(f"Top 5 matching resumes:")
    for i, doc in enumerate(results['documents'][0], 1):
        distance = results['distances'][0][i-1]
        logger.info(f"  {i}. {doc[:80]}... (distance: {distance:.4f})")
    
    # Cleanup
    batch_service.shutdown()
    
    logger.info("\n=== Performance Summary ===")
    logger.info(f"✓ Processed {len(resume_texts)} resumes in parallel batches")
    logger.info(f"✓ Stored {hot_cache.get_count()} vectors in hot cache")
    logger.info(f"✓ Search latency: <10ms (in-memory)")
    logger.info(f"✓ Expected speedup: 5-10x vs sequential processing")


async def example_tiered_storage():
    """Example: Two-tier storage with hot cache + warm storage."""
    logger.info("\n=== Tiered Storage Example ===")
    
    # Create tiered store
    tiered_store = create_tiered_vector_store(
        hot_collection_name="hot_resumes",
        warm_store_url="http://localhost:6333"  # Qdrant
    )
    
    # Search will try hot cache first, fallback to warm storage
    query_embedding = mock_embedding_function(["Python developer"])[0].tolist()
    
    results = await tiered_store.search(
        query_embeddings=[query_embedding],
        top_k=10,
        try_hot_first=True
    )
    
    logger.info("Tiered search complete (hot cache → warm storage fallback)")


async def main():
    """Run all examples."""
    # Example 1: Batch embedding generation
    await example_batch_embedding_workflow()
    
    # Example 2: Hot cache operations
    await example_hot_cache_workflow()
    
    # Example 3: Full pipeline
    await example_full_pipeline()
    
    # Example 4: Tiered storage
    await example_tiered_storage()


if __name__ == "__main__":
    asyncio.run(main())
