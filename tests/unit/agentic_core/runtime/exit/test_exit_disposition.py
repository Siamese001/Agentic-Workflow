"""Unit tests for agentic_core.runtime.exit.exit_disposition.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 Exit/X3 spine.
``exit_disposition`` (fan_in=15, L_RUNTIME) carries the single X3 disposition code
(exactly one per request) plus the Exit review packet. Frozen/slots dataclasses;
__post_init__ validates the x3_code against the canonical set.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from agentic_core.runtime.exit.exit_disposition import (
    ALL_X3_CODES,
    EXIT_DISPOSITION_SCHEMA_VERSION,
    X3A_DENY_REROUTE,
    X3B_ESCALATE_HITL,
    X3C_COMMIT_REQUEST_TO_UWG,
    X3D_ALLOW_FINISH,
    X3E_SAFE_ABSTAIN,
    ExitDispositionReceipt,
    ExitReviewPacket,
    RuntimeExhaustBundle,
    X2AggregationResult,
)


class TestX3Codes:
    def test_code_string_values(self) -> None:
        assert X3A_DENY_REROUTE == "X3A_DENY_REROUTE"
        assert X3B_ESCALATE_HITL == "X3B_ESCALATE_HITL"
        assert X3C_COMMIT_REQUEST_TO_UWG == "X3C_COMMIT_REQUEST_TO_UWG"
        assert X3D_ALLOW_FINISH == "X3D_ALLOW_FINISH"
        assert X3E_SAFE_ABSTAIN == "X3E_SAFE_ABSTAIN"

    def test_all_codes_set(self) -> None:
        assert ALL_X3_CODES == frozenset({
            X3A_DENY_REROUTE, X3B_ESCALATE_HITL, X3C_COMMIT_REQUEST_TO_UWG,
            X3D_ALLOW_FINISH, X3E_SAFE_ABSTAIN,
        })
        assert len(ALL_X3_CODES) == 5


class TestExitDispositionReceipt:
    def test_defaults_safe_abstain(self) -> None:
        r = ExitDispositionReceipt()
        assert r.x3_code == X3E_SAFE_ABSTAIN
        assert r.required_gates_passed is False
        assert r.hard_fail_count == 0
        assert r.unknown_count == 0
        assert r.decisive_blocker_gate_ids == ()
        assert r.schema_version == EXIT_DISPOSITION_SCHEMA_VERSION

    @pytest.mark.parametrize("code", sorted(ALL_X3_CODES))
    def test_all_valid_codes_accepted(self, code: str) -> None:
        assert ExitDispositionReceipt(x3_code=code).x3_code == code

    @pytest.mark.parametrize("bad", ["X3Z", "ALLOW", "", "x3d_allow_finish"])
    def test_invalid_code_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="invalid x3_code"):
            ExitDispositionReceipt(x3_code=bad)

    def test_exactly_one_property_true_per_code(self) -> None:
        assert ExitDispositionReceipt(x3_code=X3D_ALLOW_FINISH).allows_finish is True
        assert ExitDispositionReceipt(x3_code=X3A_DENY_REROUTE).is_deny is True
        assert ExitDispositionReceipt(x3_code=X3B_ESCALATE_HITL).is_hitl is True
        assert ExitDispositionReceipt(x3_code=X3C_COMMIT_REQUEST_TO_UWG).is_commit is True
        # abstain default: none of the affirmative properties are True
        abstain = ExitDispositionReceipt(x3_code=X3E_SAFE_ABSTAIN)
        assert not any([abstain.allows_finish, abstain.is_deny, abstain.is_hitl, abstain.is_commit])

    def test_as_dict_round_trips_fields(self) -> None:
        r = ExitDispositionReceipt(
            request_id="req-1",
            x3_code=X3D_ALLOW_FINISH,
            decisive_blocker_gate_ids=("G1", "G2"),
            hard_fail_count=2,
        )
        d = r.as_dict()
        assert d["request_id"] == "req-1"
        assert d["x3_code"] == X3D_ALLOW_FINISH
        assert d["decisive_blocker_gate_ids"] == ["G1", "G2"]  # tuple -> list
        assert d["hard_fail_count"] == 2

    def test_as_json_is_valid_json(self) -> None:
        r = ExitDispositionReceipt(x3_code=X3D_ALLOW_FINISH, run_id="run-1")
        assert json.loads(r.as_json()) == r.as_dict()

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            ExitDispositionReceipt().x3_code = X3D_ALLOW_FINISH  # type: ignore[misc]


class TestNestedPackets:
    def test_exit_review_packet_defaults_and_dict(self) -> None:
        p = ExitReviewPacket(request_id="req-1")
        d = p.as_dict()
        assert d["request_id"] == "req-1"
        # nested results render via their own as_dict()
        assert "x1_checkout_result" in d and isinstance(d["x1_checkout_result"], dict)
        assert "x2_aggregation_result" in d and isinstance(d["x2_aggregation_result"], dict)

    def test_x2_aggregation_defaults(self) -> None:
        x2 = X2AggregationResult()
        assert x2.evidence_quality_score == 0.0
        assert x2.gate_verdicts == {}
        assert x2.as_dict()["evidence_quality_score"] == 0.0

    def test_runtime_exhaust_bundle_created_after_exit(self) -> None:
        b = RuntimeExhaustBundle(run_id="run-1")
        assert b.created_after_exit is True
        assert b.writeback_candidates == []
        assert b.as_dict()["run_id"] == "run-1"
