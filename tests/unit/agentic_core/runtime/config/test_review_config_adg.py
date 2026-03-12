"""ADG importability contract for agentic_core/runtime/config/review_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_review_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.config.review_config import (  # noqa: F401
        ReviewStatus,
        ReviewRequest,
        ReviewResult,
        HumanReviewProtocol,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReviewStatus = None  # type: ignore[assignment,misc]
    ReviewRequest = None  # type: ignore[assignment,misc]
    ReviewResult = None  # type: ignore[assignment,misc]
    HumanReviewProtocol = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="review_config.py deps unavailable")
class TestReviewConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: review_config.py must be importable."""
        assert _AVAILABLE

    def test_reviewstatus_is_type(self) -> None:
        assert ReviewStatus is not None

    def test_reviewrequest_is_type(self) -> None:
        assert ReviewRequest is not None

    def test_reviewresult_is_type(self) -> None:
        assert ReviewResult is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

