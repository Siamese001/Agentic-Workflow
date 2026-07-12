"""Phase G materialized views — transparent repository-health intelligence.

Phase G turns the existing ADG evidence into a compact, queryable health contract.
It does not replace raw graph facts or gate verdicts.  Every score carries its raw
value, thresholds, availability, and source so consumers can audit the result.

Output tables
-------------
``mv_repo_health_signals``
    One normalized row per health signal.
``mv_repo_health_dimensions``
    Weighted roll-up for governance, graph truth, testing, architecture, change
    safety, and maintainability.
``mv_repo_health_summary``
    One confidence-aware repository verdict.  Insufficient evidence emits
    ``UNKNOWN`` regardless of numeric score.
``mv_repo_health_hotspots``
    Per-production-module remediation ranking with explicit risk drivers.
"""

from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from agentic_core.adg.artifact.edge_authority import PROOF_STATUSES, RISK_STATUSES
from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv as _connect_sqlite

_PHASE_G_TABLES: Final[tuple[str, ...]] = (
    "mv_repo_health_signals",
    "mv_repo_health_dimensions",
    "mv_repo_health_summary",
    "mv_repo_health_hotspots",
)

_CONTRACT_VERSION: Final[str] = "1.0"
_CONFIDENCE_FLOOR: Final[float] = 0.70
_INACTIVE_DISPOSITIONS: Final[tuple[str, ...]] = (
    "approved",
    "resolved",
    "false_positive",
    "exempted",
    "closed",
)
_DIMENSION_WEIGHTS: Final[dict[str, float]] = {
    "governance_safety": 0.25,
    "graph_truth": 0.20,
    "test_protection": 0.18,
    "architecture": 0.17,
    "change_safety": 0.10,
    "maintainability": 0.10,
}


@dataclass(frozen=True)
class HealthSignal:
    """A single auditable health measurement."""

    key: str
    dimension: str
    value: float
    unit: str
    polarity: str
    warn_threshold: float
    critical_threshold: float
    score: float
    status: str
    available: bool
    weight: float
    source_table: str
    description: str


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return (
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name=? LIMIT 1",
            (table,),
        ).fetchone()
        is not None
    )


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    if not _table_exists(conn, table):
        return set()
    return {str(row[1]) for row in conn.execute(f'PRAGMA table_info("{table}")')}


def _scalar(
    conn: sqlite3.Connection,
    sql: str,
    params: tuple[object, ...] = (),
    *,
    default: float = 0.0,
) -> float:
    row = conn.execute(sql, params).fetchone()
    if row is None or row[0] is None:
        return default
    return float(row[0])


def _snapshot_id(conn: sqlite3.Connection) -> str:
    if not _table_exists(conn, "meta"):
        return ""
    row = conn.execute("SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1").fetchone()
    return str(row[0]) if row else ""


def _meta_value(conn: sqlite3.Connection, key: str) -> str | None:
    if not _table_exists(conn, "meta"):
        return None
    row = conn.execute("SELECT value FROM meta WHERE key=? LIMIT 1", (key,)).fetchone()
    return None if row is None else str(row[0])


def _status_for_score(score: float, *, available: bool = True) -> str:
    if not available:
        return "UNKNOWN"
    if score >= 90.0:
        return "HEALTHY"
    if score >= 75.0:
        return "WATCH"
    if score >= 55.0:
        return "AT_RISK"
    return "CRITICAL"


def _score_lower_is_better(value: float, warn: float, critical: float) -> float:
    """Piecewise score: 100 at zero, 85 at warn, 40 at critical, 0 at 2× critical."""

    value = max(0.0, float(value))
    warn = max(0.0, float(warn))
    critical = max(warn + 1e-9, float(critical))
    if value <= warn:
        if warn <= 1e-9:
            return 100.0 if value <= 1e-9 else 85.0
        return 100.0 - 15.0 * (value / warn)
    if value <= critical:
        return 85.0 - 45.0 * ((value - warn) / (critical - warn))
    return max(0.0, 40.0 * (1.0 - min(1.0, (value - critical) / critical)))


def _score_higher_is_better(value: float, warn: float, good: float) -> float:
    """Piecewise score: 0 at zero, 60 at warn, 100 at the good threshold."""

    value = max(0.0, float(value))
    warn = max(1e-9, float(warn))
    good = max(warn + 1e-9, float(good))
    if value < warn:
        return 60.0 * min(1.0, value / warn)
    if value < good:
        return 60.0 + 40.0 * ((value - warn) / (good - warn))
    return 100.0


def _make_signal(
    *,
    key: str,
    dimension: str,
    value: float,
    unit: str,
    polarity: str,
    warn: float,
    critical: float,
    available: bool,
    weight: float,
    source_table: str,
    description: str,
) -> HealthSignal:
    if not available:
        score = 0.0
    elif polarity == "lower_is_better":
        score = _score_lower_is_better(value, warn, critical)
    elif polarity == "higher_is_better":
        score = _score_higher_is_better(value, warn, critical)
    elif polarity == "binary_good":
        score = 100.0 if value >= critical else 0.0
    else:
        raise ValueError(f"Unsupported signal polarity: {polarity}")

    score = round(max(0.0, min(100.0, score)), 2)
    return HealthSignal(
        key=key,
        dimension=dimension,
        value=round(float(value), 4),
        unit=unit,
        polarity=polarity,
        warn_threshold=float(warn),
        critical_threshold=float(critical),
        score=score,
        status=_status_for_score(score, available=available),
        available=available,
        weight=float(weight),
        source_table=source_table,
        description=description,
    )


def _production_module_count(conn: sqlite3.Connection) -> int:
    return int(
        _scalar(
            conn,
            """
            SELECT COUNT(DISTINCT resolved_path)
            FROM nodes
            WHERE entity_type='module'
              AND resolved_path != ''
              AND resolved_path NOT LIKE 'tests/%'
              AND resolved_path NOT LIKE 'tools/%'
              AND resolved_path NOT LIKE 'ops_scripts/%'
              AND resolved_path NOT LIKE 'docs/archive/%'
            """,
        )
    )


