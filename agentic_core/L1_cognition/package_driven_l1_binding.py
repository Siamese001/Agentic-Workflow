"""
Generic Package-Driven L1 Binding

App-agnostic L1 binding that emits planning hints from app-owned config.
No app-specific logic in core.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

try:
    import yaml
except ImportError:
    yaml = None

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract as BaseL1PlanContract

_LOGGER = logging.getLogger(__name__)


class HintSource(Enum):
    """Source of planning hints."""
    APP_CONFIG = "app_config"
    PAYLOAD = "payload"
    PACKAGE_REF = "package_ref"
    DEFAULT = "default"


@dataclass(frozen=True)
class AppHint:
    """Single planning hint from app config."""
    hint_name: str
    hint_value: Any
    hint_source: str
    confidence: str = "high"


@dataclass(frozen=True)
class PackageDrivenL1Plan:
    """L1 planning output driven by app-owned package config."""
    
    # Core identity
    request_id: str
    run_id: str
    app_id: str
    task_class: str
    tenant_id: str
    
    # Planning hints (from app config, not hardcoded)
    app_hints: List[AppHint]
    
    # Package refs consumed
    runtime_package_ref: str
    l1_planning_profile_ref: str
    
    # Authority boundary (always false for L1)
    has_runtime_authority: bool = False
    
    # Metadata
    trace_id: str = ""
    schema_version: str = "AG9.L1.PKG.1"


def _load_l1_planning_profile(profile_ref: str) -> Optional[Dict[str, Any]]:
    """Load L1 planning profile from app-owned config."""
    if not yaml:
        _LOGGER.error("PyYAML not available, cannot load L1 planning profile")
        return None
    
    repo_root = Path(__file__).parent.parent.parent.parent
    profile_path = repo_root / profile_ref
    
    if not profile_path.exists():
        _LOGGER.warning(f"L1 planning profile not found: {profile_path}")
        return None
    
    try:
        with open(profile_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:  # guardian: allow-return-none-swallow -- P1 ADG burndown  # guardian: allow-broad-exception -- P1 ADG burndown
        _LOGGER.error(f"Failed to load L1 planning profile {profile_path}: {e}")
        return None


def _extract_hint_from_profile(
    hint_name: str,
    profile: Dict[str, Any],
    payload: Dict[str, Any],
    package: Dict[str, Any],
) -> Optional[AppHint]:
    """
    Extract a single hint from profile, payload, or package.
    
    Priority: payload > package > profile > None
    """
    # Check payload first
    if hint_name in payload:
        return AppHint(
            hint_name=hint_name,
            hint_value=payload[hint_name],
            hint_source="payload",
        )
    
    # Check package refs
    if hint_name == "runtime_package_origin_hint":
        origin = "explicit"
        if package.get("auto_injected_runtime_package"):
            origin = "auto_injected"
        return AppHint(
            hint_name=hint_name,
            hint_value=origin,
            hint_source="package",
        )
    
    # Check profile
    # Map hint names to profile sections
    profile_mapping = {
        "source_scope_hint": ("source_scope", "default_sources"),
        "freshness_profile_hint": ("freshness_profile", "default_window"),
        "coverage_family_hint": ("coverage_family", "default"),
        "cache_lookup_candidate_hint": ("cache_hints", "r1a_exact_cache_candidate"),
        "semantic_cache_candidate_hint": ("cache_hints", "r1b_semantic_cache_candidate"),
        "semantic_cache_policy_hint": ("cache_hints", "semantic_cache_policy"),
        "grounding_required_hint": ("execution_hints", "grounding_required"),
        "prompt_assembly_required_hint": ("execution_hints", "prompt_assembly_required"),
        "writeback_candidate_hint": ("execution_hints", "writeback_candidate"),
        "cross_app_reuse_candidate_hint": ("delegation_hints", "cross_app_reuse_candidate"),
        "reuse_policy_hint": ("delegation_hints", "reuse_policy"),
        "uploaded_briefing_present_hint": ("context_hints", "uploaded_briefing_present"),
        "jd_context_present_hint": ("context_hints", "jd_context_present"),
        "role_context_present_hint": ("context_hints", "role_context_present"),
        "hitl_required_for_ambiguous": ("hitl_hints", "required_for_ambiguous_entities"),
        "entity_ambiguity_risk_hint": ("risk_hints", "entity_ambiguity_risk"),
    }
    
    if hint_name in profile_mapping:
        section, key = profile_mapping[hint_name]
        if section in profile and key in profile[section]:
            return AppHint(
                hint_name=hint_name,
                hint_value=profile[section][key],
                hint_source="app_config",
            )
    
    return None


def l1_plan_package_driven(
    validated_request: ValidatedRequest,
    l1_planning_profile_ref: Optional[str] = None,
) -> PackageDrivenL1Plan:
    """
    Generic L1 planning that emits hints from app-owned config.
    
    Consumes:
        - ValidatedRequest with app_payload.runtime_customization_package
        - Optional L1 planning profile ref (from package or payload)
    
    Emits:
        - PackageDrivenL1Plan with hints from app config (not hardcoded)
    
    No app-specific logic - all values come from app-owned config.
    """
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(f"Expected ValidatedRequest, got {type(validated_request)}")
    
    # Extract app_payload and package
    app_payload = validated_request.app_payload or {}
    package = app_payload.get("runtime_customization_package", {})
    
    # Resolve L1 planning profile ref
    if l1_planning_profile_ref is None:
        # Try to get from package extra fields
        l1_planning_profile_ref = package.get("extra", {}).get("l1_planning_profile_ref")
    
    if l1_planning_profile_ref is None:
        # Try to construct from app_id and task_class
        app_id = validated_request.app_id
        task_class = validated_request.task_class
        if app_id and task_class:
            l1_planning_profile_ref = f"{app_id}/config/domain_contract/l1_planning_profile.{task_class}.v1.yaml"
    
    # Load L1 planning profile from app-owned config
    profile = _load_l1_planning_profile(l1_planning_profile_ref) if l1_planning_profile_ref else {}
    
    # Build hints list
    hints: List[AppHint] = []
    
    # Core hints always present
    hints.append(AppHint(
        hint_name="task_class_hint",
        hint_value=validated_request.task_class,
        hint_source="validated_request",
    ))
    
    hints.append(AppHint(
        hint_name="company_entity_hint",
        hint_value=app_payload.get("target_company", ""),
        hint_source="payload",
    ))
    
    hints.append(AppHint(
        hint_name="depth_profile_hint",
        hint_value=app_payload.get("depth", "standard"),
        hint_source="payload",
    ))
    
    # Runtime package origin
    origin_hint = _extract_hint_from_profile(
        "runtime_package_origin_hint", profile, app_payload, package
    )
    if origin_hint:
        hints.append(origin_hint)
    
    # Source scope hint
    source_hint = _extract_hint_from_profile(
        "source_scope_hint", profile, app_payload, package
    )
    if source_hint:
        hints.append(source_hint)
    
    # Freshness profile hint
    freshness_hint = _extract_hint_from_profile(
        "freshness_profile_hint", profile, app_payload, package
    )
    if freshness_hint:
        hints.append(freshness_hint)
    
    # Coverage family hint
    coverage_hint = _extract_hint_from_profile(
        "coverage_family_hint", profile, app_payload, package
    )
    if coverage_hint:
        hints.append(coverage_hint)
    
    # Cache hints
    for hint_name in [
        "cache_lookup_candidate_hint",
        "semantic_cache_candidate_hint",
        "semantic_cache_policy_hint",
    ]:
        cache_hint = _extract_hint_from_profile(hint_name, profile, app_payload, package)
        if cache_hint:
            hints.append(cache_hint)
    
    # Execution hints
    for hint_name in [
        "grounding_required_hint",
        "prompt_assembly_required_hint",
        "writeback_candidate_hint",
    ]:
        exec_hint = _extract_hint_from_profile(hint_name, profile, app_payload, package)
        if exec_hint:
            hints.append(exec_hint)
    
    # Delegation hints
    caller_app_id = app_payload.get("auto_injection_context", {}).get("resolved_app_id")
    if caller_app_id and caller_app_id != validated_request.app_id:
        hints.append(AppHint(
            hint_name="downstream_consumer_hint",
            hint_value="delegated",
            hint_source="auto_injection_context",
        ))
        hints.append(AppHint(
            hint_name="caller_app_id_hint",
            hint_value=caller_app_id,
            hint_source="auto_injection_context",
        ))
    else:
        hints.append(AppHint(
            hint_name="downstream_consumer_hint",
            hint_value="direct",
            hint_source="auto_injection_context",
        ))
    
    cross_reuse = _extract_hint_from_profile(
        "cross_app_reuse_candidate_hint", profile, app_payload, package
    )
    if cross_reuse:
        hints.append(cross_reuse)
    
    # Context hints
    for hint_name in [
        "uploaded_briefing_present_hint",
        "jd_context_present_hint",
        "role_context_present_hint",
    ]:
        ctx_hint = _extract_hint_from_profile(hint_name, profile, app_payload, package)
        if ctx_hint:
            hints.append(ctx_hint)
    
    # HITL hint
    hitl_hint = _extract_hint_from_profile(
        "hitl_required_for_ambiguous", profile, app_payload, package
    )
    if hitl_hint:
        hints.append(AppHint(
            hint_name="hitl_hint",
            hint_value=hitl_hint.hint_value,
            hint_source=hitl_hint.hint_source,
        ))
    
    # Risk hint
    entity_ambiguity = not app_payload.get("target_company")
    hints.append(AppHint(
        hint_name="risk_hint",
        hint_value={
            "entity_ambiguity": entity_ambiguity,
            "auto_injected": package.get("auto_injected_runtime_package", False),
        },
        hint_source="computed",
    ))
    
    _LOGGER.debug(
        "L1 package-driven plan: app_id=%s task_class=%s hints_count=%d profile_ref=%s",
        validated_request.app_id,
        validated_request.task_class,
        len(hints),
        l1_planning_profile_ref or "none",
    )
    
    return PackageDrivenL1Plan(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        task_class=validated_request.task_class,
        tenant_id=validated_request.tenant_id,
        app_hints=hints,
        runtime_package_ref=package.get("package_ref", ""),
        l1_planning_profile_ref=l1_planning_profile_ref or "",
        has_runtime_authority=False,
        trace_id=validated_request.trace_id,
        schema_version="AG9.L1.PKG.1",
    )


def l1_plan_to_contract(l1_plan: PackageDrivenL1Plan) -> BaseL1PlanContract:
    """Convert package-driven plan to standard L1PlanContract."""
    # Build hints dict
    hints_dict = {
        hint.hint_name: hint.hint_value
        for hint in l1_plan.app_hints
    }
    
    return BaseL1PlanContract(
        request_id=l1_plan.request_id,
        run_id=l1_plan.run_id,
        app_id=l1_plan.app_id,
        task_class=l1_plan.task_class,
        tenant_id=l1_plan.tenant_id,
        app_hints=hints_dict,
        target_level="",
        trace_id=l1_plan.trace_id,
    )


__all__ = [
    "l1_plan_package_driven",
    "l1_plan_to_contract",
    "PackageDrivenL1Plan",
    "AppHint",
]
