"""X1D judges for competencies — reuses executive_summary_x1d provider adapters."""
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

JUDGE_RUBRIC_VERSION = "competencies_x1d_v1"

COMPETENCIES_RUBRIC = """
You are evaluating six to eight executive resume competency categories (short labels plus compact capability phrases).
This is OPTIONAL ADVISORY taxonomy grading — deterministic X2 gates are authoritative for proof eligibility.
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.

Rubric dimensions:
1. factual_support: terms align with claim_ledger and allowed bul_* resume facts only.
2. ats_alignment_without_stuffing: relevant clusters without keyword stuffing or JD-as-proof.
3. seniority_executive_relevance: reads as executive-level capability groupings.
4. complementarity: augments executive summary, Unify, and IBM generated sections; not a mechanical restatement of bullets.
5. no_bullet_restatement: avoids copying long bullet fragments or outcome laundry lists.
6. anti_overfit: no JD-only or briefing-only skills framed as proof.
7. category_clarity: labels are crisp; terms are compact keyword phrases (not sentence-style competency claims).

Advisory notes:
- Sentence-style competency claims are out of scope for this section format; flag them as quality_flags only.
- Judge pass/fail does not gate product proof eligibility for competencies.

Decisive failure triggers (advisory only):
- JD or briefing used as primary evidence for unsupported clusters
- obvious bullet paste or first-person resume voice leakage
- format breaks (full sentences inside terms, bullet markers)
""".strip()


def _build_prompt(
    competencies_json: str,
    claim_ledger: list[dict[str, Any]],
    companion_context: str,
) -> str:
    block = (
        f"\nREAD_ONLY_GENERATED_SECTIONS:\n{companion_context}\n"
        if companion_context.strip()
        else "\n(No companion generated-section artifacts on disk.)\n"
    )
    return (
        f"{COMPETENCIES_RUBRIC}\n\n{JUDGE_COMPACT_OUTPUT}\n\n"
        f"COMPETENCIES_JSON:\n{competencies_json}\n"
        f"{block}\n"
        f"CLAIM_LEDGER:\n{json.dumps(claim_ledger, separators=(',', ':'))}"
    )


def _mocked(provider_key: str, input_hash: str) -> JudgeOutput:
    meta = PROVIDERS[provider_key]
    return JudgeOutput(
        judge_id=f"x1d_{provider_key}_competencies",
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


def run_competencies_judges(
    *,
    competencies: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    companion_context: str = "",
    mode: str = "blocked_if_unavailable",
    artifact_base: Path | None = None,
) -> list[JudgeOutput]:
    competencies_json = json.dumps(competencies, separators=(",", ":"), ensure_ascii=False)
    input_payload = {
        "competencies": competencies,
        "claim_ledger": claim_ledger,
        "companion_context": companion_context,
        "rubric": COMPETENCIES_RUBRIC,
    }
    input_hash = hashlib.sha256(json.dumps(input_payload, sort_keys=True).encode()).hexdigest()[:16]
    prompt = _build_prompt(competencies_json, claim_ledger, companion_context)

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
            out.judge_id = f"x1d_{key}_competencies"
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
            out.judge_id = f"x1d_{key}_competencies"
            outputs.append(out)
            continue

        if key == "gemini_pro":
            model, model_source = _resolve_gemini_model(meta, section_id="competencies")
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
            output.judge_id = f"x1d_{key}_competencies"
            output.rubric_version = JUDGE_RUBRIC_VERSION
            output.advisory_only = True
            output.proof_eligible_judge = False
            outputs.append(output)
        except Exception as exc:  # noqa: BLE001  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            blocked = _make_blocked_output(
                key,
                input_hash,
                "BLOCKED_PROVIDER_UNAVAILABLE",
                "BLOCKED_PROVIDER_UNAVAILABLE",
                f"{meta['provider_name']} judge call failed: {type(exc).__name__}: {exc}",
                model_name=model,
            )
            blocked.judge_id = f"x1d_{key}_competencies"
            outputs.append(blocked)

    return outputs


__all__ = ["run_competencies_judges", "JUDGE_RUBRIC_VERSION"]
