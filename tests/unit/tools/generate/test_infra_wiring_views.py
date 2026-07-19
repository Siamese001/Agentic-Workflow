"""Tests for tools/generate/infra_wiring_views.py"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tools.generate import infra_wiring_views as infra_wiring
from tools.generate.infra_wiring_views import (
    _APPROVED_ADAPTER_PATHS,
    _PROCESS_BOUNDARY_ADAPTERS,
    materialize_infra_views,
)


def _write_receipt_source(repo_root: Path, calls_by_line: dict[int, str]) -> None:
    path = repo_root / "apps_rg/fact_inventory/c03_graph_kpi_health.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    last_line = max(calls_by_line)
    lines = ["# filler"] * last_line
    for line_no, source in calls_by_line.items():
        lines[line_no - 1] = source
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _create_test_db(tmp_path: Path) -> Path:
    """Create a minimal ADG SQLite with nodes/edges tables for testing."""
    db_path = tmp_path / "test_adg.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE nodes (
            id            INTEGER PRIMARY KEY,
            adg_name      TEXT NOT NULL,
            entity_type   TEXT NOT NULL,
            layer         TEXT NOT NULL,
            identity_kind TEXT NOT NULL,
            confidence    TEXT NOT NULL,
            resolved_path TEXT NOT NULL,
            precision_type TEXT DEFAULT 'symbol',
            span_start INTEGER DEFAULT 0, span_end INTEGER DEFAULT 0,
            span_line INTEGER DEFAULT 0, span_column INTEGER DEFAULT 0,
            span_end_line INTEGER DEFAULT 0, span_end_column INTEGER DEFAULT 0,
            logical_sequence_id INTEGER DEFAULT 0,
            control_path_id TEXT DEFAULT '',
            temporal_order INTEGER DEFAULT 0,
            type_surface TEXT DEFAULT '',
            enclosing_symbol TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE edges (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id        INTEGER NOT NULL REFERENCES nodes(id),
            dst_id        INTEGER NOT NULL REFERENCES nodes(id),
            relation_type TEXT NOT NULL,
            edge_kind     TEXT NOT NULL,
            source_file   TEXT,
            line_no       INTEGER,
            symbol        TEXT NOT NULL DEFAULT '',
            semantic_type TEXT DEFAULT '',
            confidence_score REAL DEFAULT 1.0,
            source_span_start INTEGER DEFAULT 0, source_span_end INTEGER DEFAULT 0,
            source_span_line INTEGER DEFAULT 0, source_span_column INTEGER DEFAULT 0,
            target_span_start INTEGER DEFAULT 0, target_span_end INTEGER DEFAULT 0,
            target_span_line INTEGER DEFAULT 0, target_span_column INTEGER DEFAULT 0,
            dynamic_resolution TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()
    return db_path


def _insert_node(
    conn: sqlite3.Connection,
    node_id: int,
    adg_name: str,
    entity_type: str,
    layer: str,
    identity_kind: str,
    resolved_path: str,
) -> None:
    conn.execute(
        "INSERT INTO nodes (id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path) "
        "VALUES (?, ?, ?, ?, ?, 'high', ?)",
        (node_id, adg_name, entity_type, layer, identity_kind, resolved_path),
    )


def _insert_edge(
    conn: sqlite3.Connection,
    src_id: int,
    dst_id: int,
    relation_type: str,
    source_file: str | None,
    line_no: int | None,
    symbol: str = "",
    edge_kind: str = "direct",
) -> None:
    conn.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol),
    )


class TestMaterializeInfraViews:
    """Tests for materialize_infra_views()."""

    def test_empty_db_returns_zero_counts(self, tmp_path: Path) -> None:
        """Happy path: empty DB produces views with zero rows."""
        db_path = _create_test_db(tmp_path)
        counts = materialize_infra_views(db_path)
        for view_name, count in counts.items():
            assert count == 0, f"{view_name} should be 0 on empty DB, got {count}"

    def test_detects_apps_direct_infra_p0(self, tmp_path: Path) -> None:
        """Happy path: detects P0 violation when apps_* imports raw infra."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        # Node: apps_eval file
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_eval/services/bad.py",
            "module",
            "apps",
            "internal_module",
            "apps_eval/services/bad.py",
        )
        # Node: sqlite3 external module
        _insert_node(conn, 2, "ADG::Symbol::sqlite3", "external", "external", "external_module", "sqlite3")
        # Edge: apps_eval imports sqlite3
        _insert_edge(conn, 1, 2, "imports", "apps_eval/services/bad.py", 6, "sqlite3")
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        assert counts["v_p0_apps_direct_infra"] == 1

    def test_detects_apps_rg_fact_ingest_raw_chromadb_import(self, tmp_path: Path) -> None:
        """Regression: c02_fact_vector_ingest is no longer grandfathered for raw Chroma imports."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_rg/runtime/c0/c02_fact_vector_ingest.py",
            "module",
            "L_APP",
            "repo_module",
            "apps_rg/runtime/c0/c02_fact_vector_ingest.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::chromadb", "external", "external", "external_module", "chromadb")
        _insert_edge(conn, 1, 2, "imports", "apps_rg/runtime/c0/c02_fact_vector_ingest.py", 183, "chromadb")
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        assert counts["v_p0_apps_direct_infra"] == 1

    def test_apps_rg_fact_ingest_adapter_import_clears_raw_chromadb_view(self, tmp_path: Path) -> None:
        """Fixed code imports the sanctioned L4 adapter module, so no raw-SDK P0 row appears."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_rg/runtime/c0/c02_fact_vector_ingest.py",
            "module",
            "L_APP",
            "repo_module",
            "apps_rg/runtime/c0/c02_fact_vector_ingest.py",
        )
        _insert_node(
            conn,
            2,
            "ADG::Module::agentic_core/L4_state/utils/client/chroma_client.py",
            "module",
            "L4",
            "repo_module",
            "agentic_core/L4_state/utils/client/chroma_client.py",
        )
        _insert_edge(
            conn,
            1,
            2,
            "imports",
            "apps_rg/runtime/c0/c02_fact_vector_ingest.py",
            183,
            "chromadb_module",
        )
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        assert counts["v_p0_apps_direct_infra"] == 0

    def test_apps_shared_not_flagged_as_p0(self, tmp_path: Path) -> None:
        """Edge case: apps_shared imports are NOT P0 violations."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_shared/utils/tracing.py",
            "module",
            "apps",
            "internal_module",
            "apps_shared/utils/tracing.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 2, "imports", "apps_shared/utils/tracing.py", 3, "redis")
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        assert counts["v_p0_apps_direct_infra"] == 0

    def test_idempotent_view_creation(self, tmp_path: Path) -> None:
        """Edge case: calling twice does not error (views recreated)."""
        db_path = _create_test_db(tmp_path)
        counts1 = materialize_infra_views(db_path)
        counts2 = materialize_infra_views(db_path)
        assert counts1 == counts2

    def test_views_exist_in_sqlite(self, tmp_path: Path) -> None:
        """Verification: all infra wiring views are registered in sqlite_master."""
        db_path = _create_test_db(tmp_path)
        materialize_infra_views(db_path)
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        view_names = {r[0] for r in cursor.fetchall()}
        conn.close()
        expected = {
            "v_p0_apps_direct_infra",
            "v_p0_provider_bypass",
            "v_p0_core_imports_apps",
            "v_p0_write_bypass_uwg",
            "v_p0_l1_direct_infra",
            "v_p0_l6_mutation",
            "v_p0_l0_raw_execution",
            "v_p1_zero_caller_infra",
            "v_p1_not_on_spine",
            "v_p1_ad_hoc_imports",
            "v_p1_mis_layered_infra",
            "v_p1_raw_http_outside_seam",
            "v_p2_mixed_usage",
            "v_p2_duplicated_adapters",
            "v_p2_dormant_ambiguous",
            "v_p3_isolated_experimental",
            "v_infra_violations_summary",
        }
        assert expected == view_names

    def test_summary_view_unions_all_p0_views(self, tmp_path: Path) -> None:
        """Happy path: summary view is union of all P0 views."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        # P0 apps direct infra
        _insert_node(
            conn, 1, "ADG::Module::apps_eval/svc.py", "module", "apps", "internal_module", "apps_eval/svc.py"
        )
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 2, "imports", "apps_eval/svc.py", 1, "redis")
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        p0_total = (
            counts["v_p0_apps_direct_infra"]
            + counts["v_p0_provider_bypass"]
            + counts["v_p0_core_imports_apps"]
            + counts["v_p0_write_bypass_uwg"]
            + counts["v_p0_l1_direct_infra"]
            + counts["v_p0_l6_mutation"]
            + counts["v_p0_l0_raw_execution"]
        )
        assert counts["v_infra_violations_summary"] == p0_total

    def test_detects_agentic_core_importing_apps_package(self, tmp_path: Path) -> None:
        """Regression: core importing apps_* must be a first-class P0 view."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L0_routing/gates/app_gate.py",
            "module",
            "L0",
            "repo_module",
            "agentic_core/L0_routing/gates/app_gate.py",
        )
        _insert_node(
            conn,
            2,
            "ADG::Module::apps_demo/runtime/binding.py",
            "module",
            "L_APP",
            "repo_module",
            "apps_demo/runtime/binding.py",
        )
        _insert_edge(conn, 1, 2, "imports", "agentic_core/L0_routing/gates/app_gate.py", 18, "apps_demo")
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        assert counts["v_p0_core_imports_apps"] == 1
        assert counts["v_infra_violations_summary"] == 1

    def test_core_importing_apps_shared_not_flagged(self, tmp_path: Path) -> None:
        """apps_shared is the shared app layer, not an app implementation leak."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/runtime/ok.py",
            "module",
            "L2",
            "repo_module",
            "agentic_core/runtime/ok.py",
        )
        _insert_node(
            conn,
            2,
            "ADG::Module::apps_shared/contracts.py",
            "module",
            "L_SHARED",
            "repo_module",
            "apps_shared/contracts.py",
        )
        _insert_edge(conn, 1, 2, "imports", "agentic_core/runtime/ok.py", 9, "apps_shared")
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        assert counts["v_p0_core_imports_apps"] == 0


