"""Section lane → agentic_core L7 binding manifest (refs only; no L7 artifact emission).

Emits ``section_l7_binding_manifest.json`` after modular section runs. Classifies
on-disk artifacts and records which core L7 surfaces are present, missing, or
untrusted — without writing duplicate ``agentic_core_how_trace.json`` / spine proof files.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.section_binding_taxonomy import (
    APPS_RG_DOMAIN_ARTIFACTS,
    APPS_RG_SHIM_ARTIFACTS,
    CORE_99_DESIGN_ONLY_ARTIFACTS,
    L7_CORE_ARTIFACTS,
    design_law_owner_for_artifact,
)

BINDING_MANIFEST_ARTIFACT = "section_l7_binding_manifest.json"
SCHEMA_VERSION = "section_l7_binding_manifest_v2"
_CANONICAL_PRODUCER = "apps_rg_section_l7_binding"

# Legacy aliases (tests) — design-law taxonomy is authoritative in design_law_owner_classifications.
CLASS_CORE_L7_REF = "CORE_L7_REF"
CLASS_CORE_L7_MISSING = "MISSING"
CLASS_CORE_99_DESIGN_ONLY = "DESIGN_ONLY"
CLASS_APPS_RG_DOMAIN = "APP_DOMAIN_EVIDENCE"
CLASS_APPS_RG_SHIM = "APP_SHIM"
CLASS_APPS_RG_ADAPTER = "APP_ADAPTER"
CLASS_NOT_APPLICABLE = "NOT_APPLICABLE"
CLASS_CORE_L7_UNTRUSTED = "DRIFT"

DEFAULT_MISSING_L7_SURFACES: tuple[str, ...] = (
    "agentic_core_how_trace.json",
    "agentic_core_l7_route_family_coverage.json",
    "agentic_core_spine_proof.json",
    "integrated_runtime_artifact_manifest.json",
)

DEFAULT_MISSING_99_SURFACES: tuple[str, ...] = CORE_99_DESIGN_ONLY_ARTIFACTS

DEFAULT_EXPLICIT_NON_CLAIMS: tuple[str, ...] = (
    "section_l7_binding_manifest is not agentic_core_how_trace",
    "section_l7_binding_manifest is not agentic_core_spine_proof",
    "section_l7_binding_manifest is not 99 RuntimeProofBundle",
    "apps_rg X2 gates are not 00C GateVerdicts",
    "apps_rg section_runtime_proof_bundle is not core 99 RuntimeProofBundle",
    "no durable UWG/L4 commit unless CommitRequest + StateCommitReceipt are present",
    "no product certification unless product_certification_receipt says certified",
    "apps_rg does not emit duplicate L7 audit artifacts from this binding module",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_rel(repo_root: Path, path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix().replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _payload(doc: Mapping[str, Any]) -> Mapping[str, Any]:
    p = doc.get("payload")
    return p if isinstance(p, Mapping) else doc


def _producer_component(doc: Mapping[str, Any]) -> str:
    pc = doc.get("producer_component")
    return pc.strip() if isinstance(pc, str) else ""


def assess_l7_how_trace_trust(doc: Mapping[str, Any]) -> tuple[bool, str]:
    """Return (trusted, reason). Trusted only for agentic_core L7 HOW trace shape."""
    if not doc:
        return False, "absent"
    pay = _payload(doc)
    if (
        pay.get("evidence_plane") == "L7_AUDITABILITY"
        and pay.get("runtime_subject") == "agentic_core"
        and pay.get("schema_version")
    ):
        return True, "l7_how_trace_shape"
    if _producer_component(doc).startswith("agentic_core."):
        return True, "integrated_runtime_envelope"
    return False, "untrusted_or_non_l7_shape"


def assess_l7_route_family_coverage_trust(doc: Mapping[str, Any]) -> tuple[bool, str]:
    if not doc:
        return False, "absent"
    pay = _payload(doc)
    if pay.get("evidence_plane") == "L7_AUDITABILITY" and pay.get("evidence_class") == (
        "ROUTE_FAMILY_COVERAGE_MATRIX"
    ):
        return True, "l7_route_family_matrix"
    if _producer_component(doc).startswith("agentic_core."):
        return True, "integrated_runtime_envelope"
    return False, "untrusted_or_non_l7_shape"


def assess_l7_spine_proof_trust(doc: Mapping[str, Any]) -> tuple[bool, str]:
    if not doc:
        return False, "absent"
    pay = _payload(doc)
    body = pay if pay.get("proof_schema_version") else doc
    if body.get("runtime_subject") != "agentic_core" and not body.get("proof_schema_version"):
        if doc.get("runtime_subject") != "agentic_core" and not doc.get("proof_schema_version"):
            return False, "missing_proof_schema_version_and_runtime_subject"
    subject = str(body.get("runtime_subject") or doc.get("runtime_subject") or "")
    if subject and subject != "agentic_core":
        return False, f"unexpected_runtime_subject={subject}"
    if not (body.get("proof_schema_version") or doc.get("proof_schema_version")):
        return False, "missing_proof_schema_version"
    if _producer_component(doc).startswith("agentic_core."):
        return True, "integrated_runtime_envelope"
    if body.get("proof_schema_version") or doc.get("proof_schema_version"):
        return True, "spine_proof_schema"
    return False, "untrusted_or_non_spine_shape"


def assess_integrated_manifest_trust(doc: Mapping[str, Any]) -> tuple[bool, str]:
    if not doc:
        return False, "absent"
    if doc.get("integrated_runtime_entrypoint_used") is True:
        return True, "integrated_runtime_manifest"
    pay = _payload(doc)
    if pay.get("integrated_runtime_entrypoint_used") is True:
        return True, "integrated_runtime_manifest_payload"
    if _producer_component(doc).startswith("agentic_core."):
        return True, "integrated_runtime_envelope"
    return False, "untrusted_or_non_integrated_manifest"


def assess_runtime_trace_snapshot_trust(doc: Mapping[str, Any]) -> tuple[bool, str]:
    if not doc:
        return False, "absent"
    if _producer_component(doc).startswith("agentic_core."):
        return True, "integrated_runtime_envelope"
    pay = _payload(doc)
    if pay.get("schema_version", "").startswith("runtime_trace_snapshot"):
        return True, "runtime_trace_snapshot_shape"
    return False, "untrusted_or_non_trace_snapshot"


def assess_runtime_gate_verdict_bundle_trust(doc: Mapping[str, Any]) -> tuple[bool, str]:
    if not doc:
        return False, "absent"
    if _producer_component(doc).startswith("agentic_core."):
        return True, "integrated_runtime_envelope"
    pay = _payload(doc)
    if pay.get("schema_version", "").startswith("runtime_gate_verdict"):
        return True, "gate_verdict_bundle_shape"
    return False, "untrusted_or_non_gate_bundle"


_L7_TRUST_ASSESSORS: dict[str, Any] = {
    "agentic_core_how_trace.json": assess_l7_how_trace_trust,
    "agentic_core_l7_route_family_coverage.json": assess_l7_route_family_coverage_trust,
    "agentic_core_spine_proof.json": assess_l7_spine_proof_trust,
    "integrated_runtime_artifact_manifest.json": assess_integrated_manifest_trust,
    "runtime_trace_snapshot.json": assess_runtime_trace_snapshot_trust,
    "runtime_gate_verdict_bundle.json": assess_runtime_gate_verdict_bundle_trust,
}


def classify_core_l7_artifact(filename: str, *, present: bool, trusted: bool) -> str:
    if filename == "runtime_gate_verdict_bundle.json" and not present:
        return CLASS_NOT_APPLICABLE
    if not present:
        return CLASS_CORE_L7_MISSING
    if trusted:
        return CLASS_CORE_L7_REF
    return CLASS_CORE_L7_UNTRUSTED


def _static_classification(filename: str) -> str:
    if filename in APPS_RG_DOMAIN_ARTIFACTS:
        return CLASS_APPS_RG_DOMAIN
    if filename in APPS_RG_SHIM_ARTIFACTS:
        return CLASS_APPS_RG_SHIM
    if filename in CORE_99_DESIGN_ONLY_ARTIFACTS:
        return CLASS_CORE_99_DESIGN_ONLY
    if filename in L7_CORE_ARTIFACTS:
        return CLASS_CORE_L7_MISSING
    return CLASS_APPS_RG_ADAPTER


def _durable_write_evidence(artifact_dir: Path) -> dict[str, Any]:
    commit_request = artifact_dir / "commit_request.json"
    state_commit = artifact_dir / "state_commit_receipt.json"
    uwg_commit = artifact_dir / "uwg_commit_receipt.json"
    uwg_any = any(
        (artifact_dir / name).is_file()
        for name in (
            "uwg_commit_receipt.json",
            "uwg_block_receipt.json",
            "state_commit_receipt.json",
        )
    )
    commit_receipt_ok = state_commit.is_file() or uwg_commit.is_file()
    return {
        "commit_request_present": commit_request.is_file(),
        "state_commit_receipt_present": state_commit.is_file(),
        "uwg_commit_receipt_present": uwg_commit.is_file(),
        "uwg_receipt_present": uwg_any,
        "durable_write_claim_allowed": commit_request.is_file() and commit_receipt_ok,
        "filename_drift_note": (
            "integrated runtime emits uwg_commit_receipt.json; "
            "StateCommitReceipt canonical name may differ on disk"
        ),
    }


def _product_certification_impact(artifact_dir: Path) -> dict[str, Any]:
    pc = _load_json(artifact_dir / "product_certification_receipt.json")
    pe = _load_json(artifact_dir / "proof_eligibility_receipt.json")
    binding_notes = (
        "L7 binding manifest records refs only; does not upgrade product certification."
    )
    return {
        "product_certification": pc.get("product_certification", "UNKNOWN"),
        "product_certification_reason": pc.get("product_certification_reason", ""),
        "proof_eligible": pe.get("proof_eligible"),
        "proof_eligibility_reason": pe.get("proof_eligibility_reason", ""),
        "binding_impact": binding_notes,
        "l7_certification_claimed": False,
        "runtime_proof_bundle_99_claimed": False,
    }


def _proof_classification(
    *,
    integrated_l7_invoked: bool,
    l7_trusted_count: int,
    l7_untrusted: list[str],
    runtime_proof_bundle_99_emitted: bool,
) -> str:
    from apps_rg.runtime.non_product_proof_stamp import (
        SECTION_L7_CORRELATION_CLASSIFICATION,
        SECTION_L7_CORRELATION_CLASSIFICATION_LEGACY,
    )

    if l7_untrusted:
        return "SECTION_MODULAR_L7_UNTRUSTED_ARTIFACTS_PRESENT"
    if integrated_l7_invoked and l7_trusted_count >= 3:
        return SECTION_L7_CORRELATION_CLASSIFICATION
    if l7_trusted_count >= 3:
        return SECTION_L7_CORRELATION_CLASSIFICATION_LEGACY
    if runtime_proof_bundle_99_emitted:
        return "SECTION_MODULAR_UNEXPECTED_99_ARTIFACT"
    return "SECTION_MODULAR_L7_BINDING_INCOMPLETE"


def build_section_l7_binding_manifest(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    command_surface: str = "python -m apps_rg --section <lane>",
    correlation: Any | None = None,
) -> dict[str, Any]:
    """Build binding manifest dict; does not write L7 artifacts."""
    artifact_dir = Path(artifact_dir)
    repo_root = Path(repo_root)

    l7_artifact_refs: dict[str, str | None] = {}
    l7_untrusted: list[dict[str, str]] = []
    artifact_classifications: dict[str, str] = {}
    design_law_owner: dict[str, str] = {}
    l7_emitted_flags = {
        "agentic_core_how_trace.json": False,
        "agentic_core_l7_route_family_coverage.json": False,
        "agentic_core_spine_proof.json": False,
    }

    for filename in L7_CORE_ARTIFACTS:
        path = artifact_dir / filename
        present = path.is_file()
        assessor = _L7_TRUST_ASSESSORS.get(filename)
        trusted = False
        reason = "absent"
        if present and assessor is not None:
            trusted, reason = assessor(_load_json(path))
        elif present:
            trusted, reason = False, "no_assessor"

        classification = classify_core_l7_artifact(filename, present=present, trusted=trusted)
        artifact_classifications[filename] = classification
        design_law_owner[filename] = design_law_owner_for_artifact(
            filename, legacy_class=classification, trusted=trusted, present=present
        )
        l7_artifact_refs[filename] = _repo_rel(repo_root, path)

        if present and not trusted:
            l7_untrusted.append({"artifact": filename, "reason": reason})
        if filename in l7_emitted_flags and present and trusted:
            l7_emitted_flags[filename] = True

    for filename in APPS_RG_DOMAIN_ARTIFACTS + APPS_RG_SHIM_ARTIFACTS:
        path = artifact_dir / filename
        legacy = _static_classification(filename)
        artifact_classifications[filename] = legacy
        design_law_owner[filename] = design_law_owner_for_artifact(
            filename, legacy_class=legacy, trusted=False, present=path.is_file()
        )
        if filename in APPS_RG_DOMAIN_ARTIFACTS:
            continue
        # shim refs collected below

    apps_rg_domain_refs = {
        name: _repo_rel(repo_root, artifact_dir / name) for name in APPS_RG_DOMAIN_ARTIFACTS
    }
    apps_rg_shim_refs = {
        name: _repo_rel(repo_root, artifact_dir / name) for name in APPS_RG_SHIM_ARTIFACTS
    }

    for filename in CORE_99_DESIGN_ONLY_ARTIFACTS:
        path = artifact_dir / filename
        present = path.is_file()
        artifact_classifications[filename] = CLASS_CORE_99_DESIGN_ONLY
        if present:
            artifact_classifications[filename] = CLASS_CORE_L7_UNTRUSTED
        design_law_owner[filename] = design_law_owner_for_artifact(
            filename,
            legacy_class=artifact_classifications[filename],
            trusted=False,
            present=present,
        )

    runtime_proof_bundle_99_emitted = False
    rpb = artifact_dir / "runtime_proof_bundle.json"
    if rpb.is_file():
        # No active 99 producer — any file is untrusted for 99 claims.
        artifact_classifications["runtime_proof_bundle.json"] = CLASS_CORE_L7_UNTRUSTED
        design_law_owner["runtime_proof_bundle.json"] = "DRIFT"
    else:
        artifact_classifications["runtime_proof_bundle.json"] = CLASS_CORE_99_DESIGN_ONLY
        design_law_owner["runtime_proof_bundle.json"] = "DESIGN_ONLY"

    from apps_rg.runtime.section_evidence_package import (
        IntegratedCorrelationResult,
        build_verified_external_refs_for_integrated,
        discover_integrated_correlation,
    )

    corr = correlation
    if corr is None:
        corr = discover_integrated_correlation(repo_root, artifact_dir, section_id=section_id)
    elif not isinstance(corr, IntegratedCorrelationResult):
        corr = IntegratedCorrelationResult(
            getattr(corr, "integrated_dir", None),
            getattr(corr, "correlation_method", None),
            getattr(corr, "correlation_missing_reason", None),
        )
    integrated_dir = corr.integrated_dir
    verified_external_refs = (
        build_verified_external_refs_for_integrated(
            repo_root, integrated_dir, section_artifact_dir=artifact_dir
        )
        if integrated_dir is not None
        else []
    )
    imported_core_evidence_snapshots: list[dict[str, Any]] = []
    for ref in verified_external_refs:
        fname = str(ref.get("artifact_name") or "")
        if fname in design_law_owner and design_law_owner[fname] in ("MISSING", "NOT_APPLICABLE"):
            design_law_owner[fname] = (
                "VERIFIED_EXTERNAL_REF"
                if ref.get("trust_status") == "trusted"
                else "DRIFT"
            )
            artifact_classifications[fname] = (
                "CORE_L7_REF" if ref.get("trust_status") == "trusted" else CLASS_CORE_L7_UNTRUSTED
            )
            l7_artifact_refs[fname] = ref.get("source_path")
            if fname in l7_emitted_flags and ref.get("trust_status") == "trusted":
                l7_emitted_flags[fname] = True

    missing_l7 = [
        name
        for name in DEFAULT_MISSING_L7_SURFACES
        if not l7_emitted_flags.get(name, False)
    ]
    missing_99 = list(DEFAULT_MISSING_99_SURFACES)
    if rpb.is_file():
        missing_99 = [n for n in missing_99 if n != "runtime_proof_bundle.json"]

    primary_l7 = (
        l7_emitted_flags["agentic_core_how_trace.json"]
        and l7_emitted_flags["agentic_core_l7_route_family_coverage.json"]
        and l7_emitted_flags["agentic_core_spine_proof.json"]
    )
    integrated_l7_invoked = primary_l7 and not l7_untrusted

    durable = _durable_write_evidence(artifact_dir)
    explicit_non_claims = list(DEFAULT_EXPLICIT_NON_CLAIMS)
    if not durable["durable_write_claim_allowed"]:
        explicit_non_claims.append(
            "this section run did not emit CommitRequest + durable UWG commit receipt; "
            "no durable UWG/L4 commit; semantic cache vector persistence not proven"
        )
    explicit_non_claims.append("apps_rg X2 is never 00C GateVerdict")
    explicit_non_claims.append("section_runtime_proof_bundle is never 99 RuntimeProofBundle")

    from apps_rg.runtime.shadow_product_path_quarantine import assess_shadow_product_shaped_artifacts

    shadow_q = assess_shadow_product_shaped_artifacts(artifact_dir, repo_root)
    for row in shadow_q.get("untrusted") or []:
        if isinstance(row, dict):
            l7_untrusted.append(
                {
                    "artifact": str(row.get("artifact") or ""),
                    "reason": str(row.get("reason") or "shadow_path"),
                }
            )
    if shadow_q.get("shadow_paths_present"):
        explicit_non_claims.extend(shadow_q.get("explicit_non_claims") or [])

    pc_impact = _product_certification_impact(artifact_dir)
    proof_class = _proof_classification(
        integrated_l7_invoked=integrated_l7_invoked,
        l7_trusted_count=sum(1 for v in l7_emitted_flags.values() if v),
        l7_untrusted=[u["artifact"] for u in l7_untrusted],
        runtime_proof_bundle_99_emitted=runtime_proof_bundle_99_emitted,
    )
    lane_proof_eligible: bool | None = None
    rm = _load_json(artifact_dir / "run_manifest.json")
    if isinstance(rm, dict) and "proof_eligible" in rm:
        lane_proof_eligible = bool(rm.get("proof_eligible"))
    l7_correlation = proof_class in {
        "SECTION_RUN_WITH_L7_CORRELATION_REFS_NOT_PRODUCT_PROOF",
        "SECTION_RUN_WITH_INTEGRATED_L7_REFS",
        "SECTION_DIR_CONTAINS_TRUSTED_L7_REFS",
    }

    design_law_owner[BINDING_MANIFEST_ARTIFACT] = "APP_BINDING_MANIFEST"

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _utc_now(),
        "producer": _CANONICAL_PRODUCER,
        "run_id": run_id,
        "section_id": section_id,
        "command_surface": command_surface,
        "integrated_run_ref": _repo_rel(repo_root, integrated_dir) if integrated_dir else None,
        "correlation_method": corr.correlation_method,
        "correlation_missing_reason": corr.correlation_missing_reason,
        "integrated_l7_invoked": integrated_l7_invoked,
        "l7_how_trace_emitted": l7_emitted_flags["agentic_core_how_trace.json"],
        "l7_route_family_coverage_emitted": l7_emitted_flags[
            "agentic_core_l7_route_family_coverage.json"
        ],
        "l7_spine_proof_emitted": l7_emitted_flags["agentic_core_spine_proof.json"],
        "runtime_proof_bundle_99_emitted": runtime_proof_bundle_99_emitted,
        "l7_artifact_refs": l7_artifact_refs,
        "apps_rg_domain_artifact_refs": apps_rg_domain_refs,
        "apps_rg_shim_artifact_refs": apps_rg_shim_refs,
        "artifact_classifications": artifact_classifications,
        "design_law_owner_classifications": design_law_owner,
        "verified_external_refs": verified_external_refs,
        "imported_core_evidence_snapshots": imported_core_evidence_snapshots,
        "l7_untrusted_artifacts": l7_untrusted,
        "missing_l7_surfaces": missing_l7,
        "missing_99_surfaces": missing_99,
        "durable_write_evidence": durable,
        "explicit_non_claims": explicit_non_claims,
        "product_certification_impact": pc_impact,
        "proof_classification": proof_class,
        "proof_classification_legacy": (
            "SECTION_RUN_WITH_INTEGRATED_L7_REFS"
            if proof_class == "SECTION_RUN_WITH_L7_CORRELATION_REFS_NOT_PRODUCT_PROOF"
            else proof_class
        ),
        "lane_proof_eligible": lane_proof_eligible,
        "section_l7_refs_are_correlation_only": bool(l7_correlation),
        "section_l7_refs_do_not_prove_spine_runtime": bool(l7_correlation),
        "shadow_path_quarantine": shadow_q,
        "shadow_paths_present": bool(shadow_q.get("shadow_paths_present")),
    }


def emit_section_l7_binding_manifest(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    command_surface: str = "python -m apps_rg --section <lane>",
) -> Path:
    """Write section_l7_binding_manifest.json under artifact_dir."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    doc = build_section_l7_binding_manifest(
        repo_root=repo_root,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        command_surface=command_surface,
    )
    out = artifact_dir / BINDING_MANIFEST_ARTIFACT
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


__all__ = [
    "BINDING_MANIFEST_ARTIFACT",
    "CLASS_APPS_RG_ADAPTER",
    "CLASS_APPS_RG_DOMAIN",
    "CLASS_APPS_RG_SHIM",
    "CLASS_CORE_99_DESIGN_ONLY",
    "CLASS_CORE_L7_MISSING",
    "CLASS_CORE_L7_REF",
    "CLASS_CORE_L7_UNTRUSTED",
    "CLASS_NOT_APPLICABLE",
    "SCHEMA_VERSION",
    "assess_l7_how_trace_trust",
    "assess_l7_spine_proof_trust",
    "build_section_l7_binding_manifest",
    "emit_section_l7_binding_manifest",
]
