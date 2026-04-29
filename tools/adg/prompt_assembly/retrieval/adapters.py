"""Retrieval Adapters — fetch raw data from canonical ADG sources.

Six adapters, each returning EvidenceItem objects:
    SQLiteAdapter         — nodes, edges, violations from adg_indexed_*.sqlite
    ReportAdapter         — parsed JSON reports (provenance, closure, edge density, layer coverage)
    RatchetAdapter        — p1/p2 ratchet ceilings and burndown table
    GraphDBAdapter        — NetworkX queries (blast radius, paths, neighborhoods) — DERIVED
    InfraWiringAdapter    — infra wiring SQL view results
    StructuralAdapter     — burndown, blast radius, seams, centrality from structural_outputs

All adapters:
    - Preserve provenance (source_artifact, snapshot_id, commit_sha, digests)
    - Tag derived evidence (is_derived=True for graph DB)
    - Handle missing artifacts gracefully (return empty items with gaps)
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import re

from tqdm import tqdm

from tools.adg.prompt_assembly.contracts import EvidenceItem

_ROOT = Path(__file__).resolve().parents[4]
_ADG_DIR = _ROOT / "artifacts" / "adg"


def _mtime_iso(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _artifact_sort_key(path: Path) -> tuple[datetime, float, str]:
    match = re.search(r"_(\d{8})_(\d{4})(?:\.|$)", path.name)
    if match:
        try:
            ts = datetime.strptime("".join(match.groups()), "%m%d%Y%H%M").replace(tzinfo=timezone.utc)
            return (ts, path.stat().st_mtime, path.name)
        except ValueError:
            pass
    return (datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc), path.stat().st_mtime, path.name)


def _find_latest(pattern: str) -> Path | None:
    """Find the latest file matching a glob pattern in artifacts/adg/."""
    candidates = list(_ADG_DIR.glob(pattern))
    return max(candidates, key=_artifact_sort_key) if candidates else None


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": "json_decode_error", "artifact": path.name, "message": str(exc)}


def _extract_snapshot_id(filename: str) -> str:
    """Extract timestamp portion from artifact filename like 'adg_snapshot_04082026_1914.json'."""
    parts = filename.replace(".json", "").replace(".sqlite", "").split("_")
    if len(parts) >= 3:
        return "_".join(parts[-2:])
    return filename


# ---------------------------------------------------------------------------
# SQLite Adapter
# ---------------------------------------------------------------------------


class SQLiteAdapter:
    """Fetch data from adg_indexed_*.sqlite."""

    def __init__(self, sqlite_path: Path | None = None):
        self.path = sqlite_path or _find_latest("adg_indexed_*.sqlite")

    def _evidence(self, data: dict[str, Any], row_refs: list[str] | None = None) -> EvidenceItem:
        snapshot_id = _extract_snapshot_id(self.path.name) if self.path else ""
        return EvidenceItem(
            source_artifact=self.path.name if self.path else "MISSING",
            source_type="sqlite",
            snapshot_id=snapshot_id,
            row_references=row_refs or [],
            freshness=_mtime_iso(self.path),
            data=data,
        )

    def fetch_violations(self, limit: int = 50) -> EvidenceItem:
        """Fetch violation edges from the edges table."""
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing", "violations": []})
        with sqlite3.connect(str(self.path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT src_id, dst_id, source_file, line_no, relation_type, edge_kind "
                "FROM edges WHERE relation_type = 'violates' LIMIT ?",
                (limit,),
            ).fetchall()
        violations = [dict(r) for r in rows]
        return self._evidence(
            {"violations": violations, "count": len(violations)},
            row_refs=[f"edges:violates:{i}" for i in range(len(violations))],
        )

    def fetch_antipatterns_by_severity(self) -> EvidenceItem:
        """Fetch anti-pattern counts grouped by severity."""
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        with sqlite3.connect(str(self.path)) as conn:
            rows = conn.execute(
                "SELECT severity, COUNT(*) as cnt FROM violations "
                "WHERE category = 'antipattern' GROUP BY severity"
            ).fetchall()
        severity_map = {r[0]: r[1] for r in rows}
        return self._evidence({"by_severity": severity_map})

    def fetch_unresolved_imports(self, limit: int = 50) -> EvidenceItem:
        """Fetch unresolved import nodes."""
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        with sqlite3.connect(str(self.path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, adg_name, layer, resolved_path FROM nodes "
                "WHERE identity_kind = 'unresolved' LIMIT ?",
                (limit,),
            ).fetchall()
        unresolved = [dict(r) for r in rows]
        return self._evidence(
            {"unresolved_imports": unresolved, "count": len(unresolved)},
            row_refs=[f"nodes:unresolved:{i}" for i in range(len(unresolved))],
        )

    def fetch_fan_in_hotspots(self, top_n: int = 20) -> EvidenceItem:
        """Fetch top fan-in hotspots (most-imported modules)."""
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        with sqlite3.connect(str(self.path)) as conn:
            rows = conn.execute(
                "SELECT dst_id, COUNT(*) as fan_in FROM edges "
                "WHERE relation_type = 'imports' "
                "GROUP BY dst_id ORDER BY fan_in DESC LIMIT ?",
                (top_n,),
            ).fetchall()
        hotspots = [{"node_id": r[0], "fan_in": r[1]} for r in rows]
        return self._evidence({"fan_in_hotspots": hotspots})

    def fetch_fan_out_hotspots(self, top_n: int = 20) -> EvidenceItem:
        """Fetch top fan-out hotspots (modules importing the most)."""
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        with sqlite3.connect(str(self.path)) as conn:
            rows = conn.execute(
                "SELECT src_id, COUNT(*) as fan_out FROM edges "
                "WHERE relation_type = 'imports' "
                "GROUP BY src_id ORDER BY fan_out DESC LIMIT ?",
                (top_n,),
            ).fetchall()
        hotspots = [{"node_id": r[0], "fan_out": r[1]} for r in rows]
        return self._evidence({"fan_out_hotspots": hotspots})

    def fetch_node_edge_counts(self) -> EvidenceItem:
        """Fetch total node and edge counts from the database."""
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        with sqlite3.connect(str(self.path)) as conn:
            node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
            edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        return self._evidence({"db_node_count": node_count, "db_edge_count": edge_count})

    def fetch_infra_wiring_views(self, limit: int = 50) -> EvidenceItem:
        """Fetch infra wiring violation view results (if views exist)."""
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        results: dict[str, Any] = {}
        with sqlite3.connect(str(self.path)) as conn:
            conn.row_factory = sqlite3.Row
            for view_name in tqdm(
                [
                    "v_infra_spread",
                    "v_write_bypass",
                    "v_provider_bypass",
                    "v_infra_callers",
                    "v_process_boundary",
                ],
                desc="Querying views",
                unit="view",
                leave=False,
            ):
                try:
                    rows = conn.execute(f"SELECT * FROM {view_name} LIMIT ?", (limit,)).fetchall()
                    results[view_name] = [dict(r) for r in rows]
                except sqlite3.OperationalError:
                    results[view_name] = {"error": f"view_{view_name}_not_found"}
        return self._evidence(results, row_refs=list(results.keys()))


# ---------------------------------------------------------------------------
# Report Adapter
# ---------------------------------------------------------------------------


class ReportAdapter:
    """Fetch parsed JSON reports."""

    def _load_report(self, pattern: str) -> tuple[dict[str, Any], str, Path | None]:
        """Load the latest report matching a pattern. Returns (data, filename, path)."""
        path = _find_latest(pattern)
        if path and path.exists():
            return _load_json(path), path.name, path
        return {"error": "report_missing", "pattern": pattern}, "MISSING", None

    def _evidence(
        self, data: dict[str, Any], filename: str, path: Path | None, source_type: str = "json_report"
    ) -> EvidenceItem:
        return EvidenceItem(
            source_artifact=filename,
            source_type=source_type,
            snapshot_id=_extract_snapshot_id(filename),
            artifact_digest=data.get("artifact_digest", ""),
            scanner_digest=data.get("scanner_digest", ""),
            commit_sha=data.get("commit_sha", ""),
            freshness=_mtime_iso(path),
            data=data,
        )

    def fetch_provenance(self) -> EvidenceItem:
        data, name, path = self._load_report("provenance_report_*.json")
        return self._evidence(data, name, path)

    def fetch_closure(self) -> EvidenceItem:
        data, name, path = self._load_report("closure_validation_report_*.json")
        return self._evidence(data, name, path)

    def fetch_edge_density(self) -> EvidenceItem:
        data, name, path = self._load_report("edge_density_report_*.json")
        return self._evidence(data, name, path)

    def fetch_layer_coverage(self) -> EvidenceItem:
        data, name, path = self._load_report("layer_coverage_report_*.json")
        return self._evidence(data, name, path)

    def fetch_snapshot(self) -> EvidenceItem:
        data, name, path = self._load_report("adg_snapshot_*.json")
        return self._evidence(data, name, path)

    def fetch_sc_ap_config(self) -> EvidenceItem:
        path = _ADG_DIR / "sc_ap_config.json"
        if path.exists():
            return self._evidence(_load_json(path), path.name, path)
        return self._evidence({"error": "sc_ap_config_missing"}, "MISSING", None)


# ---------------------------------------------------------------------------
# Ratchet Adapter
# ---------------------------------------------------------------------------


class RatchetAdapter:
    """Fetch ratchet ceilings and burndown data."""

    def fetch_p1_ratchet(self) -> EvidenceItem:
        path = _ADG_DIR / "p1_ratchet.json"
        if path.exists():
            data = _load_json(path)
            return EvidenceItem(
                source_artifact=path.name,
                source_type="ratchet",
                snapshot_id="",
                freshness=_mtime_iso(path),
                data=data,
            )
        return EvidenceItem(
            source_artifact="MISSING",
            source_type="ratchet",
            snapshot_id="",
            freshness=_mtime_iso(path),
            data={"error": "p1_ratchet_missing"},
        )

    def fetch_p2_ratchet(self) -> EvidenceItem:
        path = _ADG_DIR / "p2_ratchet.json"
        if path.exists():
            data = _load_json(path)
            return EvidenceItem(
                source_artifact=path.name,
                source_type="ratchet",
                snapshot_id="",
                freshness=_mtime_iso(path),
                data=data,
            )
        return EvidenceItem(
            source_artifact="MISSING",
            source_type="ratchet",
            snapshot_id="",
            freshness=_mtime_iso(path),
            data={"error": "p2_ratchet_missing"},
        )

    def fetch_burndown(self) -> EvidenceItem:
        path = _ADG_DIR / "adg_burndown_table.json"
        if path.exists():
            data = _load_json(path)
            return EvidenceItem(
                source_artifact=path.name,
                source_type="ratchet",
                snapshot_id="",
                freshness=_mtime_iso(path),
                data=data,
            )
        return EvidenceItem(
            source_artifact="MISSING",
            source_type="ratchet",
            snapshot_id="",
            freshness=_mtime_iso(path),
            data={"error": "burndown_missing"},
        )


# ---------------------------------------------------------------------------
# Graph DB Adapter (DERIVED — all evidence tagged is_derived=True)
# ---------------------------------------------------------------------------


class GraphDBAdapter:
    """Fetch derived evidence from graph DB (NetworkX projection).

    All results carry is_derived=True — graph DB is augmenting, not canonical.
    """

    def __init__(self, graph: Any | None = None):
        self._graph = graph

    def _derived_evidence(self, data: dict[str, Any]) -> EvidenceItem:
        return EvidenceItem(
            source_artifact="graph_db_projection",
            source_type="graph_db",
            snapshot_id="",
            is_derived=True,
            freshness=_mtime_iso(None),
            data=data,
        )

    def fetch_blast_radius(self, node_id: str, max_depth: int = 5) -> EvidenceItem:
        """Fetch transitive dependents of a node. Requires graph to be loaded."""
        if self._graph is None:
            return self._derived_evidence({"error": "graph_not_loaded", "node_id": node_id})
        try:
            from tools.graphdb.queries.blast_radius import BlastRadiusQueries

            bq = BlastRadiusQueries(self._graph)
            result = bq.transitive_dependents(node_id, max_depth=max_depth)
            return self._derived_evidence(result)
        except (ImportError, ValueError) as e:
            return self._derived_evidence({"error": str(e), "node_id": node_id})

    def fetch_violating_path(self, from_node: str, to_node: str) -> EvidenceItem:
        """Fetch the exact path between two nodes if it exists."""
        if self._graph is None:
            return self._derived_evidence({"error": "graph_not_loaded"})
        try:
            import networkx as nx

            path = nx.shortest_path(self._graph, from_node, to_node)
            edges_on_path = []
            for i in range(len(path) - 1):
                edge_data = self._graph.get_edge_data(path[i], path[i + 1], default={})
                edges_on_path.append(
                    {
                        "from": path[i],
                        "to": path[i + 1],
                        "edge_type": edge_data.get("graph_type", "unknown"),
                    }
                )
            return self._derived_evidence(
                {
                    "path": path,
                    "edges": edges_on_path,
                    "hop_count": len(path) - 1,
                }
            )
        except Exception as e:  # guardian: allow-broad-exception -- graph query may fail for many reasons (missing node, no path, etc.)
            return self._derived_evidence({"error": str(e)})

    def fetch_neighborhood(self, node_id: str, radius: int = 2) -> EvidenceItem:
        """Fetch the neighborhood subgraph around a node."""
        if self._graph is None:
            return self._derived_evidence({"error": "graph_not_loaded"})
        try:
            import networkx as nx

            subgraph = nx.ego_graph(self._graph, node_id, radius=radius)
            return self._derived_evidence(
                {
                    "center": node_id,
                    "radius": radius,
                    "node_count": subgraph.number_of_nodes(),
                    "edge_count": subgraph.number_of_edges(),
                    "nodes": list(subgraph.nodes()),
                }
            )
        except Exception as e:  # guardian: allow-broad-exception -- graph query may fail for many reasons (missing node, disconnected, etc.)
            return self._derived_evidence({"error": str(e)})


# ---------------------------------------------------------------------------
# Structural Adapter
# ---------------------------------------------------------------------------


class StructuralAdapter:
    """Fetch structural analysis outputs (burndown, blast radius, seams, centrality)."""

    def __init__(self, sqlite_path: Path | None = None):
        self.path = sqlite_path or _find_latest("adg_indexed_*.sqlite")

    def _evidence(self, data: dict[str, Any]) -> EvidenceItem:
        return EvidenceItem(
            source_artifact=self.path.name if self.path else "MISSING",
            source_type="structural",
            snapshot_id=_extract_snapshot_id(self.path.name) if self.path else "",
            freshness=_mtime_iso(self.path),
            data=data,
        )

    def fetch_burndown(self) -> EvidenceItem:
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        try:
            from tools.adg.structural_outputs import burndown_table

            with sqlite3.connect(str(self.path)) as conn:
                return self._evidence(burndown_table(conn))
        except (ImportError, sqlite3.Error) as e:
            return self._evidence({"error": str(e)})

    def fetch_centrality(self, top_n: int = 20) -> EvidenceItem:
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        try:
            from tools.adg.structural_outputs import centrality

            with sqlite3.connect(str(self.path)) as conn:
                return self._evidence(centrality(conn, top_n=top_n))
        except (ImportError, sqlite3.Error) as e:
            return self._evidence({"error": str(e)})

    def fetch_seams(self) -> EvidenceItem:
        if not self.path or not self.path.exists():
            return self._evidence({"error": "sqlite_missing"})
        try:
            from tools.adg.structural_outputs import seam_detection

            with sqlite3.connect(str(self.path)) as conn:
                return self._evidence(seam_detection(conn))
        except (ImportError, sqlite3.Error) as e:
            return self._evidence({"error": str(e)})
