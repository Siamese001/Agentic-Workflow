"""X1D judge transport parity contract — shared across apps_rg proof judge providers.

Audits that Gemini, OpenAI, and Claude receive the same grading objectives, user packet,
score normalization, and comparable token/JSON/system constraints. Transport-only API deltas
(responseSchema vs json_object) are allowed when documented.

Transport wiring audits (system/json/truncation/token parity) delegate to the
apps_rg X1D panel harness via :mod:`apps_rg.runtime.judges.x1d_panel_preflight`.
Legacy ``inspect.getsource`` checks are deprecated for provider transport profile fields.
"""

from __future__ import annotations

import ast
import inspect
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import (
    ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS,
    GEMINI_JUDGE_RESPONSE_SCHEMA,
    GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS,
    JUDGE_COMPACT_OUTPUT,
    JUDGE_COMPACT_SYSTEM,
    JUDGE_REQUIRED_FIELDS,
    JUDGE_SCORE_SCHEMA,
    PROVIDERS,
    _call_anthropic,
    _call_gemini,
    _call_openai,
    _make_model_backed_output,
    _resolved_openai_judge_max_completion_tokens,
    run_llm_judges,
)
from apps_rg.runtime.section_judge_policy import (
    REQUIRED_JUDGE_PROVIDER_KEYS,
    get_section_judge_policy,
)
from apps_rg.runtime.section_model_limits import SectionModelSSOTError, runtime_limit_int

PROOF_JUDGE_PROVIDER_KEYS: tuple[str, ...] = REQUIRED_JUDGE_PROVIDER_KEYS

UNIFIED_MAX_OUTPUT_TOKENS_SSOT_PATH = "runtime_limits.judge.x1d_max_output_tokens"
UNIFIED_MAX_OUTPUT_TOKENS_DEFAULT = runtime_limit_int("judge.x1d_max_output_tokens")

GRADE_ONLY_OBJECTIVE_MARKERS: tuple[str, ...] = (
    "grade_only",
    "do not write",
    "do not rewrite",
    "targeting context only",
    "never proof",
    "deterministic_gate_summary",
)

PACKET_REQUIRED_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {
        "judge_task",
        "section",
        "candidate_output",
        "proof_boundary",
        "deterministic_gate_summary",
    }
)

PROOF_BOUNDARY_REQUIRED_FLAGS: dict[str, bool] = {
    "jd_is_targeting_context_only": True,
    "briefing_is_targeting_context_only": True,
    "judges_must_not_rewrite": True,
}


@dataclass(frozen=True)
class TransportViolation:
    code: str
    detail: str
    path: str = ""


@dataclass(frozen=True)
class ProviderTransportProfile:
    provider_key: str
    max_output_tokens: int
    system_includes_score_schema: bool
    system_includes_compact_output: bool
    system_includes_compact_system: bool
    has_json_output_lock: bool
    temperature_is_low: bool
    checks_truncation_stop_reason: bool


def resolved_provider_max_output_tokens(provider_key: str, *, attempt: int = 1) -> int:
    """Resolved max output token budget — unified across Gemini, OpenAI, and Anthropic."""
    from apps_rg.runtime.judges.executive_summary_x1d import _resolved_x1d_judge_max_output_tokens

    if provider_key in PROOF_JUDGE_PROVIDER_KEYS:
        return _resolved_x1d_judge_max_output_tokens(attempt=attempt)
    return 0


def _call_uses_shared_judge_system(fn: Any) -> bool:
    src = inspect.getsource(fn)
    return "build_x1d_judge_system_prompt" in src or "JUDGE_SCORE_SCHEMA" in src


