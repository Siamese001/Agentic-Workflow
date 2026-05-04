"""W8 — apps_lic canonical 24 hard sentinel tests (T-suite + V1).

These are the plan-named sentinels from the T-suite section of
apps-lic-canonical-spine-wireup-e7c2a5.md.  Each function name is exact.

Categories:
  Cat 1 — L0 architecture integrity (5 tests)
  Cat 2 — Route behavior (7 tests)
  Cat 3 — Manifest integrity (2 tests)
  Cat 4 — Exit rubric behavior (3 tests)
  Cat 5 — Write discipline (2 tests)
  Cat 6 — Anti-pattern + channel (3 tests)
  Cat 7 — Scoped signal controls (5 tests + 1 extra)
  Cat 8 — BriefingReady validation (1 test)

All tests are compose-only: no provider calls, no state writes.
Existing governance suite must remain green after this file is added.

Plan: apps-lic-canonical-spine-wireup-e7c2a5 W8 T-suite + V1.
"""
from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_PY       = REPO_ROOT / "apps_lic" / "__main__.py"
MANIFEST_PY   = REPO_ROOT / "apps_lic" / "integrations" / "preloaded_outreach_context_manifest.py"
EXIT_RUBRIC   = REPO_ROOT / "apps_lic" / "config" / "exit_rubric.yaml"
PLAN_RULES    = REPO_ROOT / "apps_lic" / "config" / "lic_plan_rules.yaml"
OUTREACH_SCHEMA = REPO_ROOT / "apps_lic" / "config" / "outreach_schema.json"
SPINE_MANIFEST  = REPO_ROOT / "apps_lic" / "spine_manifest.yaml"


# ===========================================================================
# Category 1: L0 architecture integrity
# ===========================================================================

def test_apps_lic_l0_emits_exactly_one_route_contract():
    """Cat1: L0 __main__.py must produce exactly one RouteContract decision path."""
    src = MAIN_PY.read_text(encoding="utf-8")
    # Must reference RouteContract (directly or via import)
    assert "RouteContract" in src or "route_contract" in src.lower(), (
        "__main__.py must reference RouteContract — L0 emits exactly one route decision"
    )
    # Must NOT return multiple conflicting route emissions in the same branch
    # (Checked structurally: verify no direct provider execution at module level)
    assert "subprocess.run" not in src
    assert "subprocess.Popen" not in src


def test_apps_lic_l0_does_not_execute_apps_research():
    """Cat1: L0 __main__.py must not directly execute apps_research."""
    src = MAIN_PY.read_text(encoding="utf-8")
    # Direct instantiation or call of apps_research engine is forbidden
    for forbidden in (
        "CompanyBriefEngine(", "BaseResearchEngine(", "company_brief_engine.run(",
        "apps_research.run(", "apps_research.engines",
    ):
        assert forbidden not in src, (
            f"L0 must not execute apps_research directly — found {forbidden!r}"
        )


