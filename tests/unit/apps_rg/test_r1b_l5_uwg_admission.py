"""Fail-closed R1B UWG admission tests for L5 packet evidence."""

from __future__ import annotations

from apps_rg.cache.r1b_models import HistoricalIntentRecord
from apps_rg.cache.r1b_uwg_promotion import (
    R1BCachePromotionCandidate,
    build_r1b_commit_bundle,
)
from apps_rg.cache.r1b_uwg_receipt_contract import validate_commit_request_governance
from apps_rg.runtime.l5.packet_builder import compute_l5_packet_verification_digest


def _record() -> HistoricalIntentRecord:
    return HistoricalIntentRecord.from_dict(
        {
            "record_id": "hir_l5_uwg",
            "normalized_intent_digest": "intent-digest",
            "request_intent_text": "apps_rg|role_target_run|acme|svp",
            "request_intent_vector_ref": "vectors/hir_l5_uwg.json",
            "target_company": "Acme",
            "target_role": "SVP",
            "cache_admissible": True,
            "prompt_profile_hash": "policy-v1",
            "gate_profile_hash": "blueprint-v1",
            "source_run_id": "run-l5-uwg",
            "jd_digest": "jd",
            "briefing_digest": "brief",
            "srfs_digest": "",
            "proof_pool_digest": "",
            "skills_ledger_digest": "",
            "base_resume_digest": "resume",
            "final_resume_digest": "",
            "model_profile_hash": "",
            "x3_disposition": "X3_ALLOW",
            "proof_eligible": True,
            "generated_at_utc": "2026-07-12T00:00:00+00:00",
            "job_family": "",
        }
    )


def _candidate(**overrides: object) -> R1BCachePromotionCandidate:
    packet_digest = "d" * 64
    binding_digest = "b" * 64
    packet_ref = f"l5_packet:{packet_digest}"
    values = {
        "record": _record(),
        "chunks": [],
        "post_exit_eligibility": {"admissible": True},
        "source_run_id": "run-l5-uwg",
        "request_id": "req-l5-uwg",
        "trace_root": "trace-l5-uwg",
        "tenant_id": "apps_rg",
        "policy_hash": "policy-v1",
        "blueprint_hash": "blueprint-v1",
        "cleared_exit_review_packet_ref": "exit:verified",
        "x3_disposition_ref": "x3_disposition.json",
        "proof_eligibility_ref": "run_manifest.json",
        "l5_certification_packet_digest": packet_digest,
        "l5_certification_packet_ref": packet_ref,
        "l5_certification_status": "L5_CERTIFIED",
        "l5_runtime_binding_digest": binding_digest,
        "l5_certification_verified": True,
        "l5_certification_verification_digest": compute_l5_packet_verification_digest(
            request_id="req-l5-uwg",
            run_id="run-l5-uwg",
            trace_id="trace-l5-uwg",
            packet_ref=packet_ref,
            packet_digest=packet_digest,
            status="L5_CERTIFIED",
            runtime_binding_digest_value=binding_digest,
        ),
        "replay_refs": ("replay:1",),
        "audit_refs": ("audit:1",),
    }
    values.update(overrides)
    return R1BCachePromotionCandidate(**values)


def test_verified_packet_evidence_is_accepted_by_pre_uwg_validation() -> None:
    commit_request, _state_diffs, _rollback, _refresh = build_r1b_commit_bundle(
        _candidate()
    )

    result = validate_commit_request_governance(commit_request)

    assert result.valid is True, result.to_dict()
    assert commit_request.l5_certification_ref == "l5_packet:" + "d" * 64


def test_missing_packet_evidence_blocks_before_uwg_commit() -> None:
    candidate = _candidate(
        l5_certification_packet_digest="",
        l5_certification_packet_ref="",
        l5_certification_status="",
        l5_runtime_binding_digest="",
        l5_certification_verified=False,
        l5_certification_verification_digest="",
    )
    commit_request, _state_diffs, _rollback, _refresh = build_r1b_commit_bundle(
        candidate
    )

    result = validate_commit_request_governance(commit_request)

    assert result.valid is False
    assert "l5_packet_not_verified_by_exit" in result.reason_codes
    assert "l5_packet_not_certified" in result.reason_codes


def test_forged_verification_digest_blocks() -> None:
    commit_request, _state_diffs, _rollback, _refresh = build_r1b_commit_bundle(
        _candidate(l5_certification_verification_digest="f" * 64)
    )

    result = validate_commit_request_governance(commit_request)

    assert result.valid is False
    assert "l5_verification_digest_mismatch" in result.reason_codes


def test_commit_signature_is_bound_to_l5_verification() -> None:
    commit_request, _state_diffs, _rollback, _refresh = build_r1b_commit_bundle(
        _candidate()
    )
    refs = tuple(
        "verification_digest=" + "e" * 64
        if str(ref).startswith("verification_digest=")
        else ref
        for ref in commit_request.l5_certification_refs
    )
    object.__setattr__(commit_request, "l5_certification_refs", refs)

    result = validate_commit_request_governance(commit_request)

    assert result.valid is False
    assert "commit_request_signature_l5_binding_mismatch" in result.reason_codes
