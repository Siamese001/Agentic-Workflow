"""Tests for ADG materialized view fixes (Prompt 3).

Validates:
1. mv_hotspot_centrality computes nonzero fan_in
2. mv_dependency_cone_risk computes nonzero cone_risk_score
3. SC-1 and SC-5 checks are enabled and executable
"""

import sqlite3
from pathlib import Path

import pytest

from tools.generate.materialized_views.phase_a_path_authority import materialize_phase_a
from tools.generate.materialized_views.phase_b_capability_tool_task import materialize_phase_b
from tools.generate.validation.gates import _check_structural_conformance, _DEFAULT_SC_AP_CONFIG


def get_latest_adg_sqlite() -> Path:
    """Find the latest ADG SQLite snapshot."""
    adg_dir = Path('artifacts/adg')
    sqlite_files = sorted(adg_dir.glob('adg_indexed_*.sqlite'))
    if not sqlite_files:
        pytest.skip("No ADG SQLite found")
    return sqlite_files[-1]


class TestHotspotCentralityFix:
    """Validate mv_hotspot_centrality fix produces nonzero fan_in."""

    def test_fan_in_not_all_zero(self):
        """After fix, fan_in should be nonzero for modules with inbound edges."""
        sqlite_path = get_latest_adg_sqlite()
        materialize_phase_a(sqlite_path)

        conn = sqlite3.connect(str(sqlite_path))
        cur = conn.cursor()
        cur.execute('SELECT MAX(fan_in), AVG(fan_in) FROM mv_hotspot_centrality')
        max_fi, avg_fi = cur.fetchone()
        conn.close()

        assert max_fi > 0, f"Expected max fan_in > 0, got {max_fi}"
        assert avg_fi > 0, f"Expected avg fan_in > 0, got {avg_fi}"

    def test_top_hotspot_has_high_fan_in(self):
        """Top hotspot should have substantial fan_in (lifecycle_trace_contracts has ~127K)."""
        sqlite_path = get_latest_adg_sqlite()
        materialize_phase_a(sqlite_path)

        conn = sqlite3.connect(str(sqlite_path))
        cur = conn.cursor()
        cur.execute('SELECT fan_in FROM mv_hotspot_centrality ORDER BY fan_in DESC LIMIT 1')
        top_fi = cur.fetchone()[0]
        conn.close()

        assert top_fi >= 1000, f"Expected top fan_in >= 1000, got {top_fi}"


class TestDependencyConeRiskFix:
    """Validate mv_dependency_cone_risk fix produces nonzero cone_risk_score."""

    def test_cone_risk_not_all_zero(self):
        """After fix, cone_risk_score should be nonzero for high-fan-in modules."""
        sqlite_path = get_latest_adg_sqlite()
        materialize_phase_b(sqlite_path)

        conn = sqlite3.connect(str(sqlite_path))
        cur = conn.cursor()
        cur.execute('SELECT MAX(cone_risk_score), AVG(cone_risk_score) FROM mv_dependency_cone_risk')
        max_score, avg_score = cur.fetchone()
        conn.close()

        assert max_score > 0, f"Expected max cone_risk_score > 0, got {max_score}"
        assert avg_score > 0, f"Expected avg cone_risk_score > 0, got {avg_score}"

    def test_direct_fan_in_populated(self):
        """Direct fan_in should be populated (hop-2 may still be 0 due to data patterns)."""
        sqlite_path = get_latest_adg_sqlite()
        materialize_phase_b(sqlite_path)

        conn = sqlite3.connect(str(sqlite_path))
        cur = conn.cursor()
        cur.execute('SELECT MAX(direct_fan_in) FROM mv_dependency_cone_risk')
        max_direct = cur.fetchone()[0]
        conn.close()

        assert max_direct > 0, f"Expected max direct_fan_in > 0, got {max_direct}"


class TestSCChecksEnabled:
    """Validate SC-1 and SC-5 are enabled in config."""

    def test_sc1_enabled_in_config(self):
        """SC-1 should be enabled=True in default config."""
        config = _DEFAULT_SC_AP_CONFIG
        assert config['SC-1']['enabled'] is True, "SC-1 should be enabled"
        assert config['SC-1']['audit_mode'] is True, "SC-1 should be in audit mode"

    def test_sc5_enabled_in_config(self):
        """SC-5 should be enabled=True in default config."""
        config = _DEFAULT_SC_AP_CONFIG
        assert config['SC-5']['enabled'] is True, "SC-5 should be enabled"
        assert config['SC-5']['audit_mode'] is True, "SC-5 should be in audit mode"

    def test_sc1_produces_violations(self):
        """SC-1 check should find gravity import violations (L6->L2, L2->L0, etc.)."""
        sqlite_path = get_latest_adg_sqlite()
        results = _check_structural_conformance(sqlite_path)

        # SC-1 should be in results
        assert 'SC-1' in results, "SC-1 should have been executed"

        # Should find violations (there are known L2->L0, L6->L2 issues)
        sc1_results = results.get('SC-1', [])
        assert len(sc1_results) > 0, "SC-1 should find violations in current codebase"

    def test_sc5_executes(self):
        """SC-5 check should execute (may find 0 violations if spine is complete)."""
        sqlite_path = get_latest_adg_sqlite()
        results = _check_structural_conformance(sqlite_path)

        # SC-5 should be in results
        assert 'SC-5' in results, "SC-5 should have been executed"

        # Result should be a list (empty is acceptable if no spine gaps)
        assert isinstance(results['SC-5'], list), "SC-5 should return list"
