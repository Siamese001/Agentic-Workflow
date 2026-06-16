"""Shared X1D rubric for proof-bound InsurTech/EY role episode lanes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.policy_backed_section_judges import run_policy_section_judges
from apps_rg.runtime.sections.section_product_shape_ssot import NARRATIVE_MAX_CHARS, NARRATIVE_MAX_WORDS

JUDGE_RUBRIC_VERSION = "role_episode_x1d_v2"
DEFAULT_THRESHOLD = 0.80
JUDGE_RUBRIC_REF = "apps_rg/runtime/judges/role_episode_x1d.py#ROLE_EPISODE_RUBRIC"

ROLE_EPISODE_RUBRIC = f"""
You are evaluating a proof-bound InsurTech or EY role episode lane: either exactly 3 bullets
or exactly one narrative sentence. Return JSON only with: score_scale, score, threshold,
pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.
- threshold is 0.80 unless policy overrides it.

Rubric dimensions:
1. factual_support: every material claim maps to claim_ledger and source_fact_ids from the allowed proof pool.
2. claim_ledger_grounding: claim_ledger rows have non-empty claim_text and cite only role_episode_bundle_id graph evidence.
3. jd_briefing_targeting_discipline: JD and briefing are targeting only; never JD-as-proof or briefing-as-proof.
4. role_fit_targeting: targeting may shape emphasis without becoming proof of experience.

Role-lane product shape:
- Bullet lanes: exactly 3 bullets, one high-impact thought per bullet, no embedded newline.
- Narrative lanes: exactly one sentence, no more than {NARRATIVE_MAX_WORDS} words and {NARRATIVE_MAX_CHARS} characters.
- Source namespaces: InsurTech uses bul_insurtech_* source_fact_ids with reb_insurtech_* graph bundle ids;
  EY uses bul_ey_* source_fact_ids with reb_ey_* graph bundle ids.
- No first-person voice and no em dash in display text.

Decisive failure triggers:
- unsupported claim, missing source_fact_ids, or claim_ledger omission
- JD, briefing, or target company used as proof of experience
- wrong source namespace, cross-employer leakage, mixed InsurTech/EY graph evidence, or missing bul_insurtech_*/bul_ey_* source_fact_ids
- keyword stuffing, copied JD phrases, or ATS laundry-list phrasing
- wrong output shape: not 3 bullets for bullet lanes or not exactly one sentence for narrative lanes
""".strip()


def run_role_episode_judges(
    *,
    section_id: str,
    candidate_output: dict[str, Any],
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    mode: str = "blocked_if_unavailable",
    artifact_base: Path | None = None,
    targeting_context: dict[str, Any] | None = None,
    deterministic_gate_summary: dict[str, Any] | None = None,
    allowed_fact_packet: dict[str, Any] | None = None,
) -> list[JudgeOutput]:
    display = str(
        candidate_output.get("resume_display_text")
        or candidate_output.get("narrative_sentence")
        or "\n".join(
            str(row.get("bullet_text") or "")
            for row in (candidate_output.get("bullets") or [])
            if isinstance(row, dict)
        )
    )
    packet_path = (artifact_base / f"{section_id}_judge_packet.json") if artifact_base else None
    outputs = run_policy_section_judges(
        section_id,
        candidate_output=candidate_output,
        section_rubric=ROLE_EPISODE_RUBRIC,
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
    for output in outputs:
        output.judge_id = f"x1d_{output.provider_key}_{section_id}"
        output.rubric_version = JUDGE_RUBRIC_VERSION
    return outputs


__all__ = [
    "DEFAULT_THRESHOLD",
    "JUDGE_RUBRIC_REF",
    "JUDGE_RUBRIC_VERSION",
    "ROLE_EPISODE_RUBRIC",
    "run_role_episode_judges",
]
