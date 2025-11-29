#!/usr/bin/env python3
"""
Chunking Tool
Section 5: Tool Contracts - RAG tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ChunkingTool:
    """Online chunking for execution-time document processing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.chunk_size = self.config.get("chunk_size", 5)
        self.overlap = self.config.get("overlap", 1)
        self.chunking_strategy = self.config.get("chunking_strategy", "sentence_based")
    
    def chunk_document(self, document: str) -> List[Dict[str, Any]]:
        """Chunk document into smaller segments"""
        try:
            if self.chunking_strategy == "sentence_based":
                chunks = self._sentence_chunking(document)
            else:
                chunks = self._fixed_size_chunking(document)
            
            # Add metadata to chunks
            chunked_results = []
            for i, chunk in enumerate(chunks):
                chunked_results.append({
                    "chunk_id": f"chunk_{i}",
                    "content": chunk,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
            
            logger.info(f"Document chunked into {len(chunked_results)} chunks")
            return chunked_results
            
        except Exception as e:
            logger.error(f"Document chunking failed: {e}")
            return []
    
    def _sentence_chunking(self, document: str) -> List[str]:
        """Sentence-based chunking"""
        sentences = document.split(". ")
        chunks = []
        
        for i in range(0, len(sentences), self.chunk_size):
            chunk_sentences = sentences[i:i + self.chunk_size]
            chunk = ". ".join(chunk_sentences)
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _fixed_size_chunking(self, document: str) -> List[str]:
        """Fixed-size chunking"""
        chunk_length = self.chunk_size * 100  # Approximate characters
        chunks = []
        
        for i in range(0, len(document), chunk_length - self.overlap * 50):
            chunk = document[i:i + chunk_length]
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def batch_chunk(self, documents: List[str]) -> List[List[Dict[str, Any]]]:
        """Chunk multiple documents"""
        return [self.chunk_document(doc) for doc in documents]

def create_chunking_tool(config: Optional[Dict[str, Any]] = None) -> ChunkingTool:
    """Factory function to create chunking tool instance"""
    return ChunkingTool(config)

# Re-export components
__all__ = [
    'ChunkingTool', 'create_chunking_tool'
]