def build_provider_transport_profile(provider_key: str) -> ProviderTransportProfile:
    """Static profile from _call_* source (transport wiring SSOT for tests)."""
    if provider_key == "gemini_pro":
        src = inspect.getsource(_call_gemini)
        mod_src = Path(__file__).with_name("executive_summary_x1d.py").read_text(encoding="utf-8")
        shared = _call_uses_shared_judge_system(_call_gemini)
        return ProviderTransportProfile(
            provider_key=provider_key,
            max_output_tokens=resolved_provider_max_output_tokens(provider_key, attempt=1),
            system_includes_score_schema=shared or "JUDGE_SCORE_SCHEMA" in mod_src,
            system_includes_compact_output=shared or "JUDGE_COMPACT_OUTPUT" in mod_src,
            system_includes_compact_system=shared or "JUDGE_COMPACT_SYSTEM" in mod_src,
            has_json_output_lock="_gemini_generation_config" in src
            or "responseSchema" in mod_src,
            temperature_is_low="_gemini_generation_config" in src,
            checks_truncation_stop_reason="finishReason" in mod_src,
        )
    if provider_key == "openai_chatgpt":
        src = inspect.getsource(_call_openai)
        shared = _call_uses_shared_judge_system(_call_openai)
        return ProviderTransportProfile(
            provider_key=provider_key,
            max_output_tokens=resolved_provider_max_output_tokens(provider_key, attempt=1),
            system_includes_score_schema=shared or "JUDGE_SCORE_SCHEMA" in src,
            system_includes_compact_output=shared or "JUDGE_COMPACT_OUTPUT" in src,
            system_includes_compact_system=shared or "JUDGE_COMPACT_SYSTEM" in src,
            has_json_output_lock="json_object" in src,
            temperature_is_low=(
                '"temperature": 0.1' in src
                or "_is_openai_gpt5_chat_model" in src  # GPT-5 family: temperature omitted (not elevated)
            ),
            checks_truncation_stop_reason="finish_reason" in src,
        )
    if provider_key == "anthropic_claude":
        src = inspect.getsource(_call_anthropic)
        mod_src = Path(__file__).with_name("executive_summary_x1d.py").read_text(encoding="utf-8")
        shared = _call_uses_shared_judge_system(_call_anthropic)
        return ProviderTransportProfile(
            provider_key=provider_key,
            max_output_tokens=resolved_provider_max_output_tokens(provider_key, attempt=1),
            system_includes_score_schema=shared or "JUDGE_SCORE_SCHEMA" in src,
            system_includes_compact_output=shared or "JUDGE_COMPACT_OUTPUT" in src,
            system_includes_compact_system=shared or "JUDGE_COMPACT_SYSTEM" in src,
            has_json_output_lock=shared
            or "json_object" in src
            or "structured" in src.lower()
            or "build_x1d_judge_system_prompt" in mod_src,
            temperature_is_low='"temperature": 0.1' in src,
            checks_truncation_stop_reason="stop_reason" in mod_src,
        )
    raise KeyError(provider_key)


def audit_unified_token_budget_env() -> list[TransportViolation]:
    """All providers should resolve max tokens from one YAML runtime limit."""
    violations: list[TransportViolation] = []
    try:
        configured = runtime_limit_int("judge.x1d_max_output_tokens")
    except SectionModelSSOTError as exc:  # guardian: strict SSOT load surfaced as audit failure
        violations.append(
            TransportViolation(
                code="missing_unified_x1d_max_output_tokens_ssot",
                detail=f"{UNIFIED_MAX_OUTPUT_TOKENS_SSOT_PATH} unreadable: {exc}",
                path="apps_rg/config/provider_profiles.yaml",
            )
        )
        configured = 0
    if configured <= 0:
        violations.append(
            TransportViolation(
                code="invalid_unified_x1d_max_output_tokens_ssot",
                detail=f"{UNIFIED_MAX_OUTPUT_TOKENS_SSOT_PATH} must be positive; got {configured}",
                path="apps_rg/config/provider_profiles.yaml",
            )
        )
    budgets = {k: resolved_provider_max_output_tokens(k) for k in PROOF_JUDGE_PROVIDER_KEYS}
    min_b, max_b = min(budgets.values()), max(budgets.values())
    if max_b > min_b * 2:
        violations.append(
            TransportViolation(
                code="token_budget_spread_exceeds_2x",
                detail=f"provider max_output_tokens map: {budgets}",
                path=str(x1d_path),
            )
        )
    return violations


def _core_preflight_codes(*codes: str) -> list[TransportViolation]:
    from apps_rg.runtime.judges.x1d_panel_preflight import audit_provider_transport_preflight_core

    allowed = frozenset(codes)
    return [v for v in audit_provider_transport_preflight_core() if v.code in allowed]


