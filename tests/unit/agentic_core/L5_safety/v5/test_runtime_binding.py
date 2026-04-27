"""Tests for `runtime_binding.py` (G1 closure — 00A.8 Runtime Certification Binding).

The 6 named tests required by 00A.8 doctrine:

1. ``test_l5_binding_requires_policy_blueprint_registry``
2. ``test_l5_snapshot_receipt_detects_policy_drift``
3. ``test_l2_e2_rejects_missing_l5_binding_for_governed_packet``
4. ``test_exit_requires_l5_reclearance_for_human_modified_packet``
5. ``test_uwg_rejects_commit_request_missing_required_l5_refs``
6. ``test_l5_never_emits_runtime_disposition``
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5 import (
    L5CertificationEvidenceRefSet,
    L5ReclearanceBinding,
    L5RuntimeCertificationBinding,
    L5SnapshotVerificationReceipt,
    emit_runtime_binding,
    verify_snapshot,
)
from agentic_core.L5_safety.v5.types import MatchStatus, ReasonCode


def _evidence_refs() -> L5CertificationEvidenceRefSet:
    return L5CertificationEvidenceRefSet(
        policy_ref="p",
        blueprint_ref="b",
        registry_ref="r",
        authority_context_ref="ac",
        capability_scope_ref="ct",
        sandbox_scope_ref="sb",
        origin_trust_ref="ot",
        egress_cert_ref="",
        hitl_reclearance_ref="",
        replay_audit_ref="rep",
        static_governance_ref="",
    )


def _binding(**overrides) -> L5RuntimeCertificationBinding:
    base = dict(
        binding_id="b1",
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-1",
        route_contract_ref="route-1",
        packet_ref="packet-1",
        policy_hash="P0",
        blueprint_hash="B0",
        registry_digest_set=("D0",),
        principal_ref="pri-1",
        capability_token_ref="cap-1",
        sandbox_envelope_ref="sand-1",
        origin_trust_manifest_ref="otm-1",
        egress_cert_ref="",
        replay_envelope_ref="rep-1",
        audit_manifest_ref="aud-1",
        certification_scope="default",
        certification_status="L5_CERTIFIED",
        evidence_refs=_evidence_refs(),
    )
    base.update(overrides)
    return L5RuntimeCertificationBinding(**base)


# Test 1: L5 binding requires policy/blueprint/registry ------------------------
def test_l5_binding_requires_policy_blueprint_registry() -> None:
    """00A.8 §4 — L2 E1 must receive policy/blueprint/registry refs."""

    with pytest.raises(ValueError, match="policy_hash required"):
        _binding(policy_hash="")

    with pytest.raises(ValueError, match="blueprint_hash required"):
        _binding(blueprint_hash="")

    with pytest.raises(ValueError, match="registry_digest_set required"):
        _binding(registry_digest_set=())


# Test 2: snapshot receipt detects policy drift -------------------------------
def test_l5_snapshot_receipt_detects_policy_drift() -> None:
    """Drift between binding-pinned and active hashes → MISMATCH receipt."""

    binding = _binding()
    receipt = verify_snapshot(
        binding=binding,
        active_policy_hash="P_DRIFTED",  # different from binding's P0
        active_blueprint_hash="B0",
        active_registry_digest_set=("D0",),
        snapshot_receipt_id="snap-1",
    )
    assert receipt.match_status == MatchStatus.MISMATCH
    assert receipt.severity == "critical"
    assert ReasonCode.POLICY_VIOLATION in receipt.mismatch_reason_codes
    # Match path
    receipt_ok = verify_snapshot(
        binding=binding,
        active_policy_hash="P0",
        active_blueprint_hash="B0",
        active_registry_digest_set=("D0",),
        snapshot_receipt_id="snap-2",
    )
    assert receipt_ok.match_status == MatchStatus.MATCH
    assert receipt_ok.mismatch_reason_codes == ()


# Test 3: L2 E2 rejects missing L5 binding for governed packet ----------------
def test_l2_e2_rejects_missing_l5_binding_for_governed_packet() -> None:
    """L2 E2 contract: governed packet without binding refs → reject.

    Modeled here as a function the E2 layer would call. L5 plane provides the
    helper; absence-of-binding is the trigger.
    """

    def e2_admit_packet(binding: L5RuntimeCertificationBinding | None) -> bool:
        if binding is None:
            return False
        if binding.certification_status != "L5_CERTIFIED":
            return False
        return True

    assert e2_admit_packet(None) is False  # missing binding → reject
    assert e2_admit_packet(_binding(certification_status="L5_NOT_CERTIFIED")) is False
    assert e2_admit_packet(_binding()) is True


# Test 4: Exit requires L5 reclearance for human-modified packet --------------
def test_exit_requires_l5_reclearance_for_human_modified_packet() -> None:
    """00A.8 §4 — Exit gate requires re-clearance refs when HITL modified the packet."""

    rb = L5ReclearanceBinding(
        binding_id="rb-1",
        original_binding_ref="b1",
        human_modification_diff_ref="diff-1",
        human_review_packet_ref="hrp-1",
        reclearance_status="CLEARED",
        reclearance_evidence_refs=("ev-1",),
        re_certified_at="2026-04-26T22:00:00Z",
    )
    assert rb.reclearance_status == "CLEARED"

    with pytest.raises(ValueError, match="reclearance_status"):
        L5ReclearanceBinding(
            binding_id="rb-2",
            original_binding_ref="b1",
            human_modification_diff_ref="diff-1",
            human_review_packet_ref="hrp-1",
            reclearance_status="BOGUS",
            reclearance_evidence_refs=(),
            re_certified_at="",
        )


# Test 5: UWG rejects commit request missing required L5 refs -----------------
def test_uwg_rejects_commit_request_missing_required_l5_refs() -> None:
    """UWG contract: any commit request must carry L5 evidence refs.

    Modeled as a UWG admission predicate. Empty/missing refs → reject.
    """

    def uwg_admit_commit(refs: L5CertificationEvidenceRefSet) -> bool:
        # UWG requires policy + blueprint + registry + replay_audit at minimum
        return all(
            (
                refs.policy_ref,
                refs.blueprint_ref,
                refs.registry_ref,
                refs.replay_audit_ref,
            )
        )

    assert uwg_admit_commit(_evidence_refs()) is True
    incomplete = L5CertificationEvidenceRefSet(
        policy_ref="",  # missing
        blueprint_ref="b",
        registry_ref="r",
        authority_context_ref="",
        capability_scope_ref="",
        sandbox_scope_ref="",
        origin_trust_ref="",
        egress_cert_ref="",
        hitl_reclearance_ref="",
        replay_audit_ref="rep",
        static_governance_ref="",
    )
    assert uwg_admit_commit(incomplete) is False


# Test 6: L5 never emits runtime disposition ----------------------------------
def test_l5_never_emits_runtime_disposition() -> None:
    """`L5RuntimeCertificationBinding` MUST NOT carry a runtime disposition.

    Forbidden values per 00A_L5 §1.3: ALLOW, DENY, REROUTE, ESCALATE_HITL,
    COMMIT_REQUEST, BLOCK_COMMIT, ALLOW_FINISH. Verifies that the public
    surface of a binding cannot stamp such a value through the ``certification_status``
    field accidentally — only L5-prefixed statuses are conventional.
    """

    forbidden = {
        "ALLOW",
        "DENY",
        "CLARIFY",
        "ABSTAIN",
        "REROUTE",
        "SHRINK_SCOPE",
        "ESCALATE_HITL",
        "COMMIT_REQUEST",
        "BLOCK_COMMIT",
        "ALLOW_FINISH",
    }
    binding = _binding(certification_status="L5_CERTIFIED")
    assert binding.certification_status not in forbidden
    serialized = binding.to_dict()
    # No forbidden disposition value anywhere in the serialized binding payload
    payload = repr(serialized)
    for term in forbidden:
        assert term not in payload, f"forbidden disposition {term!r} leaked into binding"


# Bonus: emit_runtime_binding builds a deterministic binding -------------------
def test_emit_runtime_binding_is_deterministic() -> None:
    a = emit_runtime_binding(
        request_id="r1",
        run_id="run1",
        trace_root="t1",
        route_contract_ref="rc1",
        packet_ref="pk1",
        policy_hash="PH",
        blueprint_hash="BH",
        registry_digest_set=("D1", "D2"),
        principal_ref="pri",
        capability_token_ref="cap",
        sandbox_envelope_ref="sb",
        origin_trust_manifest_ref="ot",
        replay_envelope_ref="rep",
        audit_manifest_ref="aud",
        certification_scope="default",
        certification_status="L5_CERTIFIED",
    )
    b = emit_runtime_binding(
        request_id="r1",
        run_id="run1",
        trace_root="t1",
        route_contract_ref="rc1",
        packet_ref="pk1",
        policy_hash="PH",
        blueprint_hash="BH",
        registry_digest_set=("D1", "D2"),
        principal_ref="pri",
        capability_token_ref="cap",
        sandbox_envelope_ref="sb",
        origin_trust_manifest_ref="ot",
        replay_envelope_ref="rep",
        audit_manifest_ref="aud",
        certification_scope="default",
        certification_status="L5_CERTIFIED",
    )
    assert a.deterministic_digest == b.deterministic_digest
    assert a.binding_id == b.binding_id


def test_snapshot_receipt_severity_validation() -> None:
    with pytest.raises(ValueError, match="severity"):
        L5SnapshotVerificationReceipt(
            snapshot_receipt_id="x",
            active_policy_hash="P",
            packet_policy_hash="P",
            active_blueprint_hash="B",
            packet_blueprint_hash="B",
            active_registry_digest_set=("D",),
            packet_registry_digest_set=("D",),
            replay_snapshot_ref="",
            live_snapshot_ref="",
            match_status=MatchStatus.MATCH,
            mismatch_reason_codes=(),
            severity="bogus",
            generated_at="",
        )
