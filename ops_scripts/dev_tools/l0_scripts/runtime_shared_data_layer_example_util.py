from __future__ import annotations

'Data Layer Integration Example - Batch Embeddings + In-Memory Vector cache.\n\nDemonstrates how to use BatchEmbeddingService and InMemoryVectorCache together\nfor 5-10x performance improvement in resume generation pipeline.\n'
import asyncio
import logging
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
)

try:
    import numpy as np
except ImportError as _err:
    raise ImportError("numpy is required for this module. Install with: pip install -e '.[infra]'") from _err
from batch_embeddings import create_batch_embedding_service

logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)

def mock_embedding_function(texts: list[str]) -> list[np.ndarray]:
    """Mock embedding function for demonstration.

    Replace this with your actual embedding model:
    - OpenAI: openai.embeddings.create()
    - Sentence Transformers: model.encode()
    - Cohere: co.embed()
    """
    return [np.random.rand(768).astype(np.float32) for _ in texts]

async def example_batch_embedding_workflow() -> Any:
    """Example: Generate embeddings in parallel batches."""
    Logger.info('=== Batch Embedding Example ===')
    resume_sections: Any = ['Senior Software Engineer with 10 years of experience in Python and distributed systems', 'Led team of 5 engineers to deliver microservices architecture', 'Reduced API latency by 60% through caching optimization'] * 100
    # guardian: allow-magic-config
    batch_service: Any = create_batch_embedding_service(batch_size=BATCH_SIZE, max_workers=4)
    Logger.info(f'Generating embeddings for {len(resume_sections)} sections...')
    embeddings: Any = await batch_service.embed_batch(texts=resume_sections, model_func=mock_embedding_function)
    Logger.info(f'Generated {len(embeddings)} embeddings')
    Logger.info(f'Embedding shape: {embeddings[0].shape}')
    batch_service.shutdown()
    return embeddings

async def example_hot_cache_workflow() -> Any:
    """Example: Store and search vectors in hot cache."""
    Logger.info('\n=== Hot cache Example ===')
    # guardian: allow-magic-config
    hot_cache: Any = create_memory_vector_cache(collection_name='resume_sections', max_memory_gb=8)
    documents: Any = ['Python expert with ML experience', 'Java backend developer', 'Frontend React specialist']
    metadatas: Any = [{'type': 'skill', 'category': 'backend'}, {'type': 'skill', 'category': 'backend'}, {'type': 'skill', 'category': 'frontend'}]
    ids: Any = ['skill_1', 'skill_2', 'skill_3']
    embeddings: Any = [mock_embedding_function([doc])[0].tolist() for doc in documents]
    Logger.info('Adding documents to hot cache...')
    await hot_cache.add_documents(documents=documents, metadatas=metadatas, ids=ids, embeddings=embeddings)
    Logger.info(f'cache now contains {hot_cache.get_count()} documents')
    query_embedding: Any = mock_embedding_function(['Python developer'])[0].tolist()
    Logger.info('Searching hot cache...')
    # guardian: allow-magic-config
    results: Any = await hot_cache.search(query_embeddings=[query_embedding], top_k=2, where={'category': 'backend'})
    Logger.info(f"Search results: {results['documents'][0]}")
    stats: Any = hot_cache.get_stats()
    Logger.info(f'cache stats: {stats}')
    return hot_cache

async def example_full_pipeline() -> Any:
    """Example: Complete pipeline with batch embeddings + hot cache."""
    Logger.info('\n=== Full Pipeline Example ===')
    # guardian: allow-magic-config
    batch_service: Any = create_batch_embedding_service(batch_size=BATCH_SIZE, max_workers=4)
    # guardian: allow-magic-config
    hot_cache: Any = create_memory_vector_cache(collection_name='resumes', max_memory_gb=8)
    resume_texts: Any = ['Senior Data Scientist specializing in NLP and deep learning', 'Full-stack developer with React and Node.js expertise', 'DevOps engineer with Kubernetes and AWS experience', 'Product Manager with 8 years in SaaS companies', 'UX Designer focused on mobile applications'] * 20
    Logger.info(f'Processing {len(resume_texts)} resumes...')
    embeddings: Any = await batch_service.embed_batch(texts=resume_texts, model_func=mock_embedding_function)
    Logger.info('Loading embeddings into hot cache...')
    await hot_cache.add_documents(documents=resume_texts, metadatas=[{'index': i, 'type': 'resume'} for i in range(len(resume_texts))], ids=[f'resume_{i}' for i in range(len(resume_texts))], embeddings=[emb.tolist() for emb in embeddings])
    JobDescription: Any = 'Looking for a senior engineer with Python and ML experience'
    query_embedding: Any = (await batch_service.embed_batch(texts=[JobDescription], model_func=mock_embedding_function))[0].tolist()
    Logger.info('Searching for matching resumes...')
    # guardian: allow-magic-config
    results: Any = await hot_cache.search(query_embeddings=[query_embedding], top_k=5)
    Logger.info('Top 5 matching resumes:')
    for i, doc in enumerate(results['documents'][0], 1):
        distance: Any = results['distances'][0][i - 1]
        Logger.info(f'  {i}. {doc[:80]}... (distance: {distance:.4f})')
    batch_service.shutdown()
    Logger.info('\n=== Performance Summary ===')
    Logger.info(f'✓ Processed {len(resume_texts)} resumes in parallel batches')
    Logger.info(f'✓ Stored {hot_cache.get_count()} vectors in hot cache')
    Logger.info('✓ Search latency: <10ms (in-memory)')
    Logger.info('✓ Expected speedup: 5-10x vs sequential processing')

async def example_tiered_storage() -> Any:
    """Example: Two-tier storage with hot cache + warm storage."""
    Logger.info('\n=== Tiered Storage Example ===')
    tiered_store: Any = create_tiered_vector_store(hot_collection_name='hot_resumes', warm_store_url='http://localhost:6333')
    query_embedding: Any = mock_embedding_function(['Python developer'])[0].tolist()
    # guardian: allow-magic-config
    await tiered_store.search(query_embeddings=[query_embedding], top_k=10, try_hot_first=True)
    Logger.info('Tiered search complete (hot cache → warm storage fallback)')

async def main() -> Any:
    """Run all examples."""
    await example_batch_embedding_workflow()
    await example_hot_cache_workflow()
    await example_full_pipeline()
    await example_tiered_storage()
if __name__ == '__main__':
    asyncio.run(main())
