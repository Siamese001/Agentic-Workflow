from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from typing import Any, Iterable


@dataclass
class HybridSearchResult:
    chunk_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    combined_score: float = 0.0
    source: str = "hybrid"
    vector_score: float = 0.0
    lexical_score: float = 0.0


class HybridSearchEngine:
    """Minimal, deterministic hybrid-search shim with defensive guards.

    The implementation stays intentionally lightweight for offline regression tests,
    while still hardening the runtime path around malformed inputs, sqlite issues,
    and inconsistent Chroma-style payloads.
    """

    def __init__(self, chroma_client: Any | None = None, adg_db_path: str | None = None, top_k: int = 10):
        self.chroma_client = chroma_client
        self.adg_db_path = adg_db_path
        self.top_k = max(1, int(top_k))
        self._bge_model: Any | None = None
        self._adg_conn: sqlite3.Connection | None = None

    def __enter__(self) -> "HybridSearchEngine":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close_adg_connection()

    def __del__(self) -> None:
        try:
            self.close_adg_connection()
        except Exception:
            pass

    @staticmethod
    def _normalize_query(query: Any) -> str:
        if query is None:
            return ""
        return str(query).strip()

    @staticmethod
    def _ensure_mapping(value: Any) -> dict[str, Any]:
        return dict(value) if isinstance(value, dict) else {}

    def _ensure_adg_connection(self) -> sqlite3.Connection | None:
        if self._adg_conn is None and self.adg_db_path and Path(self.adg_db_path).exists():
            self._adg_conn = sqlite3.connect(self.adg_db_path)
            self._adg_conn.row_factory = sqlite3.Row
        return self._adg_conn

    def close_adg_connection(self) -> None:
        if self._adg_conn is not None:
            self._adg_conn.close()
            self._adg_conn = None

    def _fetch_rows(self, sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
        conn = self._ensure_adg_connection()
        if conn is None:
            return []
        try:
            cur = conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error:
            return []

    def get_node_by_id(self, node_id: int) -> dict[str, Any] | None:
        rows = self._fetch_rows("SELECT * FROM nodes WHERE id = ?", (node_id,))
        return rows[0] if rows else None

    def get_callers(self, node_id: int) -> list[dict[str, Any]]:
        return self._fetch_rows(
            "SELECT n.* FROM edges e JOIN nodes n ON n.id = e.src_id WHERE e.dst_id = ? AND e.relation_type = ?",
            (node_id, "calls"),
        )

    def get_callees(self, node_id: int) -> list[dict[str, Any]]:
        return self._fetch_rows(
            "SELECT n.* FROM edges e JOIN nodes n ON n.id = e.dst_id WHERE e.src_id = ? AND e.relation_type = ?",
            (node_id, "calls"),
        )

    def get_importers(self, node_id: int) -> list[dict[str, Any]]:
        return self._fetch_rows(
            "SELECT n.* FROM edges e JOIN nodes n ON n.id = e.src_id WHERE e.dst_id = ? AND e.relation_type = ?",
            (node_id, "imports"),
        )

    def get_imports(self, node_id: int) -> list[dict[str, Any]]:
        return self._fetch_rows(
            "SELECT n.* FROM edges e JOIN nodes n ON n.id = e.dst_id WHERE e.src_id = ? AND e.relation_type = ?",
            (node_id, "imports"),
        )

    def get_violations(self, node_id: int) -> list[dict[str, Any]]:
        conn = self._ensure_adg_connection()
        if conn is None:
            return []
        try:
            cur = conn.execute("SELECT * FROM violations WHERE node_id = ?", (node_id,))
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error:
            return []

    def _apply_governance_filters(
        self,
        results: list[HybridSearchResult],
        governance_filter: dict[str, Any],
    ) -> list[HybridSearchResult]:
        if not governance_filter:
            return list(results)
        filtered = list(results)
        layers = governance_filter.get("layers")
        if layers:
            allowed_layers = set(layers)
            filtered = [result for result in filtered if result.metadata.get("layer") in allowed_layers]
        entity_types = governance_filter.get("entity_types")
        if entity_types:
            allowed_types = set(entity_types)
            filtered = [result for result in filtered if result.metadata.get("entity_type") in allowed_types]
        return filtered

    def enforce_context_budget(
        self,
        results: list[HybridSearchResult],
        max_tokens: int,
        avg_tokens_per_chunk: int = 100,
    ) -> list[HybridSearchResult]:
        if avg_tokens_per_chunk <= 0:
            raise ValueError("avg_tokens_per_chunk must be positive")
        if max_tokens <= 0:
            return []
        allowed = max_tokens // avg_tokens_per_chunk
        if allowed >= len(results):
            return list(results)
        return sorted(results, key=lambda result: result.combined_score, reverse=True)[:allowed]

    # ------------------------------------------------------------------
    # Wave D2.3 — bounded ADG fan-in / fan-out expansion (WC-G05 / F12)
    # ------------------------------------------------------------------

    ADG_SYNTHETIC_PREFIX: str = "__adg__"
    """Prefix applied to every synthetic ADG-expansion ``chunk_id`` minted
    by :meth:`expand_results_with_adg`. Namespaces ADG neighbours so they
    never collide with real chunk ids or with the D2.2 ``__parent__:``
    synthetic parents.
    """

    ADG_DEFAULT_RELATIONS: tuple[str, ...] = ("callers", "callees")
    """Default relation set for :meth:`expand_results_with_adg`.

    D2.3 intentionally restricts expansion to call-graph fan-in + fan-out
    (Option 1 from the D2.3 HITL entry). ``callers`` uses
    :meth:`get_callers` (fan-in), ``callees`` uses :meth:`get_callees`
    (fan-out). The class still exposes :meth:`get_importers` and
    :meth:`get_imports` for other consumers, but this helper does not
    drive imports expansion — that is out of the D2.3 scope.
    """

    def expand_results_with_adg(
        self,
        results: list[HybridSearchResult],
        relation_types: list[str] | None = None,
        limit_per_relation: int = 3,
    ) -> list[HybridSearchResult]:
        """Expand each result to its ADG call-graph neighbours.

        Wave D2.3 (WC-G05 / F12). Uses the existing
        :meth:`get_callers` / :meth:`get_callees` ADG helpers on this
        engine — which already swallow :class:`sqlite3.Error` inside
        :meth:`_fetch_rows` — and wraps the call-site in an additional
        broad-exception guard so any unexpected ADG runtime failure
        degrades to a silent no-op for that relation.

        Expansion rule (one hop, bounded):

        * For every input result with a parseable integer
          ``metadata["node_id"]``, fetch up to ``limit_per_relation``
          neighbours per relation in ``relation_types``.
        * Only ``"callers"`` and ``"callees"`` are honoured (see
          :data:`ADG_DEFAULT_RELATIONS`). Unknown relation names are
          silently ignored so callers may pass extras without error.
        * Each neighbour becomes a synthetic :class:`HybridSearchResult`
          tagged ``source="adg"``. Its ``chunk_id`` is
          ``{ADG_SYNTHETIC_PREFIX}:{relation}:{neighbour_node_id}`` —
          deterministic and collision-free against real ids and the
          D2.2 ``__parent__:`` synthetics.
        * Deduplication: one synthetic row per unique
          ``(relation, neighbour_node_id)`` pair. Multiple parents
          referencing the same neighbour produce exactly one synthetic
          row, whose ``combined_score`` is the maximum parent score.
        * Depth is capped at 1 hop per parent. The ``limit_per_relation``
          cap ensures total fanout is bounded by
          ``len(results) * len(active_relations) * limit_per_relation``.
        * If ``metadata["node_id"]`` is missing, un-parseable, or the
          helper raises, the parent passes through unchanged.
        * ``limit_per_relation <= 0`` and empty ``results`` short-circuit
          to ``list(results)``.

        Output order: synthetic ADG neighbours first (in first-seen
        parent order, stable across invocations), followed by every
        input result in its original order. Original results are never
        reordered and never dropped.
        """
        if not results or limit_per_relation <= 0:
            return list(results)

        if relation_types is None:
            active: tuple[str, ...] = self.ADG_DEFAULT_RELATIONS
        else:
            active = tuple(r for r in relation_types if r in self.ADG_DEFAULT_RELATIONS)
        if not active:
            return list(results)

        fetchers: dict[str, Any] = {
            "callers": self.get_callers,
            "callees": self.get_callees,
        }

        existing_ids = {r.chunk_id for r in results}
        synth_by_key: dict[tuple[str, str], HybridSearchResult] = {}
        first_seen_order: list[tuple[str, str]] = []

        for parent_index, parent in enumerate(results):
            meta = parent.metadata or {}
            raw_node_id = meta.get("node_id")
            if raw_node_id is None:
                continue  # no ADG linkage — graceful no-op for this row
            try:
                parent_node_id = int(raw_node_id)
            except (TypeError, ValueError):
                continue  # un-parseable node_id -> no-op

            for relation in active:
                fetcher = fetchers[relation]
                try:
                    neighbours = fetcher(parent_node_id)
                except Exception:  # guardian: allow-broad-exception -- ADG helpers can raise sqlite.Error / RuntimeError; degrade to no-op per D2.3 contract
                    neighbours = []
                if not neighbours:
                    continue

                for neighbour in neighbours[:limit_per_relation]:
                    if not isinstance(neighbour, dict):
                        continue
                    neighbour_id_raw = neighbour.get("id")
                    if neighbour_id_raw is None:
                        continue
                    neighbour_id = str(neighbour_id_raw)
                    if not neighbour_id:
                        continue

                    adg_chunk_id = f"{self.ADG_SYNTHETIC_PREFIX}:{relation}:{neighbour_id}"
                    if adg_chunk_id in existing_ids:
                        continue  # already a real result

                    key = (relation, neighbour_id)
                    if key in synth_by_key:
                        # Dedup: update to max parent score so ranking is stable.
                        existing = synth_by_key[key]
                        if parent.combined_score > existing.combined_score:
                            synth_by_key[key] = HybridSearchResult(
                                chunk_id=existing.chunk_id,
                                content=existing.content,
                                metadata=existing.metadata,
                                combined_score=parent.combined_score,
                                source=existing.source,
                                vector_score=existing.vector_score,
                                lexical_score=existing.lexical_score,
                            )
                        continue

                    neighbour_name = (
                        neighbour.get("adg_name") or neighbour.get("name") or neighbour.get("file_path") or ""
                    )
                    neighbour_meta: dict[str, Any] = {
                        "node_id": neighbour_id,
                        "adg_relation": relation,
                        "adg_parent_chunk_id": parent.chunk_id,
                        "adg_parent_node_id": parent_node_id,
                        "is_synthetic_adg_expansion": True,
                        "first_child_index": parent_index,
                    }
                    for copy_key in ("adg_name", "name", "file_path", "layer", "entity_type"):
                        val = neighbour.get(copy_key)
                        if val is not None:
                            neighbour_meta[copy_key] = val

                    synth_by_key[key] = HybridSearchResult(
                        chunk_id=adg_chunk_id,
                        content=str(neighbour_name),
                        metadata=neighbour_meta,
                        combined_score=parent.combined_score,
                        source="adg",
                        vector_score=0.0,
                        lexical_score=0.0,
                    )
                    first_seen_order.append(key)

        synthetic = [synth_by_key[k] for k in first_seen_order]
        return synthetic + list(results)

    # ------------------------------------------------------------------
    # Wave D2.2 — collapse-group parent-child expansion (WC-G05 / F12)
    # ------------------------------------------------------------------

    PARENT_SYNTHETIC_PREFIX: str = "__parent__"
    """Prefix applied to every synthetic parent ``chunk_id`` minted by
    :meth:`expand_results_with_parent_child`.

    The prefix namespaces synthesised parents so callers can cheaply
    distinguish a lifted parent (empty content, inherited score) from a
    real retrieved chunk. It is intentionally an unlikely-to-collide
    string — production ``chunk_id`` values are hash / uuid flavoured.
    """

    PARENT_HEADING_SEPARATOR: str = " > "
    """Canonical separator used in ``metadata["heading_path"]`` across all
    ingestion pipelines (see ``tools/generate/ingestion/ingest_repo_evidence.py``
    line 320). Re-declared here so the parent-child expansion stays a
    pure-function operation on result metadata without reaching back into
    an ingestion-owned module.
    """

    def expand_results_with_parent_child(
        self,
        results: list[HybridSearchResult],
        max_depth: int = 1,
    ) -> list[HybridSearchResult]:
        """Lift each result to its collapse-group parent via ``heading_path``.

        Wave D2.2 (WC-G05 / F12). Operates only on metadata already present
        on the result list — no chroma query, no ADG call, no ingestion
        coupling. The expansion rule:

        * For every input result with BOTH a non-empty ``collapse_group``
          AND a ``heading_path`` containing at least 2 segments (separator
          :data:`PARENT_HEADING_SEPARATOR`), mint a synthetic parent
          ``HybridSearchResult`` whose ``heading_path`` is
          ``segments[:-1]`` and whose ``collapse_group`` matches the child.
          At depth :math:`d > 1`, grandparents (``segments[:-d]``) are
          lifted too, one synthetic row per depth level per unique parent.
        * Parents are deduplicated by ``(collapse_group, parent_heading_path)``
          — multiple children that share a parent contribute ONE synthetic
          row whose ``combined_score`` is the maximum child score.
        * If the parent is already present in ``results`` (keyed by the
          same ``(collapse_group, heading_path)`` pair), no synthetic row
          is emitted for it — the existing real result is preserved in
          place.
        * If linkage is missing (absent ``collapse_group``, absent
          ``heading_path``, single-segment ``heading_path``, empty parent
          path after stripping), the child is preserved without expansion
          and the function is a no-op for that row.
        * Output order: synthetic parents first, ordered by first-seen
          child index (stable across invocations with the same input),
          followed by every input result in its original order. Original
          results are never reordered and never dropped.
        * ``max_depth <= 0`` short-circuits to ``list(results)`` — the
          pre-D2.2 behavior — so callers can opt out without changing the
          signature.

        Args:
            results: Input result list, typically the output of
                :meth:`search` (possibly after RRF fusion).
            max_depth: Number of ancestor levels to synthesise per child.
                ``1`` = parents only (default). ``2`` = parents +
                grandparents. ``0`` or negative = no-op pass-through.

        Returns:
            A new list with synthetic parents prepended. The input list is
            not mutated.
        """
        if max_depth <= 0 or not results:
            return list(results)

        sep = self.PARENT_HEADING_SEPARATOR

        # Map (collapse_group, heading_path) -> existing result in the input
        # list. Used to skip synthesis when the parent is already present.
        existing_by_key: dict[tuple[str, str], HybridSearchResult] = {}
        for r in results:
            meta = r.metadata or {}
            cg = str(meta.get("collapse_group") or "")
            hp = str(meta.get("heading_path") or "")
            if cg and hp:
                existing_by_key.setdefault((cg, hp), r)

        parent_by_key: dict[tuple[str, str], HybridSearchResult] = {}
        parent_first_seen_order: list[tuple[str, str]] = []

        for child_index, child in enumerate(results):
            meta = child.metadata or {}
            collapse_group = str(meta.get("collapse_group") or "")
            heading_path = str(meta.get("heading_path") or "")
            if not collapse_group or not heading_path:
                continue  # linkage missing — graceful no-op
            segments = [s.strip() for s in heading_path.split(sep) if s.strip()]
            if len(segments) < 2:
                continue  # single-segment path has no parent to lift

            for depth in range(1, max_depth + 1):
                if len(segments) <= depth:
                    break
                parent_segments = segments[:-depth]
                if not parent_segments:
                    break
                parent_path = sep.join(parent_segments)
                key = (collapse_group, parent_path)

                # Parent already present as a real result — skip synthesis
                # entirely so we don't duplicate a real chunk.
                if key in existing_by_key:
                    continue

                if key in parent_by_key:
                    # Merge: keep the max combined_score of all children
                    # referring to this parent, preserving determinism.
                    existing = parent_by_key[key]
                    if child.combined_score > existing.combined_score:
                        parent_by_key[key] = HybridSearchResult(
                            chunk_id=existing.chunk_id,
                            content=existing.content,
                            metadata=existing.metadata,
                            combined_score=child.combined_score,
                            source=existing.source,
                            vector_score=existing.vector_score,
                            lexical_score=existing.lexical_score,
                        )
                    continue

                parent_id = f"{self.PARENT_SYNTHETIC_PREFIX}:{collapse_group}:{parent_path}"
                parent_by_key[key] = HybridSearchResult(
                    chunk_id=parent_id,
                    content="",
                    metadata={
                        "collapse_group": collapse_group,
                        "heading_path": parent_path,
                        "is_synthetic_parent": True,
                        "expansion_depth": depth,
                        "first_child_index": child_index,
                    },
                    combined_score=child.combined_score,
                    source="parent",
                    vector_score=0.0,
                    lexical_score=0.0,
                )
                parent_first_seen_order.append(key)

        synth_parents = [parent_by_key[k] for k in parent_first_seen_order]
        return synth_parents + list(results)

    def _generate_query_embedding(self, query: str) -> list[float] | None:
        if self._bge_model is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except ImportError:
                return None
            self._bge_model = SentenceTransformer("BAAI/bge-m3")
        encoded = self._bge_model.encode(query)
        if hasattr(encoded, "tolist"):
            encoded = encoded.tolist()
        if encoded and isinstance(encoded[0], list):
            encoded = encoded[0]
        return [float(value) for value in encoded]

    @staticmethod
    def _coerce_query_payload(raw: Any, key: str) -> list[Any]:
        value = raw.get(key) if isinstance(raw, dict) else None
        if value is None:
            return []
        if value and isinstance(value[0], list):
            return list(value[0])
        if isinstance(value, list):
            return list(value)
        return []

    def _collection_query(
        self,
        collection: Any,
        query: str,
        query_embedding: list[float] | None,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding] if query_embedding is not None else None,
            "query_texts": [query],
            "n_results": self.top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where
        try:
            return collection.query(**kwargs)
        except TypeError:
            return collection.query(query_texts=[query], n_results=self.top_k)

    @staticmethod
    def _apply_authority_rerank(
        results: list["HybridSearchResult"],
        authority_bonus: float = 0.15,
    ) -> list["HybridSearchResult"]:
        """Boost combined_score by authority_level metadata when present.

        authority_level is a float in [0.0, 1.0] stored in chunk metadata.
        Bonus = authority_bonus * authority_level, added to combined_score.
        Results missing authority_level receive no bonus (safe fallback).
        """
        reranked = []
        for r in results:
            level = r.metadata.get("authority_level")
            if level is not None:
                try:
                    bonus = authority_bonus * float(level)
                except (TypeError, ValueError):
                    bonus = 0.0
            else:
                bonus = 0.0
            reranked.append(
                HybridSearchResult(
                    chunk_id=r.chunk_id,
                    content=r.content,
                    metadata=r.metadata,
                    combined_score=r.combined_score + bonus,
                    source=r.source,
                    vector_score=r.vector_score,
                    lexical_score=r.lexical_score,
                )
            )
        return reranked

    def _vector_search(
        self,
        query: str,
        query_embedding: list[float] | None,
        collection_name: str,
        governance_filter: dict[str, Any] | None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[HybridSearchResult] | dict:
        if self.chroma_client is None:
            return {}
        normalized_query = self._normalize_query(query)
        if query_embedding is None:
            query_embedding = self._generate_query_embedding(normalized_query)
        try:
            collection = self.chroma_client.get_collection(collection_name)
        except Exception:  # guardian: allow-broad-exception -- chromadb raises collection-not-found as an untyped internal exception across client versions
            return []
        raw = self._collection_query(collection, normalized_query, query_embedding, where=metadata_filter)
        ids = self._coerce_query_payload(raw, "ids")
        docs = self._coerce_query_payload(raw, "documents")
        metas = self._coerce_query_payload(raw, "metadatas")
        distances = self._coerce_query_payload(raw, "distances")

        results: list[HybridSearchResult] = []
        for idx, chunk_id in enumerate(ids):
            distance = float(distances[idx]) if idx < len(distances) else 1.0
            score = max(1e-9, 1.0 - distance)
            content = str(docs[idx]) if idx < len(docs) else ""
            metadata = self._ensure_mapping(metas[idx] if idx < len(metas) else {})
            results.append(
                HybridSearchResult(
                    chunk_id=str(chunk_id),
                    content=content,
                    metadata=metadata,
                    combined_score=score,
                    source="vector",
                    vector_score=score,
                    lexical_score=0.0,
                )
            )
        return self._apply_governance_filters(results, governance_filter or {})

    @staticmethod
    def _deduplicate_results(results: Iterable[HybridSearchResult]) -> list[HybridSearchResult]:
        by_id: dict[str, HybridSearchResult] = {}
        for result in results:
            current = by_id.get(result.chunk_id)
            if current is None or result.combined_score > current.combined_score:
                by_id[result.chunk_id] = result
        return list(by_id.values())

    # ------------------------------------------------------------------
    # Wave D2.1 — BM25 lexical backend + RRF fusion (WC-G05 / F12)
    # ------------------------------------------------------------------

    RRF_K: int = 60
    """Reciprocal Rank Fusion constant ``k`` (Cormack et al., 2009).

    Used exclusively by :meth:`_rrf_fuse` when merging the dense and lexical
    result lists. The value 60 is the canonical default across the hybrid
    retrieval literature; it balances the contribution of high-ranked items
    without letting any single list dominate the fused ordering.
    """

    def _lexical_search(
        self,
        query: str,
        collection_name: str,
        governance_filter: dict[str, Any] | None,
    ) -> list[HybridSearchResult]:
        """Run the BM25 / FTS5 lexical backend for *collection_name*.

        Returns an empty list (not a dict) when:

        * The ``bm25_store`` module is not importable (optional dependency
          ``rank_bm25`` missing at module import time).
        * The collection has no sparse sidecar (``get_sparse_index`` returns
          ``None`` — only the 8 canonical collections are indexed).
        * The sidecar exists but the query is empty / yields no hits.
        * The sidecar raises at query time.

        This matches the dense-search convention of returning ``[]`` on any
        soft failure so :meth:`search` can cleanly choose between
        dense-only, lexical-only, and fused code paths.
        """
        normalized_query = self._normalize_query(query)
        if not normalized_query:
            return []
        try:
            from agentic_core.L4_state.utils.memory.bm25_store import (
                get_sparse_index,
            )
        except ImportError:
            # rank_bm25 not installed or bm25_store module load failed.
            return []
        try:
            index = get_sparse_index(collection_name)
        except Exception:  # guardian: allow-broad-exception -- sparse backend can raise untyped sqlite errors across versions during sidecar probing
            return []
        if index is None or not index.is_available:
            return []
        try:
            hits = index.search(normalized_query, top_k=self.top_k)
        except (
            Exception
        ):  # guardian: allow-broad-exception -- FTS5 query layer raises untyped sqlite errors across versions
            return []
        results: list[HybridSearchResult] = []
        for hit in hits or []:
            if not isinstance(hit, dict):
                continue
            score = 0.0
            try:
                score = float(hit.get("score", 0.0))
            except (TypeError, ValueError):
                score = 0.0
            results.append(
                HybridSearchResult(
                    chunk_id=str(hit.get("id", "")),
                    content=str(hit.get("content", "")),
                    metadata=self._ensure_mapping(hit.get("metadata", {})),
                    combined_score=score,
                    source="lexical",
                    vector_score=0.0,
                    lexical_score=score,
                )
            )
        return self._apply_governance_filters(results, governance_filter or {})

    @classmethod
    def _rrf_fuse(
        cls,
        vector_results: list[HybridSearchResult],
        lexical_results: list[HybridSearchResult],
        k: int | None = None,
    ) -> list[HybridSearchResult]:
        """Reciprocal Rank Fusion of dense and lexical result lists.

        For every chunk appearing in either input list, the fused score is::

            rrf_score = sum_{L in {vector, lexical}} 1.0 / (k + rank_L(chunk))

        A chunk absent from a list contributes 0 from that list. Input lists
        are consumed in their current order (caller is responsible for any
        pre-sort); positions are 1-based.

        The preserved-metadata side is the vector hit when both are present
        (dense hits typically carry richer Chroma metadata), with a fallback
        to the lexical hit otherwise. The ``source`` field tags each fused
        row as ``"hybrid"`` (both lists), ``"vector"`` (dense only), or
        ``"lexical"`` (BM25 only). Per-list scores (``vector_score``,
        ``lexical_score``) are preserved so downstream re-rankers (e.g.
        ``apply_authority_rerank``) retain their existing semantics.

        Returns a list sorted by fused score descending, with ``chunk_id``
        ascending as a deterministic tie-breaker so the output is stable
        across invocations with identical inputs.
        """
        rrf_k = cls.RRF_K if k is None else int(k)
        vec_rank: dict[str, int] = {}
        for i, r in enumerate(vector_results):
            # Keep the first-seen rank per chunk to match deduplication.
            if r.chunk_id not in vec_rank:
                vec_rank[r.chunk_id] = i + 1
        lex_rank: dict[str, int] = {}
        for i, r in enumerate(lexical_results):
            if r.chunk_id not in lex_rank:
                lex_rank[r.chunk_id] = i + 1

        vec_by_id = {r.chunk_id: r for r in vector_results}
        lex_by_id = {r.chunk_id: r for r in lexical_results}

        fused: list[HybridSearchResult] = []
        for chunk_id in set(vec_rank) | set(lex_rank):
            score = 0.0
            if chunk_id in vec_rank:
                score += 1.0 / (rrf_k + vec_rank[chunk_id])
            if chunk_id in lex_rank:
                score += 1.0 / (rrf_k + lex_rank[chunk_id])

            vr = vec_by_id.get(chunk_id)
            lr = lex_by_id.get(chunk_id)
            base = vr if vr is not None else lr
            if base is None:
                # set-union guarantees membership in at least one map, so
                # this branch is unreachable in normal flow; kept for a
                # defensive MyPy narrowing.
                continue

            if vr is not None and lr is not None:
                src = "hybrid"
            elif vr is not None:
                src = "vector"
            else:
                src = "lexical"

            fused.append(
                HybridSearchResult(
                    chunk_id=chunk_id,
                    content=base.content,
                    metadata=base.metadata,
                    combined_score=score,
                    source=src,
                    vector_score=vr.vector_score if vr is not None else 0.0,
                    lexical_score=lr.lexical_score if lr is not None else 0.0,
                )
            )

        # Primary sort: RRF score descending. Secondary sort: chunk_id
        # ascending — guarantees deterministic ordering when two chunks
        # happen to earn identical RRF scores (same rank in both lists).
        fused.sort(key=lambda r: (-r.combined_score, r.chunk_id))
        return fused

    def search(
        self,
        query: str,
        query_embedding: list[float] | None = None,
        collection_name: str = "code_chunks",
        governance_filter: dict[str, Any] | None = None,
        metadata_filter: dict[str, Any] | None = None,
        authority_rerank: bool = False,
        collapse_group_dedup_max: int | None = None,
        enable_lexical: bool = False,
    ) -> list[HybridSearchResult]:
        """Hybrid search entry point.

        Wave D2.1 (WC-G05 / F12) wires a BM25 lexical backend alongside the
        existing dense path and fuses the two lists with Reciprocal Rank
        Fusion when ``enable_lexical`` is ``True``. The new kwarg defaults
        to ``False`` so existing callers are byte-identical unchanged — no
        behavioral change reaches the 14 downstream test modules or the
        141 call-sites surveyed during the D2.1 entry review.

        When ``enable_lexical`` is ``True``:

        * Dense-only fallback: BM25 empty -> the dense list is returned
          verbatim (existing code path).
        * BM25-only fallback: dense empty -> the lexical list is returned
          with ``combined_score`` preserved from the BM25 scores.
        * Both populated -> :meth:`_rrf_fuse` merges the two into a single
          stable ranked list (ties broken by ``chunk_id`` ascending).

        All downstream post-processing (``authority_rerank``,
        ``collapse_group_dedup``) runs on the fused / fallback list exactly
        as before.
        """
        vector_results = self._vector_search(
            query, query_embedding, collection_name, governance_filter, metadata_filter
        )
        # The dict sentinel is the "chroma_client is None" signal. Normalize
        # it to an empty list so the lexical-only fallback can still fire
        # when BM25 is enabled on an engine without a dense backend.
        if isinstance(vector_results, dict):
            vector_results = []

        lexical_results: list[HybridSearchResult] = []
        if enable_lexical:
            lexical_results = self._lexical_search(query, collection_name, governance_filter)

        if not vector_results and not lexical_results:
            return []

        if enable_lexical and vector_results and lexical_results:
            # Both backends produced rows — fuse via RRF.
            deduped = self._rrf_fuse(
                self._deduplicate_results(vector_results),
                self._deduplicate_results(lexical_results),
            )
        elif enable_lexical and not vector_results:
            # BM25-only fallback.
            deduped = self._deduplicate_results(lexical_results)
        else:
            # Dense-only path (either enable_lexical is False or BM25 was
            # empty / unavailable). Byte-for-byte preserves the pre-D2.1
            # behavior for all existing callers.
            deduped = self._deduplicate_results(vector_results)

        if authority_rerank:
            deduped = self._apply_authority_rerank(deduped)
        results = sorted(
            deduped,
            key=lambda result: (result.combined_score, result.vector_score, result.lexical_score),
            reverse=True,
        )
        if collapse_group_dedup_max is not None:
            from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
                collapse_group_dedup,
            )

            results = collapse_group_dedup(results, max_per_group=collapse_group_dedup_max)
        return results


_global_hybrid_engine: HybridSearchEngine | None = None


def get_global_hybrid_engine() -> HybridSearchEngine:
    global _global_hybrid_engine
    if _global_hybrid_engine is None:
        try:
            import chromadb

            client = chromadb.PersistentClient()
        except Exception:
            client = None
        _global_hybrid_engine = HybridSearchEngine(chroma_client=client)
    return _global_hybrid_engine


def hybrid_search(
    query: str,
    query_embedding: list[float] | None = None,
    collection_name: str = "code_chunks",
) -> list[HybridSearchResult]:
    return get_global_hybrid_engine().search(query, query_embedding, collection_name)
