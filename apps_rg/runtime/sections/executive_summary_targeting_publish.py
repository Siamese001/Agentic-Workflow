"""Publish targeting parity receipt + section_input_usage_ledger for executive_summary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.targeting_context_authority import (
    GenerationMaterialContext,
    JudgeMaterialContext,
    evaluate_targeting_parity,
    judge_material_context_from_packet,
    material_targeting_digest,
    merge_targeting_parity_into_usage_ledger,
    require_material_targeting_bundle,
)


def resolve_judge_packet_for_parity(artifact_dir: Path, *, fallback: dict[str, Any]) -> dict[str, Any]:
    """Prefer post-X2 refresh packet when present; else initial judge packet."""
    for name in (
        "executive_summary_judge_packet_post_x2.json",
        "executive_summary_judge_packet.json",
    ):
        path = artifact_dir / name
        if not path.is_file():
            continue
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(loaded, dict):
            return loaded
    return fallback


def audit_judge_packet_targeting_digests(
    artifact_dir: Path,
    *,
    generation_material: GenerationMaterialContext,
) -> dict[str, Any]:
    """Manifest for regen cycles: targeting digests per on-disk judge packet."""
    rows: list[dict[str, Any]] = []
    gen_d = generation_material.generation_material_digest
    for path in sorted(artifact_dir.glob("executive_summary_judge_packet*.json")):
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(packet, dict):
            continue
        judge = judge_material_context_from_packet(packet)
        rows.append(
            {
                "path": path.name,
                "judge_material_digest": judge.judge_material_digest,
                "matches_generation": judge.judge_material_digest == gen_d,
            }
        )
    all_match = bool(rows) and all(r.get("matches_generation") for r in rows)
    return {
        "schema": "judge_packet_targeting_digest_audit_v1",
        "generation_material_digest": gen_d,
        "packets": rows,
        "all_packets_match_generation": all_match,
    }


def judge_packet_for_parity_evaluation(
    judge_packet: dict[str, Any],
    *,
    generation_material: GenerationMaterialContext,
) -> dict[str, Any]:
    """Prefer on-disk judge packet targeting; else generation material (pre-judge / X2-block)."""
    if isinstance(judge_packet, dict):
        tc = judge_packet.get("targeting_context")
        if isinstance(tc, dict):
            jd = str(tc.get("jd_text") or "")
            br = str(tc.get("briefing") or "")
            if jd or br:
                return judge_packet
    return {
        "targeting_context": {
            "jd_text": generation_material.jd_text_material,
            "briefing": generation_material.briefing_text_material,
        }
    }


def publish_targeting_parity_and_usage_ledger(
    *,
    artifact_dir: Path,
    runtime_payload: dict[str, Any],
    generation_material: GenerationMaterialContext,
    judge_packet: dict[str, Any],
    usage_doc: dict[str, Any],
    write_json_fn: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Write parity receipt + merged usage ledger; update runtime_payload."""
    bundle = require_material_targeting_bundle(runtime_payload)
    judge_material = judge_material_context_from_packet(
        judge_packet_for_parity_evaluation(judge_packet, generation_material=generation_material)
    )
    parity = evaluate_targeting_parity(
        generation=generation_material,
        judge=judge_material,
        bundle=bundle,
    )
    write_json_fn(artifact_dir / "targeting_context_parity_receipt.json", parity)
    runtime_payload["targeting_context_parity"] = parity
    merged = merge_targeting_parity_into_usage_ledger(dict(usage_doc), parity)
    write_json_fn(artifact_dir / "section_input_usage_ledger.json", merged)
    return parity, merged


INSTRUCTIONAL_TRIM_COMPONENTS: frozenset[str] = frozenset(
    {
        "e0_examples",
        "y0_style_preferences",
        "jd_briefing_prose",
        "jd_text_prose",
    }
)

# E0 is excluded from judge GRADE_ONLY packets by design (see JUDGE_EXCLUDED_BY_DESIGN);
# trimming E0 alone does not make judge-regen deltas unfair to the writer thread.
JUDGE_REGEN_BLOCKING_TRIM_COMPONENTS: frozenset[str] = frozenset(
    {
        "y0_style_preferences",
        "jd_briefing_prose",
        "jd_text_prose",
    }
)


def _trimmed_component_names(token_budget_receipt: dict[str, Any] | None) -> set[str]:
    if not isinstance(token_budget_receipt, dict) or not token_budget_receipt.get("trim_applied"):
        return set()
    return {
        str(row.get("component") or "")
        for row in (token_budget_receipt.get("trimmed_components") or [])
        if isinstance(row, dict)
    }


def instructional_surface_drift_risk(token_budget_receipt: dict[str, Any] | None) -> bool:
    """True when L2 trim removed instructional slots (manifest/RCA; includes optional E0)."""
    return bool(_trimmed_component_names(token_budget_receipt) & INSTRUCTIONAL_TRIM_COMPONENTS)


def judge_regen_blocked_by_trim(token_budget_receipt: dict[str, Any] | None) -> bool:
    """True when trim removed Y0/JD prose judges also lack — blocks same-authority judge regen."""
    return bool(_trimmed_component_names(token_budget_receipt) & JUDGE_REGEN_BLOCKING_TRIM_COMPONENTS)


def parity_allows_judge_regen(
    runtime_payload: dict[str, Any],
    *,
    token_budget_receipt: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    tcp = runtime_payload.get("targeting_context_parity")
    if not isinstance(tcp, dict):
        return False, "targeting_context_parity missing"
    if tcp.get("parity_match") is not True:
        return False, "parity_match is false — judge regen would use unfair targeting context"
    if judge_regen_blocked_by_trim(token_budget_receipt):
        return (
            False,
            "L2 instructional surface trimmed (Y0/JD prose) — judge packet lacks those blocks",
        )
    return True, "parity_match"


__all__ = [
    "INSTRUCTIONAL_TRIM_COMPONENTS",
    "JUDGE_REGEN_BLOCKING_TRIM_COMPONENTS",
    "audit_judge_packet_targeting_digests",
    "instructional_surface_drift_risk",
    "judge_packet_for_parity_evaluation",
    "judge_regen_blocked_by_trim",
    "parity_allows_judge_regen",
    "publish_targeting_parity_and_usage_ledger",
    "resolve_judge_packet_for_parity",
]
