#!/usr/bin/env python3
"""
Ingest ADG reports from docs/reports into ChromaDB
"""

import hashlib
import logging
from pathlib import Path

import chromadb

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_adg_reports():
    """Ingest ADG reports from docs/reports into ChromaDB"""

    # ADG-related report files
    adg_report_files = [
        "docs/reports/ADG QA Workflow.md",
        "docs/reports/Anti-Pattern RCA.md",
        "docs/reports/RCA_adg_generation_hang.md",
        "docs/reports/infrastructure_gaps_four_layer_analysis.md",
        "docs/reports/infrastructure_hardening_implementation_report.md",
        "docs/reports/rca_gravity_leak_corruption_phase4.md",
        "docs/reports/system-learning-signal-enhancement-final-report.md",
    ]

    # P0-P4 final validation reports
    p_reports = [
        "docs/reports/p0_final_100_percent_validation.md",
        "docs/reports/p1_microwave_final_validation.md",
        "docs/reports/p2_microwave_final_validation.md",
        "docs/reports/p3_microwave_final_validation.md",
        "docs/reports/p4_microwave_final_validation.md",
    ]

    all_files = adg_report_files + p_reports

    # Initialize ChromaDB
    client = chromadb.PersistentClient("artifacts/chromadb")

    # Get or create collection
    try:
        collection = client.get_collection("adg_artifacts")
        logger.info("Using existing collection: adg_artifacts")
    except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
        collection = client.create_collection(
            name="adg_artifacts",
            metadata={"description": "ADG artifact reports and analyses"},
        )
        logger.info("Created new collection: adg_artifacts")

    # Process files
    chunks = []
    for filepath in all_files:
        file_path = Path(filepath)

        if not file_path.exists():
            logger.warning(f"File not found: {filepath}")
            continue

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Create chunk ID
            chunk_id = hashlib.sha256(f"{filepath}:{content}".encode()).hexdigest()

            # Determine artifact type
            if (
                "p0" in filepath
                or "p1" in filepath
                or "p2" in filepath
                or "p3" in filepath
                or "p4" in filepath
            ):
                artifact_type = "p_validation"
            elif "RCA" in filepath or "rca" in filepath:
                artifact_type = "rca"
            elif "infrastructure" in filepath:
                artifact_type = "infrastructure"
            elif "system-learning" in filepath:
                artifact_type = "system_learning"
            else:
                artifact_type = "adg_report"

            # Create chunk
            chunk = {
                "id": chunk_id,
                "content": content,
                "metadata": {
                    "file_path": str(file_path),
                    "filename": file_path.name,
                    "artifact_type": artifact_type,
                    "type": "adg_artifact",
                    "report_category": file_path.parent.name if file_path.parent != Path(".") else "root",
                },
            }

            chunks.append(chunk)
            logger.info(f"Processed: {filepath}")

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            logger.error(f"Error processing {filepath}: {e}")

    if not chunks:
        logger.error("No files processed successfully")
        return

    logger.info(f"Generated {len(chunks)} chunks from {len(all_files)} files")

    # Generate embeddings
    logger.info("Generating embeddings...")
    embeddings = [[0.0] * 1536 for _ in chunks]  # Mock embeddings
    logger.info(f"Generated {len(embeddings)} mock embeddings")

    # Ingest into ChromaDB
    logger.info("Ingesting into ChromaDB...")

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    logger.info(f"Successfully ingested {len(chunks)} chunks into ChromaDB")

    # Get collection stats
    stats = {
        "collection_name": "adg_artifacts",
        "total_chunks": collection.count(),
        "vector_dimensions": 1536,
        "vector_metric": "cosine",
    }

    logger.info(f"Collection stats: {stats}")


if __name__ == "__main__":
    ingest_adg_reports()
