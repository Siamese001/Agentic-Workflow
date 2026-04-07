"""
V15 P4 Framework Contracts — Knowledge, Retrieval, Provenance & Traceability.

Runtime contracts enforcing P4 (Immutable Traceability) invariants required
by the V15 Target State audit (Prompt v5.0 Enhanced).

Contract version: 1.0.0
"""

from __future__ import annotations

import hashlib
from typing import Any

from agentic_core.L0_routing.types.traceability_types import (
    CitationBundle,
    CognitiveDiffBundle,
    ErrorSignature,
    KnowledgeAdvisoryConstraint,
    KnowledgeDirective,
    PlanProvenance,
    PolicyConfigPin,
    RerankScore,
    RetrievalQuery,
    RetrievedChunk,
    compute_error_signature_hash,
    validate_trace_id,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402
    record_execution_trace,
)

record_execution_trace("traceability_contracts", "traceability_contracts_trace")

_emit_records_execution_trace("p0", "evidence", "traceability_contracts")
# =============================================================================
# §15.5 — Trace ID generation + validation
# =============================================================================


class TraceIDFormatError(Exception):
    """Raised when a trace ID does not match the required format."""


def generate_trace_id(hex_suffix: str) -> str:
    """§15.5 — Generate a compliant trace ID: CC3AL1-{8 uppercase hex chars}."""
    if len(hex_suffix) != 8:
        raise TraceIDFormatError(
            f"FAIL (P4): hex_suffix must be exactly 8 chars, got {len(hex_suffix)}",
        )
    candidate = f"CC3AL1-{hex_suffix.upper()}"
    validate_trace_id(candidate)
    return candidate


# =============================================================================
# §5.2 — Error Signature construction
# =============================================================================


class ErrorSignatureError(Exception):
    """Raised when error signature construction fails."""


def build_error_signature(
    error_type: str,
    target_node_id: str,
    time_bucket: int,
) -> ErrorSignature:
    """§5.2 — Build a deterministic error signature. Fail-closed."""
    try:
        sig_hash = compute_error_signature_hash(error_type, target_node_id, time_bucket)
        return ErrorSignature(
            error_type=error_type,
            target_node_id=target_node_id,
            time_bucket=time_bucket,
            signature_hash=sig_hash,
        )
    except (ValueError, TypeError) as exc:
        raise ErrorSignatureError(
            f"FAIL (P4): ErrorSignature construction failed: {exc}",
        ) from exc


# =============================================================================
# §4.2 — Policy Config Pin
# =============================================================================


class PolicyConfigPinError(Exception):
    """Raised when policy config pin construction or verification fails."""


def pin_policy_config(
    wave_id: str,
    policy_config_bytes: bytes,
    semantic_clock_tick: int,
) -> PolicyConfigPin:
    """§4.2 — Capture SHA-256 of policy config at wave start."""
    config_hash = hashlib.sha256(policy_config_bytes).hexdigest()
    try:
        return PolicyConfigPin(
            wave_id=wave_id,
            policy_config_hash=config_hash,
            semantic_clock_tick=semantic_clock_tick,
        )
    except (ValueError, TypeError) as exc:
        raise PolicyConfigPinError(
            f"FAIL (P4): PolicyConfigPin construction failed: {exc}",
        ) from exc


def verify_policy_config_unchanged(
    pin: PolicyConfigPin,
    current_config_bytes: bytes,
) -> bool:
    """§4.2 — Verify policy config unchanged since wave start. Fail-closed."""
    current_hash = hashlib.sha256(current_config_bytes).hexdigest()
    if current_hash != pin.policy_config_hash:
        raise PolicyConfigPinError(
            f"FAIL (P4): Policy config mutated during wave '{pin.wave_id}'. "
            f"Expected {pin.policy_config_hash}, got {current_hash}.",
        )
    return True


# =============================================================================
# §1.6 — Hash Verification (manifest_hash from ast_snippet bytes)
# =============================================================================


class ManifestHashError(Exception):
    """Raised when manifest hash verification fails."""


