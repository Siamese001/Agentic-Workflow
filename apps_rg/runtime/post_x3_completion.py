"""Post-X3 completion for full apps_rg resume runs.

The full resume product path is not complete at X3 alone. After a successful
all-section package is produced, this module admits the generated resume
artifact through UWG, runs apps_eval against that exact current-run snapshot,
and binds the resulting L6 shadow bridge back into the run evidence.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L4_state.contracts import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
)
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.uwg.durable_write_gateway import get_default_gateway
from agentic_core.L6_observability.shadow_eval.grain_parity import (
    L6_APPS_EVAL_COVERAGE_JOIN_KEY,
    build_l6_apps_eval_grain_parity,
)
from agentic_core.L6_observability.shadow_eval.microsteps import (
    EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF,
    EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY,
    EVIDENCE_CLASS_FAILURE_TERMINAL_ADVISORY,
)
from agentic_core.runtime.artifacts.integrated_runtime_emitter import compute_artifact_hash
from apps_rg.runtime.package.apps_rg_full_resume_x3_eligibility import (
    evaluate_apps_rg_full_success_eligibility,
)
from apps_rg.runtime.shadow.l6_microstep_observability import (
    emit_apps_rg_l6_microstep_artifacts,
)

POST_X3_COMPLETION_RECEIPT = "apps_rg_post_x3_completion_receipt.json"
UWG_DIR = "uwg"
UWG_COMMIT_REQUEST = "commit_request.json"
UWG_VALIDATION_RECEIPT = "uwg_validation_receipt.json"
UWG_COMMIT_RECEIPT = "uwg_commit_receipt.json"
UWG_REFRESH_RECEIPTS = "uwg_refresh_receipts.json"
POST_X3_FAILURE_L6_SHADOW_BRIDGE = "post_x3_failure_l6_shadow_bridge.json"
POST_X3_FAILURE_L6_APPS_EVAL_GRAIN_PARITY = "post_x3_failure_l6_apps_eval_grain_parity.json"
L6_SECTION_APPS_EVAL_BINDINGS = "l6_section_apps_eval_bindings.json"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _payload(doc: Mapping[str, Any]) -> dict[str, Any]:
    inner = doc.get("payload")
    return dict(inner) if isinstance(inner, dict) else dict(doc)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _artifact_or_repo_rel(path: Path, artifact_dir: Path) -> str:
    try:
        return path.relative_to(artifact_dir).as_posix()
    except ValueError:
        pass
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _artifact_ref(root: Path, path: Path) -> str:
    return f"artifact://{_repo_rel(path, root)}"


def _json_ready(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _json_ready(dataclasses.asdict(value))
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


def _state_diffs_digest(state_diffs: list[Any]) -> str:
    from agentic_core.L4_state.uwg.durable_write_gateway import compute_state_diffs_digest

    return compute_state_diffs_digest(state_diffs)


def _commit_request_signature(
    *,
    commit_request_id: str,
    state_diff_hash: str,
    clearance_proof_id: str,
) -> str:
    from agentic_core.L4_state.contracts.digests import compute_deterministic_digest

    return compute_deterministic_digest(
        {
            "commit_request_id": commit_request_id,
            "staged_diff_hash": state_diff_hash,
            "clearance_proof_id": clearance_proof_id,
        }
    )


def _generated_resume_path(artifact_dir: Path) -> Path | None:
    candidates = [
        artifact_dir / "outputs" / "generated_resume.json",
        artifact_dir / "modular_r4" / "outputs" / "generated_resume.json",
        artifact_dir / "modular_r4" / "final_resume_assembly" / "final_resume.json",
        artifact_dir / "modular_r4" / "outputs" / "final_resume.json",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def _load_output_manifest(artifact_dir: Path) -> dict[str, Any]:
    manifest = _read_json(artifact_dir / "apps_rg_output_manifest.json")
    if manifest:
        return manifest
    generated = _generated_resume_path(artifact_dir)
    if generated is None:
        return {}
    return {
        "schema_version": "apps_rg_output_manifest.synthetic_for_post_x3.v1",
        "generated_resume_json_relpath": _repo_rel(generated, artifact_dir),
        "apps_rg_generation_status": "REAL_RESUME",
        "full_resume_generated": True,
        "resume_shape": "REAL_RESUME",
        "docx_output_required": True,
        "required_artifacts": {
            "generated_resume_json": "verified",
            "resume_docx": "missing",
            "docx_verified": False,
        },
    }


def is_full_resume_product_artifact_dir(artifact_dir: Path | str) -> bool:
    art = Path(artifact_dir)
    return any(
        path.is_file()
        for path in (
            art / "apps_rg_output_manifest.json",
            art / "outputs" / "generated_resume.json",
            art / "full_run_section_status.json",
        )
    )


def _identity(artifact_dir: Path, result: Mapping[str, Any]) -> dict[str, str]:
    runtime_identity = _payload(_read_json(artifact_dir / "runtime_identity_envelope.json"))
    route_contract = _payload(_read_json(artifact_dir / "route_contract.json"))
    manifest = _read_json(artifact_dir / "r4_run_manifest.json")
    run_id = str(result.get("run_id") or manifest.get("run_id") or route_contract.get("route_contract_id") or runtime_identity.get("run_id") or artifact_dir.name)
    request_id = str(result.get("request_id") or manifest.get("request_id") or route_contract.get("request_id") or runtime_identity.get("request_id") or f"req:{run_id}")
    trace_root = str(route_contract.get("trace_root") or runtime_identity.get("trace_root") or f"trace:{run_id}")
    policy_hash = str(route_contract.get("policy_hash") or runtime_identity.get("policy_hash") or "ph:apps-rg-post-x3")
    blueprint_hash = str(route_contract.get("blueprint_hash") or runtime_identity.get("blueprint_hash") or "bh:apps-rg-post-x3")
    replay_key = str(route_contract.get("replay_key") or runtime_identity.get("replay_key") or manifest.get("replay_key") or f"apps-rg-post-x3:{run_id}")
    route_contract_ref = str(route_contract.get("route_contract_id") or route_contract.get("route_id") or "route:apps_rg:resume_generation_v1")
    return {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "tenant_id": "apps_rg",
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "route_contract_ref": route_contract_ref,
    }


def _build_commit_packet(
    *,
    artifact_dir: Path,
    generated_resume: Path,
    output_hash: str,
    ids: Mapping[str, str],
) -> tuple[CommitRequest, list[StateDiff], RollbackPlan, ReadSurfaceRefreshPlan]:
    run_id = ids["run_id"]
    target_surface = "apps_rg_resume_package"
    rollback = stamp_digest(
        RollbackPlan(
            rollback_plan_id=f"rp:apps-rg-post-x3:{run_id}",
            blast_radius="single_surface",
            target_surfaces=(target_surface,),
            before_snapshot_refs=("snap:apps-rg-resume-package:before",),
            rollback_operation_types=("tombstone",),
        )
    )
    refresh = stamp_digest(
        ReadSurfaceRefreshPlan(
            refresh_plan_id=f"rfp:apps-rg-post-x3:{run_id}",
            source_commit_receipt_ref="<pending>",
            before_snapshot="snap:apps-rg-resume-package:before",
            expected_after_snapshot="snap:apps-rg-resume-package:after",
            stale_projection_policy="fail_closed",
            retry_policy="none",
            policy_hash=ids["policy_hash"],
            blueprint_hash=ids["blueprint_hash"],
            affected_surfaces=(target_surface,),
            required_refreshes=("apps_rg_resume_package_projection",),
            refresh_order=("apps_rg_resume_package_projection",),
        )
    )
    state_diff = stamp_digest(
        StateDiff(
            state_diff_id=f"sd:apps-rg-post-x3:{run_id}",
            target_surface=target_surface,
            operation_type="append_record",
            after_candidate=f"{_artifact_ref(artifact_dir, generated_resume)}#sha256:{output_hash}",
            schema_ref="schema:apps_rg.generated_resume@1",
            blast_radius="single_surface",
            rollback_plan_ref=rollback.rollback_plan_id,
            proposed_by_surface="Exit",
            created_at=_utc_now_iso(),
            replay_refs=(ids["replay_key"],),
            audit_refs=(
                "x3_disposition_receipt.json",
                "exit_review_packet.json",
                _repo_rel(generated_resume, artifact_dir),
            ),
        )
    )
    commit_request_id = f"cr:apps-rg-post-x3:{run_id}"
    clearance_proof_id = "exit_review_packet.json"
    state_diff_hash = _state_diffs_digest([state_diff])
    commit_request = stamp_digest(
        CommitRequest(
            commit_request_id=commit_request_id,
            cleared_exit_review_packet_ref=clearance_proof_id,
            request_id=ids["request_id"],
            run_id=run_id,
            trace_root=ids["trace_root"],
            tenant_id=ids["tenant_id"],
            policy_hash=ids["policy_hash"],
            blueprint_hash=ids["blueprint_hash"],
            route_contract_ref=ids["route_contract_ref"],
            replay_key=ids["replay_key"],
            rollback_plan_ref=rollback.rollback_plan_id,
            blast_radius="single_surface",
            state_diff_refs=(state_diff.state_diff_id,),
            gate_verdict_refs=("x3_disposition_receipt.json", "apps_rg_output_manifest.json"),
            l5_certification_ref=f"l5:apps-rg-post-x3:{run_id}",
            affected_state_surfaces=(target_surface,),
            expected_read_surface_refreshes=("apps_rg_resume_package_projection",),
            audit_refs=(
                "runtime_certification_binding.json",
                "x3_disposition_receipt.json",
                "apps_rg_output_manifest.json",
            ),
            registry_digest_set=(
                f"registry:policy:{ids['policy_hash']}",
                f"registry:blueprint:{ids['blueprint_hash']}",
            ),
            capability_token_ref=f"capability:apps_rg:post-x3:{run_id}",
            clearance_proof_id=clearance_proof_id,
            validator_receipt_id=f"validator:apps-rg-post-x3:{run_id}",
            staged_diff_hash=state_diff_hash,
            commit_request_signature=_commit_request_signature(
                commit_request_id=commit_request_id,
                state_diff_hash=state_diff_hash,
                clearance_proof_id=clearance_proof_id,
            ),
        )
    )
    return commit_request, [state_diff], rollback, refresh


def _write_uwg_artifacts(
    *,
    artifact_dir: Path,
    commit_request: CommitRequest,
    state_diff: StateDiff,
    rollback_plan: RollbackPlan,
    refresh_plan: ReadSurfaceRefreshPlan,
    validation: Any,
    commit_receipt: Any,
    refresh_receipts: list[Any],
    generated_resume: Path,
    output_hash: str,
    ids: Mapping[str, str],
) -> dict[str, str]:
    uwg_dir = artifact_dir / UWG_DIR
    commit_request_payload = _json_ready(commit_request)
    state_diff_payload = _json_ready(state_diff)
    rollback_payload = _json_ready(rollback_plan)
    refresh_payload = _json_ready(refresh_plan)
    validation_payload = {
        **_json_ready(validation),
        "commit_status": "VALIDATED",
        "run_id": ids["run_id"],
        "request_id": ids["request_id"],
        "trace_root": ids["trace_root"],
        "integrated_runtime_origin": True,
    }
    receipt_payload = {
        **_json_ready(commit_receipt),
        "commit_status": "COMMITTED",
        "run_id": ids["run_id"],
        "request_id": ids["request_id"],
        "trace_root": ids["trace_root"],
        "output_path": _repo_rel(generated_resume, artifact_dir),
        "output_hash": output_hash,
        "output_hash_sha256": f"sha256:{output_hash}",
        "committed_artifact_ref": _artifact_ref(artifact_dir, generated_resume),
        "integrated_runtime_origin": True,
    }
    refresh_payloads = [_json_ready(item) for item in refresh_receipts]
    refresh_list_payload = {
        "refresh_plan_ref": refresh_plan.refresh_plan_id,
        "source_commit_receipt_ref": commit_receipt.commit_receipt_id,
        "refresh_count": len(refresh_payloads),
        "refresh_receipts": refresh_payloads,
        "run_id": ids["run_id"],
        "request_id": ids["request_id"],
        "trace_root": ids["trace_root"],
        "integrated_runtime_origin": True,
    }
    files = {
        "commit_request": uwg_dir / UWG_COMMIT_REQUEST,
        "state_diff": uwg_dir / "state_diff.json",
        "rollback_plan": uwg_dir / "rollback_plan.json",
        "read_surface_refresh_plan": uwg_dir / "read_surface_refresh_plan.json",
        "uwg_validation_receipt": uwg_dir / UWG_VALIDATION_RECEIPT,
        "uwg_commit_receipt": uwg_dir / UWG_COMMIT_RECEIPT,
        "uwg_refresh_receipts": uwg_dir / UWG_REFRESH_RECEIPTS,
    }
    _write_json(files["commit_request"], commit_request_payload)
    _write_json(files["state_diff"], state_diff_payload)
    _write_json(files["rollback_plan"], rollback_payload)
    _write_json(files["read_surface_refresh_plan"], refresh_payload)
    _write_json(files["uwg_validation_receipt"], validation_payload)
    _write_json(files["uwg_commit_receipt"], receipt_payload)
    _write_json(files["uwg_refresh_receipts"], refresh_list_payload)

    # Root aliases keep legacy renderers and probes honest without forcing them
    # to know the namespaced UWG directory.
    for name, payload in (
        (UWG_COMMIT_REQUEST, commit_request_payload),
        (UWG_VALIDATION_RECEIPT, validation_payload),
        (UWG_COMMIT_RECEIPT, receipt_payload),
        (UWG_REFRESH_RECEIPTS, refresh_list_payload),
    ):
        _write_json(artifact_dir / name, payload)

    return {key: _repo_rel(path, artifact_dir) for key, path in files.items()}


def _update_envelope_payload(path: Path, updates: Mapping[str, Any]) -> str:
    doc = _read_json(path)
    if not doc:
        return ""
    payload = doc.get("payload") if isinstance(doc.get("payload"), dict) else None
    if payload is None:
        return ""
    payload.update(dict(updates))
    doc["artifact_hash"] = compute_artifact_hash(payload)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(doc.get("artifact_hash") or "")


def _update_plain_manifest(path: Path, updates: Mapping[str, Any]) -> None:
    doc = _read_json(path)
    if not doc:
        return
    doc.update(dict(updates))
    seed = {k: v for k, v in doc.items() if k != "artifact_hash"}
    doc["artifact_hash"] = compute_artifact_hash(seed)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _bind_completion_artifacts(
    *,
    artifact_dir: Path,
    receipt_path: Path,
    receipt_hash: str,
    uwg_paths: Mapping[str, str],
    eval_record_path: str,
    eval_record_hash: str,
    l6_bridge_path: str,
    l6_bridge_hash: str,
    commit_receipt_id: str,
    fact_vector_writeback: Mapping[str, Any] | None = None,
    l6_shadow_refs: Mapping[str, Any] | None = None,
) -> None:
    fv = dict(fact_vector_writeback or {})
    l6_refs = dict(l6_shadow_refs or {})
    updates = {
        "apps_rg_post_x3_completion_status": "PASS",
        "apps_rg_post_x3_completion_ref": _repo_rel(receipt_path, artifact_dir),
        "apps_rg_post_x3_completion_sha256": f"sha256:{receipt_hash}",
        "uwg_commit_receipt_ref": uwg_paths.get("uwg_commit_receipt", ""),
        "uwg_commit_receipt_id": commit_receipt_id,
        "uwg_commit_receipt_sha256": f"sha256:{_sha256_file(artifact_dir / uwg_paths['uwg_commit_receipt'])}",
        "commit_request_ref": uwg_paths.get("commit_request", ""),
        "apps_eval_record_ref": eval_record_path,
        "apps_eval_record_sha256": f"sha256:{eval_record_hash}",
        "l6_shadow_bridge_ref": l6_bridge_path,
        "l6_shadow_bridge_sha256": f"sha256:{l6_bridge_hash}" if l6_bridge_hash else "",
        "l6_apps_eval_alignment_ref": str(l6_refs.get("l6_apps_eval_alignment_ref") or ""),
        "l6_apps_eval_grain_parity_ref": str(l6_refs.get("l6_apps_eval_grain_parity_ref") or ""),
        "l6_section_apps_eval_bindings_ref": str(l6_refs.get("l6_section_apps_eval_bindings_ref") or ""),
        "alignment_source": str(l6_refs.get("alignment_source") or ""),
        "apps_eval_rows_bound": bool(l6_refs.get("apps_eval_rows_bound") is True),
        "grain_parity_status": str(l6_refs.get("grain_parity_status") or ""),
        "evidence_class": str(l6_refs.get("evidence_class") or ""),
        "future_run_only": True,
        "current_run_mutated": False,
        "fact_vector_writeback_status": str(fv.get("status") or ""),
        "fact_vector_writeback_reason": str(fv.get("reason") or ""),
    }
    _update_plain_manifest(artifact_dir / "r4_run_manifest.json", updates)
    manifest_hash = _update_envelope_payload(artifact_dir / "integrated_runtime_artifact_manifest.json", updates)
    spine_updates = {
        **updates,
        "uwg_commit_or_block_ref": updates["uwg_commit_receipt_sha256"],
        "apps_rg_e2e_completion_certified": True,
    }
    if manifest_hash:
        spine_updates["artifact_manifest_ref"] = manifest_hash
    _update_envelope_payload(artifact_dir / "agentic_core_spine_proof.json", spine_updates)

    coverage_path = artifact_dir / "agentic_core_l7_route_family_coverage.json"
    coverage_doc = _read_json(coverage_path)
    coverage_payload = coverage_doc.get("payload") if isinstance(coverage_doc.get("payload"), dict) else None
    if isinstance(coverage_payload, dict):
        coverage_payload["apps_rg_post_x3_completion"] = {
            "status": "PASS",
            "uwg_commit_receipt_ref": updates["uwg_commit_receipt_ref"],
            "apps_eval_record_ref": eval_record_path,
            "l6_shadow_bridge_ref": l6_bridge_path,
            "l6_apps_eval_alignment_ref": updates["l6_apps_eval_alignment_ref"],
            "l6_apps_eval_grain_parity_ref": updates["l6_apps_eval_grain_parity_ref"],
            "l6_section_apps_eval_bindings_ref": updates["l6_section_apps_eval_bindings_ref"],
            "alignment_source": updates["alignment_source"],
            "apps_eval_rows_bound": updates["apps_eval_rows_bound"],
            "grain_parity_status": updates["grain_parity_status"],
            "evidence_class": updates["evidence_class"],
            "fact_vector_writeback": fv,
            "note": "route-family certification is separate from app workflow completion",
        }
        coverage_doc["artifact_hash"] = compute_artifact_hash(coverage_payload)
        coverage_path.write_text(
            json.dumps(coverage_doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _run_current_eval(
    *,
    artifact_dir: Path,
    result: Mapping[str, Any],
    raw_request: Mapping[str, Any] | None,
) -> Any:
    from apps_eval.adapters.apps_rg import normalize_existing_apps_rg_run_snapshot
    from apps_eval.runner.core import run_current_snapshot_eval

    preflight = {
        "status": "passed",
        "resolved_inputs": {
            "target_company": str((raw_request or {}).get("target_company") or ""),
            "target_role": str((raw_request or {}).get("target_role") or ""),
            "target_level": str((raw_request or {}).get("target_level") or ""),
            "jd_present": bool((raw_request or {}).get("jd")),
            "generation_mode": str((raw_request or {}).get("generation_mode") or ""),
            "artifact_dir": str(artifact_dir),
        },
    }
    snapshot = normalize_existing_apps_rg_run_snapshot(
        scenario_id="apps_rg_current_run_post_x3",
        result=dict(result),
        artifact_dir=artifact_dir,
        preflight=preflight,
    )
    return run_current_snapshot_eval(
        snapshot,
        suite_id="apps_rg.current.resume_generation",
        out_dir=str(artifact_dir / "apps_eval"),
        deterministic_only=True,
        emit_l6_handoff=True,
    )


def _emit_post_x3_failure_l6_shadow_bridge(
    *,
    artifact_dir: Path,
    failure_stage: str,
    reason: str,
    partial_payload: Mapping[str, Any],
) -> dict[str, Any]:
    bridge_path = artifact_dir / POST_X3_FAILURE_L6_SHADOW_BRIDGE
    parity_path = artifact_dir / POST_X3_FAILURE_L6_APPS_EVAL_GRAIN_PARITY
    bridge = {
        "schema_version": "apps_rg.post_x3_failure_l6_shadow_bridge.v1",
        "failure_stage": failure_stage,
        "reason": reason,
        "partial_payload": dict(partial_payload),
        "alignment_source": "failure_terminal_no_apps_eval_rows",
        "apps_eval_rows_bound": False,
        "evidence_class": EVIDENCE_CLASS_FAILURE_TERMINAL_ADVISORY,
        "grain_parity_status": "WARN",
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only": True,
    }
    parity = build_l6_apps_eval_grain_parity(
        run_id=str(partial_payload.get("run_id") or ""),
        runtime_exhaust_bundle_id="",
        microstep_contract_digest="",
        apps_eval_scorecard_ref="",
        l6_observation_ref=_repo_rel(bridge_path, artifact_dir),
        apps_eval_rows=[],
        l6_observations=[],
        alignment_source="failure_terminal_no_apps_eval_rows",
    )
    parity.update(
        {
            "direct_l4_write_assertion": False,
            "durable_write_assertion": False,
        }
    )
    _write_json(bridge_path, bridge)
    _write_json(parity_path, parity)
    return {
        "l6_shadow_bridge_ref": _repo_rel(bridge_path, artifact_dir),
        "l6_apps_eval_grain_parity_ref": _repo_rel(parity_path, artifact_dir),
        "alignment_source": "failure_terminal_no_apps_eval_rows",
        "apps_eval_rows_bound": False,
        "evidence_class": EVIDENCE_CLASS_FAILURE_TERMINAL_ADVISORY,
        "grain_parity_status": "WARN",
        "future_run_only": True,
        "current_run_mutated": False,
    }


def _emit_post_x3_success_l6_grain_parity(
    *,
    artifact_dir: Path,
    eval_record: Any,
    l6_bridge_path: str,
) -> dict[str, Any]:
    bridge = _read_json(Path(l6_bridge_path)) if l6_bridge_path else {}
    runtime_exhaust_bundle_id = str(bridge.get("runtime_exhaust_bundle_id") or "")
    scorecard_rows = list(getattr(eval_record.scorecard, "scorecard_rows", []) or [])
    scorecard_ref = str(eval_record.artifact_paths.get("scorecard_rows") or "")
    paths = emit_apps_rg_l6_microstep_artifacts(
        output_dir=artifact_dir / "l6_grain_parity",
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        run_id=str(eval_record.record_id),
        runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
        section_id="",
        apps_eval_scorecard_rows=scorecard_rows,
        apps_eval_scorecard_ref=scorecard_ref,
    )
    parity = _read_json(paths["l6_apps_eval_grain_parity"])
    return {
        "l6_apps_eval_alignment_ref": _repo_rel(paths["l6_apps_eval_alignment"], artifact_dir),
        "l6_apps_eval_grain_parity_ref": _repo_rel(paths["l6_apps_eval_grain_parity"], artifact_dir),
        "l6_microstep_observations_ref": _repo_rel(paths["l6_microstep_observations"], artifact_dir),
        "alignment_source": str(parity.get("alignment_source") or ""),
        "apps_eval_rows_bound": bool(parity.get("apps_eval_rows_bound") is True),
        "evidence_class": str(parity.get("evidence_class") or ""),
        "grain_parity_status": str(parity.get("grain_parity_status") or ""),
        "future_run_only": bool(parity.get("future_run_only") is True),
        "current_run_mutated": False,
    }


def _lane_ids_from_contract_or_rows(scorecard_rows: list[Mapping[str, Any]]) -> list[str]:
    contract_path = REPO_ROOT / "apps_eval" / "registries" / "apps_rg_lane_contract.json"
    lane_ids: list[str] = []
    doc = _read_json(contract_path)
    for lane in doc.get("generated_lanes", []) if doc else []:
        text = str(lane or "").strip()
        if text and text not in lane_ids:
            lane_ids.append(text)
    for row in scorecard_rows:
        text = str(row.get("lane_id") or "").strip()
        if text and text not in lane_ids:
            lane_ids.append(text)
    return lane_ids


def _resolve_section_pointer_ref(ref: str, artifact_dir: Path) -> Path:
    path = Path(ref)
    if path.is_absolute():
        return path
    repo_candidate = (REPO_ROOT / path).resolve()
    if repo_candidate.exists():
        return repo_candidate
    return (artifact_dir / path).resolve()


def _section_pointer_payload(artifact_dir: Path, lane_id: str) -> dict[str, Any]:
    lane_dir = artifact_dir / "modular_r4" / "sections" / lane_id
    for name in ("latest_successful_real_run.json", "latest_real_run.json"):
        payload = _read_json(lane_dir / name)
        if payload:
            return payload
    return {}


def _section_package_candidates(artifact_dir: Path, lane_id: str) -> list[Path]:
    candidates = [
        artifact_dir / "lanes" / lane_id / "l6_v40_shadow_eval_package.json",
        artifact_dir / "modular_r4" / "sections" / lane_id / "l6_v40_shadow_eval_package.json",
        artifact_dir / lane_id / "l6_v40_shadow_eval_package.json",
    ]
    pointer = _section_pointer_payload(artifact_dir, lane_id)
    links: dict[str, Any] = {}
    for key in ("artifact_links", "artifact_links_compact"):
        raw_links = pointer.get(key)
        if isinstance(raw_links, dict):
            links.update(raw_links)
    linked_ref = str(links.get("l6_v40_shadow_eval_package.json") or "").strip()
    if linked_ref:
        candidates.insert(0, _resolve_section_pointer_ref(linked_ref, artifact_dir))
    run_dir_ref = str(pointer.get("run_dir_repo_relative") or pointer.get("run_dir") or "").strip()
    if run_dir_ref:
        candidates.insert(0, _resolve_section_pointer_ref(run_dir_ref, artifact_dir) / "l6_v40_shadow_eval_package.json")
    return candidates


def _section_legacy_package_candidates(artifact_dir: Path, lane_id: str) -> list[Path]:
    candidates = [
        artifact_dir / "lanes" / lane_id / "l6_shadow_eval_package.json",
        artifact_dir / "modular_r4" / "sections" / lane_id / "l6_shadow_eval_package.json",
        artifact_dir / lane_id / "l6_shadow_eval_package.json",
    ]
    pointer = _section_pointer_payload(artifact_dir, lane_id)
    links: dict[str, Any] = {}
    for key in ("artifact_links", "artifact_links_compact"):
        raw_links = pointer.get(key)
        if isinstance(raw_links, dict):
            links.update(raw_links)
    linked_ref = str(links.get("l6_shadow_eval_package.json") or "").strip()
    if linked_ref:
        candidates.insert(0, _resolve_section_pointer_ref(linked_ref, artifact_dir))
    run_dir_ref = str(pointer.get("run_dir_repo_relative") or pointer.get("run_dir") or "").strip()
    if run_dir_ref:
        candidates.insert(0, _resolve_section_pointer_ref(run_dir_ref, artifact_dir) / "l6_shadow_eval_package.json")
    return candidates


def _first_existing_path(candidates: list[Path]) -> Path | None:
    return next((path for path in candidates if path.is_file()), None)


def _row_grain_key(row: Mapping[str, Any]) -> dict[str, str]:
    return {field: str(row.get(field) or "") for field in L6_APPS_EVAL_COVERAGE_JOIN_KEY}


def _emit_l6_section_apps_eval_bindings(
    *,
    artifact_dir: Path,
    eval_record: Any,
) -> dict[str, Any]:
    scorecard_rows = [
        dict(row)
        for row in list(getattr(eval_record.scorecard, "scorecard_rows", []) or [])
        if isinstance(row, Mapping) and row.get("required", True)
    ]
    bindings: list[dict[str, Any]] = []
    for lane_id in _lane_ids_from_contract_or_rows(scorecard_rows):
        lane_rows = [row for row in scorecard_rows if str(row.get("lane_id") or "") == lane_id]
        v40_package_path = _first_existing_path(_section_package_candidates(artifact_dir, lane_id))
        legacy_package_path = _first_existing_path(_section_legacy_package_candidates(artifact_dir, lane_id))
        package_path = v40_package_path or legacy_package_path
        package_tier = "v40" if v40_package_path is not None else "legacy" if legacy_package_path is not None else ""
        package = _read_json(package_path) if package_path is not None else {}
        proof_gaps: list[str] = []
        if package_path is None:
            proof_gaps.append("missing_l6_shadow_eval_package")
        if not lane_rows:
            proof_gaps.append("missing_apps_eval_scorecard_rows")
        evidence_class = (
            EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF
            if package_path is not None and lane_rows
            else EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY
        )
        bindings.append(
            {
                "section_id": lane_id,
                "artifact_dir_ref": _artifact_or_repo_rel(package_path.parent, artifact_dir) if package_path is not None else "",
                "l6_package_tier": package_tier,
                "l6_v40_shadow_eval_package_ref": _artifact_or_repo_rel(v40_package_path, artifact_dir) if v40_package_path is not None else "",
                "l6_v40_shadow_eval_package_sha256": f"sha256:{_sha256_file(v40_package_path)}" if v40_package_path is not None else "",
                "l6_shadow_eval_package_ref": _artifact_or_repo_rel(package_path, artifact_dir) if package_path is not None else "",
                "l6_shadow_eval_package_sha256": f"sha256:{_sha256_file(package_path)}" if package_path is not None else "",
                "apps_eval_row_count": len(lane_rows),
                "apps_eval_row_ids": [str(row.get("row_id") or "") for row in lane_rows],
                "apps_eval_grain_keys": [_row_grain_key(row) for row in lane_rows],
                "binding_status": "PASS" if evidence_class == EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF else "WARN",
                "evidence_class": evidence_class,
                "proof_gaps": proof_gaps,
                "package_grain_parity_status": str(package.get("grain_parity_status") or ""),
                "package_alignment_source": str(package.get("alignment_source") or ""),
                "package_immutable": True,
                "future_run_only": True,
                "current_run_mutation_assertion": False,
                "direct_l4_write_assertion": False,
                "durable_write_assertion": False,
            }
        )

    summary = {
        "sections_total": len(bindings),
        "sections_bound": sum(1 for item in bindings if item["binding_status"] == "PASS"),
        "sections_contract_only": sum(1 for item in bindings if item["evidence_class"] != EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF),
        "apps_eval_rows_bound": sum(int(item["apps_eval_row_count"]) for item in bindings),
        "grain_parity_status_by_section": {
            str(item["section_id"]): str(item["package_grain_parity_status"] or item["binding_status"])
            for item in bindings
        },
    }
    payload = {
        "schema_version": "apps_rg.l6_section_apps_eval_bindings.v1",
        "eval_record_id": str(getattr(eval_record, "record_id", "") or ""),
        "eval_record_ref": str(getattr(eval_record, "artifact_paths", {}).get("eval_record") or ""),
        "summary": summary,
        "bindings": bindings,
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only": True,
    }
    path = artifact_dir / L6_SECTION_APPS_EVAL_BINDINGS
    _write_json(path, payload)
    return {
        "l6_section_apps_eval_bindings_ref": _repo_rel(path, artifact_dir),
        "l6_section_apps_eval_bindings_summary": summary,
    }


def _complete_fact_vector_writeback_after_x3(
    *,
    artifact_dir: Path,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    """Promote deferred grounded fact vectors for the full run after X3 success."""
    from apps_rg.runtime.c0.c02_fact_vector_ingest import INGEST_RECEIPT_NAME
    from apps_rg.runtime.c0.fact_vector_write_back import (
        PROMOTION_MODE_DEFERRED,
        promote_staged_fact_vectors,
        promotion_mode,
    )

    receipts: list[dict[str, Any]] = []
    candidate_run_ids: list[str] = []
    for path in artifact_dir.rglob(INGEST_RECEIPT_NAME):
        doc = _read_json(path)
        if not doc:
            continue
        rel = _repo_rel(path, artifact_dir)
        staged_count = int(doc.get("staged_count") or 0)
        promoted_count = int((doc.get("promotion") or {}).get("promoted_count") or 0)
        receipts.append(
            {
                "path": rel,
                "status": str(doc.get("status") or ""),
                "reason": str(doc.get("reason") or ""),
                "run_id": str(doc.get("run_id") or ""),
                "section_id": str(doc.get("section_id") or ""),
                "staged_count": staged_count,
                "promoted_count": promoted_count,
                "promotion_mode": str(doc.get("promotion_mode") or ""),
            }
        )
        if staged_count > 0 and str(doc.get("status") or "") == "STAGED_DEFERRED":
            rid = str(doc.get("run_id") or "").strip()
            if rid and rid not in candidate_run_ids:
                candidate_run_ids.append(rid)

    mode = promotion_mode()
    payload: dict[str, Any] = {
        "schema_version": "apps_rg.fact_vector_writeback_post_x3_completion.v1",
        "status": "EMPTY",
        "reason": "no_deferred_grounded_fact_vectors",
        "promotion_mode": mode,
        "candidate_run_ids": candidate_run_ids,
        "ingest_receipts": receipts,
        "promotions": [],
    }
    if not candidate_run_ids:
        return payload
    if mode != PROMOTION_MODE_DEFERRED:
        payload["status"] = "SKIPPED"
        payload["reason"] = "promotion_mode_not_deferred"
        return payload

    chroma_path = str(os.environ.get("CHROMA_PERSIST_DIR", "")).strip()
    payload["chroma_path"] = chroma_path or None
    if not chroma_path:
        payload["status"] = "FAIL"
        payload["reason"] = "CHROMA_PERSIST_DIR unset"
        return payload

    source_x3 = str(result.get("x3_disposition") or "").strip()
    for rid in candidate_run_ids:
        safe_rid = rid.replace(":", "_").replace("\\", "_").replace("/", "_")
        promotion_dir = artifact_dir / "fact_vectors_post_x3" / safe_rid
        promotion = promote_staged_fact_vectors(
            chroma_path=chroma_path,
            artifact_dir=promotion_dir,
            run_id=rid,
            x3_code=source_x3,
            require_x3_allow=True,
            promotion_run_id=f"post_x3:{rid}",
        )
        payload["promotions"].append(
            {
                "run_id": rid,
                "artifact_dir": _repo_rel(promotion_dir, artifact_dir),
                "status": str(promotion.get("status") or ""),
                "reason": str(promotion.get("reason") or ""),
                "promoted_count": int(promotion.get("promoted_count") or 0),
                "uwg_status": str((promotion.get("uwg") or {}).get("status") or ""),
                "live_projection_status": str(
                    (promotion.get("live_projection") or {}).get("status") or ""
                ),
                "retrieval_proof_status": str(
                    (promotion.get("retrieval_proof") or {}).get("status") or ""
                ),
                "receipt_ref": _repo_rel(
                    promotion_dir / "fact_vector_promotion_receipt.json",
                    artifact_dir,
                ),
            }
        )

    failures = [
        p for p in payload["promotions"]
        if p["status"] != "PASS"
        or p["uwg_status"] != "ADMITTED"
        or p["retrieval_proof_status"] != "PASS"
    ]
    payload["status"] = "FAIL" if failures else "PASS"
    payload["reason"] = (
        "fact_vector_writeback_chain_failed"
        if failures
        else "fact_vector_writeback_chain_complete"
    )
    return payload


def complete_apps_rg_post_x3(
    *,
    artifact_dir: Path | str,
    result: Mapping[str, Any],
    raw_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run mandatory full-resume post-X3 UWG, apps_eval, and L6 completion."""
    art = Path(artifact_dir)
    receipt_path = art / POST_X3_COMPLETION_RECEIPT
    generated = _generated_resume_path(art)
    manifest = _load_output_manifest(art)
    eligible, reasons = evaluate_apps_rg_full_success_eligibility(
        manifest=manifest,
        run_root=art,
    ) if manifest else (False, ["apps_rg_output_manifest_missing"])

    if generated is None or not eligible:
        payload = {
            "schema_version": "apps_rg.post_x3_completion.v1",
            "generated_at_utc": _utc_now_iso(),
            "status": "FAIL",
            "completed": False,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "failure_stage": "pre_uwg_product_eligibility",
            "generated_resume_path": _repo_rel(generated, art) if generated else "",
            "eligibility_reasons": reasons,
        }
        payload["l6_shadow"] = _emit_post_x3_failure_l6_shadow_bridge(
            artifact_dir=art,
            failure_stage="pre_uwg_product_eligibility",
            reason=";".join(str(reason) for reason in reasons),
            partial_payload=payload,
        )
        _write_json(receipt_path, payload)
        return payload

    output_hash = _sha256_file(generated)
    ids = _identity(art, result)
    commit_request, state_diffs, rollback_plan, refresh_plan = _build_commit_packet(
        artifact_dir=art,
        generated_resume=generated,
        output_hash=output_hash,
        ids=ids,
    )
    gw = get_default_gateway()
    commit_receipt, blocked_receipt, refresh_receipts = gw.commit(
        commit_request=commit_request,
        state_diffs=state_diffs,
        rollback_plan=rollback_plan,
        refresh_plan=refresh_plan,
    )
    if commit_receipt is None or blocked_receipt is not None:
        blocked_payload = _json_ready(blocked_receipt) if blocked_receipt is not None else {}
        payload = {
            "schema_version": "apps_rg.post_x3_completion.v1",
            "generated_at_utc": _utc_now_iso(),
            "status": "FAIL",
            "completed": False,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "failure_stage": "uwg_commit",
            "blocked_receipt": blocked_payload,
        }
        payload["l6_shadow"] = _emit_post_x3_failure_l6_shadow_bridge(
            artifact_dir=art,
            failure_stage="uwg_commit",
            reason="uwg_commit_blocked",
            partial_payload=payload,
        )
        _write_json(receipt_path, payload)
        return payload

    validation = gw.get_validation_receipt(commit_receipt.uwg_validation_receipt_ref)
    if validation is None:
        payload = {
            "schema_version": "apps_rg.post_x3_completion.v1",
            "generated_at_utc": _utc_now_iso(),
            "status": "FAIL",
            "completed": False,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "failure_stage": "uwg_validation_receipt_lookup",
            "uwg_validation_receipt_ref": commit_receipt.uwg_validation_receipt_ref,
        }
        payload["l6_shadow"] = _emit_post_x3_failure_l6_shadow_bridge(
            artifact_dir=art,
            failure_stage="uwg_validation_receipt_lookup",
            reason="uwg_validation_receipt_missing",
            partial_payload=payload,
        )
        _write_json(receipt_path, payload)
        return payload

    uwg_paths = _write_uwg_artifacts(
        artifact_dir=art,
        commit_request=commit_request,
        state_diff=state_diffs[0],
        rollback_plan=rollback_plan,
        refresh_plan=refresh_plan,
        validation=validation,
        commit_receipt=commit_receipt,
        refresh_receipts=list(refresh_receipts),
        generated_resume=generated,
        output_hash=output_hash,
        ids=ids,
    )
    fact_vector_writeback = _complete_fact_vector_writeback_after_x3(
        artifact_dir=art,
        result=result,
    )
    _write_json(art / "fact_vector_writeback_completion_receipt.json", fact_vector_writeback)
    if fact_vector_writeback.get("status") == "FAIL":
        payload = {
            "schema_version": "apps_rg.post_x3_completion.v1",
            "generated_at_utc": _utc_now_iso(),
            "status": "FAIL",
            "completed": False,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "failure_stage": "fact_vector_writeback",
            "fact_vector_writeback": fact_vector_writeback,
        }
        payload["l6_shadow"] = _emit_post_x3_failure_l6_shadow_bridge(
            artifact_dir=art,
            failure_stage="fact_vector_writeback",
            reason=str(fact_vector_writeback.get("reason") or "fact_vector_writeback_failed"),
            partial_payload=payload,
        )
        _write_json(receipt_path, payload)
        return payload
    eval_record = _run_current_eval(
        artifact_dir=art,
        result=result,
        raw_request=raw_request,
    )
    eval_record_path = str(eval_record.artifact_paths.get("eval_record") or "")
    l6_bridge_path = str(eval_record.artifact_paths.get("l6_shadow_bridge") or "")
    eval_record_hash = _sha256_file(Path(eval_record_path)) if eval_record_path else ""
    l6_bridge_hash = _sha256_file(Path(l6_bridge_path)) if l6_bridge_path and Path(l6_bridge_path).is_file() else ""
    l6_grain_refs = _emit_post_x3_success_l6_grain_parity(
        artifact_dir=art,
        eval_record=eval_record,
        l6_bridge_path=l6_bridge_path,
    )
    l6_section_bindings = _emit_l6_section_apps_eval_bindings(
        artifact_dir=art,
        eval_record=eval_record,
    )
    l6_shadow_refs = {**l6_grain_refs, **l6_section_bindings}
    coverage = dict(eval_record.scorecard.coverage_summary or {})
    eval_pass = coverage.get("release_blocked") is False and coverage.get("coverage_complete") is True
    payload = {
        "schema_version": "apps_rg.post_x3_completion.v1",
        "generated_at_utc": _utc_now_iso(),
        "status": "PASS" if eval_pass else "FAIL",
        "completed": bool(eval_pass),
        "x3_to_uwg_to_eval_to_l6_completed": bool(eval_pass and l6_bridge_hash),
        "failure_stage": "" if eval_pass else "apps_eval",
        "generated_resume_path": _repo_rel(generated, art),
        "output_hash": output_hash,
        "output_hash_sha256": f"sha256:{output_hash}",
        "uwg": {
            "commit_request_id": commit_request.commit_request_id,
            "uwg_validation_receipt_id": validation.uwg_validation_receipt_id,
            "uwg_commit_receipt_id": commit_receipt.commit_receipt_id,
            "uwg_validation_status": validation.validation_status,
            "commit_status": "COMMITTED",
            "artifacts": dict(uwg_paths),
        },
        "fact_vector_writeback": fact_vector_writeback,
        "apps_eval": {
            "record_id": eval_record.record_id,
            "eval_record_ref": eval_record_path,
            "eval_record_sha256": f"sha256:{eval_record_hash}" if eval_record_hash else "",
            "score": eval_record.scorecard.score,
            "verdict": eval_record.scorecard.verdict,
            "coverage_summary": coverage,
            "scorecard_rows_ref": eval_record.artifact_paths.get("scorecard_rows", ""),
            "coverage_matrix_ref": eval_record.artifact_paths.get("coverage_matrix", ""),
        },
        "l6_shadow": {
            "l6_shadow_bridge_ref": l6_bridge_path,
            "l6_shadow_bridge_sha256": f"sha256:{l6_bridge_hash}" if l6_bridge_hash else "",
            **l6_shadow_refs,
            "future_run_only": True,
            "current_run_mutated": False,
        },
    }
    _write_json(receipt_path, payload)
    receipt_hash = _sha256_file(receipt_path)
    if eval_pass and l6_bridge_hash:
        _bind_completion_artifacts(
            artifact_dir=art,
            receipt_path=receipt_path,
            receipt_hash=receipt_hash,
            uwg_paths=uwg_paths,
            eval_record_path=eval_record_path,
            eval_record_hash=eval_record_hash,
            l6_bridge_path=l6_bridge_path,
            l6_bridge_hash=l6_bridge_hash,
            commit_receipt_id=commit_receipt.commit_receipt_id,
            fact_vector_writeback=fact_vector_writeback,
            l6_shadow_refs=l6_shadow_refs,
        )
    return payload


__all__ = [
    "POST_X3_FAILURE_L6_APPS_EVAL_GRAIN_PARITY",
    "POST_X3_FAILURE_L6_SHADOW_BRIDGE",
    "POST_X3_COMPLETION_RECEIPT",
    "L6_SECTION_APPS_EVAL_BINDINGS",
    "complete_apps_rg_post_x3",
    "is_full_resume_product_artifact_dir",
]
