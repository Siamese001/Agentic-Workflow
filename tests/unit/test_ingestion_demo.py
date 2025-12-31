"""Demonstration test: Apply semantic chunking to the semantic_cache.py file."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path
from agentic_core.L0_maintenance.scripts.sovereign_ingestion_mission import (
    chunk_text,
    ChunkType,
)


def test_chunk_semantic_cache_file():
    """Test semantic chunking on the actual semantic_cache.py file."""
    cache_file = Path("C:/Git/Agentic-Workflow/agentic_core/runtime/shared_runtime/semantic_cache.py")
    
    if not cache_file.exists():
        print(f"File not found: {cache_file}")
        return
    
    text = cache_file.read_text(encoding='utf-8')
    chunks = chunk_text(text, cache_file)
    
    print(f"\n{'='*80}")
    print(f"Semantic Chunking Demo: {cache_file.name}")
    print(f"{'='*80}\n")
    print(f"Total chunks: {len(chunks)}\n")
    
    # Group by chunk type
    by_type = {}
    for chunk in chunks:
        chunk_type = chunk['metadata']['chunk_type']
        by_type.setdefault(chunk_type, []).append(chunk)
    
    print("Chunk Type Distribution:")
    for chunk_type, type_chunks in sorted(by_type.items()):
        print(f"  {chunk_type:15s}: {len(type_chunks):3d} chunks")
    
    print(f"\n{'='*80}")
    print("Sample Chunks (first 5):")
    print(f"{'='*80}\n")
    
    for i, chunk in enumerate(chunks[:5], 1):
        meta = chunk['metadata']
        print(f"{i}. [{meta['chunk_type']}] {meta['name']}")
        print(f"   Lines {meta['start_line']}-{meta['end_line']}")
        if meta.get('parent'):
            print(f"   Parent: {meta['parent']}")
        if meta.get('docstring'):
            doc_preview = meta['docstring'][:80].replace('\n', ' ')
            print(f"   Docstring: {doc_preview}...")
        print(f"   Text preview: {chunk['text'][:100].replace(chr(10), ' ')}...")
        print()
    
    # Assertions
    assert len(chunks) > 0, "Should have chunks"
    # Note: Module docstrings may be captured in import block if they appear before imports
    assert any(c['metadata']['chunk_type'] == ChunkType.IMPORT_BLOCK.value for c in chunks), "Should have imports"
    assert any(c['metadata']['chunk_type'] == ChunkType.CLASS.value for c in chunks), "Should have classes"
    assert any(c['metadata']['chunk_type'] == ChunkType.FUNCTION.value for c in chunks), "Should have functions"
    
    # Check that classes have docstrings in metadata
    class_chunks = [c for c in chunks if c['metadata']['chunk_type'] == ChunkType.CLASS.value]
    assert any(c['metadata'].get('docstring') for c in class_chunks), "Classes should have docstrings"
    
    # Check specific expected chunks
    chunk_names = [c['metadata']['name'] for c in chunks]
    assert 'SemanticCache' in chunk_names, "Should find SemanticCache class"
    assert 'CacheEntry' in chunk_names, "Should find CacheEntry class"
    assert 'create_semantic_cache' in chunk_names, "Should find create_semantic_cache function"
    
    print(f"{'='*80}")
    print("✓ All assertions passed!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_chunk_semantic_cache_file()