class TestP0ProviderBypass:
    """Tests for v_p0_provider_bypass — provider SDK imports outside sanctioned seams."""

    def test_external_provider_identity_kind_detected(self, tmp_path: Path) -> None:
        """Regression: provider nodes tagged external_provider must populate provider_in.

        Bug f7ece2e937: identity_kind filter matched only external_module, silently
        dropping anthropic/openai/google nodes tagged external_provider.
        """
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L3_orchestration/bad_provider.py",
            "module",
            "L3",
            "repo_module",
            "agentic_core/L3_orchestration/bad_provider.py",
        )
        _insert_node(
            conn,
            2,
            "ADG::Symbol::anthropic",
            "external",
            "external",
            "external_provider",
            "anthropic",
        )
        _insert_edge(
            conn,
            1,
            2,
            "imports",
            "agentic_core/L3_orchestration/bad_provider.py",
            7,
            "anthropic",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_provider_bypass"] == 1

    def test_external_module_provider_still_detected(self, tmp_path: Path) -> None:
        """Sanity: external_module provider SDK tagging still flags bypass."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L2_execution/bad_provider.py",
            "module",
            "L2",
            "repo_module",
            "agentic_core/L2_execution/bad_provider.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::openai", "external", "external", "external_module", "openai")
        _insert_edge(conn, 1, 2, "imports", "agentic_core/L2_execution/bad_provider.py", 3, "openai")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_provider_bypass"] == 1


class TestApprovedAdapterEnrollment:
    """Approved adapter paths excluded from zero-caller / not-on-spine violations."""

    def test_augmented_skills_graph_sqlite_adapter_enrolled(self) -> None:
        """C0.3 SQLite materialization is an app-owned canonical adapter."""
        assert "apps_rg/fact_inventory/augmented_skills_graph_sqlite.py" in _APPROVED_ADAPTER_PATHS

    def test_x1d_claude_judge_adapter_enrolled(self) -> None:
        """Regression f7ece2e937/34dcf683a2: apps_lic X1D judge adapter is sanctioned."""
        assert "apps_lic/engines/x1d_claude_judge_adapter.py" in _APPROVED_ADAPTER_PATHS


class TestP0WriteBypassUWG:
    """Tests for v_p0_write_bypass_uwg."""

    def test_augmented_skills_graph_sqlite_adapter_local_lock_is_not_bypass(self, tmp_path: Path) -> None:
        """The canonical adapter may create its ephemeral maintenance lock."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        adapter_path = "apps_rg/fact_inventory/augmented_skills_graph_sqlite.py"
        _insert_node(
            conn,
            1,
            f"ADG::Module::{adapter_path}",
            "module",
            "L_APP",
            "repo_module",
            adapter_path,
        )
        _insert_node(
            conn,
            2,
            "ADG::Symbol::sqlite3",
            "external",
            "external",
            "external_module",
            "sqlite3",
        )
        _insert_edge(conn, 1, 2, "imports", adapter_path, 10, "sqlite3")
        _insert_edge(conn, 1, 1, "writes_to", adapter_path, 42, "os.open")
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)

        assert counts["v_p0_write_bypass_uwg"] == 0

    def test_c03_graph_health_receipt_exclusion_is_exact_and_relation_agnostic(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Only output.write_text at the graph-health receipt site is non-durable."""
        monkeypatch.setattr(infra_wiring, "_REPO_ROOT", tmp_path)
        _write_receipt_source(tmp_path, {100: "output.write_text('receipt')"})
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        receipt_path = "apps_rg/fact_inventory/c03_graph_kpi_health.py"
        counterexample_path = "apps_rg/fact_inventory/other_health_writer.py"
        _insert_node(
            conn,
            1,
            f"ADG::Module::{receipt_path}",
            "module",
            "L_APP",
            "repo_module",
            receipt_path,
        )
        _insert_node(
            conn,
            2,
            f"ADG::Module::{counterexample_path}",
            "module",
            "L_APP",
            "repo_module",
            counterexample_path,
        )
        _insert_node(
            conn,
            3,
            "ADG::Symbol::sqlite3",
            "external",
            "external",
            "external_module",
            "sqlite3",
        )
        _insert_edge(conn, 1, 3, "imports", receipt_path, 10, "sqlite3")
        _insert_edge(conn, 2, 3, "imports", counterexample_path, 10, "sqlite3")
        _insert_edge(conn, 1, 1, "writes_to", receipt_path, 100, "output.write_text")
        _insert_edge(conn, 1, 1, "writes_through", receipt_path, 100, "output.write_text")
        _insert_edge(conn, 1, 1, "writes_to", receipt_path, 101, "path.write_text")
        _insert_edge(conn, 2, 2, "writes_to", counterexample_path, 102, "output.write_text")
        conn.commit()
        conn.close()

        materialize_infra_views(db_path)
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute(
            "SELECT writer_file, write_symbol FROM v_p0_write_bypass_uwg ORDER BY writer_file, write_symbol"
        ).fetchall()
        conn.close()

        assert rows == [
            (receipt_path, "path.write_text"),
            (counterexample_path, "output.write_text"),
        ]

    def test_c03_graph_health_second_receipt_site_fails_closed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A second output.write_text line makes every ambiguous site visible."""
        monkeypatch.setattr(infra_wiring, "_REPO_ROOT", tmp_path)
        _write_receipt_source(
            tmp_path,
            {
                100: "output.write_text('first')",
                101: "output.write_text('second')",
            },
        )
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        receipt_path = "apps_rg/fact_inventory/c03_graph_kpi_health.py"
        _insert_node(
            conn,
            1,
            f"ADG::Module::{receipt_path}",
            "module",
            "L_APP",
            "repo_module",
            receipt_path,
        )
        _insert_node(
            conn,
            2,
            "ADG::Symbol::sqlite3",
            "external",
            "external",
            "external_module",
            "sqlite3",
        )
        _insert_edge(conn, 1, 2, "imports", receipt_path, 10, "sqlite3")
        _insert_edge(conn, 1, 1, "writes_to", receipt_path, 100, "output.write_text")
        _insert_edge(conn, 1, 1, "writes_through", receipt_path, 100, "output.write_text")
        _insert_edge(conn, 1, 1, "writes_to", receipt_path, 101, "output.write_text")
        conn.commit()
        conn.close()

        materialize_infra_views(db_path)
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute(
            "SELECT write_line FROM v_p0_write_bypass_uwg "
            "WHERE writer_file = ? AND write_symbol = ? ORDER BY write_line",
            (receipt_path, "output.write_text"),
        ).fetchall()
        conn.close()

        assert rows == [(100,), (100,), (101,)]

    def test_c03_graph_health_two_same_line_ast_calls_fail_closed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Source AST multiplicity defeats line-only ADG edge deduplication."""
        monkeypatch.setattr(infra_wiring, "_REPO_ROOT", tmp_path)
        _write_receipt_source(
            tmp_path,
            {100: "output.write_text('first'); output.write_text('second')"},
        )
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        receipt_path = "apps_rg/fact_inventory/c03_graph_kpi_health.py"
        _insert_node(
            conn,
            1,
            f"ADG::Module::{receipt_path}",
            "module",
            "L_APP",
            "repo_module",
            receipt_path,
        )
        _insert_node(
            conn,
            2,
            "ADG::Symbol::sqlite3",
            "external",
            "external",
            "external_module",
            "sqlite3",
        )
        _insert_edge(conn, 1, 2, "imports", receipt_path, 10, "sqlite3")
        _insert_edge(conn, 1, 1, "writes_to", receipt_path, 100, "output.write_text")
        _insert_edge(conn, 1, 1, "writes_through", receipt_path, 100, "output.write_text")
        conn.commit()
        conn.close()

        materialize_infra_views(db_path)
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute(
            "SELECT write_line FROM v_p0_write_bypass_uwg "
            "WHERE writer_file = ? AND write_symbol = ? ORDER BY write_line",
            (receipt_path, "output.write_text"),
        ).fetchall()
        conn.close()

        assert rows == [(100,), (100,)]

    def test_c03_graph_health_unresolved_receipt_peer_fails_closed(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A NULL site identity defeats the exemption for every peer edge."""
        monkeypatch.setattr(infra_wiring, "_REPO_ROOT", tmp_path)
        _write_receipt_source(tmp_path, {100: "output.write_text('receipt')"})
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        receipt_path = "apps_rg/fact_inventory/c03_graph_kpi_health.py"
        _insert_node(
            conn,
            1,
            f"ADG::Module::{receipt_path}",
            "module",
            "L_APP",
            "repo_module",
            receipt_path,
        )
        _insert_node(
            conn,
            2,
            "ADG::Symbol::sqlite3",
            "external",
            "external",
            "external_module",
            "sqlite3",
        )
        _insert_edge(conn, 1, 2, "imports", receipt_path, 10, "sqlite3")
        _insert_edge(conn, 1, 1, "writes_to", receipt_path, 100, "output.write_text")
        _insert_edge(conn, 1, 1, "writes_through", receipt_path, 100, "output.write_text")
        _insert_edge(conn, 1, 1, "writes_to", None, None, "output.write_text")
        conn.commit()
        conn.close()

        materialize_infra_views(db_path)
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute(
            "SELECT write_line FROM v_p0_write_bypass_uwg "
            "WHERE writer_file = ? AND write_symbol = ? "
            "ORDER BY write_line IS NULL, write_line",
            (receipt_path, "output.write_text"),
        ).fetchall()
        conn.close()

        assert rows == [(100,), (100,), (None,)]

    def test_detects_direct_write_from_app(self, tmp_path: Path) -> None:
        """L_APP file writing directly should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_eval/engine.py",
            "module",
            "L_APP",
            "repo_module",
            "apps_eval/engine.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 2, "imports", "apps_eval/engine.py", 1, "redis")
        _insert_edge(conn, 1, 1, "writes_to", "apps_eval/engine.py", 100, "open")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_write_bypass_uwg"] == 1

    def test_excludes_uwg_sanctioned_writes(self, tmp_path: Path) -> None:
        """Writes through _wg.write_text should NOT be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_eval/engine.py",
            "module",
            "L_APP",
            "repo_module",
            "apps_eval/engine.py",
        )
        _insert_edge(conn, 1, 1, "writes_to", "apps_eval/engine.py", 100, "_wg.write_text")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_write_bypass_uwg"] == 0

    def test_excludes_tools_layer(self, tmp_path: Path) -> None:
        """Writes from tools/ are exempt."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(conn, 1, "ADG::Module::tools/gen.py", "module", "L_TOOLS", "repo_module", "tools/gen.py")
        _insert_edge(conn, 1, 1, "writes_to", "tools/gen.py", 50, "open")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_write_bypass_uwg"] == 0

    def test_excludes_uwg_file(self, tmp_path: Path) -> None:
        """Writes from UniversalWriteGateway itself are exempt."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L2_execution/enforcement/UniversalWriteGateway.py",
            "module",
            "L_APP",
            "repo_module",
            "agentic_core/L2_execution/enforcement/UniversalWriteGateway.py",
        )
        _insert_edge(
            conn,
            1,
            1,
            "writes_to",
            "agentic_core/L2_execution/enforcement/UniversalWriteGateway.py",
            200,
            "open",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_write_bypass_uwg"] == 0

    def test_writes_through_edge_flagged(self, tmp_path: Path) -> None:
        """writes_through edge (alternate durable write relation) must also be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_eval/engine.py",
            "module",
            "L_APP",
            "repo_module",
            "apps_eval/engine.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 2, "imports", "apps_eval/engine.py", 1, "redis")
        _insert_edge(conn, 1, 1, "writes_through", "apps_eval/engine.py", 105, "conn.execute")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_write_bypass_uwg"] == 1

    def test_chromadb_upsert_outside_l4_adapter_flagged(self, tmp_path: Path) -> None:
        """Regression: raw Chroma import plus collection.upsert is a UWG bypass."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_rg/runtime/c0/raw_fact_vector_writer.py",
            "module",
            "L_APP",
            "repo_module",
            "apps_rg/runtime/c0/raw_fact_vector_writer.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::chromadb", "external", "external", "external_module", "chromadb")
        _insert_edge(conn, 1, 2, "imports", "apps_rg/runtime/c0/raw_fact_vector_writer.py", 10, "chromadb")
        _insert_edge(
            conn,
            1,
            1,
            "writes_through",
            "apps_rg/runtime/c0/raw_fact_vector_writer.py",
            42,
            "collection.upsert",
        )
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        assert counts["v_p0_write_bypass_uwg"] == 1

    def test_chromadb_upsert_inside_l4_adapter_not_write_bypass(self, tmp_path: Path) -> None:
        """The sanctioned L4 Chroma adapter may import and write through Chroma."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        adapter_path = "agentic_core/L4_state/utils/client/chroma_client.py"
        _insert_node(
            conn,
            1,
            f"ADG::Module::{adapter_path}",
            "module",
            "L4",
            "repo_module",
            adapter_path,
        )
        _insert_node(conn, 2, "ADG::Symbol::chromadb", "external", "external", "external_module", "chromadb")
        _insert_edge(conn, 1, 2, "imports", adapter_path, 10, "chromadb")
        _insert_edge(conn, 1, 1, "writes_through", adapter_path, 42, "collection.upsert")
        conn.commit()
        conn.close()

        counts = materialize_infra_views(db_path)
        assert counts["v_p0_write_bypass_uwg"] == 0


class TestP0L1DirectInfra:
    """Tests for v_p0_l1_direct_infra."""

    def test_detects_l1_raw_import(self, tmp_path: Path) -> None:
        """L1 importing sqlite3 should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L1_cognition/engine.py",
            "module",
            "L1",
            "repo_module",
            "agentic_core/L1_cognition/engine.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::sqlite3", "external", "external", "external_module", "sqlite3")
        _insert_edge(conn, 1, 2, "imports", "agentic_core/L1_cognition/engine.py", 5, "sqlite3")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_l1_direct_infra"] == 1

    def test_l2_import_not_flagged(self, tmp_path: Path) -> None:
        """L2 importing raw infra should NOT be flagged here."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L2/engine.py",
            "module",
            "L2",
            "repo_module",
            "agentic_core/L2/engine.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 2, "imports", "agentic_core/L2/engine.py", 5, "redis")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_l1_direct_infra"] == 0


class TestP0L6Mutation:
    """Tests for v_p0_l6_mutation."""

    def test_detects_l6_write(self, tmp_path: Path) -> None:
        """L6 file doing writes_to should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L6_observability/store.py",
            "module",
            "L6",
            "repo_module",
            "agentic_core/L6_observability/store.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 2, "imports", "agentic_core/L6_observability/store.py", 1, "redis")
        _insert_edge(conn, 1, 1, "writes_to", "agentic_core/L6_observability/store.py", 42, "f.write")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_l6_mutation"] == 1

    def test_excludes_telemetry_store(self, tmp_path: Path) -> None:
        """Telemetry stores in L6 are exempt."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L6_observability/telemetry_store.py",
            "module",
            "L6",
            "repo_module",
            "agentic_core/L6_observability/telemetry_store.py",
        )
        _insert_edge(
            conn, 1, 1, "writes_to", "agentic_core/L6_observability/telemetry_store.py", 42, "f.write"
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_l6_mutation"] == 0

    def test_excludes_uwg_sanctioned(self, tmp_path: Path) -> None:
        """L6 writes through _wg.write_text are exempt."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L6_observability/report.py",
            "module",
            "L6",
            "repo_module",
            "agentic_core/L6_observability/report.py",
        )
        _insert_edge(conn, 1, 1, "writes_to", "agentic_core/L6_observability/report.py", 42, "_wg.write_text")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_l6_mutation"] == 0


