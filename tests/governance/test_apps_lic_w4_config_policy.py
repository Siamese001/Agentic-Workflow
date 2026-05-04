"""W4 sentinel tests for apps_lic config, policy, identity, and PA compiler.

Covers P10, P11, P12, P13, P14:
- P10: spine_manifest.yaml claims R4_SINGLE_ACTION + R3R4_MANAGED_WORKFLOW.
- P11: intake_policy.yaml has E1-E4; l0_policy.yaml has U0_REJECTION + 4 routes.
- P12: lic_plan_rules.yaml has channel_rules + pa_compiler_slots;
        outreach_schema.json has send_mode enum and 'not' forbidden constraint.
- P13: R5ReasonCode has 14 values; decide_route_full handles all policy gates;
        lic_identity_resolver resolves sender identity and rejects forbidden modes.
- P14: LicPACompiler returns CompiledPrompt with 8 slots;
        forbidden send_mode rejected; DATA fences present in C0/D0;
        render() produces non-empty string.

Plan: apps-lic-canonical-spine-wireup-e7c2a5 W4.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SPINE_MANIFEST = REPO_ROOT / "apps_lic" / "spine_manifest.yaml"
INTAKE_POLICY  = REPO_ROOT / "apps_lic" / "config" / "intake_policy.yaml"
L0_POLICY      = REPO_ROOT / "apps_lic" / "config" / "l0_policy.yaml"
PLAN_RULES     = REPO_ROOT / "apps_lic" / "config" / "lic_plan_rules.yaml"
OUTREACH_SCHEMA = REPO_ROOT / "apps_lic" / "config" / "outreach_schema.json"
PA_COMPILER_MODULE = REPO_ROOT / "apps_lic" / "prompt_assembly" / "lic_pa_compiler.py"
IDENTITY_MODULE    = REPO_ROOT / "apps_lic" / "integrations" / "lic_identity_resolver.py"
R5_POLICY_MODULE   = REPO_ROOT / "apps_lic" / "integrations" / "lic_r5_policy.py"


# ---------------------------------------------------------------------------
# P10 — spine_manifest.yaml
# ---------------------------------------------------------------------------

def test_spine_manifest_claims_r4_single_action():
    """P10: spine_manifest.yaml must claim R4_SINGLE_ACTION."""
    with SPINE_MANIFEST.open(encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)
    route_types = [r["type"] for r in manifest.get("claimed_routes", [])]
    assert "R4_SINGLE_ACTION" in route_types, (
        f"spine_manifest.yaml must claim R4_SINGLE_ACTION. Found: {route_types}"
    )


def test_spine_manifest_claims_r3r4_managed_workflow():
    """P10: spine_manifest.yaml must claim R3R4_MANAGED_WORKFLOW."""
    with SPINE_MANIFEST.open(encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)
    route_types = [r["type"] for r in manifest.get("claimed_routes", [])]
    assert "R3R4_MANAGED_WORKFLOW" in route_types, (
        f"spine_manifest.yaml must claim R3R4_MANAGED_WORKFLOW. Found: {route_types}"
    )


def test_spine_manifest_r4_not_sole_route():
    """P10: spine_manifest.yaml must have 2+ routes (not R3_grounded_read-only)."""
    with SPINE_MANIFEST.open(encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)
    routes = manifest.get("claimed_routes", [])
    assert len(routes) >= 2, (
        f"spine_manifest must declare at least 2 routes. Found {len(routes)}."
    )


# ---------------------------------------------------------------------------
# P11 — intake_policy.yaml
# ---------------------------------------------------------------------------

def test_intake_policy_exists():
    """P11: intake_policy.yaml must exist."""
    assert INTAKE_POLICY.exists(), f"Missing: {INTAKE_POLICY}"


def test_intake_policy_has_e1_to_e4():
    """P11: intake_policy.yaml must define exit conditions E1, E2, E3, E4."""
    with INTAKE_POLICY.open(encoding="utf-8") as fh:
        policy = yaml.safe_load(fh)
    exits = policy.get("exit_conditions", {})
    for eid in ("E1", "E2", "E3", "E4"):
        assert eid in exits, f"intake_policy.yaml missing exit condition {eid}"


def test_intake_policy_e1_is_not_r5():
    """P11: E1 (schema validation failure) must set produces_r5=false."""
    with INTAKE_POLICY.open(encoding="utf-8") as fh:
        policy = yaml.safe_load(fh)
    e1 = policy["exit_conditions"]["E1"]
    assert e1.get("produces_r5") is False, (
        "E1 schema validation failure must NOT produce an R5 — it is exit_code=2."
    )


def test_intake_policy_e2_forbidden_send_modes():
    """P11: E2 must list all 3 forbidden send modes."""
    with INTAKE_POLICY.open(encoding="utf-8") as fh:
        policy = yaml.safe_load(fh)
    e2 = policy["exit_conditions"]["E2"]
    forbidden = set(e2.get("forbidden_values", []))
    expected = {"send_now", "auto_send", "connector_send"}
    missing = expected - forbidden
    assert not missing, f"E2 missing forbidden send modes: {missing}"


def test_l0_policy_exists():
    """P11: l0_policy.yaml must exist."""
    assert L0_POLICY.exists(), f"Missing: {L0_POLICY}"


def test_l0_policy_has_u0_rejection():
    """P11: l0_policy.yaml must have U0_REJECTION as exit_code=2 (not R5)."""
    with L0_POLICY.open(encoding="utf-8") as fh:
        policy = yaml.safe_load(fh)
    routes = {r["id"]: r for r in policy["route_decision"]["routes"]}
    assert "U0_REJECTION" in routes
    u0 = routes["U0_REJECTION"]
    assert u0.get("exit_code") == 2
    assert u0.get("produces_r5") is False


def test_l0_policy_has_four_main_routes():
    """P11: l0_policy.yaml must define R3_SIMPLE_GROUNDED_READ, R4_SINGLE_ACTION, R3R4_MANAGED_WORKFLOW, R5_FALLBACK."""
    with L0_POLICY.open(encoding="utf-8") as fh:
        policy = yaml.safe_load(fh)
    ids = {r["id"] for r in policy["route_decision"]["routes"]}
    expected = {"R3_SIMPLE_GROUNDED_READ", "R4_SINGLE_ACTION", "R3R4_MANAGED_WORKFLOW", "R5_FALLBACK"}
    missing = expected - ids
    assert not missing, f"l0_policy.yaml missing routes: {missing}"


def test_l0_policy_r5_has_all_failure_conditions():
    """P11: R5_FALLBACK in l0_policy.yaml must list all research failure conditions."""
    with L0_POLICY.open(encoding="utf-8") as fh:
        policy = yaml.safe_load(fh)
    r5 = next(r for r in policy["route_decision"]["routes"] if r["id"] == "R5_FALLBACK")
    cond_names = {list(c.keys())[0] for c in r5.get("conditions", [])}
    expected_subset = {
        "briefing_missing_research_not_authorized",
        "apps_research_failed",
        "apps_research_empty",
        "apps_research_blocked",
        "apps_research_stale",
        "apps_research_weak_support",
    }
    missing = expected_subset - cond_names
    assert not missing, f"l0_policy.yaml R5 missing conditions: {missing}"


# ---------------------------------------------------------------------------
# P12 — lic_plan_rules.yaml + outreach_schema.json
# ---------------------------------------------------------------------------

def test_plan_rules_exists():
    """P12: lic_plan_rules.yaml must exist."""
    assert PLAN_RULES.exists(), f"Missing: {PLAN_RULES}"


def test_plan_rules_has_channel_rules():
    """P12: lic_plan_rules.yaml must have channel_rules for email, linkedin, text."""
    with PLAN_RULES.open(encoding="utf-8") as fh:
        rules = yaml.safe_load(fh)
    channels = set(rules.get("channel_rules", {}).keys())
    assert {"email", "linkedin", "text"} <= channels


def test_plan_rules_has_pa_compiler_slots():
    """P12: lic_plan_rules.yaml must define all 8 PA compiler slots."""
    with PLAN_RULES.open(encoding="utf-8") as fh:
        rules = yaml.safe_load(fh)
    slots = set(rules.get("pa_compiler_slots", {}).keys())
    expected = {"S0", "I0", "C0", "U0", "D0", "E0", "Y0", "R0"}
    missing = expected - slots
    assert not missing, f"lic_plan_rules.yaml missing PA slots: {missing}"


def test_outreach_schema_exists():
    """P12: outreach_schema.json must exist."""
    assert OUTREACH_SCHEMA.exists(), f"Missing: {OUTREACH_SCHEMA}"


def test_outreach_schema_send_mode_enum():
    """P12: outreach_schema.json send_mode must only allow draft_only, review_required, send_ready_candidate."""
    with OUTREACH_SCHEMA.open(encoding="utf-8") as fh:
        schema = json.load(fh)
    send_mode_enum = schema["properties"]["send_mode"]["enum"]
    assert set(send_mode_enum) == {"draft_only", "review_required", "send_ready_candidate"}


def test_outreach_schema_forbids_send_now():
    """P12: outreach_schema.json 'not' constraint must forbid send_now, auto_send, connector_send."""
    with OUTREACH_SCHEMA.open(encoding="utf-8") as fh:
        schema = json.load(fh)
    not_clause = schema.get("not", {})
    forbidden = set(not_clause.get("properties", {}).get("send_mode", {}).get("enum", []))
    expected = {"send_now", "auto_send", "connector_send"}
    missing = expected - forbidden
    assert not missing, f"outreach_schema.json 'not' clause missing forbidden modes: {missing}"


def test_outreach_schema_has_omission_policy():
    """P12: outreach_schema.json must include omission_policy field."""
    with OUTREACH_SCHEMA.open(encoding="utf-8") as fh:
        schema = json.load(fh)
    assert "omission_policy" in schema["properties"]
    assert set(schema["properties"]["omission_policy"]["enum"]) == {
        "omit_unsupported", "hitl_required", "fail_closed"
    }


# ---------------------------------------------------------------------------
# P13 — R5ReasonCode (14 codes) + decide_route_full + lic_identity_resolver
# ---------------------------------------------------------------------------

def test_r5_policy_module_exists():
    """P13: lic_r5_policy.py must exist."""
    assert R5_POLICY_MODULE.exists()


def test_r5_reason_code_has_14_values():
    """P13: R5ReasonCode enum must have exactly 14 values."""
    from apps_lic.integrations.lic_r5_policy import R5ReasonCode
    assert len(R5ReasonCode) == 14, (
        f"Expected 14 R5ReasonCode values, got {len(R5ReasonCode)}: {list(R5ReasonCode)}"
    )


def test_r5_reason_code_all_required_values():
    """P13: R5ReasonCode must contain all plan-specified codes."""
    from apps_lic.integrations.lic_r5_policy import R5ReasonCode
    expected = {
        "BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED",
        "APPS_RESEARCH_FAILED",
        "APPS_RESEARCH_EMPTY",
        "APPS_RESEARCH_BLOCKED",
        "APPS_RESEARCH_STALE",
        "APPS_RESEARCH_WEAK_SUPPORT",
        "SEND_MODE_FORBIDDEN",
        "HIGH_FRICTION_ASK",
        "UNSUPPORTED_MANDATORY_CLAIMS",
        "LOW_CONFIDENCE",
        "LOW_CONFIDENCE_SENIOR_EXEC",
        "INVALID_RECIPIENT_CLASS",
        "INVALID_ROUTE_CONTRACT",
        "L0_POLICY_VIOLATION",
    }
    actual = {code.value for code in R5ReasonCode}
    missing = expected - actual
    assert not missing, f"R5ReasonCode missing values: {missing}"


def test_decide_route_full_forbidden_send_mode():
    """P13: decide_route_full → SEND_MODE_FORBIDDEN for forbidden send modes."""
    from apps_lic.integrations.lic_r5_policy import decide_route_full, R5ReasonCode
    for mode in ("send_now", "auto_send", "connector_send"):
        result = decide_route_full(
            has_fresh_briefing=True,
            research_authorized=True,
            request_is_briefing_only=False,
            send_mode=mode,
        )
        assert result.is_terminal is True
        assert result.reason_code == R5ReasonCode.SEND_MODE_FORBIDDEN.value, (
            f"Expected SEND_MODE_FORBIDDEN for {mode!r}, got {result.reason_code}"
        )


def test_decide_route_full_low_confidence():
    """P13: decide_route_full → LOW_CONFIDENCE when personalization_confidence < 0.3."""
    from apps_lic.integrations.lic_r5_policy import decide_route_full, R5ReasonCode
    result = decide_route_full(
        has_fresh_briefing=True,
        research_authorized=True,
        request_is_briefing_only=False,
        personalization_confidence=0.1,
    )
    assert result.is_terminal is True
    assert result.reason_code == R5ReasonCode.LOW_CONFIDENCE.value


def test_decide_route_full_low_confidence_senior_exec():
    """P13: decide_route_full → LOW_CONFIDENCE_SENIOR_EXEC for exec + low confidence + no generic note."""
    from apps_lic.integrations.lic_r5_policy import decide_route_full, R5ReasonCode
    result = decide_route_full(
        has_fresh_briefing=True,
        research_authorized=True,
        request_is_briefing_only=False,
        personalization_confidence=0.4,
        recipient_class="EXECUTIVE",
        has_safe_generic_note=False,
    )
    assert result.is_terminal is True
    assert result.reason_code == R5ReasonCode.LOW_CONFIDENCE_SENIOR_EXEC.value


def test_decide_route_full_high_friction_ask():
    """P13: decide_route_full → HIGH_FRICTION_ASK."""
    from apps_lic.integrations.lic_r5_policy import decide_route_full, R5ReasonCode
    result = decide_route_full(
        has_fresh_briefing=True,
        research_authorized=True,
        request_is_briefing_only=False,
        has_high_friction_ask=True,
    )
    assert result.is_terminal is True
    assert result.reason_code == R5ReasonCode.HIGH_FRICTION_ASK.value


def test_decide_route_full_happy_path_r4():
    """P13: decide_route_full → R4_SINGLE_ACTION on clean inputs with fresh briefing."""
    from apps_lic.integrations.lic_r5_policy import decide_route_full
    result = decide_route_full(
        has_fresh_briefing=True,
        research_authorized=True,
        request_is_briefing_only=False,
    )
    assert result.route_id == "R4_SINGLE_ACTION"
    assert result.is_terminal is False


def test_identity_resolver_module_exists():
    """P13: lic_identity_resolver.py must exist."""
    assert IDENTITY_MODULE.exists()


def test_identity_resolver_constants():
    """P13: Identity constants must be apps_lic canonical values."""
    from apps_lic.integrations.lic_identity_resolver import APP_NAME, SOURCE_CHANNEL, DECLARED_SCHEMA
    assert APP_NAME == "apps_lic"
    assert SOURCE_CHANNEL == "apps_lic_cli"
    assert DECLARED_SCHEMA == "apps_lic_outreach_v1"


def test_identity_resolver_success():
    """P13: resolve_sender_identity returns valid identity for correct inputs."""
    from apps_lic.integrations.lic_identity_resolver import resolve_sender_identity
    result = resolve_sender_identity(
        request_id="req-1", run_id="run-1", trace_id="tr-1",
        policy_hash="sha256:aaa", blueprint_hash="sha256:bbb", resume_ref="sha256:ccc",
        recipient_class="RECRUITER", channel="email", outreach_mode="cold",
    )
    assert result.is_valid is True
    assert result.identity is not None
    assert result.identity.app_name == "apps_lic"
    assert result.identity.source_channel == "apps_lic_cli"


def test_identity_resolver_rejects_forbidden_send_mode():
    """P13: resolve_sender_identity rejects forbidden send modes."""
    from apps_lic.integrations.lic_identity_resolver import resolve_sender_identity
    for mode in ("send_now", "auto_send", "connector_send"):
        result = resolve_sender_identity(
            request_id="r", run_id="r", trace_id="t",
            policy_hash="p", blueprint_hash="b", resume_ref="r",
            recipient_class="RECRUITER", channel="email", outreach_mode="cold",
            send_mode=mode,
        )
        assert result.is_valid is False
        assert any(mode in e for e in result.errors), (
            f"Expected error mentioning {mode!r}, got: {result.errors}"
        )


def test_identity_resolver_rejects_invalid_source_channel():
    """P13: resolve_sender_identity rejects wrong source_channel."""
    from apps_lic.integrations.lic_identity_resolver import resolve_sender_identity
    result = resolve_sender_identity(
        request_id="r", run_id="r", trace_id="t",
        policy_hash="p", blueprint_hash="b", resume_ref="r",
        recipient_class="RECRUITER", channel="email", outreach_mode="cold",
        source_channel="wrong_channel",
    )
    assert result.is_valid is False


# ---------------------------------------------------------------------------
# P14 — LicPACompiler
# ---------------------------------------------------------------------------

def test_pa_compiler_module_exists():
    """P14: lic_pa_compiler.py must exist."""
    assert PA_COMPILER_MODULE.exists()


def test_pa_compiler_slot_count():
    """P14: PROMPT_SLOTS must define exactly 8 slots."""
    from apps_lic.prompt_assembly.lic_pa_compiler import PROMPT_SLOTS, SLOT_ORDER
    assert len(PROMPT_SLOTS) == 8, f"Expected 8 slots, got {len(PROMPT_SLOTS)}"
    assert len(SLOT_ORDER) == 8


def test_pa_compiler_required_slots():
    """P14: REQUIRED_SLOTS must include S0, I0, C0, U0, D0, R0."""
    from apps_lic.prompt_assembly.lic_pa_compiler import REQUIRED_SLOTS
    expected = {"S0", "I0", "C0", "U0", "D0", "R0"}
    missing = expected - REQUIRED_SLOTS
    assert not missing, f"Missing required slots: {missing}"


def _make_mock_manifest():
    from dataclasses import dataclass, field as dc_field
    @dataclass
    class MockManifest:
        manifest_hash: str = "sha256:test001"
        confidence_score: float = 0.85
        source_items: list = dc_field(default_factory=list)
        claim_permission_map: dict = dc_field(default_factory=dict)
        omission_policy: str = "omit_unsupported"
        recipient_brief_ref: str = "Jane Smith"
        company_brief_ref: str = "Acme Corp"
        resume_ref: str = "sha256:resume001"
    return MockManifest()


def test_pa_compiler_compile_returns_compiled_prompt():
    """P14: LicPACompiler.compile() returns a valid CompiledPrompt on clean input."""
    from apps_lic.prompt_assembly.lic_pa_compiler import LicPACompiler, CompiledPrompt
    compiler = LicPACompiler()
    result = compiler.compile(
        manifest=_make_mock_manifest(),
        channel="email",
        outreach_mode="cold",
        recipient_class="RECRUITER",
        send_mode="draft_only",
    )
    assert result.is_valid is True
    assert isinstance(result.compiled_prompt, CompiledPrompt)


def test_pa_compiler_compile_has_8_slots():
    """P14: Compiled prompt must populate all 8 slot keys."""
    from apps_lic.prompt_assembly.lic_pa_compiler import LicPACompiler, SLOT_ORDER
    compiler = LicPACompiler()
    result = compiler.compile(
        manifest=_make_mock_manifest(),
        channel="email",
        outreach_mode="cold",
        recipient_class="RECRUITER",
    )
    assert result.is_valid
    for slot_id in SLOT_ORDER:
        assert slot_id in result.compiled_prompt.slots, (
            f"Compiled prompt missing slot {slot_id}"
        )


def test_pa_compiler_render_nonempty():
    """P14: CompiledPrompt.render() must produce a non-empty string."""
    from apps_lic.prompt_assembly.lic_pa_compiler import LicPACompiler
    compiler = LicPACompiler()
    result = compiler.compile(
        manifest=_make_mock_manifest(),
        channel="linkedin",
        outreach_mode="warm",
        recipient_class="HIRING_MANAGER",
    )
    assert result.is_valid
    rendered = result.compiled_prompt.render()
    assert isinstance(rendered, str)
    assert len(rendered) > 100


def test_pa_compiler_data_fences_in_c0():
    """P14: C0 slot must contain DATA fence markers for external content."""
    from apps_lic.prompt_assembly.lic_pa_compiler import LicPACompiler
    compiler = LicPACompiler()
    result = compiler.compile(
        manifest=_make_mock_manifest(),
        channel="email",
        outreach_mode="cold",
        recipient_class="EXECUTIVE",
    )
    assert result.is_valid
    c0 = result.compiled_prompt.slots["C0"]
    assert "<<<DATA" in c0, "C0 must contain <<<DATA fence"
    assert "DATA>>>" in c0, "C0 must contain DATA>>> fence"


def test_pa_compiler_data_fences_in_d0():
    """P14: D0 slot must contain injection fence language."""
    from apps_lic.prompt_assembly.lic_pa_compiler import LicPACompiler
    compiler = LicPACompiler()
    result = compiler.compile(
        manifest=_make_mock_manifest(),
        channel="email",
        outreach_mode="cold",
        recipient_class="RECRUITER",
    )
    assert result.is_valid
    d0 = result.compiled_prompt.slots["D0"]
    assert "DATA" in d0
    assert "injection" in d0.lower()


def test_pa_compiler_rejects_forbidden_send_mode():
    """P14: LicPACompiler.compile() must reject forbidden send modes."""
    from apps_lic.prompt_assembly.lic_pa_compiler import LicPACompiler
    compiler = LicPACompiler()
    for mode in ("send_now", "auto_send", "connector_send"):
        result = compiler.compile(
            manifest=_make_mock_manifest(),
            channel="email",
            outreach_mode="cold",
            recipient_class="RECRUITER",
            send_mode=mode,
        )
        assert result.is_valid is False, (
            f"Expected compile to fail for send_mode={mode!r}"
        )
        assert any(mode in e for e in result.errors)


def test_pa_compiler_no_provider_calls_in_source():
    """P14: lic_pa_compiler.py must not contain provider API imports."""
    source = PA_COMPILER_MODULE.read_text(encoding="utf-8")
    for forbidden in ("openai", "anthropic", "google.generativeai", "boto3", "llama"):
        assert forbidden not in source, (
            f"lic_pa_compiler.py must not import/reference provider: {forbidden!r}"
        )


def test_pa_compiler_claim_permission_map_in_result():
    """P14: CompiledPrompt must carry claim_permission_map from manifest."""
    from apps_lic.prompt_assembly.lic_pa_compiler import LicPACompiler
    from dataclasses import dataclass, field as dc_field

    @dataclass
    class ManifestWithClaims:
        manifest_hash: str = "sha256:cpm001"
        confidence_score: float = 0.9
        source_items: list = dc_field(default_factory=list)
        claim_permission_map: dict = dc_field(default_factory=lambda: {
            "github_link": "use",
            "salary_ask": "omit_unsupported",
        })
        omission_policy: str = "omit_unsupported"
        recipient_brief_ref: str = "Bob"
        company_brief_ref: str = "Corp"
        resume_ref: str = "sha256:r001"

    compiler = LicPACompiler()
    result = compiler.compile(
        manifest=ManifestWithClaims(),
        channel="email",
        outreach_mode="cold",
        recipient_class="RECRUITER",
    )
    assert result.is_valid
    assert result.compiled_prompt.claim_permission_map.get("salary_ask") == "omit_unsupported"
