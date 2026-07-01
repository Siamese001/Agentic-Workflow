"""X1D judge transport parity — inputs, formats, token budgets, objectives, pass math.

Fails on current wiring until exec-summary-x1d-transport-parity-d8f2a1 ships.
Sanity tests (pass today) prove divergence is transport/packet, not _make_model_backed_output.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from apps_rg.runtime.judges.executive_summary_judge_packet import (
    REQUIRED_JUDGE_OUTPUT_SCHEMA,
    judge_packet_hash,
    render_judge_prompt_from_packet,
)
from apps_rg.runtime.judges.executive_summary_x1d import (
    GEMINI_JUDGE_RESPONSE_SCHEMA,
    JUDGE_COMPACT_OUTPUT,
    JUDGE_COMPACT_SYSTEM,
    JUDGE_GRADE_ONLY_AUTHORITY,
    JUDGE_REQUIRED_FIELDS,
    JUDGE_SCORE_SCHEMA,
    build_x1d_judge_system_prompt,
    _make_model_backed_output,
    _resolved_section_x1d_judge_max_output_tokens,
    run_llm_judges,
    _section_x1d_judge_max_attempts,
)
from apps_rg.runtime.judges.grade_only_judge_packet import (
    REQUIRED_JUDGE_OUTPUT_SCHEMA as GENERIC_REQUIRED_SCHEMA,
    build_grade_only_judge_packet,
    render_judge_prompt_from_packet as render_generic_packet_prompt,
)
from apps_rg.runtime.judges.x1d_judge_transport_contract import (
    PROOF_JUDGE_PROVIDER_KEYS,
    UNIFIED_MAX_OUTPUT_TOKENS_SSOT_PATH,
    audit_gemini_schema_covers_required_fields,
    audit_json_output_lock_all_providers,
    audit_openai_retry_system_escalation_only,
    audit_packet_grade_only_objectives,
    audit_policy_sections_proof_judge_roster,
    audit_providers_registry_complete,
    audit_rendered_user_prompt_objectives_and_schema,
    audit_run_llm_judges_single_prompt_assignment,
    audit_score_normalization_provider_neutral,
    audit_system_prompt_anchor_parity,
    audit_truncation_guard_all_providers,
    audit_unified_token_budget_env,
    audit_x1d_judge_transport_parity,
    build_provider_transport_profile,
    resolved_provider_max_output_tokens,
)
from apps_rg.runtime.section_judge_policy import get_section_judge_policy
from apps_rg.runtime.sections.executive_summary_x1d_judge_contract import (
    build_brown_brown_six_sentence_packet,
    load_frozen_post_x2_packet,
)

_REPO = Path(__file__).resolve().parents[3]


def _codes(violations: list) -> list[str]:
    return [getattr(v, "code", "") for v in violations]


# --- Token budget -------------------------------------------------------------


@pytest.mark.parametrize("provider_key", PROOF_JUDGE_PROVIDER_KEYS)
def test_resolved_token_budget_at_least_2048_class(provider_key: str) -> None:
    """After W2, all providers should be in the same budget class (>=2048)."""
    budget = resolved_provider_max_output_tokens(provider_key)
    assert budget >= 2048, f"{provider_key} max_tokens={budget}"


def test_unified_token_env_wired() -> None:
    violations = audit_unified_token_budget_env()
    assert violations == [], _codes(violations)


def test_token_budget_spread_across_providers() -> None:
    budgets = {k: resolved_provider_max_output_tokens(k) for k in PROOF_JUDGE_PROVIDER_KEYS}
    assert len(set(budgets.values())) == 1, budgets


# --- System / JSON format -----------------------------------------------------


@pytest.mark.parametrize("provider_key", PROOF_JUDGE_PROVIDER_KEYS)
def test_provider_profile_json_lock(provider_key: str) -> None:
    profile = build_provider_transport_profile(provider_key)
    assert profile.has_json_output_lock, provider_key


def test_all_providers_system_score_schema_parity() -> None:
    violations = audit_system_prompt_anchor_parity()
    assert violations == [], _codes(violations)


def test_all_providers_json_output_lock() -> None:
    violations = audit_json_output_lock_all_providers()
    assert violations == [], _codes(violations)


def test_all_providers_truncation_guards() -> None:
    violations = audit_truncation_guard_all_providers()
    assert violations == [], _codes(violations)


def test_gemini_schema_required_fields_superset() -> None:
    violations = audit_gemini_schema_covers_required_fields()
    assert violations == []
    assert set(JUDGE_REQUIRED_FIELDS).issubset(set(GEMINI_JUDGE_RESPONSE_SCHEMA.get("required") or []))


# --- Packet objectives & rendered user prompt -----------------------------------


def test_exec_summary_packet_grade_only_objectives() -> None:
    packet = build_brown_brown_six_sentence_packet()
    violations = audit_packet_grade_only_objectives(packet)
    assert violations == [], _codes(violations)


def test_rendered_prompt_includes_schema_and_gate_authority() -> None:
    packet = build_brown_brown_six_sentence_packet()
    prompt = render_judge_prompt_from_packet(packet)
    violations = audit_rendered_user_prompt_objectives_and_schema(packet, prompt)
    assert violations == [], _codes(violations)
    assert "DETERMINISTIC_GATE_SUMMARY" in prompt
    assert "0_to_5" in prompt or "score_scale" in prompt.lower()
    assert REQUIRED_JUDGE_OUTPUT_SCHEMA.split("0_to_5")[0][:20] in prompt or "0_to_5" in prompt


def test_generic_section_packet_grade_only_objectives() -> None:
    packet = build_grade_only_judge_packet(
        section_id="headline",
        candidate_output={"headline_line": "SVP | Platform"},
        section_rubric="Executive presence and clarity.",
        rubric_ref="apps_rg/runtime/judges/headline_x1d.py",
        claim_ledger=[],
        targeting_context={"target_title": "SVP", "target_company": "Acme", "jd_text": "", "briefing": ""},
    )
    violations = audit_packet_grade_only_objectives(packet)
    assert violations == [], _codes(violations)
    prompt = render_generic_packet_prompt(packet)
    assert "GRADE_ONLY" in prompt.upper() or "grade_only" in prompt.lower()


# --- Pipeline: single user prompt for all providers -----------------------------


def test_run_llm_judges_assigns_one_rendered_prompt() -> None:
    violations = audit_run_llm_judges_single_prompt_assignment()
    assert violations == [], _codes(violations)


def test_run_llm_judges_passes_identical_user_prompt_to_each_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Integration: same judge_packet -> same prompt arg on every _call_*."""
    from apps_rg.runtime.judges.section_judge_profile import SectionJudgeModelResolution

    captured: dict[str, str] = {}
    packet = build_brown_brown_six_sentence_packet()
    expected_prompt = render_judge_prompt_from_packet(packet)

    def _capture(key: str):
        def _inner(*_a, prompt: str = "", **_k):
            captured[key] = prompt or (_a[1] if len(_a) > 1 else "")
            return _make_model_backed_output(
                key,
                "hash",
                "model",
                {
                    "score_scale": "0_to_5",
                    "score": 4.2,
                    "threshold": 4.0,
                    "pass": True,
                    "decisive_failure": False,
                    "findings": [],
                    "cited_sentence_indexes": [1],
                    "remediation_suggestions": [],
                },
            )

        return _inner

    def _fake_resolve(section_id: str, provider_key: str, environ=None):
        return SectionJudgeModelResolution(
            provider_key=provider_key,
            section_id=section_id,
            judge_tier="enhanced_reasoning",
            model_requested="test-model",
            model_actual="test-model",
            model_source="test",
            model_tier="enhanced_reasoning",
            proof_eligible_judge=True,
        )

    monkeypatch.setenv("GOOGLE_API_KEY", "test-google")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic")
    monkeypatch.setenv("APPS_RG_ENABLE_NETWORK_TESTS", "1")
    monkeypatch.setattr(
        "apps_rg.runtime.judges.section_judge_profile.resolve_section_proof_judge_model",
        _fake_resolve,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.judges.executive_summary_x1d._call_openai",
        _capture("openai_chatgpt"),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.judges.executive_summary_x1d._call_anthropic",
        _capture("anthropic_claude"),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.judges.executive_summary_x1d._call_gemini",
        _capture("gemini_pro"),
    )

    outputs = run_llm_judges(
        resume_display_text=packet["candidate_output"]["resume_display_text"],
        claim_ledger=packet["candidate_output"]["claim_ledger"],
        judge_keys=list(PROOF_JUDGE_PROVIDER_KEYS),
        judge_packet=packet,
        section_id="executive_summary",
    )
    assert len(outputs) == len(PROOF_JUDGE_PROVIDER_KEYS)
    assert set(captured.keys()) == set(PROOF_JUDGE_PROVIDER_KEYS)
    for key in PROOF_JUDGE_PROVIDER_KEYS:
        assert captured[key] == expected_prompt


