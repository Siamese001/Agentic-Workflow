"""v5 parity tests — Exit Eval & Control v5 §H4/§L5 RE-CLEARANCE.

Covers the gaps closed by plan ``exit-eval-v5-gap-c0aa47``:

- ``HumanDecision`` carries all 5 v5 outcomes (APPROVE, REJECT,
  MODIFY_DIFF, RETURN_TO_L1, REQUEST_MORE_EVIDENCE) plus DENY back-compat alias.
- ``ReClearOutcome`` carries RECLEAR_RESTART / RETURNED_TO_L1 /
  MORE_EVIDENCE_REQUESTED in addition to legacy CLEARED_*/BLOCKED.
- REJECT and DENY both BLOCK and pop the active packet.
- RETURN_TO_L1 produces RETURNED_TO_L1 and pops the packet.
- REQUEST_MORE_EVIDENCE produces MORE_EVIDENCE_REQUESTED and KEEPS the packet.
- MODIFY_DIFF without ``reclear_callback`` still BLOCKS (back-compat).
- MODIFY_DIFF with ``reclear_callback`` produces RECLEAR_RESTART and
  surfaces the re-hydrated artifact.
- MODIFY_DIFF rejects empty / malformed proposed_diff.
- Re-clear callback exception is handled fail-closed (BLOCKED).
"""

from __future__ import annotations

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.exit_control_hitl")

ExitControlHITL = mod.ExitControlHITL
HumanDecision = mod.HumanDecision
HumanReviewInput = mod.HumanReviewInput
ReClearOutcome = mod.ReClearOutcome
AuthorityState = mod.AuthorityState
WriteAuthority = mod.WriteAuthority
BoundedPacket = mod.BoundedPacket


# --------------------------------------------------------------------------- #
# Lightweight fixtures
# --------------------------------------------------------------------------- #


class _StubGateResult:
    """Minimal gate-result shape consumed by ``freeze_and_materialize``."""

    def __init__(self, trace_id: str = "trace-v5", reason: str = "stub-escalation") -> None:
        self._trace_id = trace_id
        self._reason = reason

    def to_dict(self) -> dict:
        return {"trace_id": self._trace_id, "reason": self._reason}


@pytest.fixture()
def hitl():
    return ExitControlHITL()


@pytest.fixture()
def hitl_with_callback():
    """Return an HITL instance whose reclear_callback records calls."""
    calls: list = []

    def _callback(artifact: dict, human_input):  # noqa: ANN001 — duck-typed
        calls.append((dict(artifact), human_input))
        merged = {**artifact, "applied_diff": dict(human_input.proposed_diff or {})}
        return merged

    return ExitControlHITL(reclear_callback=_callback), calls


@pytest.fixture()
def packet(hitl):
    sealed = {"foo": "bar", "raw_content": "should-be-stripped"}
    return hitl.freeze_and_materialize(_StubGateResult(), sealed)


@pytest.fixture()
def packet_cb(hitl_with_callback):
    hitl, _ = hitl_with_callback
    sealed = {"foo": "bar", "has_commit_payload": False}
    return hitl.freeze_and_materialize(_StubGateResult(trace_id="trace-cb"), sealed)


# --------------------------------------------------------------------------- #
# Enum parity
# --------------------------------------------------------------------------- #


def test_human_decision_v5_parity():
    """v5 §H4 enumerates APPROVE/MODIFY_DIFF/REJECT/RETURN_TO_L1/REQUEST_MORE_EVIDENCE."""
    expected = {"APPROVE", "REJECT", "MODIFY_DIFF", "RETURN_TO_L1", "REQUEST_MORE_EVIDENCE"}
    actual = {m.value for m in HumanDecision}
    assert expected.issubset(actual), f"missing v5 decisions: {expected - actual}"


def test_human_decision_deny_backcompat_alias():
    assert HumanDecision.DENY.value == "DENY"
    # REJECT must coexist as the canonical v5 name.
    assert HumanDecision.REJECT.value == "REJECT"


def test_reclear_outcome_v5_outcomes_present():
    expected = {
        "CLEARED_ALLOW",
        "CLEARED_COMMIT",
        "RECLEAR_RESTART",
        "RETURNED_TO_L1",
        "MORE_EVIDENCE_REQUESTED",
        "BLOCKED",
    }
    actual = {m.value for m in ReClearOutcome}
    assert expected == actual, f"outcome enum drift: missing={expected - actual}, extra={actual - expected}"


# --------------------------------------------------------------------------- #
# REJECT / DENY → BLOCKED + packet popped
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("decision", [HumanDecision.REJECT, HumanDecision.DENY])
def test_reject_or_deny_blocks_and_pops_packet(hitl, packet, decision):
    h = HumanReviewInput(
        packet_id=packet.packet_id,
        decision=decision,
        reviewer_id="alice",
        justification="not aligned with policy",
    )
    result = hitl.validate_and_reclear(h, packet)
    assert result.outcome is ReClearOutcome.BLOCKED
    assert "rejected clearance" in result.reason
    # Packet must be removed from active set so a stale resubmit cannot re-enter H5.
    assert packet.packet_id not in hitl._active_packets  # pylint: disable=protected-access


# --------------------------------------------------------------------------- #
# RETURN_TO_L1
# --------------------------------------------------------------------------- #


def test_return_to_l1_produces_returned_outcome_and_pops_packet(hitl, packet):
    h = HumanReviewInput(
        packet_id=packet.packet_id,
        decision=HumanDecision.RETURN_TO_L1,
        reviewer_id="bob",
        justification="plan needs re-routing",
    )
    result = hitl.validate_and_reclear(h, packet)
    assert result.outcome is ReClearOutcome.RETURNED_TO_L1
    assert "replan" in result.reason
    assert packet.packet_id not in hitl._active_packets  # pylint: disable=protected-access