def _active_high_violations(conn: sqlite3.Connection) -> tuple[int, bool]:
    columns = _table_columns(conn, "violations")
    if "severity" not in columns:
        return 0, False

    disposition_clause = ""
    params: tuple[object, ...] = ()
    if "disposition" in columns:
        placeholders = ", ".join("?" for _ in _INACTIVE_DISPOSITIONS)
        disposition_clause = f" AND LOWER(COALESCE(disposition, 'untriaged')) NOT IN ({placeholders})"
        params = _INACTIVE_DISPOSITIONS

    count = _scalar(
        conn,
        "SELECT COUNT(*) FROM violations "
        "WHERE UPPER(COALESCE(severity, '')) IN ('CRITICAL', 'HIGH')" + disposition_clause,
        params,
    )
    return int(count), True


def _write_bypass_count(conn: sqlite3.Connection) -> int:
    table = "mv_write_sovereignty_paths"
    if not _table_exists(conn, table):
        return 0
    columns = _table_columns(conn, table)
    if "is_uwg_routed" in columns:
        return int(_scalar(conn, f"SELECT COUNT(*) FROM {table} WHERE COALESCE(is_uwg_routed, 0)=0"))
    return int(_scalar(conn, f"SELECT COUNT(*) FROM {table}"))


def _edge_authority_metrics(conn: sqlite3.Connection) -> tuple[int, int, int, bool]:
    """Return total, proof, risk edge counts and whether authority evidence exists."""

    columns = _table_columns(conn, "edges")
    if not columns:
        return 0, 0, 0, False

    source_filter = ""
    if "source_file" in columns:
        source_filter = (
            " WHERE COALESCE(source_file, '') NOT LIKE 'tests/%'"
            " AND COALESCE(source_file, '') NOT LIKE 'tools/%'"
            " AND COALESCE(source_file, '') NOT LIKE 'ops_scripts/%'"
        )
    total = int(_scalar(conn, f"SELECT COUNT(*) FROM edges{source_filter}"))

    if "authority_status" in columns:
        proof_marks = ", ".join("?" for _ in PROOF_STATUSES)
        risk_marks = ", ".join("?" for _ in RISK_STATUSES)
        proof = int(
            _scalar(
                conn,
                f"SELECT COUNT(*) FROM edges{source_filter}"
                + (" AND " if source_filter else " WHERE ")
                + f"authority_status IN ({proof_marks})",
                tuple(sorted(PROOF_STATUSES)),
            )
        )
        risk = int(
            _scalar(
                conn,
                f"SELECT COUNT(*) FROM edges{source_filter}"
                + (" AND " if source_filter else " WHERE ")
                + f"authority_status IN ({risk_marks})",
                tuple(sorted(RISK_STATUSES)),
            )
        )
        # Inventory-only edges are intentionally excluded from the health ratio:
        # under the three-bucket law they are neither proof nor risk evidence.
        return proof + risk, proof, risk, True

    if "authority" in columns:
        proof = int(
            _scalar(
                conn,
                f"SELECT COUNT(*) FROM edges{source_filter}"
                + (" AND " if source_filter else " WHERE ")
                + "authority IN ('verified', 'runtime_observed')",
            )
        )
        risk = int(
            _scalar(
                conn,
                f"SELECT COUNT(*) FROM edges{source_filter}"
                + (" AND " if source_filter else " WHERE ")
                + "authority IN ('unresolved', 'dynamic')",
            )
        )
        return proof + risk, proof, risk, True

    return total, 0, 0, False


def _structural_edge_metrics(conn: sqlite3.Connection) -> tuple[int, int]:
    if not _table_exists(conn, "edges") or not _table_exists(conn, "nodes"):
        return 0, 0
    total = int(
        _scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM edges e
            JOIN nodes src ON src.id=e.src_id
            WHERE e.relation_type IN ('imports', 'calls')
              AND COALESCE(src.resolved_path, '') NOT LIKE 'tests/%'
              AND COALESCE(src.resolved_path, '') NOT LIKE 'tools/%'
              AND COALESCE(src.resolved_path, '') NOT LIKE 'ops_scripts/%'
            """,
        )
    )
    cross = int(
        _scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM edges e
            JOIN nodes src ON src.id=e.src_id
            JOIN nodes dst ON dst.id=e.dst_id
            WHERE e.relation_type IN ('imports', 'calls')
              AND COALESCE(src.layer, '') != ''
              AND COALESCE(dst.layer, '') != ''
              AND src.layer != dst.layer
              AND COALESCE(src.resolved_path, '') NOT LIKE 'tests/%'
              AND COALESCE(src.resolved_path, '') NOT LIKE 'tools/%'
              AND COALESCE(src.resolved_path, '') NOT LIKE 'ops_scripts/%'
            """,
        )
    )
    return total, cross


def _cycle_coupling_metrics(conn: sqlite3.Connection) -> tuple[int, bool]:
    """Return production modules participating in cyclic/tightly-coupled zones."""

    scc_columns = _table_columns(conn, "mv_graph_scc_clusters")
    if "file_path" in scc_columns:
        count = _scalar(
            conn,
            "SELECT COUNT(DISTINCT file_path) FROM mv_graph_scc_clusters "
            "WHERE COALESCE(file_path, '') NOT LIKE 'tests/%' "
            "AND COALESCE(file_path, '') NOT LIKE 'tools/%'",
        )
        return int(count), True

    edge_columns = _table_columns(conn, "edges")
    if "relation_type" in edge_columns:
        count = _scalar(conn, "SELECT COUNT(*) FROM edges WHERE relation_type='in_cycle'")
        return int(count), True
    return 0, False


