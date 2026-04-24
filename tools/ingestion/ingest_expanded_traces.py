#!/usr/bin/env python3
"""
Ingest expanded trace sources into ChromaDB traces collection
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

import chromadb
from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_jsonl_traces():
    """Ingest JSONL trace files"""

    # JSONL trace files with metadata
    jsonl_files = [
        {
            "path": "artifacts/healing/healing_events.jsonl",
            "trace_type": "healing_event",
            "namespace": "healing_contexts",
            "description": "Healing event traces",
        },
        {
            "path": "artifacts/hitl/decisions.jsonl",
            "trace_type": "hitl_decision",
            "namespace": "human_in_loop",
            "description": "Human-in-the-loop decision traces",
        },
        {
            "path": "artifacts/outputs/classification_experience.jsonl",
            "trace_type": "classification_trace",
            "namespace": "classification",
            "description": "Classification experience traces",
        },
        {
            "path": "artifacts/outputs/healing_experience.jsonl",
            "trace_type": "healing_experience",
            "namespace": "healing_contexts",
            "description": "Healing experience traces",
        },
        {
            "path": "artifacts/outputs/prompt_injection_attacks_200.jsonl",
            "trace_type": "security_trace",
            "namespace": "security",
            "description": "Prompt injection attack traces",
        },
        {
            "path": "artifacts/outputs/tool_use_ground_truth_1000.jsonl",
            "trace_type": "tool_usage",
            "namespace": "tool_execution",
            "description": "Tool usage ground truth traces",
        },
    ]

    # Initialize ChromaDB
    client = chromadb.PersistentClient(canonical_persist_dir_str())
    collection = client.get_collection("traces")

    # Process each JSONL file
    total_chunks = 0
    for file_info in jsonl_files:
        file_path = Path(file_info["path"])

        if not file_path.exists():
            logger.warning(f"File not found: {file_info['path']}")
            continue

        try:
            chunks = []
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        # Create trace content
                        content = json.dumps(data, indent=2)

                        # Create unique ID
                        chunk_id = hashlib.sha256(
                            f"{file_info['path']}:{line_num}:{content}".encode(),
                        ).hexdigest()

                        # Enhanced metadata
                        metadata = {
                            "source_file": str(file_path),
                            "trace_type": file_info["trace_type"],
                            "namespace": file_info["namespace"],
                            "description": file_info["description"],
                            "line_number": line_num,
                            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                            "trace_id": f"trace_{file_info['trace_type']}_{line_num:06d}",
                            "created_utc": int(datetime.now().timestamp()),
                            "chunk_type": "expanded_trace",
                            "file_size": len(content),
                        }

                        # Add any additional fields from the data
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if key not in metadata and isinstance(value, (str, int, float, bool)):
                                    metadata[f"data_{key}"] = value

                        chunk = {
                            "id": chunk_id,
                            "content": content,
                            "metadata": metadata,
                        }

                        chunks.append(chunk)

                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num} in {file_info['path']}: {e}")
                        continue

            if chunks:
                # Ingest chunks
                ids = [chunk["id"] for chunk in chunks]
                documents = [chunk["content"] for chunk in chunks]
                metadatas = [chunk["metadata"] for chunk in chunks]

                # Generate mock embeddings
                embeddings = [[0.0] * 1536 for _ in chunks]

                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings,
                )

                logger.info(f"Ingested {len(chunks)} chunks from {file_info['path']}")
                total_chunks += len(chunks)

        except Exception as e:
            logger.error(f"Error processing {file_info['path']}: {e}")

    return total_chunks


def ingest_log_traces():
    """Ingest log files as traces"""

    log_files = [
        {
            "path": "artifacts/logs/_ssot_stderr.log",
            "trace_type": "error_log",
            "namespace": "system_logs",
        },
        {
            "path": "artifacts/logs/_ssot_stderr_v2.log",
            "trace_type": "error_log_v2",
            "namespace": "system_logs",
        },
    ]

    client = chromadb.PersistentClient(canonical_persist_dir_str())
    collection = client.get_collection("traces")

    total_chunks = 0
    for file_info in log_files:
        file_path = Path(file_info["path"])

        if not file_path.exists():
            logger.warning(f"File not found: {file_info['path']}")
            continue

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Split into chunks (e.g., by lines or paragraphs)
            lines = content.split("\n")
            chunks = []

            for i in range(0, len(lines), 100):  # Chunk every 100 lines
                chunk_lines = lines[i : i + 100]
                chunk_content = "\n".join(chunk_lines)

                if not chunk_content.strip():
                    continue

                chunk_id = hashlib.sha256(
                    f"{file_info['path']}:{i}:{chunk_content}".encode(),
                ).hexdigest()

                metadata = {
                    "source_file": str(file_path),
                    "trace_type": file_info["trace_type"],
                    "namespace": file_info["namespace"],
                    "line_start": i + 1,
                    "line_end": min(i + 100, len(lines)),
                    "content_hash": hashlib.sha256(chunk_content.encode()).hexdigest(),
                    "trace_id": f"trace_{file_info['trace_type']}_{i // 100:06d}",
                    "created_utc": int(datetime.now().timestamp()),
                    "chunk_type": "log_trace",
                    "file_size": len(chunk_content),
                }

                chunk = {
                    "id": chunk_id,
                    "content": chunk_content,
                    "metadata": metadata,
                }

                chunks.append(chunk)

            if chunks:
                # Ingest chunks
                ids = [chunk["id"] for chunk in chunks]
                documents = [chunk["content"] for chunk in chunks]
                metadatas = [chunk["metadata"] for chunk in chunks]

                # Generate mock embeddings
                embeddings = [[0.0] * 1536 for _ in chunks]

                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings,
                )

                logger.info(f"Ingested {len(chunks)} chunks from {file_info['path']}")
                total_chunks += len(chunks)

        except Exception as e:
            logger.error(f"Error processing {file_info['path']}: {e}")

    return total_chunks


def main():
    """Main function"""
    logger.info("Starting expanded traces ingestion...")

    jsonl_chunks = ingest_jsonl_traces()
    log_chunks = ingest_log_traces()

    total_new_chunks = jsonl_chunks + log_chunks

    # Get final collection stats
    client = chromadb.PersistentClient(canonical_persist_dir_str())
    collection = client.get_collection("traces")
    final_count = collection.count()

    logger.info("Wave 5 Complete:")
    logger.info(f"  - JSONL traces: {jsonl_chunks} chunks")
    logger.info(f"  - Log traces: {log_chunks} chunks")
    logger.info(f"  - Total new chunks: {total_new_chunks}")
    logger.info(f"  - Final traces collection: {final_count} items")


if __name__ == "__main__":
    main()
