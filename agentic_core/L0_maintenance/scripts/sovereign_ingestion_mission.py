"""
Sovereign Ingestion Mission - Index all sovereign territories into vector store
"""
import argparse
import asyncio
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

async def load_text_file(file_path: Path) -> str:
    """Load text from supported files with encoding fallback"""
    try:
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return file_path.read_text(encoding='latin-1')
    except Exception as e:
        print(f'   [!] Failed to read {file_path}: {e}')
        return ''

def chunk_text(text: str, file_path: Path) -> List[Dict]:
    """
    Chunk text into manageable pieces with metadata
    """
    chunks: Any = []
    lines: Any = text.split('\n')
    current_chunk: Any = ''
    start_line: Any = 0
    for i, line in enumerate(lines, 1):
        current_chunk += line + '\n'
        if i % 50 == 0 or i == len(lines):
            if current_chunk.strip():
                chunk_hash: Any = hashlib.sha256(f'{file_path}:{start_line}-{i}'.encode()).hexdigest()[:16]
                chunks.append({'hash': chunk_hash, 'text': current_chunk.strip(), 'metadata': {'source': str(file_path), 'start_line': start_line, 'end_line': i - 1, 'file_type': file_path.suffix}})
                current_chunk: Any = ''
                start_line: Any = i
    return chunks

async def process_file(file_path: Path, embedder: Any, vector_store: Any) -> int:
    """Process a single file and add to vector store"""
    text: Any = await load_text_file(file_path)
    if not text or len(text.strip()) < 10:
        return 0
    chunks: Any = chunk_text(text, file_path)
    if not chunks:
        return 0
    batch_size: Any = 10
    total_processed: Any = 0
    for i in range(0, len(chunks), batch_size):
        batch: Any = chunks[i:i + batch_size]
        texts: Any = [chunk['text'] for chunk in batch]
        embeddings: Any = await embedder.embed_documents(texts)
        vectors: Any = []
        for j, embedding in enumerate(embeddings):
            chunk: Any = batch[j]
            meta: Any = chunk['metadata']
            meta['text'] = chunk['text']
            vectors.append({'id': chunk['hash'], 'values': embedding, 'metadata': meta})
        await vector_store.upsert(vectors)
        total_processed += len(batch)
        print(f'   [+] Indexed {file_path.name}: chunks {i + 1}-{min(i + batch_size, len(chunks))}')
    return total_processed

async def scan_directory(directory: Path, embedder: Any, vector_store: Any) -> Dict[str, int]:
    """Scan directory and process all supported files"""
    stats: Any = {'files_processed': 0, 'chunks_indexed': 0}
    extensions: Any = {'.py', '.md', '.txt', '.json', '.yaml', '.yml'}
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix in extensions:
            if file_path.name.startswith('.') or '__pycache__' in str(file_path):
                continue
            chunks: Any = await process_file(file_path, embedder, vector_store)
            if chunks > 0:
                stats['files_processed'] += 1
                stats['chunks_indexed'] += chunks
    return stats

async def main() -> Any:
    """Main ingestion mission"""
    parser: Any = argparse.ArgumentParser(description='Sovereign Ingestion Mission')
    parser.add_argument('--target', required=True, help='Target directory to index')
    parser.add_argument('--reset', action='store_true', help='Reset index before ingestion')
    args: Any = parser.parse_args()
    target_path: Any = Path(args.target).resolve()
    if not target_path.exists():
        print(f'[ERROR] Target directory does not exist: {target_path}')
        return
    print(f'\n[*] Sovereign Ingestion Mission: {target_path}')
    embedder: Any = None
    vector_store: Any = None
    if args.reset:
        print('[*] Resetting vector index...')
    stats: Any = await scan_directory(target_path, embedder, vector_store)
    print(f'\n[✓] Ingestion Complete:')
    print(f"    Files processed: {stats['files_processed']}")
    print(f"    Chunks indexed: {stats['chunks_indexed']}")
if __name__ == '__main__':
    asyncio.run(main())
