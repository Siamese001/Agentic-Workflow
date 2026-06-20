"""Closed-loop tests for L0/path + L0/agentic routers (constitutional §29 non-matrix).

Plan: closed-loop-router-fleet-rollout-d8f2a3 / NEXT_STEP wave (W5.5)

Verifies:
  - PathRouter.route_with_confidence() emits ROUTER_DECISION + writes ledger row
  - AgenticRouter.route() records decision + binds outcome in one shot
  - Both wirings are fail-soft and preserve their existing public APIs
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
def _seed_ledger(tmp_path: Path, schema_filename: str, ledger_filename: str) -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    base_sql = (repo_root / ".codex" / "schemas" / "ledger_base.schema.sql").read_text()
    per_sql = (repo_root / ".codex" / "schemas" / schema_filename).read_text()
    db_path = tmp_path / ledger_filename
    conn = sqlite3.connect(str(db_path))
    conn.executescript(base_sql)
    conn.executescript(per_sql)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def temp_path_ledger(tmp_path, monkeypatch):
    from tools.ledgers import schema_registry, writer as writer_mod
    from agentic_core.L0_routing.reasoning import path_router as pr

    monkeypatch.setattr(schema_registry, "LEDGERS_DIR", tmp_path)
    monkeypatch.setattr(writer_mod, "_WRITERS", {})
    monkeypatch.setattr(pr, "_PATH_HELPER", None)
    return _seed_ledger(tmp_path, "router_l0_path_ledger.schema.sql", "router_l0_path.sqlite")


@pytest.fixture
def temp_agentic_ledger(tmp_path, monkeypatch):
    from tools.ledgers import schema_registry, writer as writer_mod
    from agentic_core.L0_routing.reasoning import agentic_router as ar

    monkeypatch.setattr(schema_registry, "LEDGERS_DIR", tmp_path)
    monkeypatch.setattr(writer_mod, "_WRITERS", {})
    monkeypatch.setattr(ar, "_AGENTIC_HELPER", None)
    return _seed_ledger(tmp_path, "router_l0_agentic_ledger.schema.sql", "router_l0_agentic.sqlite")


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


# =========================================================================== #
# L0/path PathRouter
# =========================================================================== #
class TestPathRouterClosedLoop:
    def test_proceed_path_writes_decision_row(self, temp_path_ledger):
        from agentic_core.L0_routing.reasoning.path_router import PathRouter
        from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload

        payload = GovernedPayload(
            s0_system="sys", i0_instructional="inst",
            c0_context="ctx", u0_user_prompt="hello",
        )

        router = PathRouter()
        result = router.route_with_confidence(payload, confidence=0.9, threshold=0.5)
        assert result["route"] in {"A", "B", "C", "D", "R5"}

        rows = _read_rows(temp_path_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["event_kind"] == "route_decision"
        pred = json.loads(row["prediction_json"])
        assert pred["selected"] == result["route"]
        assert pred["cell"]["threshold"] == pytest.approx(0.5)
        assert pred["predicted_p_success"] == pytest.approx(0.9)
        # eu_score = confidence - threshold = 0.4
        assert pred["eu_score"] == pytest.approx(0.4)

    def test_abstain_writes_r5_decision(self, temp_path_ledger):
        from agentic_core.L0_routing.reasoning.path_router import PathRouter
        from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload

        payload = GovernedPayload(
            s0_system="sys", i0_instructional="inst",
            c0_context="ctx", u0_user_prompt="hi",
        )

        router = PathRouter()
        result = router.route_with_confidence(payload, confidence=0.1, threshold=0.5)
        assert result["route"] == "R5"

        rows = _read_rows(temp_path_ledger)
        assert len(rows) == 1
        pred = json.loads(rows[0]["prediction_json"])
        assert pred["selected"] == "R5"
        assert pred["abstain"] is True
        assert pred["eu_score"] == pytest.approx(-0.4)

    def test_metadata_anchors_to_constitutional_29(self, temp_path_ledger):
        from agentic_core.L0_routing.reasoning.path_router import PathRouter
        from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload

        payload = GovernedPayload(
            s0_system="sys", i0_instructional="inst",
            c0_context="ctx", u0_user_prompt="x",
        )

        router = PathRouter()
        router.route_with_confidence(payload, confidence=0.9, threshold=0.5)
        meta = json.loads(_read_rows(temp_path_ledger)[0]["metadata_json"])
        assert meta["router"] == "L0/path"
        assert meta["constitutional_rule"] == "§29"


# =========================================================================== #
# L0/agentic AgenticRouter
# =========================================================================== #
class TestAgenticRouterClosedLoop:
    def test_route_records_decision_with_outcome(self, temp_agentic_ledger):
        from agentic_core.L0_routing.reasoning.agentic_router import AgenticRouter

        async def _fallback(_input, _ctx):
            return "fallback-result"

        router = AgenticRouter(fallback_handler=_fallback, min_confidence=0.5)
        # No registered targets so confidence will be 0 → fallback fires.
        decision = asyncio.run(router.route("hello world"))
        assert decision is not None

        rows = _read_rows(temp_agentic_ledger)
        assert len(rows) == 1
        row = rows[0]
        assert row["event_kind"] == "route_decision"
        # Should be bound (decision + outcome captured in one shot)
        assert row["status"] == "bound"

        pred = json.loads(row["prediction_json"])
        assert "intent" in pred
        assert pred["min_confidence"] == pytest.approx(0.5)
        assert "had_classifier" in pred

    def test_metadata_anchors_to_constitutional_29(self, temp_agentic_ledger):
        from agentic_core.L0_routing.reasoning.agentic_router import AgenticRouter

        async def _fallback(_input, _ctx):
            return "x"

        router = AgenticRouter(fallback_handler=_fallback, min_confidence=0.5)
        asyncio.run(router.route("hi"))
        meta = json.loads(_read_rows(temp_agentic_ledger)[0]["metadata_json"])
        assert meta["router"] == "L0/agentic"
        assert meta["constitutional_rule"] == "§29"
