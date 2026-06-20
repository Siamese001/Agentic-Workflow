"""apps_eval bridge into core L6 shadow observability.

apps_eval is a proof harness. This bridge emits completed-eval evidence for L6
observation only; it never requests current-run mutation or durable writes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L6_observability.shadow_eval.pipeline import (
    L6PipelineState,
    run_6a,
    run_observer,
)
from agentic_core.L6_observability.shadow_eval.span_export import write_span_artifacts
from apps_eval.contracts import CURRENT_EVAL_RECORD_SCHEMA_VERSION, CompletedEvalRecord

L6_SHADOW_BRIDGE_ARTIFACT = "l6_shadow_bridge.json"
L6_SHADOW_BRIDGE_SPANS_ARTIFACT = "l6_shadow_bridge_spans.json"
L6_SHADOW_BRIDGE_SPANS_JSONL_ARTIFACT = "l6_shadow_bridge_spans.jsonl"


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


def _hash_ref(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _write_json_artifact(path: Path, payload: Any) -> Path:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def build_completed_eval_shadow_exhaust(
    record: CompletedEvalRecord,
    *,
    eval_record_path: str,
    l6_handoff_path: str = "",
) -> dict[str, object]:
    """Build a v40-like completed-run exhaust payload for an apps_eval record."""
    scorecard = record.scorecard.to_dict()
    record_ref = eval_record_path.replace("\\", "/")
    handoff_ref = l6_handoff_path.replace("\\", "/") if l6_handoff_path else ""
    outcome_class = "normal_success" if record.scorecard.verdict == "pass" else "policy_failure"
    trace_root = f"trace:apps_eval:{record.record_id}"
    policy_hash = _hash_ref(record.rubric_ids)
    return {
        "runtime_boundary_crossed": True,
        "completed_at": record.created_at,
        "request_id": f"apps-eval:{record.record_id}",
        "run_id": record.record_id,
        "session_id": record.suite_id,
        "tenant_id": "apps_eval",
        "trace_root": trace_root,
        "exit_disposition_ref": record_ref,
        "exit_disposition": record.scorecard.verdict,
        "route_id": record.suite_id,
        "execution_form": "apps_eval_completed_eval_record",
        "terminal_class": outcome_class,
        "outcome_class": outcome_class,
        "policy_hash": policy_hash,
        "blueprint_hash": _hash_ref({"suite_id": record.suite_id, "app_id": record.app_id}),
        "replay_key": f"apps_eval:deterministic:{record.record_id}",
        "route_contract_ref": record.suite_id,
        "l1_plan_ref": "apps_eval:proof_harness",
        "c0_evidence_contract_refs": [record_ref],
        "prompt_envelope_refs": [],
        "l2_artifact_refs": [record_ref],
        "source_lineage_manifest_ref": record_ref,
        "l5_certification_ref": f"l5-cert-ref:apps_eval:{record.record_id}",
        "source_exhaust": [
            {
                "source_type": "apps_eval_completed_eval_record",
                "source_ref": record_ref,
                "source_hash": _hash_ref(record.to_dict()),
                "source_schema_version": CURRENT_EVAL_RECORD_SCHEMA_VERSION,
                "observed_stage": "EXIT",
                "expected_stage_order": 7,
                "lineage_parent_refs": [trace_root],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            }
        ],
        "events": [
            {
                "event_type": "apps_eval.scorecard",
                "stage": "EXIT",
                "source_ref": record_ref,
                "payload_ref": record_ref,
                "trace_id": trace_root,
                "span_id": f"apps_eval:{record.record_id}:scorecard",
                "parent_span_id": None,
                "provider_lane": "apps_eval",
                "prompt_hash": "",
                "context_hash": "",
                "artifact_digest": _hash_ref(scorecard),
                "eval_readiness_hint": "READY",
            }
        ],
        "artifacts": {
            "generated": [record_ref] + ([handoff_ref] if handoff_ref else []),
            "sealed": [record_ref],
            "file_hashes": {record_ref: _hash_ref(record.to_dict())},
            "artifact_lineage": {record_ref: [trace_root]},
            "missing": [],
            "orphans": [],
        },
    }


def emit_completed_eval_l6_shadow_bridge(
    record: CompletedEvalRecord,
    run_dir: Path,
    *,
    eval_record_path: str,
    l6_handoff_path: str = "",
) -> dict[str, str]:
    """Run 6A + observer readiness for a completed apps_eval record."""
    raw_exhaust = build_completed_eval_shadow_exhaust(
        record,
        eval_record_path=eval_record_path,
        l6_handoff_path=l6_handoff_path,
    )
    state = L6PipelineState()
    ingest = run_6a(state, raw_exhaust)
    readiness = run_observer(state)
    state.recorder.assert_no_runtime_feedback_edge()
    state.recorder.assert_pipeline_order()
    span_paths = write_span_artifacts(
        state.recorder.records,
        run_dir,
        json_name=L6_SHADOW_BRIDGE_SPANS_ARTIFACT,
        jsonl_name=L6_SHADOW_BRIDGE_SPANS_JSONL_ARTIFACT,
        source="apps_eval_l6_shadow_bridge",
    )
    bridge = {
        "schema_version": "apps_eval.l6_shadow_bridge.v1",
        "record_id": record.record_id,
        "suite_id": record.suite_id,
        "app_id": record.app_id,
        "runtime_exhaust_bundle_id": ingest.bundle.runtime_exhaust_bundle_id,
        "readiness_decision": readiness.readiness_decision,
        "readiness_receipt": _jsonable(readiness),
        "g28_audit_completeness": _jsonable(state.g28),
        "g29_learning_firewall": _jsonable(state.g29),
        "span_export_ref": span_paths["span_export_json"].as_posix(),
        "span_export_jsonl_ref": span_paths["span_export_jsonl"].as_posix(),
        "requested_action": "consume_completed_eval_record_only",
        "current_run_mutated": False,
        "direct_l4_write_attempted": False,
        "durable_write_attempted": False,
        "future_run_only": True,
    }
    bridge_path = _write_json_artifact(run_dir / L6_SHADOW_BRIDGE_ARTIFACT, bridge)
    return {
        "l6_shadow_bridge": bridge_path.as_posix(),
        "l6_shadow_bridge_spans": span_paths["span_export_json"].as_posix(),
        "l6_shadow_bridge_spans_jsonl": span_paths["span_export_jsonl"].as_posix(),
    }


def emit_driver_l6_shadow_bridge(
    run_dir: Path,
    *,
    eval_id: str | None,
    app_scorecards: list[Mapping[str, Any]],
    output_refs: Mapping[str, str],
) -> dict[str, str]:
    """Write a lightweight downstream L6 bridge for trend/gate outputs."""
    run_dir.mkdir(parents=True, exist_ok=True)
    bridge = build_driver_l6_shadow_bridge_payload(
        eval_id=eval_id,
        app_scorecards=app_scorecards,
        output_refs=output_refs,
    )
    bridge_path = _write_json_artifact(run_dir / L6_SHADOW_BRIDGE_ARTIFACT, bridge)
    return {"l6_shadow_bridge": bridge_path.as_posix()}


def build_driver_l6_shadow_bridge_payload(
    *,
    eval_id: str | None,
    app_scorecards: list[Mapping[str, Any]],
    output_refs: Mapping[str, str],
) -> dict[str, Any]:
    """Build a lightweight bridge payload for apps_shared proof drivers."""
    return {
        "schema_version": "apps_eval.driver_l6_shadow_bridge.v1",
        "eval_id": eval_id,
        "scorecard_count": len(app_scorecards),
        "output_refs": dict(output_refs),
        "requires_g28_audit_completeness": True,
        "requires_g29_learning_firewall": True,
        "requested_action": "consume_completed_eval_artifacts_only",
        "current_run_mutated": False,
        "direct_l4_write_attempted": False,
        "durable_write_attempted": False,
        "future_run_only": True,
    }


__all__ = [
    "L6_SHADOW_BRIDGE_ARTIFACT",
    "L6_SHADOW_BRIDGE_SPANS_ARTIFACT",
    "L6_SHADOW_BRIDGE_SPANS_JSONL_ARTIFACT",
    "build_completed_eval_shadow_exhaust",
    "build_driver_l6_shadow_bridge_payload",
    "emit_driver_l6_shadow_bridge",
    "emit_completed_eval_l6_shadow_bridge",
]
