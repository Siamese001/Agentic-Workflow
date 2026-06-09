from pathlib import Path

import yaml

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY_TRIGGER,
    NAMESPACE_JD,
    NAMESPACE_PRIOR_THREAD,
    NAMESPACE_REFERRAL,
    NAMESPACE_RELATIONSHIP,
    WRITE_AUTHORITY_GOVERNED_INGESTION,
    InMemoryOpportunityFactStore,
    OpportunityIngestionInput,
    run_governed_opportunity_ingestion,
)
from apps_lic.engines.message_type_requirement_gate import (
    CANONICAL_MESSAGE_TYPES,
    MESSAGE_FOLLOW_UP,
    MESSAGE_GENERAL_INTRO,
    MESSAGE_REFERRAL_ASK,
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
    MISSING_APPLICATION_STATUS,
    MISSING_COMPANY_TRIGGER,
    MISSING_JD_FACTS,
    MISSING_PRIOR_THREAD,
    MISSING_REFERRER_CONTEXT,
    MISSING_RELATIONSHIP_CONTEXT,
    MISSING_REQUISITION_NUMBER,
    RECIPIENT_CLASS_NOT_DERIVED,
    STATUS_REQUIREMENTS_BLOCKED,
    STATUS_REQUIREMENTS_PASS,
    evaluate_message_requirements_from_store,
    resolve_message_type,
)
from apps_lic.engines.recipient_classification import (
    CLASS_HIRING_MANAGER,
    CLASS_EXECUTIVE,
    CLASS_RECRUITER,
    CLASS_SENIOR_TA,
    CLASS_UNKNOWN,
    STATUS_DERIVED,
    STATUS_LOW_CONFIDENCE,
    derive_recipient_class_from_store,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
W4_CONFIG = (
    REPO_ROOT
    / "apps_lic"
    / "config"
    / "domain_contract"
    / "message_type_requirements.v1.yaml"
)


def _store_for(
    *,
    title: str = "Senior Technical Recruiter",
    jd: object | None = None,
    company_trigger: object | None = None,
    referral: object | None = None,
    relationship: object | None = None,
    prior_thread: object | None = None,
) -> InMemoryOpportunityFactStore:
    store = InMemoryOpportunityFactStore()
    payload = OpportunityIngestionInput(
        request_id=f"req-w4-{title}",
        trace_root="trace-w4",
        idempotency_key=f"idem-w4-{title}",
        contact={
            "name": "Jane Target",
            "title": title,
            "headline": title,
            "company": "AIG",
            "linkedin_url": "https://www.linkedin.com/in/jane-target",
        },
        jd=jd,
        company_trigger=company_trigger,
        referral=referral,
        relationship=relationship,
        prior_thread=prior_thread,
        collected_at="2026-06-08T00:00:00+00:00",
    )
    run_governed_opportunity_ingestion(
        payload,
        store=store,
        write_authority=WRITE_AUTHORITY_GOVERNED_INGESTION,
        write_enabled=True,
    )
    return store


def _result(
    store: InMemoryOpportunityFactStore,
    *,
    message_type_hint: str,
    intent_text: str = "",
    application_status: str = "",
):
    derivation = derive_recipient_class_from_store(store)
    return evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=derivation,
        message_type_hint=message_type_hint,
        intent_text=intent_text,
        application_status=application_status,
    )


def test_w4_config_freezes_five_message_types_modifiers_and_statuses() -> None:
    with W4_CONFIG.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    assert config["canonical_message_types"] == list(CANONICAL_MESSAGE_TYPES)
    for modifier in (
        "uses_jd",
        "application_status_claimed",
        "uses_company_trigger",
        "uses_referral_context",
        "uses_prior_thread",
        "uses_sensitive_constraints",
    ):
        assert modifier in config["modifiers"]
    for missing_status in (
        RECIPIENT_CLASS_NOT_DERIVED,
        MISSING_JD_FACTS,
        MISSING_REQUISITION_NUMBER,
        MISSING_APPLICATION_STATUS,
        MISSING_PRIOR_THREAD,
        MISSING_REFERRER_CONTEXT,
        MISSING_RELATIONSHIP_CONTEXT,
        MISSING_COMPANY_TRIGGER,
    ):
        assert missing_status in config["missing_field_statuses"]


