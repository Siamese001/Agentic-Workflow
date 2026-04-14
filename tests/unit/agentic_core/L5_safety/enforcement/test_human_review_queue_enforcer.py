"""Behavioral tests for human_review_queue_enforcer hardening changes.

Covers: _require_signing_secret, _utc_now, approve() empty-secret rejection.
"""

from __future__ import annotations

from datetime import timezone

import pytest


@pytest.mark.unit
class TestHumanReviewQueueEnforcer:
    """Behavioral tests for human_review_queue_enforcer hardening changes."""

    def test_require_signing_secret_empty_bytes_raises(self):
        """Empty bytes secret must raise ValueError."""
        from agentic_core.L5_safety.enforcement.human_review_queue_enforcer import _require_signing_secret

        with pytest.raises(ValueError, match="non-empty secret"):
            _require_signing_secret(b"")

    def test_require_signing_secret_nonempty_passes(self):
        """Non-empty secret must not raise."""
        from agentic_core.L5_safety.enforcement.human_review_queue_enforcer import _require_signing_secret

        _require_signing_secret(b"signing-key")  # must not raise

    def test_utc_now_returns_timezone_aware_datetime(self):
        """_utc_now must return a timezone-aware UTC datetime."""
        from agentic_core.L5_safety.enforcement.human_review_queue_enforcer import _utc_now

        result = _utc_now()
        assert result.tzinfo is not None
        assert result.tzinfo == timezone.utc

    def test_approve_empty_secret_raises_before_lock(self):
        """approve() with empty secret must raise ValueError immediately."""
        from agentic_core.L5_safety.enforcement.human_review_queue_enforcer import HumanReviewQueue

        queue = HumanReviewQueue()
        with pytest.raises(ValueError, match="non-empty secret"):
            queue.approve("any-id", "reviewer-1", secret=b"")
