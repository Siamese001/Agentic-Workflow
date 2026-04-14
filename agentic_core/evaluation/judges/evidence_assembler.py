"""Evidence Assembler — collects ADG + source + runtime data for judge evaluation.

Bridges the gap between raw ADG data (SQLite edges, Redis cache) and the
structured EvidenceBundle that judges consume. Supports both SQLite-direct
and Redis-backed evidence collection.

Usage::

    assembler = EvidenceAssembler(
        repo_root="c:/Git/Agentic-Workflow",
        adg_db_path="artifacts/adg/adg_indexed_03172026_0002.sqlite",
    )
    bundle = assembler.assemble("agentic_core/L2_execution/providers.py",
                                relations=["imports", "calls", "antipattern"])
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from agentic_core.evaluation.judges.source_retriever import SourceRetriever
from agentic_core.evaluation.judges.types import (
    EvidenceBundle,
    SourceSnippet,
)
from tqdm import tqdm

_log = logging.getLogger(__name__)


class EvidenceAssembler:
    """Assembles structured evidence bundles from ADG SQLite and source code.

    Collects:
    - ADG edges by relation type for a target module
    - Source code snippets at ADG-referenced line numbers
    - Module metadata (layer, entity_type, node count)
    """

    def __init__(
        self,
        repo_root: str,
        adg_db_path: str = "",
    ) -> None:
        self._repo_root = repo_root
        self._adg_db_path = adg_db_path
        self._retriever = SourceRetriever(repo_root)

    def _connect_adg(self) -> sqlite3.Connection | None:
        """Connect to the ADG SQLite database."""
        if not self._adg_db_path:
            _log.warning("[EvidenceAssembler] No ADG DB path configured")
            return None

        db_path = Path(self._adg_db_path)
        if not db_path.is_file():
            # Try relative to repo root
            db_path = Path(self._repo_root) / self._adg_db_path
            if not db_path.is_file():
                _log.warning("[EvidenceAssembler] ADG DB not found: %s", self._adg_db_path)
                return None

        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _get_adg_digest(self, conn: sqlite3.Connection) -> str:
        """Extract the ADG digest from the database filename or metadata."""
        try:
            db_name = Path(conn.execute("PRAGMA database_list").fetchone()[2]).stem
            return db_name
        except (ValueError, TypeError, RuntimeError) as e:
            return ""

    def _get_module_node_id(self, conn: sqlite3.Connection, module_path: str) -> int | None:
        """Find the ADG node ID for a module by its resolved_path or adg_name."""
        row = conn.execute(
            "SELECT id FROM nodes WHERE resolved_path = ? OR adg_name = ? LIMIT 1",
            (module_path, module_path),
        ).fetchone()
        if row:
            return row["id"]

        # Try partial match on resolved_path ending
        row = conn.execute(
            "SELECT id FROM nodes WHERE resolved_path LIKE ? LIMIT 1",
            (f"%{module_path}",),
        ).fetchone()
        return row["id"] if row else None

    def _get_module_metadata(
        self,
        conn: sqlite3.Connection,
        node_id: int,
    ) -> dict[str, Any]:
        """Get module metadata from the nodes table."""
        row = conn.execute(
            "SELECT adg_name, entity_type, layer, identity_kind, confidence, resolved_path FROM nodes WHERE id = ?",
            (node_id,),
        ).fetchone()
        if not row:
            return {}
        return {
            "adg_name": row["adg_name"],
            "entity_type": row["entity_type"],
            "layer": row["layer"],
            "identity_kind": row["identity_kind"],
            "confidence": row["confidence"],
            "resolved_path": row["resolved_path"],
        }

    def _get_edges_by_relation(
        self,
        conn: sqlite3.Connection,
        node_id: int,
        relation: str,
        direction: str = "outgoing",
    ) -> list[dict[str, Any]]:
        """Get all edges of a given relation type for a node.

        Args:
            direction: "outgoing" (src=node) or "incoming" (dst=node) or "both"
        """
        results: list[dict[str, Any]] = []

        if direction in ("outgoing", "both"):
            rows = conn.execute(
                """SELECT e.relation_type, e.edge_kind, e.source_file, e.line_no, e.symbol,
                          n.adg_name AS target_name, n.layer AS target_layer, n.resolved_path AS target_path
                   FROM edges e
                   JOIN nodes n ON e.dst_id = n.id
                   WHERE e.src_id = ? AND e.relation_type = ?""",
                (node_id, relation),
            ).fetchall()
            for r in tqdm(rows, desc="Processing", unit="item"):
                results.append(
                    {
                        "direction": "outgoing",
                        "relation_type": r["relation_type"],
                        "edge_kind": r["edge_kind"],
                        "source_file": r["source_file"],
                        "line_no": r["line_no"],
                        "symbol": r["symbol"],
                        "target_name": r["target_name"],
                        "target_layer": r["target_layer"],
                        "target_path": r["target_path"],
                    },
                )

        if direction in ("incoming", "both"):
            rows = conn.execute(
                """SELECT e.relation_type, e.edge_kind, e.source_file, e.line_no, e.symbol,
                          n.adg_name AS source_name, n.layer AS source_layer, n.resolved_path AS source_path
                   FROM edges e
                   JOIN nodes n ON e.src_id = n.id
                   WHERE e.dst_id = ? AND e.relation_type = ?""",
                (node_id, relation),
            ).fetchall()
            for r in tqdm(rows, desc="Processing", unit="item"):
                results.append(
                    {
                        "direction": "incoming",
                        "relation_type": r["relation_type"],
                        "edge_kind": r["edge_kind"],
                        "source_file": r["source_file"],
                        "line_no": r["line_no"],
                        "symbol": r["symbol"],
                        "source_name": r["source_name"],
                        "source_layer": r["source_layer"],
                        "source_path": r["source_path"],
                    },
                )

        return results

    def _collect_source_snippets(
        self,
        edges: dict[str, list[dict[str, Any]]],
        module_path: str,
    ) -> tuple[SourceSnippet, ...]:
        """Extract source snippets at edge-referenced line numbers."""
        seen: set[tuple[str, int]] = set()
        snippets: list[SourceSnippet] = []

        for _rel, edge_list in tqdm(edges.items(), desc="Processing", unit="item"):
            for edge in tqdm(edge_list, desc="Processing", unit="item"):
                file_path = edge.get("source_file", "") or module_path
                line_no = edge.get("line_no", 0)
                if not file_path or line_no <= 0:
                    continue
                key = (file_path, line_no)
                if key in seen:
                    continue
                seen.add(key)

                snippet = self._retriever.get_context(
                    file_path,
                    line_no,
                    window=5,
                )
                if snippet:
                    snippets.append(snippet)

        return tuple(snippets)

    def assemble(
        self,
        module_path: str,
        relations: list[str] | None = None,
        include_source: bool = True,
        direction: str = "outgoing",
    ) -> EvidenceBundle:
        """Assemble a complete evidence bundle for a module.

        Args:
            module_path: Relative path to the target module.
            relations: ADG relation types to collect. If None, collects common ones.
            include_source: Whether to read source code at edge line numbers.
            direction: Edge direction — "outgoing", "incoming", or "both".

        Returns:
            EvidenceBundle with all collected evidence.
        """
        if relations is None:
            relations = [
                "imports",
                "calls",
                "antipattern",
                "violates",
                "records_execution_trace",
                "applies_guardrail",
            ]

        conn = self._connect_adg()
        if conn is None:
            return EvidenceBundle(target=module_path)

        try:
            adg_digest = self._get_adg_digest(conn)

            node_id = self._get_module_node_id(conn, module_path)
            if node_id is None:
                _log.warning(
                    "[EvidenceAssembler] Module not found in ADG: %s",
                    module_path,
                )
                return EvidenceBundle(target=module_path, adg_digest=adg_digest)

            metadata = self._get_module_metadata(conn, node_id)

            adg_edges: dict[str, list[dict[str, Any]]] = {}
            for rel in relations:
                edges = self._get_edges_by_relation(conn, node_id, rel, direction)
                if edges:
                    adg_edges[rel] = edges

            snippets: tuple[SourceSnippet, ...] = ()
            if include_source:
                snippets = self._collect_source_snippets(adg_edges, module_path)

            return EvidenceBundle(
                target=module_path,
                adg_edges=adg_edges,
                source_snippets=snippets,
                adg_digest=adg_digest,
                module_metadata=metadata,
            )
        finally:
            conn.close()

    def assemble_for_rubric(
        self,
        module_path: str,
        rubric_evidence_requirements: list[dict[str, str]],
        include_source: bool = True,
    ) -> EvidenceBundle:
        """Assemble evidence specifically for a rubric's requirements.

        Args:
            module_path: Relative path to the target module.
            rubric_evidence_requirements: List of requirement dicts with
                'evidence_type' and 'relation' keys.
            include_source: Whether to include source code snippets.

        Returns:
            EvidenceBundle matching the rubric's needs.
        """
        relations = []
        needs_source = False

        for req in rubric_evidence_requirements:
            ev_type = req.get("evidence_type", "")
            if ev_type == "adg_edge" and req.get("relation"):
                relations.append(req["relation"])
            elif ev_type == "source_code":
                needs_source = True

        return self.assemble(
            module_path=module_path,
            relations=relations if relations else None,
            include_source=include_source or needs_source,
        )


__all__ = ["EvidenceAssembler"]
