from pathlib import Path

import yaml

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY,
    NAMESPACE_JD,
    NAMESPACE_ROLE_OWNERSHIP,
    NAMESPACE_CONTACT,
    WRITE_AUTHORITY_GOVERNED_INGESTION,
    InMemoryOpportunityFactStore,
    OpportunityFactDocument,
    OpportunityIngestionInput,
    run_governed_opportunity_ingestion,
)
from apps_lic.engines.recipient_classification import (
    ALT_GENERAL_INTRO_NO_JD,
    ALT_PEER_NETWORKING_INTRO,
    CLASS_CEO,
    CLASS_CTO,
    CLASS_C_LEVEL,
    CLASS_EXECUTIVE,
    CLASS_HIRING_MANAGER,
    CLASS_RECRUITER,
    CLASS_REFERRAL_CONTACT,
    CLASS_SENIOR_TA,
    CLASS_UNKNOWN,
    CLASS_VP_ENG,
    DRAFT_EXPOSURE_ALLOWED,
    DRAFT_EXPOSURE_BLOCKED,
    MESSAGE_ROLE_SPECIFIC,
    STATUS_CONFLICTED,
    STATUS_DERIVED,
    STATUS_LOW_CONFIDENCE,
    STATUS_MISSING_EVIDENCE,
    TARGET_C0_EVIDENCE_REQUIRED,
    TARGET_ELIGIBLE,
    TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE,
    TARGET_NOT_TARGETABLE,
    derive_recipient_class,
    derive_recipient_class_from_store,
    evaluate_target_eligibility_from_store,
    evaluate_user_visible_draft_exposure,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
W3_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "recipient_classification.v1.yaml"
)


def _store_for_contact(
    *,
    title: str,
    headline: str = "",
    role_ownership: str = "",
    name: str = "Target Person",
) -> InMemoryOpportunityFactStore:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id=f"req-{title}",
        trace_root="trace-w3",
        idempotency_key=f"idem-{title}",
        contact={
            "name": name,
            "title": title,
            "headline": headline,
            "company": "AIG",
            "linkedin_url": f"https://example.com/{name.replace(' ', '-').lower()}",
        },
        role_ownership={"ownership_signal": role_ownership} if role_ownership else None,
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    return store


def _daisuke_store() -> InMemoryOpportunityFactStore:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id="req-daisuke",
        trace_root="trace-w3",
        idempotency_key="idem-daisuke",
        contact={
            "name": "Daisuke Hayashi",
            "title": "Head of Talent Acquisition, AIG Japan",
            "headline": "Head of Talent Acquisition for AIG Japan in Tokyo.",
            "company": "AIG",
            "linkedin_url": "https://example.com/daisuke-hayashi",
        },
        company={"company": "AIG", "context": "AIG enterprise insurance context."},
        jd={
            "title": "VP, Global Head of Agentic AI Solutions",
            "requisition_number": "JR2601998",
            "company": "AIG",
            "location": "NY-New York, NC-Charlotte, GA-Atlanta",
            "description": "Lead agentic AI platforms for US-based regulated workflows.",
        },
        role_ownership={
            "ownership_signal": "Head of Talent Acquisition for AIG Japan in Tokyo.",
            "source_id": "profile:daisuke-role-ownership",
        },
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    return store


def test_w3_config_freezes_c0_authority_and_classes() -> None:
    with W3_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    assert config["authority"] == "C0"
    assert config["u0_policy"]["recipient_class_input"] == "hint_only"
    for recipient_class in (
        CLASS_RECRUITER,
        CLASS_SENIOR_TA,
        CLASS_HIRING_MANAGER,
        CLASS_EXECUTIVE,
        CLASS_C_LEVEL,
        CLASS_CEO,
        CLASS_CTO,
        CLASS_VP_ENG,
        CLASS_REFERRAL_CONTACT,
        CLASS_UNKNOWN,
    ):
        assert recipient_class in config["canonical_classes"]
    assert config["target_eligibility"]["output_values"] == [
        TARGET_ELIGIBLE,
        TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE,
        TARGET_NOT_TARGETABLE,
        TARGET_C0_EVIDENCE_REQUIRED,
    ]
    assert ALT_GENERAL_INTRO_NO_JD in config["target_eligibility"]["alternate_message_modes"]
    assert config["target_eligibility"]["peer_networking_intro_policy"] == "explicitly_allowed_only"
    assert (
        config["target_eligibility"]["no_send_rules"]
        ["blocked_strict_jd_specific_draft_user_visible"]
        is False
    )
    assert (
        config["target_eligibility"]["no_send_rules"]
        ["alternate_general_intro_no_jd_must_omit_jd_reference"]
        is True
    )


