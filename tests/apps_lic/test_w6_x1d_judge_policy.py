import json
from pathlib import Path

import yaml

from apps_lic.engines.e2e_acceptance import ACCEPTANCE_MODE_STRICT_TARGET_FIT
from apps_lic.engines.governed_opportunity_ingestion import (
    WRITE_AUTHORITY_GOVERNED_INGESTION,
    InMemoryOpportunityFactStore,
    OpportunityIngestionInput,
    run_governed_opportunity_ingestion,
)
from apps_lic.engines.message_type_requirement_gate import evaluate_message_requirements_from_store
from apps_lic.engines.recipient_classification import derive_recipient_class_from_store
from apps_lic.engines.sender_proof_graph import build_sender_proof_graph_packet_from_store
from apps_lic.engines.validation_exit import (
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    EXIT_BLOCKED,
    JUDGE_CEO_EVIDENCE_RISK,
    JUDGE_CEO_ORIGINALITY,
    JUDGE_EVIDENCE_SUPPORT,
    JUDGE_LINKEDIN_TONE,
    JUDGE_LINKEDIN_TONE_NON_GENERIC,
    MODIFIER_PROVIDER_BACKED_GENERATION,
    MODIFIER_SIMILARITY_GATE_FLAGGED,
    STATUS_X1D_BLOCKED,
    X1DJudgeResult,
    required_x1d_judge_ids_for_context,
    required_x1d_profiles,
    run_validation_exit,
    x1d_judge_profile_policy,
)
from apps_lic.engines.whole_message_generation import (
    build_whole_message_generation_request_from_store,
    generate_whole_message_candidates,
)
from apps_lic.engines.x1d_preflight import X1D_MODE_FAKE, X1D_MODE_LIVE
from scripts.apps_lic.run_aig_30_profile_e2e import run_aig_30_profile_e2e


REPO_ROOT = Path(__file__).resolve().parents[2]
W7_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "validation_exit.v1.yaml"
)
NORMALIZED_RESULT_KEYS = {
    "judge_id",
    "model",
    "provider",
    "score",
    "threshold",
    "passed",
    "availability_status",
    "independence_status",
    "transport_provenance",
    "transport_provider",
    "transport_call_id",
    "raw_response_digest",
    "issues",
    "required_repairs",
    "clearance",
}


def _store_for(
    *,
    title: str,
    jd: object | None = None,
    company_trigger: object | None = None,
) -> InMemoryOpportunityFactStore:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id=f"req-w6-x1d-{title}",
        trace_root="trace-w6-x1d",
        idempotency_key=f"idem-w6-x1d-{title}",
        contact={
            "name": "Jane Target",
            "title": title,
            "headline": title,
            "company": "AIG",
            "linkedin_url": "https://www.linkedin.com/in/jane-target",
        },
        company={"company": "AIG", "context": "Regulated insurer expanding agentic AI."},
        jd=jd,
        company_trigger=company_trigger,
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    return store


def _request(
    store: InMemoryOpportunityFactStore,
    *,
    message_type_hint: str,
    campaign_objective: str,
):
    derivation = derive_recipient_class_from_store(store)
    gate = evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=derivation,
        message_type_hint=message_type_hint,
    )
    proof_packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective=campaign_objective,
        desired_next_step="a quick review",
    )
    return build_whole_message_generation_request_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        sender_proof_packet=proof_packet,
        request_id="req-w6-x1d",
        trace_root="trace-w6-x1d",
        campaign_objective=campaign_objective,
        desired_next_step="a quick review",
    )


def _passing_non_live_judge(judge_id: str) -> X1DJudgeResult:
    return X1DJudgeResult(
        judge_id=judge_id,
        model=DEFAULT_X1D_JUDGE_MODEL,
        provider=DEFAULT_X1D_JUDGE_PROVIDER,
        score=0.96,
        passed=True,
    )


def test_w6_config_declares_recipient_specific_judge_matrix() -> None:
    with W7_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    profiles = config["x1d"]["rubric_profiles"]
    assert "linkedin_tone_non_generic_x1d" in profiles
    assert profiles["linkedin_tone_non_generic_x1d"]["threshold"] == 0.84
    assert profiles[JUDGE_CEO_ORIGINALITY]["rubric_id"] == "apps_lic.x1d.ceo_originality.v1"
    assert profiles[JUDGE_CEO_ORIGINALITY]["threshold"] == 0.88
    assert profiles[JUDGE_CEO_EVIDENCE_RISK]["rubric_id"] == "apps_lic.x1d.ceo_evidence_overclaim.v1"
    assert profiles[JUDGE_CEO_EVIDENCE_RISK]["threshold"] == 0.86
    assert config["risk_matrix"]["hiring_manager_role_specific"]["required_judges"] == [
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE_NON_GENERIC,
    ]
    assert config["risk_matrix"]["hiring_manager_strategic_trigger"]["required_judges"] == [
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE_NON_GENERIC,
    ]
    assert config["risk_matrix"]["executive_vp_eng_trigger"]["required_judges"] == [
        JUDGE_LINKEDIN_TONE,
        JUDGE_EVIDENCE_SUPPORT,
    ]
    assert config["risk_matrix"]["ceo_cto_or_c_level"]["required_judges"] == [
        JUDGE_CEO_ORIGINALITY,
        JUDGE_CEO_EVIDENCE_RISK,
    ]


