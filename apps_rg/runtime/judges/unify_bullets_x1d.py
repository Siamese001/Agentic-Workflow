"""X1D LLM judges for unify_bullets — policy-backed GRADE_ONLY JudgePacket."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.judges.employment_bullet_judge_rubric import (
    assert_no_exec_summary_dimensions,
    grade_only_rubric_text,
)
from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.policy_backed_section_judges import run_policy_section_judges

JUDGE_RUBRIC_VERSION = "unify_bullets_x1d_v4"
JUDGE_RUBRIC_REF = "apps_rg/runtime/judges/employment_bullet_judge_rubric.py#unify_bullets"

UNIFY_RUBRIC = grade_only_rubric_text(
    "unify_bullets",
    bullet_count=6,
    bullet_id_range="bul_unify_001..006",
)
assert_no_exec_summary_dimensions("unify_bullets")


def _bullets_display_text(bullets: list[dict[str, Any]]) -> str:
    lines = []
    for idx, bullet in enumerate(bullets, start=1):
        bid = bullet.get("bullet_id", f"bullet_{idx}")
        text = bullet.get("bullet_text", "")
        lines.append(f"[{idx}] {bid}: {text}")
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
