#!/usr/bin/env python3
"""
Document Ingestion Pipeline for Vector DB Population

Ingests markdown documents from docs/ directory into ChromaDB vector store
with proper chunking, metadata extraction, and OpenAI embeddings.

Usage:
    python tools/ingestion/ingest_docs.py [--source-dir docs/] [--collection-name docs]
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path

import chromadb
from openai import OpenAI

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L4_state.config.memory_store_config import MemoryStoreConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
Logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunks markdown documents by section headers with metadata preservation."""

    def __init__(self, min_chunk_size: int = 200, max_chunk_size: int = 1000):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def chunk_document(self, file_path: Path) -> list[dict]:
        """Split a markdown document into chunks with metadata."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            Logger.error(f"Failed to read {file_path}: {e}")
            return []

        # Extract document metadata
        metadata = self._extract_metadata(file_path, content)

        # Split by headers
        sections = self._split_by_headers(content)

        chunks = []
        current_chunk = ""
        current_section = "Introduction"

        for section_title, section_content in sections:
            if not section_content.strip():
                continue

            # If section is too large, split it further
            if len(section_content) > self.max_chunk_size:
                sub_chunks = self._split_large_section(section_content, current_section)
                for sub_chunk in sub_chunks:
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update(
                        {"section": current_section, "subsection": section_title, "chunk_type": "section"}
                    )
                    chunks.append({"content": sub_chunk, "metadata": chunk_metadata})
            else:
                chunk_metadata = metadata.copy()
                chunk_metadata.update(
                    {"section": current_section, "subsection": section_title, "chunk_type": "section"}
                )
                chunks.append({"content": section_content, "metadata": chunk_metadata})

            current_section = section_title

        return chunks

    def _extract_metadata(self, file_path: Path, content: str) -> dict:
        """Extract metadata from file path and content."""
        # Determine document type from path
        # Use the source directory as base for relative paths
        base_path = Path.cwd().resolve()

        try:
            relative_path = file_path.relative_to(base_path)
        except ValueError:
            # If file is not relative to cwd, use the filename only
            relative_path = file_path.name
        doc_type = "unknown"

        if "architecture" in str(relative_path):
            doc_type = "architecture"
        elif "reports" in str(relative_path):
            doc_type = "report"
        elif "specs" in str(relative_path):
            doc_type = "specification"
        elif "policies" in str(relative_path):
            doc_type = "policy"
        elif "contracts" in str(relative_path):
            doc_type = "contract"
        elif "runbooks" in str(relative_path):
            doc_type = "runbook"
        elif relative_path.name == "README.md":
            doc_type = "readme"

        # Extract layer information if present
        layer = "unknown"
        if "P0" in str(relative_path):
            layer = "P0"
        elif "P1" in str(relative_path):
            layer = "P1"
        elif "P2" in str(relative_path):
            layer = "P2"
        elif "P3" in str(relative_path):
            layer = "P3"
        elif "P4" in str(relative_path):
            layer = "P4"
        elif "L0" in str(relative_path):
            layer = "L0"
        elif "L1" in str(relative_path):
            layer = "L1"
        elif "L2" in str(relative_path):
            layer = "L2"
        elif "L3" in str(relative_path):
            layer = "L3"
        elif "L4" in str(relative_path):
            layer = "L4"
        elif "L5" in str(relative_path):
            layer = "L5"
        elif "L6" in str(relative_path):
            layer = "L6"

        # Get file modification time
        mtime = file_path.stat().st_mtime

        return {
            "doc_id": str(relative_path),
            "doc_type": doc_type,
            "layer": layer,
            "file_path": str(relative_path),
            "created_date": mtime,
            "category": self._determine_category(doc_type, layer),
        }

    def _determine_category(self, doc_type: str, layer: str) -> str:
        """Determine document category."""
        if doc_type in ["architecture", "specification"]:
            return "technical"
        elif doc_type in ["report", "policy"]:
            return "governance"
        elif doc_type == "readme":
            return "overview"
        elif doc_type == "runbook":
            return "operations"
        else:
            return "general"

    def _split_by_headers(self, content: str) -> list[tuple[str, str]]:
        """Split content by markdown headers."""
        lines = content.split("\n")
        sections = []
        current_title = "Introduction"
        current_lines = []

        for line in lines:
            header_match = self.header_pattern.match(line)
            if header_match:
                # Save previous section
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines)))

                # Start new section
                current_title = header_match.group(2).strip()
                current_lines = []
            else:
                current_lines.append(line)

        # Save last section
        if current_lines:
            sections.append((current_title, "\n".join(current_lines)))

        return sections

    def _split_large_section(self, content: str, section_title: str) -> list[str]:
        """Split a large section into smaller chunks."""
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= self.max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks


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
                    "or use --mock-embeddings for testing"
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
            batch = texts[i : i + batch_size]
            try:
                response = self.client.embeddings.create(model=self.model, input=batch)
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                Logger.info(f"Generated embeddings for batch {i // batch_size + 1}")
            except Exception as e:
                Logger.error(f"Failed to generate embeddings for batch {i // batch_size + 1}: {e}")
                # Add zero embeddings as fallback
                embeddings.extend([[0.0] * 1536] * len(batch))

        return embeddings


class VectorDBIngestor:
    """Handles ingestion into ChromaDB vector store."""

    def __init__(self, collection_name: str = "docs"):
        self.collection_name = collection_name
        self.config = MemoryStoreConfig()

        # Initialize ChromaDB client
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)

        Logger.info(f"Initialized ChromaDB collection: {collection_name}")

    def ingest_chunks(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        """Ingest chunks and embeddings into ChromaDB."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            # Generate unique ID with more entropy
            content_hash = hashlib.sha256(chunk["content"].encode()).hexdigest()[:16]
            chunk_index = hashlib.md5(
                f"{chunk['metadata']['doc_id']}_{i}_{content_hash}".encode()
            ).hexdigest()[:8]
            # Fix escape sequences for Python 3.10 compatibility
            doc_id_clean = chunk["metadata"]["doc_id"].replace("/", "_").replace("\\", "_")
            chunk_id = f"{doc_id_clean}_{content_hash}_{chunk_index}"

            ids.append(chunk_id)
            documents.append(chunk["content"])
            metadatas.append(chunk["metadata"])

        # Add to ChromaDB in batches to handle size limits
        batch_size = 5000  # ChromaDB default limit
        total_ingested = 0

        for i in range(0, len(chunks), batch_size):
            batch_ids = ids[i : i + batch_size]
            batch_documents = documents[i : i + batch_size]
            batch_metadatas = metadatas[i : i + batch_size]
            batch_embeddings = embeddings[i : i + batch_size]

            try:
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas,
                    embeddings=batch_embeddings,
                )
                batch_count = len(batch_ids)
                total_ingested += batch_count
                Logger.info(f"Successfully ingested batch {i // batch_size + 1}: {batch_count} chunks")
            except Exception as e:
                Logger.error(f"Failed to ingest batch {i // batch_size + 1}: {e}")
                # Continue with next batch instead of failing completely

        Logger.info(f"Successfully ingested {total_ingested} chunks into ChromaDB")
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