def test_w6_runtime_judge_profile_policy_matches_domain_contract() -> None:
    with W7_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    configured_profiles = config["x1d"]["rubric_profiles"]
    loaded_profiles = x1d_judge_profile_policy()

    assert set(configured_profiles) <= set(loaded_profiles)
    for judge_id, configured in configured_profiles.items():
        loaded = loaded_profiles[judge_id]
        assert loaded.judge_id == judge_id
        assert loaded.rubric_id == configured["rubric_id"]
        assert loaded.role == configured["role"]
        assert loaded.threshold == configured["threshold"]


def test_w6_required_judge_mapping_by_recipient_class_and_message_type() -> None:
    assert required_x1d_judge_ids_for_context(
        recipient_class="RECRUITER",
        message_type="role_specific",
    ) == (JUDGE_EVIDENCE_SUPPORT,)
    assert required_x1d_judge_ids_for_context(
        recipient_class="RECRUITER",
        message_type="role_specific",
        modifiers={MODIFIER_PROVIDER_BACKED_GENERATION: True},
    ) == (JUDGE_EVIDENCE_SUPPORT, JUDGE_LINKEDIN_TONE_NON_GENERIC)
    assert required_x1d_judge_ids_for_context(
        recipient_class="SENIOR_TA",
        message_type="role_specific",
        modifiers={MODIFIER_SIMILARITY_GATE_FLAGGED: True},
    ) == (JUDGE_EVIDENCE_SUPPORT, JUDGE_LINKEDIN_TONE_NON_GENERIC)
    assert required_x1d_judge_ids_for_context(
        recipient_class="HIRING_MANAGER",
        message_type="role_specific",
    ) == (JUDGE_EVIDENCE_SUPPORT, JUDGE_LINKEDIN_TONE_NON_GENERIC)
    assert required_x1d_judge_ids_for_context(
        recipient_class="CTO",
        message_type="trigger_based_insight",
        proof_ids=("sp_agentic_platform",),
    ) == (JUDGE_CEO_ORIGINALITY, JUDGE_CEO_EVIDENCE_RISK)
    assert required_x1d_judge_ids_for_context(
        recipient_class="EXECUTIVE",
        message_type="trigger_based_insight",
        proof_ids=("sp_platform_commercialization",),
    ) == (JUDGE_LINKEDIN_TONE, JUDGE_EVIDENCE_SUPPORT)
    assert required_x1d_judge_ids_for_context(
        recipient_class="HIRING_MANAGER",
        message_type="trigger_based_insight",
        proof_ids=("sp_platform_commercialization",),
    ) == (JUDGE_EVIDENCE_SUPPORT, JUDGE_LINKEDIN_TONE_NON_GENERIC)
    assert required_x1d_judge_ids_for_context(
        recipient_class="CEO",
        message_type="trigger_based_insight",
    ) == (JUDGE_CEO_ORIGINALITY, JUDGE_CEO_EVIDENCE_RISK)


def test_w6_rescoped_rubrics_defer_metric_grounding_to_deterministic_gate() -> None:
    """W2 (graph-claim-gate-rescope): the two evidence judges are narrowed to the
    NON-metric residual. The graph-SSOT metric gate (corpus-load + draft-level
    GATE_GENERATED_METRIC_GROUNDED) deterministically owns numeric/metric grounding,
    so these LLM judges defer that and focus on what only they can catch.
    """
    profiles = x1d_judge_profile_policy()
    for judge_id in (JUDGE_EVIDENCE_SUPPORT, JUDGE_CEO_EVIDENCE_RISK):
        role = profiles[judge_id].role.lower()
        assert "metric" in role, (judge_id, profiles[judge_id].role)
        assert "do not re-score" in role, (judge_id, profiles[judge_id].role)
    # The re-scope must NOT drop either judge from the policy matrix.
    assert required_x1d_judge_ids_for_context(
        recipient_class="RECRUITER", message_type="role_specific",
    ) == (JUDGE_EVIDENCE_SUPPORT,)
    assert required_x1d_judge_ids_for_context(
        recipient_class="CEO", message_type="trigger_based_insight",
    ) == (JUDGE_CEO_ORIGINALITY, JUDGE_CEO_EVIDENCE_RISK)


