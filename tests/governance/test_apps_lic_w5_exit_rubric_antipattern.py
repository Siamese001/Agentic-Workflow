"""W5 sentinel tests for apps_lic exit rubric, omission policy, and anti-pattern detector.

Covers P15, P16, P17, SE-P0a:
- P15: exit_rubric.yaml has corrected fail-closed scoping + 5 new dimensions.
- P16: OutreachDraft + OmissionDecision + apply_omission_policy implemented.
- P17: send_mode_enforcement in exit_rubric.yaml (always fail-closed).
- SE-P0a: OutreachAntipatternDetector has 15 default patterns; all fire correctly;
          extension patterns injectable; from_rubric_config() factory works;
          DetectionResult carries evidence_refs and reason_codes.

Plan: apps-lic-canonical-spine-wireup-e7c2a5 W5.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EXIT_RUBRIC   = REPO_ROOT / "apps_lic" / "config" / "exit_rubric.yaml"
ANTIPATTERN_MODULE = REPO_ROOT / "apps_lic" / "engines" / "outreach_antipattern_detector.py"
MANIFEST_MODULE    = REPO_ROOT / "apps_lic" / "integrations" / "preloaded_outreach_context_manifest.py"


# ---------------------------------------------------------------------------
# P15 — exit_rubric.yaml structure
# ---------------------------------------------------------------------------

def test_exit_rubric_exists():
    """P15: exit_rubric.yaml must exist."""
    assert EXIT_RUBRIC.exists()


def test_exit_rubric_has_required_dimensions():
    """P15: exit_rubric.yaml must define all required dimensions."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dim_ids = {d["id"] for d in rubric["dimensions"]}
    required = {
        "no_fabricated_relationship",
        "no_fabricated_application_status",
        "no_confidential_leakage",
        "antipattern_clean",
        "factual_support",
        "no_unsupported_company_facts",
        "no_unsupported_recipient_facts",
        "voice_compliance",
        "channel_length_fit",
        "send_mode_enforcement",
        "tone_fit_seniority",
        "clear_cta",
        "ask_friction_score",
        "proof_appropriate_for_recipient",
        "personalization_mode_appropriate",
        "asymmetric_insight_present",
        "omission_policy_respected",
    }
    missing = required - dim_ids
    assert not missing, f"exit_rubric.yaml missing dimensions: {missing}"


def test_exit_rubric_always_fail_closed_dims():
    """P15: Hard-fail dimensions must be fail_closed=always."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    always_closed = {
        "no_fabricated_relationship",
        "no_fabricated_application_status",
        "no_confidential_leakage",
        "antipattern_clean",
        "send_mode_enforcement",
        "omission_policy_respected",
    }
    for dim_id in always_closed:
        assert dims[dim_id].get("fail_closed") == "always", (
            f"Dimension {dim_id} must have fail_closed=always"
        )


def test_exit_rubric_factual_support_scoped():
    """P15: factual_support must be scoped to remaining_claims_in_draft (not always)."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    fs = dims["factual_support"]
    assert fs.get("fail_closed") == "remaining_claims_in_draft", (
        "factual_support must be scoped to remaining_claims_in_draft, not always"
    )


def test_exit_rubric_channel_length_fit_tolerance():
    """P15: channel_length_fit must have tolerance=1.10."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    clf = dims["channel_length_fit"]
    assert float(clf.get("tolerance", 0)) == pytest.approx(1.10)


def test_exit_rubric_new_p15_dimensions_present():
    """P15: Five new P15 dimensions must be present."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dim_ids = {d["id"] for d in rubric["dimensions"]}
    new_dims = {
        "ask_friction_score",
        "proof_appropriate_for_recipient",
        "personalization_mode_appropriate",
        "asymmetric_insight_present",
        "omission_policy_respected",
    }
    missing = new_dims - dim_ids
    assert not missing, f"P15 new dimensions missing: {missing}"


def test_exit_rubric_ask_friction_fail_closed_above_bound():
    """P15: ask_friction_score must be fail_closed when score > 0.5."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    afs = dims["ask_friction_score"]
    assert "0.5" in str(afs.get("fail_closed_when", "")), (
        "ask_friction_score must have fail_closed_when containing 0.5"
    )


def test_exit_rubric_proof_not_universally_mandatory():
    """P15: proof_appropriate_for_recipient must NOT be fail_closed=always."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    proof = dims["proof_appropriate_for_recipient"]
    assert proof.get("fail_closed") != "always", (
        "proof_appropriate_for_recipient must NOT be universally fail-closed"
    )
    assert proof.get("contextual") is True or "required_when" in proof


