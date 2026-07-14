"""Receipt-derived product-stage closure adapters for the full apps_rg run.

These adapters never accept a caller-authored stage status.  Each status is
recomputed from exact, contained runtime artifact bytes and the frozen
canonical run identity, then persisted with source byte bindings for replay.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

AUTHORITY_RECEIPT_DIR = "e2e_authority_receipts"
AUTHORITY_SOURCE_DIR = "e2e_authority_sources"


class ProductStageAuthorityError(RuntimeError):
    """Raised when canonical stage evidence cannot be reopened or derived."""


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductStageAuthorityError(
            f"unreadable stage authority artifact {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ProductStageAuthorityError(
            f"stage authority artifact is not an object: {path}"
        )
    return value


def _payload(value: Mapping[str, Any]) -> dict[str, Any]:
    nested = value.get("payload")
    return dict(nested) if isinstance(nested, Mapping) else dict(value)


def _resolve_contained(root: Path, ref: str | Path) -> Path:
    base = root.resolve()
    raw = Path(ref)
    target = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ProductStageAuthorityError(f"stage evidence escapes run root: {ref}") from exc
    if not target.is_file():
        raise ProductStageAuthorityError(f"stage evidence is missing: {ref}")
    return target


def _binding(root: Path, ref: str | Path) -> dict[str, Any]:
    target = _resolve_contained(root, ref)
    raw = target.read_bytes()
    return {
        "artifact_ref": target.relative_to(root.resolve()).as_posix(),
        "sha256": _sha256_bytes(raw),
        "byte_length": len(raw),
    }


def _write_atomic(path: Path, payload: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def mirror_external_authority_artifact(
    *,
    artifact_dir: Path,
    source: Path,
    relative_ref: str,
) -> Path:
    """Copy exact external producer bytes under the consumer run root."""

    source_path = Path(source).resolve()
    if not source_path.is_file():
        raise ProductStageAuthorityError(
            f"external authority artifact is missing: {source_path}"
        )
    target = Path(artifact_dir) / AUTHORITY_SOURCE_DIR / relative_ref
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ProductStageAuthorityError(
            f"authority mirror already exists: {target}"
        )
    raw = source_path.read_bytes()
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(target)
    if target.read_bytes() != raw:
        raise ProductStageAuthorityError(
            f"authority mirror bytes changed while copying: {source_path}"
        )
    return target


def _identity_matches(
    payload: Mapping[str, Any],
    identity: Mapping[str, Any],
) -> bool:
    return all(
        str(payload.get(receipt_field) or "")
        == str(identity.get(identity_field) or "")
        for receipt_field, identity_field in (
            ("run_id", "parent_run_id"),
            ("request_id", "request_id"),
            ("trace_root", "trace_root"),
        )
    )


def _write_stage_receipt(
    *,
    artifact_dir: Path,
    stage_id: str,
    identity: Mapping[str, Any],
    passed: bool,
    checks: Mapping[str, bool],
    source_refs: Sequence[str | Path],
    derived_fields: Mapping[str, Any] | None = None,
) -> Path:
    bindings = [_binding(artifact_dir, ref) for ref in source_refs]
    failed_checks = sorted(name for name, value in checks.items() if not value)
    payload = {
        "schema_version": f"apps_rg.e2e_stage_authority.{stage_id.lower()}.v1",
        "authority_contract_id": "apps_research_rg_e2e_authority",
        "stage_id": stage_id,
        "status": "PASS" if passed and not failed_checks else "BLOCKED",
        "identity": dict(identity),
        "checks": dict(checks),
        "failed_checks": failed_checks,
        "source_bindings": bindings,
        **dict(derived_fields or {}),
    }
    return _write_atomic(
        Path(artifact_dir)
        / AUTHORITY_RECEIPT_DIR
        / f"{stage_id.lower()}_authority_receipt.json",
        payload,
    )


def emit_runtime_stage_authority_receipts(
    *,
    artifact_dir: Path,
    identity: Mapping[str, Any],
) -> dict[str, Path]:
    """Recompute C0/PA/L2/X1/X2/X3 from persisted spine receipts."""

    root = Path(artifact_dir).resolve()
    witness_path = root / "runtime_execution_witness.json"
    terminal_path = root / "terminal_ret_packet.json"
    review_path = root / "exit_review_packet.json"
    x3_path = root / "x3_disposition_receipt.json"
    witness = _payload(_read_json(witness_path))
    terminal = _payload(_read_json(terminal_path))
    review = _payload(_read_json(review_path))
    x3 = _payload(_read_json(x3_path))
    runtime_identity = all(
        _identity_matches(value, identity)
        for value in (witness, terminal, review, x3)
    )
    c0 = witness.get("c0") if isinstance(witness.get("c0"), Mapping) else {}
    l2 = witness.get("l2") if isinstance(witness.get("l2"), Mapping) else {}
    x1 = witness.get("x1") if isinstance(witness.get("x1"), Mapping) else {}
    x2 = witness.get("x2") if isinstance(witness.get("x2"), Mapping) else {}
    x3_witness = witness.get("x3") if isinstance(witness.get("x3"), Mapping) else {}
    x3_code = str(x3.get("disposition") or x3.get("x3_code") or "")
    review_x3 = str(review.get("x3_disposition") or review.get("disposition") or "")

    prompt_candidates = (
        root / "compiled_prompt_artifact.json",
        root / "prompt_assembly_bypass_receipt.json",
    )
    prompt_path = next((path for path in prompt_candidates if path.is_file()), None)
    if prompt_path is None:
        raise ProductStageAuthorityError(
            "PA authority requires compiled prompt or explicit bypass receipt"
        )

    checks_by_stage: dict[str, dict[str, bool]] = {
        "APPS_RG_C0": {
            "runtime_identity_match": runtime_identity,
            "c0_receipt_present": bool(c0),
            "c0_status_authorized": str(c0.get("status") or "")
            in {"PASS", "BYPASSED_PRELOADED_CONTEXT"},
        },
        "APPS_RG_PA": {
            "runtime_identity_match": runtime_identity,
            "prompt_authority_receipt_present": prompt_path.is_file(),
        },
        "APPS_RG_L2": {
            "runtime_identity_match": runtime_identity,
            "l2_executed": l2.get("executed") is True,
            "l2_status_pass": l2.get("status") == "PASS",
            "l2_fault_empty": not str(l2.get("fault") or terminal.get("l2_fault") or ""),
        },
        "X1_REVIEW": {
            "runtime_identity_match": runtime_identity,
            "x1_executed": x1.get("status") == "EXECUTED",
            "review_packet_x3_authorizing": review_x3 == "X3D_ALLOW_FINISH",
        },
        "X2_AGGREGATION": {
            "runtime_identity_match": runtime_identity,
            "x2_executed": x2.get("status") == "EXECUTED",
            "x2_no_failed_gates": not list(x2.get("failed_gate_ids") or ()),
            "x2_disposition_authorizing": str(x2.get("disposition") or "")
            == "X3D_ALLOW_FINISH",
        },
        "X3_DISPOSITION": {
            "runtime_identity_match": runtime_identity,
            "x3_witness_emitted": x3_witness.get("status") == "EMITTED",
            "x3_receipt_exact_authorizing_code": x3_code == "X3D_ALLOW_FINISH",
            "unknown_never_pass": x3.get("unknown_never_pass") is True,
        },
    }
    sources = {
        "APPS_RG_C0": (witness_path,),
        "APPS_RG_PA": (prompt_path,),
        "APPS_RG_L2": (witness_path, terminal_path),
        "X1_REVIEW": (witness_path, review_path),
        "X2_AGGREGATION": (witness_path, review_path),
        "X3_DISPOSITION": (x3_path, witness_path),
    }
    return {
        stage_id: _write_stage_receipt(
            artifact_dir=root,
            stage_id=stage_id,
            identity=identity,
            passed=all(checks.values()),
            checks=checks,
            source_refs=sources[stage_id],
        )
        for stage_id, checks in checks_by_stage.items()
    }


def emit_product_eligibility_authority_receipt(
    *,
    artifact_dir: Path,
    identity: Mapping[str, Any],
) -> Path:
    """Recompute product eligibility from manifest and exact output bytes."""

    from apps_rg.runtime.package.apps_rg_full_resume_x3_eligibility import (
        evaluate_apps_rg_full_success_eligibility,
    )

    root = Path(artifact_dir).resolve()
    manifest_path = root / "apps_rg_output_manifest.json"
    manifest = _read_json(manifest_path)
    eligible, reasons = evaluate_apps_rg_full_success_eligibility(
        manifest=manifest,
        run_root=root,
    )
    generated_ref = str(
        manifest.get("generated_resume_json_relpath")
        or "outputs/generated_resume.json"
    )
    checks = {
        "eligibility_validator_pass": bool(eligible),
        "eligibility_reasons_empty": not reasons,
        "generated_output_present": _resolve_contained(root, generated_ref).is_file(),
    }
    return _write_stage_receipt(
        artifact_dir=root,
        stage_id="PRODUCT_ELIGIBILITY",
        identity=identity,
        passed=all(checks.values()),
        checks=checks,
        source_refs=(manifest_path, generated_ref),
    )


def emit_post_boundary_authority_receipts(
    *,
    artifact_dir: Path,
    identity: Mapping[str, Any],
    post_x3_completion: Mapping[str, Any],
) -> dict[str, Path]:
    """Derive Eval/L6/parity/promotion states from persisted closure bytes."""

    root = Path(artifact_dir).resolve()
    completion_path = root / "apps_rg_post_x3_completion_receipt.json"
    completion = _read_json(completion_path)
    if dict(completion) != dict(post_x3_completion):
        raise ProductStageAuthorityError(
            "post-X3 completion bytes differ from the returned completion payload"
        )
    apps_eval = completion.get("apps_eval")
    apps_eval = dict(apps_eval) if isinstance(apps_eval, Mapping) else {}
    coverage = apps_eval.get("coverage_summary")
    coverage = dict(coverage) if isinstance(coverage, Mapping) else {}
    l6 = completion.get("l6_shadow")
    l6 = dict(l6) if isinstance(l6, Mapping) else {}
    fact_vector = completion.get("fact_vector_writeback")
    fact_vector = dict(fact_vector) if isinstance(fact_vector, Mapping) else {}

    eval_ref = str(apps_eval.get("eval_record_ref") or "")
    l6_ref = str(l6.get("l6_shadow_bridge_ref") or "")
    parity_ref = str(l6.get("l6_apps_eval_binding_closure_ref") or "")
    promotion_ref = "fact_vector_writeback_completion_receipt.json"
    eval_path = _resolve_contained(root, eval_ref)
    l6_path = _resolve_contained(root, l6_ref)
    parity_path = _resolve_contained(root, parity_ref)
    promotion_path = _resolve_contained(root, promotion_ref)
    eval_record = _read_json(eval_path)
    parity = _read_json(parity_path)
    promotion = _read_json(promotion_path)
    from apps_eval.runner.core import verify_apps_rg_eval_package_seal

    eval_seal_path = eval_path.parent / "apps_rg_eval_package_seal.json"
    eval_seal_valid, eval_seal_errors = verify_apps_rg_eval_package_seal(
        eval_path.parent
    )
    eval_seal = _read_json(eval_seal_path)
    completion_record_id = str(apps_eval.get("record_id") or "")
    eval_record_id = str(eval_record.get("record_id") or "")
    eval_self_record_id = str(eval_record.get("eval_record_id") or "")
    seal_record_id = str(eval_seal.get("record_id") or "")
    eval_package_refs = tuple(
        eval_path.parent / str(row.get("artifact_ref") or "")
        for row in eval_seal.get("artifacts") or ()
        if isinstance(row, Mapping) and str(row.get("artifact_ref") or "")
    )

    checks_by_stage: dict[str, dict[str, bool]] = {
        "APPS_EVAL": {
            "eval_record_present": eval_path.is_file(),
            "eval_package_seal_present": eval_seal_path.is_file(),
            "eval_package_seal_valid": eval_seal_valid and not eval_seal_errors,
            "eval_record_schema_exact": eval_record.get("schema_version")
            == "apps_eval.completed_eval.v3",
            "eval_record_product_app_exact": eval_record.get("app_id") == "apps_rg",
            "eval_record_id_bound": bool(completion_record_id)
            and completion_record_id == eval_record_id == eval_self_record_id
            and eval_record_id == seal_record_id,
            "eval_record_parent_identity_match": str(
                eval_record.get("parent_run_id") or ""
            )
            == str(identity.get("parent_run_id") or ""),
            "coverage_complete": coverage.get("coverage_complete") is True,
            "release_not_blocked": coverage.get("release_blocked") is False,
        },
        "L6_SHADOW": {
            "l6_bridge_present": l6_path.is_file(),
            "grain_parity_pass": l6.get("grain_parity_status") == "PASS",
            "eval_rows_bound": l6.get("apps_eval_rows_bound") is True,
        },
        "INDEPENDENT_PARITY": {
            "parity_receipt_present": parity_path.is_file(),
            "binding_closure_pass": parity.get("binding_closure_status") == "PASS",
        },
        "PROMOTION_TERMINAL": {
            "promotion_receipt_present": promotion_path.is_file(),
            "terminal_status_present": bool(str(promotion.get("status") or "")),
            "promotion_not_failed": promotion.get("status") != "FAIL",
        },
    }
    sources = {
        "APPS_EVAL": tuple(
            dict.fromkeys(
                (completion_path, eval_path, eval_seal_path, *eval_package_refs)
            )
        ),
        "L6_SHADOW": (completion_path, l6_path),
        "INDEPENDENT_PARITY": (completion_path, parity_path),
        "PROMOTION_TERMINAL": (completion_path, promotion_path),
    }
    return {
        stage_id: _write_stage_receipt(
            artifact_dir=root,
            stage_id=stage_id,
            identity=identity,
            passed=all(checks.values()),
            checks=checks,
            source_refs=sources[stage_id],
            derived_fields=(
                {
                    "promotion_terminal_status": (
                        "PROMOTED"
                        if fact_vector.get("status") == "PASS"
                        else "REJECTED"
                    )
                }
                if stage_id == "PROMOTION_TERMINAL"
                else None
            ),
        )
        for stage_id, checks in checks_by_stage.items()
    }


def emit_mandatory_outputs_authority_receipt(
    *,
    artifact_dir: Path,
    identity: Mapping[str, Any],
) -> Path:
    """Reopen the mandatory output and derive its terminal gate status."""

    root = Path(artifact_dir).resolve()
    mandatory_path = root / "APPS_RG_MANDATORY_RUN_OUTPUT.json"
    mandatory = _read_json(mandatory_path)
    from apps_rg.runtime.mandatory_outputs import (
        MANDATORY_OUTPUT_COMMIT_MANIFEST,
        PRODUCT_MANDATORY_OUTPUT_PROFILE,
        validate_mandatory_output_seal,
    )
    from apps_rg.runtime.run_output_contract import (
        APPS_RG_MANDATORY_RUN_OUTPUT_MD,
        BCG_EXECUTIVE_OUTPUT_MD,
        FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
        FINAL_RESUME_DOCX_RELPATH,
        FINAL_RESUME_OUTPUT_JSON,
        FINAL_RESUME_OUTPUT_TXT,
        L7_AUDIT_ABILITY_OUTPUT_MD,
        OUTPUT_BISECT_MD,
    )

    marker_path = root / MANDATORY_OUTPUT_COMMIT_MANIFEST
    marker = _read_json(marker_path)
    declared_required = {
        str(value) for value in marker.get("required_artifacts") or ()
    }
    declared_artifacts = {
        str(value) for value in (marker.get("artifacts") or {})
    }
    product_minimum = {
        "APPS_RG_MANDATORY_RUN_OUTPUT.json",
        APPS_RG_MANDATORY_RUN_OUTPUT_MD,
        BCG_EXECUTIVE_OUTPUT_MD,
        OUTPUT_BISECT_MD,
        L7_AUDIT_ABILITY_OUTPUT_MD,
        FINAL_RESUME_OUTPUT_TXT,
        FINAL_RESUME_OUTPUT_JSON,
        FINAL_RESUME_DOCX_RELPATH,
        FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
        "apps_rg_output_manifest.json",
    }
    seal_valid, seal_errors = validate_mandatory_output_seal(
        root,
        expected_profile_id=PRODUCT_MANDATORY_OUTPUT_PROFILE,
    )
    gate = mandatory.get("mandatory_output_hard_stop")
    gate = dict(gate) if isinstance(gate, Mapping) else {}
    checks = {
        "mandatory_output_present": mandatory_path.is_file(),
        "mandatory_gate_present": bool(gate),
        "mandatory_gate_pass": gate.get("pass") is True,
        "product_profile_exact": marker.get("profile_id")
        == PRODUCT_MANDATORY_OUTPUT_PROFILE,
        "declared_artifact_set_exact": declared_required == declared_artifacts,
        "product_required_artifacts_not_shrunk": product_minimum.issubset(
            declared_required
        ),
        "mandatory_commit_seal_valid": seal_valid and not seal_errors,
    }
    return _write_stage_receipt(
        artifact_dir=root,
        stage_id="MANDATORY_OUTPUTS",
        identity=identity,
        passed=all(checks.values()),
        checks=checks,
        source_refs=(
            mandatory_path,
            marker_path,
            *(root / relative for relative in sorted(declared_required)),
        ),
    )


__all__ = [
    "ProductStageAuthorityError",
    "emit_mandatory_outputs_authority_receipt",
    "emit_post_boundary_authority_receipts",
    "emit_product_eligibility_authority_receipt",
    "emit_runtime_stage_authority_receipts",
    "mirror_external_authority_artifact",
]
