"""Unit tests for the W5 P5.3 blast-radius pilot on ``ExecutionOrchestrator``.

Plan: ``docs/archive/windsurf/legacy-tree/plans/adg-three-bucket-unified-c4f8e2.md`` (W5 P5.3).
ADR:  ``docs/architecture/adr/ADR-079-l2-agent-graph-layer-contract.md``.

The pilot is the first L2/L3 consumer of the P3.3 graph-layer MCP surface.
Tests verify:
  * default path (flag OFF) returns empty dict and does not touch ADG
  * enabled path (flag ON) populates the cache from an injected service
  * ADG exceptions degrade to empty dict without raising
  * cache is keyed by node_id so multiple calls accumulate
  * pre-existing orchestrator behavior (run / history / reset) unaffected

Tests are offline — they inject a fake ``ADGService`` rather than touching
the real SQLite snapshot.
"""

from __future__ import annotations

# Inventory: this test file exercises an L3 orchestrator that itself declares
# inventory consumer mode per ADR-079.
__adg_consumer_mode__ = "inventory"

import logging

import pytest

from agentic_core.L3_orchestration.reasoning.engines.execution_orchestrator import (
    ExecutionOrchestrator,
    _PILOT_FLAG_ENV,
    _pilot_enabled,
    validate_execution_orchestrator,
)


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeADGResponse:
    """Mimics ``tools.adg.core.service.ADGResponse`` for injection tests."""

    def __init__(self, data: dict, backend_used: str = "sqlite") -> None:
        self.data = data
        self.backend_used = backend_used


class _FakeADGService:
    """Records calls and returns canned ``_FakeADGResponse`` objects.

    Set ``raise_exc`` to inject a failure on the next ``get_blast_radius`` call.
    """

    def __init__(self, response: _FakeADGResponse | None = None, raise_exc: Exception | None = None) -> None:
        self._response = response or _FakeADGResponse(data={"edges": [], "nodes": []})
        self._raise_exc = raise_exc
        self.calls: list[tuple[str, int]] = []

    def get_blast_radius(self, node_id: str, hops: int = 2):
        self.calls.append((node_id, hops))
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._response


# ---------------------------------------------------------------------------
# _pilot_enabled
# ---------------------------------------------------------------------------


def test_pilot_enabled_default_is_false(monkeypatch) -> None:
    monkeypatch.delenv(_PILOT_FLAG_ENV, raising=False)
    assert _pilot_enabled() is False


def test_pilot_enabled_when_env_is_one(monkeypatch) -> None:
    monkeypatch.setenv(_PILOT_FLAG_ENV, "1")
    assert _pilot_enabled() is True


@pytest.mark.parametrize("value", ["0", "", "true", "yes", "ON", "anything-else"])
def test_pilot_enabled_only_fires_on_exact_one(monkeypatch, value: str) -> None:
    """Only the literal "1" activates the pilot — a deliberately strict check."""
    monkeypatch.setenv(_PILOT_FLAG_ENV, value)
    assert _pilot_enabled() is False


# ---------------------------------------------------------------------------
# populate_blast_radius_cache — flag OFF (default)
# ---------------------------------------------------------------------------


def test_populate_returns_empty_when_flag_off(monkeypatch) -> None:
    """Default path must not touch ADG nor mutate state."""
    monkeypatch.delenv(_PILOT_FLAG_ENV, raising=False)
    orch = ExecutionOrchestrator()
    fake = _FakeADGService()

    result = orch.populate_blast_radius_cache("ADG::Symbol::X", service=fake)

    assert result == {}
    assert fake.calls == [], "ADG service was invoked despite flag being OFF"
    assert "blast_radius_cache" not in orch.state, "state was mutated with flag OFF"


# ---------------------------------------------------------------------------
# populate_blast_radius_cache — flag ON, happy path
# ---------------------------------------------------------------------------


def test_populate_populates_cache_when_flag_on(monkeypatch) -> None:
    monkeypatch.setenv(_PILOT_FLAG_ENV, "1")
    orch = ExecutionOrchestrator()
    fake = _FakeADGService(
        response=_FakeADGResponse(
            data={"edges": [{"src": "A", "dst": "B"}], "nodes": ["A", "B"]},
            backend_used="sqlite",
        )
    )

    result = orch.populate_blast_radius_cache(
        "ADG::Symbol::pkg.mod.func", hops=3, service=fake
    )

    assert result["node_id"] == "ADG::Symbol::pkg.mod.func"
    assert result["hops"] == 3
    assert result["data"]["nodes"] == ["A", "B"]
    assert result["backend_used"] == "sqlite"
    assert fake.calls == [("ADG::Symbol::pkg.mod.func", 3)]

    cache = orch.state["blast_radius_cache"]
    assert cache["ADG::Symbol::pkg.mod.func"] is result


def test_populate_default_hops_is_two(monkeypatch) -> None:
    """Default ``hops=2`` matches the P3.3 MCP tool default."""
    monkeypatch.setenv(_PILOT_FLAG_ENV, "1")
    orch = ExecutionOrchestrator()
    fake = _FakeADGService()
    orch.populate_blast_radius_cache("X", service=fake)
    assert fake.calls == [("X", 2)]


def test_populate_multiple_keys_accumulate(monkeypatch) -> None:
    monkeypatch.setenv(_PILOT_FLAG_ENV, "1")
    orch = ExecutionOrchestrator()
    fake = _FakeADGService()
    orch.populate_blast_radius_cache("A", service=fake)
    orch.populate_blast_radius_cache("B", service=fake)
    orch.populate_blast_radius_cache("C", service=fake)
    cache = orch.state["blast_radius_cache"]
    assert set(cache.keys()) == {"A", "B", "C"}


# ---------------------------------------------------------------------------
# populate_blast_radius_cache — flag ON, ADG failure paths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "exc",
    [
        OSError("sqlite snapshot unreachable"),
        RuntimeError("MV query failed"),
        ValueError("invalid node_id"),
        ImportError("ADGService import path broken"),
    ],
)
def test_populate_degrades_to_empty_on_adg_exception(
    monkeypatch, caplog, exc: Exception
) -> None:
    """ADR-079: ADG failure must degrade to empty dict, never propagate."""
    monkeypatch.setenv(_PILOT_FLAG_ENV, "1")
    orch = ExecutionOrchestrator()
    fake = _FakeADGService(raise_exc=exc)

    with caplog.at_level(logging.WARNING):
        result = orch.populate_blast_radius_cache("Y", service=fake)

    assert result == {}
    # Cache created (setdefault) but no entry for "Y" — the failure path
    # MUST NOT partially populate.
    assert "Y" not in orch.state.get("blast_radius_cache", {})
    # Failure is logged with the ADG pilot marker, not silently swallowed.
    assert any(
        "P5.3 blast-radius pilot" in record.message for record in caplog.records
    ), f"expected pilot-warning log entry; got records: {caplog.records}"


# ---------------------------------------------------------------------------
# Regression: pre-existing orchestrator methods still work
# ---------------------------------------------------------------------------


def test_run_history_reset_unaffected() -> None:
    """The new method must not break the existing shim contract."""
    orch = ExecutionOrchestrator()
    r1 = orch.run({"a": 1})
    r2 = orch.run({"b": 2})
    assert r1["a"] == 1 and r1["run_count"] == 1
    assert r2["b"] == 2 and r2["run_count"] == 2
    assert len(orch.history()) == 2
    orch.reset()
    assert orch.state == {}
    assert orch.history() == []


def test_validate_execution_orchestrator_still_passes() -> None:
    """Module-level validator shouldn't regress."""
    assert validate_execution_orchestrator() is True
