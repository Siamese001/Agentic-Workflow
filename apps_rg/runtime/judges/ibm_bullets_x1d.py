"""X1D LLM judges for ibm_bullets — reuses provider adapters from executive_summary_x1d."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import (
    DEFAULT_THRESHOLD,
    JUDGE_COMPACT_OUTPUT,
    PROVIDERS,
    JudgeOutput,
    _call_anthropic,
    _call_gemini,
    _call_openai,
    _make_blocked_output,
    _resolve_anthropic_model,
    _resolve_gemini_model,
    resolve_x1d_provider_credentials,
)

JUDGE_RUBRIC_VERSION = "ibm_bullets_x1d_v1"

IBM_RUBRIC = """
You are evaluating exactly five IBM employment bullets (bul_ibm_001..005).
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.
- Keep score and threshold within the declared scale.

Rubric dimensions:
1. factual_support: each bullet maps to bul_ibm_* source_fact_ids in the claim ledger; metrics supported.
2. enterprise_platform_credibility: IBM reads as enterprise/platform proof, not current agentic runtime ownership.
3. ibm_scope_accuracy: no Unify, InsurTech, EY, education, or early-career contamination; IBM-only facts.
4. bullet_impact_clarity: concise, high-impact bullets; no narrative paragraphs.
5. ats_alignment_without_stuffing: relevant to target role without JD keyword dumping.
6. anti_overfit: no JD-as-proof, no briefing-as-proof, no target company as candidate experience.
7. no_unify_inflation: no Unify-era agentic runtime vocabulary (agentic AI, GraphRAG, multi-agent orchestration, etc.).

Decisive failure triggers:
- unsupported metric or cross-employer fact leakage (bul_unify_*, InsurTech, EY, etc.)
- first-person language
- wrong bullet count or invalid rewrite distribution for IBM slice
- JD phrase copied as proof (>4 consecutive words)
- Unify runtime vocabulary in bullet text
""".strip()


def _bullets_display_text(bullets: list[dict[str, Any]]) -> str:
    lines = []
    for idx, bullet in enumerate(bullets, start=1):
        bid = bullet.get("bullet_id", f"bullet_{idx}")
        intensity = bullet.get("rewrite_intensity", "")
        text = bullet.get("bullet_text", "")
        lines.append(f"[{idx}] {bid} ({intensity}): {text}")
    return "\n".join(lines)


def _build_judge_user_prompt(bullets: list[dict[str, Any]], claim_ledger: list[dict[str, Any]]) -> str:
    return (
        f"{IBM_RUBRIC}\n\n{JUDGE_COMPACT_OUTPUT}\n\n"
        f"IBM_BULLETS:\n{_bullets_display_text(bullets)}\n\n"
        f"CLAIM_LEDGER:\n{json.dumps(claim_ledger, separators=(',', ':'))}"
    )


def _mocked_output(provider_key: str, input_hash: str) -> JudgeOutput:
    meta = PROVIDERS[provider_key]
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_ibm_bullets",
        provider_name=meta["provider_name"],
        provider_key=provider_key,
        evaluator_mode="MOCKED",
        provider_status="MOCKED",
        model_name=meta.get("default_model", "unknown"),
        provider_available=False,
        provider_blocked=False,
        exact_provider_error=None,
        rubric_version=JUDGE_RUBRIC_VERSION,
        input_hash=input_hash,
        output_hash="mocked-output",
        score=0.80,
        score_scale="0_to_1",
        normalized_score=0.80,
        threshold=DEFAULT_THRESHOLD,
        normalized_threshold=0.80,
        pass_=True,
        decisive_failure=False,
        findings=["MOCKED plumbing judge. Not valid for X3_ALLOW."],
        cited_sentence_indexes=[],
        remediation_suggestions=[],
    )


def run_ibm_bullets_judges(
    *,
    bullets: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    mode: str = "blocked_if_unavailable",
    artifact_base: Path | None = None,
) -> list[JudgeOutput]:
    input_payload = {"bullets": bullets, "claim_ledger": claim_ledger, "rubric": IBM_RUBRIC}
    input_hash = hashlib.sha256(json.dumps(input_payload, sort_keys=True).encode()).hexdigest()[:16]
    prompt = _build_judge_user_prompt(bullets, claim_ledger)

    outputs: list[JudgeOutput] = []
    for key in judge_keys:
        if key not in PROVIDERS:
            outputs.append(
                _make_blocked_output(
                    key,
                    input_hash,
                    "BLOCKED_PROVIDER_UNAVAILABLE",
                    "BLOCKED_PROVIDER_UNAVAILABLE",
                    f"Unknown judge provider key: {key}",
                )
            )
            continue

        if mode == "mocked":
            outputs.append(_mocked_output(key, input_hash))
            continue

        meta = PROVIDERS[key]
        api_key, env_checked = resolve_x1d_provider_credentials(key, os.environ)
        if not api_key:
            detail = (
                f"No non-empty API credential in {env_checked}; "
                f"(Gemini: GOOGLE_API_KEY, then deprecated GEMINI_API_KEY alias)."
                if key == "gemini_pro"
                else f"{meta['env']} environment variable not set"
            )
            outputs.append(
                _make_blocked_output(
                    key,
                    input_hash,
                    "BLOCKED_PROVIDER_UNAVAILABLE",
                    "BLOCKED_PROVIDER_UNAVAILABLE",
                    detail,
                )
            )
            continue

        if key == "gemini_pro":
            model, model_source = _resolve_gemini_model(meta)
        elif key == "anthropic_claude":
            model, model_source = _resolve_anthropic_model(meta)
        else:
            model_env = meta.get("model_env", meta["env"].replace("_API_KEY", "_MODEL"))
            model = os.environ.get(model_env, "").strip() or meta.get("default_model", "unknown")
            model_source = model_env if model else "default"

        try:
            if key == "openai_chatgpt":
                output = _call_openai(
                    api_key, prompt, model, input_hash, key, artifact_base=artifact_base
                )
            elif key == "anthropic_claude":
                output = _call_anthropic(
                    api_key,
                    prompt,
                    model,
                    input_hash,
                    key,
                    model_source=model_source,
                    artifact_base=artifact_base,
                )
            else:
                output = _call_gemini(
                    api_key,
                    prompt,
                    model,
                    input_hash,
                    key,
                    model_source=model_source,
                    artifact_base=artifact_base,
                )
            output.judge_id = f"x1d_{key}_ibm_bullets"
            output.rubric_version = JUDGE_RUBRIC_VERSION
            outputs.append(output)
        except Exception as exc:  # noqa: BLE001
            blocked = _make_blocked_output(
                key,
                input_hash,
                "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE",
                f"{meta['provider_name']} judge call failed: {type(exc).__name__}: {exc}",
                model_name=model,
            )
            blocked.judge_id = f"x1d_{key}_ibm_bullets"
            outputs.append(blocked)

    return outputs


__all__ = ["run_ibm_bullets_judges", "JUDGE_RUBRIC_VERSION"]
