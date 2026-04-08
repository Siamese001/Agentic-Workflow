"""Integration tests: SC/AP checks against the LIVE ADG SQLite.

These tests verify that the current codebase violations match expected audit
counts within a configurable delta threshold.  They run against whichever
``adg_indexed_*.sqlite`` is present in ``artifacts/adg/``.

Skip gracefully if no SQLite artifact exists (CI-only or fresh clone).
"""

from __future__ import annotations

import glob
import json
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = ROOT / "artifacts" / "adg"
_SQLITE_GLOB = str(ADG_DIR / "adg_indexed_*.sqlite")


def _find_latest_sqlite() -> Path | None:
    """Return the latest ADG SQLite file or None."""
    candidates = sorted(glob.glob(_SQLITE_GLOB))
    return Path(candidates[-1]) if candidates else None


LIVE_SQLITE = _find_latest_sqlite()

_SKIP_REASON = "No live ADG SQLite found — skip integration tests"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def live_conn():
    """Yield a read-only connection to the live ADG SQLite."""
    if LIVE_SQLITE is None:
        pytest.skip(_SKIP_REASON)
    conn = sqlite3.connect(f"file:{LIVE_SQLITE}?mode=ro", uri=True)
    yield conn
    conn.close()


@pytest.fixture
def live_db():
    """Return live SQLite path."""
    if LIVE_SQLITE is None:
        pytest.skip(_SKIP_REASON)
    return LIVE_SQLITE


# ---------------------------------------------------------------------------
# Schema presence tests
# ---------------------------------------------------------------------------


class TestLiveSchemaPresence:
    """Verify the live ADG SQLite has expected tables/columns."""

    def test_nodes_table_exists(self, live_conn):
        """nodes table exists with expected columns."""
        rows = live_conn.execute("PRAGMA table_info(nodes)").fetchall()
        col_names = {r[1] for r in rows}
        assert "id" in col_names
        assert "layer" in col_names
        assert "entity_type" in col_names

    def test_edges_table_exists(self, live_conn):
        """edges table exists with expected columns."""
        rows = live_conn.execute("PRAGMA table_info(edges)").fetchall()
        col_names = {r[1] for r in rows}
        assert "src_id" in col_names
        assert "dst_id" in col_names
        assert "relation_type" in col_names

    def test_violations_table_exists(self, live_conn):
        """violations table exists with core columns (violation_class may be added by migration)."""
        rows = live_conn.execute("PRAGMA table_info(violations)").fetchall()
        col_names = {r[1] for r in rows}
        assert "severity" in col_names
        # violation_class is added by _ensure_violation_class_column migration
        # It may not exist yet on older DBs — gate functions handle this


# ---------------------------------------------------------------------------
# SC/AP query smoke tests — run each check against live graph
# ---------------------------------------------------------------------------


class TestLiveSCQueries:
    """Run all SC query functions against live graph — must not crash."""

    def test_sc_queries_return_lists(self, live_conn):
        """All SC query functions return list[dict] without error."""
        from tools.generate.validation.gates import (
            _query_sc1_gravity,
            _query_sc2_lifecycle,
            _query_sc3_uwg_write,
            _query_sc4_choke_point,
            _query_sc5_spine,
            _query_sc6_role_purity,
            _query_sc7_grounding,
            _query_sc8_trace_coverage,
        )

        for fn in [
            _query_sc1_gravity,
            _query_sc2_lifecycle,
            _query_sc3_uwg_write,
            _query_sc4_choke_point,
            _query_sc5_spine,
            _query_sc6_role_purity,
            _query_sc7_grounding,
            _query_sc8_trace_coverage,
        ]:
            result = fn(live_conn)
            assert isinstance(result, list), f"{fn.__name__} must return list"


class TestLiveAPQueries:
    """Run all AP query functions against live graph — must not crash."""

    def test_ap_queries_return_lists(self, live_conn):
        """All AP query functions return list[dict] without error."""
        from tools.generate.validation.gates import (
            _query_ap1_text_to_action,
            _query_ap2_phase_bypass,
            _query_ap3_provider_bypass,
            _query_ap4_direct_write,
            _query_ap5_tool_overlap,
            _query_ap6_manager_sprawl,
            _query_ap7_dup_specialization,
            _query_ap8_missing_trace,
            _query_ap9_infra_spread,
            _query_ap10_mutation_confusion,
            _query_ap11_work_contracts,
            _query_ap12_prompt_scatter,
            _query_ap13_retry_no_exit,
            _query_ap14_retrieval_no_evidence,
            _query_ap15_agent_tool_ratio,
            _query_ap16_dormant_infra,
            _query_ap17_semantic_precision,
        )

        for fn in [
            _query_ap1_text_to_action,
            _query_ap2_phase_bypass,
            _query_ap3_provider_bypass,
            _query_ap4_direct_write,
            _query_ap5_tool_overlap,
            _query_ap6_manager_sprawl,
            _query_ap7_dup_specialization,
            _query_ap8_missing_trace,
            _query_ap9_infra_spread,
            _query_ap10_mutation_confusion,
            _query_ap11_work_contracts,
            _query_ap12_prompt_scatter,
            _query_ap13_retry_no_exit,
            _query_ap14_retrieval_no_evidence,
            _query_ap15_agent_tool_ratio,
            _query_ap16_dormant_infra,
            _query_ap17_semantic_precision,
        ]:
            result = fn(live_conn)
            assert isinstance(result, list), f"{fn.__name__} must return list"