def test_run_llm_judges_same_input_hash_all_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    """All panel judges must grade the same hashed packet (not per-provider inputs)."""
    from apps_rg.runtime.judges.section_judge_profile import SectionJudgeModelResolution

    packet = build_brown_brown_six_sentence_packet()
    expected_hash = judge_packet_hash(packet)

    def _fake_resolve(section_id: str, provider_key: str, environ=None):
        return SectionJudgeModelResolution(
            provider_key=provider_key,
            section_id=section_id,
            judge_tier="enhanced_reasoning",
            model_requested="test-model",
            model_actual="test-model",
            model_source="test",
            model_tier="enhanced_reasoning",
            proof_eligible_judge=True,
        )

    def _stub(*_a, **_k):
        input_hash = _a[3] if len(_a) > 3 else expected_hash
        provider_key = _a[4] if len(_a) > 4 else "gemini_pro"
        return _make_model_backed_output(
            provider_key,
            input_hash,
            "m",
            {
                "score_scale": "0_to_5",
                "score": 4.2,
                "threshold": 4.0,
                "pass": True,
                "decisive_failure": False,
                "findings": [],
                "cited_sentence_indexes": [1],
                "remediation_suggestions": [],
            },
        )

    monkeypatch.setenv("GOOGLE_API_KEY", "test-google")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic")
    monkeypatch.setenv("APPS_RG_ENABLE_NETWORK_TESTS", "1")
    monkeypatch.setattr(
        "apps_rg.runtime.judges.section_judge_profile.resolve_section_proof_judge_model",
        _fake_resolve,
    )
    monkeypatch.setattr("apps_rg.runtime.judges.executive_summary_x1d._call_openai", _stub)
    monkeypatch.setattr("apps_rg.runtime.judges.executive_summary_x1d._call_anthropic", _stub)
    monkeypatch.setattr("apps_rg.runtime.judges.executive_summary_x1d._call_gemini", _stub)

    outputs = run_llm_judges(
        resume_display_text=packet["candidate_output"]["resume_display_text"],
        claim_ledger=packet["candidate_output"]["claim_ledger"],
        judge_keys=list(PROOF_JUDGE_PROVIDER_KEYS),
        judge_packet=packet,
        section_id="executive_summary",
    )
    hashes = {o.provider_key: o.input_hash for o in outputs}
    assert len(set(hashes.values())) == 1
    assert next(iter(hashes.values())) == expected_hash


