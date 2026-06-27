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
    _invoke_judge_with_bounded_retries,
    _make_blocked_output,
    _resolve_anthropic_model,
    _resolve_gemini_model,
    resolve_x1d_provider_credentials,
)
from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model

JUDGE_RUBRIC_VERSION = "competencies_x1d_v3"

COMPETENCIES_RUBRIC_DIMENSION_IDS: tuple[str, ...] = (
    "factual_support",
    "ats_alignment_without_stuffing",
    "seniority_executive_relevance",
    "complementarity",
    "no_bullet_restatement",
    "anti_overfit",
    "category_clarity",
    "svp_agentic_specificity",
)

COMPETENCIES_JUDGE_OUTPUT_CONTRACT = (
    "Required competencies dimension_verdicts keys: "
    + ", ".join(COMPETENCIES_RUBRIC_DIMENSION_IDS)
    + ". Do not substitute executive_summary dimension ids.\n"
    '"dimension_verdicts": {'
    + ", ".join(
        f'"{dim}": {{"pass": true, "severity": "none", "codes": []}}'
        for dim in COMPETENCIES_RUBRIC_DIMENSION_IDS
    )
    + "}"
)

COMPETENCIES_RUBRIC = """
You are evaluating exactly 8 executive resume competency categories (short labels plus compact capability phrases).
This is REQUIRED proof taxonomy grading. Deterministic X2 gates remain authoritative for source lineage,
and this X1D judge must pass before competencies can be product proof eligible.
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.

Rubric dimensions:
1. factual_support: terms align with claim_ledger and allowed bul_* resume facts only; graph-skill support may inform phrasing, but JD/briefing never become proof.
2. ats_alignment_without_stuffing: relevant clusters without keyword stuffing or JD-as-proof; favor semantic coverage and distinct ATS query clusters over repeating the same three metrics or one employer lane.
3. seniority_executive_relevance: reads as executive-level capability groupings with breadth across the graph, not a single repeated theme or junior operator checklist.
4. complementarity: augments executive summary, Unify, and IBM generated sections; not a mechanical restatement of bullets, the same proof surface, or career-phase narration.
5. no_bullet_restatement: avoids copying long bullet fragments, outcome laundry lists, repeated metric language, or employer-specific verbatim lines.
6. anti_overfit: no JD-only or briefing-only skills framed as proof; company-specific targeting may influence label choice, not evidence; do not collapse multiple categories onto one metric family; no AI-authenticity dead giveaways such as template phrasing or buzzword soup.
7. category_clarity: labels are crisp; terms are compact keyword phrases (not sentence-style competency claims) and each category should be semantically distinct, graph-backed, and tied to a different skill family.
8. svp_agentic_specificity: no generic or mundane competency terms; phrases should sound like believable work by an SVP-level engineering leader and deep agentic AI practitioner, with concrete mechanisms plus operating/commercial context. Penalize table-stakes phrases such as "hyperscaler co-sell", "platform commercialization", "stakeholder alignment", "cloud architecture", or "runtime policy controls" when they appear without richer mechanism/context.

Adversarial review lens:
- Head of Talent Acquisition pass: would the taxonomy feel recruiter-clean and senior enough for the target company?
- AI authenticity pass: no generic generated labels, no buzzword soup, no phrase recycling across categories.

Anti-AI filters:
- no em dashes in labels or findings
- no template phrasing like "strategic leadership" repeated across categories
- no repeated metric families copied into multiple categories
- no first-person voice, self-reference, or resume prose leakage
- no unsupported tools, benchmarks, certifications, or employer claims
- no sentence-style category labels or bullet-shaped terms
- no "transformational", "innovative", or "cutting-edge" filler without concrete grounding

Required judge notes:
- The deterministic product shape expects exactly 8 categories; flag missing, extra, or duplicate category groups as quality_flags.
- Sentence-style competency claims are out of scope for this section format; flag them as quality_flags only.
- Judge pass/fail gates product proof eligibility for competencies.
- companion_context_used_as_proof must remain false; JD/briefing/targeting_only — never proof (aligns with PA contract).
- Terms require source_fact_ids / claim_ledger binding — no JD-only skills as proof.
- When the categories collapse onto the same few metrics, fact surfaces, or employer lane, lower the score even if the shape is technically valid.
- If the labels feel machine-generated or too generic to survive a TA skim, treat that as a quality flag.
- If the terms could belong unchanged to any cloud/AI executive rather than this candidate's graph-backed SVP agentic work, fail or lower svp_agentic_specificity.

Decisive failure triggers (advisory only):
- JD or briefing used as primary evidence for unsupported clusters
- obvious bullet paste or first-person resume voice leakage
- format breaks (full sentences inside terms, bullet markers)
- repeated metric/language loops across multiple categories
- generic category labels with no graph-backed differentiation
- mundane visible competency phrases that lack agentic mechanism, executive operating context, or believable SVP scope
- company-specific targeting used as proof rather than label choice
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
        f"{COMPETENCIES_JUDGE_OUTPUT_CONTRACT}\n\n"
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


def _empty_competencies_dimension_verdict(*, pass_: bool) -> dict[str, Any]:
    return {
        "pass": pass_,
        "severity": "none" if pass_ else "major",
        "codes": [],
    }


def _normalize_competencies_dimension_verdicts(output: JudgeOutput) -> JudgeOutput:
    raw = output.dimension_verdicts if isinstance(output.dimension_verdicts, dict) else {}
    normalized: dict[str, dict[str, Any]] = {}
    inferred = bool(output.dimension_verdicts_inferred)

    for dim in COMPETENCIES_RUBRIC_DIMENSION_IDS:
        verdict = raw.get(dim)
        if not isinstance(verdict, dict):
            normalized[dim] = _empty_competencies_dimension_verdict(pass_=bool(output.pass_))
            inferred = True
            continue
        codes = verdict.get("codes")
        normalized[dim] = {
            "pass": bool(verdict.get("pass", output.pass_)),
            "severity": str(verdict.get("severity") or ("none" if verdict.get("pass", output.pass_) else "major")),
            "codes": codes if isinstance(codes, list) else [],
        }

    if set(raw) != set(COMPETENCIES_RUBRIC_DIMENSION_IDS):
        inferred = True
        if "competencies_dimension_verdicts_normalized" not in output.quality_flags:
            output.quality_flags.append("competencies_dimension_verdicts_normalized")

    output.dimension_verdicts = normalized
    output.dimension_verdicts_inferred = inferred
    return output


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
            outputs.append(_normalize_competencies_dimension_verdicts(_mocked(key, input_hash)))
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

        resolution = resolve_section_proof_judge_model("competencies", key)
        if resolution.blocked:
            out = _make_blocked_output(
                key,
                input_hash,
                "BLOCKED_MODEL_CONFIG",
                "BLOCKED_MODEL_CONFIG",
                resolution.block_reason or "proof judge model unavailable",
                model_name=resolution.model_requested or "unconfigured",
            )
            out.judge_id = f"x1d_{key}_competencies"
            out.section_id = "competencies"
            out.model_tier = resolution.model_tier
            outputs.append(out)
            continue

        if key == "gemini_pro":
            model, model_source = _resolve_gemini_model(meta, section_id="competencies")
        elif key == "anthropic_claude":
            model, model_source = _resolve_anthropic_model(meta, section_id="competencies")
        else:
            model = resolution.model_actual
            model_source = resolution.model_source
        model_requested = resolution.model_requested or model
        reasoning_effort = resolution.reasoning_effort

        try:
            def _dispatch(attempt_no: int) -> JudgeOutput:
                if key == "openai_chatgpt":
                    return _call_openai(
                        api_key,
                        prompt,
                        model,
                        input_hash,
                        key,
                        artifact_base=artifact_base,
                        reasoning_effort=reasoning_effort,
                        model_requested=model_requested,
                        model_env_source=model_source,
                        attempt=attempt_no,
                        section_id="competencies",
                    )
                if key == "anthropic_claude":
                    return _call_anthropic(
                        api_key,
                        prompt,
                        model,
                        input_hash,
                        key,
                        model_source=model_source,
                        artifact_base=artifact_base,
                        model_requested=model_requested,
                        attempt=attempt_no,
                        section_id="competencies",
                    )
                return _call_gemini(
                    api_key,
                    prompt,
                    model,
                    input_hash,
                    key,
                    model_source=model_source,
                    artifact_base=artifact_base,
                    model_requested=model_requested,
                    attempt=attempt_no,
                    section_id="competencies",
                )

            output = _invoke_judge_with_bounded_retries(
                _dispatch,
                provider_key=key,
                section_id="competencies",
            )
            output.judge_id = f"x1d_{key}_competencies"
            output.rubric_version = JUDGE_RUBRIC_VERSION
            output.section_id = "competencies"
            output.model_tier = resolution.model_tier
            output.advisory_only = False
            output.proof_eligible_judge = bool(
                resolution.proof_eligible_judge
                and output.evaluator_mode == "MODEL_BACKED"
                and not output.provider_blocked
            )
            outputs.append(_normalize_competencies_dimension_verdicts(output))
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
