"""Post-X3 completion for full apps_rg resume runs.

Current-run authority is Exit -> UWG.  apps_eval and L6 execute only after UWG
has closed the current-run durable-admission decision.  Their outputs are
post-boundary observations and future-run evidence; they cannot rescue, veto,
or authorize the current run.
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
from agentic_core.L6_observability.shadow_eval.independent_parity import (
    SEALED_APPS_RG_OBSERVATION_ORIGIN,
    build_independent_apps_eval_parity,
    read_jsonl,
    write_independent_parity,
)
from agentic_core.runtime.artifacts.integrated_runtime_emitter import compute_artifact_hash
from apps_rg.runtime.package.apps_rg_full_resume_x3_eligibility import (
    evaluate_apps_rg_full_success_eligibility,
)

POST_X3_COMPLETION_RECEIPT = "apps_rg_post_x3_completion_receipt.json"
POST_X3_AUTHORITY_ORDER_RECEIPT = "apps_rg_post_x3_authority_order_receipt.json"
POST_X3_FAILURE_L6_SHADOW_BRIDGE = "post_x3_failure_l6_shadow_bridge.json"
POST_X3_FAILURE_L6_APPS_EVAL_GRAIN_PARITY = "post_x3_failure_l6_apps_eval_grain_parity.json"
L6_SECTION_APPS_EVAL_BINDINGS = "l6_section_apps_eval_bindings.json"
L6_APPS_EVAL_BINDING_CLOSURE = "l6_apps_eval_binding_closure_receipt.json"
UWG_DIR = "uwg"
UWG_COMMIT_REQUEST = "commit_request.json"
UWG_VALIDATION_RECEIPT = "uwg_validation_receipt.json"
UWG_COMMIT_RECEIPT = "uwg_commit_receipt.json"
UWG_REFRESH_RECEIPTS = "uwg_refresh_receipts.json"
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
    return dict(data) if isinstance(data, Mapping) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _payload(doc: Mapping[str, Any]) -> dict[str, Any]:
    inner = doc.get("payload")
    return dict(inner) if isinstance(inner, Mapping) else dict(doc)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _artifact_or_repo_rel(path: Path, artifact_dir: Path) -> str:
    try:
        return path.resolve().relative_to(artifact_dir.resolve()).as_posix()
    except ValueError:
        pass
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


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
    return next((path for path in candidates if path.is_file()), None)


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


def _identity(
    artifact_dir: Path,
    result: Mapping[str, Any],
    *,
    raw_request: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    identity_candidate = (
        (raw_request or {}).get("canonical_run_identity")
        or result.get("canonical_run_identity")
        or {}
    )
    identity = (
        dict(identity_candidate)
        if isinstance(identity_candidate, Mapping)
        else {}
    )
    required = {
        "producer_app_id",
        "consumer_app_id",
        "parent_run_id",
        "child_run_id",
        "request_id",
        "trace_root",
        "tenant_id",
        "target_company",
        "target_role",
        "jd_sha256",
        "brief_sha256",
        "policy_hash",
        "blueprint_hash",
        "schema_version",
    }
    missing = sorted(
        field for field in required if not str(identity.get(field) or "").strip()
    )
    if missing:
        raise ValueError(
            "canonical run identity is required before UWG: " + ", ".join(missing)
        )
    if identity.get("schema_version") != "apps_research_rg_run_identity.v1":
        raise ValueError("canonical run identity schema_version is invalid")
    for field in ("jd_sha256", "brief_sha256", "policy_hash", "blueprint_hash"):
        digest = str(identity.get(field) or "")
        if (
            len(digest) != 71
            or not digest.startswith("sha256:")
            or any(char not in "0123456789abcdef" for char in digest[7:])
        ):
            raise ValueError(f"canonical run identity {field} is not sha256-bound")
    route_contract_path = artifact_dir / "route_contract.json"
    if not route_contract_path.is_file():
        raise FileNotFoundError("route_contract.json is required before UWG")
    route_contract_sha256 = _sha256_file(route_contract_path)
    identity_sha256 = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "run_id": str(identity["parent_run_id"]),
        "request_id": str(identity["request_id"]),
        "trace_root": str(identity["trace_root"]),
        "tenant_id": str(identity["tenant_id"]),
        "policy_hash": str(identity["policy_hash"]),
        "blueprint_hash": str(identity["blueprint_hash"]),
        "replay_key": f"identity:sha256:{identity_sha256}",
        "route_contract_ref": (
            f"route_contract.json#sha256:{route_contract_sha256}"
        ),
    }


def _digest_bound_ref(artifact_dir: Path, ref: str) -> str:
    path = artifact_dir / ref
    if not path.is_file():
        raise FileNotFoundError(f"required UWG authority artifact is missing: {ref}")
    return f"{ref}#sha256:{_sha256_file(path)}"


def _build_commit_packet(
    *,
    artifact_dir: Path,
    generated_resume: Path,
    output_hash: str,
    ids: Mapping[str, str],
) -> tuple[CommitRequest, list[StateDiff], RollbackPlan, ReadSurfaceRefreshPlan]:
    run_id = ids["run_id"]
    target_surface = "apps_rg_resume_package"
    clearance_proof_id = _digest_bound_ref(
        artifact_dir,
        "exit_review_packet.json",
    )
    x3_receipt_ref = _digest_bound_ref(
        artifact_dir,
        "x3_disposition_receipt.json",
    )
    output_manifest_ref = _digest_bound_ref(
        artifact_dir,
        "apps_rg_output_manifest.json",
    )
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
                x3_receipt_ref,
                clearance_proof_id,
                _repo_rel(generated_resume, artifact_dir),
            ),
        )
    )
    commit_request_id = f"cr:apps-rg-post-x3:{run_id}"
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
            gate_verdict_refs=(x3_receipt_ref, output_manifest_ref),
            l5_certification_ref=f"l5:apps-rg-post-x3:{run_id}",
            affected_state_surfaces=(target_surface,),
            expected_read_surface_refreshes=("apps_rg_resume_package_projection",),
            audit_refs=(
                "runtime_certification_binding.json",
                x3_receipt_ref,
                output_manifest_ref,
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
    for key, payload in (
        ("commit_request", commit_request_payload),
        ("state_diff", state_diff_payload),
        ("rollback_plan", rollback_payload),
        ("read_surface_refresh_plan", refresh_payload),
        ("uwg_validation_receipt", validation_payload),
        ("uwg_commit_receipt", receipt_payload),
        ("uwg_refresh_receipts", refresh_list_payload),
    ):
        _write_json(files[key], payload)
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
    payload = doc.get("payload") if isinstance(doc.get("payload"), Mapping) else None
    if not isinstance(payload, dict):
        return ""
    payload.update(dict(updates))
    doc["artifact_hash"] = compute_artifact_hash(payload)
    _write_json(path, doc)
    return str(doc.get("artifact_hash") or "")


def _update_plain_manifest(path: Path, updates: Mapping[str, Any]) -> None:
    doc = _read_json(path)
    if not doc:
        return
    doc.update(dict(updates))
    doc["artifact_hash"] = compute_artifact_hash(
        {key: value for key, value in doc.items() if key != "artifact_hash"}
    )
    _write_json(path, doc)


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
    l6_refs = dict(l6_shadow_refs or {})
    fv = dict(fact_vector_writeback or {})
    updates = {
        "apps_rg_post_x3_completion_status": "PASS",
        "apps_rg_post_x3_completion_ref": _repo_rel(receipt_path, artifact_dir),
        "apps_rg_post_x3_completion_sha256": f"sha256:{receipt_hash}",
        "uwg_commit_receipt_ref": uwg_paths.get("uwg_commit_receipt", ""),
        "uwg_commit_receipt_id": commit_receipt_id,
        "apps_eval_record_ref": eval_record_path,
        "apps_eval_record_sha256": f"sha256:{eval_record_hash}" if eval_record_hash else "",
        "l6_shadow_bridge_ref": l6_bridge_path,
        "l6_shadow_bridge_sha256": f"sha256:{l6_bridge_hash}" if l6_bridge_hash else "",
        "l6_section_apps_eval_bindings_ref": str(
            l6_refs.get("l6_section_apps_eval_bindings_ref") or ""
        ),
        "l6_apps_eval_binding_closure_ref": str(
            l6_refs.get("l6_apps_eval_binding_closure_ref") or ""
        ),
        "alignment_source": str(l6_refs.get("alignment_source") or ""),
        "apps_eval_rows_bound": bool(l6_refs.get("apps_eval_rows_bound") is True),
        "grain_parity_status": str(l6_refs.get("grain_parity_status") or ""),
        "fact_vector_writeback_status": str(fv.get("status") or ""),
        "future_run_only": True,
        "current_run_mutated": False,
    }
    _update_plain_manifest(artifact_dir / "r4_run_manifest.json", updates)
    _update_envelope_payload(artifact_dir / "integrated_runtime_artifact_manifest.json", updates)
    _update_envelope_payload(artifact_dir / "agentic_core_spine_proof.json", updates)


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
        "schema_version": "apps_rg.post_x3_failure_l6_shadow_bridge.v2",
        "failure_stage": failure_stage,
        "reason": reason,
        "partial_payload": dict(partial_payload),
        "alignment_source": "failure_terminal_no_apps_eval_rows",
        "apps_eval_rows_bound": False,
        "evidence_class": "FAILURE_TERMINAL_ADVISORY",
        "grain_parity_status": "WARN",
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only": True,
    }
    parity = {
        "schema_version": "agentic_core.l6_independent_apps_eval_parity.v1",
        "run_id": str(partial_payload.get("run_id") or ""),
        "alignment_source": "failure_terminal_no_apps_eval_rows",
        "apps_eval_rows_bound": False,
        "evidence_class": "FAILURE_TERMINAL_ADVISORY",
        "grain_parity_status": "WARN",
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only": True,
    }
    _write_json(bridge_path, bridge)
    _write_json(parity_path, parity)
    return {
        "l6_shadow_bridge_ref": _repo_rel(bridge_path, artifact_dir),
        "l6_apps_eval_grain_parity_ref": _repo_rel(parity_path, artifact_dir),
        "alignment_source": "failure_terminal_no_apps_eval_rows",
        "apps_eval_rows_bound": False,
        "evidence_class": "FAILURE_TERMINAL_ADVISORY",
        "grain_parity_status": "WARN",
        "future_run_only": True,
        "current_run_mutated": False,
    }


def _lane_ids_from_rows(rows: list[Mapping[str, Any]]) -> list[str]:
    lane_ids: list[str] = []
    for row in rows:
        lane = str(row.get("lane_id") or "").strip()
        if lane and lane not in lane_ids:
            lane_ids.append(lane)
    return lane_ids


def _section_package_candidates(artifact_dir: Path, lane_id: str, *, legacy: bool) -> list[Path]:
    name = "l6_shadow_eval_package.json" if legacy else "l6_v40_shadow_eval_package.json"
    candidates = [
        artifact_dir / "lanes" / lane_id / name,
        artifact_dir / "modular_r4" / "sections" / lane_id / name,
        artifact_dir / lane_id / name,
    ]
    # Mutable ``latest_*`` pointers are discovery conveniences, never
    # certification evidence.  Binding considers only current-run local
    # candidates under the sealed artifact root.
    return candidates


def _first_existing(candidates: list[Path]) -> Path | None:
    return next((path for path in candidates if path.is_file()), None)


def _resolve_package_artifact_ref(
    ref: str,
    *,
    package_dir: Path,
    artifact_dir: Path,
    fallback_name: str,
) -> Path:
    text = str(ref or "").strip()
    candidates: list[Path] = []
    root = artifact_dir.resolve()
    if text:
        raw = Path(text)
        if raw.is_absolute():
            candidates.append(raw.resolve())
        else:
            candidates.extend(
                [(REPO_ROOT / raw).resolve(), (artifact_dir / raw).resolve(), (package_dir / raw).resolve()]
            )
    candidates.append(package_dir / fallback_name)
    contained = [
        path.resolve()
        for path in candidates
        if path.resolve() == root or root in path.resolve().parents
    ]
    return next((path for path in contained if path.is_file()), (package_dir / fallback_name).resolve())


def _revalidate_observability_closure(
    *,
    closure: Mapping[str, Any],
    package: Mapping[str, Any],
    artifact_dir: Path,
) -> list[str]:
    """Reopen every closure artifact and recompute the closure root."""

    gaps: list[str] = []
    refs = closure.get("refs")
    digests = closure.get("artifact_digests")
    if not isinstance(refs, Mapping) or not isinstance(digests, Mapping):
        return ["observability_closure_artifact_map_missing"]
    recomputed: dict[str, str] = {}
    root = artifact_dir.resolve()
    for name, ref in sorted(refs.items()):
        raw = Path(str(ref or ""))
        candidates = [raw] if raw.is_absolute() else [REPO_ROOT / raw, artifact_dir / raw]
        path = next(
            (
                candidate.resolve()
                for candidate in candidates
                if candidate.is_file()
                and (candidate.resolve() == root or root in candidate.resolve().parents)
            ),
            None,
        )
        if path is None:
            gaps.append(f"closure_artifact_missing_or_uncontained:{name}")
            continue
        actual = f"sha256:{_sha256_file(path)}"
        recomputed[str(name)] = actual
        if str(digests.get(name) or "").lower() != actual.lower():
            gaps.append(f"closure_artifact_digest_mismatch:{name}")

    if {str(key) for key in digests} != set(recomputed):
        gaps.append("closure_artifact_set_mismatch")
    identity_fields = (
        "runtime_exhaust_bundle_id",
        "runtime_exhaust_bundle_digest",
        "parent_run_id",
        "child_run_id",
        "section_attempt_id",
        "microstep_contract_digest",
        "registry_digest",
    )
    for field in identity_fields:
        if not str(closure.get(field) or "") or str(closure.get(field) or "") != str(
            package.get(field) or ""
        ):
            gaps.append(f"closure_identity_mismatch:{field}")
    seed = {
        "runtime_exhaust_bundle_id": str(closure.get("runtime_exhaust_bundle_id") or ""),
        "runtime_exhaust_bundle_digest": str(
            closure.get("runtime_exhaust_bundle_digest") or ""
        ),
        "parent_run_id": str(closure.get("parent_run_id") or ""),
        "child_run_id": str(closure.get("child_run_id") or ""),
        "section_attempt_id": str(closure.get("section_attempt_id") or ""),
        "microstep_contract_digest": str(closure.get("microstep_contract_digest") or ""),
        "registry_digest": str(closure.get("registry_digest") or ""),
        "checks": dict(closure.get("checks") or {}),
        "artifact_digests": recomputed,
    }
    expected = "sha256:" + hashlib.sha256(
        json.dumps(seed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if str(closure.get("closure_digest") or "").lower() != expected.lower():
        gaps.append("observability_closure_digest_mismatch")
    return sorted(set(gaps))


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
    scorecard_ref = str(getattr(eval_record, "artifact_paths", {}).get("scorecard_rows") or "")
    bindings: list[dict[str, Any]] = []
    binding_dir = artifact_dir / "l6_apps_eval_bindings"

    for lane_id in _lane_ids_from_rows(scorecard_rows):
        lane_rows = [row for row in scorecard_rows if str(row.get("lane_id") or "") == lane_id]
        v40_path = _first_existing(_section_package_candidates(artifact_dir, lane_id, legacy=False))
        legacy_path = _first_existing(_section_package_candidates(artifact_dir, lane_id, legacy=True))
        if v40_path is None:
            status = "LEGACY_PACKAGE_ADVISORY" if legacy_path is not None else "MISSING_PACKAGE"
            bindings.append(
                {
                    "section_id": lane_id,
                    "binding_status": status,
                    "evidence_class": "CONTRACT_ONLY_ADVISORY",
                    "apps_eval_row_count": len(lane_rows),
                    "l6_package_tier": "legacy" if legacy_path is not None else "",
                    "l6_shadow_eval_package_ref": (
                        _artifact_or_repo_rel(legacy_path, artifact_dir) if legacy_path else ""
                    ),
                    "proof_gaps": [
                        "governed_v40_package_required_for_independent_binding"
                    ],
                    "package_immutable": True,
                    "future_run_only": True,
                    "current_run_mutation_assertion": False,
                    "direct_l4_write_assertion": False,
                    "durable_write_assertion": False,
                }
            )
            continue

        package = _read_json(v40_path)
        observation_path = _resolve_package_artifact_ref(
            str(package.get("l6_microstep_observations_ref") or ""),
            package_dir=v40_path.parent,
            artifact_dir=artifact_dir,
            fallback_name="l6_microstep_observations.jsonl",
        )
        closure_path = _resolve_package_artifact_ref(
            str(package.get("l6_observability_closure_receipt_ref") or ""),
            package_dir=v40_path.parent,
            artifact_dir=artifact_dir,
            fallback_name="l6_observability_closure_receipt.json",
        )
        closure = _read_json(closure_path)
        proof_gaps: list[str] = []
        if not observation_path.is_file():
            proof_gaps.append("missing_persisted_l6_observations")
        if str(closure.get("observability_closure_status") or closure.get("closure_status") or "") != "PASS":
            proof_gaps.append("observability_closure_not_pass")
        proof_gaps.extend(
            _revalidate_observability_closure(
                closure=closure,
                package=package,
                artifact_dir=artifact_dir,
            )
        )
        if not lane_rows:
            proof_gaps.append("missing_apps_eval_scorecard_rows")

        parity_path = binding_dir / f"{lane_id}.independent_parity.json"
        parity: dict[str, Any] = {}
        if not proof_gaps:
            observations = [
                row
                for row in read_jsonl(observation_path)
                if str(row.get("lane_id") or "") == lane_id and row.get("required", True)
            ]
            parity = build_independent_apps_eval_parity(
                run_id=str(getattr(eval_record, "record_id", "") or ""),
                runtime_exhaust_bundle_id=str(package.get("runtime_exhaust_bundle_id") or ""),
                microstep_contract_digest=str(package.get("microstep_contract_digest") or ""),
                apps_eval_scorecard_ref=scorecard_ref,
                l6_observation_ref=_artifact_or_repo_rel(observation_path, artifact_dir),
                apps_eval_rows=lane_rows,
                l6_observations=observations,
                observation_origin=SEALED_APPS_RG_OBSERVATION_ORIGIN,
                expected_observation_bundle_id=str(package.get("runtime_exhaust_bundle_id") or ""),
                parent_run_id=str(package.get("parent_run_id") or ""),
                child_run_id=str(package.get("child_run_id") or ""),
                section_attempt_id=str(package.get("section_attempt_id") or ""),
                eval_record_id=str(getattr(eval_record, "record_id", "") or ""),
                snapshot_digest=str(
                    getattr(eval_record, "snapshot_digest", "")
                    or getattr(eval_record, "source_snapshot_digest", "")
                    or (lane_rows[0].get("snapshot_digest") if lane_rows else "")
                    or ""
                ),
                registry_digest=str(
                    getattr(eval_record, "registry_digest", "")
                    or (lane_rows[0].get("registry_digest") if lane_rows else "")
                    or package.get("registry_digest")
                    or ""
                ),
                source_run_root=artifact_dir.as_posix(),
                repository_root=REPO_ROOT.as_posix(),
                compare_artifact_digests=True,
            )
            write_independent_parity(parity_path, parity)
            if parity.get("grain_parity_status") != "PASS":
                proof_gaps.append("independent_grain_parity_failed")

        bound = not proof_gaps and parity.get("grain_parity_status") == "PASS"
        bindings.append(
            {
                "section_id": lane_id,
                "artifact_dir_ref": _artifact_or_repo_rel(v40_path.parent, artifact_dir),
                "l6_package_tier": "v40",
                "l6_v40_shadow_eval_package_ref": _artifact_or_repo_rel(v40_path, artifact_dir),
                "l6_v40_shadow_eval_package_sha256": f"sha256:{_sha256_file(v40_path)}",
                "l6_microstep_observations_ref": _artifact_or_repo_rel(observation_path, artifact_dir),
                "l6_observability_closure_ref": _artifact_or_repo_rel(closure_path, artifact_dir),
                "independent_parity_ref": (
                    _artifact_or_repo_rel(parity_path, artifact_dir) if parity_path.is_file() else ""
                ),
                "apps_eval_row_count": len(lane_rows),
                "apps_eval_row_ids": [str(row.get("row_id") or "") for row in lane_rows],
                "binding_status": "BOUND_PASS" if bound else "PARITY_FAIL",
                "evidence_class": "APPS_EVAL_BOUND_PROOF" if bound else "CONTRACT_ONLY_ADVISORY",
                "proof_gaps": proof_gaps,
                "package_immutable": True,
                "independent_observations": bool(parity.get("independent_observations") is True),
                "future_run_only": True,
                "current_run_mutation_assertion": False,
                "direct_l4_write_assertion": False,
                "durable_write_assertion": False,
            }
        )

    all_bound = bool(bindings) and all(item["binding_status"] == "BOUND_PASS" for item in bindings)
    summary = {
        "sections_total": len(bindings),
        "sections_bound": sum(1 for item in bindings if item["binding_status"] == "BOUND_PASS"),
        "sections_contract_only": sum(
            1 for item in bindings if item["evidence_class"] != "APPS_EVAL_BOUND_PROOF"
        ),
        "apps_eval_rows_bound": all_bound,
        "apps_eval_rows_bound_count": sum(
            int(item.get("apps_eval_row_count") or 0)
            for item in bindings
            if item["binding_status"] == "BOUND_PASS"
        ),
        "grain_parity_status": "PASS" if all_bound else "FAIL",
        "grain_parity_status_by_section": {
            str(item["section_id"]): str(item["binding_status"]) for item in bindings
        },
    }
    payload = {
        "schema_version": "apps_rg.l6_section_apps_eval_bindings.v2",
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

    closure_checks = {
        "sections_present": bool(bindings),
        "all_required_sections_bound": all_bound,
        "independent_observations": bool(bindings)
        and all(item.get("independent_observations") is True for item in bindings),
        "no_legacy_bound_proof": all(
            item.get("l6_package_tier") != "legacy"
            or item.get("evidence_class") != "APPS_EVAL_BOUND_PROOF"
            for item in bindings
        ),
    }
    closure_failed = sorted(name for name, passed in closure_checks.items() if not passed)
    binding_closure = {
        "schema_version": "apps_rg.l6_apps_eval_binding_closure_receipt.v1",
        "eval_record_id": str(getattr(eval_record, "record_id", "") or ""),
        "binding_closure_status": "PASS" if not closure_failed else "FAIL",
        "checks": closure_checks,
        "failed_checks": closure_failed,
        "l6_section_apps_eval_bindings_ref": _repo_rel(path, artifact_dir),
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only": True,
    }
    closure_path = artifact_dir / L6_APPS_EVAL_BINDING_CLOSURE
    _write_json(closure_path, binding_closure)
    return {
        "l6_section_apps_eval_bindings_ref": _repo_rel(path, artifact_dir),
        "l6_section_apps_eval_bindings_summary": summary,
        "l6_apps_eval_binding_closure_ref": _repo_rel(closure_path, artifact_dir),
        "alignment_source": "independent_persisted_observations",
        "apps_eval_rows_bound": all_bound,
        "evidence_class": "APPS_EVAL_BOUND_PROOF" if all_bound else "CONTRACT_ONLY_ADVISORY",
        "grain_parity_status": "PASS" if all_bound else "FAIL",
        "future_run_only": True,
        "current_run_mutated": False,
    }


def _complete_fact_vector_writeback_after_x3(
    *,
    artifact_dir: Path,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    """Retain separately governed fact-vector promotion after current-run UWG closure."""

    try:
        from apps_rg.runtime.c0.c02_fact_vector_ingest import INGEST_RECEIPT_NAME
        from apps_rg.runtime.c0.fact_vector_write_back import (
            PROMOTION_MODE_DEFERRED,
            promote_staged_fact_vectors,
        )
    except ImportError as exc:
        return {
            "schema_version": "apps_rg.fact_vector_writeback_post_x3_completion.v1",
            "status": "SKIPPED",
            "reason": f"fact_vector_components_unavailable:{type(exc).__name__}",
            "promotions": [],
        }

    receipts: list[dict[str, Any]] = []
    candidate_run_ids: list[str] = []
    for path in sorted(artifact_dir.rglob(INGEST_RECEIPT_NAME)):
        doc = _read_json(path)
        if not doc:
            continue
        receipts.append({"ref": _repo_rel(path, artifact_dir), "payload": doc})
        run_id = str(doc.get("run_id") or doc.get("staging_run_id") or "").strip()
        if run_id and run_id not in candidate_run_ids:
            candidate_run_ids.append(run_id)

    mode = str(os.environ.get("APPS_RG_FACT_VECTOR_PROMOTION_MODE", PROMOTION_MODE_DEFERRED)).strip()
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
        payload.update(status="SKIPPED", reason="promotion_mode_not_deferred")
        return payload
    chroma_path = str(os.environ.get("CHROMA_PERSIST_DIR", "")).strip()
    payload["chroma_path"] = chroma_path or None
    if not chroma_path:
        payload.update(status="FAIL", reason="CHROMA_PERSIST_DIR unset")
        return payload

    source_x3 = str(result.get("x3_disposition") or "").strip()
    for run_id in candidate_run_ids:
        safe_run_id = run_id.replace(":", "_").replace("\\", "_").replace("/", "_")
        promotion_dir = artifact_dir / "fact_vectors_post_x3" / safe_run_id
        promotion = promote_staged_fact_vectors(
            chroma_path=chroma_path,
            artifact_dir=promotion_dir,
            run_id=run_id,
            x3_code=source_x3,
            require_x3_allow=True,
            promotion_run_id=f"post_x3:{run_id}",
        )
        payload["promotions"].append(
            {
                "run_id": run_id,
                "artifact_dir": _repo_rel(promotion_dir, artifact_dir),
                "status": str(promotion.get("status") or ""),
                "reason": str(promotion.get("reason") or ""),
                "promoted_count": int(promotion.get("promoted_count") or 0),
                "uwg_status": str((promotion.get("uwg") or {}).get("status") or ""),
                "retrieval_proof_status": str(
                    (promotion.get("retrieval_proof") or {}).get("status") or ""
                ),
            }
        )
    failures = [
        row
        for row in payload["promotions"]
        if row["status"] != "PASS"
        or row["uwg_status"] != "ADMITTED"
        or row["retrieval_proof_status"] != "PASS"
    ]
    payload["status"] = "FAIL" if failures else "PASS"
    payload["reason"] = (
        "fact_vector_writeback_chain_failed" if failures else "fact_vector_writeback_chain_complete"
    )
    return payload


def _authority_order_receipt(
    *,
    artifact_dir: Path,
    ids: Mapping[str, str],
    commit_receipt: Any,
) -> dict[str, Any]:
    payload = {
        "schema_version": "apps_rg.post_x3_authority_order.v1",
        "run_id": ids["run_id"],
        "request_id": ids["request_id"],
        "uwg_commit_receipt_id": str(getattr(commit_receipt, "commit_receipt_id", "") or ""),
        "exit_completed_before_uwg": True,
        "uwg_closed_before_l6": True,
        "runtime_boundary_crossed_before_l6": True,
        "l6_influenced_current_uwg_decision": False,
        "apps_eval_influenced_current_uwg_decision": False,
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "future_run_only": True,
        "generated_at_utc": _utc_now_iso(),
    }
    _write_json(artifact_dir / POST_X3_AUTHORITY_ORDER_RECEIPT, payload)
    return payload


def _complete_apps_rg_post_x3(
    *,
    artifact_dir: Path | str,
    result: Mapping[str, Any],
    raw_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Commit the Exit-cleared run through UWG, then perform apps_eval/L6 observation."""

    art = Path(artifact_dir)
    receipt_path = art / POST_X3_COMPLETION_RECEIPT
    generated = _generated_resume_path(art)
    manifest = _load_output_manifest(art)
    eligible, reasons = (
        evaluate_apps_rg_full_success_eligibility(manifest=manifest, run_root=art)
        if manifest
        else (False, ["apps_rg_output_manifest_missing"])
    )
    if generated is None or not eligible:
        payload: dict[str, Any] = {
            "schema_version": "apps_rg.post_x3_completion.v2",
            "generated_at_utc": _utc_now_iso(),
            "status": "FAIL",
            "completed": False,
            "x3_to_uwg_completed": False,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "failure_stage": "pre_uwg_product_eligibility",
            "generated_resume_path": _repo_rel(generated, art) if generated else "",
            "eligibility_reasons": reasons,
            "durable_promotion_attempted": False,
            "product_authorized": False,
            "pipeline_complete": False,
            "observability_repair_required": False,
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
    ids = _identity(art, result, raw_request=raw_request)
    commit_request, state_diffs, rollback_plan, refresh_plan = _build_commit_packet(
        artifact_dir=art,
        generated_resume=generated,
        output_hash=output_hash,
        ids=ids,
    )

    # Current-run authority closes here, before apps_eval or L6 are invoked.
    gateway = get_default_gateway()
    commit_receipt, blocked_receipt, refresh_receipts = gateway.commit(
        commit_request=commit_request,
        state_diffs=state_diffs,
        rollback_plan=rollback_plan,
        refresh_plan=refresh_plan,
    )
    if commit_receipt is None or blocked_receipt is not None:
        payload = {
            "schema_version": "apps_rg.post_x3_completion.v2",
            "generated_at_utc": _utc_now_iso(),
            "status": "FAIL",
            "completed": False,
            "x3_to_uwg_completed": False,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "failure_stage": "uwg_commit",
            "durable_promotion_attempted": True,
            "durable_promotion_committed": False,
            "blocked_receipt": _json_ready(blocked_receipt) if blocked_receipt else {},
            "product_authorized": False,
            "pipeline_complete": False,
            "observability_repair_required": False,
        }
        payload["l6_shadow"] = _emit_post_x3_failure_l6_shadow_bridge(
            artifact_dir=art,
            failure_stage="uwg_commit",
            reason="uwg_commit_blocked",
            partial_payload=payload,
        )
        _write_json(receipt_path, payload)
        return payload

    validation = gateway.get_validation_receipt(commit_receipt.uwg_validation_receipt_ref)
    if validation is None:
        payload = {
            "schema_version": "apps_rg.post_x3_completion.v2",
            "generated_at_utc": _utc_now_iso(),
            "status": "FAIL",
            "completed": False,
            "x3_to_uwg_completed": True,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "failure_stage": "uwg_validation_receipt_lookup",
            "durable_promotion_attempted": True,
            "durable_promotion_committed": True,
            "uwg_validation_receipt_ref": commit_receipt.uwg_validation_receipt_ref,
            # UWG already committed.  Missing local validation evidence is a
            # reconciliation failure and cannot retroactively revoke it.
            "product_authorized": True,
            "pipeline_complete": False,
            "observability_repair_required": True,
        }
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
    authority = _authority_order_receipt(
        artifact_dir=art,
        ids=ids,
        commit_receipt=commit_receipt,
    )

    from apps_rg.runtime.terminal_state import (
        TerminalStateError,
        TerminalStateMachine,
        persist_product_authorization_receipt,
    )

    terminal_state = TerminalStateMachine()
    uwg_decision_ref = str(uwg_paths.get("uwg_commit_receipt") or "")
    uwg_decision_path = art / uwg_decision_ref
    terminal_state.close_product_authorization(
        authorized=True,
        decision_receipt_ref=uwg_decision_ref,
        decision_receipt_sha256=f"sha256:{_sha256_file(uwg_decision_path)}",
        output_artifact_sha256=f"sha256:{output_hash}",
        closed_at_utc=_utc_now_iso(),
    )
    identity_candidate = (
        (raw_request or {}).get("canonical_run_identity")
        or result.get("canonical_run_identity")
        or {}
    )
    canonical_identity = (
        dict(identity_candidate) if isinstance(identity_candidate, Mapping) else {}
    )
    required_identity_fields = {
        "producer_app_id",
        "consumer_app_id",
        "parent_run_id",
        "child_run_id",
        "request_id",
        "trace_root",
        "tenant_id",
        "target_company",
        "target_role",
        "jd_sha256",
        "brief_sha256",
        "policy_hash",
        "blueprint_hash",
        "schema_version",
    }
    product_authorization_receipt_ref = ""
    terminal_identity_gap = ""
    if required_identity_fields.issubset(canonical_identity) and all(
        str(canonical_identity.get(field) or "").strip()
        for field in required_identity_fields
    ):
        try:
            product_authorization_path = persist_product_authorization_receipt(
                artifact_dir=art,
                identity=canonical_identity,
                state=terminal_state.product_authorization,
                decision_receipt_ref=uwg_decision_ref,
                output_artifact_ref=generated,
            )
            product_authorization_receipt_ref = _repo_rel(
                product_authorization_path,
                art,
            )
        except TerminalStateError as exc:
            terminal_identity_gap = f"product_authorization_receipt:{exc}"
    else:
        terminal_identity_gap = "canonical_run_identity_missing_after_uwg"

    # Post-boundary observation begins only after UWG has closed.
    eval_record = _run_current_eval(
        artifact_dir=art,
        result=result,
        raw_request=raw_request,
    )
    eval_record_path = str(eval_record.artifact_paths.get("eval_record") or "")
    l6_bridge_path = str(eval_record.artifact_paths.get("l6_shadow_bridge") or "")
    eval_record_hash = _sha256_file(Path(eval_record_path)) if eval_record_path else ""
    l6_bridge_hash = (
        _sha256_file(Path(l6_bridge_path))
        if l6_bridge_path and Path(l6_bridge_path).is_file()
        else ""
    )
    l6_binding = _emit_l6_section_apps_eval_bindings(
        artifact_dir=art,
        eval_record=eval_record,
    )
    coverage = dict(eval_record.scorecard.coverage_summary or {})
    eval_pass = coverage.get("release_blocked") is False and coverage.get("coverage_complete") is True
    l6_pass = (
        l6_binding.get("grain_parity_status") == "PASS"
        and l6_binding.get("apps_eval_rows_bound") is True
    )

    fact_vector_writeback = _complete_fact_vector_writeback_after_x3(
        artifact_dir=art,
        result=result,
    )
    _write_json(art / "fact_vector_writeback_completion_receipt.json", fact_vector_writeback)
    post_boundary_pass = eval_pass and l6_pass and fact_vector_writeback.get("status") != "FAIL"
    pipeline_complete = bool(
        post_boundary_pass and product_authorization_receipt_ref
    )
    terminal_state.record_pipeline_completion(
        complete=pipeline_complete,
        failed=not pipeline_complete,
        decisive_stage_id=(
            "PIPELINE_COMPLETION_CLOSE"
            if pipeline_complete
            else "PRODUCT_AUTHORIZATION_CLOSE"
            if terminal_identity_gap
            else "APPS_EVAL_OR_L6"
        ),
    )
    post_boundary_stage = ""
    if not eval_pass:
        post_boundary_stage = "apps_eval_post_boundary"
    elif not l6_pass:
        post_boundary_stage = "l6_binding_post_boundary"
    elif fact_vector_writeback.get("status") == "FAIL":
        post_boundary_stage = "fact_vector_writeback_post_boundary"
    elif terminal_identity_gap:
        post_boundary_stage = "terminal_identity_reconciliation"

    apps_eval_payload = {
        "record_id": eval_record.record_id,
        "eval_record_ref": eval_record_path,
        "eval_record_sha256": f"sha256:{eval_record_hash}" if eval_record_hash else "",
        "score": eval_record.scorecard.score,
        "verdict": eval_record.scorecard.verdict,
        "coverage_summary": coverage,
        "scorecard_rows_ref": eval_record.artifact_paths.get("scorecard_rows", ""),
        "coverage_matrix_ref": eval_record.artifact_paths.get("coverage_matrix", ""),
        "current_run_authority": "NONE",
    }
    l6_shadow_payload = {
        "l6_shadow_bridge_ref": l6_bridge_path,
        "l6_shadow_bridge_sha256": f"sha256:{l6_bridge_hash}" if l6_bridge_hash else "",
        **l6_binding,
        "authority_order_receipt_ref": POST_X3_AUTHORITY_ORDER_RECEIPT,
        "future_run_only": True,
        "current_run_mutated": False,
    }
    payload = {
        "schema_version": "apps_rg.post_x3_completion.v2",
        "generated_at_utc": _utc_now_iso(),
        "status": "PASS" if pipeline_complete else "PASS_WITH_POST_BOUNDARY_GAPS",
        "completed": True,
        "x3_to_uwg_completed": True,
        "x3_to_uwg_to_eval_to_l6_completed": bool(post_boundary_pass),
        "product_authorized": True,
        "pipeline_complete": pipeline_complete,
        "observability_repair_required": terminal_state.observability_repair_required,
        "product_authorization_receipt_ref": product_authorization_receipt_ref,
        "terminal_identity_gap": terminal_identity_gap,
        "failure_stage": post_boundary_stage,
        "post_boundary_observability_status": "PASS" if post_boundary_pass else "FAIL",
        "durable_promotion_attempted": True,
        "durable_promotion_committed": True,
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
        "authority_order": authority,
        "fact_vector_writeback": fact_vector_writeback,
        "apps_eval": apps_eval_payload,
        "l6_shadow": l6_shadow_payload,
    }
    _write_json(receipt_path, payload)
    receipt_hash = _sha256_file(receipt_path)
    if eval_pass and l6_pass:
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
            l6_shadow_refs=l6_binding,
        )
    return payload