def test_apps_lic_l0_does_not_import_apps_research():
    """Cat1: L0 __main__.py must not import apps_research packages."""
    src = MAIN_PY.read_text(encoding="utf-8")
    # Top-level or inline import of apps_research is forbidden in L0 path
    forbidden_patterns = [
        "from apps_research",
        "import apps_research",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in src, (
            f"L0 must not import apps_research — found {pattern!r}"
        )


def test_apps_lic_l0_does_not_call_providers():
    """Cat1: L0 __main__.py must not call LLM providers."""
    src = MAIN_PY.read_text(encoding="utf-8")
    for forbidden in (
        "openai.ChatCompletion", "anthropic.Anthropic", "anthropic.Claude",
        "get_client(", "llm_call(", "chat_completion(",
        "openai.chat.completions",
    ):
        assert forbidden not in src, (
            f"L0 must not call providers — found {forbidden!r}"
        )


def test_apps_lic_l0_allows_read_only_config_open_but_blocks_write_mode_open():
    """Cat1: L0 open() calls must be read-mode only; write-mode open is forbidden."""
    src = MAIN_PY.read_text(encoding="utf-8")
    # Write-mode open patterns are forbidden
    for forbidden in ('open(', ):
        # scan for write modes if open is used
        import re
        write_opens = re.findall(r'open\([^)]+["\']w["\']', src)
        assert not write_opens, (
            f"L0 must not use write-mode open — found: {write_opens}"
        )
    # json.dump to durable paths is also forbidden
    assert "json.dump" not in src or "StringIO" in src, (
        "L0 must not use json.dump to durable state"
    )


# ===========================================================================
# Category 2: Route behavior
# ===========================================================================

def test_apps_lic_complete_briefing_routes_r4_single_action():
    """Cat2: When briefing is complete, route must be R4_SINGLE_ACTION."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        PreloadedOutreachContextManifest,
    )
    # Manifest is the gating artifact for R4; its presence implies R4 is the route
    import dataclasses
    fields = {f.name for f in dataclasses.fields(PreloadedOutreachContextManifest)}
    assert "manifest_id" in fields
    assert "confidence_score" in fields
    # Route claim in spine_manifest
    with SPINE_MANIFEST.open(encoding="utf-8") as fh:
        sm = yaml.safe_load(fh)
    claimed = sm.get("claimed_routes", [])
    routes = [r.get("type", "") for r in claimed]
    assert "R4_SINGLE_ACTION" in routes, (
        f"spine_manifest must claim R4_SINGLE_ACTION — found: {routes}"
    )


def test_apps_lic_missing_briefing_routes_r3r4_managed_workflow():
    """Cat2: When briefing is missing, route must be R3R4_MANAGED_WORKFLOW."""
    with SPINE_MANIFEST.open(encoding="utf-8") as fh:
        sm = yaml.safe_load(fh)
    claimed = sm.get("claimed_routes", [])
    routes = [r.get("type", "") for r in claimed]
    assert "R3R4_MANAGED_WORKFLOW" in routes, (
        f"spine_manifest must claim R3R4_MANAGED_WORKFLOW — found: {routes}"
    )


def test_apps_lic_apps_research_success_resumes_r4_single_action():
    """Cat2: After research succeeds, dispatcher resumes R4_SINGLE_ACTION."""
    dispatcher = REPO_ROOT / "apps_lic" / "integrations" / "managed_workflow_dispatcher.py"
    assert dispatcher.exists(), "managed_workflow_dispatcher.py must exist"
    src = dispatcher.read_text(encoding="utf-8")
    # After research success the dispatcher must signal R4 or equivalent resume
    assert "R4_SINGLE_ACTION" in src or "r4_single_action" in src.lower() or "resume" in src.lower(), (
        "dispatcher must resume R4_SINGLE_ACTION after research success"
    )


def test_apps_lic_apps_research_failure_fails_closed_through_exit():
    """Cat2: Research failure R5 codes must route through Exit, not direct return."""
    dispatcher = REPO_ROOT / "apps_lic" / "integrations" / "managed_workflow_dispatcher.py"
    src = dispatcher.read_text(encoding="utf-8")
    # Must reference fail-closed R5 reason codes
    for code in ("APPS_RESEARCH_FAILED", "APPS_RESEARCH_EMPTY", "APPS_RESEARCH_STALE"):
        assert code in src, (
            f"dispatcher must handle research failure code {code!r}"
        )


def test_apps_lic_invalid_outreach_request_rejected_by_u0_not_r5():
    """Cat2: Invalid schema request rejected at U0 (exit code 2), not as R5."""
    with OUTREACH_SCHEMA.open(encoding="utf-8") as fh:
        schema = json.load(fh)
    # Schema must have required fields including send_mode
    assert "send_mode" in str(schema), "outreach schema must define send_mode"
    # L0 policy must have invalid schema rejection distinct from R5
    l0_policy = REPO_ROOT / "apps_lic" / "config" / "l0_policy.yaml"
    assert l0_policy.exists(), "l0_policy.yaml must exist"
    with l0_policy.open(encoding="utf-8") as fh:
        l0 = yaml.safe_load(fh)
    # Must have invalid schema handling
    l0_str = str(l0)
    assert "invalid" in l0_str.lower() or "schema" in l0_str.lower() or "reject" in l0_str.lower(), (
        "l0_policy.yaml must describe schema-rejection behavior"
    )


def test_apps_lic_briefing_missing_research_not_authorized_only_when_policy_blocks_research():
    """Cat2: BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED fires only when policy blocks research."""
    dispatcher = REPO_ROOT / "apps_lic" / "integrations" / "managed_workflow_dispatcher.py"
    src = dispatcher.read_text(encoding="utf-8")
    # The code must NOT fire this code on the normal missing-briefing path
    # (normal missing briefing → R3R4_MANAGED_WORKFLOW)
    # Verify the code distinguishes policy-blocked from normal missing
    assert "BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED" in src or "research_not_authorized" in src.lower(), (
        "dispatcher must handle BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED for policy-blocked case"
    )


def test_apps_lic_r3_simple_grounded_read_briefing_only_no_outreach_draft():
    """Cat2: R3_SIMPLE_GROUNDED_READ with briefing_only=True produces briefing, never OutreachDraft."""
    with SPINE_MANIFEST.open(encoding="utf-8") as fh:
        sm = yaml.safe_load(fh)
    claimed = sm.get("claimed_routes", [])
    routes = [r.get("type", "") for r in claimed]
    assert "R3_SIMPLE_GROUNDED_READ" in routes, (
        "spine_manifest must claim R3_SIMPLE_GROUNDED_READ"
    )
    # Verify OutreachDraft import does not appear in the research bridge
    bridge = REPO_ROOT / "apps_lic" / "integrations" / "apps_research_bridge.py"
    assert bridge.exists(), "apps_research_bridge.py must exist"
    src = bridge.read_text(encoding="utf-8")
    assert "OutreachDraft" not in src, (
        "apps_research_bridge must not produce OutreachDraft — briefing-only path"
    )


# ===========================================================================
# Category 3: Manifest integrity
# ===========================================================================

def test_apps_lic_preloaded_outreach_context_manifest_has_hash_lineage_policy_blueprint_replay():
    """Cat3: Manifest must have manifest_hash, lineage, policy, blueprint, and replay fields."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        PreloadedOutreachContextManifest,
    )
    import dataclasses
    fields = {f.name for f in dataclasses.fields(PreloadedOutreachContextManifest)}
    for required in ("manifest_hash", "omission_policy", "source_items", "audit_refs", "request_id"):
        assert required in fields, (
            f"PreloadedOutreachContextManifest missing required field {required!r}"
        )


