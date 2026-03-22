"""ADG-driven tests for review_protocol_util and verification_types_util shims — fan_in=2.

Contract tests: re-export identity for both shims.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# review_protocol_util
# ---------------------------------------------------------------------------
class TestReviewProtocolShim:
    def test_importable(self):
        import agentic_core.utils.review_protocol_util as mod
        assert mod is not None

    def test_human_review_protocol_exported(self):
        from agentic_core.utils.review_protocol_util import HumanReviewProtocol
        assert callable(HumanReviewProtocol)

    def test_review_request_exported(self):
        from agentic_core.utils.review_protocol_util import ReviewRequest
        assert callable(ReviewRequest)

    def test_review_result_exported(self):
        from agentic_core.utils.review_protocol_util import ReviewResult
        assert callable(ReviewResult)

    def test_review_status_exported(self):
        from agentic_core.utils.review_protocol_util import ReviewStatus
        assert callable(ReviewStatus)

    def test_all_list_complete(self):
        from agentic_core.utils.review_protocol_util import __all__
        for name in ("HumanReviewProtocol", "ReviewRequest", "ReviewResult", "ReviewStatus"):
            assert name in __all__

    def test_identity_matches_canonical(self):
        from agentic_core.runtime.config.review_config import ReviewRequest as canon
        from agentic_core.utils.review_protocol_util import ReviewRequest as shim
        assert shim is canon


# ---------------------------------------------------------------------------
# verification_types_util
# ---------------------------------------------------------------------------
class TestVerificationTypesShim:
    def test_importable(self):
        import agentic_core.utils.verification_types_util as mod
        assert mod is not None

    def test_verification_gate_protocol_exported(self):
        from agentic_core.utils.verification_types_util import VerificationGateProtocol
        assert callable(VerificationGateProtocol)

    def test_verification_request_exported(self):
        from agentic_core.utils.verification_types_util import VerificationRequest
        assert callable(VerificationRequest)

    def test_verification_result_exported(self):
        from agentic_core.utils.verification_types_util import VerificationResult
        assert callable(VerificationResult)

    def test_all_list_complete(self):
        from agentic_core.utils.verification_types_util import __all__
        for name in ("VerificationGateProtocol", "VerificationRequest", "VerificationResult"):
            assert name in __all__

    def test_identity_matches_canonical(self):
        from agentic_core.L5_safety.types.verification_types import VerificationRequest as canon
        from agentic_core.utils.verification_types_util import VerificationRequest as shim
        assert shim is canon