def audit_system_prompt_anchor_parity() -> list[TransportViolation]:
    """Score schema via core preflight; compact anchors via static provider profile."""
    violations = list(_core_preflight_codes("system_missing_score_schema"))
    for key in PROOF_JUDGE_PROVIDER_KEYS:
        p = build_provider_transport_profile(key)
        if not p.system_includes_compact_output:
            violations.append(
                TransportViolation(
                    code="system_missing_judge_compact_output",
                    detail=f"{key} _call_* does not wire JUDGE_COMPACT_OUTPUT into system path",
                    path="apps_rg/runtime/judges/executive_summary_x1d.py",
                )
            )
        if not p.system_includes_compact_system:
            violations.append(
                TransportViolation(
                    code="system_missing_judge_compact_system",
                    detail=f"{key} _call_* does not wire JUDGE_COMPACT_SYSTEM",
                    path="apps_rg/runtime/judges/executive_summary_x1d.py",
                )
            )
    return violations


def audit_json_output_lock_all_providers() -> list[TransportViolation]:
    """Delegates to agentic_core panel transport preflight (replaces inspect.getsource)."""
    return _core_preflight_codes("json_output_lock_mismatch")


def audit_truncation_guard_all_providers() -> list[TransportViolation]:
    """Delegates to agentic_core panel transport preflight (replaces module-level string grep)."""
    return _core_preflight_codes("truncation_stop_reason")


def audit_packet_grade_only_objectives(packet: dict[str, Any]) -> list[TransportViolation]:
    """Judge packet must encode GRADE_ONLY objectives and proof boundary."""
    violations: list[TransportViolation] = []
    if str(packet.get("judge_task", "")).upper() != "GRADE_ONLY":
        violations.append(
            TransportViolation(
                code="packet_not_grade_only",
                detail=f"judge_task={packet.get('judge_task')!r}",
            )
        )
    missing = sorted(PACKET_REQUIRED_TOP_LEVEL_KEYS - set(packet.keys()))
    if missing:
        violations.append(
            TransportViolation(
                code="packet_missing_required_keys",
                detail=f"missing keys: {missing}",
            )
        )
    boundary = packet.get("proof_boundary") or {}
    for flag, expected in PROOF_BOUNDARY_REQUIRED_FLAGS.items():
        if boundary.get(flag) is not expected:
            violations.append(
                TransportViolation(
                    code="proof_boundary_flag_wrong",
                    detail=f"{flag} expected {expected} got {boundary.get(flag)!r}",
                )
            )
    instruction_blob = " ".join(
        str(packet.get(k) or "")
        for k in ("grading_instruction", "grading_only_instructions", "section_specific_rubric", "rubric")
    ).lower()
    if not all(m in instruction_blob or m in json.dumps(packet).lower() for m in ("grade_only", "do not rewrite")):
        violations.append(
            TransportViolation(
                code="packet_missing_grade_only_objective_markers",
                detail="grading instructions must forbid rewrite/replacement",
            )
        )
    return violations


def audit_rendered_user_prompt_objectives_and_schema(packet: dict[str, Any], prompt: str) -> list[TransportViolation]:
    """Rendered user prompt must include gate authority, schema, and GRADE_ONLY objectives."""
    violations: list[TransportViolation] = []
    pl = prompt.lower()
    if "deterministic_gate_summary" not in pl:
        violations.append(
            TransportViolation(code="prompt_missing_gate_summary", detail="no deterministic_gate_summary block")
        )
    if "authoritative" not in pl and "do not contradict" not in pl:
        violations.append(
            TransportViolation(
                code="prompt_missing_gate_authority_language",
                detail="prompt lacks authoritative gate instruction",
            )
        )
    if "0_to_5" not in prompt and "0_to_1" not in prompt:
        violations.append(
            TransportViolation(code="prompt_missing_score_scale", detail="no score_scale in rendered prompt")
        )
    if "threshold" not in pl:
        violations.append(
            TransportViolation(code="prompt_missing_threshold", detail="no threshold in rendered prompt")
        )
    for marker in GRADE_ONLY_OBJECTIVE_MARKERS[:4]:
        if marker not in pl:
            violations.append(
                TransportViolation(
                    code="prompt_missing_grade_only_marker",
                    detail=f"missing objective marker {marker!r}",
                )
            )
            break
    return violations


