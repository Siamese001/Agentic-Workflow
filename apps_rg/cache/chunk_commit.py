"""Commit resume chunks to durable storage via UWG.

This module handles the Exit→UWG→L4 commit flow for output chunks.
NO direct writes to L4 — all durable state changes go through UWG.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from apps_rg.chunking.resume_chunker import ResumeChunk

_logger = logging.getLogger(__name__)


def commit_chunks_via_exit(
    chunks: list[ResumeChunk],
    run_context: dict,
) -> Optional[str]:
    """Commit chunks to durable storage via Exit pipeline.

    This function builds the CommitRequest payload and sends it to
the UWG for durable admission. It does NOT write directly to L4.

    Returns UWG commit receipt on success, None on failure.
    """
    if not chunks:
        _logger.debug("No chunks to commit")
        return None

    try:
        from agentic_core.L4_state.durable_write_gateway import (
            CommitRequest,
            DurableWriteGateway,
        )
    except ImportError as exc:
        _logger.warning("UWG not available for chunk commit: %s", exc)
        return None

    # Build chunks payload
    chunks_data = [chunk.to_dict() for chunk in chunks]

    # Build commit request
    try:
        intent_hash = chunks[0].source_input_intent_hash if chunks else None
    except Exception:
        intent_hash = None

    commit_request = CommitRequest(
        mutation_intent="store_resume_chunks",
        proposed_state_diff={
            "semantic_cache_entries": [
                {
                    "namespace": "apps_rg.resume_generation.chunks",
                    "key": chunk.chunk_id,
                    "value": chunk.to_dict(),
                    "metadata": {
                        "intent_hash": chunk.source_input_intent_hash,
                        "tenant_id": chunk.tenant_id,
                    },
                }
                for chunk in chunks
            ]
        },
        lineage_context={
            "source_run_id": run_context.get("run_id"),
            "source_request_id": run_context.get("request_id"),
            "input_intent_hash": intent_hash,
            "exit_disposition": run_context.get("exit_disposition"),
        },
        policy_hash=run_context.get("policy_hash", "unknown"),
    )

    # Submit to UWG
    try:
        uwg = DurableWriteGateway.get_instance()
        receipt = uwg.commit(commit_request)
        _logger.info("Committed %d chunks via UWG: receipt=%s", len(chunks), receipt)
        return receipt
    except Exception as exc:  # guardian: allow-broad-exception -- UWG commit is fail-soft
        _logger.error("UWG commit failed: %s", exc)
        return None


def build_chunk_commit_receipt(
    chunks: list[ResumeChunk],
    uwg_receipt: str,
    run_context: dict,
) -> dict:
    """Build a structured receipt document for chunk commitment.

    This receipt can be stored in the run directory for audit.
    """
    return {
        "receipt_type": "chunk_commit",
        "uwg_receipt": uwg_receipt,
        "committed_at": run_context.get("timestamp"),
        "run_id": run_context.get("run_id"),
        "request_id": run_context.get("request_id"),
        "chunks_committed": len(chunks),
        "chunk_ids": [c.chunk_id for c in chunks],
        "intent_hash": chunks[0].source_input_intent_hash if chunks else None,
    }


__all__ = ["commit_chunks_via_exit", "build_chunk_commit_receipt"]