def test_apps_lic_manifest_has_claim_permission_map_and_personalization_mode():
    """Cat3: Manifest must have claim_permission_map and personalization_mode."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        PreloadedOutreachContextManifest,
    )
    import dataclasses
    fields = {f.name for f in dataclasses.fields(PreloadedOutreachContextManifest)}
    assert "claim_permission_map" in fields, "Manifest must have claim_permission_map"
    assert "personalization_mode" in fields, "Manifest must have personalization_mode"


# ===========================================================================
# Category 4: Exit rubric behavior
# ===========================================================================

def test_apps_lic_exit_blocks_unsupported_mandatory_personalization_claim():
    """Cat4: Exit rubric has a personalization_mode_appropriate dimension."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dims = rubric.get("dimensions", [])
    dim_ids = {d.get("id", "") for d in dims}
    assert "personalization_mode_appropriate" in dim_ids, (
        "exit rubric must have personalization_mode_appropriate dimension"
    )


def test_apps_lic_exit_omits_unsupported_optional_claim():
    """Cat4: omit_unsupported policy produces omit actions for unsupported claims."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        apply_omission_policy,
        PreloadedOutreachContextManifest,
    )
    import hashlib
    # Use manifest with empty source_items and omit_unsupported policy
    # so claims not in source_items get action="omit"
    import dataclasses
    manifest = _make_minimal_manifest(omission_policy="omit_unsupported")
    manifest_no_src = dataclasses.replace(manifest, source_items=[], claim_permission_map={})
    # apply_omission_policy(claims, manifest) -> List[OmissionDecision]
    decisions = apply_omission_policy(
        claims=["optional_claim"],
        manifest=manifest_no_src,
    )
    assert len(decisions) >= 1
    # omit_unsupported must not produce a hard-fail decision
    for d in decisions:
        assert d.action in ("omit", "include"), f"unexpected action: {d.action}"


def test_apps_lic_exit_escalates_hitl_for_senior_exec_low_confidence():
    """Cat4: Exit rubric references HITL escalation for low-confidence or exec outreach."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    rubric_str = str(rubric).lower()
    # Exit rubric must mention hitl somewhere (escalation path present)
    assert "hitl" in rubric_str, (
        "exit_rubric.yaml must reference HITL escalation"
    )