def test_w6_request_profiles_report_two_judges_for_hiring_manager_role_specific() -> None:
    request = _request(
        _store_for(
            title="Director of Engineering",
            jd={
                "title": "Director, AI Platforms",
                "requisition_number": "JR-12345",
                "company": "AIG",
                "description": "Build production AI platforms.",
            },
        ),
        message_type_hint="role_specific",
        campaign_objective="Discuss fit for the Director AI Platforms role.",
    )

    profiles = required_x1d_profiles(request)

    assert request.reasoning_policy.x1d_llm_judge_depth == 2
    assert tuple(profile.judge_id for profile in profiles) == (
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE_NON_GENERIC,
    )
    assert {profile.required_for_depth for profile in profiles} == {"two"}


def test_w6_missing_required_judge_blocks_exit_after_x2_passes() -> None:
    request = _request(
        _store_for(
            title="Director of Engineering",
            jd={
                "title": "Director, AI Platforms",
                "requisition_number": "JR-12345",
                "company": "AIG",
                "description": "Build production AI platforms.",
            },
        ),
        message_type_hint="role_specific",
        campaign_objective="Discuss fit for the Director AI Platforms role.",
    )
    batch = generate_whole_message_candidates(request)
    selected = batch.candidates[0]

    bundle = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(_passing_non_live_judge(JUDGE_EVIDENCE_SUPPORT),),
    )

    assert bundle.disposition == EXIT_BLOCKED
    assert bundle.x1d_result.status == STATUS_X1D_BLOCKED
    assert bundle.x1d_result.missing_judge_ids == (JUDGE_LINKEDIN_TONE_NON_GENERIC,)
    assert f"missing_required_judge:{JUDGE_LINKEDIN_TONE_NON_GENERIC}" in bundle.x1d_result.reason_codes


def test_w6_wrong_model_and_provider_fail_required_judge_gate() -> None:
    request = _request(
        _store_for(
            title="Senior Technical Recruiter",
            jd={
                "title": "Director, AI Platforms",
                "requisition_number": "JR-12345",
                "company": "AIG",
                "description": "Build production AI platforms.",
            },
        ),
        message_type_hint="role_specific",
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
    )
    batch = generate_whole_message_candidates(request)
    selected = batch.candidates[0]

    bundle = run_validation_exit(
        request,
        batch,
        selected_candidate_id=selected.candidate_id,
        judge_results=(
            X1DJudgeResult(
                judge_id=JUDGE_EVIDENCE_SUPPORT,
                model="Claude Haiku",
                provider="anthropic",
                score=0.99,
                passed=True,
            ),
        ),
    )

    assert bundle.disposition == EXIT_BLOCKED
    assert f"wrong_judge_model:{JUDGE_EVIDENCE_SUPPORT}" in bundle.x1d_result.reason_codes
    assert f"wrong_judge_provider:{JUDGE_EVIDENCE_SUPPORT}" in bundle.x1d_result.reason_codes


def test_w6_aig_30_runner_has_required_receipts_for_every_clear_draft(tmp_path: Path) -> None:
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=tmp_path,
    )
    summary = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    results = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    judges = json.loads((tmp_path / "judge_receipts.json").read_text(encoding="utf-8"))

    assert summary["judge_policy_passed"] is True
    assert summary["judge_policy"]["all_clear_drafts_have_required_receipts"] is True
    assert summary["judge_policy"]["ceo_c_level_all_have_two_judges"] is True
    assert summary["judge_policy"]["missing_required_judge_receipts"] == []
    assert summary["judge_policy"]["required_judge_count"] == judges["receipt_count"]

    rows_by_id = {row["id"]: row for row in results["rows"]}
    assert rows_by_id["mayowa_l"]["x1d_required_judges"] == [
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE_NON_GENERIC,
    ]
    assert rows_by_id["wali_butt"]["x1d_required_judges"] == [
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE_NON_GENERIC,
    ]
    assert rows_by_id["jon_hancock"]["x1d_required_judges"] == [
        JUDGE_CEO_ORIGINALITY,
        JUDGE_CEO_EVIDENCE_RISK,
    ]


def test_w6_fake_and_live_fixture_modes_share_normalized_receipt_contract(tmp_path: Path) -> None:
    fake_dir = tmp_path / "fake"
    live_dir = tmp_path / "live"
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_FAKE,
        output_dir=fake_dir,
    )
    run_aig_30_profile_e2e(
        mode=ACCEPTANCE_MODE_STRICT_TARGET_FIT,
        x1d_mode=X1D_MODE_LIVE,
        output_dir=live_dir,
    )
    fake_receipts = json.loads((fake_dir / "judge_receipts.json").read_text(encoding="utf-8"))["receipts"]
    live_receipts = json.loads((live_dir / "judge_receipts.json").read_text(encoding="utf-8"))["receipts"]

    assert fake_receipts
    assert live_receipts
    assert NORMALIZED_RESULT_KEYS <= set(fake_receipts[0]["normalized_result_contract"])
    assert NORMALIZED_RESULT_KEYS <= set(live_receipts[0]["normalized_result_contract"])
    assert fake_receipts[0]["live_claude_proof"] is False
    assert live_receipts[0]["live_claude_proof"] is False
