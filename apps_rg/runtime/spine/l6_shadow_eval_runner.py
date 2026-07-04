"""apps_rg v40 L6 shadow-eval runner.

Runs only after the section RuntimeExhaustBundle is sealed. Outputs are
additive post-runtime artifacts and never change X3, Exit, L2, or L4 state.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L6_observability.shadow_eval.adapters import (
    from_section_artifacts,
    validate_v40_shadow_exhaust,
)
from agentic_core.L6_observability.shadow_eval.pipeline import (
    L6PipelineState,
    run_6a,
    run_observer,
)
from agentic_core.L6_observability.shadow_eval.span_export import write_span_artifacts
from apps_rg.runtime.observability.trace_reconciliation import (
    TRACE_RECONCILIATION_ARTIFACT,
    emit_trace_reconciliation_artifacts,
)
from apps_rg.runtime.shadow.l6_microstep_observability import (
    emit_apps_rg_l6_microstep_artifacts,
)

APPS_RG_L6_V40_SHADOW_EVAL_ENV = "APPS_RG_L6_V40_SHADOW_EVAL"
APPS_RG_L6_V40_SHADOW_EVAL_SKIP_ENV = "APPS_RG_L6_V40_SHADOW_EVAL_SKIP"
APPS_RG_L6_V40_L5_CERTIFICATION_REF_ENV = "APPS_RG_L6_V40_L5_CERTIFICATION_REF"

L6_V40_SHADOW_EVAL_PACKAGE_ARTIFACT = "l6_v40_shadow_eval_package.json"
L6_V40_SHADOW_EVAL_SPANS_ARTIFACT = "l6_v40_shadow_eval_spans.json"
L6_V40_SHADOW_EVAL_SPANS_JSONL_ARTIFACT = "l6_v40_shadow_eval_spans.jsonl"

APPS_RG_V40_STAGE_BY_FILE: dict[str, str] = {
    "runtime_exhaust_bundle.json": "EXIT",
    "exit_disposition_receipt.json": "EXIT",
    "x3_disposition.json": "EXIT",
    "x2_gate_outputs.json": "EXIT",
    "x1d_llm_judge_outputs.json": "EXIT",
    "l2_output.json": "L2",
    "provider_request.json": "L2",
    "provider_response.json": "L2",
    "route_contract.json": "L0",
    "compiled_prompt_artifact.json": "PA",
    "final_evidence_contract_bridge.json": "C0",
    "l6_shadow_eval_package.json": "EXIT",
    TRACE_RECONCILIATION_ARTIFACT: "L6",
}


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def l6_v40_shadow_eval_enabled(env: Mapping[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    if _truthy(source.get(APPS_RG_L6_V40_SHADOW_EVAL_SKIP_ENV)):
        return False
    configured = source.get(APPS_RG_L6_V40_SHADOW_EVAL_ENV)
    if configured is None or not str(configured).strip():
        return True
    return _truthy(configured)


def _repo_rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _jsonable(value: object) -> object:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return value


def run_l6_v40_shadow_eval_for_section(
    artifact_dir: Path,
    *,
    section_id: str,
    repo_root: Path,
    session_id: str = "",
    tenant_id: str = "",
    l5_certification_ref: str = "",
) -> dict[str, Path]:
    """Build v40 exhaust, run 6A + observer readiness, and write artifacts."""
    l5_ref = l5_certification_ref or os.environ.get(APPS_RG_L6_V40_L5_CERTIFICATION_REF_ENV, "")
    raw_exhaust = from_section_artifacts(
        artifact_dir,
        repo_root,
        section_id=section_id,
        stage_by_file=APPS_RG_V40_STAGE_BY_FILE,
        provider_lane="apps_rg",
        session_id=session_id,
        tenant_id=tenant_id,
        l5_certification_ref=l5_ref,
    )
    valid_v40, v40_gaps = validate_v40_shadow_exhaust(raw_exhaust)

    state = L6PipelineState()
    ingest = run_6a(state, raw_exhaust)
    readiness = run_observer(state)
    state.recorder.assert_no_runtime_feedback_edge()
    state.recorder.assert_pipeline_order()

    span_paths = write_span_artifacts(
        state.recorder.records,
        artifact_dir,
        json_name=L6_V40_SHADOW_EVAL_SPANS_ARTIFACT,
        jsonl_name=L6_V40_SHADOW_EVAL_SPANS_JSONL_ARTIFACT,
        source="apps_rg_l6_v40_shadow_eval",
    )
    microstep_paths = emit_apps_rg_l6_microstep_artifacts(
        output_dir=artifact_dir,
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        run_id=ingest.bundle.run_id,
        runtime_exhaust_bundle_id=ingest.bundle.runtime_exhaust_bundle_id,
        section_id=section_id,
    )
    trace_reconciliation_paths = emit_trace_reconciliation_artifacts(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        section_id=section_id,
        run_id=ingest.bundle.run_id,
    )
    parity_payload = {}
    try:
        parity_payload = json.loads(microstep_paths["l6_apps_eval_grain_parity"].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        parity_payload = {}

    package: dict[str, Any] = {
        "schema_version": "apps_rg.l6_v40_shadow_eval.v1",
        "section_id": section_id,
        "runtime_exhaust_bundle_id": ingest.bundle.runtime_exhaust_bundle_id,
        "runtime_exhaust_bundle_digest": ingest.bundle.deterministic_digest,
        "valid_v40_shadow_exhaust": valid_v40,
        "v40_gap_codes": v40_gaps,
        "readiness_decision": readiness.readiness_decision,
        "readiness_receipt": _jsonable(readiness),
        "g28_audit_completeness": _jsonable(state.g28),
        "g29_learning_firewall": _jsonable(state.g29),
        "ingest_gap_report": _jsonable(ingest.gap_report),
        "span_export_ref": _repo_rel(repo_root, span_paths["span_export_json"]),
        "span_export_jsonl_ref": _repo_rel(repo_root, span_paths["span_export_jsonl"]),
        "l6_microstep_observations_ref": _repo_rel(repo_root, microstep_paths["l6_microstep_observations"]),
        "l6_microstep_coverage_ref": _repo_rel(repo_root, microstep_paths["l6_microstep_coverage"]),
        "l6_microstep_rca_ref": _repo_rel(repo_root, microstep_paths["l6_microstep_rca"]),
        "l6_microstep_patterns_ref": _repo_rel(repo_root, microstep_paths["l6_microstep_patterns"]),
        "l6_microstep_future_run_proposals_ref": _repo_rel(
            repo_root,
            microstep_paths["l6_microstep_future_run_proposals"],
        ),
        "l6_apps_eval_alignment_ref": _repo_rel(repo_root, microstep_paths["l6_apps_eval_alignment"]),
        "l6_apps_eval_grain_parity_ref": _repo_rel(repo_root, microstep_paths["l6_apps_eval_grain_parity"]),
        "alignment_source": str(parity_payload.get("alignment_source") or "contract_only_pseudo_rows"),
        "apps_eval_rows_bound": bool(parity_payload.get("apps_eval_rows_bound") is True),
        "grain_parity_status": str(parity_payload.get("grain_parity_status") or "WARN"),
        "trace_reconciliation_ref": _repo_rel(
            repo_root,
            trace_reconciliation_paths["trace_reconciliation"],
        ),
        "trace_reconciliation_rows_ref": _repo_rel(
            repo_root,
            trace_reconciliation_paths["trace_reconciliation_rows"],
        ),
        "input_refs": {
            "artifact_dir": _repo_rel(repo_root, artifact_dir),
            "runtime_exhaust_bundle": _repo_rel(repo_root, artifact_dir / "runtime_exhaust_bundle.json"),
            "exit_disposition_receipt": _repo_rel(repo_root, artifact_dir / "exit_disposition_receipt.json"),
            "trace_reconciliation": _repo_rel(
                repo_root,
                trace_reconciliation_paths["trace_reconciliation"],
            ),
        },
        "current_run_mutation_assertion": False,
        "current_run_x3_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only_assertion": True,
    }
    package_path = artifact_dir / L6_V40_SHADOW_EVAL_PACKAGE_ARTIFACT
    package_path.write_text(
        json.dumps(package, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "l6_v40_shadow_eval_package": package_path,
        "l6_v40_shadow_eval_spans": span_paths["span_export_json"],
        "l6_v40_shadow_eval_spans_jsonl": span_paths["span_export_jsonl"],
        **trace_reconciliation_paths,
        **microstep_paths,
    }


def maybe_run_l6_v40_shadow_eval_for_section(
    artifact_dir: Path,
    *,
    section_id: str,
    repo_root: Path,
    session_id: str = "",
    tenant_id: str = "",
    l5_certification_ref: str = "",
    env: Mapping[str, str] | None = None,
) -> dict[str, Path]:
    if not l6_v40_shadow_eval_enabled(env):
        return {}
    return run_l6_v40_shadow_eval_for_section(
        artifact_dir,
        section_id=section_id,
        repo_root=repo_root,
        session_id=session_id,
        tenant_id=tenant_id,
        l5_certification_ref=l5_certification_ref,
    )


__all__ = [
    "APPS_RG_L6_V40_L5_CERTIFICATION_REF_ENV",
    "APPS_RG_L6_V40_SHADOW_EVAL_ENV",
    "APPS_RG_L6_V40_SHADOW_EVAL_SKIP_ENV",
    "L6_V40_SHADOW_EVAL_PACKAGE_ARTIFACT",
    "L6_V40_SHADOW_EVAL_SPANS_ARTIFACT",
    "L6_V40_SHADOW_EVAL_SPANS_JSONL_ARTIFACT",
    "l6_v40_shadow_eval_enabled",
    "maybe_run_l6_v40_shadow_eval_for_section",
    "run_l6_v40_shadow_eval_for_section",
]