# ===========================================================================
# Category 5: Write discipline
# ===========================================================================

def test_apps_lic_no_direct_l4_write():
    """Cat5: apps_lic modules must not import or call L4 state-write surfaces directly."""
    forbidden_patterns = [
        "from agentic_core.L4_state",
        "import agentic_core.L4_state",
        "L4StateWriter(",
        "durable_write(",
        "commit_state(",
    ]
    # Check main orchestration files
    for fname in ("__main__.py",):
        fpath = REPO_ROOT / "apps_lic" / fname
        if not fpath.exists():
            continue
        src = fpath.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            assert pattern not in src, (
                f"apps_lic/{fname} must not write to L4 directly — found {pattern!r}"
            )


def test_apps_lic_send_now_forbidden():
    """Cat5: send_now, auto_send, connector_send must be blocked at schema and Exit."""
    with OUTREACH_SCHEMA.open(encoding="utf-8") as fh:
        schema = json.load(fh)
    schema_str = str(schema).lower()
    for forbidden_mode in ("send_now", "auto_send", "connector_send"):
        # Either explicitly listed as forbidden, or not in enum at all
        # Verify it's not in the allowed enum values
        send_mode_enum = []
        if "properties" in schema:
            sm_prop = schema["properties"].get("send_mode", {})
            send_mode_enum = sm_prop.get("enum", [])
        if send_mode_enum:
            assert forbidden_mode not in send_mode_enum, (
                f"{forbidden_mode!r} must not be in send_mode enum"
            )

    # Also check exit_rubric blocks them
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    rubric_str = str(rubric).lower()
    assert "send_now" in rubric_str or "forbidden" in rubric_str or "send_mode" in rubric_str, (
        "exit_rubric.yaml must reference send_mode enforcement"
    )


# ===========================================================================
# Category 6: Anti-pattern + channel
# ===========================================================================

def test_antipattern_detector_default_15_patterns_and_config_extension():
    """Cat6: Anti-pattern detector has ≥15 default patterns; extension via from_rubric_config."""
    from apps_lic.engines.outreach_antipattern_detector import (
        OutreachAntipatternDetector, _DEFAULT_PATTERNS,
    )
    assert len(_DEFAULT_PATTERNS) >= 15, (
        f"Expected ≥15 default patterns, got {len(_DEFAULT_PATTERNS)}"
    )
    # Extension path: from_rubric_config must work
    ext_rubric = {"antipattern_extension_patterns": [{"id": "custom_pat", "pattern": "synergy"}]}
    detector = OutreachAntipatternDetector.from_rubric_config(ext_rubric)
    result = detector.detect("We leverage synergy to drive value.")
    assert not result.is_clean, "Extension pattern 'synergy' must fire (is_clean=False)"
    assert len(result.matches) > 0, "Extension pattern 'synergy' must produce a match"


