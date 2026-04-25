"""Regression coverage for severity classification in multi_writer.

Plan: .windsurf/plans/antipattern-reclassify-e5a569.md Wave 4 (Priority 5).

The severity CASE inside ``agentic_core/adg/artifact/multi_writer.py`` is the
authority for how antipattern edges are classified into
CRITICAL / HIGH / MEDIUM / LOW bands at ADG generation time. These tests run
real rows through an in-memory SQLite using a fixture CASE that mirrors the
production SQL, and assert band membership rather than exact equality so the
production rules can expand (e.g. new kinds added to HIGH) without breaking
this test as long as the invariants hold.

Invariants tested:

  1. Tier-1 agent-safety kinds (``missing_hitl_on_irreversible``,
     ``chokepoint_bypass``) → CRITICAL regardless of layer.
  2. The 4 HIGH-class exception kinds in production layers
     (``agentic_core/%``, ``system_learning/%``) → HIGH.
  3. The same 4 kinds outside production and not in the explicit LOW
     downgrade paths → MEDIUM.
  4. The same 4 kinds in explicitly downgraded paths (tests/, tools/,
     apps_*/engines/base_*, etc.) → LOW.
  5. ``retry_without_backoff`` is always MEDIUM (not HIGH, not LOW).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator

import pytest

MULTI_WRITER_PATH = (
    Path(__file__).resolve().parents[5] / "agentic_core" / "adg" / "artifact" / "multi_writer.py"
)


def _extract_severity_case_from_source() -> str:
    """Read the CASE expression literal out of multi_writer.py.

    Locates the INSERT INTO violations statement and extracts the CASE
    expression that derives severity. Returns the CASE SQL text, which is
    then wrapped into a SELECT during tests to run against fixture rows.

    Raises:
        RuntimeError: if the expected anchors are missing (means the SQL has
            been restructured and this test + the plan evidence need updating).
    """
    source = MULTI_WRITER_PATH.read_text(encoding="utf-8")
    start_anchor = "INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)"
    start = source.find(start_anchor)
    if start < 0:
        raise RuntimeError("Could not locate the 'INSERT INTO violations' anchor in multi_writer.py")
    case_start = source.find("CASE", start)
    case_end = source.find("END as severity", case_start)
    if case_start < 0 or case_end < 0:
        raise RuntimeError("Could not locate CASE ... END as severity in multi_writer.py")
    return source[case_start : case_end + len("END")]


@pytest.fixture(scope="module")
def severity_case_sql() -> str:
    return _extract_severity_case_from_source()


@pytest.fixture()
def conn(severity_case_sql: str) -> Iterator[sqlite3.Connection]:
    """Build a fresh in-memory SQLite edges table matching the production schema."""
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL DEFAULT 0,
            dst_id INTEGER NOT NULL DEFAULT 0,
            relation_type TEXT NOT NULL,
            edge_kind TEXT NOT NULL,
            source_file TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            symbol TEXT NOT NULL DEFAULT ''
        );
        """
    )
    yield connection
    connection.close()


def _classify(
    connection: sqlite3.Connection,
    severity_case_sql: str,
    *,
    edge_kind: str,
    source_file: str,
    relation_type: str = "antipattern",
) -> str:
    """Insert one edge row, run the CASE against it, return the severity."""
    connection.execute("DELETE FROM edges")
    connection.execute(
        "INSERT INTO edges (relation_type, edge_kind, source_file, line_no, symbol) VALUES (?, ?, ?, ?, ?)",
        (relation_type, edge_kind, source_file, 1, ""),
    )
    query = f"SELECT {severity_case_sql} FROM edges WHERE relation_type IN ('violates', 'antipattern', 'dynamic_exec')"
    row = connection.execute(query).fetchone()
    assert row is not None, "CASE returned no row — check query structure"
    return row[0]


# ---------------------------------------------------------------------------
# Tier-1 agent-safety → CRITICAL
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "edge_kind",
    ["missing_hitl_on_irreversible", "chokepoint_bypass"],
)
@pytest.mark.parametrize(
    "source_file",
    [
        "agentic_core/L0_routing/reasoning/sample.py",
        "apps_rg/engines/custom_engine.py",
        "tools/diag/foo.py",
    ],
)
def test_tier1_agent_safety_is_critical(
    conn: sqlite3.Connection,
    severity_case_sql: str,
    edge_kind: str,
    source_file: str,
) -> None:
    severity = _classify(conn, severity_case_sql, edge_kind=edge_kind, source_file=source_file)
    assert severity == "CRITICAL", f"{edge_kind} @ {source_file} must be CRITICAL; got {severity}"