def verify_manifest_hash(ast_snippet: str, manifest_hash: str) -> bool:
    """§1.6 — Verify manifest_hash matches SHA-256 of ast_snippet bytes."""
    expected = hashlib.sha256(ast_snippet.encode("utf-8")).hexdigest()
    if manifest_hash != expected:
        raise ManifestHashError(
            f"FAIL (P4): manifest_hash mismatch. Expected {expected}, got {manifest_hash}.",
        )
    return True


# =============================================================================
# §6.7 — Plan Provenance
# =============================================================================


class PlanProvenanceError(Exception):
    """Raised when plan provenance construction fails."""


def build_plan_provenance(
    trace_id: str,
    plan_id: str,
    policy_liaison_node: str,
    semantic_clock_tick: int,
    plan_content: str,
) -> PlanProvenance:
    """§6.7 — Build a PlanProvenance linking plan to policy liaison node."""
    plan_hash = hashlib.sha256(plan_content.encode("utf-8")).hexdigest()
    try:
        return PlanProvenance(
            trace_id=trace_id,
            plan_id=plan_id,
            policy_liaison_node=policy_liaison_node,
            semantic_clock_tick=semantic_clock_tick,
            plan_hash=plan_hash,
        )
    except (ValueError, TypeError) as exc:
        raise PlanProvenanceError(
            f"FAIL (P4): PlanProvenance construction failed: {exc}",
        ) from exc


# =============================================================================
# §6.5 — RAG Artifact Chain validation
# =============================================================================


class RAGChainError(Exception):
    """Raised when RAG chain validation fails."""


def build_retrieval_query(
    trace_id: str,
    query_text: str,
    source_agent: str,
    semantic_clock_tick: int,
) -> RetrievalQuery:
    """§6.5 — Build a RetrievalQuery with deterministic hash."""
    query_hash = hashlib.sha256(query_text.encode("utf-8")).hexdigest()
    try:
        return RetrievalQuery(
            trace_id=trace_id,
            query_text=query_text,
            query_hash=query_hash,
            source_agent=source_agent,
            semantic_clock_tick=semantic_clock_tick,
        )
    except (ValueError, TypeError) as exc:
        raise RAGChainError(
            f"FAIL (P4): RetrievalQuery construction failed: {exc}",
        ) from exc


def build_retrieved_chunk(
    chunk_id: str,
    source_id: str,
    content: str,
    location: str,
    retrieval_query_hash: str,
) -> RetrievedChunk:
    """§6.5 — Build a RetrievedChunk with content hash."""
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    try:
        return RetrievedChunk(
            chunk_id=chunk_id,
            source_id=source_id,
            content=content,
            content_hash=content_hash,
            location=location,
            retrieval_query_hash=retrieval_query_hash,
        )
    except (ValueError, TypeError) as exc:
        raise RAGChainError(
            f"FAIL (P4): RetrievedChunk construction failed: {exc}",
        ) from exc


def validate_retrieval_set(
    chunks: tuple[RetrievedChunk, ...],
    rerank_scores: tuple[RerankScore, ...],
) -> bool:
    """§6.5 — Validate retrieval set: stable ordering, all chunks scored.

    - Every chunk must have a corresponding rerank score.
    - Rerank scores must be in descending order (stable ranking).
    """
    if not chunks:
        raise RAGChainError("FAIL (P4): Retrieval set must contain at least one chunk")

    chunk_ids = {c.chunk_id for c in chunks}
    scored_ids = {s.chunk_id for s in rerank_scores}

    missing = chunk_ids - scored_ids
    if missing:
        raise RAGChainError(
            f"FAIL (P4): Chunks without rerank scores: {missing}",
        )

    # Verify descending score order
    scores = [s.score for s in rerank_scores]
    for i in range(len(scores) - 1):
        if scores[i] < scores[i + 1]:
            raise RAGChainError(
                f"FAIL (P4): Rerank scores not in descending order at index {i}: "
                f"{scores[i]} < {scores[i + 1]}",
            )

    return True