# ---------------------------------------------------------------------------
# Gate integration — run full gates in audit mode on live DB
# ---------------------------------------------------------------------------


class TestLiveGateExecution:
    """Run _check_structural_conformance and _check_agentic_antipatterns
    against the live DB with all checks enabled in audit mode."""

    def _audit_config(self, tmp_path):
        """Create config with all checks enabled in audit mode."""
        from tools.generate.validation.gates import _DEFAULT_SC_AP_CONFIG

        import copy

        config = copy.deepcopy(_DEFAULT_SC_AP_CONFIG)
        for v in config.values():
            v["enabled"] = True
            v["audit_mode"] = True
        cfg_path = tmp_path / "sc_ap_config_integration.json"
        cfg_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        return cfg_path

    def test_sc_gate_audit_mode(self, live_db, tmp_path):
        """SC gate runs in audit mode without crashing or exiting."""
        from tools.generate.validation.gates import _check_structural_conformance

        cfg = self._audit_config(tmp_path)
        result = _check_structural_conformance(sqlite_path=live_db, config_path=cfg)
        assert isinstance(result, dict)
        # All check IDs present
        for cid in ["SC-1", "SC-2", "SC-3", "SC-4", "SC-5", "SC-6", "SC-7", "SC-8"]:
            assert cid in result, f"{cid} missing from SC gate result"

    def test_ap_gate_audit_mode(self, live_db, tmp_path):
        """AP gate runs in audit mode without crashing or exiting."""
        from tools.generate.validation.gates import _check_agentic_antipatterns

        cfg = self._audit_config(tmp_path)
        result = _check_agentic_antipatterns(sqlite_path=live_db, config_path=cfg)
        assert isinstance(result, dict)
        for i in range(1, 18):
            cid = f"AP-{i}"
            assert cid in result, f"{cid} missing from AP gate result"


# ---------------------------------------------------------------------------
# Snapshot test — violation counts within delta threshold
# ---------------------------------------------------------------------------

_SNAPSHOT_FILE = ADG_DIR / "sc_ap_snapshot_counts.json"
_MAX_DELTA = 50  # Allow up to 50 new violations before alerting


class TestViolationSnapshot:
    """Compare live violation counts against snapshot baseline."""

    def test_snapshot_delta_within_threshold(self, live_db, tmp_path):
        """If a snapshot exists, verify that live counts don't spike."""
        if not _SNAPSHOT_FILE.exists():
            pytest.skip("No snapshot baseline — run with --update-snapshot first")

        baseline = json.loads(_SNAPSHOT_FILE.read_text(encoding="utf-8"))
        cfg = TestLiveGateExecution._audit_config(TestLiveGateExecution(), tmp_path)

        from tools.generate.validation.gates import (
            _check_structural_conformance,
            _check_agentic_antipatterns,
        )

        sc_result = _check_structural_conformance(sqlite_path=live_db, config_path=cfg)
        ap_result = _check_agentic_antipatterns(sqlite_path=live_db, config_path=cfg)

        for cid, violations in {**sc_result, **ap_result}.items():
            live_count = len(violations)
            baseline_count = baseline.get(cid, 0)
            delta = live_count - baseline_count
            assert delta <= _MAX_DELTA, (
                f"{cid}: live={live_count}, baseline={baseline_count}, delta={delta} > {_MAX_DELTA}"
            )


# ---------------------------------------------------------------------------
# Burndown by_class integration
# ---------------------------------------------------------------------------


class TestLiveBurndownByClass:
    """Verify burndown JSON reflects SC/AP violations from live DB."""

    def test_burndown_file_has_by_class(self):
        """adg_burndown_table.json has by_class with SC/AP entries."""
        burndown_path = ADG_DIR / "adg_burndown_table.json"
        if not burndown_path.exists():
            pytest.skip("No burndown artifact")

        data = json.loads(burndown_path.read_text(encoding="utf-8"))
        assert "by_class" in data
        assert "structural_conformance" in data["by_class"]
        assert "agentic_antipattern" in data["by_class"]
        for cls_data in data["by_class"].values():
            for band in ["P0", "P1", "P2", "P3"]:
                assert band in cls_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
