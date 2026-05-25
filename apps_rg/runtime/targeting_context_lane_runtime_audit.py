"""Runtime targeting parity audit helpers — evidence from on-disk lane artifacts only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.targeting_context_authority import (
    evaluate_targeting_parity,
    generation_material_context_from_compiled_prompt,
    judge_material_context_from_packet,
    material_targeting_digest,
)

TARGETING_NOT_APPLICABLE = "TARGETING_NOT_APPLICABLE"

LANE_RUNTIME_AUDIT_SPECS: dict[str, dict[str, Any]] = {
    "executive_summary": {
        "compiled_prompt_glob": "compiled_prompt.txt",
        "judge_packet_glob": "executive_summary_judge_packet.json",
        "ledger_glob": "section_input_usage_ledger.json",
        "parity_receipt_glob": "targeting_context_parity_receipt.json",
        "judges_use_targeting": True,
    },
    "headline": {
        "compiled_prompt_glob": "compiled_prompt.txt",
        "judge_packet_glob": None,
        "ledger_glob": "section_input_usage_ledger.json",
        "judges_use_targeting": False,
    },
    "competencies": {
        "compiled_prompt_glob": "compiled_prompt.txt",
        "judge_packet_glob": None,
        "ledger_glob": "section_input_usage_ledger.json",
        "judges_use_targeting": False,
    },
    "unify_bullets": {
        "compiled_prompt_glob": "compiled_prompt.txt",
        "judge_packet_glob": None,
        "ledger_glob": "section_input_usage_ledger.json",
        "judges_use_targeting": False,
    },
    "unify_narrative": {
        "compiled_prompt_glob": "compiled_prompt.txt",
        "judge_packet_glob": None,
        "ledger_glob": "section_input_usage_ledger.json",
        "judges_use_targeting": False,
    },
    "ibm_bullets": {
        "compiled_prompt_glob": "compiled_prompt.txt",
        "judge_packet_glob": None,
        "ledger_glob": "section_input_usage_ledger.json",
        "judges_use_targeting": True,
    },
    "ibm_narrative": {
        "compiled_prompt_glob": "compiled_prompt.txt",
        "judge_packet_glob": None,
        "ledger_glob": "section_input_usage_ledger.json",
        "judges_use_targeting": False,
    },
}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def audit_lane_artifact_dir(artifact_dir: Path, *, lane_id: str) -> dict[str, Any]:
    """Classify targeting parity from runtime artifacts; no grep-based inference."""
    spec = LANE_RUNTIME_AUDIT_SPECS.get(lane_id)
    if spec is None:
        return {"lane_id": lane_id, "status": "UNKNOWN_LANE"}

    row: dict[str, Any] = {
        "lane_id": lane_id,
        "artifact_dir": str(artifact_dir),
        "schema": "targeting_lane_runtime_audit_v1",
    }

    if not spec.get("judges_use_targeting"):
        row["classification"] = TARGETING_NOT_APPLICABLE
        row["parity_match"] = None
        row["runtime_evidence"] = "judges_do_not_evaluate_targeting_dimensions"
        ledger = _read_json(artifact_dir / str(spec.get("ledger_glob") or ""))
        if ledger:
            row["ledger_targeting_bundle_digest"] = ledger.get("targeting_bundle_digest")
            row["ledger_generation_material_digest"] = ledger.get("generation_material_digest")
            row["ledger_judge_material_digest"] = ledger.get("judge_material_digest")
            row["ledger_parity_match"] = ledger.get("parity_match")
        return row

    parity_path = artifact_dir / str(spec.get("parity_receipt_glob") or "")
    parity = _read_json(parity_path)
    if parity and parity.get("schema") == "targeting_context_parity_v1":
        row.update(
            {
                "classification": "RUNTIME_PARITY_RECEIPT",
                "targeting_bundle_digest": parity.get("targeting_bundle_digest"),
                "generation_material_digest": parity.get("generation_material_digest"),
                "judge_material_digest": parity.get("judge_material_digest"),
                "parity_match": parity.get("parity_match"),
            }
        )
        return row

    compiled_path = artifact_dir / str(spec.get("compiled_prompt_glob") or "")
    jp_name = spec.get("judge_packet_glob")
    if not compiled_path.is_file() or not jp_name:
        row["classification"] = "INSUFFICIENT_RUNTIME_ARTIFACTS"
        return row

    compiled = compiled_path.read_text(encoding="utf-8")
    gen = generation_material_context_from_compiled_prompt(compiled)
    jp = _read_json(artifact_dir / jp_name)
    if jp is None:
        row["classification"] = "INSUFFICIENT_RUNTIME_ARTIFACTS"
        return row

    judge = judge_material_context_from_packet(jp)
    parity = evaluate_targeting_parity(generation=gen, judge=judge, bundle=None)
    bundle_raw = _read_json(artifact_dir / "targeting_context_receipt.json")
    if bundle_raw:
        parity["targeting_bundle_digest"] = bundle_raw.get("bundle_digest")

    row.update(
        {
            "classification": "RUNTIME_DERIVED_PARITY",
            "targeting_bundle_digest": parity.get("targeting_bundle_digest"),
            "generation_material_digest": parity.get("generation_material_digest"),
            "judge_material_digest": parity.get("judge_material_digest"),
            "parity_match": parity.get("parity_match"),
        }
    )
    return row


def build_lane_runtime_matrix(artifact_roots: dict[str, Path]) -> dict[str, Any]:
    """artifact_roots: lane_id -> artifact_dir with runtime proof."""
    rows = {
        lane: audit_lane_artifact_dir(path, lane_id=lane)
        for lane, path in artifact_roots.items()
    }
    return {"schema": "targeting_lane_runtime_matrix_v1", "lanes": rows}


__all__ = [
    "TARGETING_NOT_APPLICABLE",
    "LANE_RUNTIME_AUDIT_SPECS",
    "audit_lane_artifact_dir",
    "build_lane_runtime_matrix",
]
