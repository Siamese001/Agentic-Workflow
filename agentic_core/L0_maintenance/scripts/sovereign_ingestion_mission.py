#!/usr/bin/env python3
"""
Sovereign Ingestion Mission - Index all sovereign territories into vector store
"""

import asyncio
import os
from pathlib import Path
from typing import List, Dict, Optional

import hashlib
import argparse

async def load_text_file(file_path: Path) -> str:
    """Load text from supported files with encoding fallback"""
    try:
        # Try UTF-8 first, fallback to latin-1 for messy logs
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="latin-1")
    except Exception as e:
        print(f"   [!] Failed to read {file_path}: {e}")
        return ""

def chunk_text(text: str, file_path: Path) -> List[Dict]:
    """
    Chunk text into manageable pieces with metadata
    """
    chunks = []
    lines = text.split('\n')
    
    current_chunk = ""
    start_line = 0
    
    for i, line in enumerate(lines, 1):
        current_chunk += line + "\n"
        
        # Chunk every 50 lines or at file boundaries
        if i % 50 == 0 or i == len(lines):
            if current_chunk.strip():
                chunk_hash = hashlib.sha256(
                    f"{file_path}:{start_line}-{i}".encode()
                ).hexdigest()[:16]
                
                chunks.append({
                    "hash": chunk_hash,
                    "text": current_chunk.strip(),
                    "metadata": {
                        "source": str(file_path),
                        "start_line": start_line,
                        "end_line": i - 1,
                        "file_type": file_path.suffix
                    }
                })
                
                current_chunk = ""
                start_line = i
    
    return chunks

async def process_file(file_path: Path, embedder, vector_store) -> int:
    """Process a single file and add to vector store"""
    text = await load_text_file(file_path)
    
    if not text or len(text.strip()) < 10:
        return 0
    
    chunks = chunk_text(text, file_path)
    
    if not chunks:
        return 0
    
    # Generate embeddings in batches
    batch_size = 10
    total_processed = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        
        # Extract text for embedding
        texts = [chunk["text"] for chunk in batch]
        
        # Generate embeddings
        embeddings = await embedder.embed_documents(texts)
        
        # Prepare vectors for upsert
        vectors = []
        for j, embedding in enumerate(embeddings):
            chunk = batch[j]
            # CRITICAL: We must include the text in metadata for L2 retrieval
            meta = chunk["metadata"]
            meta["text"] = chunk["text"] 
            
            vectors.append({
                "id": chunk["hash"],
                "values": embedding,
                "metadata": meta
            })
        
        # Upsert to vector store
        await vector_store.upsert(vectors)
        total_processed += len(batch)
        
        print(f"   [+] Indexed {file_path.name}: chunks {i+1}-{min(i+batch_size, len(chunks))}")
    
    return total_processed

async def scan_directory(directory: Path, embedder, vector_store) -> Dict[str, int]:
    """Scan directory and process all supported files"""
    stats = {"files_processed": 0, "chunks_indexed": 0}
    
    # Supported file types
    extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml'}
    
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix in extensions:
            # Skip hidden and cache files
            if file_path.name.startswith('.') or '__pycache__' in str(file_path):
                continue
            
            chunks = await process_file(file_path, embedder, vector_store)
            if chunks > 0:
                stats["files_processed"] += 1
                stats["chunks_indexed"] += chunks
    
    return stats

async def main():
    """Main ingestion mission"""
    parser = argparse.ArgumentParser(description="Sovereign Ingestion Mission")
    parser.add_argument("--target", required=True, help="Target directory to index")
    parser.add_argument("--reset", action="store_true", help="Reset index before ingestion")
    args = parser.parse_args()
    
    target_path = Path(args.target).resolve()
    
    if not target_path.exists():
        print(f"[ERROR] Target directory does not exist: {target_path}")
        return
    
    print(f"\n[*] Sovereign Ingestion Mission: {target_path}")
    
    # Initialize components (placeholders)
    embedder = None  # Would be SubAtomicEngine or similar
    vector_store = None  # Would be Pinecone or similar
    
    if args.reset:
        print("[*] Resetting vector index...")
        # await vector_store.reset()
    
    # Scan and process
    stats = await scan_directory(target_path, embedder, vector_store)
    
    print(f"\n[✓] Ingestion Complete:")
    print(f"    Files processed: {stats['files_processed']}")
    print(f"    Chunks indexed: {stats['chunks_indexed']}")

if __name__ == "__main__":
    asyncio.run(main())
