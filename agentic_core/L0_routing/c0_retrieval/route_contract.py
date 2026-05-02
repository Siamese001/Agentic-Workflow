"""C0 INPUT CONTRACT — RouteContract from L0 + L1PlanContract.

Spec lines 116-130 (RouteContract fields) and lines 147-153 (preflight inputs).
RouteContract is L0's command to C0; L1PlanContract carries the user task/query.
Both are immutable inputs into C0 — C0 never mutates either.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .verdicts import FreshnessClass, SourceClass, SupportTarget


@dataclass(frozen=True)
class L1PlanContract:
    """L1 reasoning output that flows into C0 via L0."""

    task_spec: str
    query_spec: str
    grounding_required: bool = True
    user_task_text: str = ""
    """Raw user-typed text — must be classified as DATA, never instruction."""

    def __post_init__(self) -> None:
        if not isinstance(self.task_spec, str):
            raise TypeError("task_spec must be str")
        if not isinstance(self.query_spec, str):
            raise TypeError("query_spec must be str")


@dataclass(frozen=True)
class RouteContract:
    """L0's deterministic instruction to C0.

    Every field comes directly from the spec C0 INPUT CONTRACT block (lines 116-130).
    """

    route_id: str
    grounding_required: bool
    execution_form: str  # "SINGLE_STEP" | "MANAGED_WORKFLOW_STEP"
    freshness_class: FreshnessClass
    support_target: SupportTarget
    tenant_scope: str
    region: str = ""
    data_class: str = "internal"
    acl_roles: tuple[str, ...] = ()
    max_k: int = 20
    max_hops: int = 1
    max_parent_expansion: int = 2
    max_child_expansion: int = 2
    max_refine_attempts: int = 1
    max_token_context: int = 4000
    max_source_classes: int = 7
    max_latency_ms: int = 5000
    max_cost_tier: str = "standard"
    latency_slo: int = 5000
    token_budget: int = 4000
    allowed_sources: tuple[SourceClass, ...] = ()
    disallowed_sources: tuple[SourceClass, ...] = ()
    allowed_data_classes: tuple[str, ...] = ("public", "internal")
    fallback_policy: str = "caveat"  # caveat | abstain | R5 | reroute
    route_replay_key: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""
    origin_trust_manifest: Mapping[str, str] = field(default_factory=dict)
    hmac_sig: str = ""
    """Optional HMAC signature minted by L0 v15 selector. Empty when route
    was constructed without v15 signing (e.g. proof harness, direct caller).
    Downstream verifiers MUST treat empty as 'unsigned' and apply the
    appropriate policy."""

    # ----- Fort Knox app-domain contract refs (plan apps-domain-contract-fortknox-c4d8e2) -----
    # All optional and default-empty so existing callers are untouched. When
    # populated (by agentic_core/L0_routing/app_domain_resolver.py) they bind
    # the route to a specific apps_* domain contract resolved from L4.
    app_id: str = ""
    task_class: str = ""
    domain_contract_ref: str = ""
    domain_contract_digest: str = ""
    rubric_ref: str = ""
    threshold_profile_ref: str = ""
    grader_roster_ref: str = ""
    retrieval_profile_ref: str = ""
    prompt_profile_ref: str = ""
    capability_profile_ref: str = ""
    route_profile_ref: str = ""
    input_contract_ref: str = ""
    output_schema_ref: str = ""
    orchestration_profile_ref: str = ""
    app_contract_l4_record_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.max_k <= 0:
            raise ValueError("max_k must be positive")
        if self.max_hops < 0:
            raise ValueError("max_hops must be >= 0")
        if self.max_refine_attempts < 0:
            raise ValueError("max_refine_attempts must be >= 0")
        if self.max_token_context <= 0:
            raise ValueError("max_token_context must be positive")
        if self.execution_form not in ("SINGLE_STEP", "MANAGED_WORKFLOW_STEP"):
            raise ValueError(f"invalid execution_form: {self.execution_form}")
        if self.fallback_policy not in ("caveat", "abstain", "R5", "reroute"):
            raise ValueError(f"invalid fallback_policy: {self.fallback_policy}")

    def allows_source(self, sc: SourceClass) -> bool:
        if sc in self.disallowed_sources:
            return False
        if self.allowed_sources and sc not in self.allowed_sources:
            return False
        return True

    def allows_data_class(self, dc: str) -> bool:
        return dc in self.allowed_data_classes