def test_judge_packet_hash_deterministic() -> None:
    packet = build_brown_brown_six_sentence_packet()
    assert judge_packet_hash(packet) == judge_packet_hash(packet)


@pytest.mark.parametrize("provider_key", PROOF_JUDGE_PROVIDER_KEYS)
def test_provider_uses_low_temperature(provider_key: str) -> None:
    profile = build_provider_transport_profile(provider_key)
    assert profile.temperature_is_low, provider_key


def test_openai_retry_attempt_token_budget_escalates_bounded() -> None:
    """Retry may double budget up to 8192 (reasoning SKUs consume completion cap)."""
    a1 = resolved_provider_max_output_tokens("openai_chatgpt", attempt=1)
    a2 = resolved_provider_max_output_tokens("openai_chatgpt", attempt=2)
    assert a2 >= a1
    assert a2 <= 8192


def test_section_retry_profile_is_proportional() -> None:
    assert _section_x1d_judge_max_attempts("competencies") == 2
    assert _section_x1d_judge_max_attempts("unify_bullets") == 2
    assert _section_x1d_judge_max_attempts("executive_summary") == 3

    assert _resolved_section_x1d_judge_max_output_tokens("competencies", attempt=1) == 4096
    assert _resolved_section_x1d_judge_max_output_tokens("unify_bullets", attempt=1) == 4096
    assert _resolved_section_x1d_judge_max_output_tokens("executive_summary", attempt=1) == 8192
    assert _resolved_section_x1d_judge_max_output_tokens("competencies", attempt=2) == 8192
    assert _resolved_section_x1d_judge_max_output_tokens("unify_bullets", attempt=2) == 8192
    assert _resolved_section_x1d_judge_max_output_tokens("executive_summary", attempt=2) == 8192


