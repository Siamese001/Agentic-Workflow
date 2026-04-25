"""Tests for PromotionAuthority - promotion gate authority."""
import pytest
from unittest.mock import Mock
from agentic_core.L4_state.enforcement.promotion_authority import PromotionAuthority


class TestPromotionAuthority:
    def test_init(self):
        pa = PromotionAuthority()
        assert pa is not None

    def test_authorize_promotion(self):
        pa = PromotionAuthority()
        request = {"artifact": "model_v2", "from_stage": "uwg", "to_stage": "L4"}
        result = pa.authorize(request)
        assert hasattr(result, "approved")

    def test_reject_invalid_promotion(self):
        pa = PromotionAuthority()
        request = {"artifact": "model_v2"}  # missing fields
        result = pa.authorize(request)
        assert result.approved is False

    def test_promotion_requires_evidence(self):
        pa = PromotionAuthority(require_evidence=True)
        request = {"artifact": "model_v2", "from_stage": "uwg", "to_stage": "L4"}
        result = pa.authorize(request)
        assert result.approved is False  # missing evidence

    def test_promotion_with_evidence(self):
        pa = PromotionAuthority(require_evidence=True)
        request = {
            "artifact": "model_v2",
            "from_stage": "uwg",
            "to_stage": "L4",
            "evidence": {"regression_pass": True}
        }
        result = pa.authorize(request)
        assert result.approved is True

    def test_get_promotion_history(self):
        pa = PromotionAuthority()
        pa.authorize({"artifact": "x", "from_stage": "uwg", "to_stage": "L4"})
        history = pa.get_history()
        assert len(history) >= 1

    def test_revoke_promotion(self):
        pa = PromotionAuthority()
        pa.revoke("artifact_id")
        revoked = pa.get_revoked()
        assert "artifact_id" in revoked
