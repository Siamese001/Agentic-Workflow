"""Tests for Chunking Modes implementation."""

import pytest


# Lazy imports to avoid collection-time conflicts
@pytest.fixture
def chunking_classes():
    from agentic_core.knowledge.chunking.chunking_modes import (
        Chunk,
        ChunkingEngine,
        FixedTokenChunker,
        OverlapWindowChunker,
        SectionAwareChunker,
        SemanticObjectChunker,
        chunk_document,
    )

    return (
        Chunk,
        ChunkingEngine,
        FixedTokenChunker,
        OverlapWindowChunker,
        SectionAwareChunker,
        SemanticObjectChunker,
        chunk_document,
    )


class TestChunkingModes:
    """Test chunking strategies."""

    def test_fixed_token_chunker(self, chunking_classes):
        """Test fixed token chunking."""
        _, _, FixedTokenChunker, _, _, _, _ = chunking_classes
        chunker = FixedTokenChunker(tokens_per_chunk=10, overlap_tokens=2)

        text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12 word13 word14"
        chunks = chunker.chunk(text, "test_doc")

        assert len(chunks) > 1
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.chunk_type == "fixed_token" for chunk in chunks)
        assert chunks[0].id.startswith("test_doc_fixed_")

    def test_overlap_window_chunker(self):
        """Test overlap window chunking."""
        chunker = OverlapWindowChunker(window_size=50, stride=25)

        # Create a long text that will definitely create multiple chunks
        text = " ".join([f"word{i}" for i in range(200)])  # 200 words
        chunks = chunker.chunk(text, "test_doc")

        # Should create multiple chunks with overlap
        assert len(chunks) > 1
        assert all(chunk.chunk_type == "overlap_window" for chunk in chunks)
        assert chunks[0].id.startswith("test_doc_overlap_")

    def test_section_aware_chunker(self):
        """Test section-aware chunking."""
        chunker = SectionAwareChunker()

        text = "# Section 1\nContent of section 1.\n## Section 2\nContent of section 2."
        chunks = chunker.chunk(text, "test_doc")

        assert len(chunks) >= 2
        assert all(chunk.chunk_type == "section_aware" for chunk in chunks)

        # Check heading metadata
        headings = [chunk.metadata.get("heading") for chunk in chunks]
        assert any("Section 1" in str(h) for h in headings)

    def test_semantic_object_chunker(self):
        """Test semantic object chunking."""
        chunker = SemanticObjectChunker(target_tokens=20)

        text = "This is a sentence. This is another sentence. A third sentence is here."
        chunks = chunker.chunk(text, "test_doc")

        assert len(chunks) >= 1
        assert all(chunk.chunk_type == "semantic_object" for chunk in chunks)

    def test_chunking_engine_auto_select(self):
        """Test automatic strategy selection."""
        engine = ChunkingEngine()

        # Markdown text should select section_aware
        markdown_text = "# Heading\nContent under heading."
        chunks = engine.chunk(markdown_text, "test_doc")
        assert chunks[0].chunk_type == "section_aware"

        # Code text should select semantic_object
        code_text = "```python\ndef func():\n    pass\n```"
        chunks = engine.chunk(code_text, "test_doc")
        assert chunks[0].chunk_type == "semantic_object"

    def test_chunking_engine_explicit_strategy(self):
        """Test explicit strategy selection."""
        engine = ChunkingEngine()

        text = "This is test content for chunking."
        chunks = engine.chunk(text, "test_doc", strategy="fixed_token")
        assert chunks[0].chunk_type == "fixed_token"

    def test_chunk_batch_processing(self):
        """Test batch document processing."""
        engine = ChunkingEngine()

        documents = [
            ("doc1", "Content for document 1."),
            ("doc2", "Content for document 2."),
        ]

        results = engine.chunk_batch(documents)

        assert "doc1" in results
        assert "doc2" in results
        assert len(results["doc1"]) > 0
        assert len(results["doc2"]) > 0

    def test_convenience_functions(self):
        """Test convenience functions."""
        text = "Test content for convenience function."
        chunks = chunk_document(text, "test_doc", "fixed_token")

        assert len(chunks) > 0
        assert chunks[0].id.startswith("test_doc_fixed_")
        assert chunks[0].chunk_type == "fixed_token"

    def test_chunk_metadata(self):
        """Test chunk metadata preservation."""
        chunker = FixedTokenChunker()

        text = "Test content with metadata."
        chunks = chunker.chunk(text, "test_doc")

        assert "strategy" in chunks[0].metadata
        assert chunks[0].metadata["strategy"] == "fixed_token"

    def test_empty_text_handling(self):
        """Test empty text handling."""
        chunker = FixedTokenChunker()

        chunks = chunker.chunk("", "test_doc")
        assert len(chunks) == 0

    def test_very_short_text(self):
        """Test very short text handling."""
        chunker = FixedTokenChunker(tokens_per_chunk=50)

        chunks = chunker.chunk("Short", "test_doc")
        assert len(chunks) == 1
        assert chunks[0].content == "Short"
