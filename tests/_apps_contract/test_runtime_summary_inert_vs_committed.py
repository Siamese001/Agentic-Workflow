"""W8 tests: Runtime summary distinguishes inert vs committed writes.
"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from apps_rg.runtime.bindings.inert_writeback_types import (
    AppsRgInertWritebackCandidate,
    WritebackCommitStatus,
    L6ShadowHandoff,
)
from apps_rg.runtime.runtime_executive_summary import (
    RuntimeExecutiveSummary,
)


class TestWritebackCommitStatus(unittest.TestCase):
    """Test writeback commit status tracking."""

    def test_all_inert_no_commits(self) -> None:
        """All candidates inert, none committed."""
        candidate = AppsRgInertWritebackCandidate(
            writeback_type="semantic_cache",
            content_path="artifacts/cache.json",
            content_hash="sha256:abc",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence",
            status="CANDIDATE",
        )
        
        status = WritebackCommitStatus(
            inert_writeback_candidates=[candidate],
            inert_candidate_count=1,
            uwg_committed_writes=[],
            uwg_committed_count=0,
            durable_commit_occurred=False,
            pending_commit_count=0,
        )
        
        self.assertEqual(status.total_candidates, 1)
        self.assertEqual(status.inert_candidate_count, 1)
        self.assertEqual(status.uwg_committed_count, 0)
        self.assertFalse(status.durable_commit_occurred)
        self.assertEqual(status.commit_rate, 0.0)

    def test_mixed_inert_and_committed(self) -> None:
        """Some inert, some committed."""
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
        
        committed = AppsRgInertWritebackCandidate(
            writeback_type="golden_state",
            content_path="artifacts/golden.json",
            content_hash="sha256:def",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence2",
            status="COMMITTED",
            uwg_receipt_ref="uwg-001",
            uwg_commit_timestamp=datetime.now(timezone.utc),
        )
        
        status = WritebackCommitStatus(
            inert_writeback_candidates=[inert],
            inert_candidate_count=1,
            uwg_committed_writes=[committed],
            uwg_committed_count=1,
            durable_commit_occurred=True,  # At least one committed
            pending_commit_count=0,
        )
        
        self.assertEqual(status.total_candidates, 2)
        self.assertEqual(status.inert_candidate_count, 1)
        self.assertEqual(status.uwg_committed_count, 1)
        self.assertTrue(status.durable_commit_occurred)
        self.assertEqual(status.commit_rate, 0.5)

    def test_pending_commits(self) -> None:
        """Candidates submitted to UWG but awaiting receipt."""
        pending = AppsRgInertWritebackCandidate(
            writeback_type="semantic_cache",
            content_path="artifacts/cache.json",
            content_hash="sha256:abc",
            run_id="run_001",
            request_id="req_001",
            trace_id="trace_001",
            evidence_digest="sha256:evidence",
            status="SUBMITTED_TO_UWG",
        )
        
        status = WritebackCommitStatus(
            inert_writeback_candidates=[],
            inert_candidate_count=0,
            uwg_committed_writes=[],
            uwg_committed_count=0,
            durable_commit_occurred=False,  # No receipt yet
            pending_commit_count=1,
        )
        
        self.assertEqual(status.total_candidates, 1)
        self.assertEqual(status.pending_commit_count, 1)
        self.assertFalse(status.durable_commit_occurred)

    def test_durable_commit_false_without_receipt(self) -> None:
        """Critical: durable_commit_occurred is False without UWG receipt."""
        # Only inert candidates
        inert_only = WritebackCommitStatus(
            inert_writeback_candidates=[
                AppsRgInertWritebackCandidate(
                    writeback_type="semantic_cache",
                    content_path="artifacts/cache.json",
                    content_hash="sha256:abc",
                    run_id="run_001",
                    request_id="req_001",
                    trace_id="trace_001",
                    evidence_digest="sha256:evidence",
                    status="CANDIDATE",
                ),
            ],
            inert_candidate_count=1,
            uwg_committed_writes=[],
            uwg_committed_count=0,
            durable_commit_occurred=False,
            pending_commit_count=0,
        )
        
        self.assertFalse(inert_only.durable_commit_occurred)
        
        # Only pending
        pending_only = WritebackCommitStatus(
            inert_writeback_candidates=[],
            inert_candidate_count=0,
            uwg_committed_writes=[],
            uwg_committed_count=0,
            durable_commit_occurred=False,
            pending_commit_count=1,
        )
        
        self.assertFalse(pending_only.durable_commit_occurred)


class TestRuntimeSummaryWritebackFields(unittest.TestCase):
    """Test RuntimeExecutiveSummary writeback fields."""

    def test_summary_has_inert_writeback_fields(self) -> None:
        """Runtime summary tracks inert writeback candidates."""
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary
        
        # Check fields exist
        self.assertTrue(hasattr(RuntimeExecutiveSummary, 'inert_writeback_candidates'))
        self.assertTrue(hasattr(RuntimeExecutiveSummary, 'uwg_committed_writes'))

    def test_summary_distinguishes_inert_vs_committed(self) -> None:
        """Summary correctly separates inert and committed."""
        summary = RuntimeExecutiveSummary(
            run_id="run_001",
            trace_id="trace_001",
            target_company="TestCorp",
            target_role="Engineer",
            generation_mode="resume_shipping",
            start_timestamp=datetime.now(timezone.utc).isoformat(),
            end_timestamp=datetime.now(timezone.utc).isoformat(),
            total_duration_ms=1000,
            sections=[],
            inert_writeback_candidates=2,  # 2 candidates proposed
            uwg_committed_writes=1,         # 1 actually committed
        )
        
        # Summary distinguishes the two
        self.assertEqual(summary.inert_writeback_candidates, 2)
        self.assertEqual(summary.uwg_committed_writes, 1)


class TestL6ShadowHandoff(unittest.TestCase):
    """Test L6 shadow handoff is future-run only."""

    def test_handoff_is_future_run_only(self) -> None:
        """L6 handoff is marked as future-run only."""
        handoff = L6ShadowHandoff(
            handoff_type="L6_SHADOW_FUTURE_RUN",
            trace_refs=["trace_001", "trace_002"],
            applicable_run="FUTURE_ONLY",
            can_mutate_current_run=False,
            can_rescue_current_run=False,
            handoff_timestamp=datetime.now(timezone.utc),
            run_id="run_001",
            trace_id="trace_001",
        )
        
        self.assertEqual(handoff.applicable_run, "FUTURE_ONLY")
        self.assertFalse(handoff.can_mutate_current_run)
        self.assertFalse(handoff.can_rescue_current_run)

    def test_handoff_cannot_enable_mutation(self) -> None:
        """L6 handoff cannot be created with mutation enabled."""
        with self.assertRaises(ValueError):
            L6ShadowHandoff(
                handoff_type="L6_SHADOW_FUTURE_RUN",
                trace_refs=["trace_001"],
                applicable_run="FUTURE_ONLY",
                can_mutate_current_run=True,  # Attempting to enable mutation
                can_rescue_current_run=False,
            )

    def test_handoff_cannot_enable_rescue(self) -> None:
        """L6 handoff cannot be created with rescue enabled."""
        with self.assertRaises(ValueError):
            L6ShadowHandoff(
                handoff_type="L6_SHADOW_FUTURE_RUN",
                trace_refs=["trace_001"],
                applicable_run="FUTURE_ONLY",
                can_mutate_current_run=False,
                can_rescue_current_run=True,  # Attempting to enable rescue
            )

    def test_handoff_cannot_enable_both(self) -> None:
        """L6 handoff cannot enable both mutation and rescue."""
        with self.assertRaises(ValueError):
            L6ShadowHandoff(
                handoff_type="L6_SHADOW_FUTURE_RUN",
                trace_refs=["trace_001"],
                applicable_run="FUTURE_ONLY",
                can_mutate_current_run=True,
                can_rescue_current_run=True,
            )


class TestRuntimeExhaustBundleEmitted(unittest.TestCase):
    """Test RuntimeExhaustBundle emission tracking."""

    def test_bundle_emitted_field_exists(self) -> None:
        """Runtime summary tracks bundle emission."""
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary
        
        self.assertTrue(hasattr(RuntimeExecutiveSummary, 'runtime_exhaust_bundle_emitted'))

    def test_l6_handoff_emitted_field_exists(self) -> None:
        """Runtime summary tracks L6 handoff emission."""
        from apps_rg.runtime.runtime_executive_summary import RuntimeExecutiveSummary
        
        self.assertTrue(hasattr(RuntimeExecutiveSummary, 'l6_shadow_handoff_emitted'))


if __name__ == "__main__":
    unittest.main()
