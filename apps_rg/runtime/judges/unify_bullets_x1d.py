"""X1D LLM judges for unify_bullets — policy-backed GRADE_ONLY JudgePacket."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.policy_backed_section_judges import run_policy_section_judges

JUDGE_RUBRIC_VERSION = "unify_bullets_x1d_v2"
JUDGE_RUBRIC_REF = "apps_rg/runtime/judges/unify_bullets_x1d.py#UNIFY_BULLETS_GRADE_ONLY_RUBRIC"

UNIFY_RUBRIC = """
You are evaluating exactly six Unify Consulting employment bullets (bul_unify_001..006).
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.
- Keep score and threshold within the declared scale.

Rubric dimensions:
1. factual_support: each bullet maps to bul_unify_* source_fact_ids in the claim ledger; metrics supported.
2. executive_platform_signal: platform architecture, governance, operating model, commercial impact, and engineering scale where evidenced.
3. current_role_attention: Unify reads like the candidate's strongest current-position proof point for SVP Engineering screens.
4. bullet_impact_clarity: concise, high-impact bullets; no narrative paragraphs.
5. ats_alignment_without_stuffing: relevant to target role without JD keyword dumping or briefing-as-proof.
6. anti_overfit: no JD-as-proof, no briefing-as-proof, no target company as candidate experience.
7. rewrite_quality: respects rewrite distribution (2 HEAVY, 3 MODERATE, 1 LIGHT_PROTECTED default); bul_unify_006 protected commercial metrics preserved.

Decisive failure triggers:
- unsupported metric or cross-employer fact leakage (IBM/InsurTech/EY)
- first-person language
- wrong bullet count or invalid rewrite distribution
- protected bul_unify_006 metrics missing or split incorrectly
- JD phrase copied as proof (>4 consecutive words)
- generic executive filler that loses Unify-specific mechanisms or protected metrics
""".strip()


def _bullets_display_text(bullets: list[dict[str, Any]]) -> str:
    lines = []
    for idx, bullet in enumerate(bullets, start=1):
        bid = bullet.get("bullet_id", f"bullet_{idx}")
        intensity = bullet.get("rewrite_intensity", "")
        text = bullet.get("bullet_text", "")
        lines.append(f"[{idx}] {bid} ({intensity}): {text}")
    return "\n".join(lines)


def run_unify_bullets_judges(
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
    packet_path = (artifact_base / "unify_bullets_judge_packet.json") if artifact_base else None
    outputs = run_policy_section_judges(
        "unify_bullets",
        candidate_output=candidate,
        section_rubric=UNIFY_RUBRIC,
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
        o.judge_id = f"x1d_{o.provider_key}_unify_bullets"
        o.rubric_version = JUDGE_RUBRIC_VERSION
    return outputs


__all__ = ["run_unify_bullets_judges", "JUDGE_RUBRIC_VERSION", "UNIFY_RUBRIC"]
