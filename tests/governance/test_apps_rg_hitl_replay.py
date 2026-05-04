"""W7 HITL sentinel — decision_hash round-trip and replay_key binding.

Verifies:
1. decision_hash = sha256(decision_id + chosen_option_id + input_manifest_hash)
2. HumanReviewDecision.verify_hash() returns True for a correctly built decision.
3. Tampering with any field breaks verify_hash().
4. replay_key on the decision matches the request's replay_key.
5. HITLReplayStore round-trip: append → load → verify_all() clean.

Plan: apps-rg-canonical-wireup-c8a4f2 W7 sentinel.
"""
from __future__ import annotations

import hashlib
import tempfile
import uuid
from pathlib import Path

import pytest

from apps_rg.hitl.hitl_schemas import (
    BoundedOption,
    HumanReviewDecision,
    RuntimeAuthorGateDecisionRequest,
    make_decision_request,
)
from apps_rg.hitl.hitl_replay_store import HITLReplayStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_request(replay_key: str = "rk-test-001") -> RuntimeAuthorGateDecisionRequest:
    return make_decision_request(
        trigger_kind="LOW_CONFIDENCE",
        run_id="run-test-001",
        input_manifest_hash="abc123",
        recommendations=["Increase evidence coverage"],
        confidence_score=0.45,
        evidence_refs=["artifacts/run-001/resume_draft.md"],
        bounded_options=[
            BoundedOption("APPROVE_RELEASE", "Approve", "Exits ALLOW", is_recommended=False),
            BoundedOption("REJECT_RELEASE", "Reject", "Exits DENY", is_recommended=True),
        ],
        replay_key=replay_key,
    )


def _make_decision(request: RuntimeAuthorGateDecisionRequest, chosen: str = "REJECT_RELEASE") -> HumanReviewDecision:
    decision_id = str(uuid.uuid4())
    decision_hash = HumanReviewDecision.compute_hash(
        decision_id, chosen, request.input_manifest_hash
    )
    return HumanReviewDecision(
        decision_id=decision_id,
        request_id=request.request_id,
        chosen_option_id=chosen,
        decision_timestamp="2026-05-04T12:00:00+00:00",
        input_manifest_hash=request.input_manifest_hash,
        decision_hash=decision_hash,
        replay_key=request.replay_key,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_rg_hitl_decision_hash_correct() -> None:
    """decision_hash must equal sha256(decision_id + chosen_option_id + input_manifest_hash)."""
    request = _make_request()
    decision = _make_decision(request)

    expected = hashlib.sha256(
        (decision.decision_id + decision.chosen_option_id + decision.input_manifest_hash).encode()
    ).hexdigest()
    assert decision.decision_hash == expected


@pytest.mark.governance
def test_apps_rg_hitl_verify_hash_passes_for_valid_decision() -> None:
    """HumanReviewDecision.verify_hash() must return True for a correctly built decision."""
    request = _make_request()
    decision = _make_decision(request)
    assert decision.verify_hash() is True


@pytest.mark.governance
def test_apps_rg_hitl_verify_hash_fails_on_tampered_chosen_option() -> None:
    """Tampering with chosen_option_id must break verify_hash()."""
    request = _make_request()
    decision = _make_decision(request, chosen="REJECT_RELEASE")
    from dataclasses import replace
    tampered = replace(decision, chosen_option_id="APPROVE_RELEASE")
    assert tampered.verify_hash() is False


@pytest.mark.governance
def test_apps_rg_hitl_replay_key_matches_request() -> None:
    """Decision replay_key must equal the request's replay_key."""
    replay_key = "rk-canonical-001"
    request = _make_request(replay_key=replay_key)
    decision = _make_decision(request)
    assert decision.replay_key == replay_key


@pytest.mark.governance
def test_apps_rg_hitl_replay_store_round_trip(tmp_path: Path) -> None:
    """HITLReplayStore: append → load → verify_all returns no errors."""
    store = HITLReplayStore(tmp_path)
    request = _make_request()
    decision = _make_decision(request)

    store.append(decision)
    rows = store.load_all()
    assert len(rows) == 1
    assert rows[0]["decision_id"] == decision.decision_id
    assert rows[0]["replay_key"] == decision.replay_key

    errors = store.verify_all()
    assert errors == [], f"Hash verification failed: {errors}"


@pytest.mark.governance
def test_apps_rg_hitl_replay_store_find_by_replay_key(tmp_path: Path) -> None:
    """find_by_replay_key returns the correct row."""
    store = HITLReplayStore(tmp_path)
    request = _make_request(replay_key="rk-find-me")
    decision = _make_decision(request)
    store.append(decision)

    found = store.find_by_replay_key("rk-find-me")
    assert found is not None
    assert found["decision_id"] == decision.decision_id

    not_found = store.find_by_replay_key("rk-nonexistent")
    assert not_found is None
