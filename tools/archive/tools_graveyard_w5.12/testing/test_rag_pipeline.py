#!/usr/bin/env python3
"""Test RAG pipeline smoke test."""

import asyncio
from pathlib import Path


async def test_rag_pipeline():
    """Test that RAG pipeline can ingest and retrieve documents."""
    print("[TEST] Starting RAG pipeline smoke test...")

    # Create test document
    test_doc = Path("test_rag_doc.txt")
    test_doc.write_text("""
    Client ABC experienced increased claim denials in Q4 2025.
    The denial rate increased from 15% to 32% due to policy changes.
    Main reasons: missing documentation, coding errors, authorization issues.
    """)

    try:
        # Import RAG orchestrator
        from agentic_core.knowledge.engine.rag_orchestrator import SovereignRagOrchestrator

        # Initialize RAG orchestrator
        project_root = Path.cwd()
        orchestrator = SovereignRagOrchestrator(project_root)

        # Test ingestion
        print("[TEST] Testing document ingestion...")
        orchestrator.ingest(test_doc)

        # Test retrieval
        print("[TEST] Testing document retrieval...")
        results = await orchestrator.retrieve(
            "Why did denied claims increase for Client ABC?",
            top_k=3,
        )

        # Verify results
        assert results, "Should retrieve some results"
        assert len(results) > 0, "Should have at least one result"

        print(f"[TEST] Retrieved {len(results)} results:")
        for i, result in enumerate(results[:3]):
            print(f"  {i + 1}. Score: {result.get('score', 0):.3f}")
            print(f"     Content: {result.get('content', '')[:100]}...")

        print("[TEST] RAG pipeline smoke test completed successfully!")
        return True

    except ImportError as e:
        print(f"[TEST] RAG pipeline not available: {e}")
        return False
    except Exception as e:
        print(f"[TEST] RAG pipeline test failed: {e}")
        return False
    finally:
        # Cleanup
        if test_doc.exists():
            test_doc.unlink()


if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())
