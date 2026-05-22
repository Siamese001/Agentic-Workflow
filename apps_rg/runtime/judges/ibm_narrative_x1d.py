"""X1D judges for ibm_narrative — policy-backed GRADE_ONLY JudgePacket."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.policy_backed_section_judges import run_policy_section_judges

JUDGE_RUBRIC_VERSION = "ibm_narrative_x1d_v2"
JUDGE_RUBRIC_REF = "apps_rg/runtime/judges/ibm_narrative_x1d.py#IBM_NARRATIVE_GRADE_ONLY_RUBRIC"

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
8. role_fit_targeting: JD/briefing shape emphasis only — never proof.
9. why_role_mattered: sentence explains IBM foundation mandate (cloud, data, lineage, observability, regulated context) — companion bullets carry KPI proof.
10. no_meta_disclaimer: display text must not contain "without claiming/asserting" or similar editorial boundary language.

Decisive failure triggers:
- first person or wrong-company proof framing
- unsupported metrics or bul_unify_* / non-IBM fact leakage
- multiple sentences or obvious five-bullet recap
- meta-disclaimer phrasing in narrative_sentence ("without claiming", "without asserting", etc.)
- career-bridge phrasing ("supported later", "subsequent roles") without explicit allowed career-bridge fact
""".strip()


def run_ibm_narrative_judges(
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
    packet_path = (artifact_base / "ibm_narrative_judge_packet.json") if artifact_base else None
    outputs = run_policy_section_judges(
        "ibm_narrative",
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
        o.judge_id = f"x1d_{o.provider_key}_ibm_narrative"
        o.rubric_version = JUDGE_RUBRIC_VERSION
    return outputs


__all__ = ["run_ibm_narrative_judges", "JUDGE_RUBRIC_VERSION", "NARRATIVE_RUBRIC"]