def test_recruiter_is_derived_from_contact_title() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(title="Senior Technical Recruiter")
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_RECRUITER
    assert result.recipient_class_confidence >= 0.60
    assert "recruiter_title_signal" in result.class_reason_codes
    assert result.source_snapshot_ids
    assert result.hitl_required is False


def test_senior_ta_is_derived_from_leadership_and_ownership_signals() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(
            title="Global Head of Talent Acquisition",
            role_ownership="Leads recruiting strategy and owns executive hiring programs.",
        )
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_SENIOR_TA
    assert result.recipient_class_confidence >= 0.65
    assert "senior_ta_leadership_title" in result.class_reason_codes


def test_senior_ta_manager_and_leader_titles_are_derived() -> None:
    for title in ("Talent Acquisition Manager", "Talent Acquisition Leader"):
        result = derive_recipient_class_from_store(_store_for_contact(title=title))

        assert result.status == STATUS_DERIVED
        assert result.derived_recipient_class == CLASS_SENIOR_TA
        assert "senior_ta_function_leadership_title" in result.class_reason_codes


def test_talent_acquisition_partner_is_recruiter_not_senior_ta() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(
            title="Senior Talent Acquisition Partner",
            headline="Global Talent Acquisition Partner supporting AIG hiring.",
            role_ownership="Supports recruiting execution for assigned openings.",
        )
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_RECRUITER
    assert "recruiter_partner_signal" in result.class_reason_codes


def test_senior_talent_acquisition_professional_is_recruiter() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(title="Senior Talent Acquisition Professional")
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_RECRUITER
    assert "senior_talent_acquisition_professional_signal" in result.class_reason_codes


def test_negated_role_inventory_does_not_create_false_class_signal() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(
            title="Talent Acquisition Professional",
            headline="Public profile does not expose current ownership scope.",
            role_ownership="No explicit current Head, Manager, Partner, Recruiter, or role owner signal.",
            name="Ambiguous Target",
        )
    )

    assert result.status == STATUS_LOW_CONFIDENCE
    assert result.derived_recipient_class == CLASS_UNKNOWN
    assert "recruiter_title_signal" not in result.class_reason_codes


def test_hiring_manager_is_derived_from_manager_and_owner_signals() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(
            title="Director of AI Platform Engineering",
            role_ownership="Owns hiring for the agentic AI platform team.",
        )
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_HIRING_MANAGER
    assert result.recipient_class_confidence >= 0.60
    assert any(code in result.class_reason_codes for code in ("hiring_manager_leader_signal", "hiring_owner_signal"))


def test_function_heads_are_derived_as_hiring_managers() -> None:
    cases = (
        "Head of eDiscovery & Cyber Investigations",
        "Head of Broker Services and Producer Licensing",
    )

    for title in cases:
        result = derive_recipient_class_from_store(_store_for_contact(title=title))

        assert result.status == STATUS_DERIVED
        assert result.derived_recipient_class == CLASS_HIRING_MANAGER
        assert "hiring_manager_function_head_signal" in result.class_reason_codes


def test_executive_is_derived_without_collapsing_into_c_level() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(title="SVP, Enterprise Transformation")
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_EXECUTIVE
    assert result.derived_recipient_class != CLASS_C_LEVEL


def test_compound_evp_chief_officer_title_derives_c_level() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(
            title="EVP, Chief Digital Officer",
            headline="Chief Digital Officer leading digital, data and GenAI strategy at AIG.",
            role_ownership="Leads digital, data, and GenAI strategy.",
            name="Scott Hallworth",
        )
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_C_LEVEL
    assert "c_level_title_signal" in result.class_reason_codes


def test_c_suite_titles_win_over_generic_evp_or_svp_text() -> None:
    cases = (
        ("EVP, Chief Information Officer", CLASS_C_LEVEL),
        ("EVP, Chief Marketing & Communications Officer", CLASS_C_LEVEL),
        ("Executive Vice President, Chief Risk Officer", CLASS_C_LEVEL),
        ("EVP, Chief Executive Officer, General Insurance", CLASS_CEO),
    )

    for title, expected_class in cases:
        result = derive_recipient_class_from_store(_store_for_contact(title=title))

        assert result.status == STATUS_DERIVED
        assert result.derived_recipient_class == expected_class


