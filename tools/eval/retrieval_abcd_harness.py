"""4-cell A/B retrieval benchmark harness (Wave E, ADR-045 acceptance gate).

Compares four ingestion / embedding configurations head-to-head on a
calibration corpus:

    A. baseline        - raw chunks, standard BGE embedding
    B. contextualized  - ADR-045 main path (LLM-written situated context)
    C. late_chunked    - ADR-045 Alt-5 (Jina Late Chunking, token pooling)
    D. both            - A + B combined (stacks cleanly)

Each cell can additionally run through any of 3 reranker modes (controlled
by the ``RERANKER`` env var via ``reranker_factory.get_reranker``):
    - none          (no rerank)
    - heuristic     (SeniorLibrarianReranker)
    - cross_encoder (two-stage: heuristic pre-filter + bge-reranker-v2-m3)

producing up to 12 measurement rows per run.

Architecture
------------
The harness is **pure-Python compute + injected retriever**. It does not talk
to ChromaDB directly; the caller passes a ``Retriever`` callable that maps
``(query, collection) -> list[RetrievedChunk]``. This lets the unit tests
validate metrics math without requiring a populated vector DB, and lets the
production caller plug in whatever retrieval implementation they have
(SovereignChromaClient, raw chromadb client, hybrid engine, etc.).

The calibration corpus lives outside the harness, in
``config/retrieval/calibration_manifest.yaml`` (when populated). Each entry
is a ``CalibrationQuery`` with a query string and a set of doc_ids that
count as correct hits.

Metrics (all returned in ``CellResult``)
----------------------------------------
- ``recall_at_k``: |relevant ∩ top_k| / |relevant|. Primary metric — directly
  maps to ADR-045 acceptance (Recall@20 >= baseline + 20pct).
- ``precision_at_k``: |relevant ∩ top_k| / k. Complement to recall.
- ``mrr``: Mean Reciprocal Rank of the first relevant hit in the ranking.
- ``hit_at_k``: binary — did ANY relevant doc appear in top_k.

Output artifact
---------------
JSON report at ``artifacts/retrieval_baseline/c0_abcd_<ts>.json`` with:
    - per-cell aggregate metrics (mean across queries)
    - per-query breakdown so regressions are diagnosable
    - metadata: collection names, reranker mode, top_k, run timestamp

Invocation (deferred — env-blocked until ChromaDB has ingested collections)
---------------------------------------------------------------------------
::

    python tools/eval/retrieval_abcd_harness.py \\
        --manifest config/retrieval/calibration_manifest.yaml \\
        --top-k 20 \\
        --cell baseline --collection code_chunks_baseline \\
        --cell contextualized --collection code_chunks_contextualized \\
        --cell late_chunked --collection code_chunks_late \\
        --cell both --collection code_chunks_both

The script emits a table summary to stdout and writes the JSON artifact.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CalibrationQuery:
    """A single calibration-corpus query with known-relevant doc_ids.

    ``relevant_doc_ids`` is the ground-truth set. Any doc_id present in
    retrieval output that's in this set is a hit.
    """

    query: str
    relevant_doc_ids: frozenset[str]
    category: str = ""  # optional bucket for breakdown analysis


@dataclass(frozen=True)
class RetrievedChunk:
    """Minimal retrieval-result shape the harness consumes.

    Keeps the harness decoupled from whichever ChromaDB / hybrid-engine
    client the caller is using. Only ``doc_id`` is strictly required for
    metric computation; ``content`` is used when a reranker is wired in.
    """

    doc_id: str
    score: float = 0.0
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class Retriever(Protocol):
    """Callable protocol for cell retrievers.

    Implementations receive a query string and a collection name, and return
    a ranked list of ``RetrievedChunk`` (higher score = more relevant, caller
    is responsible for ordering).
    """

    def __call__(self, query: str, collection: str) -> list[RetrievedChunk]: ...


@dataclass
class CellConfig:
    """One measurement cell in the A/B grid.

    ``name`` is the user-facing label (baseline / contextualized / etc.);
    ``collection`` is the ChromaDB collection to query; ``reranker_mode`` is
    the value that will be set in the RERANKER env before the retriever is
    invoked (so reranker_factory.get_reranker() picks the right backend).
    """

    name: str
    collection: str
    reranker_mode: str = "none"  # "none" | "heuristic" | "cross_encoder"


@dataclass
class QueryResult:
    """Per-query metrics + the full retrieved ranking (for diagnostics)."""

    query: str
    category: str
    retrieved_doc_ids: list[str]
    relevant_doc_ids: list[str]
    hit_at_k: bool
    recall_at_k: float
    precision_at_k: float
    reciprocal_rank: float  # 0.0 when no relevant hit found


@dataclass
class CellResult:
    """Aggregate metrics for one cell across the full calibration corpus."""

    cell_name: str
    collection: str
    reranker_mode: str
    top_k: int
    num_queries: int
    mean_recall_at_k: float
    mean_precision_at_k: float
    mean_reciprocal_rank: float
    hit_rate_at_k: float
    per_query: list[QueryResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Metric math (pure functions — tested directly, no retriever needed)
# ---------------------------------------------------------------------------


def _recall_at_k(retrieved: Iterable[str], relevant: Iterable[str]) -> float:
    """|retrieved ∩ relevant| / |relevant|. Returns 0.0 when relevant is empty.

    The retrieved set is already truncated to top-k by the caller.
    """
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    retrieved_set = set(retrieved)
    return len(retrieved_set & relevant_set) / len(relevant_set)


def _precision_at_k(retrieved: list[str], relevant: Iterable[str], k: int) -> float:
    """|retrieved ∩ relevant| / k. Returns 0.0 when k == 0."""
    if k <= 0:
        return 0.0
    relevant_set = set(relevant)
    return sum(1 for d in retrieved[:k] if d in relevant_set) / k


def _reciprocal_rank(retrieved: list[str], relevant: Iterable[str]) -> float:
    """1 / (1-indexed position of first relevant hit). 0.0 if no hit.

    MRR is the mean of this across queries, so per-query this is just RR.
    """
    relevant_set = set(relevant)
    for i, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant_set:
            return 1.0 / i
    return 0.0


# ---------------------------------------------------------------------------
# Cell runner
# ---------------------------------------------------------------------------


def evaluate_cell(
    cell: CellConfig,
    queries: list[CalibrationQuery],
    retriever: Retriever,
    *,
    top_k: int = 20,
) -> CellResult:
    """Run every query through one cell and compute aggregate metrics.

    The caller is responsible for having already configured the environment
    (e.g. set ``RERANKER=<cell.reranker_mode>``, primed any model loads).
    The harness itself stays pure: it only calls the retriever and computes
    metrics from the returned rankings.
    """
    per_query: list[QueryResult] = []
    recall_sum = 0.0
    precision_sum = 0.0
    rr_sum = 0.0
    hits = 0

    for cq in queries:
        try:
            ranked = retriever(cq.query, cell.collection)
        except (RuntimeError, ValueError, OSError) as exc:
            # A single-query failure shouldn't nuke the whole cell run —
            # log, attribute a zero, move on. Downstream analysis can see
            # the zero and cross-reference the log to diagnose.
            logger.warning(
                "Retriever raised for query=%r cell=%s: %s; recording zero",
                cq.query,
                cell.name,
                exc,
            )
            ranked = []

        top = ranked[:top_k]
        retrieved_ids = [r.doc_id for r in top]
        relevant_list = sorted(cq.relevant_doc_ids)

        recall = _recall_at_k(retrieved_ids, cq.relevant_doc_ids)
        precision = _precision_at_k(retrieved_ids, cq.relevant_doc_ids, top_k)
        rr = _reciprocal_rank(retrieved_ids, cq.relevant_doc_ids)
        hit = rr > 0.0

        per_query.append(
            QueryResult(
                query=cq.query,
                category=cq.category,
                retrieved_doc_ids=retrieved_ids,
                relevant_doc_ids=relevant_list,
                hit_at_k=hit,
                recall_at_k=recall,
                precision_at_k=precision,
                reciprocal_rank=rr,
            )
        )
        recall_sum += recall
        precision_sum += precision
        rr_sum += rr
        if hit:
            hits += 1

    n = len(queries) or 1  # guard against zero-div; returned metrics are 0
    return CellResult(
        cell_name=cell.name,
        collection=cell.collection,
        reranker_mode=cell.reranker_mode,
        top_k=top_k,
        num_queries=len(queries),
        mean_recall_at_k=recall_sum / n,
        mean_precision_at_k=precision_sum / n,
        mean_reciprocal_rank=rr_sum / n,
        hit_rate_at_k=hits / n,
        per_query=per_query,
    )


def evaluate_all_cells(
    cells: list[CellConfig],
    queries: list[CalibrationQuery],
    retriever_factory: Callable[[CellConfig], Retriever],
    *,
    top_k: int = 20,
) -> list[CellResult]:
    """Run every cell through every query and return the grid of results.

    ``retriever_factory`` is a function that builds a ``Retriever`` for a
    given cell — the indirection lets the production caller set the
    RERANKER env var + warm caches before producing each cell's retriever.
    """
    results: list[CellResult] = []
    for cell in cells:
        logger.info("Evaluating cell: %s (collection=%s)", cell.name, cell.collection)
        retriever = retriever_factory(cell)
        results.append(evaluate_cell(cell, queries, retriever, top_k=top_k))
    return results


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def render_summary_table(results: list[CellResult]) -> str:
    """Plain-text table for stdout. Columns chosen for quick scan diffs."""
    header = (
        f"{'Cell':<18} {'Rerank':<14} {'Queries':>8} "
        f"{'Recall@K':>10} {'Prec@K':>10} {'MRR':>10} {'HitRate':>10}"
    )
    sep = "-" * len(header)
    lines = [header, sep]
    for r in results:
        lines.append(
            f"{r.cell_name:<18} {r.reranker_mode:<14} {r.num_queries:>8} "
            f"{r.mean_recall_at_k:>10.4f} {r.mean_precision_at_k:>10.4f} "
            f"{r.mean_reciprocal_rank:>10.4f} {r.hit_rate_at_k:>10.4f}"
        )
    return "\n".join(lines)


def render_json_report(
    results: list[CellResult],
    *,
    top_k: int,
    timestamp: str,
) -> dict[str, Any]:
    """JSON-serializable artifact. Paired with the summary table above."""
    return {
        "schema_version": "1.0",
        "generated_at_utc": timestamp,
        "top_k": top_k,
        "cells": [asdict(r) for r in results],
    }


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------


def load_manifest(path: Path) -> list[CalibrationQuery]:
    """Load a calibration manifest from JSON or YAML.

    Expected shape (JSON; YAML uses same keys):
        {
          "queries": [
            {"query": "...", "relevant_doc_ids": ["...", "..."], "category": "..."},
            ...
          ]
        }
    """
    if not path.exists():
        raise FileNotFoundError(f"Calibration manifest not found: {path}")
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError("PyYAML required for YAML manifests; install or switch to JSON") from exc
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)

    if not isinstance(data, dict) or "queries" not in data:
        raise ValueError(f"Manifest must be an object with 'queries' key; got {type(data).__name__}")
    out: list[CalibrationQuery] = []
    for entry in data["queries"]:
        out.append(
            CalibrationQuery(
                query=entry["query"],
                relevant_doc_ids=frozenset(entry.get("relevant_doc_ids", [])),
                category=entry.get("category", ""),
            )
        )
    return out


# ---------------------------------------------------------------------------
# CLI entry point (deferred execution — populated collections required)
# ---------------------------------------------------------------------------


def _build_default_retriever_factory(
    client: Any,
) -> Callable[[CellConfig], Retriever]:
    """Produce a retriever_factory bound to a SovereignChromaClient.

    Exposed as a separate function so unit tests can verify the glue code
    without needing a live Chroma instance; they pass in a MagicMock for
    ``client``.
    """
    import os  # noqa: PLC0415

    def factory(cell: CellConfig) -> Retriever:
        os.environ["RERANKER"] = cell.reranker_mode

        def retrieve(query: str, collection: str) -> list[RetrievedChunk]:
            # SovereignChromaClient.query returns dict[ids/documents/metadatas/distances].
            response = client.query(
                collection_name=collection,
                query_texts=[query],
                n_results=100,
            )
            # Flatten response to RetrievedChunk list, sorted by distance asc
            # (Chroma uses cosine DISTANCE — lower is better; we invert to
            # score so the caller can treat it uniformly).
            ids = (response.get("ids") or [[]])[0]
            docs = (response.get("documents") or [[]])[0]
            metas = (response.get("metadatas") or [[]])[0]
            dists = (response.get("distances") or [[]])[0]
            out: list[RetrievedChunk] = []
            for i, doc_id in enumerate(ids):
                content = docs[i] if i < len(docs) else ""
                meta = metas[i] if i < len(metas) else {}
                dist = dists[i] if i < len(dists) else 1.0
                out.append(
                    RetrievedChunk(
                        doc_id=str(doc_id),
                        score=1.0 - float(dist),
                        content=content,
                        metadata=meta or {},
                    )
                )
            return out

        return retrieve

    return factory


def main(argv: list[str] | None = None) -> int:
    """CLI entry — intended to be run after ingest pipeline has produced the
    4 cell collections. Emits JSON + stdout summary."""
    parser = argparse.ArgumentParser(
        description="4-cell A/B retrieval benchmark harness (ADR-045 acceptance gate)"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Calibration manifest (JSON or YAML) with queries + relevant_doc_ids",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=20,
        help="Top-K cutoff for recall/precision/hit metrics",
    )
    parser.add_argument(
        "--cell",
        action="append",
        required=True,
        metavar="NAME:COLLECTION:RERANKER",
        help=(
            "Cell spec 'name:collection:reranker_mode'. Repeat for multiple. "
            "reranker_mode ∈ {none, heuristic, cross_encoder}. "
            "Example: baseline:code_chunks_baseline:heuristic"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON report path. Defaults to artifacts/retrieval_baseline/c0_abcd_<ts>.json",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    queries = load_manifest(args.manifest)
    logger.info("Loaded %d calibration queries from %s", len(queries), args.manifest)

    cells: list[CellConfig] = []
    for spec in args.cell:
        parts = spec.split(":")
        if len(parts) != 3:
            parser.error(f"--cell must be 'name:collection:reranker_mode', got {spec!r}")
        cells.append(CellConfig(name=parts[0], collection=parts[1], reranker_mode=parts[2]))

    # Lazy import so unit tests don't pay chromadb import cost.
    from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str  # noqa: PLC0415
    from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient  # noqa: PLC0415

    client = SovereignChromaClient(persist_dir=canonical_persist_dir_str())
    retriever_factory = _build_default_retriever_factory(client)
    results = evaluate_all_cells(cells, queries, retriever_factory, top_k=args.top_k)

    # Print summary to stdout.
    print(render_summary_table(results))

    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_path = args.output or (Path("artifacts/retrieval_baseline") / f"c0_abcd_{timestamp}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = render_json_report(results, top_k=args.top_k, timestamp=timestamp)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Wrote report: %s", out_path)
    return 0


__all__ = [
    "CalibrationQuery",
    "CellConfig",
    "CellResult",
    "QueryResult",
    "RetrievedChunk",
    "Retriever",
    "evaluate_cell",
    "evaluate_all_cells",
    "load_manifest",
    "main",
    "render_json_report",
    "render_summary_table",
]


if __name__ == "__main__":
    sys.exit(main())
