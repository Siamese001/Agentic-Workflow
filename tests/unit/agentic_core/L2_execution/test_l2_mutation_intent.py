"""Tests for spec 04.9 L2 StateDiff Candidate & Mutation Intent.

Spec source: docs/reference/04_L2_Execute/04.9_L2_StateDiffCandidate_and_Mutation_Intent.md
SUT:         agentic_core/L2_execution/types/l2_mutation_intent.py
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.l2_mutation_intent import (
    CandidateKind,
    MutationIntentClass,
    MutationIntentDetectionReceipt,
    MutationSourceStage,
    ProposedStateDiffCandidate,
    SchemaValidationStatus,
    StateDiffCandidateManifest,
    WRITE_AUTH_NONE_INSIDE_L2,
)


def _detection(**overrides: object) -> MutationIntentDetectionReceipt:
    base = dict(
        detection_receipt_id="det-1",
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-1",
        source_stage=MutationSourceStage.E3_EXEC,
        mutation_detected=True,
        mutation_intent_class=MutationIntentClass.SANDBOX_ARTIFACT,
        side_effect_class="sandbox_write",
        irreversible_risk=False,
        high_impact_risk=False,
        policy_hash="ph",
        blueprint_hash="bh",
        replay_key="rk",
        deterministic_digest="dig",
    )
    base.update(overrides)
    return MutationIntentDetectionReceipt(**base)  # type: ignore[arg-type]


def _candidate(**overrides: object) -> ProposedStateDiffCandidate:
    base = dict(
        candidate_id="cand-1",
        candidate_kind=CandidateKind.JSON_PATCH,
        target_surface_hint="cache:user_profile",
        target_object_ref="obj-1",
        after_candidate_ref="after-1",
        diff_payload_ref="payload-1",
        diff_payload_hash="hash-1",
        schema_ref="schema-1",
        schema_validation_status=SchemaValidationStatus.LOCALLY_VALID,
        route_contract_ref="route-1",
        l2_authority_ref="auth-1",
        capability_token_ref="cap-1",
        sandbox_envelope_ref="sb-1",
        blast_radius_hint="single_record",
        policy_hash="ph",
        blueprint_hash="bh",
        replay_key="rk",
        trace_root="trace-1",
        deterministic_digest="dig",
    )
    base.update(overrides)
    return ProposedStateDiffCandidate(**base)  # type: ignore[arg-type]


def _manifest(refs: tuple[str, ...] = ("cand-1",)) -> StateDiffCandidateManifest:
    return StateDiffCandidateManifest(
        manifest_id="mani-1",
        candidate_count=len(refs),
        total_payload_hash="thash",
        local_validation_summary="ok",
        forbidden_direct_write_check=True,
        exit_handoff_eligibility_hint="eligible",
        sealed_l2_artifact_ref="seal-1",
        proposed_state_diff_candidate_refs=refs,
    )


# ---------------------------------- spec 04.9 §TEST REQUIREMENTS (8 entries)
def test_l2_detects_mutation_intent() -> None:
    """Detection receipt distinguishes mutation_detected vs intent_class consistency."""
    r = _detection()
    assert r.mutation_detected is True
    assert r.mutation_intent_class is MutationIntentClass.SANDBOX_ARTIFACT
    # mutation_detected=True with NONE class is invalid
    with pytest.raises(ValueError, match="inconsistent"):
        _detection(mutation_intent_class=MutationIntentClass.NONE)
    # mutation_detected=False with non-NONE is invalid
    with pytest.raises(ValueError, match="NONE"):
        _detection(
            mutation_detected=False,
            mutation_intent_class=MutationIntentClass.CACHE_CANDIDATE,
        )


def test_l2_state_diff_candidate_requires_policy_hash_and_replay_key() -> None:
    """ProposedStateDiffCandidate refuses empty policy_hash / replay_key."""
    for missing in ("policy_hash", "blueprint_hash", "replay_key"):
        with pytest.raises(ValueError, match=missing):
            _candidate(**{missing: ""})


def test_l2_state_diff_candidate_has_write_auth_none_inside_l2() -> None:
    """write_auth_status invariant — must equal sentinel and cannot be overridden."""
    c = _candidate()
    assert c.write_auth_status == WRITE_AUTH_NONE_INSIDE_L2 == "none_inside_l2"
    with pytest.raises(ValueError, match="write_auth_status"):
        _candidate(write_auth_status="full_l4")
    # inert_until_exit_uwg also pinned True.
    assert c.inert_until_exit_uwg is True
    with pytest.raises(ValueError, match="inert_until_exit_uwg"):
        _candidate(inert_until_exit_uwg=False)


def test_l2_blocks_candidate_that_changes_route_contract() -> None:
    """A candidate with empty route_contract_ref (i.e. unbinding) is rejected."""
    with pytest.raises(ValueError, match="route_contract_ref"):
        _candidate(route_contract_ref="")
    # And the existing route binding is preserved on a valid candidate.
    c = _candidate(route_contract_ref="route-original")
    assert c.route_contract_ref == "route-original"
    # Frozen dataclass — cannot mutate route_contract_ref post-construction.
    with pytest.raises((AttributeError, Exception)):
        c.route_contract_ref = "route-different"  # type: ignore[misc]


def test_l2_seals_candidate_manifest_without_commit() -> None:
    """Manifest carries refs, l2_no_commit_assertion=True, and counts match."""
    m = _manifest(refs=("cand-1", "cand-2"))
    assert m.l2_no_commit_assertion is True
    assert m.candidate_count == 2
    # candidate_count mismatch with refs raises.
    with pytest.raises(ValueError, match="candidate_count"):
        StateDiffCandidateManifest(
            manifest_id="mani-2",
            candidate_count=3,
            total_payload_hash="t",
            local_validation_summary="ok",
            forbidden_direct_write_check=True,
            exit_handoff_eligibility_hint="eligible",
            sealed_l2_artifact_ref="seal-1",
            proposed_state_diff_candidate_refs=("a", "b"),
        )


def test_l2_never_emits_commit_request() -> None:
    """No field on these contracts can be mistaken for a commit request."""
    for cls in (
        ProposedStateDiffCandidate,
        StateDiffCandidateManifest,
        MutationIntentDetectionReceipt,
    ):
        forbidden = {"commit_request", "uwg_commit", "x1j_disposition", "write_token"}
        assert forbidden.isdisjoint(cls.__dataclass_fields__)


def test_exit_can_consume_l2_candidate_manifest() -> None:
    """Manifest exposes exit_handoff_eligibility_hint and refs Exit can iterate."""
    m = _manifest(refs=("cand-1", "cand-2"))
    assert m.exit_handoff_eligibility_hint == "eligible"
    assert isinstance(m.proposed_state_diff_candidate_refs, tuple)
    assert "cand-1" in m.proposed_state_diff_candidate_refs


def test_uwg_rejects_candidate_without_exit_commit_request() -> None:
    """Contract surface: candidate carries no commit token, so any UWG path
    that requires one will reject. We assert the absence of any commit-shaped
    attribute on the candidate."""
    c = _candidate()
    forbidden = {"commit_request", "uwg_token", "write_grant", "commit_signature"}
    actual = set(ProposedStateDiffCandidate.__dataclass_fields__)
    assert forbidden.isdisjoint(actual)
    assert c.write_auth_status == WRITE_AUTH_NONE_INSIDE_L2
