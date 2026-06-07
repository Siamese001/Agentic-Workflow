"""v9 L0 route-contract invariant conformance tests — audit plan W4.

Plan ref: `docs/archive/windsurf/legacy-tree/plans/l0-routing-best-practice-audit-1f9180.md` §W4
v9 doc ref: `docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v9.md`

These tests lock in the v9 execution-class invariants:

  * **Terminal-class routes** (R1A, R1B, R5) execute ZERO L2 steps, use
    `execution_form="terminal_return"`, and bypass L3 entirely.
  * **Single-step routes** (R3, R4) execute EXACTLY one L2 step and bypass L3.
    R3 uses C0 (PROMPT ASSEMBLY); R4 does not.
  * **Orchestrated route** (R3R4_MANAGED) is the only arm permitted to enter L3.
  * **Fail-closed gates**: with both env flags off, :func:`check_route_gates`
    returns ``None`` and callers MUST fall through to ``select_path``.
  * **Contract shape**: on hit, the returned :class:`L0RouteContract` has
    ``selected_route`` ∈ {R1A, R1B} and ``execution_form="terminal_return"``.

This file is tests-only, has no call sites in production code, and must not
import anything from L1/L2/L3/L4. The only allowed production imports are
`agentic_core.L0_routing.types.routing_artifact_types` and
`agentic_core.L0_routing.reasoning.route_gates`.
"""

from __future__ import annotations

import os
from typing import Any
from unittest import mock

import pytest

from agentic_core.L0_routing.reasoning import route_gates
from agentic_core.L0_routing.reasoning.route_gates import (
    canonical_request_hash,
    check_d1_exact_cache,
    check_d2_semantic_cache,
    check_route_gates,
)
from agentic_core.L0_routing.types.routing_artifact_types import (
    L0_ORCHESTRATED_ROUTES,
    L0_SINGLE_STEP_ROUTES,
    L0_TERMINAL_ROUTES,
    L0Route,
)


# =============================================================================
# Invariant 1 — L0Route taxonomy partitions are complete and disjoint
# =============================================================================


class TestL0RoutePartitions:
    """The six L0Route arms partition cleanly into terminal / single / managed."""

    def test_terminal_routes_are_r1a_r1b_r5(self) -> None:
        assert L0_TERMINAL_ROUTES == frozenset(
            {L0Route.R1A, L0Route.R1B, L0Route.R5},
        )

    def test_single_step_routes_are_r3_r4(self) -> None:
        assert L0_SINGLE_STEP_ROUTES == frozenset({L0Route.R3, L0Route.R4})

    def test_orchestrated_routes_are_r3r4_managed_only(self) -> None:
        assert L0_ORCHESTRATED_ROUTES == frozenset({L0Route.R3R4_MANAGED})

    def test_partitions_are_disjoint(self) -> None:
        assert L0_TERMINAL_ROUTES.isdisjoint(L0_SINGLE_STEP_ROUTES)
        assert L0_TERMINAL_ROUTES.isdisjoint(L0_ORCHESTRATED_ROUTES)
        assert L0_SINGLE_STEP_ROUTES.isdisjoint(L0_ORCHESTRATED_ROUTES)

    def test_partitions_cover_all_six_arms(self) -> None:
        union = L0_TERMINAL_ROUTES | L0_SINGLE_STEP_ROUTES | L0_ORCHESTRATED_ROUTES
        assert union == set(L0Route)
        assert len(union) == 6


# =============================================================================
# Invariant 2 — canonical_request_hash is stable across key order
# =============================================================================


class TestCanonicalRequestHash:
    """D1 exact-cache keys MUST be stable regardless of dict key order."""

    def test_hash_is_stable_across_key_order(self) -> None:
        a = {"query": "hello", "tenant": "acme", "model": "gpt-4"}
        b = {"model": "gpt-4", "tenant": "acme", "query": "hello"}
        assert canonical_request_hash(a) == canonical_request_hash(b)

    def test_hash_differs_for_different_content(self) -> None:
        a = {"query": "hello"}
        b = {"query": "world"}
        assert canonical_request_hash(a) != canonical_request_hash(b)

    def test_hash_is_sha256_hex(self) -> None:
        digest = canonical_request_hash({"x": 1})
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_hash_handles_non_json_values_via_default_str(self) -> None:
        # object() isn't JSON-serializable; default=str must kick in.
        marker = object()
        digest = canonical_request_hash({"obj": marker})
        assert isinstance(digest, str)
        assert len(digest) == 64


# =============================================================================
# Invariant 3 — Fail-closed when env gates are off
# =============================================================================


@pytest.fixture
def gates_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force both D1 and D2 gates off."""
    monkeypatch.delenv("EXACT_CACHE_D1_ENABLED", raising=False)
    monkeypatch.delenv("SEMANTIC_CACHE_D2_ENABLED", raising=False)


class TestFailClosedWhenGatesOff:
    """With env flags off, gates return None without touching L4."""

    def test_d1_returns_none_when_disabled(self, gates_off: None) -> None:
        assert check_d1_exact_cache({"q": "x"}) is None

    def test_d2_returns_none_when_disabled(self, gates_off: None) -> None:
        assert check_d2_semantic_cache({"q": "x"}, namespace="test") is None

    def test_composed_gate_returns_none_when_both_disabled(
        self,
        gates_off: None,
    ) -> None:
        assert check_route_gates({"q": "x"}, namespace="test") is None

    def test_d1_does_not_import_l4_when_disabled(
        self,
        gates_off: None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Fail-closed must be cheap — no L4 import when D1 is off."""
        import_calls: list[str] = []
        real_import = (
            __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__
        )

        def tracking_import(name: str, *args: Any, **kwargs: Any) -> Any:
            if "l1_exact_cache" in name:
                import_calls.append(name)
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=tracking_import):
            check_d1_exact_cache({"q": "x"})
        assert import_calls == []


