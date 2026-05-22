"""X1D LLM judges for ibm_bullets — policy-backed GRADE_ONLY JudgePacket."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.policy_backed_section_judges import run_policy_section_judges

JUDGE_RUBRIC_VERSION = "ibm_bullets_x1d_v2"
JUDGE_RUBRIC_REF = "apps_rg/runtime/judges/ibm_bullets_x1d.py#IBM_BULLETS_GRADE_ONLY_RUBRIC"

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
8. role_fit_targeting: JD/briefing targeting shapes emphasis without JD-as-proof.
9. bullet_semantic_distribution: five IBM bullets cover distinct enterprise outcomes, not five restatements of the same theme.
10. narrative_complementarity: bullets are outcome lines that complement (not preempt) the IBM narrative capstone.

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


def run_ibm_bullets_judges(
    *,
    bullets: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    mode: str = "blocked_if_unavailable",
    artifact_base: Path | None = None,
    targeting_context: dict[str, Any] | None = None,
    deterministic_gate_summary: dict[str, Any] | None = None,
    allowed_fact_packet: dict[str, Any] | None = None,
) -> list[JudgeOutput]:
    display = _bullets_display_text(bullets)
    candidate = {"bullets": bullets, "resume_display_text": display}
    packet_path = (artifact_base / "ibm_bullets_judge_packet.json") if artifact_base else None
    outputs = run_policy_section_judges(
        "ibm_bullets",
        candidate_output=candidate,
        section_rubric=IBM_RUBRIC,
        rubric_ref=JUDGE_RUBRIC_REF,
        claim_ledger=claim_ledger,
        judge_keys=judge_keys,
        allowed_fact_packet=allowed_fact_packet,
        targeting_context=targeting_context,
        deterministic_gate_summary=deterministic_gate_summary,
        resume_display_text=display,
        mode=mode,
        artifact_base=artifact_base,
        judge_packet_path=packet_path,
    )
    for o in outputs:
        o.judge_id = f"x1d_{o.provider_key}_ibm_bullets"
        o.rubric_version = JUDGE_RUBRIC_VERSION
    return outputs


__all__ = ["run_ibm_bullets_judges", "JUDGE_RUBRIC_VERSION", "IBM_RUBRIC"]
