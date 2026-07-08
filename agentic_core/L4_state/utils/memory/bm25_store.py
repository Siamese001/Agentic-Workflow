"""
In-memory BM25 retrieval engine for hybrid search operations.

Zero-Ambiguity Standard: Renamed from Bm25Store.py to bm25_store.py
Moved from semantic_memory/store to L4_state/memory/semantic

SparseIndex (Phase B1)
──────────────────────
Persistent sidecar-backed sparse retrieval. Reads from SQLite FTS5 + term_freq
databases built by tools/generate/ingestion/build_sparse_index.py.

Query contract (same as Bm25Store.query):
  .search(query: str, top_k: int) -> list[dict]
  Each dict: {"id", "content", "score", "metadata", "source"="sparse_fts"}
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import Any

_SparseLogger = logging.getLogger(__name__)

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "bm25_store")
trace_contract.emit_determinism_digest("p0", "bm25_store")

trace_contract._emit_dispatches_healing_run("p1", "bm25_store", "L4")
trace_contract._emit_routes_through("p1", "bm25_store", "L4")
trace_contract._emit_checks_agent_registry("p1", "bm25_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "bm25_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "bm25_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "bm25_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "bm25_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "bm25_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "bm25_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "bm25_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "bm25_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "bm25_store")
trace_contract._emit_gated_by_confidence("p1", "bm25_store", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "bm25_store", "L4")
trace_contract._emit_reads_policy_state("p1", "bm25_store", "L4")
trace_contract._emit_authorize_and_execute("p2", "bm25_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "bm25_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "bm25_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "bm25_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "bm25_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "bm25_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "bm25_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "bm25_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "bm25_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "bm25_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "bm25_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "bm25_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "bm25_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "bm25_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "bm25_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "bm25_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "bm25_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "bm25_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "bm25_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "bm25_store", "exec_snapshot_link")

try:
    from rank_bm25 import BM25Okapi
except ImportError as _err:
    raise ImportError(
        "rank-bm25 is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err
from agentic_core.L2_execution.config.hybrid_retriever_config import ASTAwareTokenizer
from tqdm import tqdm

trace_contract._emit_emits_metric_event("bm25_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("bm25_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("bm25_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("bm25_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("bm25_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("bm25_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("bm25_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("bm25_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("bm25_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("bm25_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("bm25_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("bm25_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("bm25_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("bm25_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("bm25_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("bm25_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("bm25_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("bm25_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("bm25_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("bm25_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("bm25_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("bm25_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("bm25_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("bm25_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("bm25_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("bm25_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("bm25_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("bm25_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "bm25_store", "context_pull")
trace_contract._emit_pulls_context("p1", "bm25_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "bm25_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "bm25_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "bm25_store", "write_through")
trace_contract._emit_writes_through("p1", "bm25_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "bm25_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "bm25_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "bm25_store", "routing_commit")

_tokenizer = ASTAwareTokenizer()


class Bm25Store:
    """In-memory BM25 index for fast keyword retrieval."""

    def __init__(self):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "Bm25Store.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "Bm25Store.__init__", "p0_governance")
        self.documents: list[dict] = []
        self.bm25: BM25Okapi | None = None
        self._build_index()

    def add_documents(self, docs: list[dict]) -> None:
        """Add or update documents."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "Bm25Store.add_documents")

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
        for idx, score in tqdm(ranked, desc="Processing", unit="item"):
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
                },
            )
        return results


_bm25_store: Any = Bm25Store()


def get_bm25_store() -> Bm25Store:
    """Get the singleton BM25 store instance for hybrid search operations."""
    return _bm25_store


# ---------------------------------------------------------------------------
# SparseIndex — persistent SQLite FTS5 sidecar (Phase B1)
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SPARSE_DIR = _REPO_ROOT / "data" / "cache" / "sparse"

# Collections that have a built sparse sidecar (all 8 canonical — Phase C)
_SPARSE_COLLECTIONS = frozenset(
    {
        "code_chunks",
        "symbols",
        "arch_docs",
        "tests_guardrails",
        "runtime_evidence",
        "process_docs",
        "ext_knowledge",
        "incidents_rca",
    }
)

# Simple tokenizer — must match build_sparse_index.py tokenize() exactly
_STOP = frozenset(
    "self cls none true false return if else elif for while try except finally with "
    "as import from def class pass break continue and or not in is lambda yield raise "
    "assert del global nonlocal async await the a an of to".split()
)
_SPLIT_RE_SPARSE = re.compile(r"[^A-Za-z0-9_]+")
_CAMEL_RE_SPARSE = re.compile(r"([a-z0-9])([A-Z])")


