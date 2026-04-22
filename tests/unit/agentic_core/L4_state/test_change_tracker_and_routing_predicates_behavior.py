"""Behavioral tests for L4 change_tracker + vllm_routing_predicates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_core.L4_state.config.vllm_routing_predicates import (
    Provider,
    ROUTING_PREDICATES,
    RoutingDecision,
    RoutingPredicate,
    default_routing,
    evaluate,
    invalid_ast_detected,
    iteration_count_exceeded,
    requires_policy_read,
)
from agentic_core.L4_state.enforcement.change_tracker import (
    ChangeRecord,
    ChangeTracker,
)


# ============================================================================
# change_tracker
# ============================================================================


class TestChangeRecord:
    def test_resolves_file_path(self, tmp_path: Path) -> None:
        f = tmp_path / "x.py"
        rec = ChangeRecord("agent_a", f, "did thing")
        assert Path(rec.file_path).is_absolute()
        assert rec.agent == "agent_a"
        assert rec.description == "did thing"

    def test_accepts_str_path(self) -> None:
        rec = ChangeRecord("a", "relative/x.py", "d")
        # str path resolved to absolute
        assert Path(rec.file_path).is_absolute()


class TestChangeTracker:
    def test_empty_tracker(self) -> None:
        t = ChangeTracker()
        assert len(t) == 0
        assert t.records == []

    def test_record_appends(self, tmp_path: Path) -> None:
        t = ChangeTracker()
        t.record("a", tmp_path / "x.py", "d1")
        t.record("a", tmp_path / "y.py", "d2")
        assert len(t) == 2

    def test_clear_resets(self, tmp_path: Path) -> None:
        t = ChangeTracker()
        t.record("a", tmp_path / "x.py", "d")
        t.clear()
        assert len(t) == 0

    def test_group_by_agent(self, tmp_path: Path) -> None:
        t = ChangeTracker()
        t.record("agent_a", tmp_path / "x.py", "d1")
        t.record("agent_a", tmp_path / "y.py", "d2")
        t.record("agent_b", tmp_path / "z.py", "d3")
        groups = t._group_by_agent()
        assert len(groups["agent_a"]) == 2
        assert len(groups["agent_b"]) == 1

    def test_group_by_file(self, tmp_path: Path) -> None:
        t = ChangeTracker()
        f = tmp_path / "shared.py"
        t.record("agent_a", f, "d1")
        t.record("agent_b", f, "d2")
        groups = t._group_by_file()
        # one file, two agents
        assert len(groups) == 1
        changes = next(iter(groups.values()))
        assert len(changes) == 2

    def test_generate_markdown_report_includes_agents_and_files(
        self, tmp_path: Path,
    ) -> None:
        t = ChangeTracker()
        t.record("agent_a", tmp_path / "x.py", "did stuff")
        report = t.generate_markdown_report()
        assert "Sovereign Healing Change Report" in report
        assert "agent_a" in report
        assert "did stuff" in report
        assert "Total recorded modifications:** 1" in report

    def test_markdown_report_empty(self) -> None:
        t = ChangeTracker()
        report = t.generate_markdown_report()
        assert "Total recorded modifications:** 0" in report


# ============================================================================
# vllm_routing_predicates
# ============================================================================


class TestProviderEnum:
    @pytest.mark.parametrize("name,value", [
        ("OPUS", "opus"),
        ("LOCAL_VLLM", "local_vllm"),
        ("GEMINI_FLASH", "gemini_flash"),
        ("GEMINI_PRO", "gemini_pro"),
    ])
    def test_values(self, name: str, value: str) -> None:
        assert Provider[name].value == value


class TestRoutingDecisionImmutability:
    def test_frozen(self) -> None:
        d = RoutingDecision(
            provider=Provider.OPUS,
            predicate_evaluation_hash="h",
            routing_version="1",
        )
        with pytest.raises((AttributeError, Exception)):  # FrozenInstanceError
            d.provider = Provider.LOCAL_VLLM  # type: ignore[misc]


class TestPredicates:
    @pytest.mark.parametrize("ctx,expected", [
        ({}, False),
        ({"requires_policy_read": False}, False),
        ({"requires_policy_read": True}, True),
        ({"requires_policy_read": 1}, True),
    ])
    def test_requires_policy_read(self, ctx: dict[str, Any], expected: bool) -> None:
        assert requires_policy_read(ctx) is expected

    @pytest.mark.parametrize("ctx,expected", [
        ({}, False),  # 0 > 100 False
        ({"iteration_count": 50}, False),
        ({"iteration_count": 101}, True),
        ({"iteration_count": 5, "max_iterations": 2}, True),
        ({"iteration_count": 2, "max_iterations": 5}, False),
    ])
    def test_iteration_count_exceeded(
        self, ctx: dict[str, Any], expected: bool,
    ) -> None:
        assert iteration_count_exceeded(ctx) is expected

    @pytest.mark.parametrize("ctx,expected", [
        ({}, False),
        ({"invalid_ast": True}, True),
        ({"invalid_ast": False}, False),
    ])
    def test_invalid_ast_detected(self, ctx: dict[str, Any], expected: bool) -> None:
        assert invalid_ast_detected(ctx) is expected

    def test_default_routing_always_true(self) -> None:
        assert default_routing({}) is True
        assert default_routing({"x": 1}) is True


class TestRoutingPredicatesRegistry:
    def test_registry_shape(self) -> None:
        assert isinstance(ROUTING_PREDICATES, tuple)
        assert len(ROUTING_PREDICATES) == 4

    def test_entries_are_named_tuples(self) -> None:
        for entry in ROUTING_PREDICATES:
            assert isinstance(entry, RoutingPredicate)
            assert callable(entry.predicate)
            assert isinstance(entry.provider, Provider)

    def test_default_routing_last_and_local_vllm(self) -> None:
        last = ROUTING_PREDICATES[-1]
        assert last.name == "default_routing"
        assert last.provider is Provider.LOCAL_VLLM


class TestEvaluate:
    def test_policy_read_routes_to_opus(self) -> None:
        decision = evaluate({"requires_policy_read": True})
        assert decision.provider is Provider.OPUS

    def test_iteration_exceeded_routes_to_opus(self) -> None:
        decision = evaluate({"iteration_count": 200})
        assert decision.provider is Provider.OPUS

    def test_invalid_ast_routes_to_opus(self) -> None:
        decision = evaluate({"invalid_ast": True})
        assert decision.provider is Provider.OPUS

    def test_default_falls_through_to_local(self) -> None:
        decision = evaluate({})
        assert decision.provider is Provider.LOCAL_VLLM

    def test_does_not_mutate_context(self) -> None:
        ctx = {"requires_policy_read": True, "x": [1, 2, 3]}
        snapshot = {"requires_policy_read": True, "x": [1, 2, 3]}
        evaluate(ctx)
        assert ctx == snapshot

    def test_deterministic_hash(self) -> None:
        a = evaluate({"requires_policy_read": True, "extra": "x"})
        b = evaluate({"extra": "x", "requires_policy_read": True})  # reorder
        assert a.predicate_evaluation_hash == b.predicate_evaluation_hash

    def test_routing_version_copied_from_context(self) -> None:
        d = evaluate({"routing_version": "v42"})
        assert d.routing_version == "v42"

    def test_routing_version_defaults_to_unknown(self) -> None:
        d = evaluate({})
        assert d.routing_version == "unknown"

    def test_first_match_wins(self) -> None:
        # Both policy_read AND iteration triggers — first (policy_read) wins
        d = evaluate({"requires_policy_read": True, "iteration_count": 999})
        assert d.provider is Provider.OPUS  # both would route OPUS, but order matters
