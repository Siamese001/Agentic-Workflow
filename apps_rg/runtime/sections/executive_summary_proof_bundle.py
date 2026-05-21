"""Post–X3 runtime proof surfaces for executive_summary (lane-local; not agentic_core)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from apps_rg.runtime.section_spine_terminology import section_lane_spine_classification

_CANONICAL_PRODUCER = "apps_rg_canonical_section_runtime"


def _repo_rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix().replace("\\", "/")


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except OSError:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None
    return h.hexdigest()


def _sha16_file(path: Path) -> str | None:
    full = _sha256_file(path)
    return full[:16] if full else None


def build_stage_sequence() -> dict[str, Any]:
    return {
        "schema_version": "executive_summary_stage_sequence_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_stages": [
            "U0_material_resolution",
            "section_lane_selection",
            "selected_fact_plan",
            "prompt_assembly",
            "l2_execution",
            "parse_and_canonical_ledger",
            "x2_deterministic_gates",
            "x1d_judges",
            "x3_exit",
        ],
        "runtime_terminal_stage": "x3_exit",
        "post_runtime_stages": [
            "runtime_exhaust_bundle",
            "section_runtime_proof_bundle",
            "l6_shadow_evaluation",
        ],
        "l6_is_runtime_gate": False,
        "l6_can_change_x3": False,
    }


def _inventory_rows(
    repo_root: Path,
    artifact_dir: Path,
    expected: Iterable[tuple[str, str, str, bool]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for logical_name, filename, stage_owner, required in expected:
        p = artifact_dir / filename
        digest256 = _sha256_file(p)
        digest16 = _sha16_file(p)
        rows.append(
            {
                "logical_name": logical_name,
                "filename": filename,
                "repo_relative_path": _repo_rel(repo_root, p) if p.exists() else None,
                "stage_owner": stage_owner,
                "required": required,
                "present": p.is_file(),
                "sha256": digest256,
                "sha16": digest16,
                "missing_reason": None if p.is_file() else "absent_at_emit",
                "producer": _CANONICAL_PRODUCER,
            }
        )
    return rows


def build_artifact_inventory(
    *,
    repo_root: Path,
    artifact_dir: Path,
) -> dict[str, Any]:
    expected: tuple[tuple[str, str, str, bool], ...] = (
        ("run_manifest", "run_manifest.json", "runtime finalize", True),
        ("l2_output", "l2_output.json", "l2_execution", True),
        ("runtime_payload", "runtime_payload.json", "U0_material_resolution", False),
        ("compiled_prompt_txt", "compiled_prompt.txt", "prompt_assembly", False),
        ("compiled_prompt_artifact", "compiled_prompt_artifact.json", "prompt_assembly", False),
        ("prompt_selection_trace", "prompt_selection_trace.json", "prompt_assembly", False),
        ("provider_request", "provider_request.json", "l2_execution", False),
        ("provider_response", "provider_response.json", "l2_execution", False),
        ("parsed_output", "parsed_output.json", "parse_and_canonical_ledger", False),
        ("canonical_claim_ledger_v2", "canonical_claim_ledger_v2.json", "parse_and_canonical_ledger", False),
        ("claim_ledger", "claim_ledger.json", "parse_and_canonical_ledger", False),
        ("text_claim_coverage", "text_claim_coverage.json", "parse_and_canonical_ledger", False),
        ("selected_fact_plan", "selected_fact_plan.json", "selected_fact_plan", False),
        ("x2_gate_outputs", "x2_gate_outputs.json", "x2_deterministic_gates", False),
        ("x1d_llm_judge_outputs", "x1d_llm_judge_outputs.json", "x1d_judges", False),
        ("x3_disposition", "x3_disposition.json", "x3_exit", True),
        ("cli_section_execution_report", "cli_section_execution_report.json", "x3_exit", False),
        ("real_l2_generation_result", "real_l2_generation_result.json", "l2_execution", False),
        ("section_metric_receipt", "section_metric_receipt.json", "x3_exit", False),
        ("l6_shadow_eval_package", "l6_shadow_eval_package.json", "l6_shadow_evaluation", False),
        ("artifact_inventory", "artifact_inventory.json", "post_runtime", True),
        ("stage_sequence", "stage_sequence.json", "post_runtime", True),
        ("runtime_exhaust_bundle", "runtime_exhaust_bundle.json", "post_runtime", True),
        ("section_runtime_proof_bundle", "section_runtime_proof_bundle.json", "post_runtime", True),
        ("resume_display_text", "resume_display_text.txt", "l2_execution", False),
        ("post_runtime_l6", "post_runtime/l6_shadow_eval_package.json", "l6_shadow_evaluation", False),
    )
    return {
        "schema_version": "artifact_inventory_v1",
        "section_id": "executive_summary",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "producer": _CANONICAL_PRODUCER,
        "artifacts": _inventory_rows(repo_root, artifact_dir, expected),
    }


def build_runtime_exhaust_bundle(
    *,
    repo_root: Path,
    artifact_dir: Path,
    x3: dict[str, Any],
    failed_gate_ids: list[str],
) -> dict[str, Any]:
    def ref(name: str) -> str | None:
        p = artifact_dir / name
        return _repo_rel(repo_root, p) if p.is_file() else None

    spine = section_lane_spine_classification()
    return {
        "schema_version": "runtime_exhaust_bundle_v1",
        "section_id": "executive_summary",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "producer": _CANONICAL_PRODUCER,
        "spine_classification": spine,
        "lane_local_runtime_exhaust": True,
        "claims_spine_runtime_exhaust_bundle": False,
        "runtime_terminal_boundary": "x3_exit_post_aggregation",
        "x3_code": x3.get("x3_code"),
        "x2_failed_gate_ids": list(failed_gate_ids),
        "refs": {
            "x3_disposition": ref("x3_disposition.json"),
            "x2_gate_outputs": ref("x2_gate_outputs.json"),
            "x1d_llm_judge_outputs": ref("x1d_llm_judge_outputs.json"),
            "provider_request": ref("provider_request.json"),
            "provider_response": ref("provider_response.json"),
            "parsed_output": ref("parsed_output.json"),
            "canonical_claim_ledger_v2": ref("canonical_claim_ledger_v2.json"),
            "text_claim_coverage": ref("text_claim_coverage.json"),
            "cli_section_execution_report": ref("cli_section_execution_report.json"),
        },
    }


def build_section_runtime_proof_bundle(
    *,
    repo_root: Path,
    artifact_dir: Path,
    inventory: dict[str, Any],
    exhaust_rel: str | None,
) -> dict[str, Any]:
    # L99 / full L7 certification not claimed for modular section lane runs.
    l7_surfaces = [
        "agentic_core_l7_route_family_coverage.json",
        "agentic_core_spine_proof.json",
        "integrated_runtime_artifact_manifest.json",
    ]
    spine = section_lane_spine_classification()
    return {
        "schema_version": "section_runtime_proof_bundle_v1",
        "section_id": "executive_summary",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "producer": _CANONICAL_PRODUCER,
        "spine_classification": spine,
        "proof_status": "INCOMPLETE",
        "missing_proof_surfaces": l7_surfaces,
        "certified": False,
        "runtime_exhaust_bundle_ref": exhaust_rel,
        "artifact_inventory_ref": _repo_rel(repo_root, artifact_dir / "artifact_inventory.json")
        if (artifact_dir / "artifact_inventory.json").is_file()
        else None,
        "notes": "Modular executive_summary lane proof; not a full L7/99 spine certification bundle.",
    }


def emit_executive_summary_post_x3_proof_artifacts(
    *,
    repo_root: Path,
    artifact_dir: Path,
    x3: Any,
    x2_gates: list[dict[str, Any]],
) -> None:
    """Write stage sequence and runtime exhaust bundle after X3 is final."""
    x3d = x3.to_dict() if hasattr(x3, "to_dict") else (x3 if isinstance(x3, dict) else {})
    failed = [str(g.get("gate_id")) for g in x2_gates if not g.get("pass")]

    stage_doc = build_stage_sequence()
    (artifact_dir / "stage_sequence.json").write_text(
        json.dumps(stage_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # runtime_exhaust_bundle.json is emitted by section_runtime_exhaust_spine_receipt (Wave 7).


def write_executive_summary_artifact_inventory(*, repo_root: Path, artifact_dir: Path) -> None:
    """Write artifact_inventory.json and refresh section_runtime_proof_bundle with inventory ref."""
    inv = build_artifact_inventory(repo_root=repo_root, artifact_dir=artifact_dir)
    (artifact_dir / "artifact_inventory.json").write_text(
        json.dumps(inv, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    exhaust_rel = (
        _repo_rel(repo_root, artifact_dir / "runtime_exhaust_bundle.json")
        if (artifact_dir / "runtime_exhaust_bundle.json").is_file()
        else None
    )
    bundle_doc = build_section_runtime_proof_bundle(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        inventory=inv,
        exhaust_rel=exhaust_rel,
    )
    (artifact_dir / "section_runtime_proof_bundle.json").write_text(
        json.dumps(bundle_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "build_artifact_inventory",
    "build_runtime_exhaust_bundle",
    "build_section_runtime_proof_bundle",
    "build_stage_sequence",
    "emit_executive_summary_post_x3_proof_artifacts",
    "write_executive_summary_artifact_inventory",
]
