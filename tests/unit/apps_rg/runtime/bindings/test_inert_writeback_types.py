"""Wave 4.2 — unit tests for inert_writeback_types.

Covers the W8 UWG-gated writeback value objects: commit-rate math, the
inert->committed durability properties, TokenBudget within-budget/overage logic,
and the L6 firewall __post_init__ invariants on L6ShadowHandoff.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from apps_rg.runtime.bindings.inert_writeback_types import (
    L6_FIREWALL_INVARIANTS,
    AppsRgInertWritebackCandidate,
    CallerSessionBinding,
    L6ShadowHandoff,
    TokenBudget,
    WritebackCommitStatus,
)


class TestFirewallInvariants:
    def test_all_invariants_true(self) -> None:
        assert all(L6_FIREWALL_INVARIANTS.values())
        assert L6_FIREWALL_INVARIANTS["l6_is_future_run_only"] is True


class TestWritebackCommitStatus:
    def test_default_total_zero(self) -> None:
        s = WritebackCommitStatus()
        assert s.total_candidates == 0
        assert s.commit_rate == 0.0

    def test_total_candidates_sum(self) -> None:
        s = WritebackCommitStatus(
            inert_candidate_count=2,
            uwg_committed_count=3,
            pending_commit_count=5,
        )
        assert s.total_candidates == 10

    def test_commit_rate(self) -> None:
        s = WritebackCommitStatus(
            inert_candidate_count=1,
            uwg_committed_count=3,
            pending_commit_count=0,
        )
        assert s.commit_rate == 0.75

    def test_commit_rate_rounded(self) -> None:
        s = WritebackCommitStatus(uwg_committed_count=1, pending_commit_count=2)
        assert s.commit_rate == round(1 / 3, 4)


class TestInertWritebackCandidate:
    def _candidate(self, **overrides) -> AppsRgInertWritebackCandidate:
        base = dict(
            writeback_type="section",
            content_path="/p",
            content_hash="h",
            run_id="r",
            request_id="req",
            trace_id="t",
            evidence_digest="ed",
        )
        base.update(overrides)
        return AppsRgInertWritebackCandidate(**base)

    def test_default_candidate_not_committed(self) -> None:
        c = self._candidate()
        assert c.status == "CANDIDATE"
        assert c.is_committed is False
        assert c.durable_commit_occurred is False

    def test_committed_requires_receipt(self) -> None:
        c = self._candidate(status="COMMITTED", uwg_receipt_ref=None)
        assert c.is_committed is False

    def test_committed_with_receipt(self) -> None:
        c = self._candidate(status="COMMITTED", uwg_receipt_ref="rcpt")
        assert c.is_committed is True
        # durable also needs a commit timestamp
        assert c.durable_commit_occurred is False

    def test_durable_commit_full(self) -> None:
        c = self._candidate(
            status="COMMITTED",
            uwg_receipt_ref="rcpt",
            uwg_commit_timestamp=datetime.now(timezone.utc),
        )
        assert c.durable_commit_occurred is True


class TestTokenBudget:
    def test_within_budget(self) -> None:
        b = TokenBudget(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            estimated_cost_usd=0.10,
        )
        assert b.within_budget is True
        assert b.overage == {}

    def test_over_input_limit(self) -> None:
        b = TokenBudget(
            input_tokens=9000,
            output_tokens=50,
            total_tokens=9050,
            estimated_cost_usd=0.10,
        )
        assert b.within_budget is False
        assert b.overage["input_tokens"] == 9000 - 8192

    def test_over_cost_limit(self) -> None:
        b = TokenBudget(
            input_tokens=10,
            output_tokens=10,
            total_tokens=20,
            estimated_cost_usd=0.75,
        )
        assert b.within_budget is False
        assert b.overage["cost_usd"] == round(0.75 - 0.50, 4)

    def test_frozen(self) -> None:
        import dataclasses

        b = TokenBudget(
            input_tokens=1, output_tokens=1, total_tokens=2, estimated_cost_usd=0.0
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            b.input_tokens = 99  # type: ignore[misc]


class TestCallerSessionBinding:
    def test_defaults(self) -> None:
        b = CallerSessionBinding(
            caller_id="c",
            session_id="s",
            ingress_timestamp=datetime.now(timezone.utc),
            request_id="r",
            trace_id="t",
            payload_digest="d",
        )
        assert b.idempotency_key == ""
        assert b.caller_context == {}


class TestL6ShadowHandoff:
    def test_default_valid_construction(self) -> None:
        h = L6ShadowHandoff(handoff_type="metric")
        assert h.is_future_run_only is True
        assert h.applicable_run == "FUTURE_ONLY"
        assert h.trace_refs == []

    def test_mutate_current_run_raises(self) -> None:
        with pytest.raises(ValueError, match="can_mutate_current_run=True violates"):
            L6ShadowHandoff(handoff_type="metric", can_mutate_current_run=True)

    def test_rescue_current_run_raises(self) -> None:
        with pytest.raises(ValueError, match="can_rescue_current_run=True violates"):
            L6ShadowHandoff(handoff_type="metric", can_rescue_current_run=True)
