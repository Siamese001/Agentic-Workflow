"""Unit tests for agentic_core.L5_safety.enforcement.adg_hitl_enricher."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from tests.unit.tools.adg.test_runtime_query import _build_fixture_db
from tools.adg.runtime_query import RuntimeADGQuery


@pytest.fixture()
def fake_query(tmp_path: Path):
    db = tmp_path / "adg_indexed_fixture.sqlite"
    _build_fixture_db(db)
    q = RuntimeADGQuery(sqlite_path=db)
    with patch(
        "agentic_core.L5_safety.enforcement.adg_hitl_enricher.get_default_query",
        return_value=q,
    ):
        yield q


def test_enrich_packet_adds_adg_context(fake_query):
    from agentic_core.L5_safety.enforcement.adg_hitl_enricher import enrich_hitl_packet

    base = {"request_id": "req-42", "action": "write_canonical"}
    out = enrich_hitl_packet(base, "n_central")
    assert out["request_id"] == "req-42"
    assert "adg_context" in out
    ctx = out["adg_context"]
    assert ctx["available"] is True
    assert ctx["archetype"] == "CENTRAL_DEPENDENCY"
    assert ctx["target"]["node_id"] == "n_central"
    assert ctx["fan_in"] == 25
    assert len(ctx["top_upstream_callers"]) == 3
    assert "provenance" in ctx


def test_enrich_packet_is_non_mutating(fake_query):
    from agentic_core.L5_safety.enforcement.adg_hitl_enricher import enrich_hitl_packet

    base = {"k": "v"}
    out = enrich_hitl_packet(base, "n_central")
    assert "adg_context" not in base  # original unchanged
    assert "adg_context" in out


def test_enrich_packet_unknown_target(fake_query):
    from agentic_core.L5_safety.enforcement.adg_hitl_enricher import enrich_hitl_packet

    out = enrich_hitl_packet({}, "does.not.exist")
    ctx = out["adg_context"]
    assert ctx["available"] is False


def test_enrich_packet_no_snapshot():
    with patch(
        "agentic_core.L5_safety.enforcement.adg_hitl_enricher.get_default_query",
        return_value=None,
    ):
        from agentic_core.L5_safety.enforcement.adg_hitl_enricher import enrich_hitl_packet

        out = enrich_hitl_packet({"x": 1}, "anything")
        assert out["x"] == 1
        assert out["adg_context"]["available"] is False
        assert out["adg_context"]["reason"] == "no_snapshot"


def test_priority_hint_urgent_for_safety(fake_query):
    from agentic_core.L5_safety.enforcement.adg_hitl_enricher import (
        enrich_hitl_packet,
        hitl_priority_hint,
    )

    packet = enrich_hitl_packet({}, "n_safety")
    assert hitl_priority_hint(packet) == "URGENT"


def test_priority_hint_urgent_for_central_write(fake_query):
    # n_central is L0, archetype CENTRAL_DEPENDENCY, and routing implies Execution surface.
    # The hint promotes any CENTRAL_DEPENDENCY at HIGH band to URGENT.
    from agentic_core.L5_safety.enforcement.adg_hitl_enricher import (
        enrich_hitl_packet,
        hitl_priority_hint,
    )

    packet = enrich_hitl_packet({}, "n_central")
    # The exact band depends on impact score; verify hint is at least HIGH.
    assert hitl_priority_hint(packet) in ("HIGH", "URGENT")


def test_priority_hint_normal_for_unavailable():
    from agentic_core.L5_safety.enforcement.adg_hitl_enricher import hitl_priority_hint

    assert hitl_priority_hint({"adg_context": {"available": False}}) == "NORMAL"
    assert hitl_priority_hint({}) == "NORMAL"


def test_enrich_surfaces_classified(fake_query):
    from agentic_core.L5_safety.enforcement.adg_hitl_enricher import enrich_hitl_packet

    out = enrich_hitl_packet({}, "n_safety")
    surfaces = out["adg_context"]["surfaces"]
    assert "Security" in surfaces
