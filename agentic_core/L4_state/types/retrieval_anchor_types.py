"""
L4 RetrievalAnchor — Phase 2

Mandatory citation anchor returned with every L4 retrieval result.
Enforces grounding: every piece of retrieved content is traceable.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass
class RetrievalAnchor:
    """
    Citation anchor attached to every L4 retrieval result.

    All fields are required. No optional fields — absence of any field
    indicates a retrieval implementation that has not been grounded.
    """
    source_doc_id: str
    chunk_id: str
    char_start: int
    char_end: int
    retrieved_at_utc: str
    version_hash: str

    def __post_init__(self) -> None:
        if not self.source_doc_id:
            raise ValueError('source_doc_id must be non-empty')
        if not self.chunk_id:
            raise ValueError('chunk_id must be non-empty')
        if self.char_end <= self.char_start:
            raise ValueError(f'char_end ({self.char_end}) must be > char_start ({self.char_start})')
        if not self.retrieved_at_utc:
            raise ValueError('retrieved_at_utc must be non-empty')
        if not self.version_hash:
            raise ValueError('version_hash must be non-empty')

    @staticmethod
    def now_utc() -> str:
        return datetime.now(tz=timezone.utc).isoformat()

    def to_dict(self) -> dict[str, object]:
        return {'source_doc_id': self.source_doc_id, 'chunk_id': self.chunk_id, 'char_start': self.char_start, 'char_end': self.char_end, 'retrieved_at_utc': self.retrieved_at_utc, 'version_hash': self.version_hash}

@dataclass
class AnchoredResult:
    """
    A retrieval result paired with its mandatory citation anchor.
    Returned by all L4 semantic search / chunk retrieval calls.
    """
    content: str
    anchor: RetrievalAnchor

class AnchorViolationError(Exception):
    """
    Raised by Guardian when reasoning uses retrieved content without anchors.

    Violation code: MISSING_RETRIEVAL_ANCHOR
    """
    VIOLATION_CODE = 'MISSING_RETRIEVAL_ANCHOR'

    def __init__(self, message: str='Reasoning used retrieved content but provided no anchors') -> None:
        super().__init__(f'[{self.VIOLATION_CODE}] {message}')

def enforce_anchor_coverage(retrieval_context: list[AnchoredResult], anchors: list[RetrievalAnchor]) -> None:
    """
    Guardian enforcement: if retrieval_context is non-empty,
    anchors list must be non-empty and cover each retrieved chunk.

    Raises AnchorViolationError if the invariant is violated.
    """
    if not retrieval_context:
        return
    if not anchors:
        raise AnchorViolationError('retrieval_context is non-empty but anchors list is empty')
    retrieved_chunk_ids = {r.anchor.chunk_id for r in retrieval_context}
    covered_chunk_ids = {a.chunk_id for a in anchors}
    uncovered = retrieved_chunk_ids - covered_chunk_ids
    if uncovered:
        raise AnchorViolationError(f'Retrieved chunks not covered by anchors: {sorted(uncovered)}')
