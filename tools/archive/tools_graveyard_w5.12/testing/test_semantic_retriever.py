#!/usr/bin/env python3
"""
Test script for Semantic Retriever
Tests Wave 1 implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add agentic_core to path
sys.path.insert(0, str(Path(__file__).parent / "agentic_core"))

from L1_cognition.engines.semantic_retriever import RetrievalQuery, SemanticRetriever


async def test_retriever():
    """Test the semantic retriever with sample questions."""
    retriever = SemanticRetriever()

    # Get collection stats
    stats = retriever.get_collection_stats()
    print("Collection Statistics:")
    for collection, info in stats.items():
        print(f"  {collection}: {info['document_count']} documents")

    # Test questions
    questions = [
        "What does the UniversalWriteGateway do?",
        "How does the ADG scanner work?",
        "What are the L0-L6 layers?",
        "Show me the ChromaDB client implementation",
    ]

    print("\nTesting Questions:")
    for question in questions:
        print(f"\nQuestion: {question}")
        answer, results = await retriever.answer_question(question)
        print(f"Answer: {answer[:300]}...")
        print(f"Found {len(results)} results")
        if results:
            print(f"Top result from: {results[0].collection}")

    # Test direct query
    print("\nDirect Query Test:")
    query = RetrievalQuery(
        text="UniversalWriteGateway",
        collections=["repo_symbols", "repo_code_chunks"],
        max_results=5,
    )
    results = await retriever.retrieve(query)
    print(f"Found {len(results)} results for direct query")
    for i, result in enumerate(results[:3]):
        print(f"  {i + 1}. {result.collection}: {result.content[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_retriever())