def _coverage_metrics(conn: sqlite3.Connection, production_modules: int) -> dict[str, float | int | bool]:
    table = "mv_hotspot_coverage_risk"
    if not _table_exists(conn, table):
        return {
            "available": False,
            "high_risk_count": 0,
            "high_risk_protected_pct": 0.0,
            "p1_urgent": 0,
            "coverage_inventory_pct": 0.0,
            "top10_concentration_pct": 0.0,
            "concentration_available": False,
        }

    high_risk = int(_scalar(conn, f"SELECT COUNT(*) FROM {table} WHERE risk_band IN ('CRITICAL', 'HIGH')"))
    protected = int(
        _scalar(
            conn,
            f"SELECT COUNT(*) FROM {table} "
            "WHERE risk_band IN ('CRITICAL', 'HIGH') AND coverage_pct >= 70.0",
        )
    )
    p1_urgent = int(_scalar(conn, f"SELECT COUNT(*) FROM {table} WHERE priority_band='P1_URGENT'"))
    inventoried = int(_scalar(conn, f"SELECT COUNT(*) FROM {table} WHERE coverage_pct >= 0.0"))
    high_risk_protected_pct = 100.0 if high_risk == 0 else 100.0 * protected / high_risk
    coverage_inventory_pct = 0.0 if production_modules == 0 else 100.0 * inventoried / production_modules

    risks = [
        max(0.0, float(row[0] or 0.0))
        for row in conn.execute(
            f"SELECT COALESCE(criticality_score, 0.0) + "
            "COALESCE(combined_risk_score, 0.0) + COALESCE(total_debt_score, 0.0) "
            f"FROM {table} ORDER BY 1 DESC"
        )
    ]
    total_risk = sum(risks)
    concentration = 0.0 if total_risk <= 0.0 else 100.0 * sum(risks[:10]) / total_risk

    return {
        "available": True,
        "high_risk_count": high_risk,
        "high_risk_protected_pct": high_risk_protected_pct,
        "p1_urgent": p1_urgent,
        "coverage_inventory_pct": coverage_inventory_pct,
        "top10_concentration_pct": concentration,
        "concentration_available": len(risks) > 10,
    }


def _regression_metrics(conn: sqlite3.Connection, production_modules: int) -> dict[str, float | bool]:
    table = "mv_snapshot_regression_summary"
    required = {
        "violation_delta",
        "cross_layer_delta",
        "bypass_delta",
        "debt_delta",
        "is_first_run",
    }
    if not required.issubset(_table_columns(conn, table)):
        return {"available": False}

    row = conn.execute(
        "SELECT violation_delta, cross_layer_delta, bypass_delta, debt_delta, is_first_run "
        f"FROM {table} LIMIT 1"
    ).fetchone()
    if row is None or int(row[4] or 0) == 1:
        return {"available": False}

    denominator = max(1, production_modules)
    return {
        "available": True,
        "violation_delta": max(0.0, float(row[0] or 0.0)),
        "cross_layer_delta": max(0.0, float(row[1] or 0.0)),
        "bypass_delta": max(0.0, float(row[2] or 0.0)),
        "debt_delta_per_module": max(0.0, float(row[3] or 0.0) / denominator),
    }


def _debt_per_module(conn: sqlite3.Connection, production_modules: int) -> tuple[float, bool]:
    table = "mv_snapshot_baseline"
    if "debt_score" not in _table_columns(conn, table) or production_modules == 0:
        return 0.0, False
    debt = _scalar(conn, f"SELECT COALESCE(debt_score, 0.0) FROM {table} LIMIT 1")
    return debt / production_modules, True


