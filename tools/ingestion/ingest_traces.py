#!/usr/bin/env python3
"""
Healing Traces Ingestion Pipeline for Vector DB Population

Ingests JSONL healing traces from data/corpus/healing_contexts_corpus.jsonl
into ChromaDB vector store with proper metadata extraction and embeddings.

Usage:
    python tools/ingestion/ingest_traces.py [--source-file data/corpus/healing_contexts_corpus.jsonl] [--collection-name traces]
"""

import argparse
import hashlib
import json
import logging
import os
import sys
from pathlib import Path

import chromadb
from openai import OpenAI

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L4_state.config.memory_store_config import MemoryStoreConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
Logger = logging.getLogger(__name__)


class TraceChunker:
    """Chunks JSONL healing traces for vector storage."""

    def __init__(self, max_trace_length: int = 2000):
        self.max_trace_length = max_trace_length

    def chunk_trace_file(self, file_path: Path) -> list[dict]:
        """Process JSONL file and convert each trace to a chunk."""
        chunks = []

        try:
            with open(file_path, encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        trace_data = json.loads(line)
                        chunk = self._process_trace(trace_data, line_num)
                        if chunk:
                            chunks.append(chunk)
                    except json.JSONDecodeError as e:
                        Logger.warning(f"Invalid JSON on line {line_num}: {e}")
                        continue

                    # Progress reporting
                    if line_num % 10000 == 0:
                        Logger.info(f"Processed {line_num} traces...")

        except Exception as e:
            Logger.error(f"Failed to read trace file {file_path}: {e}")
            return []

        Logger.info(f"Generated {len(chunks)} trace chunks")
        return chunks

    def _process_trace(self, trace_data: dict, line_num: int) -> dict | None:
        """Process a single trace and convert to chunk format."""
        # Extract key fields with fallbacks
        trace_id = trace_data.get('trace_id', f'trace_{line_num}')
        namespace = trace_data.get('namespace', 'unknown')
        created_utc = trace_data.get('created_utc', '')
        content_hash = trace_data.get('content_hash', '')

        # Build trace content for embedding
        content_parts = []

        # Add trace context
        if 'context' in trace_data:
            context = trace_data['context']
            if isinstance(context, dict):
                content_parts.append(f"Context: {json.dumps(context, separators=(',', ':'))}")
            else:
                content_parts.append(f"Context: {context}")

        # Add trace data
        if 'trace' in trace_data:
            trace = trace_data['trace']
            if isinstance(trace, dict):
                content_parts.append(f"Trace: {json.dumps(trace, separators=(',', ':'))}")
            else:
                content_parts.append(f"Trace: {trace}")

        # Add outcome if present
        if 'outcome' in trace_data:
            outcome = trace_data['outcome']
            if isinstance(outcome, dict):
                content_parts.append(f"Outcome: {json.dumps(outcome, separators=(',', ':'))}")
            else:
                content_parts.append(f"Outcome: {outcome}")

        # Add any other fields
        for key, value in trace_data.items():
            if key not in ['trace_id', 'namespace', 'created_utc', 'content_hash', 'context', 'trace', 'outcome']:
                content_parts.append(f"{key}: {value}")

        content = '\n'.join(content_parts)

        # Truncate if too long
        if len(content) > self.max_trace_length:
            content = content[:self.max_trace_length] + "..."

        # Determine trace type from content or structure
        trace_type = self._determine_trace_type(trace_data, content)

        # Create metadata
        metadata = {
            'trace_id': trace_id,
            'namespace': namespace,
            'created_utc': created_utc,
            'content_hash': content_hash,
            'trace_type': trace_type,
            'line_number': line_num,
            'chunk_type': 'trace',
        }

        # Add additional metadata if available
        if 'error_type' in trace_data:
            metadata['error_type'] = trace_data['error_type']
        if 'healing_action' in trace_data:
            metadata['healing_action'] = trace_data['healing_action']
        if 'agent_name' in trace_data:
            metadata['agent_name'] = trace_data['agent_name']
        if 'layer' in trace_data:
            metadata['layer'] = trace_data['layer']

        return {
            'content': content,
            'metadata': metadata,
        }

    def _determine_trace_type(self, trace_data: dict, content: str) -> str:
        """Determine the type of trace based on content and structure."""
        # Check for explicit type field
        if 'type' in trace_data:
            return str(trace_data['type'])

        # Check for error-related traces
        if any(key in trace_data for key in ['error', 'exception', 'failure']):
            if 'healing' in content.lower():
                return 'healing_error'
            return 'error'

        # Check for healing-related traces
        if any(key in trace_data for key in ['healing', 'repair', 'fix', 'recover']):
            return 'healing_action'

        # Check for execution traces
        if any(key in trace_data for key in ['execution', 'run', 'invoke', 'call']):
            return 'execution_trace'

        # Check for validation traces
        if any(key in trace_data for key in ['validate', 'check', 'verify', 'test']):
            return 'validation_trace'

        # Default type
        return 'general_trace'


class EmbeddingGenerator:
    """Generates embeddings using OpenAI API or mock embeddings for testing."""

    def __init__(self, model: str = "text-embedding-ada-002", mock_embeddings: bool = False):
        self.model = model
        self.mock_embeddings = mock_embeddings

        if not mock_embeddings:
            # Check for OpenAI API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY environment variable not set. "
                    "Please set it with: export OPENAI_API_KEY=your_key_here "
                    "or use --mock-embeddings for testing",
                )

            self.client = OpenAI(api_key=api_key)
        else:
            Logger.info("Using mock embeddings for testing")

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if self.mock_embeddings:
            # Generate mock embeddings (1536-dimensional vectors)
            Logger.info(f"Generating {len(texts)} mock embeddings")
            import random
            return [[random.uniform(-1, 1) for _ in range(1536)] for _ in texts]

        embeddings = []

        # Process in batches to handle rate limits
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                Logger.info(f"Generated embeddings for batch {i//batch_size + 1}")
            except Exception as e:
                Logger.error(f"Failed to generate embeddings for batch {i//batch_size + 1}: {e}")
                # Add zero embeddings as fallback
                embeddings.extend([[0.0] * 1536] * len(batch))

        return embeddings


