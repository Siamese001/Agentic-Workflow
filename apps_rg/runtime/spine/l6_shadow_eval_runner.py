"""apps_rg v40 L6 shadow-eval runner.

Runs only after the section RuntimeExhaustBundle is sealed. Outputs are
additive post-runtime artifacts and never change X3, Exit, L2, or L4 state.
The section runner closes *observability* independently from later apps_eval
binding; contract-only section evidence is not misreported as eval proof.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
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
    L6_TRACE_OBSERVABILITY_SUMMARY_ARTIFACT,
    TRACE_RECONCILIATION_ARTIFACT,
    emit_trace_reconciliation_artifacts,
)
from apps_rg.runtime.shadow.l6_microstep_observability import (
    emit_apps_rg_l6_microstep_artifacts,
)

APPS_RG_L6_V40_SHADOW_EVAL_ENV = "APPS_RG_L6_V40_SHADOW_EVAL"
APPS_RG_L6_V40_SHADOW_EVAL_SKIP_ENV = "APPS_RG_L6_V40_SHADOW_EVAL_SKIP"
APPS_RG_L6_V40_L5_CERTIFICATION_REF_ENV = "APPS_RG_L6_V40_L5_CERTIFICATION_REF"
APPS_RG_EXECUTION_PROFILE_ENV = "APPS_RG_EXECUTION_PROFILE"

L6_V40_SHADOW_EVAL_PACKAGE_ARTIFACT = "l6_v40_shadow_eval_package.json"
L6_V40_SHADOW_EVAL_SPANS_ARTIFACT = "l6_v40_shadow_eval_spans.json"
L6_V40_SHADOW_EVAL_SPANS_JSONL_ARTIFACT = "l6_v40_shadow_eval_spans.jsonl"
L6_OBSERVABILITY_CLOSURE_RECEIPT_ARTIFACT = "l6_observability_closure_receipt.json"
L6_APPS_EVAL_BINDING_CLOSURE_RECEIPT_ARTIFACT = "l6_apps_eval_binding_closure_receipt.json"
L5_CERTIFICATION_RECEIPT_ARTIFACT = "l5_certification_receipt.json"
L5_CERTIFICATION_RECEIPT_SCHEMA = "apps_rg.l5_certification_receipt.v1"

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
    L6_TRACE_OBSERVABILITY_SUMMARY_ARTIFACT: "L6",
}


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def l6_v40_shadow_eval_enabled(env: Mapping[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    if _truthy(source.get(APPS_RG_L6_V40_SHADOW_EVAL_SKIP_ENV)):
        profile = str(source.get(APPS_RG_EXECUTION_PROFILE_ENV) or "product").strip().lower()
        if profile in {"test", "migration", "replay", "non_product"}:
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


def _write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(payload), indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return dict(value) if isinstance(value, Mapping) else {}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _normal_sha256(value: Any) -> str:
    text = str(value or "").strip().lower()
    raw = text.removeprefix("sha256:")
    if len(raw) != 64:
        return ""
    try:
        int(raw, 16)
    except ValueError:
        return ""
    return f"sha256:{raw}"


def _canonical_digest(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(dict(payload), sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _contained(path: Path, roots: tuple[Path, ...]) -> bool:
    resolved = path.resolve()
    return any(resolved == root.resolve() or root.resolve() in resolved.parents for root in roots)


def _validate_l5_certification_receipt(
    *,
    artifact_dir: Path,
    repo_root: Path,
    ref: str,
    raw_exhaust: Mapping[str, Any],
) -> tuple[bool, list[str], str, str]:
    """Validate persisted L5 provenance for the current product run."""

    candidates: list[Path] = []
    text = str(ref or "").strip()
    if text:
        raw = Path(text)
        if raw.is_absolute():
            candidates.append(raw)
        else:
            candidates.extend((artifact_dir / raw, repo_root / raw))
    candidates.append(artifact_dir / L5_CERTIFICATION_RECEIPT_ARTIFACT)
    path = next((item.resolve() for item in candidates if item.is_file()), None)
    if path is None:
        return False, ["L5_CERTIFICATION_RECEIPT_MISSING"], "", ""
    if not _contained(path, (artifact_dir, repo_root)):
        return False, ["L5_CERTIFICATION_RECEIPT_OUTSIDE_APPROVED_ROOT"], "", ""
    payload = _load_json(path)
    seed = dict(payload)
    claimed_digest = str(seed.pop("receipt_digest", "") or "")
    computed_digest = _canonical_digest(seed)
    checks = {
        "schema": payload.get("schema_version") == L5_CERTIFICATION_RECEIPT_SCHEMA,
        "status": str(payload.get("certification_status") or "").upper() == "PASS",
        "scope": str(payload.get("scope") or "") == "apps_rg.l6_shadow_eval",
        "run_id": str(payload.get("run_id") or "") == str(raw_exhaust.get("run_id") or ""),
        "tenant_id": str(payload.get("tenant_id") or "")
        == str(raw_exhaust.get("tenant_id") or ""),
        "digest": bool(claimed_digest) and claimed_digest == computed_digest,
    }
    expires = str(payload.get("expires_at_utc") or "").strip()
    if expires:
        try:
            expiry = datetime.fromisoformat(expires.replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            checks["unexpired"] = expiry > datetime.now(timezone.utc)
        except ValueError:
            checks["unexpired"] = False
    failed = [f"L5_CERTIFICATION_{name.upper()}_INVALID" for name, ok in checks.items() if not ok]
    return not failed, sorted(failed), _repo_rel(repo_root, path), computed_digest


def _gate_pass(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    return str(value.get("verdict") or value.get("status") or "").upper() == "PASS"


def _existing(path: Path | None) -> bool:
    return bool(path is not None and path.is_file())


def _emit_l6_observability_closure_receipt(
    *,
    artifact_dir: Path,
    repo_root: Path,
    package_path: Path,
    package: Mapping[str, Any],
    trace_reconciliation_paths: Mapping[str, Path],
    microstep_paths: Mapping[str, Path],
    span_paths: Mapping[str, Path] | None = None,
) -> Path:
    """Seal post-run observability without pretending apps_eval is already bound."""

    span_paths = dict(span_paths or {})
    artifacts: dict[str, Path] = {
        "runtime_exhaust_bundle": artifact_dir / "runtime_exhaust_bundle.json",
        "exit_disposition_receipt": artifact_dir / "exit_disposition_receipt.json",
        "trace_reconciliation": trace_reconciliation_paths.get("trace_reconciliation", Path()),
        "trace_reconciliation_rows": trace_reconciliation_paths.get("trace_reconciliation_rows", Path()),
        "l6_trace_observability_summary": trace_reconciliation_paths.get(
            "l6_trace_observability_summary", Path()
        ),
        "l6_microstep_observations": microstep_paths.get("l6_microstep_observations", Path()),
        "l6_microstep_coverage": microstep_paths.get("l6_microstep_coverage", Path()),
        "l6_microstep_rca": microstep_paths.get("l6_microstep_rca", Path()),
        "l6_microstep_patterns": microstep_paths.get("l6_microstep_patterns", Path()),
        "l6_microstep_future_run_proposals": microstep_paths.get(
            "l6_microstep_future_run_proposals", Path()
        ),
        "l6_apps_eval_alignment": microstep_paths.get("l6_apps_eval_alignment", Path()),
        "l6_apps_eval_grain_parity": microstep_paths.get("l6_apps_eval_grain_parity", Path()),
        "l6_v40_shadow_eval_spans": span_paths.get(
            "span_export_json", artifact_dir / L6_V40_SHADOW_EVAL_SPANS_ARTIFACT
        ),
        "l6_v40_shadow_eval_spans_jsonl": span_paths.get(
            "span_export_jsonl", artifact_dir / L6_V40_SHADOW_EVAL_SPANS_JSONL_ARTIFACT
        ),
        "l6_v40_shadow_eval_package": package_path,
    }
    checks = {
        **{f"{name}_exists": _existing(path) for name, path in artifacts.items()},
        "valid_v40_shadow_exhaust": package.get("valid_v40_shadow_exhaust") is True,
        "readiness_scorable": str(package.get("readiness_decision") or "")
        in {"READY_FOR_6B", "PARTIAL_BUT_SCORABLE"},
        "g28_pass": _gate_pass(package.get("g28_audit_completeness")),
        "g29_pass": _gate_pass(package.get("g29_learning_firewall")),
        "no_current_run_mutation_assertion": package.get("current_run_mutation_assertion") is False
        and package.get("current_run_x3_mutation_assertion") is False,
        "no_direct_l4_write_assertion": package.get("direct_l4_write_assertion") is False,
        "no_durable_write_assertion": package.get("durable_write_assertion") is False,
        "future_run_only_assertion": package.get("future_run_only_assertion") is True,
        "l5_certification_valid": package.get("l5_certification_valid") is True,
        "parent_run_id_present": bool(str(package.get("parent_run_id") or "").strip()),
        "child_run_id_present": bool(str(package.get("child_run_id") or "").strip()),
        "section_attempt_id_present": bool(
            str(package.get("section_attempt_id") or "").strip()
        ),
        "microstep_contract_digest_present": str(
            package.get("microstep_contract_digest") or ""
        ).startswith("sha256:"),
        "registry_digest_present": str(package.get("registry_digest") or "").startswith(
            "sha256:"
        ),
        "contract_registry_digest_equal": bool(
            _normal_sha256(package.get("microstep_contract_digest"))
        )
        and _normal_sha256(package.get("microstep_contract_digest"))
        == _normal_sha256(package.get("registry_digest")),
        "runtime_exhaust_bundle_digest_present": bool(
            _normal_sha256(package.get("runtime_exhaust_bundle_digest"))
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    digest_map = {
        name: _sha256_file(path)
        for name, path in sorted(artifacts.items())
        if _existing(path)
    }
    closure_seed = {
        "runtime_exhaust_bundle_id": str(package.get("runtime_exhaust_bundle_id") or ""),
        "runtime_exhaust_bundle_digest": _normal_sha256(
            package.get("runtime_exhaust_bundle_digest")
        ),
        "parent_run_id": str(package.get("parent_run_id") or ""),
        "child_run_id": str(package.get("child_run_id") or ""),
        "section_attempt_id": str(package.get("section_attempt_id") or ""),
        "microstep_contract_digest": str(package.get("microstep_contract_digest") or ""),
        "registry_digest": _normal_sha256(package.get("registry_digest")),
        "checks": checks,
        "artifact_digests": digest_map,
    }
    receipt = {
        "schema_version": "apps_rg.l6_observability_closure_receipt.v2",
        "section_id": str(package.get("section_id") or ""),
        "runtime_exhaust_bundle_id": str(package.get("runtime_exhaust_bundle_id") or ""),
        "runtime_exhaust_bundle_digest": _normal_sha256(
            package.get("runtime_exhaust_bundle_digest")
        ),
        "parent_run_id": str(package.get("parent_run_id") or ""),
        "child_run_id": str(package.get("child_run_id") or ""),
        "section_attempt_id": str(package.get("section_attempt_id") or ""),
        "microstep_contract_digest": str(package.get("microstep_contract_digest") or ""),
        "registry_digest": _normal_sha256(package.get("registry_digest")),
        "observability_closure_status": "PASS" if not failed_checks else "FAIL",
        "closure_status": "PASS" if not failed_checks else "FAIL",
        "eval_binding_status": "PENDING",
        "eval_binding_required_for_future_run_promotion": True,
        "checks": checks,
        "failed_checks": failed_checks,
        "refs": {name: _repo_rel(repo_root, path) for name, path in artifacts.items() if _existing(path)},
        "artifact_digests": digest_map,
        "closure_digest": "sha256:"
        + hashlib.sha256(
            json.dumps(closure_seed, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "current_run_mutation_assertion": False,
        "current_run_x3_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only_assertion": True,
    }
    return _write_json(artifact_dir / L6_OBSERVABILITY_CLOSURE_RECEIPT_ARTIFACT, receipt)


def emit_l6_apps_eval_binding_closure_receipt(
    *,
    artifact_dir: Path,
    observability_closure_ref: str,
    independent_parity_ref: str,
    run_id: str,
) -> Path:
    """Emit additive binding closure after apps_eval; never rewrite section packages."""

    observation_path = Path(observability_closure_ref)
    parity_path = Path(independent_parity_ref)
    if not observation_path.is_absolute():
        observation_path = artifact_dir / observation_path
    if not parity_path.is_absolute():
        parity_path = artifact_dir / parity_path
    observation = _load_json(observation_path)
    parity = _load_json(parity_path)
    checks = {
        "observability_closure_pass": str(
            observation.get("observability_closure_status") or observation.get("closure_status") or ""
        )
        == "PASS",
        "independent_parity_pass": parity.get("grain_parity_status") == "PASS",
        "apps_eval_rows_bound": parity.get("apps_eval_rows_bound") is True,
        "independent_bound_evidence": parity.get("evidence_class") == "APPS_EVAL_BOUND_PROOF",
        "independent_observations": parity.get("independent_observations") is True,
        "authority_clean": parity.get("authority_mismatch") is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "apps_rg.l6_apps_eval_binding_closure_receipt.v1",
        "run_id": run_id,
        "binding_closure_status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "observability_closure_ref": observability_closure_ref,
        "independent_parity_ref": independent_parity_ref,
        "current_run_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only": True,
    }
    return _write_json(artifact_dir / L6_APPS_EVAL_BINDING_CLOSURE_RECEIPT_ARTIFACT, payload)


def run_l6_v40_shadow_eval_for_section(
    artifact_dir: Path,
    *,
    section_id: str,
    repo_root: Path,
    session_id: str = "",
    tenant_id: str = "",
    l5_certification_ref: str = "",
) -> dict[str, Path]:
    """Build v40 exhaust, run L6.1/L6.2, and seal post-run observability."""

    artifact_dir = Path(artifact_dir)
    repo_root = Path(repo_root)
    l5_ref = l5_certification_ref or os.environ.get(APPS_RG_L6_V40_L5_CERTIFICATION_REF_ENV, "")
    preliminary_exhaust = from_section_artifacts(
        artifact_dir,
        repo_root,
        section_id=section_id,
        stage_by_file=APPS_RG_V40_STAGE_BY_FILE,
        provider_lane="apps_rg",
        session_id=session_id,
        tenant_id=tenant_id,
        l5_certification_ref=l5_ref,
    )
    trace_reconciliation_paths = emit_trace_reconciliation_artifacts(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        section_id=section_id,
        run_id=str(preliminary_exhaust.get("run_id") or section_id),
    )
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
    l5_valid, l5_gaps, l5_receipt_ref, l5_receipt_digest = (
        _validate_l5_certification_receipt(
            artifact_dir=artifact_dir,
            repo_root=repo_root,
            ref=l5_ref,
            raw_exhaust=raw_exhaust,
        )
    )
    if not l5_valid:
        valid_v40 = False
        v40_gaps = sorted({*v40_gaps, *l5_gaps})

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
        parent_run_id=str(raw_exhaust.get("parent_run_id") or ""),
        child_run_id=str(raw_exhaust.get("child_run_id") or ""),
        section_attempt_id=str(raw_exhaust.get("section_attempt_id") or ""),
    )
    parity_payload = _load_json(microstep_paths["l6_apps_eval_grain_parity"])
    package: dict[str, Any] = {
        "schema_version": "apps_rg.l6_v40_shadow_eval.v2",
        "section_id": section_id,
        "parent_run_id": str(raw_exhaust.get("parent_run_id") or ""),
        "child_run_id": str(raw_exhaust.get("child_run_id") or ""),
        "section_attempt_id": str(raw_exhaust.get("section_attempt_id") or ""),
        "runtime_exhaust_bundle_id": ingest.bundle.runtime_exhaust_bundle_id,
        "runtime_exhaust_bundle_digest": _normal_sha256(
            ingest.bundle.deterministic_digest
        ),
        "microstep_contract_digest": str(
            parity_payload.get("microstep_contract_digest") or ""
        ),
        "registry_digest": str(parity_payload.get("registry_digest") or ""),
        "valid_v40_shadow_exhaust": valid_v40,
        "l5_certification_valid": l5_valid,
        "l5_certification_receipt_ref": l5_receipt_ref,
        "l5_certification_receipt_digest": l5_receipt_digest,
        "v40_gap_codes": v40_gaps,
        "readiness_decision": readiness.readiness_decision,
        "readiness_receipt": _jsonable(readiness),
        "g28_audit_completeness": _jsonable(state.g28),
        "g29_learning_firewall": _jsonable(state.g29),
        "ingest_gap_report": _jsonable(ingest.gap_report),
        "span_export_ref": _repo_rel(repo_root, span_paths["span_export_json"]),
        "span_export_jsonl_ref": _repo_rel(repo_root, span_paths["span_export_jsonl"]),
        "l6_microstep_observations_ref": _repo_rel(
            repo_root, microstep_paths["l6_microstep_observations"]
        ),
        "l6_microstep_coverage_ref": _repo_rel(repo_root, microstep_paths["l6_microstep_coverage"]),
        "l6_microstep_rca_ref": _repo_rel(repo_root, microstep_paths["l6_microstep_rca"]),
        "l6_microstep_patterns_ref": _repo_rel(repo_root, microstep_paths["l6_microstep_patterns"]),
        "l6_microstep_future_run_proposals_ref": _repo_rel(
            repo_root, microstep_paths["l6_microstep_future_run_proposals"]
        ),
        "l6_apps_eval_alignment_ref": _repo_rel(repo_root, microstep_paths["l6_apps_eval_alignment"]),
        "l6_apps_eval_grain_parity_ref": _repo_rel(
            repo_root, microstep_paths["l6_apps_eval_grain_parity"]
        ),
        "alignment_source": str(parity_payload.get("alignment_source") or "contract_only_pseudo_rows"),
        "apps_eval_rows_bound": False,
        "grain_parity_status": str(parity_payload.get("grain_parity_status") or "WARN"),
        "evidence_class": "CONTRACT_ONLY_ADVISORY",
        "eval_binding_status": "PENDING",
        "trace_reconciliation_ref": _repo_rel(
            repo_root, trace_reconciliation_paths["trace_reconciliation"]
        ),
        "trace_reconciliation_rows_ref": _repo_rel(
            repo_root, trace_reconciliation_paths["trace_reconciliation_rows"]
        ),
        "l6_trace_observability_summary_ref": _repo_rel(
            repo_root, trace_reconciliation_paths["l6_trace_observability_summary"]
        ),
        "l6_observability_closure_receipt_ref": _repo_rel(
            repo_root, artifact_dir / L6_OBSERVABILITY_CLOSURE_RECEIPT_ARTIFACT
        ),
        "input_refs": {
            "artifact_dir": _repo_rel(repo_root, artifact_dir),
            "runtime_exhaust_bundle": _repo_rel(
                repo_root, artifact_dir / "runtime_exhaust_bundle.json"
            ),
            "exit_disposition_receipt": _repo_rel(
                repo_root, artifact_dir / "exit_disposition_receipt.json"
            ),
            "trace_reconciliation": _repo_rel(
                repo_root, trace_reconciliation_paths["trace_reconciliation"]
            ),
        },
        "current_run_mutation_assertion": False,
        "current_run_x3_mutation_assertion": False,
        "direct_l4_write_assertion": False,
        "durable_write_assertion": False,
        "future_run_only_assertion": True,
    }
    package_path = _write_json(artifact_dir / L6_V40_SHADOW_EVAL_PACKAGE_ARTIFACT, package)
    closure_path = _emit_l6_observability_closure_receipt(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        package_path=package_path,
        package=package,
        trace_reconciliation_paths=trace_reconciliation_paths,
        microstep_paths=microstep_paths,
        span_paths=span_paths,
    )
    return {
        "l6_v40_shadow_eval_package": package_path,
        "l6_observability_closure_receipt": closure_path,
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
    "APPS_RG_EXECUTION_PROFILE_ENV",
    "APPS_RG_L6_V40_SHADOW_EVAL_ENV",
    "APPS_RG_L6_V40_SHADOW_EVAL_SKIP_ENV",
    "L6_APPS_EVAL_BINDING_CLOSURE_RECEIPT_ARTIFACT",
    "L6_OBSERVABILITY_CLOSURE_RECEIPT_ARTIFACT",
    "L6_V40_SHADOW_EVAL_PACKAGE_ARTIFACT",
    "L6_V40_SHADOW_EVAL_SPANS_ARTIFACT",
    "L6_V40_SHADOW_EVAL_SPANS_JSONL_ARTIFACT",
    "emit_l6_apps_eval_binding_closure_receipt",
    "l6_v40_shadow_eval_enabled",
    "maybe_run_l6_v40_shadow_eval_for_section",
    "run_l6_v40_shadow_eval_for_section",
]
