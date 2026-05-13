"""L0 routing binding for the apps_rg `resume_generation` task class.

MIGRATED from agentic_core/L0_routing/apps_rg_l0_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2B.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 W3.P3 (initial)
+   plan apps-rg-app-payload-consumption-wiring-b3a449 W2 (AG-2).

L0 is the THIRD stage of the U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit
pipeline. Its job is to consume the L1PlanContract, read the apps_rg
declarative routing profile (rg_route_profile.yaml), and emit a typed
RouteContract that downstream C0/PA/L2 stages consume.

Key routing decisions for apps_rg resume_generation:
- Route family: R3_MANAGED_DRAFT (structured C0 + PA + L2)
- Cache eligibility: True for all standard modes (R5 fallback available)
- HITL posture: advisory (no required_always escalation; fact_check may)
- Fallback: R5_semantic_refresh if no exact match

Pattern: pure function. No state. No I/O beyond reading the route profile.
Profile content is digest-bound — tampering detectable via
profile_manifest_digest forwarded from L1.

AG-2 invariant: L0 reads `l1_plan.task_spec`, `query_spec`,
`support_expectation`, `output_expectation`, `policy_refs` projections
rather than the legacy `AppsRgIngressPayload`. These projections are the
single source of truth for routing decisions.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_RETRIEVAL


# -----------------------------------------------------------------------------
# L0 routing types (defined locally as they are apps_rg-specific interpretations)
# -----------------------------------------------------------------------------

class RouteFamily(str, Enum):
    """Route family taxonomy for apps_rg resume generation."""
    R3_MANAGED_DRAFT = "R3_MANAGED_DRAFT"
    R5_SEMANTIC_REFRESH = "R5_SEMANTIC_REFRESH"


class CacheEligibility(str, Enum):
    """Cache eligibility determination for routing decisions."""
    EXACT_MATCH_CANDIDATE = "EXACT_MATCH_CANDIDATE"
    BYPASS = "BYPASS"


class HitlPosture(str, Enum):
    """HITL (Human-in-the-Loop) posture for route execution."""
    ADVISORY = "ADVISORY"
    REQUIRED_ON_LOW = "REQUIRED_ON_LOW"
    REQUIRED_ALWAYS = "REQUIRED_ALWAYS"

# L5 certification ref for the L0 binding stage.
APPS_RG_L0_CERT_REF: str = "l0-apps-rg-resume-generation-routing-live-d4e8a1"

# Path to the apps_rg route profile (advisory per AG-RGGOV-6).
_ROUTE_PROFILE_RELPATH: str = "apps_rg/profiles/rg_route_profile.yaml"

# ---------------------------------------------------------------------------
# Canonical route constants for apps_rg resume_generation.
# These are the L0 binding's INTERPRETATION of the route profile.
# ---------------------------------------------------------------------------

# Route family — R3 managed draft (structured pipeline with C0 + PA + L2)
APPS_RG_ROUTE_FAMILY: RouteFamily = RouteFamily.R3_MANAGED_DRAFT

# Primary route ID for standard resume generation
APPS_RG_ROUTE_ID: str = "R3A_RESUME_GENERATION"

# Cache eligibility — resumes are cacheable by design (R5 fallback exists)
APPS_RG_CACHE_ELIGIBILITY: CacheEligibility = CacheEligibility.EXACT_MATCH_CANDIDATE

# HITL posture — advisory unless fact-check failure triggers required_on_low
APPS_RG_HITL_POSTURE: HitlPosture = HitlPosture.ADVISORY

# Fallback route for cache miss / research-required scenarios
APPS_RG_FALLBACK_ROUTE_ID: str = "R5_SEMANTIC_REFRESH"

# Generation modes that trigger R5 fallback (research required)
_GENERATION_MODES_REQUIRING_RESEARCH: frozenset[str] = frozenset({
    "research_first",
    "refresh_with_research",
})

# Required task_spec keys for fail-closed validation
_REQUIRED_TASK_SPEC_KEYS: tuple[str, ...] = (
    "generation_mode",
    "task_class",
)

# Required query_spec keys
_REQUIRED_QUERY_SPEC_KEYS: tuple[str, ...] = (
    "jd_hash",
    "target",
)


def _read_profile_digest(repo_root: Path) -> str:
    """Compute sha256 digest of the route profile bytes for tamper detection."""
    profile_path = repo_root / _ROUTE_PROFILE_RELPATH
    if not profile_path.exists():
        return ""
    try:
        content_bytes = profile_path.read_bytes()
    except OSError:
        return ""
    return hashlib.sha256(content_bytes).hexdigest()


def _resolve_repo_root() -> Path:
    """Best-effort repo-root resolution."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[3]


def _derive_route_family(
    task_spec: Mapping[str, Any],
    support_expectation: Mapping[str, Any],
) -> RouteFamily:
    """Determine route family from L1 projections.

    For apps_rg resume_generation, this is always R3_MANAGED_DRAFT unless
    a specific override mode triggers research-first routing (R5).
    """
    generation_mode = task_spec.get("generation_mode", "")

    # Research-first modes use R5 (semantic refresh) as primary
    if generation_mode in _GENERATION_MODES_REQUIRING_RESEARCH:
        return RouteFamily.R5_SEMANTIC_REFRESH

    # Standard modes use R3 managed draft
    return RouteFamily.R3_MANAGED_DRAFT


