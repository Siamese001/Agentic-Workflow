"""Tests for v6 §X3C UWG U1-U5 sub-flow."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6 import (
    UwgBackends,
    UwgOutcome,
    aggregate_decision,
    build_x3c_commit_request,
    default_backends,
    process_commit_request,
    run_all_x1_gates,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    V6Disposition,
    X3CommitRequestPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.uwg import (
    BlastRadiusExceeded,
    CapabilityRejected,
    CatalogConflict,
    InMemoryCatalog,
    InMemoryLedger,
    InMemoryLockStore,
    InvalidSignature,
    NoopReadSurfaceRefresher,
    PolicyMismatch,
    RbacDenied,
    WriteLockConflict,
    check_catalog,
    claim_write_lock,
    commit_and_append,
    refresh_read_surfaces,
    verify_boss,
)

from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import base_packet


def _commit_packet(**overrides) -> X3CommitRequestPacket:
    """Build a commit-request packet against a clean exit packet."""
    p = base_packet(
        terminal_class="with_state_diff",
        write_intent_class="user_data_update",
        state_diff={
            "complete": True,
            "bounded": True,
            "blast_radius": "low",
            "uwg_routed": True,
            "before_snapshot": {"v": 1},
            "after_proposed_snapshot": {"v": 2},
            "rollback_plan": {"steps": ["restore"]},
        },
        capability_token={"authorizes_write": True, "expired": False},
        grader_composition={
            "roster": ["x"],
            "threshold_profile": "p",
            "consistency": {"pass_power_estimate": 0.98, "theta": 0.95, "sample_quality": "ok"},
        },
        **overrides,
    )
    verdicts = run_all_x1_gates(p)
    decision = aggregate_decision(verdicts, p)
    assert decision.disposition is V6Disposition.COMMIT_REQUEST
    return build_x3c_commit_request(p, decision)


# ---- U1 verify_boss ----


def test_u1_rejects_missing_hmac() -> None:
    packet = _commit_packet()
    packet.hmac_sig = ""
    with pytest.raises(InvalidSignature):
        verify_boss(packet)


def test_u1_rejects_missing_policy_hash() -> None:
    packet = _commit_packet()
    packet.policy_hash = ""
    with pytest.raises(PolicyMismatch):
        verify_boss(packet)


def test_u1_rejects_expired_capability() -> None:
    packet = _commit_packet()
    packet.capability_token = {"authorizes_write": True, "expired": True}
    with pytest.raises(CapabilityRejected):
        verify_boss(packet)


def test_u1_rejects_widened_capability() -> None:
    packet = _commit_packet()
    packet.capability_token = {"authorizes_write": True, "scope_widened": True}
    with pytest.raises(CapabilityRejected):
        verify_boss(packet)


def test_u1_rejects_capability_without_write_authority() -> None:
    packet = _commit_packet()
    packet.capability_token = {"authorizes_write": False}
    with pytest.raises(CapabilityRejected):
        verify_boss(packet)


def test_u1_detects_policy_drift() -> None:
    packet = _commit_packet()
    packet.route_contract = {**packet.route_contract, "policy_hash": "different-hash"}
    with pytest.raises(PolicyMismatch):
        verify_boss(packet)


def test_u1_passes_clean() -> None:
    packet = _commit_packet()
    verify_boss(packet)  # should not raise


# ---- U2 check_catalog ----


def test_u2_rejects_denied_intent() -> None:
    packet = _commit_packet()
    catalog = InMemoryCatalog(denied_intents=("user_data_update",))
    with pytest.raises(RbacDenied):
        check_catalog(packet, catalog)


def test_u2_detects_pending_conflict() -> None:
    packet = _commit_packet()
    catalog = InMemoryCatalog(pending_intents=("user_data_update",))
    with pytest.raises(CatalogConflict):
        check_catalog(packet, catalog)


def test_u2_irreversible_requires_rollback() -> None:
    packet = _commit_packet()
    packet.blast_radius = "irreversible"
    packet.rollback_plan = {}
    with pytest.raises(BlastRadiusExceeded):
        check_catalog(packet, InMemoryCatalog())


def test_u2_passes_clean() -> None:
    packet = _commit_packet()
    check_catalog(packet, InMemoryCatalog())


# ---- U3 claim_write_lock ----


def test_u3_claims_lock_successfully() -> None:
    packet = _commit_packet()
    store = InMemoryLockStore()
    key = claim_write_lock(packet, store)
    assert key.startswith("uwg::")


def test_u3_raises_on_lock_conflict() -> None:
    packet = _commit_packet()
    store = InMemoryLockStore()
    claim_write_lock(packet, store)
    # Different commit_request_id same intent -> conflict
    packet2 = _commit_packet()
    packet2.commit_request_id = "different"
    with pytest.raises(WriteLockConflict):
        claim_write_lock(packet2, store)


# ---- U4 commit_and_append ----


def test_u4_appends_to_ledger() -> None:
    packet = _commit_packet()
    ledger = InMemoryLedger()
    result = commit_and_append(packet, ledger)
    assert result.seq == 0
    assert len(result.hash_chain_tip) == 64  # sha256 hex


def test_u4_chains_hashes() -> None:
    packet1 = _commit_packet()
    packet2 = _commit_packet()
    packet2.commit_request_id = "crq-2"
    ledger = InMemoryLedger()
    r1 = commit_and_append(packet1, ledger)
    r2 = commit_and_append(packet2, ledger)
    assert r2.seq == 1
    assert r2.hash_chain_tip != r1.hash_chain_tip


# ---- U5 refresh_read_surfaces ----


def test_u5_records_refresh_call() -> None:
    packet = _commit_packet()
    refresher = NoopReadSurfaceRefresher()
    refresh_read_surfaces(packet, refresher, l4_alias="l4://test/0")
    assert refresher.calls == [(packet.commit_request_id, "l4://test/0")]


# ---- end-to-end process_commit_request ----


def test_process_commit_accepts_clean_packet() -> None:
    packet = _commit_packet()
    backends = default_backends()
    receipt = process_commit_request(packet, backends)
    assert receipt.outcome is UwgOutcome.COMMIT_ACCEPTED
    assert receipt.ledger_seq == 0
    assert receipt.l4_alias == "l4://commit/00000000"
    assert "U1_VERIFY_BOSS:ok" in receipt.sub_flow_log
    assert "U5_REFRESH:ok" in receipt.sub_flow_log[-1]


def test_process_commit_rejects_invalid_signature() -> None:
    packet = _commit_packet()
    packet.hmac_sig = ""
    receipt = process_commit_request(packet, default_backends())
    assert receipt.outcome is UwgOutcome.COMMIT_REJECTED
    assert "INVALID_SIGNATURE" in receipt.rejected_reason


def test_process_commit_rejects_rbac_denial() -> None:
    packet = _commit_packet()
    backends = default_backends()
    backends.catalog = InMemoryCatalog(denied_intents=("user_data_update",))
    receipt = process_commit_request(packet, backends)
    assert receipt.outcome is UwgOutcome.COMMIT_REJECTED
    assert "RBAC_DENIED" in receipt.rejected_reason


def test_process_commit_held_on_lock_conflict() -> None:
    packet1 = _commit_packet()
    packet2 = _commit_packet()
    packet2.commit_request_id = "crq-2"
    backends = default_backends()
    receipt1 = process_commit_request(packet1, backends)
    assert receipt1.outcome is UwgOutcome.COMMIT_ACCEPTED
    # Hold the lock by claiming it again first via separate packet against same store
    backends.lock_store.claim(key="uwg::user_data_update", holder="other", ttl_seconds=60)
    receipt2 = process_commit_request(packet2, backends)
    assert receipt2.outcome is UwgOutcome.COMMIT_HELD
    assert "WRITE_LOCK_CONFLICT" in receipt2.rejected_reason


def test_process_commit_releases_lock_after_success() -> None:
    packet1 = _commit_packet()
    packet2 = _commit_packet()
    packet2.commit_request_id = "crq-2"
    backends = default_backends()
    process_commit_request(packet1, backends)
    # Lock should be released so packet2 can acquire it
    receipt2 = process_commit_request(packet2, backends)
    assert receipt2.outcome is UwgOutcome.COMMIT_ACCEPTED


def test_process_commit_two_distinct_intents_concurrent() -> None:
    packet1 = _commit_packet()
    packet2 = _commit_packet()
    packet2.commit_request_id = "crq-2"
    packet2.write_intent_class = "other_class"
    backends = default_backends()
    r1 = process_commit_request(packet1, backends)
    r2 = process_commit_request(packet2, backends)
    assert r1.outcome is UwgOutcome.COMMIT_ACCEPTED
    assert r2.outcome is UwgOutcome.COMMIT_ACCEPTED


def test_uwg_backends_default_factory_independent() -> None:
    a = default_backends()
    b = default_backends()
    assert a.ledger is not b.ledger
    assert a.lock_store is not b.lock_store


def test_uwg_backends_dataclass_fields() -> None:
    backends = default_backends()
    assert isinstance(backends, UwgBackends)
    assert callable(backends.alias_builder)
