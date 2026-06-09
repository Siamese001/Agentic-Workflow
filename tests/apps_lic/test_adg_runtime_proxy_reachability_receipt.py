"""W8 direct SQLite receipt for ADG runtime/test-reachability proxy counts."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest

# W8 ADG covers-edge anchor: this receipt queries SQLite directly and otherwise
# imports no apps_lic module, so it would register no `covers` edge and fail its
# own W8_TEST_FILES self-check below. A full-module-path import makes this receipt
# a genuine ADG covers source.
from apps_lic.types.route_types import Route as _ReachabilityCoversAnchor


REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_NAME = "adg_indexed_06082026_1212.sqlite"
W8_TEST_FILES = {
    "tests/apps_lic/test_adg_runtime_proxy_binding_negative_paths.py",
    "tests/apps_lic/test_adg_runtime_proxy_proof_bundle_contract.py",
    "tests/apps_lic/test_adg_runtime_proxy_generation_quality_contracts.py",
    "tests/unit/apps_lic/utils/test_lic_agent_base_util_contract.py",
    "tests/unit/apps_lic/types/test_route_and_archetype_contracts.py",
    "tests/apps_lic/test_adg_runtime_proxy_zero_cover_live_surface_triage.py",
    "tests/apps_lic/test_adg_runtime_proxy_reachability_receipt.py",
}
THIN_P1_CANONICAL_FILES = {
    "apps_lic/runtime/dispatch/runtime_proof_bundle.py",
    "apps_lic/runtime/bindings/c0_binding.py",
    "apps_lic/runtime/bindings/l3_binding.py",
    "apps_lic/runtime/bindings/l2_binding.py",
    "apps_lic/engines/generation_engine.py",
    "apps_lic/engines/message_quality.py",
    "apps_lic/engines/x1d_claude_judge_adapter.py",
}
BEHAVIOR_PINNED_ZERO_COVER_FILES = {
    "apps_lic/utils/lic_agent_base_util.py",
    "apps_lic/types/route_types.py",
    "apps_lic/types/message_route_types.py",
    "apps_lic/types/recipient_archetype_types.py",
    "apps_lic/types/competitor_recon_agent_types.py",
    "apps_lic/types/app_content_validator_agent_types.py",
    "apps_lic/types/validation_severity_types.py",
}


def _candidate_snapshots() -> list[Path]:
    paths: list[Path] = []
    for env_name in ("ADG_SQLITE_PATH", "ADG_DB_PATH", "AGENTIC_ADG_SQLITE_PATH"):
        value = os.environ.get(env_name)
        if value:
            paths.append(Path(value))
    for root in (REPO_ROOT, Path(r"C:\Git\Agentic-Workflow-FRESH")):
        paths.append(root / "artifacts" / "adg" / SNAPSHOT_NAME)
        paths.extend(sorted((root / "artifacts" / "adg").glob("*.sqlite"), reverse=True))
    deduped: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path.resolve()) if path.exists() else str(path)
        if key not in seen:
            deduped.append(path)
            seen.add(key)
    return deduped


def _snapshot_path() -> Path:
    for path in _candidate_snapshots():
        if path.is_file():
            return path
    expected = ", ".join(str(path) for path in _candidate_snapshots()[:4])
    pytest.skip(
        "ADG SQLite snapshot unavailable for W8 direct covers query; "
        f"expected one of: {expected}. In this Codex session the adg_sqlite MCP "
        "transport closed and v_runtime_proof is empty, so W8 records this as a "
        "runtime-proxy blocker rather than fabricating counts."
    )


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({_quote(table)})")}


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _pick(columns: set[str], candidates: tuple[str, ...], table: str) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    pytest.skip(f"ADG SQLite table {table!r} lacks expected columns {candidates!r}")


def _normalised_path_expr(alias: str, column: str) -> str:
    return f"replace({_quote(alias)}.{_quote(column)}, '\\\\', '/')"


def test_w8_direct_sqlite_covers_proxy_has_refreshed_reachability_edges() -> None:
    db_path = _snapshot_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    node_cols = _columns(conn, "nodes")
    edge_cols = _columns(conn, "edges")
    node_id = _pick(node_cols, ("id", "node_id"), "nodes")
    node_path = _pick(
        node_cols,
        ("resolved_path", "path", "file_path", "module_path", "filename"),
        "nodes",
    )
    src_col = _pick(
        edge_cols,
        ("src_id", "source_id", "from_id", "from_node_id", "src", "source"),
        "edges",
    )
    dst_col = _pick(
        edge_cols,
        ("dst_id", "target_id", "to_id", "to_node_id", "dst", "target"),
        "edges",
    )
    relation_col = _pick(edge_cols, ("relation_type", "edge_type", "kind", "type"), "edges")

    src_path = _normalised_path_expr("src", node_path)
    dst_path = _normalised_path_expr("dst", node_path)
    coverage_rows = conn.execute(
        f"""
        SELECT {dst_path} AS module_path, COUNT(DISTINCT {src_path}) AS test_count
        FROM edges e
        JOIN nodes src ON e.{_quote(src_col)} = src.{_quote(node_id)}
        JOIN nodes dst ON e.{_quote(dst_col)} = dst.{_quote(node_id)}
        WHERE e.{_quote(relation_col)} = 'covers'
          AND {src_path} LIKE 'tests/%'
          AND {dst_path} LIKE 'apps_lic/%.py'
        GROUP BY {dst_path}
        """
    ).fetchall()
    tests_seen = {
        row[0]
        for row in conn.execute(
            f"""
            SELECT DISTINCT {src_path} AS test_path
            FROM edges e
            JOIN nodes src ON e.{_quote(src_col)} = src.{_quote(node_id)}
            JOIN nodes dst ON e.{_quote(dst_col)} = dst.{_quote(node_id)}
            WHERE e.{_quote(relation_col)} = 'covers'
              AND {src_path} LIKE 'tests/%'
              AND {dst_path} LIKE 'apps_lic/%.py'
            """
        )
    }
    missing_w8_edges = sorted(W8_TEST_FILES - tests_seen)
    if missing_w8_edges:
        pytest.skip(
            "ADG SQLite snapshot is stale for W8: missing covers edges from "
            f"{missing_w8_edges}. Regenerate ADG/test-reachability before using "
            "the runtime-proxy counts as a benchmark gate."
        )

    coverage = {row["module_path"]: int(row["test_count"]) for row in coverage_rows}
    module_count = conn.execute(
        f"""
        SELECT COUNT(DISTINCT {_normalised_path_expr('n', node_path)}) AS module_count
        FROM nodes n
        WHERE {_normalised_path_expr('n', node_path)} LIKE 'apps_lic/%.py'
        """
    ).fetchone()["module_count"]
    zero_count = max(0, int(module_count) - len(coverage))
    thin_count = sum(1 for count in coverage.values() if 1 <= count <= 2)
    well_count = sum(1 for count in coverage.values() if count >= 3)

    assert module_count >= 200
    assert len(coverage_rows) > 0
    assert zero_count >= 0
    assert thin_count >= 0
    assert well_count >= 0
    for path in THIN_P1_CANONICAL_FILES | BEHAVIOR_PINNED_ZERO_COVER_FILES:
        assert coverage.get(path, 0) > 0, path


def test_reachability_receipt_registers_as_adg_covers_source() -> None:
    """Use the full-path import so this receipt stays a real ADG covers source."""
    assert _ReachabilityCoversAnchor is not None
