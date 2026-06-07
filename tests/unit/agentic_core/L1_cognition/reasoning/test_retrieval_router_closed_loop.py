"""Closed-loop integration tests for L1/c0 RetrievalRouter (constitutional §29).

Plan: docs/archive/windsurf/legacy-tree/plans/closed-loop-router-fleet-rollout-d8f2a3.md (W1.6)

Verifies the wiring through tools.ledgers.router_helper:
  - route() emits the §29 marker
  - route() writes a route_decision row to artifacts/ledgers/router_l1_c0.sqlite
  - bind_outcome() updates the row with success/Brier/band
  - existing public API behavior preserved (covered by sibling test file)
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

import pytest

from agentic_core.L1_cognition.reasoning.retrieval_router import (
    IntentClass,
    RetrievalRouter,
    RouterHints,
    SLO,
    classify_intent,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def temp_ledger(tmp_path, monkeypatch):
    """Redirect router_l1_c0 ledger writes to tmp_path. Returns the DB Path."""
    from tools.ledgers import schema_registry, writer as writer_mod

    monkeypatch.setattr(schema_registry, "LEDGERS_DIR", tmp_path)
    monkeypatch.setattr(writer_mod, "_WRITERS", {})

    repo_root = Path(__file__).resolve().parents[5]
    base_sql = (repo_root / ".claude" / "schemas" / "ledger_base.schema.sql").read_text()
    per_sql = (repo_root / ".claude" / "schemas" / "router_l1_c0_ledger.schema.sql").read_text()
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


class TestRetrievalRouterClosedLoop:
    def test_route_emits_router_decision_marker(self, temp_ledger, caplog):
        caplog.set_level(logging.INFO, logger="tools.ledgers.router_helper")
        router = RetrievalRouter()
        plan = router.route("how does the healer route between tiers?")

        markers = [r.getMessage() for r in caplog.records if r.getMessage().startswith("ROUTER_DECISION:")]
        assert len(markers) == 1
        line = markers[0]
        assert "layer=L1" in line
        assert "router=c0" in line
        assert "selected=" in line
        # Should report a real intent (not UNKNOWN for this query)
        assert plan.intent_class != IntentClass.UNKNOWN

    def test_route_writes_ledger_row(self, temp_ledger):
        router = RetrievalRouter()
        plan = router.route(
            "trace_lookup for trace id abc",
            RouterHints(slo=SLO.INTERACTIVE),
        )
        rows = _read_rows(temp_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["event_kind"] == "route_decision"
        assert row["status"] == "predicted"

        pred = json.loads(row["prediction_json"])
        assert pred["selected"] == plan.dim_tier
        assert "fingerprint" in pred
        assert "predicted_p_success" in pred
        assert "eu_score" in pred
        # cell carries intent_class and slo
        assert pred["cell"]["intent_class"] == plan.intent_class.value
        assert pred["cell"]["slo"] == "interactive"
        # plan substructure echoed
        assert pred["plan"]["dim_tier"] == plan.dim_tier
        assert pred["plan"]["reranker_mode"] == plan.reranker_mode
        assert pred["plan"]["reflective"] == plan.reflective
        assert pred["plan"]["implied_budget_ms"] >= 0
        assert pred["plan"]["slo_budget_ms"] == 800  # SLO.INTERACTIVE
        # metadata stamps the constitutional anchor
        meta = json.loads(row["metadata_json"])
        assert meta["router"] == "L1/c0"
        assert meta["constitutional_rule"] == "§29"

    def test_decision_handle_stamped_on_plan(self, temp_ledger):
        router = RetrievalRouter()
        plan = router.route("what is the architecture?")
        handle = getattr(plan, "_decision_handle", None)
        assert handle is not None
        assert handle.decision_id != ""
        assert handle.ledger_event_id != ""
        assert handle.selected == plan.dim_tier

    def test_bind_outcome_marks_status_and_brier(self, temp_ledger):
        router = RetrievalRouter()
        plan = router.route("incident_recall query for outage X")

        # Simulate retrieval that fit the SLO with results
        router.bind_outcome(plan, success=True, latency_ms=120, results_returned=5)

        rows = _read_rows(temp_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["status"] == "bound"
        # band depends on heuristic prior (>=0.4); should be tp for success=True
        assert row["score_band"] in {"tp", "fn"}
        outcome = json.loads(row["outcome_json"])
        assert outcome["success"] is True
        assert outcome["latency_ms"] == 120
        assert outcome["results_returned"] == 5
        assert outcome["downgraded"] == bool(plan.downgrades)

    def test_bind_outcome_failure_path(self, temp_ledger):
        router = RetrievalRouter()
        plan = router.route("how come the cache breaks?")
        router.bind_outcome(plan, success=False, latency_ms=2500, results_returned=0)
        row = _read_rows(temp_ledger)[0]
        assert row["status"] == "bound"
        outcome = json.loads(row["outcome_json"])
        assert outcome["success"] is False
        assert outcome["results_returned"] == 0

    def test_bind_outcome_noop_when_no_handle(self):
        """Call bind_outcome on a plan with no handle (e.g., helper unavailable)."""
        router = RetrievalRouter()
        # Construct a synthetic plan WITHOUT going through route()
        from agentic_core.L1_cognition.reasoning.retrieval_router import (
            RetrievalPlan,
        )

        plan = RetrievalPlan(
            intent_class=IntentClass.UNKNOWN,
            query_transform="identity",
            reranker_mode="none",
            reflective=False,
            dim_tier="hot-interactive",
            collections=("docs",),
            hydration_mode="none",
            latency_budget_ms=100,
            route_reason="manual",
        )
        # Should NOT raise
        router.bind_outcome(plan, success=True, latency_ms=50)

    def test_route_preserves_existing_public_api(self, temp_ledger):
        """Adding closed-loop wiring must not change the public RetrievalPlan shape."""
        router = RetrievalRouter()
        plan = router.route("CamelCase symbol Foo.bar()", RouterHints(slo=SLO.INTERACTIVE))
        # Public dataclass fields all present
        assert plan.intent_class is not None
        assert plan.query_transform
        assert plan.reranker_mode
        assert isinstance(plan.reflective, bool)
        assert plan.dim_tier
        assert isinstance(plan.collections, tuple)
        assert plan.hydration_mode
        assert plan.latency_budget_ms > 0
        assert plan.route_reason

    def test_classify_intent_unchanged(self):
        """The classifier is unchanged by the closed-loop wiring."""
        assert classify_intent("trace_id abc") == IntentClass.TRACE_LOOKUP
        assert classify_intent("rca for outage") == IntentClass.INCIDENT_RECALL
        assert classify_intent("") == IntentClass.UNKNOWN