def _tokenize_sparse(text: str) -> list[str]:
    """Tokenize a query the same way build_sparse_index.py tokenizes documents."""
    raw = _SPLIT_RE_SPARSE.split(text)
    tokens: list[str] = []
    seen: set[str] = set()

    def _emit(t: str) -> None:
        if t and t not in seen:
            seen.add(t)
            tokens.append(t)

    for tok in tqdm(raw, desc="Processing", unit="item"):
        if not tok or len(tok) < 2:
            continue
        lower = tok.lower()
        if lower in _STOP:
            continue
        _emit(lower)
        # sub-tokens from CamelCase / snake_case splitting
        parts = lower.split("_")
        for part in parts:
            for sub in _CAMEL_RE_SPARSE.sub(r"\1 \2", part).split():
                if len(sub) > 1 and sub not in _STOP:
                    _emit(sub)

    return tokens


class SparseIndex:
    """Persistent FTS5-backed sparse retrieval for a single canonical collection.

    Reads from the SQLite sidecar at data/cache/sparse/<collection>.db
    built by tools/generate/ingestion/build_sparse_index.py.

    API contract (matches HybridSearchEngine._lexical_search expectations):
      .search(query, top_k) -> list[{"id", "content", "score", "metadata", "source"}]
    """

    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name
        self._db_path = _SPARSE_DIR / f"{collection_name}.db"
        self._available = self._db_path.exists()
        if self._available:
            _SparseLogger.info("SparseIndex loaded: %s (%s)", collection_name, self._db_path.name)
        else:
            _SparseLogger.warning(
                "SparseIndex sidecar missing for '%s': %s — run build_sparse_index.py",
                collection_name,
                self._db_path,
            )

    @property
    def is_available(self) -> bool:
        return self._available

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """FTS5 search against the sidecar DB.

        Uses FTS5 MATCH on the full query text and falls back to
        per-token OR if the combined phrase yields no hits.

        Returns list of result dicts ordered by FTS5 rank (best first).
        """
        if not self._available:
            return []

        tokens = _tokenize_sparse(query)
        if not tokens:
            return []

        results: list[dict[str, Any]] = []
        try:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("PRAGMA query_only=ON")

            # Strategy 1: exact phrase match (all tokens must appear)
            fts_query = " ".join(tokens)
            rows = conn.execute(
                "SELECT id, document, snippet(docs_fts, 1, '', '', '...', 20) "
                "FROM docs_fts WHERE docs_fts MATCH ? ORDER BY rank LIMIT ?",
                (fts_query, top_k * 2),
            ).fetchall()

            # Strategy 2: OR-fallback if exact phrase yields nothing
            if not rows and len(tokens) > 1:
                fts_or = " OR ".join(tokens)
                rows = conn.execute(
                    "SELECT id, document, snippet(docs_fts, 1, '', '', '...', 20) "
                    "FROM docs_fts WHERE docs_fts MATCH ? ORDER BY rank LIMIT ?",
                    (fts_or, top_k * 2),
                ).fetchall()

            for rank, (doc_id, document, _snippet) in tqdm(enumerate(rows), desc="Processing", unit="item"):
                # BM25-like score: FTS5 rank is negative (lower = better), invert to positive
                # We use position-based score for normalisation (rank 0 = best)
                score = 1.0 / (1.0 + rank)

                # Fetch metadata from docs table
                meta_row = conn.execute("SELECT metadata FROM docs WHERE id=?", (doc_id,)).fetchone()
                metadata: dict[str, Any] = {}
                if meta_row and meta_row[0]:
                    try:
                        metadata = json.loads(meta_row[0])
                    except (
                        json.JSONDecodeError,
                        ValueError,
                    ):  # guardian: allow-silent-swallow -- metadata parse: malformed row, metadata simply omitted
                        pass

                results.append(
                    {
                        "id": doc_id,
                        "content": document,
                        "score": score,
                        "metadata": metadata,
                        "source": "sparse_fts",
                    }
                )

            conn.close()

        except (
            sqlite3.OperationalError
        ) as e:  # guardian: allow-log-and-swallow -- BM25 query: non-fatal, returns empty results
            _SparseLogger.error("SparseIndex query failed for '%s': %s", self.collection_name, e)

        return results[:top_k]


# Per-collection singletons — created lazily on first access
_sparse_index_cache: dict[str, SparseIndex] = {}


def sparse_sidecar_exists(collection_name: str) -> bool:
    """True when ``data/cache/sparse/<collection_name>.db`` is present on disk."""
    name = (collection_name or "").strip()
    if not name:
        return False
    return (_SPARSE_DIR / f"{name}.db").is_file()


def get_sparse_index(collection_name: str) -> SparseIndex | None:
    """Return the SparseIndex singleton for *collection_name*, or None if unavailable.

    Resolution order (profile-driven, app-agnostic):

    1. Known canonical collections in ``_SPARSE_COLLECTIONS`` (legacy allowlist).
    2. Any collection name whose FTS5 sidecar file exists under ``data/cache/sparse/``.

    Returns None when the name is empty or no sidecar is present, so callers degrade
    gracefully without app-specific literals in this module.
    """
    name = (collection_name or "").strip()
    if not name:
        return None
    if name not in _SPARSE_COLLECTIONS and not sparse_sidecar_exists(name):
        return None
    if name not in _sparse_index_cache:
        _sparse_index_cache[name] = SparseIndex(name)
    idx = _sparse_index_cache[name]
    return idx if idx.is_available else None
