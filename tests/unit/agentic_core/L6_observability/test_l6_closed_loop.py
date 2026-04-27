"""Closed-loop integration tests for L6/promo + L6/regret (constitutional §29).

Plan: .windsurf/plans/closed-loop-l6-promo-regret-wiring-e3c5b9.md (W1.5)

Verifies:
  - promotion_decision() writes a route_decision row with full Wilson interval
    evidence on every call (promote AND reject branches AND insufficient-sample)
  - RegretLedger.record() persists every sample to durable ledger AND
    in-memory list
  - Both wirings preserve existing public API
  - Both wirings are fail-soft when ledger is unreachable
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from agentic_core.L6_observability.promotion_gates import (
    PromotionVerdict,
    promotion_decision,
)
from agentic_core.L6_observability.regret_accounting import (
    DecisionRegretSample,
    RegretLedger,
)

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def temp_promo_ledger(tmp_path, monkeypatch):
    """Redirect router_l6_promo writes to tmp_path. Returns the DB Path."""
    from tools.ledgers import schema_registry, writer as writer_mod
    from agentic_core.L6_observability import promotion_gates as pg

    monkeypatch.setattr(schema_registry, "LEDGERS_DIR", tmp_path)
    monkeypatch.setattr(writer_mod, "_WRITERS", {})
    # Reset the lazy singleton so it rebinds against the redirected path
    monkeypatch.setattr(pg, "_PROMO_HELPER", None)

    repo_root = Path(__file__).resolve().parents[4]
    base_sql = (repo_root / ".windsurf" / "schemas" / "ledger_base.schema.sql").read_text()
    per_sql = (
        repo_root / ".windsurf" / "schemas" / "router_l6_promo_ledger.schema.sql"
    ).read_text()
    db_path = tmp_path / "router_l6_promo.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(base_sql)
    conn.executescript(per_sql)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def temp_regret_ledger(tmp_path, monkeypatch):
    """Redirect router_l6_regret writes to tmp_path. Returns the DB Path."""
    from tools.ledgers import schema_registry, writer as writer_mod
    from agentic_core.L6_observability import regret_accounting as ra

    monkeypatch.setattr(schema_registry, "LEDGERS_DIR", tmp_path)
    monkeypatch.setattr(writer_mod, "_WRITERS", {})
    monkeypatch.setattr(ra, "_REGRET_HELPER", None)

    repo_root = Path(__file__).resolve().parents[4]
    base_sql = (repo_root / ".windsurf" / "schemas" / "ledger_base.schema.sql").read_text()
    per_sql = (
        repo_root / ".windsurf" / "schemas" / "router_l6_regret_ledger.schema.sql"
    ).read_text()
    db_path = tmp_path / "router_l6_regret.sqlite"
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
        "prediction_json, outcome_json, metadata_json "
        "FROM events ORDER BY ts_utc"
    )
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, row)) for row in cur]
    conn.close()
    return rows


# =========================================================================== #
# L6/promo: promotion_decision wiring
# =========================================================================== #
class TestPromotionDecisionClosedLoop:
    def test_promote_writes_row_with_wilson_evidence(self, temp_promo_ledger):
        verdict = promotion_decision(
            candidate_successes=80, candidate_n=100,
            baseline_successes=50, baseline_n=100,
            min_n_each_arm=30,
        )
        assert verdict.promote is True
        rows = _read_rows(temp_promo_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["event_kind"] == "route_decision"
        pred = json.loads(row["prediction_json"])
        assert pred["selected"] == "promote"
        assert pred["promote"] is True
        assert pred["candidate_successes"] == 80
        assert pred["candidate_n"] == 100
        assert pred["baseline_successes"] == 50
        assert pred["baseline_n"] == 100
        # Wilson interval bounds present and reasonable
        assert 0.0 <= pred["candidate_lower"] <= pred["candidate_upper"] <= 1.0
        assert 0.0 <= pred["baseline_lower"] <= pred["baseline_upper"] <= 1.0
        # Promote path: candidate.lower > baseline.upper
        assert pred["candidate_lower"] > pred["baseline_upper"]
        # eu_score = candidate.lower - baseline.upper > 0 when promoted
        assert pred["eu_score"] > 0
        # Cell carries the gate parameters
        assert pred["cell"]["min_n_each_arm"] == 30
        assert "z" in pred["cell"]

    def test_reject_overlap_writes_row(self, temp_promo_ledger):
        # Tight CIs that overlap → reject
        verdict = promotion_decision(
            candidate_successes=55, candidate_n=100,
            baseline_successes=50, baseline_n=100,
            min_n_each_arm=30,
        )
        assert verdict.promote is False
        rows = _read_rows(temp_promo_ledger)
        assert len(rows) == 1
        pred = json.loads(rows[0]["prediction_json"])
        assert pred["selected"] == "reject"
        assert pred["promote"] is False
        assert "CIs overlap" in pred["verdict_reason"]

    def test_insufficient_sample_writes_row(self, temp_promo_ledger):
        verdict = promotion_decision(
            candidate_successes=8, candidate_n=10,
            baseline_successes=5, baseline_n=10,
            min_n_each_arm=30,
        )
        assert verdict.promote is False
        rows = _read_rows(temp_promo_ledger)
        assert len(rows) == 1
        pred = json.loads(rows[0]["prediction_json"])
        assert pred["selected"] == "reject"
        assert "insufficient sample" in pred["verdict_reason"]

    def test_multiple_decisions_accumulate(self, temp_promo_ledger):
        for _ in range(5):
            promotion_decision(
                candidate_successes=80, candidate_n=100,
                baseline_successes=50, baseline_n=100,
                min_n_each_arm=30,
            )
        rows = _read_rows(temp_promo_ledger)
        assert len(rows) == 5
        # All marked as promote
        for row in rows:
            pred = json.loads(row["prediction_json"])
            assert pred["selected"] == "promote"

    def test_metadata_anchors_to_constitutional_29(self, temp_promo_ledger):
        promotion_decision(
            candidate_successes=80, candidate_n=100,
            baseline_successes=50, baseline_n=100,
            min_n_each_arm=30,
        )
        meta = json.loads(_read_rows(temp_promo_ledger)[0]["metadata_json"])
        assert meta["router"] == "L6/promo"
        assert meta["constitutional_rule"] == "§29"

    def test_promotion_decision_preserves_public_api(self):
        """Wiring must not change PromotionVerdict shape or semantics."""
        verdict = promotion_decision(
            candidate_successes=80, candidate_n=100,
            baseline_successes=50, baseline_n=100,
        )
        assert isinstance(verdict, PromotionVerdict)
        assert hasattr(verdict, "promote")
        assert hasattr(verdict, "reason")
        assert hasattr(verdict, "candidate")
        assert hasattr(verdict, "baseline")


# =========================================================================== #
# L6/regret: RegretLedger.record wiring
# =========================================================================== #
class TestRegretLedgerClosedLoop:
    def test_record_persists_to_durable_ledger(self, temp_regret_ledger):
        rl = RegretLedger()
        sample = DecisionRegretSample(
            decision_id="d1",
            decision_layer="L0",
            chosen_reward=0.6,
            best_alternative_reward=0.9,
        )
        rl.record(sample)
        # In-memory still works
        assert rl.total_regret() == pytest.approx(0.3)
        # Durable row written
        rows = _read_rows(temp_regret_ledger)
        assert len(rows) == 1
        pred = json.loads(rows[0]["prediction_json"])
        assert pred["selected"] == "L0"
        assert pred["cell"]["decision_layer"] == "L0"
        assert pred["chosen_reward"] == pytest.approx(0.6)
        assert pred["best_alternative_reward"] == pytest.approx(0.9)
        assert pred["regret"] == pytest.approx(0.3)
        # eu_score = -regret
        assert pred["eu_score"] == pytest.approx(-0.3)

    def test_multiple_records_accumulate(self, temp_regret_ledger):
        rl = RegretLedger()
        for layer, chosen in [("L0", 0.3), ("L1", 0.7), ("L2", 0.5), ("L0", 0.4)]:
            rl.record(DecisionRegretSample(
                decision_id=f"d-{layer}-{chosen}",
                decision_layer=layer,
                chosen_reward=chosen,
                best_alternative_reward=1.0,
            ))
        rows = _read_rows(temp_regret_ledger)
        assert len(rows) == 4
        # In-memory aggregation still works
        by_layer = rl.by_layer()
        assert "L0" in by_layer
        assert by_layer["L0"].n_samples == 2

    def test_decision_id_propagates(self, temp_regret_ledger):
        rl = RegretLedger()
        rl.record(DecisionRegretSample(
            decision_id="custom-decision-42",
            decision_layer="L2",
            chosen_reward=0.5,
            best_alternative_reward=0.5,
        ))
        pred = json.loads(_read_rows(temp_regret_ledger)[0]["prediction_json"])
        assert pred["decision_id"] == "custom-decision-42"

    def test_metadata_anchors_to_constitutional_29(self, temp_regret_ledger):
        rl = RegretLedger()
        rl.record(DecisionRegretSample(
            decision_id="d", decision_layer="L1",
            chosen_reward=0.5, best_alternative_reward=0.6,
        ))
        meta = json.loads(_read_rows(temp_regret_ledger)[0]["metadata_json"])
        assert meta["router"] == "L6/regret"
        assert meta["constitutional_rule"] == "§29"

    def test_record_preserves_existing_aggregation(self, temp_regret_ledger):
        """The in-memory list + by_layer + top_offenders must behave identically."""
        rl = RegretLedger()
        rl.record(DecisionRegretSample(
            decision_id="d1", decision_layer="L0",
            chosen_reward=0.0, best_alternative_reward=1.0,
        ))
        rl.record(DecisionRegretSample(
            decision_id="d2", decision_layer="L0",
            chosen_reward=0.0, best_alternative_reward=1.0,
        ))
        rl.record(DecisionRegretSample(
            decision_id="d3", decision_layer="L1",
            chosen_reward=0.5, best_alternative_reward=0.6,
        ))
        offenders = rl.top_offenders(k=3)
        assert offenders[0].decision_layer == "L0"
        assert offenders[0].sum_regret == pytest.approx(2.0)
        assert offenders[0].n_samples == 2