def audit_run_llm_judges_single_prompt_assignment() -> list[TransportViolation]:
    """run_llm_judges must build one rendered prompt reused for every provider key."""
    src = inspect.getsource(run_llm_judges)
    if "prompt = render_packet(judge_packet)" not in src:
        return [
            TransportViolation(
                code="run_llm_judges_no_single_prompt_assign",
                detail="expected single prompt = render_packet(judge_packet) before provider loop",
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        ]
    for callee in ("_call_openai", "_call_anthropic", "_call_gemini"):
        if callee not in src:
            continue
        if "_prompt=prompt" not in src.replace(" ", ""):
            return [
                TransportViolation(
                    code="provider_loop_may_not_share_prompt",
                    detail=f"{callee} may not receive shared prompt= variable",
                    path="apps_rg/runtime/judges/executive_summary_x1d.py",
                )
            ]
    return []


def audit_gemini_schema_covers_required_fields() -> list[TransportViolation]:
    """Gemini responseSchema required fields must cover JUDGE_REQUIRED_FIELDS."""
    required = set(GEMINI_JUDGE_RESPONSE_SCHEMA.get("required") or [])
    missing = [f for f in JUDGE_REQUIRED_FIELDS if f not in required]
    if missing:
        return [
            TransportViolation(
                code="gemini_schema_missing_required_fields",
                detail=f"schema missing {missing}",
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        ]
    return []


def audit_score_normalization_provider_neutral() -> list[TransportViolation]:
    """Same score/threshold/scale must produce identical pass math for all providers."""
    cases = (
        (4.2, 4.0, "0_to_5", False, True),
        (3.5, 4.0, "0_to_5", False, False),
        (0.85, 0.8, "0_to_1", False, True),
        (0.9, 0.8, "0_to_1", True, False),
    )
    gate_summary = {"x2_gate": {"pass": True, "detail": "ok"}}
    for raw_score, raw_threshold, scale, decisive, _expected_pass in cases:
        statuses: dict[str, bool] = {}
        for key in PROOF_JUDGE_PROVIDER_KEYS:
            body = {
                "score_scale": scale,
                "score": raw_score,
                "threshold": raw_threshold,
                "pass": raw_score >= raw_threshold,
                "decisive_failure": decisive,
                "findings": [],
                "cited_sentence_indexes": [],
                "remediation_suggestions": [],
            }
            out = _make_model_backed_output(
                key, "h", "m", body, deterministic_gate_summary=gate_summary
            )
            statuses[key] = out.pass_
        if len(set(statuses.values())) != 1:
            return [
                TransportViolation(
                    code="score_normalization_provider_divergence",
                    detail=f"case score={raw_score} thr={raw_threshold} scale={scale} decisive={decisive} -> {statuses}",
                )
            ]
    return []


def audit_policy_sections_proof_judge_roster() -> list[TransportViolation]:
    """Proof sections must use a non-empty CROSS-PROVIDER roster that excludes the generator family.

    Recalibrated 2026-06-08: Claude Sonnet 4.6 is the generator for every lane, so ``anthropic_claude``
    must NOT appear in any judge roster (a self-judge shares the generator's blind spots). Each roster
    must be a non-empty subset of the available proof providers (``PROOF_JUDGE_PROVIDER_KEYS``). Panel
    SIZE is per-section policy (the 3-provider panel was PROVIDER_MODEL-era and is no longer required).
    """
    violations: list[TransportViolation] = []
    available = frozenset(PROOF_JUDGE_PROVIDER_KEYS)
    for section in (
        "executive_summary",
        "headline",
        "unify_bullets",
        "ibm_bullets",
        "unify_narrative",
        "ibm_narrative",
    ):
        policy = get_section_judge_policy(section)
        if not policy.judge_required_for_proof:
            continue
        roster = frozenset(policy.required_judge_providers)
        if not roster:
            violations.append(
                TransportViolation(
                    code="section_judge_roster_empty",
                    detail=f"{section} requires proof judges but has an empty roster",
                    path="apps_rg/runtime/section_judge_policy.py",
                )
            )
            continue
        unknown = roster - available
        if unknown:
            violations.append(
                TransportViolation(
                    code="section_judge_roster_unknown_provider",
                    detail=f"{section} roster has unknown providers {sorted(unknown)}",
                    path="apps_rg/runtime/section_judge_policy.py",
                )
            )
        if "anthropic_claude" in roster:
            violations.append(
                TransportViolation(
                    code="section_judge_self_judge",
                    detail=f"{section} roster includes anthropic_claude — self-judge (Claude is the generator)",
                    path="apps_rg/runtime/section_judge_policy.py",
                )
            )
    return violations


def audit_providers_registry_complete() -> list[TransportViolation]:
    """PROVIDERS registry must define every required proof panel key.

    Extra provider implementations may remain available for explicit overrides; the
    proof roster is governed by ``PROOF_JUDGE_PROVIDER_KEYS``.
    """
    reg = frozenset(PROVIDERS.keys())
    expected = frozenset(PROOF_JUDGE_PROVIDER_KEYS)
    missing = expected - reg
    if missing:
        return [
            TransportViolation(
                code="providers_registry_mismatch",
                detail=f"PROVIDERS missing required proof keys {sorted(missing)} from {sorted(expected)}",
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        ]
    return []


def audit_openai_retry_system_escalation_only() -> list[TransportViolation]:
    """Document: only OpenAI changes system prompt on attempt>=2 (parity risk)."""
    src = inspect.getsource(_call_openai)
    if "attempt >= 2" in src and "compact" in src:
        return [
            TransportViolation(
                code="openai_retry_system_prompt_asymmetry",
                detail=(
                    "OpenAI escalates system prompt on attempt>=2 (JUDGE_COMPACT_OUTPUT); "
                    "Gemini/Anthropic do not — retry semantics differ across providers."
                ),
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        ]
    return []


def audit_x1d_judge_transport_parity(
    packet: dict[str, Any] | None = None,
    *,
    prompt: str | None = None,
) -> list[TransportViolation]:
    """Full transport parity audit (provider wiring + packet objectives)."""
    from apps_rg.runtime.judges.executive_summary_judge_packet import render_judge_prompt_from_packet
    from apps_rg.runtime.sections.executive_summary_x1d_judge_contract import (
        build_brown_brown_six_sentence_packet,
    )

    pkt = packet or build_brown_brown_six_sentence_packet()
    rendered = prompt or render_judge_prompt_from_packet(pkt)
    violations: list[TransportViolation] = []
    violations.extend(audit_unified_token_budget_env())
    violations.extend(audit_system_prompt_anchor_parity())
    violations.extend(audit_json_output_lock_all_providers())
    violations.extend(audit_truncation_guard_all_providers())
    violations.extend(audit_packet_grade_only_objectives(pkt))
    violations.extend(audit_rendered_user_prompt_objectives_and_schema(pkt, rendered))
    violations.extend(audit_run_llm_judges_single_prompt_assignment())
    violations.extend(audit_gemini_schema_covers_required_fields())
    violations.extend(audit_score_normalization_provider_neutral())
    violations.extend(audit_policy_sections_proof_judge_roster())
    violations.extend(audit_providers_registry_complete())
    violations.extend(audit_openai_retry_system_escalation_only())
    return violations


def assert_x1d_judge_transport_parity(
    packet: dict[str, Any] | None = None,
    *,
    prompt: str | None = None,
) -> None:
    violations = audit_x1d_judge_transport_parity(packet, prompt=prompt)
    if violations:
        lines = "\n".join(f"  [{v.code}] {v.detail}" for v in violations)
        raise AssertionError(f"X1D judge transport parity violations:\n{lines}")


__all__ = [
    "GRADE_ONLY_OBJECTIVE_MARKERS",
    "PROOF_BOUNDARY_REQUIRED_FLAGS",
    "PROOF_JUDGE_PROVIDER_KEYS",
    "ProviderTransportProfile",
    "TransportViolation",
    "UNIFIED_MAX_OUTPUT_TOKENS_DEFAULT",
    "UNIFIED_MAX_OUTPUT_TOKENS_SSOT_PATH",
    "assert_x1d_judge_transport_parity",
    "audit_gemini_schema_covers_required_fields",
    "audit_json_output_lock_all_providers",
    "audit_packet_grade_only_objectives",
    "audit_policy_sections_proof_judge_roster",
    "audit_rendered_user_prompt_objectives_and_schema",
    "audit_score_normalization_provider_neutral",
    "audit_system_prompt_anchor_parity",
    "audit_truncation_guard_all_providers",
    "audit_unified_token_budget_env",
    "audit_x1d_judge_transport_parity",
    "build_provider_transport_profile",
    "resolved_provider_max_output_tokens",
]
