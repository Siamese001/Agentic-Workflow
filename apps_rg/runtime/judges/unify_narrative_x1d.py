"""X1D judges for unify_narrative — policy-backed GRADE_ONLY JudgePacket."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.policy_backed_section_judges import run_policy_section_judges
from apps_rg.runtime.sections.section_product_shape_ssot import NARRATIVE_MAX_CHARS, NARRATIVE_MAX_WORDS

JUDGE_RUBRIC_VERSION = "unify_narrative_x1d_v3"
JUDGE_RUBRIC_REF = "apps_rg/runtime/judges/unify_narrative_x1d.py#UNIFY_NARRATIVE_GRADE_ONLY_RUBRIC"

NARRATIVE_RUBRIC = f"""
You are evaluating one Unify Consulting role narrative sentence (executive thesis above six bullets).
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.

Rubric dimensions (must score each):
1. north_star_alignment: role-level capstone emphasizing platform roadmap, core systems architecture,
   commercialization, reusable IP / platform economics, and enterprise deployment within consulting-firm context.
2. fact_ledger_grounding: every material claim in the narrative maps to claim_ledger and bul_unify_* and/or
   unify_narrative_base_* resume facts (no JD/briefing/target-company-as-experience).
3. jd_briefing_targeting: JD and briefing themes shape emphasis without becoming proof (belongs in jd_alignment object,
   not the sentence as invented experience).
4. complementarity_vs_bullets: states the executive thesis the bullets prove without recap, checklist, or six-bullet walk.
5. executive_signal: SVP Engineering platform leadership — governed runtime, commercialization, regulated enterprise scale.
6. no_metric_rehash: avoids repeating bullet metrics unless narrowly justified; prefers conceptual commercialization language.
7. no_cross_employer_leakage: no IBM, InsurTech, EY, education, or early-career contamination.
8. resume_voice: third person or implied subject; clean board-readable executive tone; no hype or comma-packed mechanism list.
9. role_fit_targeting: JD/briefing influence emphasis only — never proof of experience.
10. why_role_mattered: narrative answers why the Unify role mattered (mandate, commercialization, IP) — companion bullets answer what was delivered.
11. executive_brevity: exactly one sentence; product shape max {NARRATIVE_MAX_WORDS} words and {NARRATIVE_MAX_CHARS} characters; JD/briefing targeting only (never proof).

Decisive failure triggers:
- merely summarizes the six bullets or mirrors bullet labels/metrics as the thesis
- spins a different role story not entailed by the finalized bullets or claim_ledger
- uses JD, briefing, or target company as proof of candidate experience
- omits commercialization / reusable platform / IP angle when base anchor facts support that arc
- lacks role-level platform mandate (reads like a delivery task list)
- multiple sentences or bullet-list formatting
""".strip()


def run_unify_narrative_judges(
    *,
    narrative_sentence: str,
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    companion_bullets_context: str = "",
    mode: str = "blocked_if_unavailable",
    artifact_base: Path | None = None,
    targeting_context: dict[str, Any] | None = None,
    deterministic_gate_summary: dict[str, Any] | None = None,
    allowed_fact_packet: dict[str, Any] | None = None,
) -> list[JudgeOutput]:
    candidate = {
        "narrative_sentence": narrative_sentence,
        "resume_display_text": narrative_sentence,
        "companion_bullets_context": companion_bullets_context,
    }
    packet_path = (artifact_base / "unify_narrative_judge_packet.json") if artifact_base else None
    outputs = run_policy_section_judges(
        "unify_narrative",
        candidate_output=candidate,
        section_rubric=NARRATIVE_RUBRIC,
        rubric_ref=JUDGE_RUBRIC_REF,
        claim_ledger=claim_ledger,
        judge_keys=judge_keys,
        allowed_fact_packet=allowed_fact_packet,
        targeting_context=targeting_context,
        deterministic_gate_summary=deterministic_gate_summary,
        resume_display_text=narrative_sentence,
        mode=mode,
        artifact_base=artifact_base,
        judge_packet_path=packet_path,
    )
    for o in outputs:
        o.judge_id = f"x1d_{o.provider_key}_unify_narrative"
        o.rubric_version = JUDGE_RUBRIC_VERSION
    return outputs


__all__ = ["run_unify_narrative_judges", "JUDGE_RUBRIC_VERSION", "NARRATIVE_RUBRIC"]