def test_ceo_cto_vp_eng_and_c_level_distinctions_are_preserved() -> None:
    cases = [
        ("Chief Executive Officer", CLASS_CEO),
        ("Chief Technology Officer", CLASS_CTO),
        ("Vice President Engineering", CLASS_VP_ENG),
        ("Chief Data Officer", CLASS_C_LEVEL),
    ]

    for title, expected in cases:
        result = derive_recipient_class_from_store(_store_for_contact(title=title))
        assert result.status == STATUS_DERIVED
        assert result.derived_recipient_class == expected


def test_former_or_stale_ceo_evidence_does_not_override_current_executive_chair() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(
            title="Executive Chairman",
            headline=(
                "LinkedIn profile/search result still says Chairman & Chief Executive Officer, "
                "but official AIG page says Executive Chairman as of June 1, 2026."
            ),
            role_ownership="Current official role is Executive Chairman; served as CEO from 2021 to June 1, 2026.",
            name="Peter Zaffino",
        )
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_EXECUTIVE
    assert "executive_chair_signal" in result.class_reason_codes
    assert any("former_or_stale_role_demotion" in code for code in result.class_reason_codes)


def test_formerly_ceo_wording_does_not_override_current_executive_chair() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(
            title="Executive Chairman",
            headline="Executive Chairman of AIG; formerly Chairman & Chief Executive Officer.",
            role_ownership="Current role is Executive Chairman.",
            name="Peter Zaffino",
        )
    )

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_EXECUTIVE
    assert "executive_chair_signal" in result.class_reason_codes


def test_referral_contact_variant_is_available_from_referral_evidence() -> None:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id="req-referral",
        trace_root="trace-w3",
        idempotency_key="idem-referral",
        referral={
            "referrer_name": "Sam Referrer",
            "permission_scope": "may mention Sam as a warm intro",
        },
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )

    result = derive_recipient_class_from_store(store)

    assert result.status == STATUS_DERIVED
    assert result.derived_recipient_class == CLASS_REFERRAL_CONTACT


def test_u0_hint_is_not_used_as_authority() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(title="Business Partner"),
        u0_recipient_class_hint=CLASS_RECRUITER,
    )

    assert result.u0_hint == CLASS_RECRUITER
    assert result.u0_hint_used_as_authority is False
    assert result.status == STATUS_LOW_CONFIDENCE
    assert result.derived_recipient_class == CLASS_UNKNOWN
    assert result.hitl_required is True


def test_ambiguous_talent_business_partner_fails_closed() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(
            title="Talent Partner / Business Partner",
            headline="Supports people operations and workforce planning.",
        )
    )

    assert result.status == STATUS_LOW_CONFIDENCE
    assert result.derived_recipient_class == CLASS_UNKNOWN
    assert result.hitl_required is True
    assert "ambiguous_title_signal" in result.class_reason_codes


def test_conflicting_public_profile_evidence_requires_hitl() -> None:
    docs = (
        OpportunityFactDocument(
            document_id="contact-recruiter",
            namespace=NAMESPACE_CONTACT,
            fact_family="contact",
            fact_text="Jane Target | Senior Technical Recruiter | AIG",
            source_id="profile:recruiter",
            source_type="public_profile",
            source_lineage=("profile:recruiter",),
            freshness_date="2026-06-08T00:00:00+00:00",
            confidence=1.0,
            metadata={"title": "Senior Technical Recruiter", "conflict_key": "contact_identity", "canonical_value": "Jane|Recruiter|AIG"},
        ),
        OpportunityFactDocument(
            document_id="contact-cto",
            namespace=NAMESPACE_CONTACT,
            fact_family="contact",
            fact_text="Jane Target | Chief Technology Officer | AIG",
            source_id="profile:cto",
            source_type="public_profile",
            source_lineage=("profile:cto",),
            freshness_date="2026-06-08T00:00:00+00:00",
            confidence=1.0,
            metadata={"title": "Chief Technology Officer", "conflict_key": "contact_identity", "canonical_value": "Jane|CTO|AIG"},
        ),
    )

    result = derive_recipient_class(docs)

    assert result.status == STATUS_CONFLICTED
    assert result.derived_recipient_class == CLASS_UNKNOWN
    assert result.hitl_required is True
    assert result.contradicted_facts
    assert result.contradiction_status == "CONFLICTED"