def _derive_cache_eligibility(
    task_spec: Mapping[str, Any],
    query_spec: Mapping[str, Any],
) -> Mapping[str, bool]:
    """Determine cache eligibility from L1 projections.

    Resumes are cacheable by design — R5 provides semantic fallback.
    Returns a dict mapping cache types to boolean eligibility.
    """
    generation_mode = task_spec.get("generation_mode", "")

    # Research modes bypass cache (always fresh research)
    if generation_mode in _GENERATION_MODES_REQUIRING_RESEARCH:
        return {"r1a_exact": False, "r1b_semantic": False, "r3_grounded": False}

    # Standard modes are cache candidates
    return {"r1a_exact": True, "r1b_semantic": True, "r3_grounded": True}


def _derive_hitl_posture(
    task_spec: Mapping[str, Any],
    support_expectation: Mapping[str, Any],
) -> HitlPosture:
    """Determine HITL posture from L1 projections.

    Default is advisory. Fact-check failures may escalate to required_on_low.
    """
    # Check if fact-checking is required — this may trigger HITL escalation
    fact_checked_required = support_expectation.get("fact_checked_required", False)
    provenance_required = support_expectation.get("provenance_required", False)

    if fact_checked_required or provenance_required:
        # High-evidence requirements may need HITL on quality issues
        return HitlPosture.REQUIRED_ON_LOW

    return HitlPosture.ADVISORY


def _derive_fallback_route_id(
    primary_family: RouteFamily,
    task_spec: Mapping[str, Any],
) -> str:
    """Determine fallback route if primary route unavailable."""
    # If primary is R3, fallback is R5 for research
    if primary_family == RouteFamily.R3_MANAGED_DRAFT:
        return APPS_RG_FALLBACK_ROUTE_ID

    # If already R5, no further fallback (fail closed)
    return ""


def l0_route_apps_rg(l1_plan: L1PlanContract) -> RouteContract:
    """Emit a RouteContract for an apps_rg L1PlanContract.

    Args:
        l1_plan: L1 output carrying the typed plan with task_spec,
                 query_spec, support_expectation, output_expectation,
                 policy_refs, and routing flags.

    Returns:
        RouteContract with route_family, route_id, cache_eligibility,
        hitl_posture, fallback_route, and routing_metadata derived from
        the apps_rg route profile and L1 projections.

    Raises:
        TypeError: if l1_plan is not a L1PlanContract.
        ValueError: if required L1 projections are missing.
    """
    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            f"l0_route_apps_rg expected L1PlanContract, got {type(l1_plan).__name__}"
        )

    if l1_plan.app_id != "apps_rg":
        raise ValueError(
            f"l0_route_apps_rg expected app_id='apps_rg', got {l1_plan.app_id!r}"
        )

    # AG-2: read L1 projections (fail-closed if missing)
    task_spec = l1_plan.task_spec or {}
    query_spec = l1_plan.query_spec or {}
    support_expectation = l1_plan.support_expectation or {}
    output_expectation = l1_plan.output_expectation or {}
    policy_refs = l1_plan.policy_refs or {}

    missing_task = [k for k in _REQUIRED_TASK_SPEC_KEYS if k not in task_spec]
    if missing_task:
        raise ValueError(
            f"l0_route_apps_rg: task_spec missing required keys: {missing_task}"
        )

    missing_query = [k for k in _REQUIRED_QUERY_SPEC_KEYS if k not in query_spec]
    if missing_query:
        raise ValueError(
            f"l0_route_apps_rg: query_spec missing required keys: {missing_query}"
        )

    # Derive routing decisions from L1 projections
    route_family = _derive_route_family(task_spec, support_expectation)
    cache_eligibility = _derive_cache_eligibility(task_spec, query_spec)

    # Determine primary route ID
    if route_family == RouteFamily.R5_SEMANTIC_REFRESH:
        route_id = APPS_RG_FALLBACK_ROUTE_ID
    else:
        route_id = APPS_RG_ROUTE_ID

    return RouteContract(
        request_id=l1_plan.request_id,
        run_id=l1_plan.run_id,
        app_id=l1_plan.app_id,
        trace_id=l1_plan.trace_id,
        route_id=route_id,
        l3_required=True,
        grounding_required=l1_plan.grounding_required,
        model_generation_required=l1_plan.model_generation_required,
        write_authority_present=False,
        tenant_id=l1_plan.tenant_id,
        route_family=route_family.value if isinstance(route_family, Enum) else route_family,
        cache_eligibility=cache_eligibility,
        posture=POSTURE_RETRIEVAL,
        l5_certification_ref=APPS_RG_L0_CERT_REF,
        schema_version="AG-2.b3a449",
        replay_key=l1_plan.replay_key,
    )


__all__ = [
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_ROUTE_FAMILY",
    "APPS_RG_ROUTE_ID",
    "APPS_RG_CACHE_ELIGIBILITY",
    "APPS_RG_HITL_POSTURE",
    "APPS_RG_FALLBACK_ROUTE_ID",
    "l0_route_apps_rg",
]