class VectorDBIngestor:
    """Handles ingestion into ChromaDB vector store."""

    def __init__(self, collection_name: str = "traces", persist_directory: str = None):
        self.collection_name = collection_name
        self.config = MemoryStoreConfig()

        # Initialize ChromaDB client with persistent storage
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            # Default to artifacts/chromadb for persistence
            persist_dir = Path("artifacts/chromadb")
            persist_dir.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(persist_dir))

        try:
            self.collection = self.client.get_or_create_collection(name=collection_name)
            Logger.info(f"Initialized ChromaDB collection: {collection_name}")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            Logger.error(f"Failed to initialize ChromaDB collection '{collection_name}': {e}")
            raise

    def ingest_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        """Ingest chunks and embeddings into ChromaDB."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            # Generate unique ID
            trace_id = chunk['metadata'].get('trace_id', f'trace_{i}')
            content_hash = hashlib.sha256(chunk["content"].encode()).hexdigest()[:16]
            chunk_id = f"{trace_id}_{content_hash}"

            ids.append(chunk_id)
            documents.append(chunk["content"])
            metadatas.append(chunk["metadata"])

        # Add to ChromaDB in batches to handle size limits
        batch_size = 5000  # ChromaDB default limit
        total_ingested = 0

        for i in range(0, len(chunks), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_documents = documents[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]

            try:
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas,
                    embeddings=batch_embeddings,
                )
                batch_count = len(batch_ids)
                total_ingested += batch_count
                Logger.info(f"Successfully ingested batch {i//batch_size + 1}: {batch_count} traces")
            except Exception as e:
                Logger.error(f"Failed to ingest batch {i//batch_size + 1}: {e}")
                # Continue with next batch instead of failing completely

        Logger.info(f"Successfully ingested {total_ingested} traces into ChromaDB")
        return total_ingested

    def get_collection_stats(self) -> dict:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "vector_dimensions": self.config.VECTOR_DIMENSIONS,
                "vector_metric": self.config.VECTOR_METRIC,
            }
        except Exception as e:
            Logger.error(f"Failed to get collection stats: {e}")
            return {}


def count_traces_in_file(file_path: Path) -> int:
    """Count the number of traces in a JSONL file."""
    count = 0
    try:
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
    except Exception as e:
        Logger.error(f"Failed to count traces in {file_path}: {e}")
        return 0

    return count


def main():
    parser = argparse.ArgumentParser(description="Ingest healing traces into ChromaDB")
    parser.add_argument("--source-file", default="data/corpus/healing_contexts_corpus.jsonl",
                       help="Source JSONL file containing healing traces")
    parser.add_argument("--collection-name", default="traces", help="ChromaDB collection name")
    parser.add_argument("--dry-run", action="store_true", help="Preview without ingesting")
    parser.add_argument("--mock-embeddings", action="store_true", help="Use mock embeddings for testing")
    parser.add_argument("--limit", type=int, help="Limit number of traces to process (for testing)")

    args = parser.parse_args()

    source_file = Path(args.source_file)
    if not source_file.exists():
        Logger.error(f"Source file {source_file} does not exist")
        return 1

    # Count total traces
    total_traces = count_traces_in_file(source_file)
    Logger.info(f"Found {total_traces} traces in {source_file}")

    # Initialize components
    chunker = TraceChunker()
    embedding_generator = EmbeddingGenerator(mock_embeddings=args.mock_embeddings)
    ingestor = VectorDBIngestor(args.collection_name)

    # Process traces
    Logger.info("Processing traces...")
    chunks = chunker.chunk_trace_file(source_file)

    if args.limit:
        chunks = chunks[:args.limit]
        Logger.info(f"Limited to {len(chunks)} traces for testing")

    if args.dry_run:
        Logger.info("DRY RUN - Not ingesting into ChromaDB")
        for chunk in chunks[:3]:  # Show first 3 chunks as preview
            Logger.info(f"Preview trace: {chunk['metadata']['trace_id']} - {chunk['metadata']['trace_type']}")
        return 0

    # Generate embeddings
    Logger.info("Generating embeddings...")
    texts = [chunk["content"] for chunk in chunks]
    embeddings = embedding_generator.generate_embeddings(texts)

    # Ingest into ChromaDB
    Logger.info("Ingesting into ChromaDB...")
    ingested_count = ingestor.ingest_chunks(chunks, embeddings)

    # Show final stats
    stats = ingestor.get_collection_stats()
    Logger.info(f"Ingestion complete: {ingested_count} traces ingested")
    Logger.info(f"Collection stats: {json.dumps(stats, indent=2)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