def validate_citation_chain(
    bundle: CitationBundle,
    chunks: tuple[RetrievedChunk, ...],
    query: RetrievalQuery,
) -> bool:
    """§6.5 — Validate citation chain end-to-end.

    - Every chunk must have at least one citation in the bundle.
    - Every citation must reference a valid chunk_id.
    - Bundle retrieval_query_hash must match query.query_hash.
    - Every citation retrieval_hash must match query.query_hash.
    """
    if bundle.retrieval_query_hash != query.query_hash:
        raise RAGChainError(
            f"FAIL (P4): CitationBundle retrieval_query_hash mismatch. "
            f"Expected {query.query_hash}, got {bundle.retrieval_query_hash}.",
        )

    chunk_ids = {c.chunk_id for c in chunks}
    cited_chunk_ids = {c.chunk_id for c in bundle.citations}

    uncited = chunk_ids - cited_chunk_ids
    if uncited:
        raise RAGChainError(
            f"FAIL (P4): Chunks without citations: {uncited}",
        )

    invalid_refs = cited_chunk_ids - chunk_ids
    if invalid_refs:
        raise RAGChainError(
            f"FAIL (P4): Citations referencing non-existent chunks: {invalid_refs}",
        )

    for citation in bundle.citations:
        if citation.retrieval_hash != query.query_hash:
            raise RAGChainError(
                f"FAIL (P4): Citation {citation.citation_id} retrieval_hash does not match query hash.",
            )

    return True


# =============================================================================
# §15.2 — Cognitive Diff Bundle
# =============================================================================


class CognitiveDiffError(Exception):
    """Raised when CognitiveDiffBundle construction fails."""


def build_cognitive_diff_bundle(
    trace_id: str,
    incident_id: str,
    intended_policy_snapshot: str,
    actual_execution_trace: str,
    diff_summary: str,
    semantic_clock_tick: int,
) -> CognitiveDiffBundle:
    """§15.2 — Build a CognitiveDiffBundle for incident response."""
    try:
        return CognitiveDiffBundle(
            trace_id=trace_id,
            incident_id=incident_id,
            intended_policy_snapshot=intended_policy_snapshot,
            actual_execution_trace=actual_execution_trace,
            diff_summary=diff_summary,
            semantic_clock_tick=semantic_clock_tick,
        )
    except (ValueError, TypeError) as exc:
        raise CognitiveDiffError(
            f"FAIL (P4): CognitiveDiffBundle construction failed: {exc}",
        ) from exc


# =============================================================================
# §6.9 — Advisory-Only Enforcement
# =============================================================================


class AdvisoryViolationError(Exception):
    """Raised when knowledge layer attempts a control directive."""


def enforce_advisory_only(constraint: Any) -> KnowledgeAdvisoryConstraint:
    """§6.9 — Enforce that knowledge outputs are advisory-only.

    Fail-closed: if directive_type is CONTROL, raise immediately.
    """
    if not isinstance(constraint, KnowledgeAdvisoryConstraint):
        raise AdvisoryViolationError(
            f"FAIL (P4): Expected KnowledgeAdvisoryConstraint, got {type(constraint).__name__}",
        )
    if constraint.directive_type == KnowledgeDirective.CONTROL:
        raise AdvisoryViolationError(
            f"FAIL (P4): Knowledge layer issued CONTROL directive "
            f"(trace_id={constraint.trace_id}). Only ADVISORY is permitted.",
        )
    return constraint


__all__ = [
    "AdvisoryViolationError",
    "CognitiveDiffError",
    "ErrorSignatureError",
    "ManifestHashError",
    "PlanProvenanceError",
    "PolicyConfigPinError",
    "RAGChainError",
    "TraceIDFormatError",
    "build_cognitive_diff_bundle",
    "build_error_signature",
    "build_plan_provenance",
    "build_retrieval_query",
    "build_retrieved_chunk",
    "enforce_advisory_only",
    "generate_trace_id",
    "pin_policy_config",
    "validate_citation_chain",
    "validate_retrieval_set",
    "verify_manifest_hash",
    "verify_policy_config_unchanged",
]
