"""Emit the mandatory ADG dead-code control report.

This module stays inside the tools/reporting layer and builds the report
payload directly from the ADG sqlite snapshot so generate_full_adg does not
need to cross-import ops_scripts verification modules.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any

from tools.reports.adg_bcg_adapter import build_deprecation_deletion_plan, render_bcg_brief_md

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
DOCS_ADG = REPO_ROOT / "docs" / "reports" / "adg"


class DeadCodeZoneControlError(Exception):
    """Raised when the dead-code report cannot be built."""


def _repo_rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True, default=str), encoding="utf-8")


def _find_sqlite_database(adg_artifacts_dir: Path) -> Path:
    sqlite_files = sorted(adg_artifacts_dir.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)
    if not sqlite_files:
        raise DeadCodeZoneControlError("No SQLite database found")
    return sqlite_files[-1]


def _sqlite_snapshot_ts(sqlite_path: Path) -> str:
    prefix = "adg_indexed_"
    stem = sqlite_path.stem
    return stem[len(prefix) :] if stem.startswith(prefix) else stem


def _first_party_filter(alias: str = "") -> str:
    prefix = f"{alias}." if alias else ""
    return (
        f"({prefix}identity_kind IS NULL OR "
        f"{prefix}identity_kind NOT IN ('external_module', 'external_provider'))"
    )


def _fetch_count(cursor: sqlite3.Cursor, query: str, params: tuple[Any, ...] = ()) -> int:
    cursor.execute(query, params)
    row = cursor.fetchone()
    return int(row[0] or 0) if row else 0


def _fetch_count_map(cursor: sqlite3.Cursor, query: str, params: tuple[Any, ...] = ()) -> dict[Any, Any]:
    cursor.execute(query, params)
    return dict(cursor.fetchall())


def _fetch_rows(cursor: sqlite3.Cursor, query: str, params: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    cursor.execute(query, params)
    return list(cursor.fetchall())


def _table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE name = ? AND type IN ('table', 'view') LIMIT 1",
        (table_name,),
    )
    return cursor.fetchone() is not None


def _relation_surface_exists(cursor: sqlite3.Cursor, name: str) -> bool:
    return _table_exists(cursor, name)


def _nodes_path_expr(cursor: sqlite3.Cursor, alias: str = "n") -> str:
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(nodes)").fetchall()}
    if "resolved_path" in columns:
        return f"{alias}.resolved_path"
    if "file_path" in columns:
        return f"{alias}.file_path"
    raise DeadCodeZoneControlError("nodes table is missing a path column")


def _merge_hotspots(*groups: list[tuple[Any, ...]]) -> list[tuple[str, int]]:
    merged: dict[str, int] = {}
    for group in groups:
        for raw_name, raw_count, *_ in group:
            name = str(raw_name or "").strip()
            if not name:
                continue
            try:
                count = int(raw_count or 0)
            except (TypeError, ValueError):
                count = 0
            merged[name] = merged.get(name, 0) + count
    return sorted(merged.items(), key=lambda item: (-item[1], item[0]))[:10]


def _overlay_dead_imports_section(cursor: sqlite3.Cursor, warnings: list[str] | None = None) -> dict[str, Any]:
    if _table_exists(cursor, "mv_dead_import_hotspots_overlay"):
        node_path_expr = _nodes_path_expr(cursor, "n")
        total_dead_imports = _fetch_count(
            cursor, "SELECT COALESCE(SUM(dead_count), 0) FROM mv_dead_import_hotspots_overlay"
        )
        dead_imports_by_layer = _fetch_count_map(
            cursor,
            """
            SELECT n.layer, COALESCE(SUM(v.dead_count), 0) FROM mv_dead_import_hotspots_overlay v
            JOIN nodes n ON {node_path_expr} = v.file
            WHERE n.entity_type = 'module'
              AND n.layer IS NOT NULL
            GROUP BY n.layer
            ORDER BY SUM(v.dead_count) DESC
            """.format(node_path_expr=node_path_expr),
        )
        try:
            dead_imports_by_domain = _fetch_count_map(
                cursor,
                """
                SELECT n.domain, COALESCE(SUM(v.dead_count), 0) FROM mv_dead_import_hotspots_overlay v
                JOIN nodes n ON {node_path_expr} = v.file
                WHERE n.entity_type = 'module'
                  AND n.domain IS NOT NULL
                GROUP BY n.domain
                ORDER BY SUM(v.dead_count) DESC
                """.format(node_path_expr=node_path_expr),
            )
        except sqlite3.OperationalError:
            if warnings is not None:
                warnings.append("Domain field not available for dead import analysis")
            dead_imports_by_domain = {}
        dead_imports_by_confidence = _fetch_count_map(
            cursor,
            """
            SELECT n.confidence, COALESCE(SUM(v.dead_count), 0) FROM mv_dead_import_hotspots_overlay v
            JOIN nodes n ON {node_path_expr} = v.file
            WHERE n.entity_type = 'module'
              AND n.confidence IS NOT NULL
            GROUP BY n.confidence
            ORDER BY SUM(v.dead_count) DESC
            """.format(node_path_expr=node_path_expr),
        )
        dead_imports_by_entity_type = _fetch_count_map(
            cursor,
            """
            SELECT n.entity_type, COALESCE(SUM(v.dead_count), 0) FROM mv_dead_import_hotspots_overlay v
            JOIN nodes n ON {node_path_expr} = v.file
            WHERE n.entity_type IS NOT NULL
            GROUP BY n.entity_type
            ORDER BY SUM(v.dead_count) DESC
            """.format(node_path_expr=node_path_expr),
        )
        dead_import_hotspots = _fetch_rows(
            cursor,
            """
            SELECT file, dead_count
            FROM mv_dead_import_hotspots_overlay
            ORDER BY dead_count DESC, file ASC
            LIMIT 10
            """,
        )
        l4_dead_imports = int(dead_imports_by_layer.get("L4", 0) or 0)
        if warnings is not None and l4_dead_imports > 5:
            warnings.append(f"L4 has {l4_dead_imports} dead imports (should trend to zero)")
        return {
            "total_overlay_dead_imports": total_dead_imports,
            "total_dead_imports": total_dead_imports,
            "overlay_dead_imports_by_severity": {},
            "overlay_dead_import_hotspots": dead_import_hotspots,
            "dead_imports_by_layer": dead_imports_by_layer,
            "dead_imports_by_domain": dead_imports_by_domain,
            "dead_imports_by_confidence": dead_imports_by_confidence,
            "dead_imports_by_entity_type": dead_imports_by_entity_type,
            "dead_import_hotspots": dead_import_hotspots,
            "l4_dead_imports": l4_dead_imports,
        }

    if not _table_exists(cursor, "overlay_violations"):
        return {
            "total_overlay_dead_imports": 0,
            "total_dead_imports": 0,
            "overlay_dead_imports_by_severity": {},
            "overlay_dead_import_hotspots": [],
            "dead_imports_by_layer": {},
            "dead_imports_by_domain": {},
            "dead_imports_by_confidence": {},
            "dead_imports_by_entity_type": {},
            "dead_import_hotspots": [],
            "l4_dead_imports": 0,
        }

    total_overlay_dead_imports = _fetch_count(
        cursor,
        "SELECT COUNT(*) FROM overlay_violations WHERE category = 'dead_import_resolved'",
    )
    overlay_dead_imports_by_severity = _fetch_count_map(
        cursor,
        """
        SELECT severity, COUNT(*) FROM overlay_violations
        WHERE category = 'dead_import_resolved'
        GROUP BY severity
        ORDER BY COUNT(*) DESC
        """,
    )

    if _table_exists(cursor, "mv_dead_import_hotspots_overlay"):
        overlay_dead_import_hotspots = _fetch_rows(
            cursor,
            """
            SELECT file, dead_count FROM mv_dead_import_hotspots_overlay
            ORDER BY dead_count DESC
            LIMIT 10
            """,
        )
    else:
        overlay_dead_import_hotspots = _fetch_rows(
            cursor,
            """
            SELECT file_path, COUNT(*) as dead_count FROM overlay_violations
            WHERE category = 'dead_import_resolved'
            GROUP BY file_path
            ORDER BY dead_count DESC
            LIMIT 10
            """,
        )

    return {
        "total_overlay_dead_imports": total_overlay_dead_imports,
        "total_dead_imports": total_overlay_dead_imports,
        "overlay_dead_imports_by_severity": overlay_dead_imports_by_severity,
        "overlay_dead_import_hotspots": overlay_dead_import_hotspots,
        "dead_imports_by_layer": {},
        "dead_imports_by_domain": {},
        "dead_imports_by_confidence": {},
        "dead_imports_by_entity_type": {},
        "dead_import_hotspots": overlay_dead_import_hotspots,
        "l4_dead_imports": 0,
    }


def _dead_imports_section(cursor: sqlite3.Cursor, warnings: list[str]) -> dict[str, Any]:
    legacy_dead_import_edges = _fetch_count(cursor, "SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_imports'")
    overlay_dead_imports = _overlay_dead_imports_section(cursor, warnings)
    total_dead_imports = legacy_dead_import_edges + int(
        overlay_dead_imports.get("total_overlay_dead_imports", 0) or 0
    )
    dead_imports_by_layer = _fetch_count_map(
        cursor,
        """
        SELECT n.layer, COUNT(*) FROM edges e
        JOIN nodes n ON e.dst_id = n.id
        WHERE e.relation_type = 'dead_imports'
        AND n.layer IS NOT NULL
        GROUP BY n.layer
        ORDER BY COUNT(*) DESC
        """,
    )
    try:
        dead_imports_by_domain = _fetch_count_map(
            cursor,
            """
            SELECT n.domain, COUNT(*) FROM edges e
            JOIN nodes n ON e.dst_id = n.id
            WHERE e.relation_type = 'dead_imports'
            AND n.domain IS NOT NULL
            GROUP BY n.domain
            ORDER BY COUNT(*) DESC
            """,
        )
    except sqlite3.OperationalError:
        warnings.append("Domain field not available for dead import analysis")
        dead_imports_by_domain = {}
    dead_imports_by_confidence = _fetch_count_map(
        cursor,
        """
        SELECT n.confidence, COUNT(*) FROM edges e
        JOIN nodes n ON e.dst_id = n.id
        WHERE e.relation_type = 'dead_imports'
        AND n.confidence IS NOT NULL
        GROUP BY n.confidence
        ORDER BY COUNT(*) DESC
        """,
    )
    legacy_dead_import_hotspots = _fetch_rows(
        cursor,
        """
        SELECT n.adg_name, COUNT(*) as dead_count FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type = 'dead_imports'
        AND """ + _first_party_filter("n") + """
        GROUP BY n.id, n.adg_name
        ORDER BY dead_count DESC
        LIMIT 10
        """,
    )
    dead_import_hotspots = _merge_hotspots(
        legacy_dead_import_hotspots,
        overlay_dead_imports.get("dead_import_hotspots")
        or overlay_dead_imports.get("overlay_dead_import_hotspots")
        or [],
    )
    l4_dead_imports = int(dead_imports_by_layer.get("L4", 0) or 0)
    if l4_dead_imports > 5:
        warnings.append(f"L4 has {l4_dead_imports} dead imports (should trend to zero)")
    return {
        "total_dead_imports": total_dead_imports,
        "source_counts": {
            "legacy_dead_import_edges": legacy_dead_import_edges,
            "overlay_dead_import_resolved": overlay_dead_imports.get("total_overlay_dead_imports", 0),
        },
        "dead_imports_by_layer": dead_imports_by_layer,
        "dead_imports_by_domain": dead_imports_by_domain,
        "dead_imports_by_confidence": dead_imports_by_confidence,
        "overlay_dead_imports_by_severity": overlay_dead_imports.get("overlay_dead_imports_by_severity", {}),
        "dead_imports_by_entity_type": overlay_dead_imports.get("dead_imports_by_entity_type", {}),
        "dead_import_hotspots": dead_import_hotspots,
        "l4_dead_imports": l4_dead_imports,
    }


def _dead_code_candidates_section(cursor: sqlite3.Cursor) -> dict[str, Any]:
    if _relation_surface_exists(cursor, "mv_dead_import_hotspots_overlay"):
        overlay = _overlay_dead_imports_section(cursor, None)
        return {
            "source": "dead_import_overlay",
            "total_dead_code_candidates": overlay["total_dead_imports"],
            "dead_code_by_layer": overlay["dead_imports_by_layer"],
            "dead_code_by_entity_type": overlay["dead_imports_by_entity_type"],
            "dead_code_by_confidence": overlay["dead_imports_by_confidence"],
            "dead_code_hotspots": overlay["dead_import_hotspots"],
        }
    total_dead_code_candidates = _fetch_count(
        cursor, "SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_code_candidate'"
    )
    dead_code_by_layer = _fetch_count_map(
        cursor,
        """
        SELECT n.layer, COUNT(*) FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type = 'dead_code_candidate'
        AND n.layer IS NOT NULL
        GROUP BY n.layer
        ORDER BY COUNT(*) DESC
        """,
    )
    dead_code_by_entity_type = _fetch_count_map(
        cursor,
        """
        SELECT n.entity_type, COUNT(*) FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type = 'dead_code_candidate'
        GROUP BY n.entity_type
        ORDER BY COUNT(*) DESC
        """,
    )
    dead_code_by_confidence = _fetch_count_map(
        cursor,
        """
        SELECT n.confidence, COUNT(*) FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type = 'dead_code_candidate'
        AND n.confidence IS NOT NULL
        GROUP BY n.confidence
        ORDER BY COUNT(*) DESC
        """,
    )
    dead_code_hotspots = _fetch_rows(
        cursor,
        """
        SELECT n.adg_name, COUNT(*) as dead_count FROM edges e
        JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type = 'dead_code_candidate'
        AND """ + _first_party_filter("n") + """
        GROUP BY n.id, n.adg_name
        ORDER BY dead_count DESC
        LIMIT 10
        """,
    )
    return {
        "total_dead_code_candidates": total_dead_code_candidates,
        "dead_code_by_layer": dead_code_by_layer,
        "dead_code_by_entity_type": dead_code_by_entity_type,
        "dead_code_by_confidence": dead_code_by_confidence,
        "dead_code_hotspots": dead_code_hotspots,
    }


def _unresolved_imports_section(cursor: sqlite3.Cursor, errors: list[str]) -> dict[str, Any]:
    total_unresolved_imports = _fetch_count(
        cursor, "SELECT COUNT(*) FROM nodes WHERE identity_kind = 'unresolved_import'"
    )
    unresolved_by_layer = _fetch_count_map(
        cursor,
        """
        SELECT layer, COUNT(*) FROM nodes
        WHERE identity_kind = 'unresolved_import'
        AND layer IS NOT NULL
        GROUP BY layer
        ORDER BY COUNT(*) DESC
        """,
    )
    unresolved_by_confidence = _fetch_count_map(
        cursor,
        """
        SELECT confidence, COUNT(*) FROM nodes
        WHERE identity_kind = 'unresolved_import'
        AND confidence IS NOT NULL
        GROUP BY confidence
        ORDER BY COUNT(*) DESC
        """,
    )
    unresolved_hotspots = _fetch_rows(
        cursor,
        """
        SELECT n_src.adg_name, COUNT(*) as unresolved_count FROM nodes n_unres
        JOIN edges e ON e.dst_id = n_unres.id
        JOIN nodes n_src ON e.src_id = n_src.id
        WHERE n_unres.identity_kind = 'unresolved_import'
        AND """ + _first_party_filter("n_src") + """
        GROUP BY n_src.id, n_src.adg_name
        ORDER BY unresolved_count DESC
        LIMIT 10
        """,
    )
    l4_unresolved = int(unresolved_by_layer.get("L4", 0) or 0)
    if l4_unresolved > 0:
        errors.append(f"L4 has {l4_unresolved} unresolved imports (should be zero)")
    return {
        "total_unresolved_imports": total_unresolved_imports,
        "unresolved_by_layer": unresolved_by_layer,
        "unresolved_by_confidence": unresolved_by_confidence,
        "unresolved_hotspots": unresolved_hotspots,
        "l4_unresolved": l4_unresolved,
    }


def _low_confidence_section(cursor: sqlite3.Cursor, warnings: list[str]) -> dict[str, Any]:
    total_low_confidence = _fetch_count(cursor, "SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW'")
    low_conf_by_layer = _fetch_count_map(
        cursor,
        """
        SELECT layer, COUNT(*) FROM nodes
        WHERE confidence = 'LOW' AND layer IS NOT NULL
        GROUP BY layer
        ORDER BY COUNT(*) DESC
        """,
    )
    low_conf_by_entity_type = _fetch_count_map(
        cursor,
        """
        SELECT entity_type, COUNT(*) FROM nodes
        WHERE confidence = 'LOW'
        GROUP BY entity_type
        ORDER BY COUNT(*) DESC
        """,
    )
    low_conf_by_identity_kind = _fetch_count_map(
        cursor,
        """
        SELECT identity_kind, COUNT(*) FROM nodes
        WHERE confidence = 'LOW'
        GROUP BY identity_kind
        ORDER BY COUNT(*) DESC
        """,
    )
    first_party_low_conf = _fetch_count(
        cursor,
        f"SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW' AND {_first_party_filter()}",
    )
    total_first_party = _fetch_count(cursor, f"SELECT COUNT(*) FROM nodes WHERE {_first_party_filter()}")
    first_party_low_confidence_ratio = (first_party_low_conf / max(1, total_first_party)) * 100
    low_conf_hotspots = _fetch_rows(
        cursor,
        """
        SELECT layer, COUNT(*) as low_conf_count FROM nodes
        WHERE confidence = 'LOW' AND layer IS NOT NULL
        GROUP BY layer
        ORDER BY low_conf_count DESC
        LIMIT 10
        """,
    )
    governance_layers = ["L0", "L1", "L2", "L3", "L5"]
    governance_low_conf = sum(int(low_conf_by_layer.get(layer, 0) or 0) for layer in governance_layers)
    placeholders = ",".join("?" for _ in governance_layers)
    governance_total = _fetch_count(
        cursor, f"SELECT COUNT(*) FROM nodes WHERE layer IN ({placeholders})", tuple(governance_layers)
    )
    governance_low_confidence_ratio = (governance_low_conf / max(1, governance_total)) * 100
    if governance_low_confidence_ratio > 20:
        warnings.append(
            f"High low-confidence ratio in governance layers: {governance_low_confidence_ratio:.1f}%"
        )
    return {
        "total_low_confidence": total_low_confidence,
        "low_conf_by_layer": low_conf_by_layer,
        "low_conf_by_entity_type": low_conf_by_entity_type,
        "low_conf_by_identity_kind": low_conf_by_identity_kind,
        "first_party_low_confidence_ratio": first_party_low_confidence_ratio,
        "governance_low_confidence_ratio": governance_low_confidence_ratio,
        "low_conf_hotspots": low_conf_hotspots,
    }


def _inferred_symbol_section(cursor: sqlite3.Cursor, warnings: list[str]) -> dict[str, Any]:
    total_inferred_symbols = _fetch_count(
        cursor, "SELECT COUNT(*) FROM nodes WHERE identity_kind = 'inferred_symbol'"
    )
    total_symbols = _fetch_count(cursor, "SELECT COUNT(*) FROM nodes WHERE entity_type = 'symbol'")
    inferred_symbol_ratio = (total_inferred_symbols / max(1, total_symbols)) * 100
    inferred_by_layer = _fetch_count_map(
        cursor,
        """
        SELECT n.layer, COUNT(*) FROM nodes n
        WHERE n.identity_kind = 'inferred_symbol' AND n.layer IS NOT NULL
        GROUP BY n.layer
        ORDER BY COUNT(*) DESC
        """,
    )
    inferred_by_confidence = _fetch_count_map(
        cursor,
        """
        SELECT confidence, COUNT(*) FROM nodes
        WHERE identity_kind = 'inferred_symbol' AND confidence IS NOT NULL
        GROUP BY confidence
        ORDER BY COUNT(*) DESC
        """,
    )
    if inferred_symbol_ratio > 30:
        warnings.append(f"High inferred symbol ratio: {inferred_symbol_ratio:.1f}%")
    return {
        "total_inferred_symbols": total_inferred_symbols,
        "total_symbols": total_symbols,
        "inferred_symbol_ratio": inferred_symbol_ratio,
        "inferred_by_layer": inferred_by_layer,
        "inferred_by_confidence": inferred_by_confidence,
    }


def _executive_readiness_section(cursor: sqlite3.Cursor) -> dict[str, Any]:
    overlay_dead_imports = _relation_surface_exists(cursor, "mv_dead_import_hotspots_overlay")
    node_path_expr = _nodes_path_expr(cursor, "n")
    dead_import_count_query = (
        "SELECT COALESCE(SUM(dead_count), 0) FROM mv_dead_import_hotspots_overlay"
        if overlay_dead_imports
        else "SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_imports'"
    )
    dead_code_count_query = (
        "SELECT COALESCE(SUM(dead_count), 0) FROM mv_dead_import_hotspots_overlay"
        if overlay_dead_imports
        else "SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_code_candidate'"
    )
    executive_metrics = {
        "dead_import_count": dead_import_count_query,
        "dead_code_count": dead_code_count_query,
        "unresolved_import_count": "SELECT COUNT(*) FROM nodes WHERE identity_kind = 'unresolved_import'",
        "low_confidence_count": "SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW'",
        "l4_unresolved_import_count": "SELECT COUNT(*) FROM nodes WHERE identity_kind = 'unresolved_import' AND layer = 'L4'",
        "first_party_low_confidence_ratio": "calculated_first_party_low_confidence_ratio",
        "inferred_symbol_ratio": "calculated",
    }

    calculated_metrics: dict[str, Any] = {}
    for metric_name, query in executive_metrics.items():
        if query == "calculated":
            inferred = _fetch_count(cursor, "SELECT COUNT(*) FROM nodes WHERE identity_kind = 'inferred_symbol'")
            total_symbols = _fetch_count(cursor, "SELECT COUNT(*) FROM nodes WHERE entity_type = 'symbol'")
            calculated_metrics[metric_name] = (inferred / max(1, total_symbols)) * 100
        elif query == "calculated_first_party_low_confidence_ratio":
            first_party_low_conf = _fetch_count(
                cursor, f"SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW' AND {_first_party_filter()}"
            )
            total_first_party = _fetch_count(cursor, f"SELECT COUNT(*) FROM nodes WHERE {_first_party_filter()}")
            calculated_metrics[metric_name] = (first_party_low_conf / max(1, total_first_party)) * 100
        else:
            calculated_metrics[metric_name] = _fetch_count(cursor, query)

    first_party_metrics: dict[str, Any] = {}
    for metric_name, query in executive_metrics.items():
        if query in {"calculated", "calculated_first_party_low_confidence_ratio"}:
            continue
        if overlay_dead_imports and metric_name in {"dead_import_count", "dead_code_count"}:
            fp_query = (
                "SELECT COALESCE(SUM(v.dead_count), 0) "
                "FROM mv_dead_import_hotspots_overlay v "
                f"JOIN nodes n ON {node_path_expr} = v.file "
                "WHERE n.entity_type = 'module' AND "
                f"{_first_party_filter('n')}"
            )
        elif "edges" in query:
            fp_query = query.replace("FROM edges", "FROM edges e JOIN nodes n ON e.src_id = n.id", 1)
            fp_query = f"{fp_query} AND {_first_party_filter('n')}"
        elif "nodes" in query:
            fp_query = f"{query} AND {_first_party_filter()}"
        else:
            fp_query = query
        try:
            first_party_metrics[metric_name] = _fetch_count(cursor, fp_query)
        except sqlite3.OperationalError:
            first_party_metrics[metric_name] = None

    readiness_issues: list[str] = []
    if calculated_metrics.get("l4_unresolved_import_count", 0) > 0:
        readiness_issues.append("L4 has unresolved imports")
    if calculated_metrics.get("first_party_low_confidence_ratio", 0) > 15:
        readiness_issues.append("High first-party low-confidence ratio")
    if calculated_metrics.get("inferred_symbol_ratio", 0) > 25:
        readiness_issues.append("High inferred symbol ratio")

    return {
        "executive_metrics": calculated_metrics,
        "first_party_metrics": first_party_metrics,
        "readiness_issues": readiness_issues,
        "executive_ready": len(readiness_issues) == 0,
    }


def _build_dead_code_zone_control_report(adg_artifacts_dir: Path) -> dict[str, Any]:
    sqlite_path = _find_sqlite_database(adg_artifacts_dir)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        with sqlite3.connect(sqlite_path) as conn:
            cursor = conn.cursor()
            dead_imports = _dead_imports_section(cursor, warnings)
            dead_code = _dead_code_candidates_section(cursor)
            unresolved = _unresolved_imports_section(cursor, errors)
            low_confidence = _low_confidence_section(cursor, warnings)
            inferred = _inferred_symbol_section(cursor, warnings)
            executive = _executive_readiness_section(cursor)
    except sqlite3.Error as exc:
        raise DeadCodeZoneControlError(f"Dead-code report verification failed: {exc}") from exc

    critical_issues = unresolved.get("l4_unresolved", 0) > 0 or not executive.get("executive_ready", True)
    source = {
        "adg_snapshot": _repo_rel(sqlite_path),
        "adg_snapshot_ts": _sqlite_snapshot_ts(sqlite_path),
        "dead_code_signal_sources": [
            "overlay_violations.category=dead_import_resolved",
            "mv_dead_import_hotspots_overlay",
            "edges.relation_type=dead_imports",
            "edges.relation_type=dead_code_candidate",
        ],
    }
    return {
        "status": "FAIL" if critical_issues else "PASS",
        "source": source,
        "dead_imports": dead_imports,
        "dead_code_candidates": dead_code,
        "unresolved_imports": unresolved,
        "low_confidence_zones": low_confidence,
        "inferred_symbols": inferred,
        "executive_readiness": executive,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "total_dead_imports": dead_imports.get("total_dead_imports", 0),
            "total_dead_code_candidates": dead_code.get("total_dead_code_candidates", 0),
            "total_unresolved_imports": unresolved.get("total_unresolved_imports", 0),
            "total_low_confidence": low_confidence.get("total_low_confidence", 0),
            "l4_unresolved_imports": unresolved.get("l4_unresolved", 0),
            "first_party_low_confidence_ratio": low_confidence.get("first_party_low_confidence_ratio", 0),
            "inferred_symbol_ratio": inferred.get("inferred_symbol_ratio", 0),
            "executive_ready": executive.get("executive_ready", False),
            "adg_snapshot": source["adg_snapshot"],
            "adg_snapshot_ts": source["adg_snapshot_ts"],
        },
    }


def _render_inline_summary(report: dict[str, Any]) -> str:
    plan = build_deprecation_deletion_plan(report, None, None)
    lines = ["## ADG Dead Code Report", ""]
    lines.extend(render_bcg_brief_md(plan["brief"]).splitlines())
    hotspots = (report.get("dead_code_candidates") or {}).get("dead_code_hotspots") or []
    hotspot_title = "### Top dead-code hotspots"
    if not hotspots:
        hotspots = (report.get("dead_imports") or {}).get("dead_import_hotspots") or []
        hotspot_title = "### Top dead-import hotspots"
    if hotspots:
        lines.append("")
        lines.append(hotspot_title)
        for idx, (module, count) in enumerate(hotspots[:5], 1):
            lines.append(f"- {idx}. {module}: {count}")
    return "\n".join(lines)


def _copyfile_if_different(src: Path, dst: Path) -> None:
    if src.resolve() == dst.resolve():
        return
    shutil.copyfile(src, dst)


def emit_mandatory_adg_dead_code_report(
    *,
    adg_artifacts_dir: Path = ARTIFACTS_ADG,
    ts: str | None = None,
    fail_closed: bool = True,
    print_inline: bool = False,
    docs_dir: Path | None = None,
) -> tuple[int, Path | None]:
    """Write the dead-code control report and latest copies.

    Returns ``(0, path)`` on successful report emission. The report contents can
    still indicate issues; that does not fail the emit step itself.
    """
    docs_target = docs_dir if docs_dir is not None else DOCS_ADG
    try:
        report = _build_dead_code_zone_control_report(adg_artifacts_dir)

        run_id = ts or str((report.get("run") or {}).get("run_id") or "latest")
        base = adg_artifacts_dir / f"dead_code_zone_control_report_{run_id}"
        json_path = base.with_suffix(".json")
        _write_json(json_path, report)

        latest = adg_artifacts_dir / "dead_code_zone_control_report_latest.json"
        docs_latest = docs_target / "dead_code_zone_control_report_latest.json"
        latest.parent.mkdir(parents=True, exist_ok=True)
        docs_latest.parent.mkdir(parents=True, exist_ok=True)
        _copyfile_if_different(json_path, latest)
        _copyfile_if_different(json_path, docs_latest)

        if print_inline:
            sys.stdout.write("\n" + _render_inline_summary(report) + "\n")

        print(f"[adg_dead_code_report] SUMMARY={_repo_rel(json_path)}", file=sys.stderr)
        return 0, json_path
    except FileNotFoundError as exc:
        print(f"[adg_dead_code_report] mandatory emit skipped: {exc}", file=sys.stderr)
        return (2 if fail_closed else 0), None
    except OSError as exc:
        print(f"[adg_dead_code_report] ERROR={exc}", file=sys.stderr)
        return (2 if fail_closed else 0), None
    except Exception as exc:  # guardian: allow-broad-exception -- report wrapper
        print(f"[adg_dead_code_report] ERROR={exc}", file=sys.stderr)
        return (2 if fail_closed else 0), None