def _hotspot_rows(
    conn: sqlite3.Connection,
    *,
    snapshot_id: str,
) -> list[tuple[object, ...]]:
    """Build deterministic per-module risk rows for ``mv_repo_health_hotspots``."""

    module_rows = conn.execute("""
        SELECT MIN(id) AS node_id, resolved_path, MAX(COALESCE(layer, '')) AS layer
        FROM nodes
        WHERE entity_type='module'
          AND resolved_path != ''
          AND resolved_path NOT LIKE 'tests/%'
          AND resolved_path NOT LIKE 'tools/%'
          AND resolved_path NOT LIKE 'ops_scripts/%'
          AND resolved_path NOT LIKE 'docs/archive/%'
        GROUP BY resolved_path
        ORDER BY resolved_path
        """).fetchall()
    modules = {str(row[1]): {"node_id": int(row[0]), "layer": str(row[2] or "")} for row in module_rows}
    if not modules:
        return []

    risk_by_file: dict[str, dict[str, object]] = {}
    if _table_exists(conn, "mv_hotspot_coverage_risk"):
        for row in conn.execute("""
            SELECT node_id, file, layer, criticality_score, combined_risk_score,
                   total_debt_score, coverage_pct, priority_band
            FROM mv_hotspot_coverage_risk
            """):
            file_path = str(row[1] or "")
            candidate = {
                "node_id": int(row[0] or modules.get(file_path, {}).get("node_id", 0)),
                "layer": str(row[2] or modules.get(file_path, {}).get("layer", "")),
                "criticality": float(row[3] or 0.0),
                "combined": float(row[4] or 0.0),
                "debt": float(row[5] or 0.0),
                "coverage": float(row[6] if row[6] is not None else -1.0),
                "priority": str(row[7] or "P5_NOOP"),
            }
            prior = risk_by_file.get(file_path)
            if prior is None or float(candidate["criticality"]) > float(prior["criticality"]):
                risk_by_file[file_path] = candidate

    violations_by_file: dict[str, tuple[int, int]] = {}
    violation_columns = _table_columns(conn, "violations")
    if {"file_path", "severity"}.issubset(violation_columns):
        where_clause = ""
        params: tuple[object, ...] = ()
        if "disposition" in violation_columns:
            placeholders = ", ".join("?" for _ in _INACTIVE_DISPOSITIONS)
            where_clause = f"WHERE LOWER(COALESCE(disposition, 'untriaged')) NOT IN ({placeholders})"
            params = _INACTIVE_DISPOSITIONS
        for row in conn.execute(
            f"""
            SELECT file_path,
                   SUM(CASE WHEN UPPER(COALESCE(severity, '')) IN ('CRITICAL', 'HIGH')
                            THEN 1 ELSE 0 END) AS high_count,
                   SUM(CASE WHEN UPPER(COALESCE(severity, ''))='MEDIUM'
                            THEN 1 ELSE 0 END) AS medium_count
            FROM violations
            {where_clause}
            GROUP BY file_path
            """,
            params,
        ):
            violations_by_file[str(row[0] or "")] = (int(row[1] or 0), int(row[2] or 0))

    edge_by_file: dict[str, tuple[int, int, int, int]] = {}
    edge_columns = _table_columns(conn, "edges")
    if {"source_file", "relation_type"}.issubset(edge_columns):
        if "authority_status" in edge_columns:
            risk_marks = ", ".join("?" for _ in RISK_STATUSES)
            risk_expr = f"authority_status IN ({risk_marks})"
            risk_params: tuple[object, ...] = tuple(sorted(RISK_STATUSES))
        elif "authority" in edge_columns:
            risk_expr = "authority IN ('unresolved', 'dynamic')"
            risk_params = ()
        else:
            risk_expr = "0"
            risk_params = ()

        dynamic_expr = (
            "(authority='dynamic' OR relation_type='dynamic_exec')"
            if "authority" in edge_columns
            else "relation_type='dynamic_exec'"
        )
        for row in conn.execute(
            f"""
            SELECT source_file,
                   COUNT(*) AS total_edges,
                   SUM(CASE WHEN {risk_expr} THEN 1 ELSE 0 END) AS risk_edges,
                   SUM(CASE WHEN {dynamic_expr} THEN 1 ELSE 0 END) AS dynamic_edges,
                   SUM(CASE WHEN relation_type='in_cycle' THEN 1 ELSE 0 END) AS cycle_edges
            FROM edges
            WHERE COALESCE(source_file, '') != ''
            GROUP BY source_file
            """,
            risk_params,
        ):
            edge_by_file[str(row[0])] = (
                int(row[1] or 0),
                int(row[2] or 0),
                int(row[3] or 0),
                int(row[4] or 0),
            )

    scc_by_file: dict[str, int] = {}
    scc_columns = _table_columns(conn, "mv_graph_scc_clusters")
    if {"file_path", "cluster_size"}.issubset(scc_columns):
        for row in conn.execute(
            "SELECT file_path, MAX(COALESCE(cluster_size, 0)) "
            "FROM mv_graph_scc_clusters GROUP BY file_path"
        ):
            scc_by_file[str(row[0] or "")] = int(row[1] or 0)

    bypass_by_file: dict[str, int] = {}
    bypass_table = "mv_write_sovereignty_paths"
    bypass_columns = _table_columns(conn, bypass_table)
    path_column = next(
        (name for name in ("source_file", "file", "resolved_path") if name in bypass_columns),
        None,
    )
    if path_column is not None:
        predicate = "WHERE COALESCE(is_uwg_routed, 0)=0" if "is_uwg_routed" in bypass_columns else ""
        for row in conn.execute(
            f'SELECT "{path_column}", COUNT(*) FROM {bypass_table} {predicate} GROUP BY "{path_column}"'
        ):
            bypass_by_file[str(row[0] or "")] = int(row[1] or 0)

    criticalities = sorted(float(values.get("criticality", 0.0)) for values in risk_by_file.values())
    p95_criticality = criticalities[int((len(criticalities) - 1) * 0.95)] if criticalities else 0.0
    max_debt = max(
        (float(values.get("debt", 0.0)) for values in risk_by_file.values()),
        default=0.0,
    )

    output: list[tuple[object, ...]] = []
    for file_path, module in modules.items():
        risk = risk_by_file.get(file_path, {})
        node_id = int(risk.get("node_id", module["node_id"]))
        layer = str(risk.get("layer", module["layer"]))
        criticality = max(0.0, float(risk.get("criticality", 0.0)))
        combined = max(0.0, float(risk.get("combined", 0.0)))
        debt = max(0.0, float(risk.get("debt", 0.0)))
        coverage = float(risk.get("coverage", -1.0))
        priority = str(risk.get("priority", "P5_NOOP"))
        high_count, medium_count = violations_by_file.get(file_path, (0, 0))
        total_edges, risk_edges, dynamic_edges, cycle_edges = edge_by_file.get(file_path, (0, 0, 0, 0))
        cycle_coupling = max(cycle_edges, scc_by_file.get(file_path, 0))
        write_bypasses = bypass_by_file.get(file_path, 0)

        governance_component = min(
            35.0,
            high_count * 18.0 + medium_count * 5.0 + write_bypasses * 20.0,
        )
        if priority == "P1_URGENT":
            coverage_component = 25.0
        elif priority == "P2_GAP":
            coverage_component = 15.0
        elif coverage < 0.0 and criticality > 0.0:
            coverage_component = 20.0
        elif 0.0 <= coverage < 70.0:
            coverage_component = 12.0
        elif 70.0 <= coverage < 90.0:
            coverage_component = 5.0
        else:
            coverage_component = 0.0

        unresolved_ratio = 0.0 if total_edges == 0 else risk_edges / total_edges
        topology_component = min(
            25.0,
            cycle_coupling * 10.0 + dynamic_edges * 8.0 + unresolved_ratio * 20.0,
        )
        criticality_component = (
            0.0 if p95_criticality <= 0.0 else min(25.0, 25.0 * criticality / p95_criticality)
        )
        debt_component = 0.0 if max_debt <= 0.0 else min(15.0, 15.0 * math.log1p(debt) / math.log1p(max_debt))
        components = {
            "governance": governance_component,
            "coverage": coverage_component,
            "topology": topology_component,
            "criticality": criticality_component,
            "debt": debt_component,
        }
        max_component = max(components.values(), default=0.0)
        primary_driver = (
            max(components, key=lambda key: (components[key], key)) if max_component > 0.0 else "none"
        )
        risk_score = round(min(100.0, sum(components.values())), 2)
        if risk_score >= 75.0:
            risk_band = "P0_CRITICAL"
        elif risk_score >= 55.0:
            risk_band = "P1_HIGH"
        elif risk_score >= 30.0:
            risk_band = "P2_MEDIUM"
        else:
            risk_band = "P3_LOW"

        recommendations = {
            "governance": (
                "Resolve active high-severity findings and route writes/egress " "through approved gates."
            ),
            "coverage": "Add behavior-level tests for this high-impact module before changing it.",
            "topology": "Break cycles or reduce unresolved/dynamic dependencies; validate blast radius.",
            "criticality": "Split responsibilities or add a stable facade to reduce dependency blast radius.",
            "debt": "Refactor concentrated debt in small, test-backed slices.",
            "none": "No material graph-health risk is currently evidenced for this module.",
        }
        evidence_count = (
            high_count
            + medium_count
            + risk_edges
            + dynamic_edges
            + cycle_coupling
            + write_bypasses
            + (1 if criticality > 0.0 else 0)
            + (1 if coverage >= 0.0 else 0)
        )

        output.append(
            (
                snapshot_id,
                node_id,
                file_path,
                layer,
                round(criticality, 4),
                round(combined, 4),
                round(debt, 4),
                round(coverage, 2),
                priority,
                high_count,
                medium_count,
                risk_edges,
                dynamic_edges,
                cycle_coupling,
                write_bypasses,
                risk_score,
                risk_band,
                primary_driver,
                recommendations[primary_driver],
                evidence_count,
            )
        )

    output.sort(key=lambda row: (-float(row[15]), str(row[2])))
    return output


