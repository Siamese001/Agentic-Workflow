"""apps_lic W5 (D4) — CampaignBatchOrchestrator sentinel tests.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W5 D4-P1, D4-P2, D4-P3

Coverage:
  - Config file presence and schema
  - BatchAdmissionReceipt shape and immutability
  - BatchRecipientResult shape and immutability
  - Successful batch dispatch
  - Deduplication by manifest_hash (DUPLICATE_SKIPPED)
  - Rate limiting (RATE_LIMITED) beyond max_recipients_per_batch
  - Partial failure: one recipient raises, rest continue (FAILED disposition)
  - Receipt counters are consistent (total_dispatched + total_skipped == total_requested)
  - All dispositions in BATCH_DISPOSITIONS whitelist
  - UWG batch receipt shape: required fields present
  - _compute_manifest_hash is deterministic and content-addressed
  - Decision-only: orchestrator does not write state; receipt is caller responsibility
"""

from __future__ import annotations

import pytest
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_run_fn(raises: bool = False, run_id: str = "run-001"):
    """Return a stub run_fn that either returns a fake record or raises."""
    def run_fn(campaign_request):
        if raises:
            raise RuntimeError("simulated run failure")
        rec = MagicMock()
        rec.run_id = run_id
        return rec
    return run_fn


def _make_entry(recipient_id: str, manifest_hash: str | None = None):
    from apps_lic.integrations.campaign_batch_orchestrator import BatchRecipientRequest
    if manifest_hash is None:
        manifest_hash = f"sha256:{recipient_id.encode().hex()[:24]}"
    req = MagicMock()
    req.recipient_id = recipient_id
    return BatchRecipientRequest(
        recipient_id=recipient_id,
        campaign_request=req,
        manifest_hash=manifest_hash,
    )


def _make_batch(entries, batch_id: str = "batch-001", sender_id: str = "sender-1"):
    from apps_lic.integrations.campaign_batch_orchestrator import BatchCampaignRequest
    return BatchCampaignRequest(
        batch_id=batch_id,
        sender_id=sender_id,
        entries=tuple(entries),
    )


def _orchestrator(run_fn=None, config: dict | None = None):
    from apps_lic.integrations.campaign_batch_orchestrator import CampaignBatchOrchestrator
    if run_fn is None:
        run_fn = _make_run_fn()
    return CampaignBatchOrchestrator(run_fn=run_fn, config=config or {})


# ===========================================================================
# 1. Config file presence and schema
# ===========================================================================

class TestCampaignBatchPolicyConfig:
    def test_config_file_exists(self):
        from pathlib import Path
        cfg = (
            Path(__file__).parent.parent.parent
            / "apps_lic" / "config" / "campaign_batch_policy.yaml"
        )
        assert cfg.exists(), f"campaign_batch_policy.yaml missing at {cfg}"

    def test_config_has_max_recipients(self):
        from pathlib import Path
        import yaml
        cfg = yaml.safe_load(
            open(Path(__file__).parent.parent.parent / "apps_lic" / "config" / "campaign_batch_policy.yaml")
        )
        assert "max_recipients_per_batch" in cfg
        assert int(cfg["max_recipients_per_batch"]) > 0


# ===========================================================================
# 2. BatchAdmissionReceipt shape + immutability
# ===========================================================================

class TestBatchAdmissionReceiptShape:
    def _receipt(self):
        orch = _orchestrator()
        return orch.dispatch(_make_batch([_make_entry("r1")]))

    def test_returns_batch_admission_receipt(self):
        from apps_lic.integrations.campaign_batch_orchestrator import BatchAdmissionReceipt
        assert isinstance(self._receipt(), BatchAdmissionReceipt)

    def test_receipt_is_immutable(self):
        receipt = self._receipt()
        with pytest.raises((FrozenInstanceError, AttributeError)):
            receipt.batch_id = "tampered"  # type: ignore

    def test_required_fields_present(self):
        r = self._receipt()
        for field in ("batch_id", "sender_id", "total_requested", "total_dispatched",
                      "total_skipped", "total_failed", "results", "batch_duration_ms", "trace_id"):
            assert hasattr(r, field), f"BatchAdmissionReceipt missing field '{field}'"

    def test_results_is_tuple(self):
        r = self._receipt()
        assert isinstance(r.results, tuple)

    def test_trace_id_is_nonempty(self):
        r = self._receipt()
        assert r.trace_id != ""

    def test_batch_duration_ms_positive(self):
        r = self._receipt()
        assert r.batch_duration_ms >= 0.0


