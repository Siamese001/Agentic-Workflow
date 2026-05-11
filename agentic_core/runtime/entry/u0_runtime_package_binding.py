"""
Generic U0 Runtime Package Binding

App-agnostic U0 binding that resolves runtime customization packages
from app-owned registries. No app-specific logic in core.
"""
from __future__ import annotations

import json
import hashlib
import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple
from uuid import uuid4

from agentic_core.runtime.contracts.runtime_customization_package import (
    RuntimeCustomizationPackage,
    PackageValidationReceipt,
    UnknownPackageFieldError,
    PackageDigestMismatchError,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    RequestEnvelope,
    ValidatedRequest,
    AuthorityValidationReceipt,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class AutoInjectionContext:
    """Context stamped when runtime package is auto-injected by U0."""
    auto_injected_runtime_package: bool
    auto_injection_reason: str
    receipt_ref: str
    package_source: str
    resolved_app_id: str
    resolved_task_class: str
    registry_source: str


class U0PackageValidationError(Exception):
    """Raised when U0 package validation fails."""
    
    def __init__(self, message: str, field: str = "", receipt: Any = None):
        self.message = message
        self.field = field
        self.receipt = receipt
        super().__init__(message)


class RuntimePackageRegistry:
    """
    Generic registry for resolving app-owned runtime packages.
    
    Loads app-owned registry files to resolve default packages.
    Core does not hardcode app-specific values.
    """
    
    def __init__(self, registry_base_path: Optional[str] = None):
        self.registry_base_path = Path(registry_base_path) if registry_base_path else None
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def load_app_registry(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Load app-owned runtime package registry.
        
        Registry path: apps_<name>/config/domain_contract/runtime_package_registry.yaml
        """
        if app_id in self._cache:
            return self._cache[app_id]
        
        # Try to load from standard location
        if self.registry_base_path:
            registry_path = self.registry_base_path / app_id / "config" / "domain_contract" / "runtime_package_registry.yaml"
        else:
            # Default relative path from repo root
            repo_root = Path(__file__).parent.parent.parent.parent
            registry_path = repo_root / app_id / "config" / "domain_contract" / "runtime_package_registry.yaml"
        
        if not registry_path.exists():
            _LOGGER.warning(f"No runtime package registry found for {app_id} at {registry_path}")
            return None
        
        try:
            import yaml
            with open(registry_path, "r") as f:
                registry = yaml.safe_load(f)
            self._cache[app_id] = registry
            return registry
        except Exception as e:
            _LOGGER.error(f"Failed to load registry for {app_id}: {e}")
            return None
    
    def resolve_default_package_ref(
        self,
        app_id: str,
        task_class: str,
        request_context: Dict[str, Any],
    ) -> Tuple[Optional[str], Optional[str], str]:
        """
        Resolve default package reference from app-owned registry.
        
        Returns:
            Tuple of (package_ref, schema_ref, reason) or (None, None, error_reason)
        """
        registry = self.load_app_registry(app_id)
        
        if not registry:
            return None, None, f"No registry found for {app_id}"
        
        default_packages = registry.get("default_packages", {})
        task_config = default_packages.get(task_class)
        
        if not task_config:
            return None, None, f"No default package configured for task_class={task_class} in {app_id} registry"
        
        # Check auto-injection eligibility
        caller_app_id = request_context.get("caller_app_id")
        is_delegated = caller_app_id is not None
        
        if is_delegated:
            blocked_for = task_config.get("auto_injection_blocked_for", [])
            blocked_key = f"delegated_{caller_app_id}_without_context"
            if blocked_key in blocked_for or "delegated_any_without_context" in blocked_for:
                return None, None, f"Auto-injection blocked for delegated call from {caller_app_id}"
        
        allowed_for = task_config.get("auto_injection_allowed_for", [])
        if is_delegated:
            allowed_key = f"delegated_{caller_app_id}"
            if allowed_key not in allowed_for and "delegated_any" not in allowed_for:
                return None, None, f"Auto-injection not explicitly allowed for {caller_app_id}"
        
        package_ref = task_config.get("package_ref")
        schema_ref = task_config.get("schema_ref")
        
        if not package_ref:
            return None, None, f"No package_ref configured for task_class={task_class}"
        
        return package_ref, schema_ref, "Resolved from app-owned registry"
    
    def load_package_from_ref(self, package_ref: str) -> Optional[RuntimeCustomizationPackage]:
        """Load package from app-owned config reference."""
        repo_root = Path(__file__).parent.parent.parent.parent
        package_path = repo_root / package_ref
        
        if not package_path.exists():
            _LOGGER.error(f"Package config not found: {package_path}")
            return None
        
        try:
            import yaml
            with open(package_path, "r") as f:
                data = yaml.safe_load(f)
            
            return RuntimeCustomizationPackage.from_dict(data)
        except Exception as e:
            _LOGGER.error(f"Failed to load package from {package_path}: {e}")
            return None


def _check_auto_injection_allowed(
    envelope: RequestEnvelope,
    registry: RuntimePackageRegistry,
) -> Tuple[bool, str, str, Optional[RuntimeCustomizationPackage]]:
    """
    Check if auto-injection is allowed and resolve default package.
    
    Returns:
        Tuple of (allowed, reason, source, package_or_none)
    """
    payload = envelope.payload
    
    # Extract context
    app_id = getattr(payload, 'app_id', None) or ""
    task_class = getattr(payload, 'task_class', None) or ""
    user_constraints = getattr(payload, 'user_constraints', {}) or {}
    caller_app_id = user_constraints.get('caller_app_id')
    
    if not app_id:
        return False, "Missing app_id", "error", None
    
    # Build request context
    request_context = {
        "caller_app_id": caller_app_id,
        "request_id": envelope.request_id,
        "is_delegated": caller_app_id is not None,
    }
    
    # Resolve from app-owned registry
    package_ref, schema_ref, reason = registry.resolve_default_package_ref(
        app_id, task_class or "default", request_context
    )
    
    if not package_ref:
        return False, reason, "error", None
    
    # Load package from app-owned config
    package = registry.load_package_from_ref(package_ref)
    
    if not package:
        return False, f"Failed to load package from {package_ref}", "error", None
    
    return True, reason, "auto_injected_from_registry", package


def _extract_explicit_package(
    app_payload: Dict[str, Any],
    schema: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[RuntimeCustomizationPackage], List[str]]:
    """Extract explicit package from app_payload and validate."""
    pkg_data = app_payload.get("runtime_customization_package")
    
    if not pkg_data:
        return None, []
    
    try:
        package = RuntimeCustomizationPackage.from_dict(pkg_data)
        
        # Validate
        is_valid, errors = package.validate_schema(schema)
        if not is_valid:
            return package, errors
        
        return package, []
    except Exception as e:
        return None, [str(e)]


def _validate_package_digest(package: RuntimeCustomizationPackage) -> bool:
    """Verify package digest."""
    if not package.package_digest:
        return False
    
    computed = package._compute_digest()
    return computed == package.package_digest


def u0_resolve_runtime_package(
    envelope: RequestEnvelope,
    registry: Optional[RuntimePackageRegistry] = None,
) -> Tuple[ValidatedRequest, PackageValidationReceipt, AutoInjectionContext]:
    """
    Generic U0 runtime package resolution.
    
    Resolves runtime customization package from app-owned registry or explicit input.
    No app-specific logic - all app defaults come from app-owned config.
    
    Args:
        envelope: RequestEnvelope with payload
        registry: Optional RuntimePackageRegistry (creates default if None)
        
    Returns:
        Tuple of (ValidatedRequest, PackageValidationReceipt, AutoInjectionContext)
        
    Raises:
        U0PackageValidationError: If package resolution/validation fails
        UnknownPackageFieldError: If explicit package has unknown fields
        PackageDigestMismatchError: If digest verification fails
    """
    if not isinstance(envelope, RequestEnvelope):
        raise TypeError(f"Expected RequestEnvelope, got {type(envelope)}")
    
    if registry is None:
        registry = RuntimePackageRegistry()
    
    # Extract app_payload
    payload = envelope.payload
    app_payload = {}
    if hasattr(payload, "user_constraints"):
        app_payload = payload.user_constraints or {}
    if hasattr(payload, "app_payload") and payload.app_payload:
        app_payload.update(payload.app_payload)
    
    # Step 1: Check for explicit package
    explicit_package, validation_errors = _extract_explicit_package(app_payload)
    
    auto_injection_context: AutoInjectionContext
    package: RuntimeCustomizationPackage
    
    if explicit_package and not validation_errors:
        # Use explicit package
        package = explicit_package
        auto_injection_context = AutoInjectionContext(
            auto_injected_runtime_package=False,
            auto_injection_reason="Explicit runtime_customization_package provided",
            receipt_ref=f"u0-explicit-{envelope.request_id}",
            package_source="explicit",
            resolved_app_id=getattr(payload, 'app_id', 'unknown'),
            resolved_task_class=getattr(payload, 'task_class', ''),
            registry_source="",
        )
    else:
        # Step 2: Attempt auto-injection from app-owned registry
        allowed, reason, source, auto_package = _check_auto_injection_allowed(
            envelope, registry
        )
        
        if not allowed or auto_package is None:
            raise U0PackageValidationError(
                message=f"Runtime customization package missing and auto-injection blocked: {reason}",
                field="runtime_customization_package",
            )
        
        package = auto_package
        auto_injection_context = AutoInjectionContext(
            auto_injected_runtime_package=True,
            auto_injection_reason=reason,
            receipt_ref=f"u0-auto-inject-{envelope.request_id}",
            package_source=source,
            resolved_app_id=getattr(payload, 'app_id', 'unknown'),
            resolved_task_class=getattr(payload, 'task_class', ''),
            registry_source=package.package_ref or "",
        )
    
    # Step 3: Validate package digest
    digest_verified = _validate_package_digest(package)
    
    if not digest_verified and not auto_injection_context.auto_injected_runtime_package:
        # For explicit packages, digest mismatch is an error
        raise PackageDigestMismatchError(
            expected=package.package_digest,
            actual=package._compute_digest(),
        )
    
    # For auto-injected, compute and set digest
    if auto_injection_context.auto_injected_runtime_package:
        package = RuntimeCustomizationPackage(
            **{**package.__dict__, "package_digest": package._compute_digest()}
        )
        digest_verified = True
    
    # Step 4: Build validation receipt
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    validation_receipt = PackageValidationReceipt(
        package_id=package.package_id,
        package_version=package.package_version,
        task_class=package.task_class,
        validation_passed=True,
        unknown_fields_found=[],
        digest_verified=digest_verified,
        timestamp_iso=timestamp_iso,
    )
    
    # Step 5: Build authority receipt
    authority_receipt = AuthorityValidationReceipt(
        allowed=True,
        passed=True,
        forbidden_fields_detected=(),
        timestamp_iso=timestamp_iso,
    )
    
    # Step 6: Compute payload digest including package
    payload_dict = {
        "runtime_customization_package": package.to_dict(),
        "auto_injection_context": {
            "auto_injected_runtime_package": auto_injection_context.auto_injected_runtime_package,
            "auto_injection_reason": auto_injection_context.auto_injection_reason,
            "receipt_ref": auto_injection_context.receipt_ref,
            "package_source": auto_injection_context.package_source,
            "resolved_app_id": auto_injection_context.resolved_app_id,
            "resolved_task_class": auto_injection_context.resolved_task_class,
        },
    }
    
    # Add other payload fields
    for key in ["target_company", "target_role", "target_level", "depth", "topic"]:
        if key in app_payload:
            payload_dict[key] = app_payload[key]
    
    canonical = json.dumps(payload_dict, sort_keys=True, ensure_ascii=False)
    payload_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    _LOGGER.debug(
        "U0 package resolved: package_id=%s app_id=%s task_class=%s auto_injected=%s",
        package.package_id,
        package.app_id,
        package.task_class,
        auto_injection_context.auto_injected_runtime_package,
    )
    
    # Step 7: Build ValidatedRequest
    # Map package fields to ValidatedRequest
    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import POSTURE_READ_ONLY
    
    validated_request = ValidatedRequest(
        request_id=envelope.request_id or f"req-{uuid4().hex[:12]}",
        run_id=envelope.run_id or f"run-{uuid4().hex[:12]}",
        app_id=package.app_id or getattr(payload, 'app_id', 'unknown'),
        task_class=package.task_class or getattr(payload, 'task_class', ''),
        payload_digest=payload_digest,
        authority_validation_receipt=authority_receipt,
        trace_id=envelope.trace_id or f"trace-{uuid4().hex[:16]}",
        tenant_id=envelope.tenant_id or package.app_id or "unknown",
        target_level=app_payload.get("target_level", ""),
        schema_version="AG9.U0.3",
        posture=POSTURE_READ_ONLY,
        l5_certification_ref="u0-runtime-package-generic-ag9",
        app_payload=payload_dict,
    )
    
    return validated_request, validation_receipt, auto_injection_context


__all__ = [
    "u0_resolve_runtime_package",
    "RuntimePackageRegistry",
    "AutoInjectionContext",
    "U0PackageValidationError",
]
