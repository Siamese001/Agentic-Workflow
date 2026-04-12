#!/usr/bin/env python3
"""Minimal RAG pipeline test - demonstrates concept without complex imports."""

import asyncio
from pathlib import Path


class MinimalRAGPipeline:
    """Minimal RAG implementation to prove the concept."""

    def __init__(self):
        self.documents = []
        self.embeddings = {}

    def ingest(self, file_path: Path):
        """Simple document ingestion."""
        content = file_path.read_text()
        chunks = self._chunk_text(content)

        for i, chunk in enumerate(chunks):
            doc_id = f"{file_path.stem}_chunk_{i}"
            # Simple fake embedding (just hash for demo)
            embedding = hash(chunk) % 1000  # Fake embedding
            self.embeddings[doc_id] = {
                "content": chunk,
                "embedding": embedding,
                "metadata": {"source": str(file_path), "chunk": i},
            }
            self.documents.append(doc_id)

        print(f"[RAG] Ingested {len(chunks)} chunks from {file_path}")

    def _chunk_text(self, text: str, chunk_size: int = 100) -> list[str]:
        """Simple text chunking."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
        return chunks

    async def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Simple retrieval using keyword matching."""
        query_words = set(query.lower().split())
        scored = []

        for doc_id in self.documents:
            doc = self.embeddings[doc_id]
            content_words = set(doc["content"].lower().split())

            # Simple relevance score: overlap ratio
            overlap = len(query_words & content_words)
            score = overlap / len(query_words) if query_words else 0

            if score > 0:
                scored.append(
                    {
                        "id": doc_id,
                        "content": doc["content"],
                        "score": score,
                        "metadata": doc["metadata"],
                    }
                )

        # Sort by score and return top_k
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


async def test_minimal_rag():
    """Test minimal RAG pipeline."""
    print("[TEST] Starting minimal RAG pipeline test...")

    # Create test document
    test_doc = Path("test_rag_doc.txt")
    test_doc.write_text("""
    Client ABC experienced increased claim denials in Q4 2025.
    The denial rate increased from 15% to 32% due to policy changes.
    Main reasons: missing documentation, coding errors, authorization issues.
    Revenue impact: $2.3M in delayed reimbursements.
    """)

    try:
        # Initialize minimal RAG
        rag = MinimalRAGPipeline()

        # Test ingestion
        print("[TEST] Testing document ingestion...")
        rag.ingest(test_doc)

        # Test retrieval
        print("[TEST] Testing document retrieval...")
        results = await rag.retrieve(
            "Why did denied claims increase for Client ABC?",
            top_k=3,
        )

        # Verify results
        assert results, "Should retrieve some results"
        assert len(results) > 0, "Should have at least one result"

        print(f"[TEST] Retrieved {len(results)} results:")
        for i, result in enumerate(results):
            print(f"  {i + 1}. Score: {result['score']:.3f}")
            print(f"     Content: {result['content'][:100]}...")

        print("[TEST] Minimal RAG pipeline test completed successfully!")
        return True

    except Exception as e:
        print(f"[TEST] Minimal RAG pipeline test failed: {e}")
        return False
    finally:
        # Cleanup
        if test_doc.exists():
            test_doc.unlink()


if __name__ == "__main__":
    asyncio.run(test_minimal_rag())
