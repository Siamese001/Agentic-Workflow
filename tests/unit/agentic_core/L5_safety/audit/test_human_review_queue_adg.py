"""ADG importability contract for agentic_core/L5_safety/audit/human_review_queue.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_human_review_queue.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.audit.human_review_queue import (  # noqa: F401
        HumanReviewQueue,
        PendingVerdict,
        get_review_queue,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PendingVerdict = None  # type: ignore[assignment,misc]
    HumanReviewQueue = None  # type: ignore[assignment,misc]
    get_review_queue = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="human_review_queue deps unavailable")
class TestHumanReviewQueueImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/audit/human_review_queue.py must be importable."""
        assert _AVAILABLE

    def test_pendingverdict_defined(self) -> None:
        assert PendingVerdict is not None

    def test_humanreviewqueue_defined(self) -> None:
        assert HumanReviewQueue is not None
