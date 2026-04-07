"""
Semantic Retriever for L1 Cognition
Retrieves relevant context from ChromaDB semantic memory layer.
"""

import asyncio
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add L4_state to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "L4_state"))

from client.chroma_client import SovereignChromaClient

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from semantic retrieval."""
    content: str
    metadata: dict[str, Any]
    score: float
    collection: str


@dataclass
class RetrievalQuery:
    """Query for semantic retrieval."""
    text: str
    collections: list[str]
    filters: dict[str, Any] | None = None
    max_results: int = 10


class SemanticRetriever:
    """
    Semantic retriever for L1 cognition layer.

    Provides intelligent retrieval from ChromaDB semantic memory
    with query routing, multi-collection fusion, and reranking.
    """

    def __init__(self, chroma_persist_dir: str = "artifacts/chromadb"):
        """
        Initialize semantic retriever.

        Args:
            chroma_persist_dir: ChromaDB persistence directory
        """
        self.chroma = SovereignChromaClient(persist_dir=chroma_persist_dir)

        # Collection routing rules
        self.collection_routing = {
            "code_questions": ["repo_code_chunks", "repo_symbols"],
            "architecture": ["repo_arch_docs", "repo_symbols"],
            "implementation": ["repo_code_chunks", "repo_symbols"],
            "documentation": ["repo_arch_docs"],
            "general": ["repo_code_chunks", "repo_symbols", "repo_arch_docs"]
        }

        # Available collections
        self.available_collections = self.chroma.list_collections()
        logger.info(f"Semantic retriever initialized with collections: {self.available_collections}")

    async def retrieve(self, query: RetrievalQuery) -> list[RetrievalResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: RetrievalQuery object with text and parameters

        Returns:
            List of RetrievalResult objects
        """
        # Route query to appropriate collections
        target_collections = self._route_query(query)

        # Filter to available collections
        target_collections = [c for c in target_collections if c in self.available_collections]

        if not target_collections:
            logger.warning(f"No available collections for query: {query.text}")
            return []

        # Execute parallel queries
        results = await self._parallel_query(query, target_collections)

        # Fuse and rank results
        fused_results = self._fuse_results(results)

        logger.info(f"Retrieved {len(fused_results)} results for query: {query.text[:50]}...")
        return fused_results

    def _route_query(self, query: RetrievalQuery) -> list[str]:
        """Route query to appropriate collections based on content."""
        query_lower = query.text.lower()

        # Explicit collection specification
        if query.collections:
            return query.collections

        # Keyword-based routing
        if any(keyword in query_lower for keyword in ["function", "class", "method", "code", "implement"]):
            return self.collection_routing["code_questions"]
        elif any(keyword in query_lower for keyword in ["architecture", "design", "pattern", "structure"]):
            return self.collection_routing["architecture"]
        elif any(keyword in query_lower for keyword in ["what", "how", "explain", "describe"]):
            return self.collection_routing["general"]
        elif any(keyword in query_lower for keyword in ["documentation", "readme", "guide"]):
            return self.collection_routing["documentation"]
        else:
            return self.collection_routing["general"]

    async def _parallel_query(self, query: RetrievalQuery, collections: list[str]) -> dict[str, list[RetrievalResult]]:
        """Execute parallel queries across collections."""
        results = {}

        # Create tasks for parallel execution
        tasks = []
        for collection in collections:
            task = self._query_collection(collection, query)
            tasks.append((collection, task))

        # Execute tasks concurrently
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

        # Process results
        for (collection, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                logger.error(f"Query failed for collection {collection}: {result}")
                results[collection] = []
            else:
                results[collection] = result

        return results

    async def _query_collection(self, collection: str, query: RetrievalQuery) -> list[RetrievalResult]:
        """Query a single collection."""
        try:
            # Query ChromaDB
            chroma_results = self.chroma.query(
                collection_name=collection,
                query_texts=[query.text],
                n_results=query.max_results,
                where=query.filters
            )

            # Convert to RetrievalResult objects
            results = []
            for i in range(len(chroma_results['ids'][0])):
                result = RetrievalResult(
                    content=chroma_results['documents'][0][i],
                    metadata=chroma_results['metadatas'][0][i],
                    score=1.0 - chroma_results['distances'][0][i],  # Convert distance to similarity
                    collection=collection
                )
                results.append(result)

            return results

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Failed to query collection {collection}: {e}")
            raise

    def _fuse_results(self, collection_results: dict[str, list[RetrievalResult]]) -> list[RetrievalResult]:
        """
        Fuse results from multiple collections using Reciprocal Rank Fusion (RRF).

        Args:
            collection_results: Results per collection

        Returns:
            Fused and ranked results
        """
        all_results = []

        # Collect all results with collection info
        for collection, results in collection_results.items():
            for result in results:
                result.collection = collection
                all_results.append(result)

        if not all_results:
            return []

        # Sort by score (descending)
        all_results.sort(key=lambda x: x.score, reverse=True)

        # Apply simple reranking based on collection priority
        collection_priority = {
            "repo_symbols": 1.1,
            "repo_code_chunks": 1.05,
            "repo_arch_docs": 1.0
        }

        for result in all_results:
            priority = collection_priority.get(result.collection, 1.0)
            result.score *= priority

        # Final sort and limit
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:20]  # Return top 20 results

    async def answer_question(self, question: str) -> tuple[str, list[RetrievalResult]]:
        """
        Answer a question using semantic retrieval.

        Args:
            question: Question to answer

        Returns:
            Tuple of (answer, retrieval_results)
        """
        # Create query
        query = RetrievalQuery(
            text=question,
            collections=[],  # Auto-route
            max_results=10
        )

        # Retrieve results
        results = await self.retrieve(query)

        if not results:
            return "I couldn't find relevant information to answer your question.", []

        # Format answer with citations
        answer_parts = ["Based on the retrieved information:\n"]

        for i, result in enumerate(results[:5]):  # Use top 5 results
            source = f"{result.collection}:{result.metadata.get('file_path', 'unknown')}"
            answer_parts.append(f"{i+1}. {result.content[:200]}...")
            answer_parts.append(f"   Source: {source} (score: {result.score:.2f})")

        answer = "\n".join(answer_parts)
        return answer, results

    def get_collection_stats(self) -> dict[str, Any]:
        """Get statistics for all collections."""
        stats = {}
        for collection in self.available_collections:
            stats[collection] = self.chroma.get_collection_stats(collection)
        return stats


# Example usage and testing
async def main():
    """Test the semantic retriever."""
    retriever = SemanticRetriever()

    # Test questions
    questions = [
        "What does the UniversalWriteGateway do?",
        "How does the ADG scanner work?",
        "What are the L0-L6 layers?",
        "Show me the ChromaDB client implementation"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        answer, results = await retriever.answer_question(question)
        print(f"Answer: {answer}")
        print(f"Found {len(results)} results")


if __name__ == "__main__":
    asyncio.run(main())