def test_target_eligibility_marks_normal_derived_recruiter_eligible() -> None:
    store = _store_for_contact(title="Senior Technical Recruiter")
    derivation = derive_recipient_class_from_store(store)

    eligibility = evaluate_target_eligibility_from_store(
        store=store,
        recipient_derivation=derivation,
        requested_message_type="general_intro",
    )

    assert eligibility.target_eligibility == TARGET_ELIGIBLE
    assert eligibility.recipient_class == CLASS_RECRUITER
    assert eligibility.user_visible_draft_allowed is True
    assert eligibility.strict_jd_user_visible_draft_allowed is True
    assert eligibility.no_send_required is False


def test_daisuke_strict_role_specific_remains_not_targetable_for_us_jd() -> None:
    store = _daisuke_store()
    derivation = derive_recipient_class_from_store(store)

    eligibility = evaluate_target_eligibility_from_store(
        store=store,
        recipient_derivation=derivation,
        requested_message_type=MESSAGE_ROLE_SPECIFIC,
        allow_alternate_message_mode=False,
    )
    blocked_exposure = evaluate_user_visible_draft_exposure(
        target_eligibility=eligibility,
        draft_text=(
            "Hi Daisuke, I noticed AIG's VP, Global Head of Agentic AI Solutions "
            "role (JR2601998). Would a quick resume review be reasonable?"
        ),
    )

    assert derivation.status == STATUS_DERIVED
    assert derivation.derived_recipient_class == CLASS_SENIOR_TA
    assert eligibility.target_eligibility == TARGET_NOT_TARGETABLE
    assert eligibility.alternate_message_mode == ""
    assert eligibility.no_send_required is True
    assert eligibility.user_visible_draft_allowed is False
    assert eligibility.strict_jd_user_visible_draft_allowed is False
    assert "not_targetable:role_ownership_region_mismatch_for_requested_jd" in eligibility.reason_codes
    assert "VP, Global Head of Agentic AI Solutions" in eligibility.blocked_copy_terms
    assert "JR2601998" in eligibility.blocked_copy_terms
    assert blocked_exposure.status == DRAFT_EXPOSURE_BLOCKED
    assert blocked_exposure.user_visible_text == ""


def test_daisuke_alternate_general_intro_passes_only_when_jd_references_are_omitted() -> None:
    store = _daisuke_store()
    derivation = derive_recipient_class_from_store(store)

    eligibility = evaluate_target_eligibility_from_store(
        store=store,
        recipient_derivation=derivation,
        requested_message_type=MESSAGE_ROLE_SPECIFIC,
        allow_alternate_message_mode=True,
    )
    jd_copy = evaluate_user_visible_draft_exposure(
        target_eligibility=eligibility,
        draft_text=(
            "Hi Daisuke, I noticed AIG's VP, Global Head of Agentic AI Solutions "
            "role (JR2601998)."
        ),
    )
    no_jd_copy = evaluate_user_visible_draft_exposure(
        target_eligibility=eligibility,
        draft_text=(
            "Hi Daisuke, I saw your talent acquisition leadership at AIG Japan. "
            "I work on governed agentic AI platforms for regulated enterprises; "
            "would a brief exchange be reasonable?"
        ),
    )

    assert eligibility.target_eligibility == TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE
    assert eligibility.alternate_message_mode == ALT_GENERAL_INTRO_NO_JD
    assert eligibility.user_visible_draft_allowed is True
    assert eligibility.strict_jd_user_visible_draft_allowed is False
    assert eligibility.required_c0_namespaces == (NAMESPACE_CONTACT, NAMESPACE_COMPANY, NAMESPACE_ROLE_OWNERSHIP)
    assert jd_copy.status == DRAFT_EXPOSURE_BLOCKED
    assert "alternate_general_intro_no_jd_contains_jd_reference" in jd_copy.reason_codes
    assert no_jd_copy.status == DRAFT_EXPOSURE_ALLOWED
    assert "JR2601998" not in no_jd_copy.user_visible_text


