"""X1D judges for headline — policy-backed GRADE_ONLY JudgePacket."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.policy_backed_section_judges import run_policy_section_judges

JUDGE_RUBRIC_VERSION = "headline_x1d_v4"
JUDGE_RUBRIC_REF = "apps_rg/runtime/judges/headline_x1d.py#HEADLINE_GRADE_ONLY_RUBRIC"

HEADLINE_RUBRIC = """
You are evaluating a single resume headline formatted exactly as: SVP Engineering | X | Y | Z
(space-pipe-space separators; exactly four segments; first segment exactly "SVP Engineering"; 10-13 total words).
Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, cited_sentence_indexes, remediation_suggestions.

Score contract:
- score_scale must be "0_to_1" or "0_to_5" only.

Rubric dimensions:
1. factual_support: every substantive phrase in X/Y/Z is supported by claim_ledger source_fact_ids from the active proof pool only (bul_*, fact_*, or metric-suffixed IDs in allowed_fact_packet — never JD/briefing/target fields as proof).
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


def run_headline_judges(
    *,
    headline_line: str,
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    companion_context: str = "",
    mode: str = "blocked_if_unavailable",
    artifact_base: Path | None = None,
    targeting_context: dict[str, Any] | None = None,
    deterministic_gate_summary: dict[str, Any] | None = None,
    allowed_fact_packet: dict[str, Any] | None = None,
) -> list[JudgeOutput]:
    candidate = {
        "headline_line": headline_line,
        "resume_display_text": headline_line,
        "companion_context": companion_context,
    }
    packet_path = (artifact_base / "headline_judge_packet.json") if artifact_base else None
    outputs = run_policy_section_judges(
        "headline",
        candidate_output=candidate,
        section_rubric=HEADLINE_RUBRIC,
        rubric_ref=JUDGE_RUBRIC_REF,
        claim_ledger=claim_ledger,
        judge_keys=judge_keys,
        allowed_fact_packet=allowed_fact_packet,
        targeting_context=targeting_context,
        deterministic_gate_summary=deterministic_gate_summary,
        resume_display_text=headline_line,
        mode=mode,
        artifact_base=artifact_base,
        judge_packet_path=packet_path,
    )
    for o in outputs:
        o.judge_id = f"x1d_{o.provider_key}_headline"
        o.rubric_version = JUDGE_RUBRIC_VERSION
    return outputs


__all__ = ["run_headline_judges", "JUDGE_RUBRIC_VERSION", "HEADLINE_RUBRIC"]