def find_markdown_files(source_dir: Path) -> list[Path]:
    """Find all markdown files in the source directory."""
    source_dir = source_dir.resolve()
    markdown_files = []

    for file_path in source_dir.rglob("*.md"):
        # Skip certain directories
        if any(skip in str(file_path) for skip in [".git", "__pycache__", "node_modules"]):
            continue
        markdown_files.append(file_path.resolve())

    return sorted(markdown_files)


def main():
    parser = argparse.ArgumentParser(description="Ingest markdown documents into ChromaDB")
    parser.add_argument("--source-dir", default="docs", help="Source directory containing markdown files")
    parser.add_argument("--collection-name", default="docs", help="ChromaDB collection name")
    parser.add_argument("--dry-run", action="store_true", help="Preview without ingesting")
    parser.add_argument("--mock-embeddings", action="store_true", help="Use mock embeddings for testing")
    parser.add_argument("--limit", type=int, help="Limit number of files to process (for testing)")

    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        Logger.error(f"Source directory {source_dir} does not exist")
        return 1

    # Find markdown files
    markdown_files = find_markdown_files(source_dir)
    if args.limit:
        markdown_files = markdown_files[: args.limit]

    Logger.info(f"Found {len(markdown_files)} markdown files to process")

    # Initialize components
    chunker = DocumentChunker()
    embedding_generator = EmbeddingGenerator(mock_embeddings=args.mock_embeddings)
    ingestor = VectorDBIngestor(args.collection_name)

    # Process documents
    all_chunks = []
    total_files = 0

    for file_path in markdown_files:
        Logger.info(f"Processing: {file_path}")
        chunks = chunker.chunk_document(file_path)
        all_chunks.extend(chunks)
        total_files += 1

        if len(chunks) == 0:
            Logger.warning(f"No chunks generated from {file_path}")

    Logger.info(f"Generated {len(all_chunks)} chunks from {total_files} files")

    if args.dry_run:
        Logger.info("DRY RUN - Not ingesting into ChromaDB")
        for chunk in all_chunks[:3]:  # Show first 3 chunks as preview
            Logger.info(f"Preview chunk: {chunk['metadata']['doc_id']}")
        return 0

    # Generate embeddings
    Logger.info("Generating embeddings...")
    texts = [chunk["content"] for chunk in all_chunks]
    embeddings = embedding_generator.generate_embeddings(texts)

    # Ingest into ChromaDB
    Logger.info("Ingesting into ChromaDB...")
    ingested_count = ingestor.ingest_chunks(all_chunks, embeddings)

    # Show final stats
    stats = ingestor.get_collection_stats()
    Logger.info(f"Ingestion complete: {ingested_count} chunks ingested")
    Logger.info(f"Collection stats: {json.dumps(stats, indent=2)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