def test_unknown_profiles_with_existing_weak_evidence_are_not_targetable() -> None:
    for name, title in (
        ("Kathleen Gerstner", "Talent Acquisition Professional"),
        ("Dennis Najar", "IT and Management Executive"),
    ):
        store = _store_for_contact(title=title, name=name)
        derivation = derive_recipient_class_from_store(store)
        eligibility = evaluate_target_eligibility_from_store(
            store=store,
            recipient_derivation=derivation,
            requested_message_type=MESSAGE_ROLE_SPECIFIC,
        )

        assert derivation.derived_recipient_class == CLASS_UNKNOWN
        assert eligibility.target_eligibility == TARGET_NOT_TARGETABLE
        assert eligibility.no_send_required is True
        assert eligibility.user_visible_draft_allowed is False
        assert "not_targetable:no_current_target_owner_signal" in eligibility.reason_codes


def test_missing_profile_evidence_requires_c0_enrichment_before_targeting() -> None:
    derivation = derive_recipient_class([], u0_recipient_class_hint=CLASS_RECRUITER)
    eligibility = evaluate_target_eligibility_from_store(
        store=InMemoryOpportunityFactStore(),
        recipient_derivation=derivation,
        requested_message_type=MESSAGE_ROLE_SPECIFIC,
    )

    assert derivation.status == STATUS_MISSING_EVIDENCE
    assert eligibility.target_eligibility == TARGET_C0_EVIDENCE_REQUIRED
    assert eligibility.required_c0_namespaces == (NAMESPACE_CONTACT, NAMESPACE_ROLE_OWNERSHIP)
    assert eligibility.user_visible_draft_allowed is False


def test_ic_profiles_cannot_pass_as_recruiter_hiring_manager_or_executive() -> None:
    for name, title in (
        ("Anirudh R", "Software Engineer"),
        ("Karthikeya Gowd", "Data Engineer"),
        ("Indu Sri", "Business Analyst"),
    ):
        store = _store_for_contact(title=title, name=name)
        derivation = derive_recipient_class_from_store(
            store,
            u0_recipient_class_hint=CLASS_RECRUITER,
        )
        eligibility = evaluate_target_eligibility_from_store(
            store=store,
            recipient_derivation=derivation,
            requested_message_type=MESSAGE_ROLE_SPECIFIC,
        )
        peer_eligibility = evaluate_target_eligibility_from_store(
            store=store,
            recipient_derivation=derivation,
            requested_message_type="general_intro",
            allow_peer_networking_scope=True,
        )

        assert derivation.derived_recipient_class == CLASS_UNKNOWN
        assert derivation.u0_hint_used_as_authority is False
        assert eligibility.target_eligibility == TARGET_NOT_TARGETABLE
        assert "not_targetable:ic_profile_out_of_apps_lic_scope" in eligibility.reason_codes
        assert peer_eligibility.target_eligibility == TARGET_ELIGIBLE_WITH_ALTERNATE_MESSAGE_MODE
        assert peer_eligibility.alternate_message_mode == ALT_PEER_NETWORKING_INTRO


def test_missing_evidence_returns_ingestion_required_and_unknown() -> None:
    result = derive_recipient_class([], u0_recipient_class_hint=CLASS_RECRUITER)

    assert result.status == STATUS_MISSING_EVIDENCE
    assert result.derived_recipient_class == CLASS_UNKNOWN
    assert result.hitl_required is True
    assert result.u0_hint_used_as_authority is False


def test_derivation_packet_contains_required_lineage_fields() -> None:
    result = derive_recipient_class_from_store(
        _store_for_contact(title="Chief Technology Officer")
    )
    packet = result.to_packet()

    assert packet["schema_version"] == "apps_lic.recipient_class_derivation.v1"
    assert packet["derived_recipient_class"] == CLASS_CTO
    assert packet["source_snapshot_ids"]
    assert packet["supporting_facts"]
    assert packet["evidence_packet_id"].startswith("sha256:")


def test_w3_classifier_is_read_only_and_provider_free() -> None:
    source = (
        REPO_ROOT / "apps_lic" / "engines" / "recipient_classification.py"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "openai",
        "anthropic",
        "chromadb",
        "SovereignChromaClient",
        "upsert_documents",
        "write_text(",
        "urlopen",
        "requests.",
    ):
        assert forbidden not in source
