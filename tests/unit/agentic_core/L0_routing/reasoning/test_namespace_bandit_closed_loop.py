"""Closed-loop integration tests for L0/bandit (constitutional §29 row #1).

Plan: closed-loop-router-fleet-rollout-d8f2a3 (Wave B, W5.4)

Verifies NamespaceBandit.choose() + .update() wire correctly through
RouterClosedLoopHelper to the durable router_l0_bandit ledger.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from agentic_core.L0_routing.reasoning.namespace_bandit import (
    BetaPosterior,
    NamespaceBandit,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def temp_bandit_ledger(tmp_path, monkeypatch):
    from tools.ledgers import schema_registry, writer as writer_mod
    from agentic_core.L0_routing.reasoning import namespace_bandit as nb

    monkeypatch.setattr(schema_registry, "LEDGERS_DIR", tmp_path)
    monkeypatch.setattr(writer_mod, "_WRITERS", {})
    monkeypatch.setattr(nb, "_BANDIT_HELPER", None)

    repo_root = Path(__file__).resolve().parents[5]
    base_sql = (repo_root / ".windsurf" / "schemas" / "ledger_base.schema.sql").read_text()
    per_sql = (
        repo_root / ".windsurf" / "schemas" / "router_l0_bandit_ledger.schema.sql"
    ).read_text()
    db_path = tmp_path / "router_l0_bandit.sqlite"
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
        "prediction_json, outcome_json, metadata_json FROM events ORDER BY ts_utc"
    )
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, row)) for row in cur]
    conn.close()
    return rows


class TestNamespaceBanditClosedLoop:
    def test_choose_writes_decision_row(self, temp_bandit_ledger):
        bandit = NamespaceBandit(seed=42)
        chosen = bandit.choose("legal", admissible=["R1B", "R3", "R5"])
        assert chosen in {"R1B", "R3", "R5"}
        rows = _read_rows(temp_bandit_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["event_kind"] == "route_decision"
        assert row["status"] == "predicted"
        pred = json.loads(row["prediction_json"])
        assert pred["selected"] == chosen
        assert pred["cell"]["namespace"] == "legal"
        assert sorted(pred["cell"]["admissible"]) == ["R1B", "R3", "R5"]
        # Beta(1,1) prior: posterior_alpha=1.0, posterior_beta=1.0, mean=0.5
        assert pred["posterior_alpha"] == 1.0
        assert pred["posterior_beta"] == 1.0
        assert pred["predicted_p_success"] == pytest.approx(0.5)

    def test_update_binds_outcome(self, temp_bandit_ledger):
        bandit = NamespaceBandit(seed=42)
        chosen = bandit.choose("legal", admissible=["R3"])
        bandit.update("legal", chosen, success=True)
        rows = _read_rows(temp_bandit_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["status"] == "bound"
        # band: 0.5 prior + success=True → fp band (predicted-success threshold 0.5 inclusive AND succeeded → tp); 0.5 → tp
        assert row["score_band"] == "tp"
        # Brier = (1.0 - 0.5)² = 0.25
        assert row["score_numeric"] == pytest.approx(0.25, abs=1e-6)
        outcome = json.loads(row["outcome_json"])
        assert outcome["success"] is True
        assert outcome["posterior_alpha_after"] == 2.0  # 1 + 1 success
        assert outcome["posterior_beta_after"] == 1.0

    def test_update_failure_path(self, temp_bandit_ledger):
        bandit = NamespaceBandit(seed=42)
        chosen = bandit.choose("legal", admissible=["R3"])
        bandit.update("legal", chosen, success=False)
        row = _read_rows(temp_bandit_ledger)[0]
        assert row["status"] == "bound"
        outcome = json.loads(row["outcome_json"])
        assert outcome["success"] is False
        assert outcome["posterior_alpha_after"] == 1.0
        assert outcome["posterior_beta_after"] == 2.0  # 1 + 1 failure

    def test_multiple_choose_update_pairs(self, temp_bandit_ledger):
        bandit = NamespaceBandit(seed=42)
        for _ in range(5):
            chosen = bandit.choose("legal", admissible=["R3"])
            bandit.update("legal", chosen, success=True)
        rows = _read_rows(temp_bandit_ledger)
        assert len(rows) == 5
        assert all(r["status"] == "bound" for r in rows)

    def test_metadata_anchors_to_constitutional_29(self, temp_bandit_ledger):
        bandit = NamespaceBandit(seed=42)
        bandit.choose("legal", admissible=["R3"])
        meta = json.loads(_read_rows(temp_bandit_ledger)[0]["metadata_json"])
        assert meta["router"] == "L0/bandit"
        assert meta["constitutional_rule"] == "§29"

    def test_update_without_prior_choose_does_not_raise(self, temp_bandit_ledger):
        """If a caller skips choose() and directly calls update(), the bandit
        still updates its in-memory posterior. The ledger has no open handle
        to bind to, but the call must not raise."""
        bandit = NamespaceBandit(seed=42)
        # Should NOT raise
        bandit.update("legal", "R3", success=True)
        # Posterior was updated
        post = bandit.posterior("legal", "R3")
        assert post.alpha == 2.0

    def test_preserves_existing_public_api(self):
        """The choose/update API surface must be unchanged."""
        bandit = NamespaceBandit(seed=42)
        assert isinstance(bandit.posterior("ns", "r"), BetaPosterior)
        snapshot = bandit.snapshot()
        assert isinstance(snapshot, dict)
