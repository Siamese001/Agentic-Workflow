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
    resolve_x1d_provider_credentials,
)

JUDGE_RUBRIC_VERSION = "headline_x1d_v2"

HEADLINE_RUBRIC = """
You are evaluating a single resume headline formatted exactly as: SVP Engineering | X | Y | Z
(space-pipe-space separators; exactly four segments; first segment exactly "SVP Engineering"; 10-13 total words).
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.

Rubric dimensions:
1. factual_support: every substantive phrase in X/Y/Z is supported by claim_ledger bul_* facts only (JD/briefing are never proof).
2. fixed_prefix_compliance: headline_line starts with "SVP Engineering | " and uses exactly three " | " separators.
3. base_identity_fidelity: authentic to the base resume headline anchor; not rewritten to chase the JD.
4. anti_keyword_stuffing: no ATS keyword bags, list-like segments, or multi-domain laundry lists.
5. JD targeting discipline: JD relevance without copying JD phrasing or treating JD as authority.
6. executive_authenticity: reads as a senior platform/engineering leader, not generic leadership filler.
7. no_title_inflation: first segment is not replaced or subverted; no "SVP at TargetCo" framing.
8. natural human resume sound: concise, human, resume-native phrasing.

Decisive failure triggers (if any, set decisive_failure true and pass false):
- missing fixed prefix "SVP Engineering" as segment 1
- not exactly four non-empty segments or not exactly three " | " separators
- word count outside 10-13 (inclusive)
- unsupported proof relative to claim_ledger / resume facts
- employer names, target company names, or candidate personal name tokens
- metrics or numeric proof in headline_line
- first person
- copied JD phrases or briefing-only / JD-only claims without fact support
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
        api_key, env_checked = resolve_x1d_provider_credentials(key, os.environ)
        if not api_key:
            detail = (
                f"No non-empty API credential in {env_checked}; "
                f"(Gemini: GOOGLE_API_KEY, then deprecated GEMINI_API_KEY alias)."
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
