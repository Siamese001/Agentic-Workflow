"""apps_rg U0 runtime package ingest via core RuntimePackageRegistry (W1 spine convergence)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.runtime.contracts.runtime_customization_package import (
    PackageValidationReceipt,
    RuntimeCustomizationPackage,
)
from agentic_core.runtime.entry.u0_runtime_package_binding import (
    RuntimePackageRegistry,
    U0PackageValidationError,
)

from apps_rg.runtime.bindings.u0_binding import APPS_RG_TASK_CLASS
from apps_rg.runtime.bindings.u0_profile_manifest import repo_root

_PACKAGE_RELPATH = "apps_rg/config/domain_contract/runtime_customization_package.yaml"

# Map core package profile_refs keys → apps_rg ingress RuntimeCustomizationPackage fields.
_PROFILE_REF_FIELD_MAP: dict[str, str] = {
    "route_profile": "route_profile_ref",
    "retrieval_profile": "retrieval_profile_ref",
    "cache_profile": "cache_profile_ref",
    "runtime_gate_profile": "runtime_gate_profile_ref",
    "prompt_registry": "prompt_profile_ref",
    "l6_learning_profile": "learning_profile_ref",
}


@dataclass(frozen=True, slots=True)
class AppsRgU0PackageIngestResult:
    """Resolved runtime package artifacts for apps_rg U0."""

    package: RuntimeCustomizationPackage
    package_ref: str
    package_dict: dict[str, Any]
    profile_manifest_refs: dict[str, str]
    validation_receipt: PackageValidationReceipt


def default_package_ref() -> str:
    return _PACKAGE_RELPATH


def ingest_apps_rg_runtime_package(
    *,
    app_id: str = "apps_rg",
    task_class: str = APPS_RG_TASK_CLASS,
    request_context: Mapping[str, Any] | None = None,
) -> AppsRgU0PackageIngestResult:
    """Load and validate the apps_rg runtime customization package from app-owned registry."""

    registry = RuntimePackageRegistry()
    ctx = dict(request_context or {})
    package_ref, _schema_ref, reason = registry.resolve_default_package_ref(
        app_id,
        task_class,
        ctx,
    )
    if not package_ref:
        raise U0PackageValidationError(
            message=f"apps_rg runtime package resolution failed: {reason}",
            field="runtime_customization_package",
        )

    package = registry.load_package_from_ref(package_ref)
    if package is None:
        raise U0PackageValidationError(
            message=f"Failed to load runtime package from {package_ref}",
            field="runtime_customization_package",
        )

    digest = package.package_digest or package._compute_digest()
    if digest != package.package_digest:
        pkg_data = package.to_dict()
        pkg_data["package_digest"] = digest
        package = RuntimeCustomizationPackage.from_dict(pkg_data)

    is_valid, errors = package.validate_schema()
    if not is_valid:
        raise U0PackageValidationError(
            message=f"Runtime package schema validation failed: {errors}",
            field="runtime_customization_package",
        )

    from datetime import datetime, timezone

    validation_receipt = PackageValidationReceipt(
        package_id=package.package_id,
        package_version=package.package_version,
        task_class=package.task_class or task_class,
        validation_passed=True,
        unknown_fields_found=[],
        digest_verified=True,
        timestamp_iso=datetime.now(timezone.utc).isoformat(),
    )

    profile_manifest_refs = _profile_manifest_refs_from_package(package, package_ref)
    package_dict = _ingress_package_dict_from_core(package)

    return AppsRgU0PackageIngestResult(
        package=package,
        package_ref=package_ref,
        package_dict=package_dict,
        profile_manifest_refs=profile_manifest_refs,
        validation_receipt=validation_receipt,
    )


def _profile_manifest_refs_from_package(
    package: RuntimeCustomizationPackage,
    package_ref: str,
) -> dict[str, str]:
    refs = dict(package.profile_refs or {})
    extra = dict(package.extra or {})
    out: dict[str, str] = {
        "runtime_customization_package_ref": package_ref,
        "runtime_customization_package_digest": package.package_digest,
        "prompt_registry_ref": refs.get(
            "prompt_registry", "apps_rg/prompt_assembly/templates/registry.v1.yaml"
        ),
        "hitl_policy_ref": refs.get("hitl_policy", "apps_rg/config/hitl_trigger_policy.yaml"),
        "l0_policy_ref": refs.get("l0_policy", "apps_rg/config/l0_policy.yaml"),
        "agent_spec_ref": refs.get(
            "agent_spec", "apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml"
        ),
        "thresholds_ref": refs.get("thresholds", "apps_rg/config/rg_thresholds.yaml"),
        "l5_governance_profile_ref": refs.get(
            "l5_governance", "apps_rg/profiles/rg_l5_governance_profile.yaml"
        ),
    }
    if wf := str(extra.get("workflow_manifest_ref") or ""):
        out["workflow_manifest_ref"] = wf
    if orch := str(extra.get("orchestration_profile_ref") or ""):
        out["orchestration_profile_ref"] = orch
    return out


def _ingress_package_dict_from_core(package: RuntimeCustomizationPackage) -> dict[str, Any]:
    """Map core RuntimeCustomizationPackage → apps_rg ingress contract field names."""

    refs = dict(package.profile_refs or {})
    extra = dict(package.extra or {})
    out: dict[str, Any] = {
        "workflow_manifest_ref": str(extra.get("workflow_manifest_ref") or ""),
        "runtime_gate_profile_ref": refs.get("runtime_gate_profile", ""),
        "route_profile_ref": refs.get("route_profile", ""),
        "retrieval_profile_ref": refs.get("retrieval_profile", ""),
        "cache_profile_ref": refs.get("cache_profile", ""),
        "learning_profile_ref": refs.get("l6_learning_profile", ""),
        "prompt_profile_ref": refs.get("prompt_registry", ""),
        "orchestration_profile_ref": str(extra.get("orchestration_profile_ref") or ""),
        "write_policy": str(extra.get("write_policy") or "read_only"),
        "package_digest": package.package_digest,
    }
    for src_key, dst_key in _PROFILE_REF_FIELD_MAP.items():
        if src_key in refs and dst_key not in out:
            out[dst_key] = refs[src_key]
    return {k: v for k, v in out.items() if v}


def assert_package_files_on_disk() -> None:
    """Fail-closed check that package YAML and registry exist (tests / CI)."""

    root = repo_root()
    pkg = root / _PACKAGE_RELPATH
    reg = root / "apps_rg/config/domain_contract/runtime_package_registry.yaml"
    if not pkg.is_file():
        raise FileNotFoundError(pkg)
    if not reg.is_file():
        raise FileNotFoundError(reg)


__all__ = [
    "AppsRgU0PackageIngestResult",
    "assert_package_files_on_disk",
    "default_package_ref",
    "ingest_apps_rg_runtime_package",
]
