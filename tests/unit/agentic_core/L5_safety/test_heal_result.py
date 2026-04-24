"""Tests for W2 HealResult + HealOutcome (plan c8e4f1)."""
from __future__ import annotations

import pytest

from agentic_core.L5_safety.types.heal_request_types import (
    HealOutcome,
    HealRequest,
    HealResult,
)


def _req(rid: str = "r1") -> HealRequest:
    return HealRequest(
        request_id=rid,
        parent_packet_id="pkt-42",
        policy_hash="pol-abc",
        blueprint_hash="bp-xyz",
        violation_payload={"kind": "schema_mismatch"},
        originating_run_id="run-1",
    )


class TestHealOutcome:
    def test_has_four_values(self):
        assert {o.value for o in HealOutcome} == {
            "SUCCESS",
            "SOFT_REPAIRABLE",
            "FAIL_TERMINAL",
            "NEEDS_HELP",
        }

    def test_is_string_enum(self):
        assert HealOutcome.SUCCESS == "SUCCESS"


class TestHealResultConstruction:
    def test_happy_path(self):
        r = HealResult(
            outcome=HealOutcome.SUCCESS,
            reason_code="retry_ok",
            parent_packet_id="pkt-1",
            repair_count=1,
            policy_hash="pol",
            blueprint_hash="bp",
        )
        assert r.outcome == HealOutcome.SUCCESS
        assert r.repair_count == 1

    def test_string_outcome_coerces(self):
        r = HealResult(
            outcome="FAIL_TERMINAL",
            reason_code="x",
            parent_packet_id="p",
            repair_count=0,
            policy_hash="pol",
            blueprint_hash="bp",
        )
        assert r.outcome == HealOutcome.FAIL_TERMINAL

    def test_invalid_outcome_raises(self):
        with pytest.raises(ValueError):
            HealResult(
                outcome="BOGUS",
                reason_code="x",
                parent_packet_id="p",
                repair_count=0,
                policy_hash="pol",
                blueprint_hash="bp",
            )

    def test_empty_reason_raises(self):
        with pytest.raises(ValueError, match="reason_code"):
            HealResult(
                outcome=HealOutcome.SUCCESS,
                reason_code="",
                parent_packet_id="p",
                repair_count=0,
                policy_hash="pol",
                blueprint_hash="bp",
            )

    def test_empty_parent_packet_raises(self):
        with pytest.raises(ValueError, match="parent_packet_id"):
            HealResult(
                outcome=HealOutcome.SUCCESS,
                reason_code="ok",
                parent_packet_id="",
                repair_count=0,
                policy_hash="pol",
                blueprint_hash="bp",
            )

    def test_negative_repair_count_raises(self):
        with pytest.raises(ValueError, match="repair_count"):
            HealResult(
                outcome=HealOutcome.SUCCESS,
                reason_code="x",
                parent_packet_id="p",
                repair_count=-1,
                policy_hash="pol",
                blueprint_hash="bp",
            )

    def test_missing_snapshot_hashes_raises(self):
        with pytest.raises(ValueError, match="snapshot"):
            HealResult(
                outcome=HealOutcome.SUCCESS,
                reason_code="x",
                parent_packet_id="p",
                repair_count=0,
                policy_hash="",
                blueprint_hash="bp",
            )

    def test_is_frozen(self):
        r = HealResult(
            outcome=HealOutcome.SUCCESS,
            reason_code="ok",
            parent_packet_id="p",
            repair_count=0,
            policy_hash="pol",
            blueprint_hash="bp",
        )
        with pytest.raises((AttributeError, TypeError)):
            r.outcome = HealOutcome.FAIL_TERMINAL  # type: ignore[misc]


class TestToDict:
    def test_roundtrip_shape(self):
        r = HealResult(
            outcome=HealOutcome.SOFT_REPAIRABLE,
            reason_code="retry_after_backoff",
            parent_packet_id="pkt-9",
            repair_count=2,
            policy_hash="pol-1",
            blueprint_hash="bp-1",
            evidence={"attempts": 2, "last_error": "rate_limit"},
            message="repairable on retry",
        )
        d = r.to_dict()
        assert d["outcome"] == "SOFT_REPAIRABLE"
        assert d["reason_code"] == "retry_after_backoff"
        assert d["parent_packet_id"] == "pkt-9"
        assert d["repair_count"] == 2
        assert d["policy_hash"] == "pol-1"
        assert d["blueprint_hash"] == "bp-1"
        assert d["evidence"] == {"attempts": 2, "last_error": "rate_limit"}
        assert d["message"] == "repairable on retry"

    def test_evidence_is_copied(self):
        original = {"x": 1}
        r = HealResult(
            outcome=HealOutcome.SUCCESS,
            reason_code="ok",
            parent_packet_id="p",
            repair_count=0,
            policy_hash="pol",
            blueprint_hash="bp",
            evidence=original,
        )
        d = r.to_dict()
        d["evidence"]["y"] = 2
        # Internal evidence dict unaffected by external mutation of the returned copy
        assert "y" not in r.evidence


class TestFromRequest:
    def test_inherits_snapshot_binding(self):
        req = _req()
        r = HealResult.from_request(req, HealOutcome.SUCCESS, "repaired")
        assert r.parent_packet_id == "pkt-42"
        assert r.policy_hash == "pol-abc"
        assert r.blueprint_hash == "bp-xyz"
        assert r.outcome == HealOutcome.SUCCESS

    def test_string_outcome_ok(self):
        req = _req()
        r = HealResult.from_request(req, "FAIL_TERMINAL", "unrecoverable")
        assert r.outcome == HealOutcome.FAIL_TERMINAL


class TestNeedsHelp:
    def test_factory_builds_valid_result(self):
        r = HealResult.needs_help(
            parent_packet_id="pkt-1",
            policy_hash="pol",
            blueprint_hash="bp",
            reason_code="not_implemented",
            message="stub",
        )
        assert r.outcome == HealOutcome.NEEDS_HELP
        assert r.repair_count == 0
        assert r.reason_code == "not_implemented"

    def test_factory_defaults_to_not_implemented(self):
        r = HealResult.needs_help(
            parent_packet_id="pkt-1",
            policy_hash="pol",
            blueprint_hash="bp",
        )
        assert r.reason_code == "not_implemented"

    def test_factory_tolerates_missing_parent_id(self):
        r = HealResult.needs_help(
            parent_packet_id="",
            policy_hash="pol",
            blueprint_hash="bp",
        )
        assert r.parent_packet_id == "unknown"
