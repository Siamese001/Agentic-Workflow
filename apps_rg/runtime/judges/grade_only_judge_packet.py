"""Generic GRADE_ONLY JudgePacket builder for apps_rg section X1D judges."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.section_judge_policy import get_section_judge_policy, normalize_section_id

JUDGE_PACKET_VERSION = "apps_rg_grade_only_judge_packet_v1"

GRADE_ONLY_INSTRUCTION = """
You are grading a generated resume section candidate produced by a separate generator.
judge_task: GRADE_ONLY

Mandatory rules:
- Do NOT write replacement section content.
- Do NOT rewrite or edit the candidate text.
- Do NOT add claims, metrics, credentials, or facts.
- JD_TEXT and BRIEFING are targeting context only — never proof.
- Grade only against the rubric, allowed_fact_packet (when provided), and candidate_output.
- Return ONLY the required structured judge JSON schema (no markdown fences, no prose).
""".strip()

REQUIRED_JUDGE_OUTPUT_SCHEMA = """
Return ONLY one compact JSON object:
{"score_scale":"0_to_5","score":0.0,"threshold":4.0,"pass":true,"decisive_failure":false,
 "findings":["short strings"],"cited_sentence_indexes":[1],
 "remediation_suggestions":[],"rationale":"one short paragraph",
 "fail_reasons":[],"unsupported_claims":[],"quality_flags":[]}
score_scale must be 0_to_5 or 0_to_1 with in-range score/threshold.
""".strip()


def build_grade_only_judge_packet(
    *,
    section_id: str,
    candidate_output: dict[str, Any],
    section_rubric: str,
    rubric_ref: str,
    claim_ledger: list[dict[str, Any]] | None = None,
    allowed_fact_packet: dict[str, Any] | list[dict[str, Any]] | None = None,
    targeting_context: dict[str, Any] | None = None,
    deterministic_gate_summary: dict[str, Any] | None = None,
    source_fact_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Build canonical GRADE_ONLY JudgePacket for any section."""
    sid = normalize_section_id(section_id)
    policy = get_section_judge_policy(sid)
    if policy.grade_only_required and policy.replacement_generation_allowed:
        raise ValueError("policy invariant: grade_only_required implies no replacement generation")

    targeting = dict(targeting_context or {})
    packet = {
        "judge_packet_version": JUDGE_PACKET_VERSION,
        "section": sid,
        "judge_task": "GRADE_ONLY",
        "candidate_output": candidate_output,
        "claim_ledger": list(claim_ledger or []),
        "source_fact_ids": list(source_fact_ids or []),
        "allowed_fact_packet": allowed_fact_packet,
        "targeting_context": {
            "target_title": targeting.get("target_title", ""),
            "target_company": targeting.get("target_company", ""),
            "jd_text": targeting.get("jd_text", ""),
            "briefing": targeting.get("briefing", ""),
        },
        "proof_boundary": {
            "jd_is_targeting_context_only": True,
            "briefing_is_targeting_context_only": True,
            "claims_must_be_supported_by_allowed_fact_packet": True,
            "judges_must_not_rewrite": True,
        },
        "deterministic_gate_summary": dict(deterministic_gate_summary or {}),
        "section_specific_rubric": section_rubric.strip(),
        "grading_only_instructions": GRADE_ONLY_INSTRUCTION,
        "required_judge_output_schema": REQUIRED_JUDGE_OUTPUT_SCHEMA,
        "rubric_ref": rubric_ref,
        "judge_tier": policy.judge_tier.value,
        "judge_packet_required": policy.judge_packet_required,
    }
    return packet


def judge_packet_hash(packet: dict[str, Any]) -> str:
    payload = {k: v for k, v in packet.items() if k != "judge_packet_hash"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def write_judge_packet(path: Path, packet: dict[str, Any]) -> str:
    enriched = dict(packet)
    enriched["judge_packet_hash"] = judge_packet_hash(packet)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        from apps_rg.runtime.runtime_proof_layout import repo_relative_path

        return repo_relative_path(path)
    except Exception:  # noqa: BLE001
        return path.as_posix()


def render_judge_prompt_from_packet(packet: dict[str, Any]) -> str:
    """Render judge user message from JudgePacket — never the generator compiled_prompt."""
    candidate = packet.get("candidate_output") or {}
    return "\n\n".join(
        [
            packet.get("grading_only_instructions") or GRADE_ONLY_INSTRUCTION,
            f"SECTION: {packet.get('section')}",
            f"RUBRIC_REF: {packet.get('rubric_ref')}",
            (packet.get("section_specific_rubric") or "").strip(),
            (packet.get("required_judge_output_schema") or REQUIRED_JUDGE_OUTPUT_SCHEMA).strip(),
            "CANDIDATE_OUTPUT:\n" + json.dumps(candidate, ensure_ascii=False, indent=2),
            "ALLOWED_FACT_PACKET:\n"
            + json.dumps(packet.get("allowed_fact_packet"), ensure_ascii=False, indent=2),
            "CLAIM_LEDGER:\n"
            + json.dumps(packet.get("claim_ledger") or [], separators=(",", ":")),
            "TARGETING_CONTEXT (not proof):\n"
            + json.dumps(packet.get("targeting_context") or {}, ensure_ascii=False, indent=2),
            "PROOF_BOUNDARY:\n"
            + json.dumps(packet.get("proof_boundary") or {}, ensure_ascii=False, indent=2),
            "DETERMINISTIC_GATE_SUMMARY:\n"
            + json.dumps(packet.get("deterministic_gate_summary") or {}, ensure_ascii=False, indent=2),
        ]
    )


__all__ = [
    "GRADE_ONLY_INSTRUCTION",
    "JUDGE_PACKET_VERSION",
    "REQUIRED_JUDGE_OUTPUT_SCHEMA",
    "build_grade_only_judge_packet",
    "judge_packet_hash",
    "render_judge_prompt_from_packet",
    "write_judge_packet",
]
