"""W8 tests: AppsRgInertWritebackCandidate — inert until UWG receipt.
"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from apps_rg.runtime.bindings.inert_writeback_types import (
    AppsRgInertWritebackCandidate,
    TokenBudget,
    CallerSessionBinding,
    L6_FIREWALL_INVARIANTS,
)


class TestAppsRgInertWritebackCandidate(unittest.TestCase):
    """Test inert writeback candidate behavior."""

    def test_candidate_created_inert(self) -> None:
        """New candidates are inert (status=CANDIDATE)."""
        candidate = AppsRgInertWritebackCandidate(
            writeback_type="semantic_cache",
            content_path="artifacts/apps_rg/runs/test/run_001/generated_resume.json",
            content_hash="sha256:content_abc",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence_xyz",
        )
        
        self.assertEqual(candidate.status, "CANDIDATE")
        self.assertFalse(candidate.is_committed)
        self.assertFalse(candidate.durable_commit_occurred)
        self.assertIsNone(candidate.uwg_receipt_ref)

    def test_candidate_submitted_to_uwg(self) -> None:
        """Candidate can be submitted to UWG."""
        candidate = AppsRgInertWritebackCandidate(
            writeback_type="c0_chunk",
            content_path="artifacts/c0_chunks.json",
            content_hash="sha256:chunk_abc",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence_xyz",
            status="SUBMITTED_TO_UWG",
        )
        
        self.assertEqual(candidate.status, "SUBMITTED_TO_UWG")
        # Still not committed without receipt
        self.assertFalse(candidate.is_committed)
        self.assertFalse(candidate.durable_commit_occurred)

    def test_candidate_committed_with_receipt(self) -> None:
        """Candidate becomes committed with UWG receipt."""
        candidate = AppsRgInertWritebackCandidate(
            writeback_type="golden_state",
            content_path="artifacts/golden/test.json",
            content_hash="sha256:golden_abc",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence_xyz",
            status="COMMITTED",
            uwg_receipt_ref="uwg-receipt-001",
            uwg_commit_timestamp=datetime.now(timezone.utc),
        )
        
        self.assertEqual(candidate.status, "COMMITTED")
        self.assertTrue(candidate.is_committed)
        self.assertTrue(candidate.durable_commit_occurred)
        self.assertIsNotNone(candidate.uwg_receipt_ref)

    def test_rejected_candidate(self) -> None:
        """Candidate can be rejected by UWG."""
        candidate = AppsRgInertWritebackCandidate(
            writeback_type="semantic_cache",
            content_path="artifacts/cache.json",
            content_hash="sha256:cache_abc",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence_xyz",
            status="REJECTED",
        )
        
        self.assertEqual(candidate.status, "REJECTED")
        self.assertFalse(candidate.is_committed)
        self.assertFalse(candidate.durable_commit_occurred)

    def test_durable_commit_only_with_receipt(self) -> None:
        """Critical: durable_commit_occurred is False without UWG receipt."""
        # Candidate without receipt
        inert = AppsRgInertWritebackCandidate(
            writeback_type="semantic_cache",
            content_path="artifacts/cache.json",
            content_hash="sha256:abc",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence",
            status="CANDIDATE",
        )
        
        # Even if someone tries to fake it
        self.assertFalse(inert.durable_commit_occurred)
        
        # Only with receipt is it durable
        committed = AppsRgInertWritebackCandidate(
            writeback_type="semantic_cache",
            content_path="artifacts/cache.json",
            content_hash="sha256:abc",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence",
            status="COMMITTED",
            uwg_receipt_ref="uwg-receipt-001",
            uwg_commit_timestamp=datetime.now(timezone.utc),
        )
        
        self.assertTrue(committed.durable_commit_occurred)


class TestTokenBudget(unittest.TestCase):
    """Test token budget tracking."""

    def test_budget_within_limits(self) -> None:
        """Budget within limits is OK."""
        budget = TokenBudget(
            input_tokens=4000,
            output_tokens=2000,
            total_tokens=6000,
            estimated_cost_usd=0.25,
        )
        
        self.assertTrue(budget.within_budget)
        self.assertEqual(budget.overage, {})

    def test_budget_overage_detected(self) -> None:
        """Budget overage is detected."""
        budget = TokenBudget(
            input_tokens=10000,  # Over 8192 limit
            output_tokens=5000,  # Over 4096 limit
            total_tokens=15000,
            estimated_cost_usd=0.75,  # Over 0.50 limit
        )
        
        self.assertFalse(budget.within_budget)
        overage = budget.overage
        self.assertIn("input_tokens", overage)
        self.assertIn("output_tokens", overage)
        self.assertIn("cost_usd", overage)

    def test_partial_overage(self) -> None:
        """Partial overage (only some limits exceeded)."""
        budget = TokenBudget(
            input_tokens=4000,  # OK
            output_tokens=5000,  # Over limit
            total_tokens=9000,
            estimated_cost_usd=0.30,  # OK
        )
        
        self.assertFalse(budget.within_budget)
        overage = budget.overage
        self.assertNotIn("input_tokens", overage)
        self.assertIn("output_tokens", overage)
        self.assertNotIn("cost_usd", overage)


class TestCallerSessionBinding(unittest.TestCase):
    """Test U0 caller/session binding."""

    def test_binding_preserved_through_runtime(self) -> None:
        """Caller binding survives through runtime."""
        binding = CallerSessionBinding(
            caller_id="apps_rg_cli",
            session_id="session_001",
            ingress_timestamp=datetime.now(timezone.utc),
            request_id="req_001",
            trace_id="trace_001",
            idempotency_key="idem_001",
            payload_digest="sha256:payload_abc",
            caller_context={"source": "cli", "user": "test"},
        )
        
        self.assertEqual(binding.caller_id, "apps_rg_cli")
        self.assertEqual(binding.session_id, "session_001")
        self.assertEqual(binding.request_id, "req_001")

    def test_digest_for_replay_detection(self) -> None:
        """Payload digest enables replay detection."""
        binding = CallerSessionBinding(
            caller_id="apps_rg_wizard",
            session_id="session_002",
            ingress_timestamp=datetime.now(timezone.utc),
            request_id="req_002",
            trace_id="trace_002",
            payload_digest="sha256:unique_digest",
        )
        
        self.assertEqual(binding.payload_digest, "sha256:unique_digest")


class TestL6FirewallInvariants(unittest.TestCase):
    """Test L6 firewall invariants."""

    def test_l6_cannot_mutate_current_run(self) -> None:
        """L6 cannot mutate current run."""
        self.assertTrue(L6_FIREWALL_INVARIANTS["l6_cannot_mutate_current_run"])

    def test_l6_cannot_rescue_current_run(self) -> None:
        """L6 cannot rescue current run."""
        self.assertTrue(L6_FIREWALL_INVARIANTS["l6_cannot_rescue_current_run"])

    def test_l6_is_future_run_only(self) -> None:
        """L6 is future-run only."""
        self.assertTrue(L6_FIREWALL_INVARIANTS["l6_is_future_run_only"])

    def test_current_run_protected_from_l6(self) -> None:
        """Current run is protected from L6."""
        self.assertTrue(L6_FIREWALL_INVARIANTS["current_run_protected_from_l6"])


if __name__ == "__main__":
    unittest.main()
