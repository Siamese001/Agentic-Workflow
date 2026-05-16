"""X1D judges for ibm_narrative — reuses executive_summary_x1d provider adapters."""
from __future__ import annotations

import hashlib
import json
import os
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

JUDGE_RUBRIC_VERSION = "ibm_narrative_x1d_v1"

NARRATIVE_RUBRIC = """
You are evaluating one IBM employment narrative sentence (complement to five IBM bullets).
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.

Rubric dimensions:
1. factual_support: claims align with claim_ledger and bul_ibm_* source facts only.
2. enterprise_platform_signal: IBM reads as supporting enterprise/platform credibility, not current agentic runtime ownership.
3. complementarity_vs_bullets: adds framing or synthesis; does not mechanically recap all five bullets.
4. resume_voice: third person or implied subject; credible executive tone.
5. ats_alignment_without_stuffing: relevant without JD dumping.
6. anti_overfit: no JD-as-proof, no briefing-as-proof, no cross-employer facts (Unify, InsurTech, EY).
7. no_unify_inflation: no Unify-era agentic runtime vocabulary in the sentence.

Decisive failure triggers:
- first person or wrong-company proof framing
- unsupported metrics or bul_unify_* / non-IBM fact leakage
- multiple sentences or obvious five-bullet recap
""".strip()


def _build_prompt(
    narrative_sentence: str,
    claim_ledger: list[dict[str, Any]],
    companion_bullets_context: str,
) -> str:
    companion_block = (
        f"\nCOMPANION_IBM_BULLETS (read-only context):\n{companion_bullets_context}\n"
        if companion_bullets_context.strip()
        else ""
    )
    return (
        f"{NARRATIVE_RUBRIC}\n\n{JUDGE_COMPACT_OUTPUT}\n\n"
        f"NARRATIVE_SENTENCE:\n{narrative_sentence}\n"
        f"{companion_block}\n"
        f"CLAIM_LEDGER:\n{json.dumps(claim_ledger, separators=(',', ':'))}"
    )


def _mocked(provider_key: str, input_hash: str) -> JudgeOutput:
    meta = PROVIDERS[provider_key]
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_ibm_narrative",
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


def run_ibm_narrative_judges(
    *,
    narrative_sentence: str,
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    companion_bullets_context: str = "",
    mode: str = "blocked_if_unavailable",
) -> list[JudgeOutput]:
    input_payload = {
        "narrative_sentence": narrative_sentence,
        "claim_ledger": claim_ledger,
        "companion_bullets_context": companion_bullets_context,
        "rubric": NARRATIVE_RUBRIC,
    }
    input_hash = hashlib.sha256(json.dumps(input_payload, sort_keys=True).encode()).hexdigest()[:16]
    prompt = _build_prompt(narrative_sentence, claim_ledger, companion_bullets_context)

    outputs: list[JudgeOutput] = []
    for key in judge_keys:
        if key not in PROVIDERS:
            out = _make_blocked_output(
                key,
                input_hash,
                "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE",
                f"Unknown judge provider key: {key}",
            )
            out.judge_id = f"x1d_{key}_ibm_narrative"
            outputs.append(out)
            continue

        if mode == "mocked":
            outputs.append(_mocked(key, input_hash))
            continue

        meta = PROVIDERS[key]
        api_key, env_checked = resolve_x1d_provider_credentials(key, os.environ)
        if not api_key:
            detail = (
                f"No non-empty API credential in {env_checked}; "
                f"(Gemini: GEMINI_API_KEY then GOOGLE_API_KEY)."
                if key == "gemini_pro"
                else f"{meta['env']} environment variable not set"
            )
            out = _make_blocked_output(
                key,
                input_hash,
                "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE",
                detail,
            )
            out.judge_id = f"x1d_{key}_ibm_narrative"
            outputs.append(out)
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
                output = _call_openai(api_key, prompt, model, input_hash, key)
            elif key == "anthropic_claude":
                output = _call_anthropic(api_key, prompt, model, input_hash, key, model_source=model_source)
            else:
                output = _call_gemini(api_key, prompt, model, input_hash, key, model_source=model_source)
            output.judge_id = f"x1d_{key}_ibm_narrative"
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
            blocked.judge_id = f"x1d_{key}_ibm_narrative"
            outputs.append(blocked)

    return outputs


__all__ = ["run_ibm_narrative_judges", "JUDGE_RUBRIC_VERSION"]