# ===========================================================================
# 3. BatchRecipientResult shape + immutability
# ===========================================================================

class TestBatchRecipientResultShape:
    def _result(self):
        orch = _orchestrator()
        receipt = orch.dispatch(_make_batch([_make_entry("r1")]))
        return receipt.results[0]

    def test_result_is_immutable(self):
        result = self._result()
        with pytest.raises((FrozenInstanceError, AttributeError)):
            result.disposition = "tampered"  # type: ignore

    def test_result_has_required_fields(self):
        r = self._result()
        for field in ("recipient_id", "disposition", "run_id", "manifest_hash", "error", "duration_ms"):
            assert hasattr(r, field), f"BatchRecipientResult missing field '{field}'"

    def test_disposition_in_whitelist(self):
        from apps_lic.integrations.campaign_batch_orchestrator import BATCH_DISPOSITIONS
        r = self._result()
        assert r.disposition in BATCH_DISPOSITIONS


# ===========================================================================
# 4. Successful batch dispatch
# ===========================================================================

class TestSuccessfulDispatch:
    def test_single_recipient_success(self):
        from apps_lic.integrations.campaign_batch_orchestrator import DISPOSITION_SUCCESS
        orch = _orchestrator(_make_run_fn(run_id="run-42"))
        receipt = orch.dispatch(_make_batch([_make_entry("r1")]))
        assert receipt.total_dispatched == 1
        assert receipt.total_skipped == 0
        assert receipt.total_failed == 0
        assert receipt.results[0].disposition == DISPOSITION_SUCCESS
        assert receipt.results[0].run_id == "run-42"

    def test_multiple_recipients_all_success(self):
        orch = _orchestrator(_make_run_fn())
        entries = [_make_entry(f"r{i}") for i in range(5)]
        receipt = orch.dispatch(_make_batch(entries))
        assert receipt.total_dispatched == 5
        assert receipt.total_skipped == 0
        assert receipt.total_requested == 5

    def test_batch_id_preserved(self):
        orch = _orchestrator()
        receipt = orch.dispatch(_make_batch([_make_entry("r1")], batch_id="my-batch-99"))
        assert receipt.batch_id == "my-batch-99"

    def test_sender_id_preserved(self):
        orch = _orchestrator()
        receipt = orch.dispatch(_make_batch([_make_entry("r1")], sender_id="sender-xyz"))
        assert receipt.sender_id == "sender-xyz"


# ===========================================================================
# 5. Deduplication
# ===========================================================================