def test_exit_rubric_asymmetric_insight_config_gated():
    """P15: asymmetric_insight_present must be config-gated (not universally required)."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    ai = dims["asymmetric_insight_present"]
    assert ai.get("fail_closed") != "always"
    assert "required_when" in ai, (
        "asymmetric_insight_present must have required_when config-gated field"
    )


def test_exit_rubric_x3_dispositions():
    """P15: exit_rubric.yaml must declare all valid X3 dispositions."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dispositions = set(rubric.get("x3_dispositions", []))
    expected = {"ALLOW_FINISH", "ESCALATE_HITL", "SAFE_ABSTAIN", "REROUTE", "DENY", "COMMIT_REQUEST"}
    missing = expected - dispositions
    assert not missing, f"exit_rubric.yaml missing X3 dispositions: {missing}"


def test_exit_rubric_hitl_policy_present():
    """P15: exit_rubric.yaml must have hitl_policy block."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    assert "hitl_policy" in rubric
    assert "escalate_on_dim_fail" in rubric["hitl_policy"]


# ---------------------------------------------------------------------------
# P17 — send_mode_enforcement dimension
# ---------------------------------------------------------------------------

def test_exit_rubric_send_mode_enforcement_always_fail_closed():
    """P17: send_mode_enforcement must be fail_closed=always."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    sme = dims["send_mode_enforcement"]
    assert sme.get("fail_closed") == "always"


def test_exit_rubric_send_mode_enforcement_forbidden_modes():
    """P17: send_mode_enforcement must list all 3 forbidden modes."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    sme = dims["send_mode_enforcement"]
    forbidden = set(sme.get("forbidden_send_modes", []))
    assert forbidden == {"send_now", "auto_send", "connector_send"}


def test_exit_rubric_send_mode_enforcement_allowed_modes():
    """P17: send_mode_enforcement must list allowed send modes."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = {d["id"]: d for d in rubric["dimensions"]}
    sme = dims["send_mode_enforcement"]
    allowed = set(sme.get("allowed_send_modes", []))
    assert allowed == {"draft_only", "review_required", "send_ready_candidate"}


# ---------------------------------------------------------------------------
# P16 — OutreachDraft + apply_omission_policy
# ---------------------------------------------------------------------------

def test_outreach_draft_class_exists():
    """P16: OutreachDraft class must exist in manifest module."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import OutreachDraft
    assert OutreachDraft is not None


def test_outreach_draft_has_omitted_claims():
    """P16: OutreachDraft must have omitted_claims field."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import OutreachDraft
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(OutreachDraft)}
    assert "omitted_claims" in field_names


def test_outreach_draft_rejects_forbidden_send_mode():
    """P16: OutreachDraft must raise ValueError for forbidden send modes."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import OutreachDraft
    for mode in ("send_now", "auto_send", "connector_send"):
        with pytest.raises(ValueError, match=mode):
            OutreachDraft(
                draft_text="hello",
                send_mode=mode,
                manifest_hash="sha256:x",
                word_count=1,
                omitted_claims=(),
                channel="email",
                outreach_mode="cold",
                recipient_class="RECRUITER",
            )


def test_outreach_draft_construction():
    """P16: OutreachDraft can be constructed with valid send_mode."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import OutreachDraft
    draft = OutreachDraft(
        draft_text="Hi there, I wanted to reach out...",
        send_mode="draft_only",
        manifest_hash="sha256:abc",
        word_count=8,
        omitted_claims=("salary_ask",),
        channel="email",
        outreach_mode="cold",
        recipient_class="RECRUITER",
    )
    assert draft.send_mode == "draft_only"
    assert "salary_ask" in draft.omitted_claims


def test_apply_omission_policy_supported_claim():
    """P16: apply_omission_policy returns action=include for supported claims."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        apply_omission_policy, SourceItem
    )
    from dataclasses import dataclass, field as dc_field

    @dataclass
    class MockManifest:
        source_items: tuple = (
            SourceItem(source_id="s1", source_type="resume", label="K8s migration",
                       uri="sha256:aaa", field_ref="k8s_claim"),
        )
        claim_permission_map: dict = dc_field(default_factory=dict)
        omission_policy: str = "omit_unsupported"

    decisions = apply_omission_policy(claims=["k8s_claim"], manifest=MockManifest())
    assert len(decisions) == 1
    assert decisions[0].action == "include"
    assert decisions[0].is_supported is True


def test_apply_omission_policy_omit_unsupported():
    """P16: apply_omission_policy returns action=omit for omit_unsupported claims."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        apply_omission_policy
    )
    from dataclasses import dataclass, field as dc_field

    @dataclass
    class MockManifest:
        source_items: tuple = ()
        claim_permission_map: dict = dc_field(default_factory=lambda: {"salary_ask": "omit_unsupported"})
        omission_policy: str = "omit_unsupported"

    decisions = apply_omission_policy(claims=["salary_ask"], manifest=MockManifest())
    assert decisions[0].action == "omit"