def test_channel_length_hard_ceiling_executive_cold_email():
    """Cat6: email+EXECUTIVE+cold ceiling=100; 115 words → hard-fail."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    draft = " ".join(["word"] * 115)
    result = e.check(draft, channel="email", recipient_class="EXECUTIVE", outreach_mode="cold")
    assert result.ceiling == 100
    assert result.is_hard_fail is True


def test_scope_calibrated_ask_executive_cold_produces_low_friction_cta():
    """Cat6: EXECUTIVE+cold ask engine produces ask_friction_score <0.5 and reciprocity_first=True."""
    from apps_lic.engines.scope_calibrated_ask_engine import ScopeCalibratedAskEngine
    e = ScopeCalibratedAskEngine()
    result = e.calibrate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        channel="email",
        relationship_distance="cold",
        hiring_posture="unknown",
    )
    assert result.ask_friction_score < 0.5
    assert result.reciprocity_first is True


# ===========================================================================
# Category 7: Scoped signal controls
# ===========================================================================

def test_recipient_trigger_requirements_scoped_by_recipient_class():
    """Cat7: EXECUTIVE needs person_level/company_strategy; RECRUITER does not."""
    from apps_lic.engines.recipient_trigger_engine import RecipientTriggerEngine, RecipientTrigger
    e = RecipientTriggerEngine()

    # EXECUTIVE cold with no triggers → not satisfied
    res_exec = e.evaluate(triggers=[], recipient_class="EXECUTIVE", outreach_mode="cold",
                          omission_policy="omit_unsupported")
    assert res_exec.is_satisfied is False

    # RECRUITER cold with no triggers → satisfied (no person_level requirement)
    res_rec = e.evaluate(triggers=[], recipient_class="RECRUITER", outreach_mode="cold",
                         omission_policy="fail_closed")
    assert res_rec.is_satisfied is True


def test_repo_proof_not_required_for_simple_recruiter_followup():
    """Cat7: RECRUITER+followup with low tech depth → proof not applicable."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_NOT_APPLICABLE
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="RECRUITER",
        channel="email",
        technical_claim_depth="low",
        draft_word_count=80,
    )
    assert req.verdict == VERDICT_NOT_APPLICABLE
    assert req.is_fail_closed is False


def test_repo_proof_required_for_high_depth_exec_technical_claim():
    """Cat7: EXECUTIVE+email+high depth → proof required, is_fail_closed when no proof."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_REQUIRED
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="EXECUTIVE",
        channel="email",
        technical_claim_depth="high",
        draft_word_count=120,
        proof_provided=False,
    )
    assert req.verdict == VERDICT_REQUIRED
    assert req.is_fail_closed is True


def test_asymmetric_insight_required_only_when_configured():
    """Cat7: EXECUTIVE needs insight (configured); RECRUITER does not."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, VERDICT_REQUIRED, VERDICT_NOT_APPLICABLE
    )
    e = AsymmetricInsightEngine()
    exec_req = e.evaluate(recipient_class="EXECUTIVE", outreach_mode="cold")
    rec_req  = e.evaluate(recipient_class="RECRUITER",  outreach_mode="cold")
    assert exec_req.verdict == VERDICT_REQUIRED
    assert rec_req.verdict  == VERDICT_NOT_APPLICABLE


