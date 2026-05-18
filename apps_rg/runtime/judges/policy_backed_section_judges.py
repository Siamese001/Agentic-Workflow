"""Policy-backed GRADE_ONLY judge runner for standard apps_rg sections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput, run_llm_judges
from apps_rg.runtime.judges.grade_only_judge_packet import (
    build_grade_only_judge_packet,
    write_judge_packet,
)
from apps_rg.runtime.section_judge_policy import get_section_judge_policy, normalize_section_id


def run_policy_section_judges(
    section_id: str,
    *,
    candidate_output: dict[str, Any],
    section_rubric: str,
    rubric_ref: str,
    claim_ledger: list[dict[str, Any]],
    judge_keys: list[str],
    allowed_fact_packet: dict[str, Any] | list[dict[str, Any]] | None = None,
    targeting_context: dict[str, Any] | None = None,
    deterministic_gate_summary: dict[str, Any] | None = None,
    resume_display_text: str = "",
    mode: str = "blocked_if_unavailable",
    artifact_base: Path | None = None,
    judge_packet_path: Path | None = None,
) -> list[JudgeOutput]:
    """Build JudgePacket and invoke ``run_llm_judges`` with section policy model tiers."""
    sid = normalize_section_id(section_id)
    policy = get_section_judge_policy(sid)
    packet = build_grade_only_judge_packet(
        section_id=sid,
        candidate_output=candidate_output,
        section_rubric=section_rubric,
        rubric_ref=rubric_ref,
        claim_ledger=claim_ledger,
        allowed_fact_packet=allowed_fact_packet,
        targeting_context=targeting_context,
        deterministic_gate_summary=deterministic_gate_summary,
    )
    packet_ref: str | None = None
    if judge_packet_path is not None:
        packet_ref = write_judge_packet(judge_packet_path, packet)

    keys = list(judge_keys)
    if policy.required_judge_providers:
        keys = [k for k in keys if k in policy.required_judge_providers] or list(
            policy.required_judge_providers
        )

    display = resume_display_text or str(candidate_output.get("resume_display_text") or "")
    if not display and "headline_line" in candidate_output:
        display = str(candidate_output.get("headline_line") or "")

    return run_llm_judges(
        resume_display_text=display,
        claim_ledger=claim_ledger,
        judge_keys=keys,
        mode=mode,
        artifact_base=artifact_base,
        judge_packet=packet,
        judge_packet_ref=packet_ref,
        section_id=sid,
    )


__all__ = ["run_policy_section_judges"]
