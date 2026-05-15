"""X1D judges for headline — reuses executive_summary_x1d provider adapters."""
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
)

JUDGE_RUBRIC_VERSION = "headline_x1d_v1"

HEADLINE_RUBRIC = """
You are evaluating a single resume headline line formatted as: SegmentOne | SegmentTwo | SegmentThree.
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.

Rubric dimensions:
1. factual_support: headline aligns with claim_ledger and bul_* resume facts only.
2. format_compliance: exactly three pipe-separated segments; 8-11 total words; no metrics; no employer names.
3. executive_signal: reads as SVP-level scope, not IC task list.
4. ats_alignment: concise keyword clusters without stuffing or JD-as-proof.
5. anti_overfit: no JD-only or briefing-only claims; no target-company framing as past employment.
6. complementarity: fits with accepted executive summary and generated sections without repeating them verbatim.

Decisive failure triggers:
- unsupported proof, employer names, metrics, or first person
- format break (not exactly three segments or word count out of range)
""".strip()


def _build_prompt(
    headline_line: str,
    claim_ledger: list[dict[str, Any]],
    companion_context: str,
) -> str:
    block = (
        f"\nREAD_ONLY_GENERATED_SECTIONS:\n{companion_context}\n"
        if companion_context.strip()
        else "\n(No companion artifacts on disk.)\n"
    )
    return (
        f"{HEADLINE_RUBRIC}\n\n{JUDGE_COMPACT_OUTPUT}\n\n"
        f"HEADLINE_LINE:\n{headline_line}\n"
        f"{block}\n"
        f"CLAIM_LEDGER:\n{json.dumps(claim_ledger, separators=(',', ':'))}"
    )


def _mocked(provider_key: str, input_hash: str) -> JudgeOutput:
    meta = PROVIDERS[provider_key]
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_headline",
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


def run_headline_judges(
    *,
    headline_line: str,
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    companion_context: str = "",
    mode: str = "blocked_if_unavailable",
) -> list[JudgeOutput]:
    input_payload = {
        "headline_line": headline_line,
        "claim_ledger": claim_ledger,
        "companion_context": companion_context,
        "rubric": HEADLINE_RUBRIC,
    }
    input_hash = hashlib.sha256(json.dumps(input_payload, sort_keys=True).encode()).hexdigest()[:16]
    prompt = _build_prompt(headline_line, claim_ledger, companion_context)

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
            out.judge_id = f"x1d_{key}_headline"
            outputs.append(out)
            continue

        if mode == "mocked":
            outputs.append(_mocked(key, input_hash))
            continue

        meta = PROVIDERS[key]
        api_key = os.environ.get(str(meta["env"]), "")
        if not api_key:
            out = _make_blocked_output(
                key,
                input_hash,
                "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE",
                f"{meta['env']} environment variable not set",
            )
            out.judge_id = f"x1d_{key}_headline"
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
            output.judge_id = f"x1d_{key}_headline"
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
            blocked.judge_id = f"x1d_{key}_headline"
            outputs.append(blocked)

    return outputs


__all__ = ["run_headline_judges", "JUDGE_RUBRIC_VERSION"]