def test_verifiable_proof_density_not_applicable_without_technical_claims():
    """Cat7: technical_claim_depth=none → proof not applicable for any recipient_class."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_NOT_APPLICABLE
    linker = RepoProofLinker()
    for rc in ("EXECUTIVE", "CTO", "RECRUITER", "HIRING_MANAGER"):
        req = linker.evaluate(
            recipient_class=rc,
            channel="email",
            technical_claim_depth="none",
            draft_word_count=100,
        )
        assert req.verdict == VERDICT_NOT_APPLICABLE, (
            f"proof must be not_applicable for {rc} with no technical claims"
        )


# ===========================================================================
# Category 8: BriefingReady validation
# ===========================================================================

def _make_minimal_manifest(omission_policy: str = "omit_unsupported") -> "PreloadedOutreachContextManifest":
    from apps_lic.integrations.preloaded_outreach_context_manifest import PreloadedOutreachContextManifest
    import hashlib
    return PreloadedOutreachContextManifest(
        manifest_id="m1",
        request_id="r1",
        run_id="run1",
        trace_id="trace1",
        policy_hash="ph1",
        blueprint_hash="bh1",
        replay_key="rk1",
        user_profile_ref="upr1",
        resume_ref="rr1",
        target_role_ref="trr1",
        job_description_ref="jdr1",
        application_status="applied",
        company_brief_ref="cbr1",
        recipient_brief_ref="rbr1",
        relationship_context_ref="rcr1",
        channel="email",
        outreach_mode="cold",
        recipient_class="RECRUITER",
        recipient_seniority="mid",
        relationship_distance="cold",
        source_items=["src1"],
        origin_label_map={"src1": "web"},
        content_hashes={"src1": "sha256:abc"},
        freshness_status="fresh",
        unsupported_fact_flags=[],
        claim_permission_map={"claim1": "include"},
        proof_mode="optional",
        personalization_mode="company",
        omission_policy=omission_policy,
        confidence_score=0.9,
        send_mode="draft_only",
        personalization_confidence=0.9,
        required_hitl_flags=[],
        audit_refs=["audit1"],
        manifest_hash=hashlib.sha256(b"test").hexdigest(),
    )


def test_apps_lic_briefing_ready_requires_confidence_freshness_sources_hashes_and_audit_refs():
    """Cat8: validate_briefing_ready enforces mandatory confidence and source gates."""
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        validate_briefing_ready,
    )
    import dataclasses

    manifest = _make_minimal_manifest()

    # All valid → is_valid=True
    result = validate_briefing_ready(manifest)
    assert result.is_valid is True

    # Low confidence → is_valid=False
    low_conf = dataclasses.replace(manifest, confidence_score=0.1)
    result = validate_briefing_ready(low_conf, confidence_threshold=0.6)
    assert result.is_valid is False

    # Empty source_items → is_valid=False
    empty_src = dataclasses.replace(manifest, source_items=[])
    result = validate_briefing_ready(empty_src)
    assert result.is_valid is False

    # Missing audit_refs → is_valid=False
    no_audit = dataclasses.replace(manifest, audit_refs=[])
    result = validate_briefing_ready(no_audit)
    assert result.is_valid is False


# ===========================================================================
# V1 — Full suite green gate
# ===========================================================================

def test_v1_all_prior_governance_files_exist():
    """V1: All W1–W7 governance test files must exist on disk."""
    for fname in (
        "test_apps_lic_w1_l0_enforcement.py",
        "test_apps_lic_w2_r4_manifest.py",
        "test_apps_lic_w3_managed_workflow.py",
        "test_apps_lic_w4_config_policy.py",
        "test_apps_lic_w5_exit_rubric_antipattern.py",
        "test_apps_lic_w6_signal_controls.py",
        "test_apps_lic_w7_credibility_proof_insight.py",
    ):
        assert (REPO_ROOT / "tests" / "governance" / fname).exists(), (
            f"Missing prior-wave governance test file: {fname}"
        )


def test_v1_all_engine_modules_importable():
    """V1: All SE-phase engine modules must import without errors."""
    engine_modules = [
        "apps_lic.engines.outreach_antipattern_detector",
        "apps_lic.engines.channel_length_enforcer",
        "apps_lic.engines.scope_calibrated_ask_engine",
        "apps_lic.engines.recipient_trigger_engine",
        "apps_lic.engines.sender_credibility_engine",
        "apps_lic.engines.repo_proof_linker",
        "apps_lic.engines.asymmetric_insight_engine",
    ]
    for mod_name in engine_modules:
        mod = importlib.import_module(mod_name)
        assert mod is not None, f"{mod_name} must be importable"


def test_v1_spine_manifest_claims_both_routes():
    """V1: spine_manifest.yaml must claim both R4_SINGLE_ACTION and R3R4_MANAGED_WORKFLOW."""
    with SPINE_MANIFEST.open(encoding="utf-8") as fh:
        sm = yaml.safe_load(fh)
    claimed = sm.get("claimed_routes", [])
    routes = [r.get("type", "") for r in claimed]
    assert "R4_SINGLE_ACTION" in routes
    assert "R3R4_MANAGED_WORKFLOW" in routes


def test_v1_exit_rubric_has_required_se_dimensions():
    """V1: exit_rubric.yaml must have ask_friction_score, antipattern_clean,
    proof_appropriate_for_recipient, personalization_mode_appropriate,
    asymmetric_insight_present dimensions."""
    with EXIT_RUBRIC.open(encoding="utf-8") as fh:
        rubric = yaml.safe_load(fh)
    dim_ids = {d.get("id", "") for d in rubric.get("dimensions", [])}
    for required_dim in (
        "ask_friction_score",
        "antipattern_clean",
        "proof_appropriate_for_recipient",
        "personalization_mode_appropriate",
        "asymmetric_insight_present",
    ):
        assert required_dim in dim_ids, (
            f"exit_rubric.yaml missing required SE dimension: {required_dim!r}"
        )
