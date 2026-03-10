"""Embedding corpus extraction for Plan A historical data ingestion.

Provides deterministic extraction, canonicalization, and JSONL writing
for healing contexts, telemetry events, and DPO pairs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True, slots=True)
class CorpusRecord:
    """Single record in embedding corpus."""

    text: str
    trace_id: str
    content_hash: str  # 64-hex SHA-256
    namespace: str  # "healing_contexts", "telemetry_events", "dpo_pairs"


def canonical_record_json(record: dict) -> bytes:
    """Convert record to canonical JSON bytes.

    Args:
        record: Dictionary to canonicalize.

    Returns:
        ASCII-only canonical JSON bytes.
    """
    return json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def compute_content_hash(canonical_bytes: bytes) -> str:
    """Compute SHA-256 hash of canonical bytes.

    Args:
        canonical_bytes: Canonical JSON bytes.

    Returns:
        64-hex SHA-256 hash.
    """
    return hashlib.sha256(canonical_bytes).hexdigest()


def write_jsonl_records(path: Path, records: list[CorpusRecord]) -> None:
    """Write records to JSONL file in deterministic order.

    Args:
        path: Output file path.
        records: List of records to write.
    """
    # Sort by (content_hash ASC, trace_id ASC) for deterministic output
    sorted_records = sorted(records, key=lambda r: (r.content_hash, r.trace_id))

    with open(path, "w", encoding="utf-8") as f:
        for record in sorted_records:
            # Create canonical JSON for output
            output_record = {
                "text": record.text,
                "trace_id": record.trace_id,
                "content_hash": record.content_hash,
                "namespace": record.namespace,
            }
            line = json.dumps(
                output_record,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            f.write(line + "\n")


def extract_healing_context_records(source: list[dict]) -> list[CorpusRecord]:
    """Extract healing context records from source data.

    Args:
        source: List of source dictionaries.

    Returns:
        List of CorpusRecord objects.

    Raises:
        ValueError: If required fields are missing.
    """
    records = []

    for i, item in enumerate(source):
        # Validate required fields
        if "violation_signature" not in item:
            raise ValueError(f"Item {i}: missing 'violation_signature' field")
        if "strategy" not in item:
            raise ValueError(f"Item {i}: missing 'strategy' field")

        # Extract text as canonical JSON of required sub-objects
        text_obj = {
            "violation_signature": item["violation_signature"],
            "strategy": item["strategy"],
        }
        text = json.dumps(
            text_obj,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        # Compute content hash
        content_hash = compute_content_hash(text.encode("ascii"))

        # Determine trace_id
        if "trace_id" in item:
            trace_id = str(item["trace_id"])
        else:
            trace_id = content_hash[:16]

        records.append(
            CorpusRecord(
                text=text,
                trace_id=trace_id,
                content_hash=content_hash,
                namespace="healing_contexts",
            )
        )

    return records


def extract_telemetry_event_records(source: list[dict]) -> list[CorpusRecord]:
    """Extract telemetry event records from source data.

    Args:
        source: List of source dictionaries.

    Returns:
        List of CorpusRecord objects.

    Raises:
        ValueError: If required fields are missing.
    """
    records = []

    for i, item in enumerate(source):
        # Validate required fields
        if "event_type" not in item:
            raise ValueError(f"Item {i}: missing 'event_type' field")
        if "payload" not in item:
            raise ValueError(f"Item {i}: missing 'payload' field")

        # Extract text as canonical JSON of required sub-objects
        text_obj = {
            "event_type": item["event_type"],
            "payload": item["payload"],
        }
        text = json.dumps(
            text_obj,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        # Compute content hash
        content_hash = compute_content_hash(text.encode("ascii"))

        # Determine trace_id
        if "trace_id" in item:
            trace_id = str(item["trace_id"])
        else:
            trace_id = content_hash[:16]

        records.append(
            CorpusRecord(
                text=text,
                trace_id=trace_id,
                content_hash=content_hash,
                namespace="telemetry_events",
            )
        )

    return records


def extract_dpo_pair_records(source: list[dict]) -> list[CorpusRecord]:
    """Extract DPO pair records from source data.

    Args:
        source: List of source dictionaries.

    Returns:
        List of CorpusRecord objects.

    Raises:
        ValueError: If required fields are missing.
    """
    records = []

    for i, item in enumerate(source):
        # Validate required fields
        if "prompt" not in item:
            raise ValueError(f"Item {i}: missing 'prompt' field")
        if "chosen" not in item:
            raise ValueError(f"Item {i}: missing 'chosen' field")
        if "rejected" not in item:
            raise ValueError(f"Item {i}: missing 'rejected' field")

        # Extract text as canonical JSON of required sub-objects
        text_obj = {
            "prompt": item["prompt"],
            "chosen": item["chosen"],
            "rejected": item["rejected"],
        }
        text = json.dumps(
            text_obj,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        # Compute content hash
        content_hash = compute_content_hash(text.encode("ascii"))

        # Determine trace_id
        if "trace_id" in item:
            trace_id = str(item["trace_id"])
        else:
            trace_id = content_hash[:16]

        records.append(
            CorpusRecord(
                text=text,
                trace_id=trace_id,
                content_hash=content_hash,
                namespace="dpo_pairs",
            )
        )

    return records


__all__ = [
    "CorpusRecord",
    "canonical_record_json",
    "compute_content_hash",
    "write_jsonl_records",
    "extract_healing_context_records",
    "extract_telemetry_event_records",
    "extract_dpo_pair_records",
]