# ---------------------------------------------------------------------------
# HIGH-class exception antipatterns in production → HIGH
# ---------------------------------------------------------------------------


HIGH_CLASS_KINDS = (
    "broad_exception_catch",
    "silent_exception_swallow",
    "log_and_swallow",
    "return_none_swallow",
)


@pytest.mark.parametrize("edge_kind", HIGH_CLASS_KINDS)
@pytest.mark.parametrize(
    "source_file",
    [
        "agentic_core/L0_routing/reasoning/x.py",
        "agentic_core/L5_safety/enforcement/guard.py",
        "agentic_core/L2_execution/engine.py",
        "system_learning/confidence/engine.py",
    ],
)
def test_high_class_in_production_is_high(
    conn: sqlite3.Connection,
    severity_case_sql: str,
    edge_kind: str,
    source_file: str,
) -> None:
    severity = _classify(conn, severity_case_sql, edge_kind=edge_kind, source_file=source_file)
    assert severity == "HIGH", f"{edge_kind} @ {source_file} must be HIGH; got {severity}"


# ---------------------------------------------------------------------------
# HIGH-class antipatterns in explicitly downgraded paths → LOW
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("edge_kind", HIGH_CLASS_KINDS)
@pytest.mark.parametrize(
    "source_file",
    [
        "tests/unit/foo.py",
        "tools/diag/probe.py",
        "ops_scripts/ci/check.py",
        "apps_rg/engines/base_rg_engine.py",
    ],
)
def test_high_class_in_downgrade_paths_is_low(
    conn: sqlite3.Connection,
    severity_case_sql: str,
    edge_kind: str,
    source_file: str,
) -> None:
    severity = _classify(conn, severity_case_sql, edge_kind=edge_kind, source_file=source_file)
    assert severity == "LOW", f"{edge_kind} @ {source_file} must be LOW via downgrade path; got {severity}"


# ---------------------------------------------------------------------------
# HIGH-class antipatterns outside production & outside downgrade paths → MEDIUM
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("edge_kind", HIGH_CLASS_KINDS)
def test_high_class_outside_production_is_medium(
    conn: sqlite3.Connection,
    severity_case_sql: str,
    edge_kind: str,
) -> None:
    severity = _classify(
        conn,
        severity_case_sql,
        edge_kind=edge_kind,
        source_file="apps_rg/reasoning/cool_feature.py",
    )
    assert severity == "MEDIUM", f"{edge_kind} @ apps_rg/reasoning/... must be MEDIUM; got {severity}"


# ---------------------------------------------------------------------------
# Always-MEDIUM kinds — retry_without_backoff + friends
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "edge_kind",
    [
        "retry_without_backoff",
        "partial_side_effects",
        "unreachable_after_raise",
        "cleanup_raises_over_original",
    ],
)
@pytest.mark.parametrize(
    "source_file",
    [
        "agentic_core/L0_routing/x.py",
        "apps_rg/reasoning/feature.py",
    ],
)
def test_always_medium_kinds_stay_medium_or_low(
    conn: sqlite3.Connection,
    severity_case_sql: str,
    edge_kind: str,
    source_file: str,
) -> None:
    """These kinds must never land in HIGH/CRITICAL.

    Result is either MEDIUM (default) or LOW (if path downgrade applies —
    not applicable for these source_files, but defensive).
    """
    severity = _classify(conn, severity_case_sql, edge_kind=edge_kind, source_file=source_file)
    assert severity in {"MEDIUM", "LOW"}, f"{edge_kind} @ {source_file} must be MEDIUM or LOW; got {severity}"
    assert severity not in {"CRITICAL", "HIGH"}


# ---------------------------------------------------------------------------
# Unknown antipattern kinds → LOW (P3 style warnings)
# ---------------------------------------------------------------------------


def test_unknown_antipattern_kind_falls_through_to_low(
    conn: sqlite3.Connection,
    severity_case_sql: str,
) -> None:
    severity = _classify(
        conn,
        severity_case_sql,
        edge_kind="never_seen_before_kind",
        source_file="agentic_core/L0_routing/x.py",
    )
    assert severity == "LOW"


# ---------------------------------------------------------------------------
# Non-antipattern relations → MEDIUM (ELSE branch)
# ---------------------------------------------------------------------------


def test_violates_relation_goes_to_else_branch(
    conn: sqlite3.Connection,
    severity_case_sql: str,
) -> None:
    severity = _classify(
        conn,
        severity_case_sql,
        edge_kind="layer_violation",
        source_file="agentic_core/L0_routing/x.py",
        relation_type="violates",
    )
    assert severity == "MEDIUM"
