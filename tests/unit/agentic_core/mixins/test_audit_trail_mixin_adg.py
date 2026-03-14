"""ADG-driven tests for mixins/audit_trail_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

_FIXED_TS = 1735689600.0  # 2026-01-01T00:00:00Z

pytestmark = pytest.mark.unit

from agentic_core.mixins.audit_trail_mixin import AuditProof, AuditTrailMixin


class TestAuditProof:
    def test_creates(self):
        proof = AuditProof(
            action_id="act-1",
            prev_hash="abc123",
            curr_hash="def456",
            timestamp=_FIXED_TS,
        )
        assert proof.action_id == "act-1"

    def test_to_dict_has_required_keys(self):
        proof = AuditProof(
            action_id="act-2",
            prev_hash="aaa",
            curr_hash="bbb",
            timestamp=1234567890.0,
        )
        d = proof.to_dict()
        for key in ("action_id", "prev_hash", "curr_hash", "timestamp", "chain_id"):
            assert key in d

    def test_verify_chain_link_valid(self):
        proof = AuditProof(
            action_id="act-3",
            prev_hash="prev",
            curr_hash="curr",
            timestamp=_FIXED_TS,
        )
        assert proof.verify_chain_link("prev") is True

    def test_verify_chain_link_invalid(self):
        proof = AuditProof(
            action_id="act-4",
            prev_hash="prev",
            curr_hash="curr",
            timestamp=_FIXED_TS,
        )
        assert proof.verify_chain_link("wrong") is False

    def test_chain_id_default_empty(self):
        proof = AuditProof(
            action_id="a", prev_hash="p", curr_hash="c", timestamp=0.0
        )
        assert proof.chain_id == ""


class TestAuditTrailMixin:
    def test_importable(self):
        assert callable(AuditTrailMixin)

    def test_has_log_sovereign_event(self):
        assert hasattr(AuditTrailMixin, "log_sovereign_event")
