"""Parent-Child Hydrator.

Stack Runner for canonical text fetching, expanding validated winners,
and parent-child relationship resolution.

Architecture reference:
  - 00C_index_materialization_runtime_handoff.md §Graph Hydrate
  - 00D_sparse_index_hybrid_merge.md §Hydration
  - C5_Retrieval_Prompt_Assembly.md §C0.3 Evidence Shaping

Changes from initial version:
  - _fetch_parent and _fetch_children wired to CanonicalStore via lineage graph.
  - Injectable canonical_store; graceful degradation when absent.
  - HydrationResult gains parent_id and child_ids fields for lineage tracing.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class HydrationResult:
    """Result of hydration with lineage context.

    Attributes
    ----------
    doc_id : str
        Identifier of the hydrated chunk.
    content : str
        Canonical raw text of the chunk.
    parent_id : str | None
        Identifier of the parent chunk/document if resolved.
    parent_content : str | None
        Raw text of the parent chunk (None when absent or not requested).
    child_ids : list[str]
        Identifiers of resolved child chunks.
    child_contents : list[str]
        Raw text of each child chunk (parallel to child_ids).
    is_expanded : bool
        True when at least one parent or child was successfully resolved.
    metadata : dict
        Hydration diagnostics: fetch flags, counts, store_used.
    """

    doc_id: str
    content: str
    parent_id: str | None = None
    parent_content: str | None = None
    child_ids: list[str] = field(default_factory=list)
    child_contents: list[str] = field(default_factory=list)
    is_expanded: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class ParentChildHydrator:
    """Hydrates documents with parent/child context from CanonicalStore.

    Expands validated recall winners with full lineage context by querying
    the ``CanonicalStore`` for parent_id and child edges.

    Args:
        canonical_store: Injected ``CanonicalStore`` for lineage lookups.
            ``None`` → no expansion (safe degradation, returns content as-is).
        max_expansion_depth: Maximum parent-traversal depth.
    """

    def __init__(
        self,
        canonical_store: Any | None = None,
        max_expansion_depth: int = 2,
    ) -> None:
        self._store = canonical_store
        self.max_expansion_depth = max_expansion_depth
        log.info(
            "ParentChildHydrator initialized (depth=%d, store=%s)",
            max_expansion_depth,
            canonical_store is not None,
        )

    def hydrate(
        self,
        doc_id: str,
        content: str,
        fetch_parent: bool = True,
        fetch_children: bool = False,
    ) -> HydrationResult:
        """Hydrate document with parent/child context.

        Args:
            doc_id: Document ID.
            content: Document content (already fetched by recall stage).
            fetch_parent: Whether to resolve the parent chunk.
            fetch_children: Whether to resolve child chunks.

        Returns:
            ``HydrationResult`` with expanded lineage context.
        """
        trace_id = f"hydrate_{doc_id}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "ParentChildHydrator.hydrate",
        )

        parent_id: str | None = None
        parent_content: str | None = None
        child_ids: list[str] = []
        child_contents: list[str] = []
        is_expanded = False
        store_used = self._store is not None

        if fetch_parent:
            parent_id, parent_content = self._fetch_parent(doc_id)
            if parent_content:
                is_expanded = True

        if fetch_children:
            child_ids, child_contents = self._fetch_children(doc_id)
            if child_contents:
                is_expanded = True

        result = HydrationResult(
            doc_id=doc_id,
            content=content,
            parent_id=parent_id,
            parent_content=parent_content,
            child_ids=child_ids,
            child_contents=child_contents,
            is_expanded=is_expanded,
            metadata={
                "fetch_parent": fetch_parent,
                "fetch_children": fetch_children,
                "has_parent": parent_content is not None,
                "child_count": len(child_contents),
                "store_used": store_used,
            },
        )

        _emit_records_telemetry_event(
            trace_id,
            "hydration",
            f"doc_{doc_id}_expanded_{is_expanded}",
        )

        log.debug(
            "Hydrated %s: parent=%s children=%d store=%s",
            doc_id,
            parent_id,
            len(child_contents),
            store_used,
        )
        return result

    def hydrate_batch(
        self,
        documents: list[dict[str, Any]],
        fetch_parent: bool = True,
    ) -> list[HydrationResult]:
        """Hydrate multiple documents.

        Args:
            documents: List of dicts with ``doc_id`` and ``content`` keys.
            fetch_parent: Whether to fetch parents.

        Returns:
            List of ``HydrationResult``.
        """
        results = []
        for doc in documents:
            result = self.hydrate(
                doc.get("doc_id", ""),
                doc.get("content", ""),
                fetch_parent=fetch_parent,
            )
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # Lineage resolution (CanonicalStore-backed)
    # ------------------------------------------------------------------

    def _fetch_parent(self, doc_id: str) -> tuple[str | None, str | None]:
        """Resolve and fetch the parent chunk via CanonicalStore lineage.

        Returns:
            Tuple of (parent_id, parent_content).  Both ``None`` when absent.
        """
        if self._store is None:
            return None, None

        try:
            unit = self._store.get_unit(doc_id)
        except (KeyError, OSError, ValueError) as exc:
            log.debug("CanonicalStore.get_unit(%s) failed: %s", doc_id, exc)
            return None, None

        if unit is None:
            return None, None

        parent_id: str | None = getattr(unit.lineage, "parent_id", None)
        if parent_id is None:
            return None, None

        try:
            parent_unit = self._store.get_unit(parent_id)
        except (KeyError, OSError, ValueError) as exc:
            log.debug("CanonicalStore.get_unit(%s) [parent] failed: %s", parent_id, exc)
            return parent_id, None

        if parent_unit is None:
            return parent_id, None

        return parent_id, parent_unit.content

    def _fetch_children(self, doc_id: str) -> tuple[list[str], list[str]]:
        """Resolve and fetch child chunks via CanonicalStore lineage graph.

        Returns:
            Tuple of (child_ids, child_contents).  Both empty when absent.
        """
        if self._store is None:
            return [], []

        try:
            lineage = self._store.get_lineage_graph(doc_id)
        except (KeyError, OSError, ValueError) as exc:
            log.debug("CanonicalStore.get_lineage_graph(%s) failed: %s", doc_id, exc)
            return [], []

        if not lineage:
            return [], []

        child_ids: list[str] = lineage.get("children", [])
        child_contents: list[str] = []

        for child_id in child_ids:
            try:
                child_unit = self._store.get_unit(child_id)
                child_contents.append(child_unit.content if child_unit else "")
            except (KeyError, OSError, ValueError) as exc:
                log.debug("CanonicalStore.get_unit(%s) [child] failed: %s", child_id, exc)
                child_contents.append("")

        return child_ids, child_contents


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_global_hydrator: ParentChildHydrator | None = None


def get_parent_child_hydrator() -> ParentChildHydrator:
    """Get or create the global hydrator (no store wired)."""
    global _global_hydrator
    if _global_hydrator is None:
        _global_hydrator = ParentChildHydrator()
    return _global_hydrator