def complete_apps_rg_post_x3(
    *,
    artifact_dir: Path | str,
    result: Mapping[str, Any],
    raw_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Close post-X3 while preserving any already-committed UWG authority."""

    art = Path(artifact_dir)
    commit_candidates = (
        art / UWG_COMMIT_RECEIPT,
        art / UWG_DIR / UWG_COMMIT_RECEIPT,
    )
    prior_commit_digests = {
        candidate: _sha256_file(candidate)
        for candidate in commit_candidates
        if candidate.is_file()
    }
    try:
        return _complete_apps_rg_post_x3(
            artifact_dir=art,
            result=result,
            raw_request=raw_request,
        )
    except Exception as exc:  # noqa: BLE001  # guardian: allow-broad-exception -- persist post-UWG reconciliation
        commit_path = next(
            (
                candidate
                for candidate in commit_candidates
                if candidate.is_file()
                and prior_commit_digests.get(candidate) != _sha256_file(candidate)
            ),
            None,
        )
        if commit_path is None:
            raise
        payload = {
            "schema_version": "apps_rg.post_x3_completion.v2",
            "generated_at_utc": _utc_now_iso(),
            "status": "PASS_WITH_POST_BOUNDARY_GAPS",
            "completed": True,
            "x3_to_uwg_completed": True,
            "x3_to_uwg_to_eval_to_l6_completed": False,
            "product_authorized": True,
            "pipeline_complete": False,
            "observability_repair_required": True,
            "failure_stage": "post_boundary_reconciliation",
            "reconciliation_error_type": type(exc).__name__,
            "durable_promotion_attempted": True,
            "durable_promotion_committed": True,
            "uwg": {
                "commit_status": "COMMITTED",
                "artifacts": {
                    "uwg_commit_receipt": _repo_rel(commit_path, art)
                },
            },
        }
        _write_json(art / POST_X3_COMPLETION_RECEIPT, payload)
        return payload


__all__ = [
    "L6_APPS_EVAL_BINDING_CLOSURE",
    "L6_SECTION_APPS_EVAL_BINDINGS",
    "POST_X3_AUTHORITY_ORDER_RECEIPT",
    "POST_X3_COMPLETION_RECEIPT",
    "POST_X3_FAILURE_L6_APPS_EVAL_GRAIN_PARITY",
    "POST_X3_FAILURE_L6_SHADOW_BRIDGE",
    "complete_apps_rg_post_x3",
    "is_full_resume_product_artifact_dir",
]