class TestP0L0RawExecution:
    """Tests for v_p0_l0_raw_execution."""

    def test_detects_l0_raw_infra(self, tmp_path: Path) -> None:
        """L0 importing raw infra should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L0_routing/bad.py",
            "module",
            "L0",
            "repo_module",
            "agentic_core/L0_routing/bad.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::boto3", "external", "external", "external_module", "boto3")
        _insert_edge(conn, 1, 2, "imports", "agentic_core/L0_routing/bad.py", 3, "boto3")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_l0_raw_execution"] == 1

    def test_l0_non_infra_not_flagged(self, tmp_path: Path) -> None:
        """L0 importing non-infra external module is fine."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L0_routing/ok.py",
            "module",
            "L0",
            "repo_module",
            "agentic_core/L0_routing/ok.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::json", "external", "external", "external_module", "json")
        _insert_edge(conn, 1, 2, "imports", "agentic_core/L0_routing/ok.py", 1, "json")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p0_l0_raw_execution"] == 0


class TestP1NotOnSpine:
    """Tests for v_p1_not_on_spine."""

    def test_adapter_with_no_spine_caller(self, tmp_path: Path) -> None:
        """Adapter with zero L0-L6 callers should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        adapter_path = _APPROVED_ADAPTER_PATHS[0]
        _insert_node(conn, 1, f"ADG::Module::{adapter_path}", "module", "L4", "repo_module", adapter_path)
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_not_on_spine"] == 1

    def test_adapter_with_spine_caller_compliant(self, tmp_path: Path) -> None:
        """Adapter imported by an L3 module is on the spine."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        adapter_path = _APPROVED_ADAPTER_PATHS[0]
        _insert_node(conn, 1, f"ADG::Module::{adapter_path}", "module", "L4", "repo_module", adapter_path)
        _insert_node(
            conn,
            2,
            "ADG::Module::agentic_core/L3/caller.py",
            "module",
            "L3",
            "repo_module",
            "agentic_core/L3/caller.py",
        )
        _insert_edge(conn, 2, 1, "imports", "agentic_core/L3/caller.py", 5)
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_not_on_spine"] == 0

    def test_process_boundary_adapter_not_flagged(self, tmp_path: Path) -> None:
        """Process-boundary adapters must be exempt from v_p1_not_on_spine even with zero callers."""
        pb_path = _PROCESS_BOUNDARY_ADAPTERS[0]  # infrastructure/sdks_mcps/__init__.py
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(conn, 1, f"ADG::Module::{pb_path}", "module", "L_INFRA", "repo_module", pb_path)
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_not_on_spine"] == 0, (
            f"Process-boundary adapter {pb_path!r} must not be flagged by v_p1_not_on_spine"
        )