# --------------------------------------------------------------------------- #
# REQUEST_MORE_EVIDENCE
# --------------------------------------------------------------------------- #


def test_request_more_evidence_keeps_packet_active(hitl, packet):
    h = HumanReviewInput(
        packet_id=packet.packet_id,
        decision=HumanDecision.REQUEST_MORE_EVIDENCE,
        reviewer_id="carol",
        justification="citations are weak; need stronger support",
    )
    result = hitl.validate_and_reclear(h, packet)
    assert result.outcome is ReClearOutcome.MORE_EVIDENCE_REQUESTED
    # Bounded re-entry: packet stays active so a follow-up review can land.
    assert packet.packet_id in hitl._active_packets  # pylint: disable=protected-access


# --------------------------------------------------------------------------- #
# MODIFY_DIFF
# --------------------------------------------------------------------------- #


def test_modify_diff_blocked_when_no_callback_wired(hitl, packet):
    h = HumanReviewInput(
        packet_id=packet.packet_id,
        decision=HumanDecision.MODIFY_DIFF,
        reviewer_id="dave",
        justification="apply patch X",
        proposed_diff={"field": "new"},
    )
    result = hitl.validate_and_reclear(h, packet)
    assert result.outcome is ReClearOutcome.BLOCKED
    assert "reclear_callback" in result.reason
    assert packet.packet_id not in hitl._active_packets  # pylint: disable=protected-access


def test_modify_diff_blocked_when_diff_missing(hitl_with_callback, packet_cb):
    hitl, _ = hitl_with_callback
    h = HumanReviewInput(
        packet_id=packet_cb.packet_id,
        decision=HumanDecision.MODIFY_DIFF,
        reviewer_id="dave",
        justification="apply patch X",
        proposed_diff=None,
    )
    result = hitl.validate_and_reclear(h, packet_cb)
    assert result.outcome is ReClearOutcome.BLOCKED
    assert "non-empty proposed_diff" in result.reason


def test_modify_diff_with_callback_produces_reclear_restart(hitl_with_callback, packet_cb):
    hitl, calls = hitl_with_callback
    h = HumanReviewInput(
        packet_id=packet_cb.packet_id,
        decision=HumanDecision.MODIFY_DIFF,
        reviewer_id="dave",
        justification="apply patch X",
        proposed_diff={"new_field": "v"},
    )
    result = hitl.validate_and_reclear(h, packet_cb)
    assert result.outcome is ReClearOutcome.RECLEAR_RESTART
    # Callback was invoked exactly once with the original artifact summary.
    assert len(calls) == 1
    artifact_arg, human_arg = calls[0]
    assert artifact_arg.get("foo") == "bar"
    assert human_arg.decision is HumanDecision.MODIFY_DIFF
    # Re-hydrated artifact is surfaced for the pipeline to re-run X1A/X1C/X1F on.
    assert result.re_cleared_artifact is not None
    assert result.re_cleared_artifact["applied_diff"] == {"new_field": "v"}
    # Packet popped so a stale resubmit cannot land on a stale packet_id.
    assert packet_cb.packet_id not in hitl._active_packets  # pylint: disable=protected-access


def test_modify_diff_callback_exception_is_blocked_fail_closed():
    """A misbehaving reclear_callback must NEVER produce a passing outcome."""

    def _broken(_artifact, _human):  # noqa: ANN001
        raise ValueError("intentional failure")

    hitl = ExitControlHITL(reclear_callback=_broken)
    sealed = {"foo": "bar"}
    pkt = hitl.freeze_and_materialize(_StubGateResult(trace_id="trace-broken"), sealed)
    h = HumanReviewInput(
        packet_id=pkt.packet_id,
        decision=HumanDecision.MODIFY_DIFF,
        reviewer_id="eve",
        justification="apply patch Y",
        proposed_diff={"k": "v"},
    )
    result = hitl.validate_and_reclear(h, pkt)
    assert result.outcome is ReClearOutcome.BLOCKED
    assert "reclear_callback failed" in result.reason


def test_modify_diff_callback_must_return_mapping():
    def _bad(_artifact, _human):  # noqa: ANN001
        return "not a dict"

    hitl = ExitControlHITL(reclear_callback=_bad)
    sealed = {"foo": "bar"}
    pkt = hitl.freeze_and_materialize(_StubGateResult(trace_id="trace-shape"), sealed)
    h = HumanReviewInput(
        packet_id=pkt.packet_id,
        decision=HumanDecision.MODIFY_DIFF,
        reviewer_id="frank",
        justification="apply patch Z",
        proposed_diff={"k": "v"},
    )
    result = hitl.validate_and_reclear(h, pkt)
    assert result.outcome is ReClearOutcome.BLOCKED
    assert "must return a mapping" in result.reason


# --------------------------------------------------------------------------- #
# Identity / justification gate fires before any decision branch
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "decision",
    [
        HumanDecision.APPROVE,
        HumanDecision.REJECT,
        HumanDecision.RETURN_TO_L1,
        HumanDecision.REQUEST_MORE_EVIDENCE,
        HumanDecision.MODIFY_DIFF,
    ],
)
def test_missing_justification_blocks_every_decision(hitl, packet, decision):
    h = HumanReviewInput(
        packet_id=packet.packet_id,
        decision=decision,
        reviewer_id="alice",
        justification="   ",  # whitespace-only
        proposed_diff={"k": "v"} if decision is HumanDecision.MODIFY_DIFF else None,
    )
    result = hitl.validate_and_reclear(h, packet)
    assert result.outcome is ReClearOutcome.BLOCKED
    assert "justification is missing or empty" in result.reason
