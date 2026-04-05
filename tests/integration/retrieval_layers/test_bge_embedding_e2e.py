"""
Test BGE Embedding E2E in Inference Pipeline (Blue vs Blue)

Validates per Agentic Retrieval Models v9.md:
- Pipeline C (Inference): Query -> Embed -> Retrieve -> Generate
- Layer 2 Semantic Cache: 🔵 intent_vec vs 🔵 intent_vec (blue vs blue)
- Uses BAAI/bge-m3 for both query embedding and cache storage
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_bge_embedding_generation():
    """Test BGE-m3 generates consistent embeddings (blue vectors)."""
    print("\n=== Test 1: BGE Embedding Generation ===")

    from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

    # Test embedding generation
    text1 = "How do I configure the semantic cache?"
    text2 = "How do I configure the semantic cache?"  # Same text
    text3 = "What is the weather today?"  # Different text

    vec1 = bmg_embed_text(text1)
    vec2 = bmg_embed_text(text2)
    vec3 = bmg_embed_text(text3)

    # Verify vectors are generated
    assert vec1 is not None, "Failed to generate embedding for text1"
    assert vec2 is not None, "Failed to generate embedding for text2"
    assert vec3 is not None, "Failed to generate embedding for text3"

    # Verify vector dimensions (bge-m3 = 1024)
    assert len(vec1) == 1024, f"Expected 1024 dims, got {len(vec1)}"
    assert len(vec2) == 1024, f"Expected 1024 dims, got {len(vec2)}"
    assert len(vec3) == 1024, f"Expected 1024 dims, got {len(vec3)}"

    # Verify identical texts produce nearly identical vectors (within float precision)
    for i, (a, b) in enumerate(zip(vec1, vec2)):
        assert abs(a - b) < 1e-6, f"Vectors differ at index {i}: {a} vs {b}"

    # Verify L2 normalization (magnitude should be ~1.0)
    import math
    mag1 = math.sqrt(sum(x * x for x in vec1))
    mag3 = math.sqrt(sum(x * x for x in vec3))
    assert abs(mag1 - 1.0) < 0.01, f"Vector 1 not L2 normalized: magnitude={mag1}"
    assert abs(mag3 - 1.0) < 0.01, f"Vector 3 not L2 normalized: magnitude={mag3}"

    print(f"  ✓ Generated {len(vec1)}-dim embeddings")
    print("  ✓ Identical texts produce identical vectors")
    print("  ✓ L2 normalized (magnitude ~1.0)")
    return vec1, vec3


def test_bge_cosine_similarity():
    """Test BGE cosine similarity computation."""
    print("\n=== Test 2: BGE Cosine Similarity ===")

    from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_cosine_similarity

    # Test similar texts
    similar_texts = [
        "How do I configure Redis?",
        "What are the Redis configuration steps?",
        "Can you help me set up Redis?",
    ]

    query = "How do I configure Redis?"
    similarity = bmg_cosine_similarity(query, similar_texts)

    assert 0.0 <= similarity <= 1.0, f"Similarity {similarity} out of range [0, 1]"
    assert similarity > 0.8, f"Expected high similarity for similar texts, got {similarity}"

    # Test dissimilar texts
    dissimilar_texts = [
        "The weather is nice today",
        "Python is a programming language",
        "Machine learning is fascinating",
    ]

    similarity_low = bmg_cosine_similarity(query, dissimilar_texts)
    assert similarity_low < 0.7, f"Expected low similarity for dissimilar texts, got {similarity_low}"

    print(f"  ✓ Similar texts: similarity={similarity:.4f} (>0.8)")
    print(f"  ✓ Dissimilar texts: similarity={similarity_low:.4f} (<0.7)")


def test_embedding_factory_bge_client():
    """Test embedding factory creates BGE-m3 client correctly."""
    print("\n=== Test 3: Embedding Factory BGE Client ===")

    import hashlib
    import os
    os.environ["EMBEDDING_ENABLED"] = "true"

    from agentic_core.embeddings.embedding_factory import create_embedding_client
    from agentic_core.embeddings.embedding_input_guard import GuardedText

    # Create BGE-m3 client
    client = create_embedding_client("bge-m3", model="BAAI/bge-m3")

    # Verify client properties
    assert client is not None, "Failed to create BGE-m3 client"
    assert hasattr(client, 'embedder_identity'), "Client missing embedder_identity"
    assert client.embedder_identity["provider"] == "bge-m3", "Wrong provider"
    assert client.embedder_identity["dimensions"] == 1024, "Wrong dimensions"

    # Test async embedding with properly constructed GuardedText
    async def test_embed():
        text = "Test query for semantic cache"
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        guarded = GuardedText(
            redacted_text=text,
            hash=text_hash,
            size=len(text)
        )
        embedding = await client.get_embedding(guarded)
        return embedding

    embedding = asyncio.run(test_embed())

    assert embedding is not None, "Failed to generate embedding"
    assert len(embedding) == 1024, f"Expected 1024 dims, got {len(embedding)}"

    print(f"  ✓ BGE-m3 client created with {client.embedder_identity['dimensions']} dims")
    print(f"  ✓ Async embedding works: {len(embedding)}-dim vector")


def test_semantic_cache_manager_embedding():
    """Test SemanticCacheManager uses BGE-m3 for vector storage."""
    print("\n=== Test 4: Semantic Cache Manager (Blue vs Blue) ===")

    from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

    # Get singleton instance
    cache = SemanticCacheManager.get_instance()

    # Verify vector store is available
    assert cache.vector_store_enabled, "Vector store not enabled"
    assert cache._vector_store is not None, "Vector store not initialized"

    # Test internal embedding method
    test_text = "Test query for semantic matching in cache"
    vector = cache._get_embedding(test_text)

    assert vector is not None, "Failed to generate embedding via cache manager"
    assert len(vector) == 1024, f"Expected 1024 dims, got {len(vector)}"

    print(f"  ✓ Cache manager generates {len(vector)}-dim blue vectors")
    print("  ✓ Vector store ready for blue vs blue comparison")


def test_in_memory_vector_store_blue_vs_blue():
    """Test InMemoryVectorStore performs blue vs blue vector comparison."""
    print("\n=== Test 5: In-Memory Vector Store (Blue vs Blue) ===")

    import asyncio

    from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text
    from agentic_core.L4_state.memory.in_memory_vector_store import InMemoryVectorStore
    from agentic_core.L4_state.types.memory_item_types import MemoryItem, MemoryQuery

    # Create store
    store = InMemoryVectorStore()
    asyncio.run(store.initialize())

    # Store some "blue" vectors (previously embedded queries/results)
    texts = [
        "How do I configure Redis?",
        "What are the steps to set up ChromaDB?",
        "How does the semantic cache work?",
    ]

    # Create MemoryItems with blue vectors (cached embeddings)
    items = []
    for i, text in enumerate(texts):
        vector = bmg_embed_text(text)
        item = MemoryItem(
            content=text,
            embedding=vector,
            metadata={"namespace": "test", "original_text": text}
        )
        items.append(item)

    # Store blue vectors
    asyncio.run(store.upsert(items))

    # Now query with a new "blue" vector (query embedding)
    query_text = "How do I configure Redis cache?"  # Semantically similar to first item
    query_vector = bmg_embed_text(query_text)

    query = MemoryQuery(vector=query_vector, top_k=3, filter_metadata={"namespace": "test"})
    results = asyncio.run(store.query(query))

    assert len(results) > 0, "No results returned from vector store"

    # Verify blue vs blue comparison
    best_match = results[0]
    assert best_match.score is not None, "Score not set on result"
    assert best_match.score > 0.85, f"Expected high similarity (>0.85), got {best_match.score}"

    # The best match should be the Redis-related text
    assert "Redis" in best_match.metadata.get("original_text", ""), "Wrong best match"

    print(f"  ✓ Stored {len(items)} blue vectors (cached embeddings)")
    print(f"  ✓ Query blue vector matched with score: {best_match.score:.4f}")
    print("  ✓ Blue vs Blue comparison working correctly")


def main():
    """Run all E2E tests."""
    print("=" * 70)
    print("BGE Embedding E2E Test Suite (Blue vs Blue)")
    print("Validating per Agentic Retrieval Models v9.md")
    print("=" * 70)

    try:
        test_bge_embedding_generation()
        test_bge_cosine_similarity()
        test_embedding_factory_bge_client()
        test_semantic_cache_manager_embedding()
        test_in_memory_vector_store_blue_vs_blue()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print("\nSemantic Cache Infrastructure Validated:")
        print("  • BGE-m3 embedding model: ✓ Working")
        print("  • Embedding factory: ✓ Creates BGE clients")
        print("  • SemanticCacheManager: ✓ Generates blue vectors")
        print("  • InMemoryVectorStore: ✓ Blue vs Blue comparison")
        print("  • L2 Semantic Cache: ✓ Ready for inference pipeline")
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