class TestP1AdHocImports:
    """Tests for v_p1_ad_hoc_imports."""

    def test_dead_infra_import_flagged(self, tmp_path: Path) -> None:
        """Dead import of infra module should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L3/orchestrator.py",
            "module",
            "L3",
            "repo_module",
            "agentic_core/L3/orchestrator.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(
            conn, 1, 2, "imports", "agentic_core/L3/orchestrator.py", 10, "redis", edge_kind="dead_import"
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_ad_hoc_imports"] == 1

    def test_live_infra_import_not_flagged(self, tmp_path: Path) -> None:
        """Active (non-dead) import of infra should NOT be flagged by ad-hoc view."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L3/orchestrator.py",
            "module",
            "L3",
            "repo_module",
            "agentic_core/L3/orchestrator.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(
            conn, 1, 2, "imports", "agentic_core/L3/orchestrator.py", 10, "redis", edge_kind="from_import"
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_ad_hoc_imports"] == 0

    def test_dead_import_in_tests_excluded(self, tmp_path: Path) -> None:
        """Dead infra imports from tests/ are excluded."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::tests/unit/test_svc.py",
            "module",
            "L_TEST",
            "repo_module",
            "tests/unit/test_svc.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::sqlite3", "external", "external", "external_module", "sqlite3")
        _insert_edge(conn, 1, 2, "imports", "tests/unit/test_svc.py", 5, "sqlite3", edge_kind="dead_import")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_ad_hoc_imports"] == 0


class TestP1MisLayeredInfra:
    """Tests for v_p1_mis_layered_infra."""

    def test_redis_in_wrong_layer_flagged(self, tmp_path: Path) -> None:
        """Redis adapter in wrong layer (L6) should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/cache/redis_cache_client.py",
            "module",
            "L6",
            "repo_module",
            "agentic_core/cache/redis_cache_client.py",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_mis_layered_infra"] == 1

    def test_redis_in_l_shared_compliant(self, tmp_path: Path) -> None:
        """Redis adapter in L_SHARED is compliant (second allowed layer per SQL)."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/cache/redis_cache_client.py",
            "module",
            "L_SHARED",
            "repo_module",
            "agentic_core/cache/redis_cache_client.py",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_mis_layered_infra"] == 0

    def test_redis_in_l2_compliant(self, tmp_path: Path) -> None:
        """Redis adapter in L2 is compliant."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/cache/redis_cache_client.py",
            "module",
            "L2",
            "repo_module",
            "agentic_core/cache/redis_cache_client.py",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_mis_layered_infra"] == 0

    def test_chroma_in_l4_compliant(self, tmp_path: Path) -> None:
        """ChromaDB adapter in L4 is compliant."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L4_state/utils/client/chroma_client.py",
            "module",
            "L4",
            "repo_module",
            "agentic_core/L4_state/utils/client/chroma_client.py",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_mis_layered_infra"] == 0


class TestP1RawHttpOutsideSeam:
    """Tests for v_p1_raw_http_outside_seam."""

    def test_httpx_in_non_exempt_layer_flagged(self, tmp_path: Path) -> None:
        """Non-exempt module importing httpx should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L2_execution/services/caller.py",
            "module",
            "L2",
            "repo_module",
            "agentic_core/L2_execution/services/caller.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::httpx", "external", "external", "external_module", "httpx")
        _insert_edge(conn, 1, 2, "imports", "agentic_core/L2_execution/services/caller.py", 3, "httpx")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_raw_http_outside_seam"] == 1

    def test_httpx_from_tools_exempt(self, tmp_path: Path) -> None:
        """tools/ importing httpx is exempt from the seam check."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::tools/mcp/http_client.py",
            "module",
            "L_TOOLS",
            "repo_module",
            "tools/mcp/http_client.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::httpx", "external", "external", "external_module", "httpx")
        _insert_edge(conn, 1, 2, "imports", "tools/mcp/http_client.py", 1, "httpx")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_raw_http_outside_seam"] == 0

    def test_httpx_from_apps_shared_exempt(self, tmp_path: Path) -> None:
        """apps_shared/ importing httpx is exempt from the seam check."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::apps_shared/utils/http_util.py",
            "module",
            "L_SHARED",
            "repo_module",
            "apps_shared/utils/http_util.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::httpx", "external", "external", "external_module", "httpx")
        _insert_edge(conn, 1, 2, "imports", "apps_shared/utils/http_util.py", 1, "httpx")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_raw_http_outside_seam"] == 0

    def test_api_gateway_integration_exempt(self, tmp_path: Path) -> None:
        """api_gateway_integration path pattern is exempt."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/L0_routing/api_gateway_integration.py",
            "module",
            "L0",
            "repo_module",
            "agentic_core/L0_routing/api_gateway_integration.py",
        )
        _insert_node(conn, 2, "ADG::Symbol::httpx", "external", "external", "external_module", "httpx")
        _insert_edge(
            conn,
            1,
            2,
            "imports",
            "agentic_core/L0_routing/api_gateway_integration.py",
            5,
            "httpx",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p1_raw_http_outside_seam"] == 0


class TestP2DuplicatedAdapters:
    """Tests for v_p2_duplicated_adapters."""

    def test_single_adapter_compliant(self, tmp_path: Path) -> None:
        """One adapter per infra is compliant."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        adapter_path = _APPROVED_ADAPTER_PATHS[0]
        _insert_node(conn, 1, f"ADG::Module::{adapter_path}", "module", "L4", "repo_module", adapter_path)
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 2, "imports", adapter_path, 5, "redis")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p2_duplicated_adapters"] == 0

    def test_two_adapters_for_same_infra_flagged(self, tmp_path: Path) -> None:
        """Two adapters importing the same infra should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        ap1 = _APPROVED_ADAPTER_PATHS[0]
        ap2 = (
            _APPROVED_ADAPTER_PATHS[1]
            if len(_APPROVED_ADAPTER_PATHS) > 1
            else "agentic_core/cache/redis_cache_client.py"
        )
        _insert_node(conn, 1, f"ADG::Module::{ap1}", "module", "L4", "repo_module", ap1)
        _insert_node(conn, 2, f"ADG::Module::{ap2}", "module", "L2", "repo_module", ap2)
        _insert_node(conn, 3, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 3, "imports", ap1, 5, "redis")
        _insert_edge(conn, 2, 3, "imports", ap2, 5, "redis")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p2_duplicated_adapters"] == 1


class TestP2DormantAmbiguous:
    """Tests for v_p2_dormant_ambiguous."""

    def test_dormant_adapter_no_imports_in_or_out(self, tmp_path: Path) -> None:
        """Adapter with zero incoming AND zero outgoing infra imports = dormant."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        adapter_path = _APPROVED_ADAPTER_PATHS[0]
        _insert_node(conn, 1, f"ADG::Module::{adapter_path}", "module", "L4", "repo_module", adapter_path)
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p2_dormant_ambiguous"] == 1

    def test_adapter_with_outgoing_imports_not_dormant(self, tmp_path: Path) -> None:
        """Adapter that imports infra is not dormant."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        adapter_path = _APPROVED_ADAPTER_PATHS[0]
        _insert_node(conn, 1, f"ADG::Module::{adapter_path}", "module", "L4", "repo_module", adapter_path)
        _insert_node(conn, 2, "ADG::Symbol::redis", "external", "external", "external_module", "redis")
        _insert_edge(conn, 1, 2, "imports", adapter_path, 5, "redis")
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p2_dormant_ambiguous"] == 0


class TestP3IsolatedExperimental:
    """Tests for v_p3_isolated_experimental."""

    def test_sandbox_with_zero_callers_flagged(self, tmp_path: Path) -> None:
        """Sandbox file with zero incoming imports should be flagged."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/sandbox_test.py",
            "module",
            "L2",
            "repo_module",
            "agentic_core/sandbox_test.py",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p3_isolated_experimental"] == 1

    def test_sandbox_with_callers_not_flagged(self, tmp_path: Path) -> None:
        """Sandbox file with incoming imports is not isolated."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::agentic_core/sandbox_test.py",
            "module",
            "L2",
            "repo_module",
            "agentic_core/sandbox_test.py",
        )
        _insert_node(
            conn,
            2,
            "ADG::Module::agentic_core/caller.py",
            "module",
            "L3",
            "repo_module",
            "agentic_core/caller.py",
        )
        _insert_edge(conn, 2, 1, "imports", "agentic_core/caller.py", 5)
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p3_isolated_experimental"] == 0

    def test_test_sandbox_excluded(self, tmp_path: Path) -> None:
        """Files in tests/ are excluded from experimental detection."""
        db_path = _create_test_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        _insert_node(
            conn,
            1,
            "ADG::Module::tests/sandbox_check.py",
            "module",
            "L_TEST",
            "repo_module",
            "tests/sandbox_check.py",
        )
        conn.commit()
        conn.close()
        counts = materialize_infra_views(db_path)
        assert counts["v_p3_isolated_experimental"] == 0
