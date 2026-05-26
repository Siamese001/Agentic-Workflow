"""Publish targeting parity receipt + section_input_usage_ledger for executive_summary."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from apps_rg.runtime.targeting_context_authority import (
    GenerationMaterialContext,
    JudgeMaterialContext,
    evaluate_targeting_parity,
    graph_targeting_capsule_from_packet,
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
    gen_capsule = runtime_payload.get("graph_targeting_capsule")
    gen_capsule_dict = dict(gen_capsule) if isinstance(gen_capsule, dict) else None
    judge_capsule = graph_targeting_capsule_from_packet(
        judge_packet_for_parity_evaluation(judge_packet, generation_material=generation_material),
    )
    parity = evaluate_targeting_parity(
        generation=generation_material,
        judge=judge_material,
        bundle=bundle,
        graph_targeting_capsule_generation=gen_capsule_dict,
        graph_targeting_capsule_judge=judge_capsule or gen_capsule_dict,
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


def targeting_parity_strict_enforcement_enabled() -> bool:
    raw = os.environ.get("APPS_RG_EXEC_SUMMARY_TARGETING_PARITY_STRICT", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def enforce_targeting_parity_before_judge_panel(
    parity_receipt: dict[str, Any],
) -> tuple[bool, str]:
    """Fail closed before X1D panel when binding digests mismatch (W3.1)."""
    status = str(parity_receipt.get("targeting_parity_status") or "")
    if status == "match" or parity_receipt.get("parity_match") is True:
        return True, "targeting_parity_ok"
    if targeting_parity_strict_enforcement_enabled():
        return (
            False,
            "targeting_parity_status=mismatch blocks judge panel "
            f"(generation={parity_receipt.get('generation_targeting_digest')!r} "
            f"judge={parity_receipt.get('judge_targeting_digest')!r})",
        )
    return True, "targeting_parity_warn_only"


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
    "enforce_targeting_parity_before_judge_panel",
    "instructional_surface_drift_risk",
    "judge_packet_for_parity_evaluation",
    "judge_regen_blocked_by_trim",
    "parity_allows_judge_regen",
    "publish_targeting_parity_and_usage_ledger",
    "resolve_judge_packet_for_parity",
    "targeting_parity_strict_enforcement_enabled",
]
