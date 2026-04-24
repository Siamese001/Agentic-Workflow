#!/usr/bin/env python3
"""
Test script to validate trace retrieval from ChromaDB
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import chromadb
from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str


def test_trace_retrieval():
    """Test basic trace retrieval from the populated ChromaDB collection."""

    # Initialize ChromaDB with persistent storage
    persist_dir = Path(canonical_persist_dir_str())
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(name="traces")

    # Get collection stats
    count = collection.count()
    print(f"Collection 'traces' contains {count} trace chunks")

    if count == 0:
        print("❌ No trace chunks found in collection")
        return False

    # Test a sample query
    query_text = "Similar to trace_000042"
    print(f"\nTesting query: '{query_text}'")

    # Generate a simple mock embedding for testing
    import random

    query_embedding = [[random.uniform(-1, 1) for _ in range(1536)]]

    try:
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=5,
        )

        print(f"✅ Retrieved {len(results['ids'][0])} trace results")

        # Show first few results
        for i, (doc_id, document, metadata) in enumerate(
            zip(results["ids"][0][:3], results["documents"][0][:3], results["metadatas"][0][:3])
        ):
            print(f"\nResult {i + 1}:")
            print(f"  ID: {doc_id}")
            print(f"  Trace ID: {metadata.get('trace_id', 'unknown')}")
            print(f"  Type: {metadata.get('trace_type', 'unknown')}")
            print(f"  Namespace: {metadata.get('namespace', 'unknown')}")
            print(f"  Line: {metadata.get('line_number', 'unknown')}")
            print(f"  Preview: {document[:150]}...")

        return True

    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False


def test_trace_type_filtering():
    """Test filtering traces by type."""

    # Initialize ChromaDB
    persist_dir = Path(canonical_persist_dir_str())
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(name="traces")

    # Get all traces to analyze types
    try:
        # Get a sample of traces
        results = collection.get(limit=100)

        trace_types = {}
        for metadata in results["metadatas"]:
            trace_type = metadata.get("trace_type", "unknown")
            trace_types[trace_type] = trace_types.get(trace_type, 0) + 1

        print("\n📊 Trace Type Distribution (sample of 100):")
        for trace_type, count in sorted(trace_types.items()):
            print(f"  {trace_type}: {count}")

        return True

    except Exception as e:
        print(f"❌ Failed to analyze trace types: {e}")
        return False


if __name__ == "__main__":
    print("=== Trace Retrieval Test ===")
    success1 = test_trace_retrieval()

    print("\n=== Trace Type Analysis ===")
    success2 = test_trace_type_filtering()

    success = success1 and success2
    print(f"\n{'✅ All tests passed' if success else '❌ Some tests failed'}")
    sys.exit(0 if success else 1)
