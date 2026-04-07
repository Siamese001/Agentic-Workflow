"""ADG Graph Audit — ReAct + Late Chunking surfaces.

_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_1")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_2")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_3")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_4")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_5")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_6")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_7")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_8")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_9")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_10")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_11")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_12")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_13")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_14")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_15")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_16")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_17")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_18")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_19")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_20")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_21")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_22")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_23")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_24")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_25")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_26")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_27")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_28")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_29")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_30")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_31")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_32")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_33")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_34")
_emit_reads_through("l4", "react_chunking_graph_audit", "urg_read_35")
Queries the live ADG SQLite index to produce a structural report for:
  - ReAct reasoning nodes (L1_cognition/enforcement/react_strategy.py,
    L1_cognition/engines/react_engine.py, L1_cognition/config/react_config.py)
  - Late chunking nodes (utils/workflow_engines/late_chunking.py)

Outputs: reports/adg/react_chunking_graph_report.json

Hard rule: any detected layer-boundary violation causes exit code 1.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))  # guardian: allow-global-mutation

_ADG_DIR = _REPO_ROOT / "artifacts" / "adg"
_REPORT_OUT = _REPO_ROOT / "reports" / "adg" / "react_chunking_graph_report.json"

_REACT_MODULES = frozenset(
    {
        "agentic_core/L1_cognition/enforcement/react_strategy.py",
        "agentic_core/L1_cognition/engines/react_engine.py",
        "agentic_core/L1_cognition/config/react_config.py",
    },
)
_LATE_CHUNK_MODULES = frozenset(
    {
        "agentic_core/utils/workflow_engines/late_chunking.py",
    },
)

# ADG layer values: L0, L1, L2, L3, L4, L5, L6, L_APP, L_OPS, L_PG,
#   L_RUNTIME, L_SHARED, L_SL, L_TEST, L_TOOLS, L_UNKNOWN
# ReAct lives in L1 and may legitimately import L0, L1, L_RUNTIME, L_SHARED, L_UNKNOWN
_ALLOWED_REACT_LAYERS = frozenset({"L0", "L1", "L_RUNTIME", "L_SHARED", "L_UNKNOWN", "L_TEST"})
# late_chunking lives in L_SHARED and may import L0, L_SHARED, L_UNKNOWN
_ALLOWED_CHUNK_LAYERS = frozenset({"L0", "L_SHARED", "L_UNKNOWN", "L_TEST"})


def _latest_sqlite() -> Path:
    candidates = sorted(_ADG_DIR.glob("adg_indexed_*.sqlite"), reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No adg_indexed_*.sqlite found in {_ADG_DIR}")
    return candidates[0]


def _open_db() -> sqlite3.Connection:
    db_path = _latest_sqlite()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _layer_from_path(rel_path: str) -> str:
    """Extract layer name from a repo-relative module path."""
    parts = rel_path.replace("\\", "/").split("/")
    for part in parts:
        if part.startswith("L") and "_" in part:
            return part
    if "utils" in parts:
        return "utils"
    if "system_learning" in parts:
        return "system_learning"
    if "runtime" in parts:
        return "runtime"
    return "unknown"


def scan_react_nodes(conn: sqlite3.Connection) -> list[dict]:
    """Return all ADG nodes belonging to ReAct surface modules."""
    rows = []
    for mod in _REACT_MODULES:
        # resolved_path stores OS path; use both / and \ separators
        pattern = "%" + mod.split("/")[-2] + "%" + mod.split("/")[-1] + "%"
        cur = conn.execute(
            "SELECT * FROM nodes WHERE resolved_path LIKE ?",
            (pattern,),
        )
        rows.extend(dict(r) for r in cur.fetchall())
    return rows


def scan_late_chunk_nodes(conn: sqlite3.Connection) -> list[dict]:
    """Return all ADG nodes belonging to late chunking surface modules."""
    rows = []
    for mod in _LATE_CHUNK_MODULES:
        pattern = "%" + mod.split("/")[-1] + "%"
        cur = conn.execute(
            "SELECT * FROM nodes WHERE resolved_path LIKE ?",
            (pattern,),
        )
        rows.extend(dict(r) for r in cur.fetchall())
    return rows


def _node_ids(nodes: list[dict]) -> set:
    return {n["id"] for n in nodes if n.get("id") is not None}


def compute_fan_in(conn: sqlite3.Connection, node_ids: set) -> int:
    """Count edges pointing INTO the given node set."""
    if not node_ids:
        return 0
    placeholders = ",".join("?" * len(node_ids))
    cur = conn.execute(
        f"SELECT COUNT(*) FROM edges WHERE dst_id IN ({placeholders})",
        list(node_ids),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def compute_fan_out(conn: sqlite3.Connection, node_ids: set) -> int:
    """Count edges pointing OUT of the given node set."""
    if not node_ids:
        return 0
    placeholders = ",".join("?" * len(node_ids))
    cur = conn.execute(
        f"SELECT COUNT(*) FROM edges WHERE src_id IN ({placeholders})",
        list(node_ids),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def _detect_violations_for_surface(
    conn: sqlite3.Connection,
    node_ids: set,
    allowed_layers: frozenset[str],
    surface_name: str,
) -> list[dict]:
    """Detect edges from the surface into disallowed layers."""
    if not node_ids:
        return []
    placeholders = ",".join("?" * len(node_ids))
    cur = conn.execute(
        f"SELECT e.src_id, e.dst_id, e.relation_type, n.resolved_path AS target_path, n.layer AS target_layer "
        f"FROM edges e "
        f"JOIN nodes n ON e.dst_id = n.id "
        f"WHERE e.src_id IN ({placeholders})",
        list(node_ids),
    )
    violations = []
    for row in cur.fetchall():
        row_dict = dict(row)
        target_path = row_dict.get("target_path", "")
        target_layer = row_dict.get("target_layer") or _layer_from_path(target_path)
        if target_layer and target_layer not in allowed_layers and target_layer != "unknown":
            violations.append(
                {
                    "surface": surface_name,
                    "src_id": row_dict.get("src_id"),
                    "dst_id": row_dict.get("dst_id"),
                    "target_path": target_path,
                    "target_layer": target_layer,
                    "relation_type": row_dict.get("relation_type", ""),
                },
            )
    return violations


def detect_layer_boundary_violations(
    conn: sqlite3.Connection,
    react_ids: set,
    chunk_ids: set,
) -> list[dict]:
    """Detect layer-boundary violations for both surfaces."""
    violations = []
    violations.extend(_detect_violations_for_surface(conn, react_ids, _ALLOWED_REACT_LAYERS, "react"))
    violations.extend(_detect_violations_for_surface(conn, chunk_ids, _ALLOWED_CHUNK_LAYERS, "late_chunking"))
    return violations


def _count_dead_imports(conn: sqlite3.Connection, node_ids: set) -> int:
    """Count import edges from the surface with no matching target node (dead imports)."""
    if not node_ids:
        return 0
    placeholders = ",".join("?" * len(node_ids))
    cur = conn.execute(
        f"SELECT COUNT(*) FROM edges e "
        f"WHERE e.src_id IN ({placeholders}) "
        f"AND e.relation_type = 'imports' "
        f"AND NOT EXISTS (SELECT 1 FROM nodes n WHERE n.id = e.dst_id)",
        list(node_ids),
    )
    row = cur.fetchone()
    return row[0] if row else 0


def run_audit() -> dict:
    """Run the full audit and return the report dict."""
    conn = _open_db()
    try:
        react_nodes = scan_react_nodes(conn)
        chunk_nodes = scan_late_chunk_nodes(conn)

        react_ids = _node_ids(react_nodes)
        chunk_ids = _node_ids(chunk_nodes)

        violations = detect_layer_boundary_violations(conn, react_ids, chunk_ids)
        dead_react = _count_dead_imports(conn, react_ids)
        dead_chunk = _count_dead_imports(conn, chunk_ids)

        report = {
            "react_node_count": len(react_nodes),
            "react_fan_in": compute_fan_in(conn, react_ids),
            "react_fan_out": compute_fan_out(conn, react_ids),
            "late_chunk_node_count": len(chunk_nodes),
            "late_chunk_fan_in": compute_fan_in(conn, chunk_ids),
            "late_chunk_fan_out": compute_fan_out(conn, chunk_ids),
            "layer_violation_count": len(violations),
            "dead_imports_in_surface": dead_react + dead_chunk,
            "violations": violations,
        }
    finally:
        conn.close()
    return report


def main() -> int:
    report = run_audit()
    _REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_OUT.write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    print(
        f"[ADG-AUDIT] react_nodes={report['react_node_count']}  "
        f"fan_in={report['react_fan_in']}  fan_out={report['react_fan_out']}",
    )
    print(
        f"[ADG-AUDIT] chunk_nodes={report['late_chunk_node_count']}  "
        f"fan_in={report['late_chunk_fan_in']}  fan_out={report['late_chunk_fan_out']}",
    )
    print(
        f"[ADG-AUDIT] layer_violations={report['layer_violation_count']}  "
        f"dead_imports={report['dead_imports_in_surface']}",
    )
    print(f"[ADG-AUDIT] Report: {_REPORT_OUT}")
    if report["layer_violation_count"] > 0:
        print("[ADG-AUDIT] FAIL — layer boundary violations detected", file=sys.stderr)
        for v in report["violations"]:
            print(f"  {v['surface']} -> {v['target_layer']} ({v['target_path']})", file=sys.stderr)
        return 1
    print("[ADG-AUDIT] PASS")
    return 0
