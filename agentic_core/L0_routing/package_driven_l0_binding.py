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

from agentic_core.knowledge.retrieval import PromptEnvelope

# L0 ingress anchors for C0 + PA + L_PG (ADG G_REACH / J1 canonical pipeline wiring).
from agentic_core.L0_routing.c0_retrieval import run_c0
from agentic_core.L0_routing.reasoning.route_gates import check_d2_semantic_cache
from agentic_core.L1_cognition.package_driven_l1_binding import (  # guardian: allow-layer-violation -- L0 route evaluation consumes L1 PackageDrivenL1Plan from the package-driven pipeline; app-agnostic binding, no app-specific route logic
    PackageDrivenL1Plan,
)
from agentic_core.prompt_governance import (
    assemble_prompt,
    get_bundled_mixin,
    validate_apply_patch,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract

_LOGGER = logging.getLogger(__name__)

# Referenced by routing tests and ADG import graph (avoid "unused import" churn).
L0_C0_RUN_ENTRY = run_c0
L0_PA_ASSEMBLE_ENTRY = assemble_prompt
L0_PROMPT_ENVELOPE_TYPE = PromptEnvelope
L0_PROMPT_MIXIN_LOOKUP = get_bundled_mixin
L0_APPLY_PATCH_VALIDATE_ENTRY = validate_apply_patch


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

    # W1 (chroma-graphrag-core-wiring-gaps-b3f7a1): R1B semantic cache enrichment fields.
    # These carry the signal emitted by check_d2_semantic_cache() so Exit and audit
    # have full provenance without needing to re-query the cache.
    semantic_similarity_score: Optional[float] = None      # similarity from D2 hit dict
    semantic_threshold_used: Optional[float] = None        # namespace-resolved threshold
    semantic_namespace: str = ""                            # cache namespace
    cache_record_ref: str = ""                             # opaque key / record ref from hit
    cache_record_digest: str = ""                          # digest from hit dict if present
    semantic_profile_ref: str = ""                         # cache_profile_id that governed lookup
    compatibility_check_fields: List[str] = field(default_factory=list)  # from profile
    ret_type: str = ""                                     # always "SEMANTIC_CACHE_HIT" for R1B hits


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
    except Exception as e:  # guardian: allow-return-none-swallow -- P1 ADG burndown  # guardian: allow-broad-exception -- P1 ADG burndown
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
    except Exception:  # guardian: allow-return-none-swallow -- P1 ADG burndown  # guardian: allow-broad-exception -- P1 ADG burndown
        return None


def _read_semantic_cache_config(cache_profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Generic reader for the semantic cache configuration block.

    Handles two canonical profile shapes without any app_id branching:

    Shape A — nested block (apps_rg, apps_lic):
        semantic_cache:
          enabled: true|false
          namespace: "some.namespace.v1"
          similarity_threshold: 0.88
          compatibility_check_fields: [...]
          live_wiring_deferred: true|false

    Shape B — flat keys (apps_research legacy shape):
        semantic_cache_enabled: true|false
        similarity_threshold: 0.92
        # namespace absent — falls back to cache_profile_id
        # live_wiring_deferred absent — treated as false (live)

    Returns a normalised dict with keys:
        enabled              bool
        namespace            str   (never empty; falls back to cache_profile_id)
        similarity_threshold float
        compatibility_check_fields  list[str]
        live_wiring_deferred bool
        wiring_gate          str
        profile_id           str

    Returns a normalized config dict even when the profile is disabled.
    """
    profile: Dict[str, Any] = cache_profile if isinstance(cache_profile, dict) else {}
    profile_id: str = str(profile.get("cache_profile_id", ""))

    # Already-normalized config dicts may be passed in by callers that have
    # already parsed the profile shape. Preserve those values directly.
    if "enabled" in profile and "semantic_cache" not in profile and "semantic_cache_enabled" not in profile:
        return {
            "enabled": bool(profile.get("enabled", False)),
            "namespace": str(profile.get("namespace") or profile_id),
            "similarity_threshold": float(profile.get("similarity_threshold", 0.98)),
            "compatibility_check_fields": list(profile.get("compatibility_check_fields") or []),
            "live_wiring_deferred": bool(profile.get("live_wiring_deferred", False)),
            "wiring_gate": str(profile.get("wiring_gate", "")),
            "profile_id": profile_id,
        }

    # --- Shape A: nested semantic_cache block ---
    nested: Optional[Dict[str, Any]] = profile.get("semantic_cache")  # type: ignore[assignment]
    if isinstance(nested, dict):
        enabled: bool = bool(nested.get("enabled", False))
        live_wiring_deferred: bool = bool(nested.get("live_wiring_deferred", False))
        namespace: str = str(nested.get("namespace") or profile_id)
        threshold: float = float(nested.get("similarity_threshold", 0.98))
        compat_fields: List[str] = list(nested.get("compatibility_check_fields") or [])
        wiring_gate: str = str(nested.get("wiring_gate", ""))
        return {
            "enabled": enabled,
            "namespace": namespace,
            "similarity_threshold": threshold,
            "compatibility_check_fields": compat_fields,
            "live_wiring_deferred": live_wiring_deferred,
            "wiring_gate": wiring_gate,
            "profile_id": profile_id,
        }

    # --- Shape B: flat keys ---
    flat_enabled: bool = bool(profile.get("semantic_cache_enabled", False))
    flat_deferred: bool = bool(profile.get("live_wiring_deferred", False))
    flat_namespace: str = str(profile.get("namespace") or profile_id)
    flat_threshold: float = float(profile.get("similarity_threshold", 0.98))
    flat_compat: List[str] = list(profile.get("compatibility_check_fields") or [])
    return {
        "enabled": flat_enabled,
        "namespace": flat_namespace,
        "similarity_threshold": flat_threshold,
        "compatibility_check_fields": flat_compat,
        "live_wiring_deferred": flat_deferred,
        "wiring_gate": str(profile.get("wiring_gate", "")),
        "profile_id": profile_id,
    }


def _read_semantic_cache_profile(cache_profile: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return the normalized cache config when R1B live wiring is active."""
    cfg = _read_semantic_cache_config(cache_profile)
    if not cfg["enabled"]:
        return None
    if cfg["live_wiring_deferred"]:
        _LOGGER.debug(
            "_read_semantic_cache_profile: R1B live_wiring_deferred=true for profile=%s — skipping call",
            cfg["profile_id"],
        )
        return None
    return cfg


def _read_graph_traverse_policy(route_profile: Dict[str, Any]) -> Optional[GraphTraversePolicy]:
    """Generic reader for the graph_traverse block in an app route profile.

    Returns a GraphTraversePolicy built from the profile's ``graph_traverse:``
    block, or None if the block is absent.  No app_id branching — field names
    are fully generic.

    The returned policy is forwarded to C0 via RouteContract.graph_traverse_policy.
    L0 does NOT call run_graph_traverse().

    W2: chroma-graphrag-core-wiring-gaps-b3f7a1
    """
    gt: Optional[Dict[str, Any]] = route_profile.get("graph_traverse")  # type: ignore[assignment]
    if not isinstance(gt, dict):
        return None
    relation_types_raw = gt.get("allowed_relation_types") or []
    return GraphTraversePolicy(
        graph_expansion_allowed=bool(gt.get("graph_expansion_allowed", False)),
        max_hops=int(gt.get("max_hops", 0)),
        max_nodes=int(gt.get("max_nodes", 0)),
        max_edges=int(gt.get("max_edges", 0)),
        allowed_relation_types=tuple(relation_types_raw),
        contradiction_scan_enabled=bool(gt.get("contradiction_scan_enabled", False)),
        supersession_scan_enabled=bool(gt.get("supersession_scan_enabled", False)),
        graph_adapter_ref=str(gt.get("graph_adapter_ref", "")),
        live_wiring_deferred=bool(gt.get("live_wiring_deferred", True)),
        wiring_gate=str(gt.get("wiring_gate", "")),
    )


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
    
    semantic_cache_config = _read_semantic_cache_config(cache_profile)
    if not semantic_cache_config["enabled"]:
        return RouteEvaluation(
            route_id="R1B_SEMANTIC_CACHE",
            status=RouteStatus.INELIGIBLE,
            eligible=False,
            reason="Semantic cache disabled in profile",
            terminal=False,
            requires_cache_hit=False,
        )
    if semantic_cache_config["live_wiring_deferred"]:
        return RouteEvaluation(
            route_id="R1B_SEMANTIC_CACHE",
            status=RouteStatus.INELIGIBLE,
            eligible=False,
            reason="Semantic cache deferred in profile",
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
                # R5 is a terminal route — no C0 grounding, no graph policy.
                selected_route = RouteContract(
                    request_id=validated_request.request_id,
                    run_id=validated_request.run_id,
                    app_id=validated_request.app_id,
                    trace_id=validated_request.trace_id,
                    tenant_id=validated_request.tenant_id,
                    route_id="R5_PRE_ROUTE_FALLBACK",
                    l3_required=False,
                    grounding_required=False,
                    model_generation_required=False,
                    write_authority_present=False,
                    l5_certification_ref=getattr(validated_request, "l5_certification_ref", ""),
                    graph_traverse_policy=None,
                )
                break
        
        elif route_id == "R1A_EXACT_CACHE":
            eval_result = _check_r1a_exact_cache(validated_request, route_profile, cache_profile)
            evaluations.append(eval_result)
            
            if eval_result.eligible:
                # R1A is a cache/terminal route — no C0 grounding, no graph policy.
                selected_route = RouteContract(
                    request_id=validated_request.request_id,
                    run_id=validated_request.run_id,
                    app_id=validated_request.app_id,
                    trace_id=validated_request.trace_id,
                    tenant_id=validated_request.tenant_id,
                    route_id="R1A_EXACT_CACHE",
                    l3_required=False,
                    grounding_required=False,
                    model_generation_required=False,
                    write_authority_present=False,
                    l5_certification_ref=getattr(validated_request, "l5_certification_ref", ""),
                    graph_traverse_policy=None,
                )
                break
        
        elif route_id == "R1B_SEMANTIC_CACHE":
            eval_result = _check_r1b_semantic_cache(validated_request, route_profile, cache_profile)
            evaluations.append(eval_result)
            
            if eval_result.eligible:
                r1b_cfg = _read_semantic_cache_config(cache_profile)
                selected_route = _execute_r1b_semantic_cache_lookup(validated_request, r1b_cfg)
                if selected_route is not None:
                    break
        
        elif route_id == "R3_SIMPLE_GROUNDED_READ":
            eval_result = _check_r3_simple_grounded_read(validated_request, route_profile)
            evaluations.append(eval_result)
            
            if eval_result.eligible:
                # R3 is the default execution route — only C0-grounded routes
                # may carry an active graph policy.  Read it generically from
                # the route profile's graph_traverse block.
                # L0 does NOT call run_graph_traverse().
                graph_policy = _read_graph_traverse_policy(route_profile)
                selected_route = RouteContract(
                    request_id=validated_request.request_id,
                    run_id=validated_request.run_id,
                    app_id=validated_request.app_id,
                    trace_id=validated_request.trace_id,
                    tenant_id=validated_request.tenant_id,
                    route_id="R3_SIMPLE_GROUNDED_READ",
                    l3_required=route_profile.get("managed_workflow_allowed", False),
                    grounding_required=True,
                    model_generation_required=True,
                    write_authority_present=False,
                    l5_certification_ref=getattr(validated_request, "l5_certification_ref", ""),
                    graph_traverse_policy=graph_policy,
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


def _build_r1b_ret_packet(
    validated_request: "ValidatedRequest",
    d2_hit: Dict[str, Any],
    r1b_cfg: Dict[str, Any],
    hit_similarity: Optional[float],
) -> RETTerminalPacket:
    """Build a fully-populated RETTerminalPacket from a D2 semantic cache hit.

    Internal helper called exclusively from the R1B arm of
    ``l0_evaluate_routes_package_driven``.  All fields are populated from
    the generic profile config and the hit dict returned by
    ``check_d2_semantic_cache()`` — no app_id branching.
    """
    return RETTerminalPacket(
        route_id="R1B_SEMANTIC_CACHE",
        terminal_type="semantic_cache_hit",
        ret_type="SEMANTIC_CACHE_HIT",
        # Evidence from the cache hit dict
        evidence_digest=d2_hit.get("evidence_digest") or d2_hit.get("query_hash", ""),
        provenance_chain=d2_hit.get("provenance_chain") or [],
        compatibility_receipt_ref=d2_hit.get("receipt_ref", ""),
        compatibility_checks_passed=d2_hit.get("checks_passed") or {},
        substrate_namespace=r1b_cfg["namespace"],
        substrate_entry_ref=d2_hit.get("entry_ref") or d2_hit.get("cache_key", ""),
        is_final_customized_output=False,
        source_app_id=d2_hit.get("source_app_id", ""),
        request_id=validated_request.request_id,
        trace_id=validated_request.trace_id,
        timestamp_iso=d2_hit.get("timestamp", ""),
        exit_status="success",
        outcome_authorized=True,
        final_output=d2_hit.get("content") or d2_hit.get("response") or {},
        # W1 enrichment fields
        semantic_similarity_score=hit_similarity,
        semantic_threshold_used=r1b_cfg["similarity_threshold"],
        semantic_namespace=r1b_cfg["namespace"],
        cache_record_ref=d2_hit.get("cache_key") or d2_hit.get("entry_ref", ""),
        cache_record_digest=d2_hit.get("digest") or d2_hit.get("evidence_digest", ""),
        semantic_profile_ref=r1b_cfg["profile_id"],
        compatibility_check_fields=r1b_cfg["compatibility_check_fields"],
    )


def _execute_r1b_semantic_cache_lookup(
    validated_request: ValidatedRequest,
    cache_config: Optional[Dict[str, Any]],
) -> Optional[RETerminalPacket]:
    """Execute the generic R1B semantic cache lookup and return a RET packet on hit."""
    r1b_cfg = _read_semantic_cache_config(cache_config)
    if not r1b_cfg["enabled"] or r1b_cfg["live_wiring_deferred"]:
        return None

    namespace = r1b_cfg["namespace"]
    if not namespace:
        return None

    app_payload_for_cache: Dict[str, Any] = validated_request.app_payload or {}
    request_dict: Dict[str, Any] = {
        "task_class": validated_request.task_class,
        "app_id": validated_request.app_id,
        "payload": app_payload_for_cache,
    }
    d2_hit = check_d2_semantic_cache(
        request_dict,
        namespace=namespace,
        tenant_id=validated_request.tenant_id,
        similarity_threshold_override=r1b_cfg["similarity_threshold"],
    )
    if not d2_hit or not isinstance(d2_hit, dict):
        return None

    if d2_hit.get("support_status") != "PASS":
        return None

    hit_similarity: Optional[float] = (
        d2_hit.get("similarity")
        or d2_hit.get("similarity_score")
    )
    return _build_r1b_ret_packet(
        validated_request=validated_request,
        d2_hit=d2_hit,
        r1b_cfg=r1b_cfg,
        hit_similarity=hit_similarity,
    )


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
    "_read_semantic_cache_config",
    "_read_semantic_cache_profile",
    "_execute_r1b_semantic_cache_lookup",
    "L0_C0_RUN_ENTRY",
    "L0_PA_ASSEMBLE_ENTRY",
    "L0_PROMPT_ENVELOPE_TYPE",
]