def test_apply_omission_policy_fail_closed():
    """P16: apply_omission_policy returns action=fail for fail_closed policy."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        apply_omission_policy
    )
    from dataclasses import dataclass, field as dc_field

    @dataclass
    class MockManifest:
        source_items: tuple = ()
        claim_permission_map: dict = dc_field(default_factory=lambda: {"github_link": "fail_closed"})
        omission_policy: str = "omit_unsupported"

    decisions = apply_omission_policy(claims=["github_link"], manifest=MockManifest())
    assert decisions[0].action == "fail"


def test_apply_omission_policy_hitl_required():
    """P16: apply_omission_policy returns action=hitl for hitl_required policy."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        apply_omission_policy
    )
    from dataclasses import dataclass, field as dc_field

    @dataclass
    class MockManifest:
        source_items: tuple = ()
        claim_permission_map: dict = dc_field(default_factory=lambda: {"ref_claim": "hitl_required"})
        omission_policy: str = "omit_unsupported"

    decisions = apply_omission_policy(claims=["ref_claim"], manifest=MockManifest())
    assert decisions[0].action == "hitl"


def test_apply_omission_policy_default_fallback():
    """P16: apply_omission_policy uses manifest.omission_policy when claim not in map."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        apply_omission_policy
    )
    from dataclasses import dataclass, field as dc_field

    @dataclass
    class MockManifest:
        source_items: tuple = ()
        claim_permission_map: dict = dc_field(default_factory=dict)  # empty map
        omission_policy: str = "fail_closed"  # default is strict

    decisions = apply_omission_policy(claims=["unknown_claim"], manifest=MockManifest())
    assert decisions[0].action == "fail", (
        "When claim not in claim_permission_map, must fall back to manifest.omission_policy"
    )


def test_omission_decision_class_exists():
    """P16: OmissionDecision class must exist."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import OmissionDecision
    assert OmissionDecision is not None


# ---------------------------------------------------------------------------
# SE-P0a — OutreachAntipatternDetector
# ---------------------------------------------------------------------------

def test_antipattern_module_exists():
    """SE-P0a: outreach_antipattern_detector.py must exist."""
    assert ANTIPATTERN_MODULE.exists()


def test_antipattern_detector_has_15_default_patterns():
    """SE-P0a: detector must have exactly 15 default patterns."""
    from apps_lic.engines.outreach_antipattern_detector import (
        OutreachAntipatternDetector, _DEFAULT_PATTERNS
    )
    assert len(_DEFAULT_PATTERNS) == 15
    detector = OutreachAntipatternDetector()
    assert detector.pattern_count == 15


def test_antipattern_all_15_pattern_ids_present():
    """SE-P0a: All 15 default pattern IDs (AP_001–AP_015) must be present."""
    from apps_lic.engines.outreach_antipattern_detector import _DEFAULT_PATTERNS
    ids = {p.pattern_id for p in _DEFAULT_PATTERNS}
    expected = {f"AP_{i:03d}" for i in range(1, 16)}
    missing = expected - ids
    assert not missing, f"Missing pattern IDs: {missing}"


def test_antipattern_passive_seeker_tone():
    """SE-P0a: AP_001 PASSIVE_SEEKER_TONE fires on 'I would love to learn more'."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("Hi Jane, I would love to learn more about the role.")
    assert result.is_clean is False
    assert "PASSIVE_SEEKER_TONE" in result.reason_codes


def test_antipattern_unevidenced_self_assessment():
    """SE-P0a: AP_002 fires on 'I think I'd be a great fit'."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("I think I'd be a great fit for this role.")
    assert result.is_clean is False
    assert "UNEVIDENCED_SELF_ASSESSMENT" in result.reason_codes


def test_antipattern_em_dash():
    """SE-P0a: AP_009 fires on em dash (—) in draft."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("I led the team — shipping K8s migration on time.")
    assert result.is_clean is False
    assert "EM_DASH" in result.reason_codes


def test_antipattern_passive_close():
    """SE-P0a: AP_014 fires on 'Please let me know if you have any questions'."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("Looking forward to connecting. Please let me know if you have any questions.")
    assert result.is_clean is False
    assert "PASSIVE_CLOSE" in result.reason_codes


