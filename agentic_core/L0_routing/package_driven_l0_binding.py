"""
Generic Package-Driven L0 Routing Binding

App-agnostic L0 binding that evaluates routes from app-owned RouteProfile.
No app-specific route logic in core.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import yaml
except ImportError:
    yaml = None

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.L1_cognition.package_driven_l1_binding import PackageDrivenL1Plan

_LOGGER = logging.getLogger(__name__)


class RouteStatus(Enum):
    """Route evaluation status."""
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    TERMINAL = "terminal"
    REQUIRES_CACHE_HIT = "requires_cache_hit"


@dataclass(frozen=True)
class RETTerminalPacket:
    """
    Rich Evidence Terminal packet for cache-hit terminal routes.
    
    R1A and R1B routes emit this to Exit, never direct to user.
    """
    route_id: str  # R1A_EXACT_CACHE or R1B_SEMANTIC_CACHE
    terminal_type: str  # "exact_cache_hit" or "semantic_cache_hit"
    
    # Evidence contract
    evidence_digest: str
    provenance_chain: List[Dict[str, Any]]
    
    # Compatibility verification
    compatibility_receipt_ref: str
    compatibility_checks_passed: Dict[str, bool]
    
    # Research substrate info
    substrate_namespace: str
    substrate_entry_ref: str
    
    # Never reuse final customized outputs
    is_final_customized_output: bool = False
    source_app_id: str = ""
    
    # Metadata
    request_id: str = ""
    trace_id: str = ""
    timestamp_iso: str = ""
    
    # X3 disposition fields
    exit_status: str = "success"
    outcome_authorized: bool = True
    final_output: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RouteEvaluation:
    """Result of evaluating a single route."""
    route_id: str
    status: RouteStatus
    eligible: bool
    reason: str
    terminal: bool
    requires_cache_hit: bool
    cache_compatibility_receipt: Optional[Dict[str, Any]] = None


def _load_route_profile(profile_ref: str) -> Optional[Dict[str, Any]]:
    """Load route profile from app-owned config."""
    if not yaml:
        _LOGGER.error("PyYAML not available")
        return None
    
    repo_root = Path(__file__).parent.parent.parent.parent
    profile_path = repo_root / profile_ref
    
    if not profile_path.exists():
        _LOGGER.warning(f"Route profile not found: {profile_path}")
        return None
    
    try:
        with open(profile_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        _LOGGER.error(f"Failed to load route profile {profile_path}: {e}")
        return None


def _load_cache_profile(profile_ref: str) -> Optional[Dict[str, Any]]:
    """Load cache profile from app-owned config."""
    if not yaml:
        return None
    
    repo_root = Path(__file__).parent.parent.parent.parent
    profile_path = repo_root / profile_ref
    
    if not profile_path.exists():
        return None
    
    try:
        with open(profile_path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _check_r5_preroute_fallback(
    validated_request: ValidatedRequest,
    route_profile: Dict[str, Any],
) -> RouteEvaluation:
    """
    Check R5 pre-route fallback conditions.
    
    Returns INELIGIBLE if request is fundamentally unroutable.
    """
    app_payload = validated_request.app_payload or {}
    
    # Check for missing target_company
    target_company = app_payload.get("target_company", "")
    if not target_company:
        return RouteEvaluation(
            route_id="R5_PRE_ROUTE_FALLBACK",
            status=RouteStatus.TERMINAL,
            eligible=True,
            reason="Missing target_company - request is unroutable",
            terminal=True,
            requires_cache_hit=False,
        )
    
    # Check for high entity ambiguity (from L1 hints)
    auto_ctx = app_payload.get("auto_injection_context", {})
    risk_hint = app_payload.get("risk_hint", {})
    if risk_hint.get("entity_ambiguity", False):
        return RouteEvaluation(
            route_id="R5_PRE_ROUTE_FALLBACK",
            status=RouteStatus.TERMINAL,
            eligible=True,
            reason="High entity ambiguity - request requires HITL",
            terminal=True,
            requires_cache_hit=False,
        )
    
    # Request is routable
    return RouteEvaluation(
        route_id="R5_PRE_ROUTE_FALLBACK",
        status=RouteStatus.INELIGIBLE,
        eligible=False,
        reason="Request is routable - proceeding to cache checks",
        terminal=False,
        requires_cache_hit=False,
    )


def _check_r1a_exact_cache(
    validated_request: ValidatedRequest,
    route_profile: Dict[str, Any],
    cache_profile: Optional[Dict[str, Any]],
) -> RouteEvaluation:
    """
    Check R1A exact cache eligibility.
    
    Always eligible for lookup, but requires cache hit to be terminal.
    """
    # R1A is always a candidate for exact cache lookup
    # Actual cache hit check happens in L2 (if route selected)
    return RouteEvaluation(
        route_id="R1A_EXACT_CACHE",
        status=RouteStatus.ELIGIBLE,
        eligible=True,
        reason="Exact cache lookup candidate",
        terminal=False,  # Only terminal if cache hit found
        requires_cache_hit=True,
    )


def _check_r1b_semantic_cache(
    validated_request: ValidatedRequest,
    route_profile: Dict[str, Any],
    cache_profile: Optional[Dict[str, Any]],
) -> RouteEvaluation:
    """
    Check R1B semantic cache eligibility with full compatibility verification.
    
    Requires all compatibility checks from route_profile to pass.
    """
    if not cache_profile:
        return RouteEvaluation(
            route_id="R1B_SEMANTIC_CACHE",
            status=RouteStatus.INELIGIBLE,
            eligible=False,
            reason="No cache profile available",
            terminal=False,
            requires_cache_hit=False,
        )
    
    # Get R1B config from route profile
    r1b_config = None
    for route in route_profile.get("route_evaluation_order", []):
        if route.get("route_id") == "R1B_SEMANTIC_CACHE":
            r1b_config = route
            break
    
    if not r1b_config:
        return RouteEvaluation(
            route_id="R1B_SEMANTIC_CACHE",
            status=RouteStatus.INELIGIBLE,
            eligible=False,
            reason="R1B not in route evaluation order",
            terminal=False,
            requires_cache_hit=False,
        )
    
    # Get compatibility requirements
    compat_reqs = r1b_config.get("compatibility_requirements", {})
    
    # Build compatibility checks (these would be evaluated by actual cache lookup)
    # For route selection, we only check if R1B is configured and enabled
    semantic_cache_config = cache_profile.get("semantic_cache", {})
    if not semantic_cache_config.get("enabled", False):
        return RouteEvaluation(
            route_id="R1B_SEMANTIC_CACHE",
            status=RouteStatus.INELIGIBLE,
            eligible=False,
            reason="Semantic cache disabled in profile",
            terminal=False,
            requires_cache_hit=False,
        )
    
    # R1B is eligible for evaluation
    # Full compatibility verification happens at cache lookup time
    return RouteEvaluation(
        route_id="R1B_SEMANTIC_CACHE",
        status=RouteStatus.ELIGIBLE,
        eligible=True,
        reason="Semantic cache eligible - requires full compatibility verification",
        terminal=False,  # Only terminal with RET packet on cache hit
        requires_cache_hit=True,
    )


def _check_r3_simple_grounded_read(
    validated_request: ValidatedRequest,
    route_profile: Dict[str, Any],
) -> RouteEvaluation:
    """
    Check R3 simple grounded read eligibility.
    
    Default route requiring C0 grounding.
    """
    app_payload = validated_request.app_payload or {}
    target_company = app_payload.get("target_company", "")
    
    if not target_company:
        return RouteEvaluation(
            route_id="R3_SIMPLE_GROUNDED_READ",
            status=RouteStatus.INELIGIBLE,
            eligible=False,
            reason="Missing target_company for grounded read",
            terminal=False,
            requires_cache_hit=False,
        )
    
    # Check managed_workflow_allowed from profile
    managed_workflow_allowed = route_profile.get("managed_workflow_allowed", False)
    if managed_workflow_allowed:
        _LOGGER.warning("managed_workflow_allowed=true in profile but apps_research uses SINGLE_STEP")
    
    return RouteEvaluation(
        route_id="R3_SIMPLE_GROUNDED_READ",
        status=RouteStatus.ELIGIBLE,
        eligible=True,
        reason="Default grounded read route - requires C0 grounding",
        terminal=False,
        requires_cache_hit=False,
    )


def l0_evaluate_routes_package_driven(
    validated_request: ValidatedRequest,
    l1_plan: Optional[PackageDrivenL1Plan] = None,
) -> Tuple[Union[RouteContract, RETTerminalPacket], List[RouteEvaluation]]:
    """
    Generic L0 route evaluation consuming app-owned route profile.
    
    Evaluates routes in order from route_profile.route_evaluation_order:
    1. R5: Pre-route fallback (unroutable check)
    2. R1A: Exact cache lookup
    3. R1B: Semantic cache lookup (with full compatibility)
    4. R3: Simple grounded read (default)
    
    Returns:
        Tuple of (selected_route_or_ret_packet, evaluation_log)
    
    Emits exactly one RouteContract or RETTerminalPacket.
    """
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(f"Expected ValidatedRequest, got {type(validated_request)}")
    
    # Extract package refs from ValidatedRequest
    app_payload = validated_request.app_payload or {}
    package = app_payload.get("runtime_customization_package", {})
    
    route_profile_ref = package.get("profile_refs", {}).get("route_profile")
    cache_profile_ref = package.get("profile_refs", {}).get("cache_profile")
    
    if not route_profile_ref:
        raise ValueError("No route_profile_ref in runtime_customization_package")
    
    # Load app-owned profiles
    route_profile = _load_route_profile(route_profile_ref)
    if not route_profile:
        raise ValueError(f"Failed to load route profile: {route_profile_ref}")
    
    cache_profile = _load_cache_profile(cache_profile_ref) if cache_profile_ref else None
    
    # Evaluate routes in order
    evaluations: List[RouteEvaluation] = []
    selected_route: Optional[Union[RouteContract, RETTerminalPacket]] = None
    
    # Get evaluation order from profile
    eval_order = route_profile.get("route_evaluation_order", [])
    
    for route_def in eval_order:
        route_id = route_def.get("route_id", "")
        
        if route_id == "R5_PRE_ROUTE_FALLBACK":
            eval_result = _check_r5_preroute_fallback(validated_request, route_profile)
            evaluations.append(eval_result)
            
            if eval_result.terminal and eval_result.eligible:
                # Request is unroutable - emit terminal RouteContract
                selected_route = RouteContract(
                    request_id=validated_request.request_id,
                    run_id=validated_request.run_id,
                    app_id=validated_request.app_id,
                    task_class=validated_request.task_class,
                    tenant_id=validated_request.tenant_id,
                    route_id="R5_PRE_ROUTE_FALLBACK",
                    route_type="TERMINAL",
                    terminal_reason=eval_result.reason,
                    trace_id=validated_request.trace_id,
                )
                break
        
        elif route_id == "R1A_EXACT_CACHE":
            eval_result = _check_r1a_exact_cache(validated_request, route_profile, cache_profile)
            evaluations.append(eval_result)
            
            if eval_result.eligible:
                # R1A is selected for cache lookup
                # Actual cache hit check happens in L2
                # For L0, we emit RouteContract for R1A
                selected_route = RouteContract(
                    request_id=validated_request.request_id,
                    run_id=validated_request.run_id,
                    app_id=validated_request.app_id,
                    task_class=validated_request.task_class,
                    tenant_id=validated_request.tenant_id,
                    route_id="R1A_EXACT_CACHE",
                    route_type="CACHE_LOOKUP",
                    requires_cache_hit=True,
                    cache_type="exact",
                    trace_id=validated_request.trace_id,
                )
                # Note: R1A evaluation continues - if cache miss, we'll try R1B then R3
                # For now, we select R1A as the route
                break
        
        elif route_id == "R1B_SEMANTIC_CACHE":
            eval_result = _check_r1b_semantic_cache(validated_request, route_profile, cache_profile)
            evaluations.append(eval_result)
            
            if eval_result.eligible:
                # R1B is selected for semantic cache lookup
                selected_route = RouteContract(
                    request_id=validated_request.request_id,
                    run_id=validated_request.run_id,
                    app_id=validated_request.app_id,
                    task_class=validated_request.task_class,
                    tenant_id=validated_request.tenant_id,
                    route_id="R1B_SEMANTIC_CACHE",
                    route_type="CACHE_LOOKUP",
                    requires_cache_hit=True,
                    cache_type="semantic",
                    semantic_compatibility_required=True,
                    trace_id=validated_request.trace_id,
                )
                break
        
        elif route_id == "R3_SIMPLE_GROUNDED_READ":
            eval_result = _check_r3_simple_grounded_read(validated_request, route_profile)
            evaluations.append(eval_result)
            
            if eval_result.eligible:
                # R3 is the default execution route
                selected_route = RouteContract(
                    request_id=validated_request.request_id,
                    run_id=validated_request.run_id,
                    app_id=validated_request.app_id,
                    task_class=validated_request.task_class,
                    tenant_id=validated_request.tenant_id,
                    route_id="R3_SIMPLE_GROUNDED_READ",
                    route_type="EXECUTION",
                    requires_grounding=True,
                    execution_form=route_profile.get("active_execution_form", "SINGLE_STEP"),
                    managed_workflow_allowed=route_profile.get("managed_workflow_allowed", False),
                    trace_id=validated_request.trace_id,
                )
                break
    
    if selected_route is None:
        # No route selected - should not happen if profile is valid
        raise RuntimeError("No route selected - invalid route profile configuration")
    
    _LOGGER.debug(
        "L0 route selected: route_id=%s type=%s for app=%s task=%s",
        selected_route.route_id if hasattr(selected_route, 'route_id') else 'RET',
        type(selected_route).__name__,
        validated_request.app_id,
        validated_request.task_class,
    )
    
    return selected_route, evaluations


def emit_r1b_ret_terminal_packet(
    route_contract: RouteContract,
    cache_entry: Dict[str, Any],
    compatibility_receipt: Dict[str, Any],
) -> RETTerminalPacket:
    """
    Emit RET terminal packet for R1B semantic cache hit.
    
    This packet goes to Exit, never directly to user.
    """
    return RETTerminalPacket(
        route_id="R1B_SEMANTIC_CACHE",
        terminal_type="semantic_cache_hit",
        evidence_digest=cache_entry.get("evidence_digest", ""),
        provenance_chain=cache_entry.get("provenance_chain", []),
        compatibility_receipt_ref=compatibility_receipt.get("receipt_ref", ""),
        compatibility_checks_passed=compatibility_receipt.get("checks_passed", {}),
        substrate_namespace=cache_entry.get("substrate_namespace", ""),
        substrate_entry_ref=cache_entry.get("entry_ref", ""),
        is_final_customized_output=False,  # Never reuse final customized outputs
        source_app_id=cache_entry.get("source_app_id", ""),
        request_id=route_contract.request_id,
        trace_id=route_contract.trace_id,
        timestamp_iso=cache_entry.get("timestamp", ""),
        exit_status="success",
        outcome_authorized=True,
        final_output=cache_entry.get("content", {}),
    )


__all__ = [
    "l0_evaluate_routes_package_driven",
    "emit_r1b_ret_terminal_packet",
    "RETTerminalPacket",
    "RouteEvaluation",
    "RouteStatus",
]
