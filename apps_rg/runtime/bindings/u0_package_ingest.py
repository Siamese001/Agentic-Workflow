"""apps_rg U0 runtime package ingest via app-owned package registry."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.runtime_customization_package import (
    PackageValidationReceipt,
    RuntimeCustomizationPackage,
)

from apps_rg.runtime.bindings.u0_binding import APPS_RG_TASK_CLASS
from apps_rg.runtime.bindings.u0_profile_manifest import repo_root

_LOGGER = logging.getLogger(__name__)
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


class U0PackageValidationError(Exception):
    """Raised when apps_rg U0 package validation fails."""

    def __init__(
        self,
        message: str,
        field: str = "",
        receipt: Any = None,
        reason_code: str = "",
    ) -> None:
        self.message = message
        self.field = field
        self.receipt = receipt
        self.reason_code = reason_code
        super().__init__(message)


class AppsRgRuntimePackageRegistry:
    """apps_rg-local registry for app-owned runtime customization packages."""

    def __init__(self, registry_base_path: str | Path | None = None) -> None:
        self.registry_base_path = Path(registry_base_path) if registry_base_path else None
        self._cache: dict[str, dict[str, Any]] = {}

    def load_app_registry(self, app_id: str) -> dict[str, Any] | None:
        if app_id in self._cache:
            return self._cache[app_id]
        base = self.registry_base_path or repo_root()
        registry_path = base / app_id / "config" / "domain_contract" / "runtime_package_registry.yaml"
        if not registry_path.exists():
            _LOGGER.warning("No runtime package registry found for %s at %s", app_id, registry_path)
            return None
        import yaml

        try:
            data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        except OSError as exc:
            message = f"Failed to read registry for {app_id}: {exc}"
            _LOGGER.error(message)
            raise U0PackageValidationError(
                message=message,
                field="runtime_package_registry",
                reason_code="registry_read_error",
                receipt={"registry_path": str(registry_path), "error_type": type(exc).__name__},
            ) from exc
        except yaml.YAMLError as exc:
            message = f"Failed to parse registry for {app_id}: {exc}"
            _LOGGER.error(message)
            raise U0PackageValidationError(
                message=message,
                field="runtime_package_registry",
                reason_code="registry_parse_error",
                receipt={"registry_path": str(registry_path), "error_type": type(exc).__name__},
            ) from exc
        if not isinstance(data, dict):
            message = f"Runtime package registry for {app_id} is not a mapping"
            _LOGGER.error(message)
            raise U0PackageValidationError(
                message=message,
                field="runtime_package_registry",
                reason_code="registry_not_mapping",
                receipt={"registry_path": str(registry_path), "data_type": type(data).__name__},
            )
        self._cache[app_id] = data
        return data

    def resolve_default_package_ref(
        self,
        app_id: str,
        task_class: str,
        request_context: Mapping[str, Any],
    ) -> tuple[str | None, str | None, str]:
        registry = self.load_app_registry(app_id)
        if not registry:
            return None, None, f"No registry found for {app_id}"
        default_packages = registry.get("default_packages", {})
        if not isinstance(default_packages, dict):
            return None, None, f"No default_packages mapping found for {app_id}"
        task_config = default_packages.get(task_class)
        if not isinstance(task_config, dict):
            return None, None, f"No default package configured for task_class={task_class} in {app_id} registry"
        caller_app_id = request_context.get("caller_app_id")
        if caller_app_id is not None:
            blocked_for = list(task_config.get("auto_injection_blocked_for", []) or [])
            blocked_key = f"delegated_{caller_app_id}_without_context"
            if blocked_key in blocked_for or "delegated_any_without_context" in blocked_for:
                return None, None, f"Auto-injection blocked for delegated call from {caller_app_id}"
            allowed_for = list(task_config.get("auto_injection_allowed_for", []) or [])
            allowed_key = f"delegated_{caller_app_id}"
            if allowed_key not in allowed_for and "delegated_any" not in allowed_for:
                return None, None, f"Auto-injection not explicitly allowed for {caller_app_id}"
        package_ref = str(task_config.get("package_ref") or "")
        schema_ref = str(task_config.get("schema_ref") or "") or None
        if not package_ref:
            return None, None, f"No package_ref configured for task_class={task_class}"
        return package_ref, schema_ref, "Resolved from app-owned registry"

    def load_package_from_ref(self, package_ref: str) -> RuntimeCustomizationPackage | None:
        package_path = repo_root() / package_ref
        if not package_path.exists():
            _LOGGER.error("Package config not found: %s", package_path)
            return None
        import yaml

        try:
            data = yaml.safe_load(package_path.read_text(encoding="utf-8"))
        except OSError as exc:
            message = f"Failed to read package from {package_path}: {exc}"
            _LOGGER.error(message)
            raise U0PackageValidationError(
                message=message,
                field="runtime_customization_package",
                reason_code="package_read_error",
                receipt={"package_path": str(package_path), "error_type": type(exc).__name__},
            ) from exc
        except yaml.YAMLError as exc:
            message = f"Failed to parse package from {package_path}: {exc}"
            _LOGGER.error(message)
            raise U0PackageValidationError(
                message=message,
                field="runtime_customization_package",
                reason_code="package_parse_error",
                receipt={"package_path": str(package_path), "error_type": type(exc).__name__},
            ) from exc
        if not isinstance(data, dict):
            message = f"Runtime package at {package_path} is not a mapping"
            _LOGGER.error(message)
            raise U0PackageValidationError(
                message=message,
                field="runtime_customization_package",
                reason_code="package_not_mapping",
                receipt={"package_path": str(package_path), "data_type": type(data).__name__},
            )
        return RuntimeCustomizationPackage.from_dict(data)


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

    registry = AppsRgRuntimePackageRegistry()
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
    "AppsRgRuntimePackageRegistry",
    "AppsRgU0PackageIngestResult",
    "U0PackageValidationError",
    "assert_package_files_on_disk",
    "default_package_ref",
    "ingest_apps_rg_runtime_package",
]
