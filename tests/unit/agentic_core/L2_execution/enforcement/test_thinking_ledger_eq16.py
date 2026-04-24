"""EQ-16 — thinking-token ledger tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement._thinking_token_ledger import (
    ThinkingTokenLedger,
    get_default_ledger,
    reset_default_ledger,
)


@pytest.fixture
def ledger() -> ThinkingTokenLedger:
    return ThinkingTokenLedger()


class TestRecord:
    def test_single_record(self, ledger: ThinkingTokenLedger) -> None:
        ledger.record(
            trace_id="t1",
            provider="openai",
            thinking_tokens=120,
            budget_tokens=500,
            model="o1-preview",
        )
        records = ledger.records_for("t1")
        assert len(records) == 1
        assert records[0].thinking_tokens == 120
        assert records[0].budget_tokens == 500

    def test_zero_thinking_tokens_is_valid(self, ledger: ThinkingTokenLedger) -> None:
        ledger.record(trace_id="t1", provider="anthropic", thinking_tokens=0)
        assert ledger.total_for("t1") == 0

    def test_negative_thinking_tokens_rejected(self, ledger: ThinkingTokenLedger) -> None:
        with pytest.raises(ValueError, match="thinking_tokens"):
            ledger.record(
                trace_id="t1", provider="openai", thinking_tokens=-5
            )


class TestAccumulation:
    def test_multiple_records_sum(self, ledger: ThinkingTokenLedger) -> None:
        ledger.record(trace_id="t1", provider="openai", thinking_tokens=100)
        ledger.record(trace_id="t1", provider="openai", thinking_tokens=150)
        assert ledger.total_for("t1") == 250

    def test_records_partitioned_by_trace(self, ledger: ThinkingTokenLedger) -> None:
        ledger.record(trace_id="t1", provider="x", thinking_tokens=10)
        ledger.record(trace_id="t2", provider="x", thinking_tokens=99)
        assert ledger.total_for("t1") == 10
        assert ledger.total_for("t2") == 99

    def test_unknown_trace_returns_empty(self, ledger: ThinkingTokenLedger) -> None:
        assert ledger.records_for("nonexistent") == []
        assert ledger.total_for("nonexistent") == 0


class TestReconcile:
    def test_reconcile_with_known_budget(self, ledger: ThinkingTokenLedger) -> None:
        ledger.record(trace_id="t1", provider="x", thinking_tokens=300, budget_tokens=500)
        out = ledger.reconcile("t1")
        assert out == {"actual": 300, "budget": 500, "delta": -200}

    def test_reconcile_with_no_budget_observations(
        self, ledger: ThinkingTokenLedger
    ) -> None:
        ledger.record(trace_id="t1", provider="x", thinking_tokens=50)
        out = ledger.reconcile("t1")
        assert out["actual"] == 50
        assert out["budget"] is None
        assert out["delta"] is None

    def test_reconcile_uses_latest_budget(
        self, ledger: ThinkingTokenLedger
    ) -> None:
        ledger.record(trace_id="t1", provider="x", thinking_tokens=10, budget_tokens=100)
        ledger.record(trace_id="t1", provider="x", thinking_tokens=10, budget_tokens=300)
        out = ledger.reconcile("t1")
        # 20 actual, latest budget observation wins.
        assert out == {"actual": 20, "budget": 300, "delta": -280}

    def test_reconcile_over_budget_has_positive_delta(
        self, ledger: ThinkingTokenLedger
    ) -> None:
        ledger.record(trace_id="t1", provider="x", thinking_tokens=800, budget_tokens=500)
        out = ledger.reconcile("t1")
        assert out["delta"] == 300


class TestDefaultLedger:
    def test_default_ledger_is_singleton(self) -> None:
        reset_default_ledger()
        a = get_default_ledger()
        b = get_default_ledger()
        assert a is b

    def test_reset_replaces_instance(self) -> None:
        before = get_default_ledger()
        before.record(trace_id="t1", provider="x", thinking_tokens=1)
        reset_default_ledger()
        after = get_default_ledger()
        assert after is not before
        assert after.total_for("t1") == 0


class TestClear:
    def test_clear_removes_all_records(self, ledger: ThinkingTokenLedger) -> None:
        ledger.record(trace_id="t1", provider="x", thinking_tokens=10)
        ledger.record(trace_id="t2", provider="x", thinking_tokens=20)
        ledger.clear()
        assert ledger.total_for("t1") == 0
        assert ledger.total_for("t2") == 0