def _collect_signals(
    conn: sqlite3.Connection,
    *,
    production_modules: int,
) -> list[HealthSignal]:
    signals: list[HealthSignal] = []

    active_high, violations_available = _active_high_violations(conn)
    write_bypass = _write_bypass_count(conn)
    gateway_available = _table_exists(conn, "mv_gateway_bypass_paths")
    gateway_bypass = (
        int(_scalar(conn, "SELECT COUNT(*) FROM mv_gateway_bypass_paths")) if gateway_available else 0
    )
    dynamic_exec = (
        int(_scalar(conn, "SELECT COUNT(*) FROM edges WHERE relation_type='dynamic_exec'"))
        if _table_exists(conn, "edges")
        else 0
    )
    signals.extend(
        (
            _make_signal(
                key="active_high_violations",
                dimension="governance_safety",
                value=active_high,
                unit="count",
                polarity="lower_is_better",
                warn=1,
                critical=10,
                available=violations_available,
                weight=2.0,
                source_table="violations",
                description="Open CRITICAL/HIGH findings not resolved, approved, or exempted.",
            ),
            _make_signal(
                key="write_bypass_paths",
                dimension="governance_safety",
                value=write_bypass,
                unit="count",
                polarity="lower_is_better",
                warn=1,
                critical=5,
                available=_table_exists(conn, "mv_write_sovereignty_paths"),
                weight=2.0,
                source_table="mv_write_sovereignty_paths",
                description="Durable-write paths that do not prove UWG routing.",
            ),
            _make_signal(
                key="gateway_bypass_paths",
                dimension="governance_safety",
                value=gateway_bypass,
                unit="count",
                polarity="lower_is_better",
                warn=1,
                critical=5,
                available=gateway_available,
                weight=1.5,
                source_table="mv_gateway_bypass_paths",
                description="Provider/egress surfaces outside approved gateways.",
            ),
            _make_signal(
                key="dynamic_exec_edges",
                dimension="governance_safety",
                value=dynamic_exec,
                unit="count",
                polarity="lower_is_better",
                warn=1,
                critical=3,
                available=_table_exists(conn, "edges"),
                weight=1.5,
                source_table="edges",
                description="Dynamic execution edges that make static graph closure incomplete.",
            ),
        )
    )

    structural_total, cross_layer = _structural_edge_metrics(conn)
    cross_layer_pct = 0.0 if structural_total == 0 else 100.0 * cross_layer / structural_total
    cyclic_modules, cycle_available = _cycle_coupling_metrics(conn)
    unknown_available = _table_exists(conn, "mv_unknown_taxonomy_and_orphans")
    unknown_orphans = (
        int(_scalar(conn, "SELECT COUNT(*) FROM mv_unknown_taxonomy_and_orphans")) if unknown_available else 0
    )
    unknown_pct = 0.0 if production_modules == 0 else 100.0 * unknown_orphans / production_modules
    signals.extend(
        (
            _make_signal(
                key="cyclic_coupling_modules",
                dimension="architecture",
                value=cyclic_modules,
                unit="count",
                polarity="lower_is_better",
                warn=1,
                critical=10,
                available=cycle_available,
                weight=2.0,
                source_table="mv_graph_scc_clusters,edges",
                description="Production modules participating in cyclic or tightly coupled graph zones.",
            ),
            _make_signal(
                key="cross_layer_edge_pct",
                dimension="architecture",
                value=cross_layer_pct,
                unit="percent",
                polarity="lower_is_better",
                warn=5,
                critical=15,
                available=structural_total > 0,
                weight=1.5,
                source_table="edges,nodes",
                description="Share of production imports/calls that cross declared layers.",
            ),
            _make_signal(
                key="unknown_orphan_pct",
                dimension="architecture",
                value=unknown_pct,
                unit="percent_of_modules",
                polarity="lower_is_better",
                warn=1,
                critical=5,
                available=unknown_available and production_modules > 0,
                weight=1.0,
                source_table="mv_unknown_taxonomy_and_orphans",
                description="Production modules with unknown taxonomy or orphaned graph identity.",
            ),
        )
    )

    coverage = _coverage_metrics(conn, production_modules)
    coverage_available = bool(coverage["available"])
    signals.extend(
        (
            _make_signal(
                key="high_risk_protected_pct",
                dimension="test_protection",
                value=float(coverage["high_risk_protected_pct"]),
                unit="percent",
                polarity="higher_is_better",
                warn=70,
                critical=90,
                available=coverage_available,
                weight=2.0,
                source_table="mv_hotspot_coverage_risk",
                description="High/critical graph-risk modules with at least 70% measured coverage.",
            ),
            _make_signal(
                key="p1_urgent_coverage_hotspots",
                dimension="test_protection",
                value=float(coverage["p1_urgent"]),
                unit="count",
                polarity="lower_is_better",
                warn=1,
                critical=10,
                available=coverage_available,
                weight=2.0,
                source_table="mv_hotspot_coverage_risk",
                description="High/critical modules with absent or minimal coverage.",
            ),
            _make_signal(
                key="coverage_inventory_pct",
                dimension="test_protection",
                value=float(coverage["coverage_inventory_pct"]),
                unit="percent_of_modules",
                polarity="higher_is_better",
                warn=70,
                critical=90,
                available=coverage_available and production_modules > 0,
                weight=1.0,
                source_table="mv_hotspot_coverage_risk",
                description="Production modules represented in the coverage ingest.",
            ),
        )
    )

    total_edges, proof_edges, risk_edges, authority_available = _edge_authority_metrics(conn)
    authoritative_pct = 0.0 if total_edges == 0 else 100.0 * proof_edges / total_edges
    unresolved_pct = 0.0 if total_edges == 0 else 100.0 * risk_edges / total_edges
    quick_check_value = _meta_value(conn, "sqlite_quick_check")
    foreign_key_value = _meta_value(conn, "sqlite_foreign_key_violation_count")
    quick_available = quick_check_value is not None
    foreign_key_available = foreign_key_value is not None
    try:
        foreign_key_count = float(foreign_key_value or 0.0)
    except ValueError:
        foreign_key_count = 0.0
        foreign_key_available = False

    signals.extend(
        (
            _make_signal(
                key="authoritative_edge_pct",
                dimension="graph_truth",
                value=authoritative_pct,
                unit="percent",
                polarity="higher_is_better",
                warn=90,
                critical=98,
                available=authority_available and total_edges > 0,
                weight=2.0,
                source_table="edges.authority_status",
                description="Production edges classified as proof under the three-bucket authority law.",
            ),
            _make_signal(
                key="risk_edge_pct",
                dimension="graph_truth",
                value=unresolved_pct,
                unit="percent",
                polarity="lower_is_better",
                warn=2,
                critical=10,
                available=authority_available and total_edges > 0,
                weight=2.0,
                source_table="edges.authority_status",
                description="Production edges classified as risk rather than proof.",
            ),
            _make_signal(
                key="foreign_key_violations",
                dimension="graph_truth",
                value=foreign_key_count,
                unit="count",
                polarity="lower_is_better",
                warn=1,
                critical=5,
                available=foreign_key_available,
                weight=2.0,
                source_table="meta.sqlite_foreign_key_violation_count",
                description="Rows returned by SQLite PRAGMA foreign_key_check.",
            ),
            _make_signal(
                key="sqlite_quick_check_ok",
                dimension="graph_truth",
                value=1.0 if quick_check_value == "ok" else 0.0,
                unit="boolean",
                polarity="binary_good",
                warn=1,
                critical=1,
                available=quick_available,
                weight=2.0,
                source_table="meta.sqlite_quick_check",
                description="Structural SQLite quick-check result recorded during materialization.",
            ),
        )
    )

    regression = _regression_metrics(conn, production_modules)
    regression_available = bool(regression.get("available", False))
    signals.extend(
        (
            _make_signal(
                key="violation_delta",
                dimension="change_safety",
                value=float(regression.get("violation_delta", 0.0)),
                unit="new_count",
                polarity="lower_is_better",
                warn=1,
                critical=10,
                available=regression_available,
                weight=1.5,
                source_table="mv_snapshot_regression_summary",
                description="Positive change in total violations versus the prior snapshot.",
            ),
            _make_signal(
                key="write_bypass_delta",
                dimension="change_safety",
                value=float(regression.get("bypass_delta", 0.0)),
                unit="new_count",
                polarity="lower_is_better",
                warn=1,
                critical=3,
                available=regression_available,
                weight=2.0,
                source_table="mv_snapshot_regression_summary",
                description="Positive change in write-sovereignty bypasses.",
            ),
            _make_signal(
                key="cross_layer_delta",
                dimension="change_safety",
                value=float(regression.get("cross_layer_delta", 0.0)),
                unit="new_count",
                polarity="lower_is_better",
                warn=1,
                critical=20,
                available=regression_available,
                weight=1.0,
                source_table="mv_snapshot_regression_summary",
                description="Positive change in cross-layer dependency edges.",
            ),
            _make_signal(
                key="debt_delta_per_module",
                dimension="change_safety",
                value=float(regression.get("debt_delta_per_module", 0.0)),
                unit="score_per_module",
                polarity="lower_is_better",
                warn=0.5,
                critical=2.0,
                available=regression_available,
                weight=1.0,
                source_table="mv_snapshot_regression_summary",
                description="Positive debt-score change normalized by production modules.",
            ),
        )
    )

    debt_per_module, debt_available = _debt_per_module(conn, production_modules)
    fan_defect_available = _table_exists(conn, "mv_high_fan_in_out_with_defects")
    fan_defects = (
        int(_scalar(conn, "SELECT COUNT(*) FROM mv_high_fan_in_out_with_defects"))
        if fan_defect_available
        else 0
    )
    signals.extend(
        (
            _make_signal(
                key="debt_per_module",
                dimension="maintainability",
                value=debt_per_module,
                unit="score_per_module",
                polarity="lower_is_better",
                warn=2,
                critical=8,
                available=debt_available,
                weight=1.5,
                source_table="mv_snapshot_baseline",
                description="Aggregate ADG debt score normalized by production module count.",
            ),
            _make_signal(
                key="top10_risk_concentration_pct",
                dimension="maintainability",
                value=float(coverage["top10_concentration_pct"]),
                unit="percent",
                polarity="lower_is_better",
                warn=25,
                critical=50,
                available=bool(coverage["concentration_available"]),
                weight=1.5,
                source_table="mv_hotspot_coverage_risk",
                description="Share of total graph/debt risk concentrated in the ten riskiest modules.",
            ),
            _make_signal(
                key="high_fan_defect_hotspots",
                dimension="maintainability",
                value=fan_defects,
                unit="count",
                polarity="lower_is_better",
                warn=5,
                critical=25,
                available=fan_defect_available,
                weight=1.0,
                source_table="mv_high_fan_in_out_with_defects",
                description="Modules combining high graph degree with defects.",
            ),
        )
    )

    return signals


