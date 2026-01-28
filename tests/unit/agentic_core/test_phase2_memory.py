# Scope: Test Vector Models, Interface Contracts, and Retrieval Logic
# Mandatory: 100% Pass Rate required.

import pytest
import asyncio
from uuid import uuid4
from pydantic import ValidationError
from agentic_core.semantic_memory.models import MemoryItem, MemoryQuery
from agentic_core.semantic_memory.in_memory import InMemoryVectorStore

# ---TestCase 1: Memory Item Validation ---
def test_memory_item_integrity():
    """
    Verify MemoryItem strictly enforces vector rules.
    Edge Case: Empty vectors, missing content.
    """
    # 1. Valid
    item = MemoryItem(content="Hello", embedding=[0.1, 0.2, 0.3])
    assert len(item.embedding) == 3

    # 2. Invalid: Empty Vector
    with pytest.raises(ValidationError) as exc:
        MemoryItem(content="Bad", embedding=[])
    assert "cannot be empty" in str(exc.value)

    # 3. Invalid: Wrong Type in Vector
    with pytest.raises(ValidationError):
        MemoryItem(content="Bad Type", embedding=["a", "b"])

# ---TestCase 2: Async CRUD Operations ---
@pytest.mark.asyncio
async def test_vector_store_crud():
    """
    Verify async upsert and delete operations.
    """
    store = InMemoryVectorStore()
    await store.initialize()

    item1 = MemoryItem(content="A", embedding=[1.0, 0.0])
    item2 = MemoryItem(content="B", embedding=[0.0, 1.0])

    # UPSERT
    success = await store.upsert([item1, item2])
    assert success is True
    assert len(store._storage) == 2

    # DELETE
    await store.delete([str(item1.id)])
    assert len(store._storage) == 1
    assert str(item2.id) in store._storage

# ---TestCase 3: Similarity Search Logic ---
@pytest.mark.asyncio
async def test_cosine_similarity_logic():
    """
    Verify that the math behind the search works (1.0 vs 0.0 similarity).
    Edge Case: Orthogonal vectors.
    """
    store = InMemoryVectorStore()
    
    # Vector A [1, 0]
    # Vector B [0, 1]
    # Query  [1, 0] -> Should match A 100%, B 0%
    item_a = MemoryItem(content="A", embedding=[1.0, 0.0], id=uuid4())
    item_b = MemoryItem(content="B", embedding=[0.0, 1.0], id=uuid4())
    
    await store.upsert([item_a, item_b])

    query = MemoryQuery(vector=[1.0, 0.0], top_k=2)
    results = await store.query(query)

    assert len(results) == 2
    assert results[0].content == "A"
    assert results[0].score > 0.99  # Float point tolerance
    assert results[1].content == "B"
    assert results[1].score < 0.01

# ---TestCase 4: Metadata Filtering ---
@pytest.mark.asyncio
async def test_metadata_filtering():
    """
    Verify retrieval respects metadata filters.
    """
    store = InMemoryVectorStore()
    
    # Both items identical vector, but different tags
    item_public = MemoryItem(content="Public", embedding=[0.5, 0.5], metadata={"access": "public"})
    item_private = MemoryItem(content="Private", embedding=[0.5, 0.5], metadata={"access": "private"})
    
    await store.upsert([item_public, item_private])

    # Query for ONLY private
    query = MemoryQuery(
        vector=[0.5, 0.5], 
        filter_metadata={"access": "private"}
    )
    results = await store.query(query)

    assert len(results) == 1
    assert results[0].content == "Private"
