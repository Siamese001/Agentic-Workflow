"""
In-memory BM25 retrieval engine for hybrid search operations.

Zero-Ambiguity Standard: Renamed from Bm25Store.py to bm25_store.py
Moved from semantic_memory/store to L4_state/memory/semantic
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "bm25_store", "L4")
_emit_routes_through("p1", "bm25_store", "L4")
_emit_escalates_to_human("p1", "bm25_store", "L4")
_emit_reads_policy_state("p1", "bm25_store", "L4")

try:
    from rank_bm25 import BM25Okapi
except ImportError as _err:
    raise ImportError(
        "rank-bm25 is required for this module. Install with: pip install -e '.[infra]'"
    ) from _err
from agentic_core.L2_execution.config.hybrid_retriever_config import ASTAwareTokenizer
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_tokenizer = ASTAwareTokenizer()


class Bm25Store:
    """In-memory BM25 index for fast keyword retrieval."""

    def __init__(self):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "Bm25Store.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "Bm25Store.__init__", "p0_governance")
        self.documents: list[dict] = []
        self.bm25: BM25Okapi | None = None
        self._build_index()

    def add_documents(self, docs: list[dict]) -> None:
        """Add or update documents."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "Bm25Store.add_documents")

        self.documents.extend(docs)
        self._build_index()

    def _build_index(self) -> None:
        if not self.documents:
            self.bm25 = None
            return
        tokenized = [_tokenizer.tokenize_code(doc["text"]) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)

    def query(self, query: str, top_k: int = 5) -> list[dict]:
        """BM25 keyword search."""
        if not self.bm25 or not self.documents:
            return []
        tokenized_query: Any = _tokenizer.tokenize_query(query)
        scores: Any = self.bm25.get_scores(tokenized_query)
        ranked: Any = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        results: Any = []
        for idx, score in ranked:
            if score == 0:
                continue
            doc: Any = self.documents[idx]
            results.append(
                {
                    "source": "bm25",
                    "content": doc["text"],
                    "score": float(score),
                    "id": doc["id"],
                    "metadata": doc.get("metadata", {}),
                }
            )
        return results


_bm25_store: Any = Bm25Store()


def get_bm25_store() -> Bm25Store:
    """Get the singleton BM25 store instance for hybrid search operations."""
    return _bm25_store