def _create_schema(cur: sqlite3.Cursor) -> None:
    # Views depend on the physical tables; remove them first so refreshes stay
    # valid under stricter SQLite schema-dependency checking.
    cur.execute("DROP VIEW IF EXISTS v_repo_health")
    for table in reversed(_PHASE_G_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {table}")

    cur.executescript("""
        CREATE TABLE mv_repo_health_signals (
            snapshot_id        TEXT NOT NULL,
            signal_key         TEXT PRIMARY KEY,
            dimension          TEXT NOT NULL,
            value              REAL NOT NULL,
            unit               TEXT NOT NULL,
            polarity           TEXT NOT NULL,
            warn_threshold     REAL NOT NULL,
            critical_threshold REAL NOT NULL,
            score              REAL NOT NULL CHECK(score >= 0.0 AND score <= 100.0),
            status             TEXT NOT NULL,
            available          INTEGER NOT NULL CHECK(available IN (0, 1)),
            weight             REAL NOT NULL CHECK(weight > 0.0),
            source_table       TEXT NOT NULL,
            description        TEXT NOT NULL
        );

        CREATE TABLE mv_repo_health_dimensions (
            snapshot_id           TEXT NOT NULL,
            dimension             TEXT PRIMARY KEY,
            score                 REAL NOT NULL CHECK(score >= 0.0 AND score <= 100.0),
            status                TEXT NOT NULL,
            weight                REAL NOT NULL CHECK(weight > 0.0),
            signal_count          INTEGER NOT NULL,
            available_signal_count INTEGER NOT NULL,
            confidence            REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
            top_risk_signal       TEXT NOT NULL,
            evidence_json         TEXT NOT NULL
        );

        CREATE TABLE mv_repo_health_hotspots (
            snapshot_id                 TEXT NOT NULL,
            node_id                     INTEGER NOT NULL,
            file                        TEXT PRIMARY KEY,
            layer                       TEXT NOT NULL,
            criticality_score           REAL NOT NULL,
            combined_risk_score         REAL NOT NULL,
            total_debt_score            REAL NOT NULL,
            coverage_pct                REAL NOT NULL,
            priority_band               TEXT NOT NULL,
            active_high_violation_count INTEGER NOT NULL,
            active_medium_violation_count INTEGER NOT NULL,
            unresolved_edge_count       INTEGER NOT NULL,
            dynamic_edge_count          INTEGER NOT NULL,
            cycle_coupling_count        INTEGER NOT NULL,
            write_bypass_count          INTEGER NOT NULL,
            health_risk_score           REAL NOT NULL CHECK(health_risk_score >= 0.0 AND health_risk_score <= 100.0),
            health_risk_band            TEXT NOT NULL,
            primary_driver              TEXT NOT NULL,
            recommended_action          TEXT NOT NULL,
            evidence_count              INTEGER NOT NULL,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        );

        CREATE TABLE mv_repo_health_summary (
            snapshot_id                  TEXT PRIMARY KEY,
            overall_score                REAL NOT NULL CHECK(overall_score >= 0.0 AND overall_score <= 100.0),
            status                       TEXT NOT NULL,
            confidence                   REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
            available_weight             REAL NOT NULL,
            dimension_count              INTEGER NOT NULL,
            critical_signal_count        INTEGER NOT NULL,
            at_risk_signal_count         INTEGER NOT NULL,
            production_module_count      INTEGER NOT NULL,
            active_high_violation_count  INTEGER NOT NULL,
            p1_urgent_hotspot_count       INTEGER NOT NULL,
            authoritative_edge_pct       REAL NOT NULL,
            high_risk_protected_pct      REAL NOT NULL,
            regression_pressure          REAL NOT NULL,
            top_risk_dimension           TEXT NOT NULL,
            top_hotspot_file             TEXT NOT NULL,
            source_node_count             INTEGER NOT NULL,
            source_edge_count             INTEGER NOT NULL,
            source_violation_count        INTEGER NOT NULL,
            metric_contract_version       TEXT NOT NULL
        );

        CREATE INDEX idx_repo_health_signals_dimension
            ON mv_repo_health_signals(dimension, status, score);
        CREATE INDEX idx_repo_health_dimensions_score
            ON mv_repo_health_dimensions(score, dimension);
        CREATE INDEX idx_repo_health_hotspots_risk
            ON mv_repo_health_hotspots(health_risk_score DESC, file);
        CREATE INDEX idx_repo_health_hotspots_layer
            ON mv_repo_health_hotspots(layer, health_risk_band, health_risk_score DESC);

        CREATE VIEW v_repo_health AS
        SELECT * FROM mv_repo_health_summary;
        """)


def materialize_phase_g(
    sqlite_path: Path,
    *,
    conn: sqlite3.Connection | None = None,
) -> dict[str, int]:
    """Materialize the canonical repository-health contract.

    Idempotent and safe for reduced fixtures. Missing optional evidence is
    represented as unavailable signals and lowers confidence; it is never
    silently converted into a passing score.
    """

    owns_conn = conn is None
    if conn is None:
        conn = _connect_sqlite(sqlite_path)
    cur = conn.cursor()
    _create_schema(cur)

    snapshot_id = _snapshot_id(conn)
    production_modules = _production_module_count(conn)

    hotspot_rows = _hotspot_rows(conn, snapshot_id=snapshot_id)
    cur.executemany(
        """
        INSERT INTO mv_repo_health_hotspots VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        hotspot_rows,
    )

    signals = _collect_signals(conn, production_modules=production_modules)
    cur.executemany(
        """
        INSERT INTO mv_repo_health_signals VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        [
            (
                snapshot_id,
                signal.key,
                signal.dimension,
                signal.value,
                signal.unit,
                signal.polarity,
                signal.warn_threshold,
                signal.critical_threshold,
                signal.score,
                signal.status,
                int(signal.available),
                signal.weight,
                signal.source_table,
                signal.description,
            )
            for signal in signals
        ],
    )

    dimension_rows: list[tuple[object, ...]] = []
    for dimension, dimension_weight in _DIMENSION_WEIGHTS.items():
        members = [signal for signal in signals if signal.dimension == dimension]
        available = [signal for signal in members if signal.available]
        total_signal_weight = sum(signal.weight for signal in members)
        available_signal_weight = sum(signal.weight for signal in available)
        confidence = 0.0 if total_signal_weight <= 0.0 else available_signal_weight / total_signal_weight
        score = (
            0.0
            if available_signal_weight <= 0.0
            else sum(signal.score * signal.weight for signal in available) / available_signal_weight
        )
        status = _status_for_score(score, available=bool(available))
        top_risk = min(available, key=lambda signal: (signal.score, signal.key)).key if available else ""
        evidence = {
            signal.key: {
                "available": signal.available,
                "score": signal.score,
                "status": signal.status,
                "value": signal.value,
                "unit": signal.unit,
            }
            for signal in sorted(members, key=lambda item: item.key)
        }
        dimension_rows.append(
            (
                snapshot_id,
                dimension,
                round(score, 2),
                status,
                dimension_weight,
                len(members),
                len(available),
                round(confidence, 4),
                top_risk,
                json.dumps(evidence, sort_keys=True, separators=(",", ":")),
            )
        )

    cur.executemany(
        "INSERT INTO mv_repo_health_dimensions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        dimension_rows,
    )

    available_dimension_rows = [row for row in dimension_rows if int(row[6]) > 0]
    available_weight = sum(float(row[4]) for row in available_dimension_rows)
    overall_score = (
        0.0
        if available_weight <= 0.0
        else sum(float(row[2]) * float(row[4]) for row in available_dimension_rows) / available_weight
    )
    confidence = sum(float(row[4]) * float(row[7]) for row in dimension_rows)
    overall_status = (
        "UNKNOWN" if confidence < _CONFIDENCE_FLOOR else _status_for_score(overall_score, available=True)
    )
    top_risk_dimension = (
        str(min(available_dimension_rows, key=lambda row: (float(row[2]), str(row[1])))[1])
        if available_dimension_rows
        else ""
    )
    top_hotspot_file = str(hotspot_rows[0][2]) if hotspot_rows else ""
    signal_by_key = {signal.key: signal for signal in signals}
    regression_pressure = sum(
        signal_by_key[key].value
        for key in ("violation_delta", "write_bypass_delta", "cross_layer_delta")
        if key in signal_by_key and signal_by_key[key].available
    )

    source_node_count = int(_scalar(conn, "SELECT COUNT(*) FROM nodes"))
    source_edge_count = int(_scalar(conn, "SELECT COUNT(*) FROM edges"))
    source_violation_count = (
        int(_scalar(conn, "SELECT COUNT(*) FROM violations")) if _table_exists(conn, "violations") else 0
    )

    cur.execute(
        """
        INSERT INTO mv_repo_health_summary VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            snapshot_id,
            round(overall_score, 2),
            overall_status,
            round(confidence, 4),
            round(available_weight, 4),
            len(dimension_rows),
            sum(signal.status == "CRITICAL" for signal in signals if signal.available),
            sum(signal.status in {"WATCH", "AT_RISK"} for signal in signals if signal.available),
            production_modules,
            int(signal_by_key["active_high_violations"].value),
            int(signal_by_key["p1_urgent_coverage_hotspots"].value),
            round(signal_by_key["authoritative_edge_pct"].value, 2),
            round(signal_by_key["high_risk_protected_pct"].value, 2),
            round(regression_pressure, 4),
            top_risk_dimension,
            top_hotspot_file,
            source_node_count,
            source_edge_count,
            source_violation_count,
            _CONTRACT_VERSION,
        ),
    )

    if _table_exists(conn, "meta"):
        meta_values = {
            "repo_health_score": f"{overall_score:.2f}",
            "repo_health_status": overall_status,
            "repo_health_confidence": f"{confidence:.4f}",
            "repo_health_contract_version": _CONTRACT_VERSION,
        }
        conn.executemany(
            "INSERT INTO meta(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            sorted(meta_values.items()),
        )

    conn.commit()
    counts = {
        table: int(cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in _PHASE_G_TABLES
    }
    if owns_conn:
        conn.close()
    return counts