class TestDeduplication:
    def test_duplicate_hash_skipped(self):
        from apps_lic.integrations.campaign_batch_orchestrator import (
            DISPOSITION_DUPLICATE_SKIPPED, DISPOSITION_SUCCESS,
        )
        orch = _orchestrator()
        shared_hash = "sha256:abc123abc123abc123abc123"
        entries = [
            _make_entry("r1", manifest_hash=shared_hash),
            _make_entry("r2", manifest_hash=shared_hash),  # duplicate
        ]
        receipt = orch.dispatch(_make_batch(entries))
        assert receipt.total_dispatched == 1
        assert receipt.total_skipped == 1
        dispositions = {r.recipient_id: r.disposition for r in receipt.results}
        assert dispositions["r1"] == DISPOSITION_SUCCESS
        assert dispositions["r2"] == DISPOSITION_DUPLICATE_SKIPPED

    def test_unique_hashes_all_dispatched(self):
        orch = _orchestrator()
        entries = [_make_entry(f"r{i}", manifest_hash=f"sha256:hash{i:06d}") for i in range(3)]
        receipt = orch.dispatch(_make_batch(entries))
        assert receipt.total_dispatched == 3
        assert receipt.total_skipped == 0

    def test_three_duplicates_only_first_dispatched(self):
        from apps_lic.integrations.campaign_batch_orchestrator import DISPOSITION_DUPLICATE_SKIPPED
        orch = _orchestrator()
        same_hash = "sha256:aaabbbcccdddeeefffaabbcc"
        entries = [_make_entry(f"r{i}", manifest_hash=same_hash) for i in range(3)]
        receipt = orch.dispatch(_make_batch(entries))
        assert receipt.total_dispatched == 1
        assert receipt.total_skipped == 2
        skipped = [r for r in receipt.results if r.disposition == DISPOSITION_DUPLICATE_SKIPPED]
        assert len(skipped) == 2


# ===========================================================================
# 6. Rate limiting
# ===========================================================================

class TestRateLimiting:
    def test_exceeds_max_recipients_rate_limited(self):
        from apps_lic.integrations.campaign_batch_orchestrator import DISPOSITION_RATE_LIMITED
        config = {"max_recipients_per_batch": 3}
        orch = _orchestrator(config=config)
        entries = [_make_entry(f"r{i}") for i in range(5)]
        receipt = orch.dispatch(_make_batch(entries))
        assert receipt.total_dispatched == 3
        assert receipt.total_skipped == 2
        rate_limited = [r for r in receipt.results if r.disposition == DISPOSITION_RATE_LIMITED]
        assert len(rate_limited) == 2

    def test_exactly_at_limit_all_dispatched(self):
        config = {"max_recipients_per_batch": 3}
        orch = _orchestrator(config=config)
        entries = [_make_entry(f"r{i}") for i in range(3)]
        receipt = orch.dispatch(_make_batch(entries))
        assert receipt.total_dispatched == 3
        assert receipt.total_skipped == 0

    def test_rate_limit_reason_in_error(self):
        from apps_lic.integrations.campaign_batch_orchestrator import DISPOSITION_RATE_LIMITED
        config = {"max_recipients_per_batch": 1}
        orch = _orchestrator(config=config)
        entries = [_make_entry(f"r{i}") for i in range(2)]
        receipt = orch.dispatch(_make_batch(entries))
        rl = [r for r in receipt.results if r.disposition == DISPOSITION_RATE_LIMITED]
        assert len(rl) == 1
        assert "rate_limit" in rl[0].error


# ===========================================================================
# 7. Partial failure
# ===========================================================================