def test_resolver_maps_hints_and_modifiers() -> None:
    resolution = resolve_message_type(
        message_type_hint="role-specific recruiter note",
        intent_text="Mention req JR-12345 after I applied, but do not discuss visa.",
    )

    assert resolution.message_type == MESSAGE_ROLE_SPECIFIC
    assert resolution.modifiers["uses_jd"] is True
    assert resolution.modifiers["application_status_claimed"] is True
    assert resolution.modifiers["uses_sensitive_constraints"] is True


def test_general_intro_passes_without_jd_for_recruiter() -> None:
    result = _result(
        _store_for(title="Senior Technical Recruiter"),
        message_type_hint="general intro",
    )

    assert result.status == STATUS_REQUIREMENTS_PASS
    assert result.allowed is True
    assert result.message_type == MESSAGE_GENERAL_INTRO
    assert NAMESPACE_JD not in result.required_namespaces


def test_role_specific_recruiter_blocks_when_jd_is_missing() -> None:
    result = _result(
        _store_for(title="Senior Technical Recruiter"),
        message_type_hint="role_specific",
    )

    assert result.status == STATUS_REQUIREMENTS_BLOCKED
    assert result.missing_fields == (MISSING_JD_FACTS,)
    assert result.required_namespaces == (NAMESPACE_JD,)


def test_role_specific_recruiter_blocks_when_requisition_is_missing() -> None:
    result = _result(
        _store_for(
            title="Senior Technical Recruiter",
            jd={
                "title": "Director, AI Platforms",
                "company": "AIG",
                "description": "Build production AI platforms.",
            },
        ),
        message_type_hint="role_specific",
    )

    assert result.status == STATUS_REQUIREMENTS_BLOCKED
    assert result.missing_fields == (MISSING_REQUISITION_NUMBER,)


def test_role_specific_recruiter_passes_with_jd_title_and_req() -> None:
    result = _result(
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
    )

    assert result.status == STATUS_REQUIREMENTS_PASS
    assert result.allowed is True
    assert result.recipient_class == CLASS_RECRUITER


def test_role_specific_senior_ta_has_same_jd_title_and_req_requirement() -> None:
    result = _result(
        _store_for(
            title="Global Head of Talent Acquisition",
            jd={
                "title": "Director, AI Platforms",
                "requisition_number": "JR-12345",
                "company": "AIG",
                "description": "Build production AI platforms.",
            },
        ),
        message_type_hint="role_specific",
    )

    assert result.status == STATUS_REQUIREMENTS_PASS
    assert result.recipient_class == CLASS_SENIOR_TA


def test_role_specific_hiring_manager_requires_jd_and_position_not_req() -> None:
    missing = _result(
        _store_for(title="Director of AI Platform Engineering"),
        message_type_hint="role_specific",
    )
    passing = _result(
        _store_for(
            title="Director of AI Platform Engineering",
            jd={
                "title": "Director, AI Platforms",
                "company": "AIG",
                "description": "Build production AI platforms.",
            },
        ),
        message_type_hint="role_specific",
    )

    assert missing.status == STATUS_REQUIREMENTS_BLOCKED
    assert missing.missing_fields == (MISSING_JD_FACTS,)
    assert passing.status == STATUS_REQUIREMENTS_PASS
    assert passing.recipient_class == CLASS_HIRING_MANAGER


def test_live_public_title_patterns_derive_recipient_class_without_u0_hint() -> None:
    cases = (
        ("Talent Acquisition Strategist", CLASS_RECRUITER, "recruiter_ta_strategist_signal"),
        ("AI Systems Builder", CLASS_HIRING_MANAGER, "hiring_manager_ai_builder_signal"),
        (
            "Head of Technology and Business Enablement",
            CLASS_EXECUTIVE,
            "executive_technology_business_enablement_signal",
        ),
        (
            "Neo4j Product / Hiring Amplifier",
            CLASS_HIRING_MANAGER,
            "hiring_manager_product_hiring_signal",
        ),
        (
            "AI and Data Platform Product/Architecture Leader",
            CLASS_HIRING_MANAGER,
            "hiring_manager_product_architecture_leader_signal",
        ),
    )

    for title, expected_class, expected_reason in cases:
        derivation = derive_recipient_class_from_store(_store_for(title=title))

        assert derivation.status == STATUS_DERIVED
        assert derivation.derived_recipient_class == expected_class
        assert expected_reason in derivation.class_reason_codes
        assert derivation.u0_hint_used_as_authority is False