# =============================================================================
# Invariant 4 — Contract shape on hit
# =============================================================================


class _FakeCacheHit:
    """Duck-typed stand-in for L1ExactCache CacheHit."""

    def __init__(self, response: str = '{"answer": "cached"}') -> None:
        self.response = response
        self.cache_key = "fake-key"
        self.query_hash = "fake-qhash"
        self.hit_timestamp = "2026-04-22T00:00:00Z"
        self.ttl_seconds = 3600


class _FakeL1Cache:
    """Duck-typed stand-in for L1ExactCache."""

    def get(self, _request_hash: str) -> _FakeCacheHit:  # noqa: D401, PLR6301
        return _FakeCacheHit()


class _FakeL1CacheMiss:
    def get(self, _request_hash: str) -> None:  # noqa: D401, PLR6301
        return None


class TestContractShapeOnHit:
    """When a gate hits, the contract MUST conform to v9 terminal-return shape."""

    def test_d1_hit_returns_r1a_terminal_contract(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EXACT_CACHE_D1_ENABLED", "1")
        monkeypatch.delenv("SEMANTIC_CACHE_D2_ENABLED", raising=False)
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.l1_exact_cache.get_global_l1_cache",
            lambda: _FakeL1Cache(),
        )

        result = check_route_gates(
            {"query": "hello"},
            namespace="tests",
            trace_id="t-1",
        )
        assert result is not None
        contract, payload = result
        assert contract["selected_route"] == L0Route.R1A
        assert contract["execution_form"] == "terminal_return"
        assert contract["reason_codes"] == ("d1_exact_hit",)
        assert contract["trace_id"] == "t-1"
        assert contract["selected_route"] in L0_TERMINAL_ROUTES
        assert payload["response"] == {"answer": "cached"}

    def test_d1_miss_falls_through_to_d2_miss_returns_none(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EXACT_CACHE_D1_ENABLED", "1")
        monkeypatch.delenv("SEMANTIC_CACHE_D2_ENABLED", raising=False)
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.l1_exact_cache.get_global_l1_cache",
            lambda: _FakeL1CacheMiss(),
        )
        result = check_route_gates({"query": "x"}, namespace="tests")
        # D1 miss + D2 disabled → None; caller proceeds to select_path.
        assert result is None


# =============================================================================
# Invariant 5 — Terminal-return contracts never imply L2 work
# =============================================================================


class TestTerminalReturnInvariant:
    """Any contract with execution_form=terminal_return MUST be R1A/R1B/R5."""

    @pytest.mark.parametrize("route", sorted(L0_TERMINAL_ROUTES, key=lambda r: r.value))
    def test_terminal_route_has_zero_l2_steps_by_classification(
        self,
        route: L0Route,
    ) -> None:
        # Classification-only check: terminal routes are disjoint from
        # single-step and orchestrated routes, so by construction they
        # cannot dispatch an L2 step.
        assert route not in L0_SINGLE_STEP_ROUTES
        assert route not in L0_ORCHESTRATED_ROUTES

    @pytest.mark.parametrize("route", sorted(L0_SINGLE_STEP_ROUTES, key=lambda r: r.value))
    def test_single_step_route_bypasses_l3(self, route: L0Route) -> None:
        # Single-step routes (R3/R4) execute exactly one L2 step and must
        # not enter L3 orchestration.
        assert route not in L0_ORCHESTRATED_ROUTES
        assert route not in L0_TERMINAL_ROUTES


# =============================================================================
# Invariant 6 — No accidental side effects at module import
# =============================================================================


class TestModuleImportHygiene:
    """Importing route_gates must not touch Redis / ChromaDB / L4."""

    def test_module_has_no_module_level_network_io(self) -> None:
        # Sentinel check: the module's __dict__ should not contain any
        # already-instantiated L4 cache singletons.
        public = {k for k in vars(route_gates) if not k.startswith("_")}
        assert "L1ExactCache" not in public
        assert "SemanticCacheManager" not in public

    def test_exports_are_stable(self) -> None:
        # W3.P1 added `check_r3_grounding_gate` — additive extension of the
        # pinned __all__. Any further additions require updating this test
        # and an ADR per the enum-closure convention.
        assert set(route_gates.__all__) == {
            "canonical_request_hash",
            "check_d1_exact_cache",
            "check_d2_semantic_cache",
            "check_r3_grounding_gate",
            "check_route_gates",
        }


# =============================================================================
# Invariant 7 — _d1_enabled / _d2_enabled accept truthy aliases
# =============================================================================


class TestEnvFlagParsing:
    """Both gates accept ``1``, ``true``, ``yes`` (case-insensitive)."""

    @pytest.mark.parametrize("value", ["1", "true", "TRUE", "Yes", "yes"])
    def test_d1_truthy_values_enable(
        self,
        value: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EXACT_CACHE_D1_ENABLED", value)
        assert route_gates._d1_enabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "", "garbage"])
    def test_d1_other_values_disable(
        self,
        value: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EXACT_CACHE_D1_ENABLED", value)
        assert route_gates._d1_enabled() is False

    def test_d1_unset_disables(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("EXACT_CACHE_D1_ENABLED", raising=False)
        assert route_gates._d1_enabled() is False