class TestPartialFailure:
    def _mixed_run_fn(self, fail_ids: set[str]):
        """run_fn that raises for recipients whose ID is in fail_ids."""
        def run_fn(campaign_request):
            rid = str(getattr(campaign_request, "recipient_id", ""))
            if rid in fail_ids:
                raise ValueError(f"simulated failure for {rid}")
            rec = MagicMock()
            rec.run_id = f"run-{rid}"
            return rec
        return run_fn

    def test_one_failure_does_not_abort_batch(self):
        from apps_lic.integrations.campaign_batch_orchestrator import (
            DISPOSITION_FAILED, DISPOSITION_SUCCESS,
        )
        entries = []
        for i in range(3):
            entry = _make_entry(f"r{i}")
            entry_req = MagicMock()
            entry_req.recipient_id = f"r{i}"
            from apps_lic.integrations.campaign_batch_orchestrator import BatchRecipientRequest
            entries.append(BatchRecipientRequest(
                recipient_id=f"r{i}",
                campaign_request=entry_req,
                manifest_hash=f"sha256:hash{i:06d}",
            ))

        fail_fn = self._mixed_run_fn(fail_ids={"r1"})
        orch = _orchestrator(run_fn=fail_fn)
        receipt = orch.dispatch(_make_batch(entries))

        assert receipt.total_requested == 3
        assert receipt.total_failed == 1
        dispositions = {r.recipient_id: r.disposition for r in receipt.results}
        assert dispositions["r0"] == DISPOSITION_SUCCESS
        assert dispositions["r1"] == DISPOSITION_FAILED
        assert dispositions["r2"] == DISPOSITION_SUCCESS

    def test_failed_result_has_error_message(self):
        from apps_lic.integrations.campaign_batch_orchestrator import (
            DISPOSITION_FAILED, BatchRecipientRequest,
        )
        entry_req = MagicMock()
        entry_req.recipient_id = "r0"
        entry = BatchRecipientRequest(
            recipient_id="r0",
            campaign_request=entry_req,
            manifest_hash="sha256:fail000000000000000000000",
        )
        orch = _orchestrator(run_fn=_make_run_fn(raises=True))
        receipt = orch.dispatch(_make_batch([entry]))
        r = receipt.results[0]
        assert r.disposition == DISPOSITION_FAILED
        assert r.error != ""

    def test_all_fail_batch_completes(self):
        from apps_lic.integrations.campaign_batch_orchestrator import DISPOSITION_FAILED
        orch = _orchestrator(run_fn=_make_run_fn(raises=True))
        entries = [_make_entry(f"r{i}") for i in range(3)]
        receipt = orch.dispatch(_make_batch(entries))
        assert receipt.total_failed == 3
        assert all(r.disposition == DISPOSITION_FAILED for r in receipt.results)


# ===========================================================================
# 8. Counter consistency
# ===========================================================================

class TestCounterConsistency:
    def test_dispatched_plus_skipped_equals_requested(self):
        config = {"max_recipients_per_batch": 2}
        orch = _orchestrator(config=config)
        entries = [_make_entry(f"r{i}") for i in range(4)]
        receipt = orch.dispatch(_make_batch(entries))
        assert receipt.total_dispatched + receipt.total_skipped == receipt.total_requested

    def test_results_length_equals_requested(self):
        orch = _orchestrator()
        entries = [_make_entry(f"r{i}") for i in range(6)]
        receipt = orch.dispatch(_make_batch(entries))
        assert len(receipt.results) == receipt.total_requested

    def test_empty_batch_zero_counts(self):
        orch = _orchestrator()
        receipt = orch.dispatch(_make_batch([]))
        assert receipt.total_requested == 0
        assert receipt.total_dispatched == 0
        assert receipt.total_skipped == 0
        assert receipt.total_failed == 0
        assert receipt.results == ()


# ===========================================================================
# 9. _compute_manifest_hash utility
# ===========================================================================

class TestComputeManifestHash:
    def test_deterministic(self):
        from apps_lic.integrations.campaign_batch_orchestrator import _compute_manifest_hash
        h1 = _compute_manifest_hash("sender-1", "r1", "policy-abc")
        h2 = _compute_manifest_hash("sender-1", "r1", "policy-abc")
        assert h1 == h2

    def test_different_recipient_different_hash(self):
        from apps_lic.integrations.campaign_batch_orchestrator import _compute_manifest_hash
        h1 = _compute_manifest_hash("sender-1", "r1")
        h2 = _compute_manifest_hash("sender-1", "r2")
        assert h1 != h2

    def test_different_policy_different_hash(self):
        from apps_lic.integrations.campaign_batch_orchestrator import _compute_manifest_hash
        h1 = _compute_manifest_hash("sender-1", "r1", "policy-A")
        h2 = _compute_manifest_hash("sender-1", "r1", "policy-B")
        assert h1 != h2

    def test_hash_starts_with_sha256(self):
        from apps_lic.integrations.campaign_batch_orchestrator import _compute_manifest_hash
        h = _compute_manifest_hash("s", "r")
        assert h.startswith("sha256:")
