#!/usr/bin/env python3
"""
Ingest ADG artifact files into ChromaDB
"""

import hashlib
import logging
from pathlib import Path

import chromadb

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_adg_files():
    """Ingest ADG-related files into ChromaDB"""

    # List of ADG-related files to ingest
    adg_files = [
        "ADG_BURNDOWN_STRATEGY.md",
        "ADG_VIOLATIONS_ANALYSIS.md",
        "ADG_VIOLATION_BURNDOWN_WAVE1.md",
        "ADG_VIOLATION_WATERFALL_CORRECTED.md",
        "ADG_VIOLATION_WATERFALL_PLAN.md",
        "adg_archiving_fix_summary.md",
        "adg_final_gap_analysis.md",
        "adg_process_summary.md",
        "dependency_graph_adg_final_gap.md",
        "dependency_graph_analysis.md"
    ]

    # Initialize ChromaDB
    client = chromadb.PersistentClient("artifacts/chromadb")

    # Get or create collection
    try:
        collection = client.get_collection("adg_artifacts")
        logger.info("Using existing collection: adg_artifacts")
    except:
        collection = client.create_collection(
            name="adg_artifacts",
            metadata={"description": "ADG artifact reports and analyses"}
        )
        logger.info("Created new collection: adg_artifacts")

    # Process files
    chunks = []
    for filepath in adg_files:
        file_path = Path(filepath)

        if not file_path.exists():
            logger.warning(f"File not found: {filepath}")
            continue

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Create chunk ID
            chunk_id = hashlib.sha256(f"{filepath}:{content}".encode()).hexdigest()

            # Create chunk
            chunk = {
                'id': chunk_id,
                'content': content,
                'metadata': {
                    'file_path': str(file_path),
                    'filename': file_path.name,
                    'artifact_type': 'adg_report',
                    'type': 'adg_artifact'
                }
            }

            chunks.append(chunk)
            logger.info(f"Processed: {filepath}")

        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    if not chunks:
        logger.error("No files processed successfully")
        return

    logger.info(f"Generated {len(chunks)} chunks from {len(adg_files)} files")

    # Generate embeddings
    logger.info("Generating embeddings...")
    embeddings = [[0.0] * 1536 for _ in chunks]  # Mock embeddings
    logger.info(f"Generated {len(embeddings)} mock embeddings")

    # Ingest into ChromaDB
    logger.info("Ingesting into ChromaDB...")

    ids = [chunk['id'] for chunk in chunks]
    documents = [chunk['content'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    logger.info(f"Successfully ingested {len(chunks)} chunks into ChromaDB")

    # Get collection stats
    stats = {
        "collection_name": "adg_artifacts",
        "total_chunks": collection.count(),
        "vector_dimensions": 1536,
        "vector_metric": "cosine"
    }

    logger.info(f"Collection stats: {stats}")

if __name__ == "__main__":
    ingest_adg_files()
