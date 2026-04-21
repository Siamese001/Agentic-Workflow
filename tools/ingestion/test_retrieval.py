#!/usr/bin/env python3
"""
Test script to validate document retrieval from ChromaDB
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import chromadb


def test_retrieval():
    """Test basic retrieval from the populated ChromaDB collection."""

    # Initialize ChromaDB with persistent storage
    persist_dir = Path("artifacts/chromadb")
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(name="docs")

    # Get collection stats
    count = collection.count()
    print(f"Collection 'docs' contains {count} chunks")

    if count == 0:
        print("❌ No chunks found in collection")
        return False

    # Test a sample query
    query_text = "How does ADG work?"
    print(f"\nTesting query: '{query_text}'")

    # Generate a simple mock embedding for testing
    import random

    query_embedding = [[random.uniform(-1, 1) for _ in range(1536)]]

    try:
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=5,
        )

        print(f"✅ Retrieved {len(results['ids'][0])} results")

        # Show first few results
        for i, (doc_id, document, metadata) in enumerate(
            zip(results["ids"][0][:3], results["documents"][0][:3], results["metadatas"][0][:3])
        ):
            print(f"\nResult {i + 1}:")
            print(f"  ID: {doc_id}")
            print(f"  Type: {metadata.get('doc_type', 'unknown')}")
            print(f"  Layer: {metadata.get('layer', 'unknown')}")
            print(f"  Category: {metadata.get('category', 'unknown')}")
            print(f"  Preview: {document[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False


if __name__ == "__main__":
    success = test_retrieval()
    sys.exit(0 if success else 1)