def test_antipattern_noise_opener():
    """SE-P0a: AP_015 fires on 'Hope this finds you well'."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("Hope this finds you well. I wanted to reach out about...")
    assert result.is_clean is False
    assert "NOISE_OPENER" in result.reason_codes


def test_antipattern_premature_logistics():
    """SE-P0a: AP_012 fires when compensation is mentioned."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("I'm targeting a compensation of $180k for this role.")
    assert result.is_clean is False
    assert "PREMATURE_LOGISTICS" in result.reason_codes


def test_antipattern_clean_draft():
    """SE-P0a: Clean draft must return is_clean=True."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    clean_draft = (
        "Jane, I shipped a K8s migration that cut deploy time by 40%. "
        "Given your team's public focus on platform reliability, I'd value "
        "a 15-minute call to explore fit. Would Thursday at 2pm work?"
    )
    result = d.detect(clean_draft)
    assert result.is_clean is True
    assert len(result.matches) == 0
    assert len(result.reason_codes) == 0


def test_antipattern_evidence_refs_populated():
    """SE-P0a: evidence_refs must be populated for each match."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("Hope you're doing well. I would love to learn more.")
    assert len(result.evidence_refs) >= 2
    for ref in result.evidence_refs:
        assert "AP_" in ref
        assert "pos=" in ref


def test_antipattern_three_para_intro_fires():
    """SE-P0a: AP_013 fires when >120 words precede the CTA."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    # 130 filler words before CTA
    filler = " ".join(["word"] * 130)
    long_draft = filler + " Would you be open to a call?"
    result = d.detect(long_draft)
    assert result.is_clean is False
    assert "THREE_PARA_INTRO" in result.reason_codes


def test_antipattern_three_para_intro_clean():
    """SE-P0a: AP_013 does NOT fire when <120 words precede the CTA."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    short_draft = "I shipped K8s to cut deploy time by 40%. Would you be open to a call?"
    result = d.detect(short_draft)
    three_para = [m for m in result.matches if m.pattern_id == "AP_013"]
    assert len(three_para) == 0


def test_antipattern_extension_patterns():
    """SE-P0a: Extension patterns are injectable and fire correctly."""
    from apps_lic.engines.outreach_antipattern_detector import (
        OutreachAntipatternDetector, AntiPattern
    )
    ext = AntiPattern(
        pattern_id="EXT_001",
        reason_code="CUSTOM_PATTERN",
        description="Custom test pattern",
        pattern_text="custom forbidden phrase",
        is_regex=False,
    )
    d = OutreachAntipatternDetector(extension_patterns=[ext])
    assert d.pattern_count == 16
    result = d.detect("This has a custom forbidden phrase in it.")
    assert result.is_clean is False
    assert "CUSTOM_PATTERN" in result.reason_codes


def test_antipattern_from_rubric_config():
    """SE-P0a: from_rubric_config() builds detector from rubric YAML content."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        import yaml
        rubric = yaml.safe_load(fh)
    d = OutreachAntipatternDetector.from_rubric_config(rubric)
    assert d.pattern_count == 15  # 15 defaults + 0 extensions from empty list


def test_antipattern_no_provider_imports():
    """SE-P0a: outreach_antipattern_detector.py must not import providers."""
    source = ANTIPATTERN_MODULE.read_text(encoding="utf-8")
    for forbidden in ("openai", "anthropic", "google.generativeai", "boto3"):
        assert forbidden not in source


def test_antipattern_does_not_rewrite_content():
    """SE-P0a: DetectionResult must not contain modified draft_text."""
    from apps_lic.engines.outreach_antipattern_detector import (
        OutreachAntipatternDetector, DetectionResult
    )
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(DetectionResult)}
    assert "draft_text" not in field_names, (
        "DetectionResult must NOT store draft_text — detector does not rewrite content"
    )


def test_antipattern_scraper_opener():
    """SE-P0a: AP_005 fires on 'I saw your company'."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("I saw your company is growing fast and wanted to reach out.")
    assert "SCRAPER_OPENER" in result.reason_codes


def test_antipattern_buzzword_filler():
    """SE-P0a: AP_007 fires on 'thought leader'."""
    from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector
    d = OutreachAntipatternDetector()
    result = d.detect("As a thought leader in the space, you might appreciate this.")
    assert "BUZZWORD_FILLER" in result.reason_codes
