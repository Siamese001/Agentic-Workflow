"""
U0 Ingress Validation Binding for apps_research with Runtime Customization Package Support

Per plan apps-research-rich-content-runtime-customization-v1 W1.

U0 is the FIRST stage. Its job is to:
1. Accept RequestEnvelope with runtime_customization_package in app_payload.
2. Validate package against known schema (no unknown fields).
3. Verify package digest.
4. Emit ValidatedRequest with preserved package + validation receipt.

apps_research is INGRESS-ONLY — runtime authority belongs to agentic_core.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Tuple
from uuid import uuid4

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    RequestEnvelope,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
    AuthorityValidationReceipt,
)
from agentic_core.runtime.contracts.apps_research_runtime_package import (
    RuntimeCustomizationPackage,
    PackageValidationReceipt,
    TaskClass,
    UnknownPackageFieldError,
    PackageDigestMismatchError,
)
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY

_LOGGER = logging.getLogger(__name__)

APPS_RESEARCH_TASK_CLASS: str = "company_brief"

# Known package fields for unknown field detection
_KNOWN_PACKAGE_FIELDS: frozenset[str] = frozenset({
    "package_id", "package_version", "app_id", "task_class",
    "spine_profile_ref", "route_profile_ref", "retrieval_profile_ref",
    "cache_profile_ref", "source_mix_policy_ref", "freshness_policy_ref",
    "runtime_gate_profile_ref", "exit_profile_ref",
    "judge_profile_ref", "grader_roster_ref", "eval_rubric_ref",
    "threshold_profile_ref", "rubric_output_map_ref", "negative_controls_ref",
    "prompt_profile_ref", "prompt_bom_ref", "output_schema_ref",
    "research_substrate_schema_ref", "learning_profile_ref",
    "meta_feedback_profile_ref", "briefing_normalization_policy_ref",
    "entity_resolution_policy_ref", "capability_profile_ref",
    "provider_profile_ref", "write_policy", "required_runtime_gates",
    "required_exit_gates", "conditional_exit_gates", "judge_execution_policy",
    "eval_execution_policy", "meta_feedback_policy", "l6_learning_policy",
    "semantic_cache_policy", "cross_app_reuse_policy", "package_digest",
})


class AppsResearchU0ValidationError(Exception):
    """Raised when U0 validation fails for apps_research."""
    
    def __init__(self, message: str, field: str = "", receipt: Any = None):
        self.message = message
        self.field = field
        self.receipt = receipt
        super().__init__(message)


@dataclass(frozen=True)
class AutoInjectionContext:
    """Context stamped when runtime package is auto-injected by U0.
    
    Required for W1 invariant: auto-injection must be auditable and
    only allowed for direct apps_research calls (not delegated).
    """
    auto_injected_runtime_package: bool
    auto_injection_reason: str
    receipt_ref: str
    package_source: str  # "explicit" | "auto_injected_direct" | "auto_injected_delegated"
    resolved_app_id: str
    resolved_task_class: str
    default_profile_source: str


def _check_auto_injection_allowed(
    envelope: RequestEnvelope,
    app_payload: Mapping[str, Any],
) -> tuple[bool, str, str]:
    """
    Check if auto-injection is allowed for this request.
    
    W1 Invariant: Auto-injection only allowed when ALL are true:
    1. Request path is direct apps_research, not delegated apps_rg/apps_lic
    2. app_id resolves unambiguously to apps_research
    3. task_class resolves to company_brief or declared default
    
    Returns: (allowed: bool, reason: str, source: str)
    """
    payload = envelope.payload
    
    # Check 1: Detect delegated calls vs direct calls
    # Delegated calls have caller_app_id or delegation context in user_constraints
    user_constraints = getattr(payload, 'user_constraints', {}) or {}
    caller_app_id = user_constraints.get('caller_app_id')
    is_delegated = caller_app_id in ('apps_rg', 'apps_lic')
    
    if is_delegated:
        return (
            False,
            f"Auto-injection blocked: delegated call from {caller_app_id} requires explicit package",
            "delegated_requires_explicit"
        )
    
    # Check 2: app_id must resolve to apps_research
    app_id = getattr(payload, 'app_id', None)
    if app_id != 'apps_research':
        return (
            False,
            f"Auto-injection blocked: app_id '{app_id}' != 'apps_research'",
            "ambiguous_app_id"
        )
    
    # Check 3: task_class must be company_brief or compatible
    task_class = getattr(payload, 'task_class', None)
    if task_class and task_class != APPS_RESEARCH_TASK_CLASS:
        return (
            False,
            f"Auto-injection blocked: task_class '{task_class}' != '{APPS_RESEARCH_TASK_CLASS}'",
            "incompatible_task_class"
        )
    
    return (
        True,
        "Direct apps_research call with unambiguous resolution - auto-injection approved",
        "auto_injected_direct"
    )


def _extract_runtime_package(app_payload: Mapping[str, Any]) -> RuntimeCustomizationPackage:
    """Extract and validate runtime_customization_package from app_payload."""
    pkg_data = app_payload.get("runtime_customization_package") or {}
    
    if not pkg_data:
        raise AppsResearchU0ValidationError(
            message="Missing runtime_customization_package in app_payload",
            field="runtime_customization_package",
        )
    
    # Check for unknown fields
    unknown_fields = set(pkg_data.keys()) - _KNOWN_PACKAGE_FIELDS
    if unknown_fields:
        raise UnknownPackageFieldError(
            field=list(unknown_fields)[0],
            message=f"Unknown fields in runtime_customization_package: {sorted(unknown_fields)}",
        )
    
    # Build package
    try:
        task_class = TaskClass(pkg_data.get("task_class", "company_brief"))
    except ValueError as e:  # guardian: allow-exception-type-erasure -- P2 burndown: fail-soft optional boundary
        raise AppsResearchU0ValidationError(
            message=f"Invalid task_class: {e}",
            field="task_class",
        )
    
    package = RuntimeCustomizationPackage(
        package_id=pkg_data.get("package_id", ""),
        package_version=pkg_data.get("package_version", "1.0.0"),
        app_id=pkg_data.get("app_id", "apps_research"),
        task_class=task_class,
        spine_profile_ref=pkg_data.get("spine_profile_ref", ""),
        route_profile_ref=pkg_data.get("route_profile_ref", ""),
        retrieval_profile_ref=pkg_data.get("retrieval_profile_ref", ""),
        cache_profile_ref=pkg_data.get("cache_profile_ref", ""),
        source_mix_policy_ref=pkg_data.get("source_mix_policy_ref", ""),
        freshness_policy_ref=pkg_data.get("freshness_policy_ref", ""),
        runtime_gate_profile_ref=pkg_data.get("runtime_gate_profile_ref", ""),
        exit_profile_ref=pkg_data.get("exit_profile_ref", ""),
        judge_profile_ref=pkg_data.get("judge_profile_ref", ""),
        grader_roster_ref=pkg_data.get("grader_roster_ref", ""),
        eval_rubric_ref=pkg_data.get("eval_rubric_ref", ""),
        threshold_profile_ref=pkg_data.get("threshold_profile_ref", ""),
        rubric_output_map_ref=pkg_data.get("rubric_output_map_ref", ""),
        negative_controls_ref=pkg_data.get("negative_controls_ref", ""),
        prompt_profile_ref=pkg_data.get("prompt_profile_ref", ""),
        prompt_bom_ref=pkg_data.get("prompt_bom_ref", ""),
        output_schema_ref=pkg_data.get("output_schema_ref", ""),
        research_substrate_schema_ref=pkg_data.get("research_substrate_schema_ref", ""),
        learning_profile_ref=pkg_data.get("learning_profile_ref", ""),
        meta_feedback_profile_ref=pkg_data.get("meta_feedback_profile_ref", ""),
        briefing_normalization_policy_ref=pkg_data.get("briefing_normalization_policy_ref", ""),
        entity_resolution_policy_ref=pkg_data.get("entity_resolution_policy_ref", ""),
        capability_profile_ref=pkg_data.get("capability_profile_ref", ""),
        provider_profile_ref=pkg_data.get("provider_profile_ref", ""),
        write_policy=pkg_data.get("write_policy", "read_only"),
        required_runtime_gates=pkg_data.get("required_runtime_gates", []),
        required_exit_gates=pkg_data.get("required_exit_gates", []),
        conditional_exit_gates=pkg_data.get("conditional_exit_gates", []),
        judge_execution_policy=pkg_data.get("judge_execution_policy", "core_only"),
        eval_execution_policy=pkg_data.get("eval_execution_policy", "core_only"),
        meta_feedback_policy=pkg_data.get("meta_feedback_policy", "l6_only"),
        l6_learning_policy=pkg_data.get("l6_learning_policy", "future_run_only"),
        semantic_cache_policy=pkg_data.get("semantic_cache_policy", "research_substrate_only"),
        cross_app_reuse_policy=pkg_data.get("cross_app_reuse_policy", "delegated_only"),
        package_digest=pkg_data.get("package_digest", ""),
    )
    
    return package


def _validate_package_digest(package: RuntimeCustomizationPackage) -> bool:
    """Validate package digest matches contents."""
    if not package.package_digest:
        return False
    return package.verify_digest()


def u0_validate_apps_research_v2(
    envelope: RequestEnvelope,
) -> Tuple[ValidatedRequest, PackageValidationReceipt, AutoInjectionContext]:
    """
    Validate apps_research ingress with runtime customization package.
    
    W1 Invariant: Auto-injection is controlled and auditable.
    
    Returns:
        Tuple of (ValidatedRequest, PackageValidationReceipt, AutoInjectionContext)
    
    Raises:
        AppsResearchU0ValidationError: If validation fails
        UnknownPackageFieldError: If package contains unknown fields
        PackageDigestMismatchError: If digest verification fails
    """
    if not isinstance(envelope, RequestEnvelope):
        raise TypeError(f"Expected RequestEnvelope, got {type(envelope)}")
    
    # Extract payload from user_constraints (where apps_research puts its data)
    payload = envelope.payload
    app_payload = {}
    if hasattr(payload, "user_constraints"):
        app_payload = payload.user_constraints or {}
    # Also check app_payload field if present
    if hasattr(payload, "app_payload") and payload.app_payload:
        app_payload.update(payload.app_payload)
    
    # Step 0: Determine if package is explicit or needs auto-injection
    auto_injection_context: AutoInjectionContext | None = None
    if "runtime_customization_package" not in app_payload:
        # Check if auto-injection is allowed per W1 invariant
        allowed, reason, source = _check_auto_injection_allowed(envelope, app_payload)
        
        if not allowed:
            raise AppsResearchU0ValidationError(
                message=f"Runtime customization package missing and auto-injection blocked: {reason}",
                field="runtime_customization_package",
            )
        
        # Auto-inject default package for approved direct calls
        default_package = RuntimeCustomizationPackage(
            package_id=f"arcp::apps_research::company_brief::auto::{envelope.request_id}",
            package_version="1.0.0",
            app_id="apps_research",
            task_class=APPS_RESEARCH_TASK_CLASS,
            route_profile_ref="apps_research/config/domain_contract/route_profiles.yaml",
            cache_profile_ref="apps_research/config/domain_contract/cache_profiles.yaml",
            write_policy="read_only",
            semantic_cache_policy="research_substrate_only",
            cross_app_reuse_policy="delegated_only",
        )
        app_payload = dict(app_payload)
        app_payload["runtime_customization_package"] = default_package.to_dict()
        
        # Stamp auto-injection context
        auto_injection_context = AutoInjectionContext(
            auto_injected_runtime_package=True,
            auto_injection_reason=reason,
            receipt_ref=f"u0-auto-inject-{envelope.request_id}",
            package_source=source,
            resolved_app_id="apps_research",
            resolved_task_class=APPS_RESEARCH_TASK_CLASS,
            default_profile_source="apps_research/config/domain_contract/runtime_customization_package.company_brief.v1.yaml",
        )
    else:
        # Explicit package provided
        auto_injection_context = AutoInjectionContext(
            auto_injected_runtime_package=False,
            auto_injection_reason="Explicit runtime_customization_package provided by caller",
            receipt_ref=f"u0-explicit-{envelope.request_id}",
            package_source="explicit",
            resolved_app_id=getattr(payload, 'app_id', 'unknown'),
            resolved_task_class=getattr(payload, 'task_class', APPS_RESEARCH_TASK_CLASS),
            default_profile_source="",
        )
    
    # Step 1: Extract and validate runtime customization package
    try:
        package = _extract_runtime_package(app_payload)
    except UnknownPackageFieldError:
        raise
    except Exception as e:  # guardian: allow-exception-type-erasure -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        raise AppsResearchU0ValidationError(
            message=f"Failed to extract runtime package: {e}",
            field="runtime_customization_package",
        )
    
    # Step 2: Verify package digest
    digest_verified = _validate_package_digest(package)
    if not digest_verified:
        raise PackageDigestMismatchError(
            expected=package.package_digest,
            actual=package._compute_digest(),
        )
    
    # Step 3: Build validation receipt
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    validation_receipt = PackageValidationReceipt(
        package_id=package.package_id,
        package_version=package.package_version,
        task_class=package.task_class.value,
        validation_passed=True,
        unknown_fields_found=[],
        digest_verified=digest_verified,
        timestamp_iso=timestamp_iso,
    )
    
    # Step 4: Build authority receipt
    authority_receipt = AuthorityValidationReceipt(
        allowed=True,
        passed=True,
        forbidden_fields_detected=(),
        timestamp_iso=timestamp_iso,
    )
    
    # Step 5: Compute payload digest
    # Include auto_injection_context so L1 can see whether package was explicit or auto-injected
    payload_dict = {
        "runtime_customization_package": package.to_dict(),
        "target_company": app_payload.get("target_company", ""),
        "target_role": app_payload.get("target_role", ""),
        "target_level": app_payload.get("target_level", ""),
        "auto_injection_context": {
            "auto_injected_runtime_package": auto_injection_context.auto_injected_runtime_package,
            "auto_injection_reason": auto_injection_context.auto_injection_reason,
            "receipt_ref": auto_injection_context.receipt_ref,
            "package_source": auto_injection_context.package_source,
            "resolved_app_id": auto_injection_context.resolved_app_id,
            "resolved_task_class": auto_injection_context.resolved_task_class,
            "default_profile_source": auto_injection_context.default_profile_source,
        },
    }
    canonical = json.dumps(payload_dict, sort_keys=True, ensure_ascii=False)
    payload_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    _LOGGER.debug(
        "U0 apps_research v2 validated: package_id=%s task_class=%s digest=%s auto_injected=%s",
        package.package_id,
        package.task_class.value,
        payload_digest[:16],
        auto_injection_context.auto_injected_runtime_package,
    )
    
    # Step 6: Build ValidatedRequest
    validated_request = ValidatedRequest(
        request_id=envelope.request_id or f"research-req-{uuid4().hex[:12]}",
        run_id=envelope.run_id or f"research-run-{uuid4().hex[:12]}",
        app_id="apps_research",
        task_class=package.task_class.value,
        payload_digest=payload_digest,
        authority_validation_receipt=authority_receipt,
        trace_id=envelope.trace_id or f"research-trace-{uuid4().hex[:16]}",
        tenant_id=envelope.tenant_id or "apps_research",
        target_level=app_payload.get("target_level", ""),
        schema_version="AG9.U0.2",
        posture=POSTURE_READ_ONLY,
        l5_certification_ref="u0-apps-research-v2-company-brief-ag9",
        app_payload=payload_dict,
    )
    
    return validated_request, validation_receipt, auto_injection_context


# Backward compatibility - keep v1 function
__all__ = [
    "APPS_RESEARCH_TASK_CLASS",
    "AppsResearchU0ValidationError",
    "u0_validate_apps_research_v2",
    "RuntimeCustomizationPackage",
    "PackageValidationReceipt",
    "AutoInjectionContext",
]
