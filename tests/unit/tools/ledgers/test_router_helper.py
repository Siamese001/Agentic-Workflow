"""Tests for tools.ledgers.router_helper.RouterClosedLoopHelper.

Plan: .windsurf/plans/closed-loop-router-fleet-rollout-d8f2a3.md (W1.5)

Covers:
  - cell_fingerprint determinism + key-order independence
  - brier_component math
  - score_band_for tp/fp/tn/fn
  - record_decision: marker emission, ledger row shape, fail-soft
  - bind_outcome: row update, Brier computation, no-op when handle empty
  - get_posterior: prior return when ledger empty, used=True at floor
  - LEDGER_WRITER_BYPASS env honored
  - Multiple routers writing to same ledger don't collide
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from pathlib import Path

import pytest

from tools.ledgers.router_helper import (
    DEFAULT_POSTERIOR_N_FLOOR,
    PosteriorVerdict,
    RouterClosedLoopHelper,
    RouterDecisionHandle,
    brier_component,
    cell_fingerprint,
    score_band_for,
)

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def temp_ledger(tmp_path, monkeypatch):
    """Redirect a router_l1_c0 ledger to tmp_path. Returns the DB Path."""
    from tools.ledgers import schema_registry, writer as writer_mod

    monkeypatch.setattr(schema_registry, "LEDGERS_DIR", tmp_path)
    monkeypatch.setattr(writer_mod, "_WRITERS", {})

    repo_root = Path(__file__).resolve().parents[4]
    base_sql = (repo_root / ".windsurf" / "schemas" / "ledger_base.schema.sql").read_text()
    per_sql = (repo_root / ".windsurf" / "schemas" / "router_l1_c0_ledger.schema.sql").read_text()
    db_path = tmp_path / "router_l1_c0.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(base_sql)
    conn.executescript(per_sql)
    conn.commit()
    conn.close()
    return db_path


def _read_rows(db_path: Path) -> list[dict]:
    conn = sqlite3.connect(str(db_path))
    cur = conn.execute(
        "SELECT event_id, event_kind, status, score_band, score_numeric, "
        "latency_ms, prediction_json, outcome_json, metadata_json "
        "FROM events ORDER BY ts_utc"
    )
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, row)) for row in cur]
    conn.close()
    return rows


# =========================================================================== #
# Pure helpers
# =========================================================================== #
class TestPureHelpers:
    def test_cell_fingerprint_is_deterministic(self):
        a = cell_fingerprint({"intent": "CODE_CONCEPT", "slo": "fast"})
        b = cell_fingerprint({"intent": "CODE_CONCEPT", "slo": "fast"})
        assert a == b
        assert len(a) == 12
        assert all(ch in "0123456789abcdef" for ch in a)

    def test_cell_fingerprint_key_order_independent(self):
        a = cell_fingerprint({"intent": "X", "slo": "fast"})
        b = cell_fingerprint({"slo": "fast", "intent": "X"})
        assert a == b

    def test_cell_fingerprint_value_sensitive(self):
        a = cell_fingerprint({"intent": "X", "slo": "fast"})
        b = cell_fingerprint({"intent": "X", "slo": "slow"})
        assert a != b

    def test_brier_component_perfect(self):
        assert brier_component(1.0, True) == pytest.approx(0.0)
        assert brier_component(0.0, False) == pytest.approx(0.0)

    def test_brier_component_calibrated_prior(self):
        assert brier_component(0.5, True) == pytest.approx(0.25)
        assert brier_component(0.5, False) == pytest.approx(0.25)

    def test_brier_component_clamps(self):
        assert brier_component(2.0, True) == pytest.approx(0.0)
        assert brier_component(-1.0, False) == pytest.approx(0.0)

    def test_score_band_tp_fp_tn_fn(self):
        assert score_band_for(0.9, True) == "tp"
        assert score_band_for(0.9, False) == "fp"
        assert score_band_for(0.2, True) == "fn"
        assert score_band_for(0.2, False) == "tn"


# =========================================================================== #
# RouterClosedLoopHelper.record_decision
# =========================================================================== #
class TestRecordDecision:
    def _helper(self):
        return RouterClosedLoopHelper(
            layer="L1",
            router="c0",
            ledger_name="router_l1_c0",
            repo_area="agentic_core/L1_cognition/reasoning/retrieval_router.py",
        )

    def test_record_decision_returns_handle_with_decision_id(self, temp_ledger):
        h = self._helper().record_decision(
            selected="tier_a",
            cell={"intent": "CODE_CONCEPT", "slo": "fast"},
            predicted_p_success=0.7,
        )
        assert h.decision_id != ""
        assert len(h.decision_id) == 32  # uuid4 hex
        assert h.ledger_event_id != ""
        assert h.fingerprint == cell_fingerprint({"intent": "CODE_CONCEPT", "slo": "fast"})
        assert h.predicted_p_success == pytest.approx(0.7)
        assert h.selected == "tier_a"

    def test_record_decision_emits_marker(self, temp_ledger, caplog):
        caplog.set_level(logging.INFO, logger="tools.ledgers.router_helper")
        h = self._helper().record_decision(
            selected="tier_b",
            cell={"intent": "PROSE_FACTUAL", "slo": "interactive"},
            predicted_p_success=0.85,
            eu_score=0.42,
        )
        markers = [r.getMessage() for r in caplog.records if r.getMessage().startswith("ROUTER_DECISION:")]
        assert len(markers) == 1
        line = markers[0]
        assert "layer=L1" in line
        assert "router=c0" in line
        assert f"decision_id={h.decision_id}" in line
        assert "selected=tier_b" in line
        assert "eu_score=0.4200" in line
        assert "confidence=0.8500" in line

    def test_record_decision_writes_ledger_row(self, temp_ledger):
        helper = self._helper()
        h = helper.record_decision(
            selected="tier_c",
            cell={"intent": "TRACE_LOOKUP", "slo": "background"},
            predicted_p_success=0.9,
            eu_score=0.5,
            prediction_extras={"plan": {"reflective": True}},
            metadata_extras={"task_id": "ut-001"},
        )
        rows = _read_rows(temp_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["event_kind"] == "route_decision"
        assert row["status"] == "predicted"
        pred = json.loads(row["prediction_json"])
        assert pred["decision_id"] == h.decision_id
        assert pred["selected"] == "tier_c"
        assert pred["fingerprint"] == h.fingerprint
        assert pred["predicted_p_success"] == pytest.approx(0.9)
        assert pred["eu_score"] == pytest.approx(0.5)
        assert pred["plan"] == {"reflective": True}
        assert pred["cell"] == {"intent": "TRACE_LOOKUP", "slo": "background"}
        meta = json.loads(row["metadata_json"])
        assert meta["router"] == "L1/c0"
        assert meta["constitutional_rule"] == "§29"
        assert meta["task_id"] == "ut-001"

    def test_record_decision_clamps_predicted_p_to_unit_interval(self, temp_ledger):
        h_high = self._helper().record_decision(
            selected="x",
            cell={"k": "v"},
            predicted_p_success=2.5,
        )
        h_low = self._helper().record_decision(
            selected="y",
            cell={"k": "v"},
            predicted_p_success=-1.0,
        )
        assert h_high.predicted_p_success == 1.0
        assert h_low.predicted_p_success == 0.0

    def test_record_decision_bypass_env_honored(self, temp_ledger, monkeypatch):
        monkeypatch.setenv("LEDGER_WRITER_BYPASS", "router_l1_c0")
        h = self._helper().record_decision(
            selected="x",
            cell={"k": "v"},
            predicted_p_success=0.5,
        )
        # Marker still emitted (audit trail) but ledger write suppressed
        assert h.decision_id != ""
        assert h.ledger_event_id == ""
        assert _read_rows(temp_ledger) == []

    def test_record_decision_explicit_decision_id(self, temp_ledger):
        custom_id = "abc123" + "0" * 26  # 32 hex chars
        h = self._helper().record_decision(
            selected="x",
            cell={"k": "v"},
            predicted_p_success=0.5,
            decision_id=custom_id,
        )
        assert h.decision_id == custom_id

    def test_record_decision_explicit_trace_id(self, temp_ledger, caplog):
        caplog.set_level(logging.INFO, logger="tools.ledgers.router_helper")
        self._helper().record_decision(
            selected="x",
            cell={"k": "v"},
            predicted_p_success=0.5,
            trace_id="trace-42",
            route_id="custom-route",
        )
        markers = [r.getMessage() for r in caplog.records if r.getMessage().startswith("ROUTER_DECISION:")]
        assert any("trace_id=trace-42" in m for m in markers)
        assert any("route_id=custom-route" in m for m in markers)


# =========================================================================== #
# RouterClosedLoopHelper.bind_outcome
# =========================================================================== #
class TestBindOutcome:
    def _helper(self):
        return RouterClosedLoopHelper(
            layer="L1",
            router="c0",
            ledger_name="router_l1_c0",
            repo_area="x",
        )

    def test_bind_outcome_marks_status_bound(self, temp_ledger):
        helper = self._helper()
        h = helper.record_decision(
            selected="tier_a",
            cell={"k": "v"},
            predicted_p_success=0.95,
        )
        helper.bind_outcome(h, success=True, latency_ms=42)
        rows = _read_rows(temp_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["status"] == "bound"
        assert row["score_band"] == "tp"
        # Brier = (1.0 - 0.95)^2 = 0.0025
        assert row["score_numeric"] == pytest.approx((1.0 - 0.95) ** 2, abs=1e-6)
        assert row["latency_ms"] == 42
        outcome = json.loads(row["outcome_json"])
        assert outcome["success"] is True
        assert outcome["latency_ms"] == 42

    def test_bind_outcome_failure_with_low_predicted(self, temp_ledger):
        helper = self._helper()
        h = helper.record_decision(
            selected="x",
            cell={"k": "v"},
            predicted_p_success=0.2,
        )
        helper.bind_outcome(h, success=False, latency_ms=500)
        row = _read_rows(temp_ledger)[0]
        assert row["score_band"] == "tn"
        # Brier = (0.2 - 0.0)^2 = 0.04
        assert row["score_numeric"] == pytest.approx(0.04, abs=1e-6)

    def test_bind_outcome_extras_merged(self, temp_ledger):
        helper = self._helper()
        h = helper.record_decision(
            selected="x",
            cell={"k": "v"},
            predicted_p_success=0.5,
        )
        helper.bind_outcome(
            h,
            success=True,
            latency_ms=10,
            outcome_extras={"results_returned": 7, "downgraded": False},
        )
        outcome = json.loads(_read_rows(temp_ledger)[0]["outcome_json"])
        assert outcome["results_returned"] == 7
        assert outcome["downgraded"] is False

    def test_bind_outcome_noop_when_handle_event_id_empty(self, temp_ledger):
        helper = self._helper()
        empty_handle = RouterDecisionHandle(
            decision_id="x",
            ledger_event_id="",
            fingerprint="f",
            predicted_p_success=0.5,
            eu_score=0.0,
            selected="y",
        )
        # Should NOT raise
        helper.bind_outcome(empty_handle, success=True, latency_ms=10)
        # Ledger remains empty
        assert _read_rows(temp_ledger) == []


# =========================================================================== #
# RouterClosedLoopHelper.get_posterior
# =========================================================================== #
class TestGetPosterior:
    def _helper(self):
        return RouterClosedLoopHelper(
            layer="L1",
            router="c0",
            ledger_name="router_l1_c0",
            repo_area="x",
        )

    def test_get_posterior_no_rows_returns_unused(self, temp_ledger, monkeypatch):
        # Point the schema-registry resolution at our temp ledger
        from tools.ledgers import schema_registry as sr

        original_get = sr.get

        def patched_get(name):
            spec = original_get(name)
            spec_dict = spec.__dict__.copy()
            return type(spec)(**spec_dict)  # immutable, can't mutate; rely on LEDGERS_DIR redirection

        # The temp_ledger fixture already redirects LEDGERS_DIR; spec.db_path will resolve to tmp.
        v = self._helper().get_posterior(
            selected="tier_a",
            cell={"intent": "X", "slo": "fast"},
        )
        assert v.used is False
        assert v.fallback_reason in {"no_rows", "ledger_unavailable"}
        # Beta(1,1) prior mean = 0.5
        assert v.posterior_mean == pytest.approx(0.5)

    def test_get_posterior_used_above_floor(self, temp_ledger):
        helper = self._helper()
        # Seed 30 winning rows for the same (selected, cell)
        sel = "tier_a"
        cell = {"intent": "X", "slo": "fast"}
        for _ in range(30):
            h = helper.record_decision(
                selected=sel,
                cell=cell,
                predicted_p_success=0.7,
            )
            helper.bind_outcome(h, success=True, latency_ms=10)

        v = helper.get_posterior(selected=sel, cell=cell)
        assert v.used is True
        assert v.fallback_reason == "ok"
        assert v.n == 30
        assert v.successes == 30
        # (1+30) / (2+30) = 31/32
        assert v.posterior_mean == pytest.approx(31 / 32, abs=1e-6)

    def test_get_posterior_below_floor_returns_unused(self, temp_ledger):
        helper = self._helper()
        sel = "tier_a"
        cell = {"intent": "X", "slo": "fast"}
        for _ in range(5):
            h = helper.record_decision(
                selected=sel,
                cell=cell,
                predicted_p_success=0.7,
            )
            helper.bind_outcome(h, success=True, latency_ms=10)
        v = helper.get_posterior(selected=sel, cell=cell)
        assert v.used is False
        assert v.fallback_reason == "n_below_floor"
        assert v.n == 5

    def test_get_posterior_n_floor_override(self, temp_ledger):
        helper = self._helper()
        sel = "tier_a"
        cell = {"intent": "X", "slo": "fast"}
        for _ in range(5):
            h = helper.record_decision(selected=sel, cell=cell, predicted_p_success=0.7)
            helper.bind_outcome(h, success=True, latency_ms=10)
        # With n_floor=5 the same data clears the floor
        v = helper.get_posterior(selected=sel, cell=cell, n_floor=5)
        assert v.used is True


# =========================================================================== #
# Default n-floor matches §29 promotion gate
# =========================================================================== #
def test_default_n_floor_matches_constitutional_29():
    """Constitutional §29 promotion gate: n>=30. Routing posterior shares it."""
    assert DEFAULT_POSTERIOR_N_FLOOR == 30


# =========================================================================== #
# Multiple routers writing to the same ledger don't collide
# =========================================================================== #
def test_multiple_routers_independent_handles(temp_ledger):
    a = RouterClosedLoopHelper(
        layer="L1",
        router="c0",
        ledger_name="router_l1_c0",
        repo_area="a",
    )
    b = RouterClosedLoopHelper(
        layer="L1",
        router="c0",
        ledger_name="router_l1_c0",
        repo_area="b",
    )
    h1 = a.record_decision(selected="x", cell={"k": "v"}, predicted_p_success=0.5)
    h2 = b.record_decision(selected="y", cell={"k": "v"}, predicted_p_success=0.5)
    assert h1.decision_id != h2.decision_id
    assert h1.ledger_event_id != h2.ledger_event_id
    rows = _read_rows(temp_ledger)
    assert len(rows) == 2