@pytest.mark.parametrize(
    "section_id,expected_providers",
    [
        # Claude Sonnet 4.6 base recalibration: summaries/headline -> dual cross-provider
        # panel; competencies/bullets/narratives -> single proof judge. No anthropic_claude
        # self-judge (Claude is the generator, so it cannot also be a proof judge).
        ("executive_summary", ("gemini_pro", "openai_chatgpt")),
        ("headline", ("gemini_pro", "openai_chatgpt")),
        ("competencies", ("openai_chatgpt",)),
        ("unify_bullets", ("gemini_pro",)),
        ("ibm_bullets", ("gemini_pro",)),
        ("unify_narrative", ("gemini_pro",)),
        ("ibm_narrative", ("gemini_pro",)),
    ],
)
def test_proof_section_recalibrated_judge_roster(
    section_id: str, expected_providers: tuple[str, ...]
) -> None:
    policy = get_section_judge_policy(section_id)
    assert policy.judge_required_for_proof
    assert frozenset(policy.required_judge_providers) == frozenset(expected_providers)
    assert "anthropic_claude" not in policy.required_judge_providers


# --- Score normalization (provider-neutral pass math) -------------------------


def test_score_normalization_same_pass_all_providers() -> None:
    violations = audit_score_normalization_provider_neutral()
    assert violations == []


@pytest.mark.parametrize(
    "score,threshold,scale,decisive,expected_pass",
    [
        (4.2, 4.0, "0_to_5", False, True),
        (3.5, 4.0, "0_to_5", False, False),
        (4.0, 4.0, "0_to_5", True, False),
        (0.85, 0.8, "0_to_1", False, True),
    ],
)
def test_pass_math_matrix_parametrized(
    score: float,
    threshold: float,
    scale: str,
    decisive: bool,
    expected_pass: bool,
) -> None:
    body = {
        "score_scale": scale,
        "score": score,
        "threshold": threshold,
        "pass": False,
        "decisive_failure": decisive,
        "findings": [],
        "cited_sentence_indexes": [],
        "remediation_suggestions": [],
    }
    for key in PROOF_JUDGE_PROVIDER_KEYS:
        out = _make_model_backed_output(key, "h", "m", dict(body))
        assert out.pass_ is expected_pass, key


# --- Policy / registry consistency --------------------------------------------


def test_proof_sections_share_recalibrated_judge_roster() -> None:
    violations = audit_policy_sections_proof_judge_roster()
    assert violations == [], _codes(violations)


def test_providers_registry_matches_policy() -> None:
    violations = audit_providers_registry_complete()
    assert violations == [], _codes(violations)


# --- Documented asymmetries (fail until fixed) --------------------------------


def test_openai_retry_system_prompt_parity() -> None:
    """OpenAI-only retry system escalation is a transport inconsistency."""
    violations = audit_openai_retry_system_escalation_only()
    assert violations == [], _codes(violations)


# --- Aggregate + frozen fixture -----------------------------------------------


def test_full_transport_parity_aggregate() -> None:
    violations = audit_x1d_judge_transport_parity()
    assert violations == [], "\n".join(f"[{v.code}] {v.detail}" for v in violations)


@pytest.mark.skipif(
    load_frozen_post_x2_packet(_REPO) is None,
    reason="frozen 001344 packet missing",
)
def test_frozen_001344_transport_parity() -> None:
    packet = load_frozen_post_x2_packet(_REPO)
    assert packet is not None
    prompt = render_judge_prompt_from_packet(packet)
    violations = audit_x1d_judge_transport_parity(packet, prompt=prompt)
    assert violations == [], _codes(violations)


# --- Sanity: shared contract strings exist ------------------------------------


def test_shared_judge_contract_strings_defined() -> None:
    assert "0_to_5" in JUDGE_COMPACT_OUTPUT
    assert "score_scale" in JUDGE_SCORE_SCHEMA.lower()
    assert "0_to_5" in GENERIC_REQUIRED_SCHEMA
    assert JUDGE_COMPACT_SYSTEM
    assert "retired" in JUDGE_GRADE_ONLY_AUTHORITY.lower()
    system = build_x1d_judge_system_prompt(compact=True)
    assert JUDGE_GRADE_ONLY_AUTHORITY in system


def test_gemini_retry_attempt_token_budget_matches_openai() -> None:
    g1 = resolved_provider_max_output_tokens("gemini_pro", attempt=1)
    g2 = resolved_provider_max_output_tokens("gemini_pro", attempt=2)
    o1 = resolved_provider_max_output_tokens("openai_chatgpt", attempt=1)
    o2 = resolved_provider_max_output_tokens("openai_chatgpt", attempt=2)
    assert g1 == o1
    assert g2 == o2
    assert g2 >= g1


def test_unified_token_budget_ssot_path_documented() -> None:
    assert UNIFIED_MAX_OUTPUT_TOKENS_SSOT_PATH == "runtime_limits.judge.x1d_max_output_tokens"