def test_follow_up_blocks_without_prior_thread() -> None:
    result = _result(
        _store_for(title="Senior Technical Recruiter"),
        message_type_hint="follow_up",
    )

    assert result.status == STATUS_REQUIREMENTS_BLOCKED
    assert result.missing_fields == (MISSING_PRIOR_THREAD,)
    assert result.required_namespaces == (NAMESPACE_PRIOR_THREAD,)


def test_referral_ask_blocks_without_referrer_and_relationship_context() -> None:
    result = _result(
        _store_for(title="Senior Technical Recruiter"),
        message_type_hint="referral_ask",
    )

    assert result.status == STATUS_REQUIREMENTS_BLOCKED
    assert result.missing_fields == (
        MISSING_REFERRER_CONTEXT,
        MISSING_RELATIONSHIP_CONTEXT,
    )
    assert result.required_namespaces == (
        NAMESPACE_REFERRAL,
        NAMESPACE_RELATIONSHIP,
    )


def test_trigger_based_insight_blocks_without_company_trigger() -> None:
    result = _result(
        _store_for(title="Chief Executive Officer"),
        message_type_hint="trigger_based_insight",
    )

    assert result.status == STATUS_REQUIREMENTS_BLOCKED
    assert result.missing_fields == (MISSING_COMPANY_TRIGGER,)
    assert result.required_namespaces == (NAMESPACE_COMPANY_TRIGGER,)


def test_application_status_claim_blocks_without_application_status_evidence() -> None:
    result = _result(
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
        intent_text="I applied last week and want a resume review.",
    )

    assert result.status == STATUS_REQUIREMENTS_BLOCKED
    assert result.missing_fields == (MISSING_APPLICATION_STATUS,)


def test_application_status_claim_passes_when_status_is_supplied() -> None:
    result = _result(
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
        intent_text="I applied last week and want a resume review.",
        application_status="applied",
    )

    assert result.status == STATUS_REQUIREMENTS_PASS


def test_unknown_recipient_class_blocks_even_when_message_inputs_exist() -> None:
    store = _store_for(
        title="Business Partner",
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production AI platforms.",
        },
    )
    derivation = derive_recipient_class_from_store(store)
    assert derivation.status == STATUS_LOW_CONFIDENCE
    assert derivation.derived_recipient_class == CLASS_UNKNOWN

    result = evaluate_message_requirements_from_store(
        store=store,
        recipient_derivation=derivation,
        message_type_hint="role_specific",
    )

    assert result.status == STATUS_REQUIREMENTS_BLOCKED
    assert result.missing_fields == (RECIPIENT_CLASS_NOT_DERIVED,)


def test_follow_up_referral_and_trigger_pass_when_evidence_is_present() -> None:
    follow_up = _result(
        _store_for(
            title="Senior Technical Recruiter",
            prior_thread={
                "thread_summary": "Recruiter asked for a concise follow-up.",
                "last_touch_date": "2026-06-01T00:00:00+00:00",
            },
        ),
        message_type_hint="follow_up",
    )
    referral = _result(
        _store_for(
            title="Senior Technical Recruiter",
            referral={
                "referrer_name": "Sam Referrer",
                "permission_scope": "may mention name",
            },
            relationship={
                "relationship_context": "Sam offered a warm intro.",
                "permission_scope": "may reference warm intro",
            },
        ),
        message_type_hint="referral_ask",
    )
    trigger = _result(
        _store_for(
            title="Chief Executive Officer",
            company_trigger={
                "trigger_text": "AIG announced a new enterprise AI operating model.",
                "url": "https://example.com/aig-ai",
            },
        ),
        message_type_hint="trigger_based_insight",
    )

    assert follow_up.status == STATUS_REQUIREMENTS_PASS
    assert referral.status == STATUS_REQUIREMENTS_PASS
    assert trigger.status == STATUS_REQUIREMENTS_PASS
    assert trigger.message_type == MESSAGE_TRIGGER_BASED_INSIGHT
    assert referral.message_type == MESSAGE_REFERRAL_ASK
    assert follow_up.message_type == MESSAGE_FOLLOW_UP


def test_w4_gate_is_read_only_and_provider_free() -> None:
    source = (
        REPO_ROOT / "apps_lic" / "engines" / "message_type_requirement_gate.py"
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
