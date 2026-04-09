"""Tests for the token budgeter."""

from __future__ import annotations

import pytest

from tools.adg.prompt_assembly.budgeting.token_budgeter import (
    BudgetResult,
    apply_budget,
    estimate_dict_tokens,
    estimate_tokens,
)
from tools.adg.prompt_assembly.packets.registry import TokenBudget


class TestEstimateTokens:
    def test_json_estimation(self) -> None:
        content = '{"key": "value"}'
        tokens = estimate_tokens(content, "json")
        assert tokens > 0
        assert tokens == max(1, int(len(content) / 3.0))

    def test_text_estimation(self) -> None:
        content = "Hello world"
        tokens = estimate_tokens(content, "text")
        assert tokens > 0

    def test_empty_string(self) -> None:
        assert estimate_tokens("", "json") == 1  # min 1

    def test_code_estimation(self) -> None:
        content = "def foo():\n    return 42"
        tokens = estimate_tokens(content, "code")
        assert tokens == max(1, int(len(content) / 3.5))

    def test_unknown_content_type_uses_fallback(self) -> None:
        content = "some content"
        tokens = estimate_tokens(content, "unknown_type")
        assert tokens == max(1, int(len(content) / 3.5))  # fallback rate 3.5

    def test_dict_estimation(self) -> None:
        data = {"key": "value", "list": [1, 2, 3]}
        tokens = estimate_dict_tokens(data)
        assert tokens > 0


class TestApplyBudget:
    def _budget(self, total: int = 6000) -> TokenBudget:
        return TokenBudget(
            total=total,
            system_policy=800,
            task=400,
            must_use_evidence=4000,
            optional_evidence=800,
            contradiction_meta=400,
        )

    def test_within_budget(self) -> None:
        must = [{"source": "a", "data": "small"}]
        opt = [{"source": "b", "data": "small"}]
        result = apply_budget(must, opt, fixed_tokens=100, budget=self._budget())
        assert result.overflow_action == "none"
        assert result.budget_status == "within_budget"
        assert len(result.must_use_evidence) == 1
        assert len(result.optional_evidence) == 1

    def test_optional_trimmed_first(self) -> None:
        must = [{"source": "a", "data": "x" * 100}]
        # Large optional evidence
        opt = [{"source": f"opt_{i}", "data": "x" * 500} for i in range(20)]
        result = apply_budget(must, opt, fixed_tokens=100, budget=self._budget(total=1000))
        # Must-use should be preserved; optional should be trimmed
        assert len(result.must_use_evidence) >= 1
        assert len(result.optional_evidence) < 20 or result.overflow_action != "none"

    def test_abstain_when_budget_exhausted(self) -> None:
        result = apply_budget(
            [{"big": "x" * 10000}],
            [],
            fixed_tokens=5900,
            budget=self._budget(total=6000),
        )
        # With only 100 tokens left (6000 - 5900), evidence can't fit
        assert result.overflow_action in ("abstained", "summarized", "narrowed")

    def test_must_use_exceeds_budget_triggers_summarize(self) -> None:
        """When must-use evidence alone exceeds the budget, summarize overflow is triggered."""
        # 10 large must-use items, tiny budget
        must = [{"source": f"item_{i}", "data": "x" * 300} for i in range(10)]
        budget = TokenBudget(
            total=500,
            system_policy=50,
            task=50,
            must_use_evidence=300,
            optional_evidence=50,
            contradiction_meta=50,
        )
        result = apply_budget(must, [], fixed_tokens=50, budget=budget)
        # Must have trimmed must-use and used summarize or narrowed
        assert result.overflow_action in ("summarized", "abstained")
        assert result.trimmed_count > 0
        assert len(result.must_use_evidence) < 10
        assert result.budget_status == "trimmed"

    def test_empty_evidence(self) -> None:
        result = apply_budget([], [], fixed_tokens=100, budget=self._budget())
        assert result.overflow_action == "none"
        assert result.budget_status == "within_budget"
        assert result.must_use_evidence == []
        assert result.optional_evidence == []


class TestStratification:
    def test_severity_ordering(self) -> None:
        must = [
            {"severity": "low", "data": "x"},
            {"severity": "critical", "data": "y"},
            {"severity": "medium", "data": "z"},
        ]
        budget = TokenBudget(total=10000)
        result = apply_budget(must, [], fixed_tokens=100, budget=budget)
        # Items should be ordered by severity (critical first)
        if len(result.must_use_evidence) >= 2:
            assert result.must_use_evidence[0]["severity"] == "critical"

    def test_fanin_ordering(self) -> None:
        must = [
            {"fan_in": 5, "data": "low"},
            {"fan_in": 100, "data": "high"},
            {"fan_in": 50, "data": "mid"},
        ]
        budget = TokenBudget(total=10000)
        result = apply_budget(must, [], fixed_tokens=100, budget=budget, stratification="fan_in")
        # Items should be ordered by fan_in (highest first → most negative key)
        assert len(result.must_use_evidence) == 3
        assert result.must_use_evidence[0]["fan_in"] == 100
        assert result.must_use_evidence[1]["fan_in"] == 50
        assert result.must_use_evidence[2]["fan_in"] == 5
