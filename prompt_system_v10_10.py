# FILE: 10_10/prompt_system_v10_10.py
"""
Prompt Registry & Governance (v10_10 · Phase 2)
===============================================

This module is the **single source of truth** for all prompts in v10_10.

It provides:

    • PromptVersion & PromptDefinition registry (G24–G25).
    • Prompt ACL governance via PromptACL + PromptActorRole (G26).
    • Envelope-style templates with deterministic section markers
      (CONTEXT / INSTRUCTIONS / OUTPUT_FORMAT) (G27).
    • ContextBudget hooks via metadata only (no token counting yet) (G28).
    • Diff + validation utilities for CI / regression checks.
    • A small helper for building prompt payloads for PromptInstance
      construction (used indirectly by L2 via prompt_builder.py).

Phase 2 clarifications:
    • L2/L3/L5 must **only** obtain prompts via get_prompt(...) here.
    • No inline prompt strings in cognitive_agents, l2, or L3/L5.
    • ACLs are enforced consistently via PromptACL + per-prompt metadata.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

from pydantic import BaseModel, Field

from models import PromptDefinition, PromptVersion


# ============================================================================
# ACTOR ROLES & ACL
# ============================================================================


class PromptActorRole(str, Enum):
    """
    Logical actors that may interact with the prompt registry.

    This is deliberately small and stable – new capabilities should be
    expressed via metadata, not new roles.
    """

    ENGINE = "engine"   # runtime engine / L2 cognition
    ADMIN = "admin"     # maintenance / DevOps
    EDITOR = "editor"   # prompt engineer
    VIEWER = "viewer"   # read-only


class PromptACL(BaseModel):
    """
    Simple role-based ACL for a single prompt ID.
    """

    id: str
    engine_can_use: bool = True
    admins_can_edit: bool = True
    editors_can_edit: bool = False
    viewers_can_read: bool = True


# Global in-memory registries.
PROMPT_REGISTRY: Dict[str, PromptDefinition] = {}
PROMPT_ACLS: Dict[str, PromptACL] = {}


# ============================================================================
# CORE REGISTRY OPERATIONS
# ============================================================================


def _check_acl(prompt_id: str, actor_role: PromptActorRole, use_case: str) -> None:
    """
    Internal ACL check.

    use_case ∈ {"read", "edit", "use"}.
    """

    acl = PROMPT_ACLS.get(prompt_id)
    if acl is None:
        # Default: engine + admins may use/edit; viewers read-only.
        acl = PromptACL(id=prompt_id)
        PROMPT_ACLS[prompt_id] = acl

    if use_case == "read":
        if actor_role == PromptActorRole.ENGINE:
            return
        if actor_role == PromptActorRole.ADMIN:
            return
        if actor_role == PromptActorRole.EDITOR and acl.viewers_can_read:
            return
        if actor_role == PromptActorRole.VIEWER and acl.viewers_can_read:
            return
        raise PermissionError(f"Role {actor_role} cannot read prompt {prompt_id}")

    if use_case == "edit":
        if actor_role == PromptActorRole.ADMIN and acl.admins_can_edit:
            return
        if actor_role == PromptActorRole.EDITOR and acl.editors_can_edit:
            return
        raise PermissionError(f"Role {actor_role} cannot edit prompt {prompt_id}")

    if use_case == "use":
        if actor_role == PromptActorRole.ENGINE and acl.engine_can_use:
            return
        if actor_role == PromptActorRole.ADMIN and acl.admins_can_edit:
            # Admins may also drive execution in tooling contexts.
            return
        raise PermissionError(f"Role {actor_role} cannot use prompt {prompt_id}")

    raise ValueError(f"Unknown use_case: {use_case}")


def register_prompt(defn: PromptDefinition, acl: Optional[PromptACL] = None) -> None:
    """
    Register or update a prompt definition in the global registry.

    Side-effects:
        • PROMPT_REGISTRY[defn.id] is updated.
        • PROMPT_ACLS[defn.id] is set if acl given or not present.
    """
    PROMPT_REGISTRY[defn.id] = defn
    if acl is not None:
        PROMPT_ACLS[defn.id] = acl
    elif defn.id not in PROMPT_ACLS:
        PROMPT_ACLS[defn.id] = PromptACL(id=defn.id)


def get_prompt(
    prompt_id: str,
    actor_role: PromptActorRole = PromptActorRole.ENGINE,
) -> PromptDefinition:
    """
    Retrieve a prompt by ID, enforcing ACL for the caller's role.

    All runtime / engine access should go through this function.
    """
    if prompt_id not in PROMPT_REGISTRY:
        raise KeyError(f"Unknown prompt id: {prompt_id}")

    _check_acl(prompt_id, actor_role, use_case="read")
    return PROMPT_REGISTRY[prompt_id]


def list_prompts(
    role: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    role_type: Optional[str] = None,
) -> List[PromptDefinition]:
    """
    List prompt definitions, optionally filtered by:
        • role_type – "system", "user", etc.
        • tags      – any of the prompt's tags.

    The `role` parameter is reserved for future multi-tenant ACL filtering.
    """

    tags_set = set(tags or [])
    results: List[PromptDefinition] = []

    for pd in PROMPT_REGISTRY.values():
        if role_type is not None and pd.role != role_type:
            continue
        if tags_set and not tags_set.intersection(pd.tags):
            continue
        results.append(pd)

    return results


# ============================================================================
# DIFF & VALIDATION UTILITIES
# ============================================================================


class PromptDiff(BaseModel):
    """
    Structured diff between two prompt versions.

    Enough for:
        • CI checks (breaking vs non-breaking changes).
        • Human review of behavioral risk.
    """

    id: str
    from_version: PromptVersion
    to_version: PromptVersion
    template_changed: bool
    metadata_changed: bool
    tags_changed: bool


SECTION_MARKERS_DEFAULT = [
    "## CONTEXT",
    "## INSTRUCTIONS",
    "## OUTPUT_FORMAT",
]


class SectionValidationResult(BaseModel):
    """
    Result of template section validation.

    For Phase 2 we check:
        • presence of configured markers
        • strict ordering of these markers
    """

    ok: bool
    missing_markers: List[str] = Field(default_factory=list)
    out_of_order: bool = False


def validate_sections(
    template: str,
    required_markers: Optional[List[str]] = None,
) -> SectionValidationResult:
    """
    Validate that a prompt template contains required section markers in
    the expected order. This is the structural guard for envelope prompts.
    """
    markers = required_markers or SECTION_MARKERS_DEFAULT

    missing: List[str] = [m for m in markers if m not in template]
    if missing:
        return SectionValidationResult(ok=False, missing_markers=missing, out_of_order=False)

    # Check order.
    last_index = -1
    out_of_order = False
    for m in markers:
        idx = template.index(m)
        if idx < last_index:
            out_of_order = True
            break
        last_index = idx

    return SectionValidationResult(ok=not out_of_order, missing_markers=[], out_of_order=out_of_order)


def diff_prompts(
    old: PromptDefinition,
    new: PromptDefinition,
) -> PromptDiff:
    """
    Compute a simple diff between two PromptDefinitions for the same id.
    """

    if old.id != new.id:
        raise ValueError("Cannot diff prompts with different IDs")

    return PromptDiff(
        id=old.id,
        from_version=old.version,
        to_version=new.version,
        template_changed=(old.template != new.template),
        metadata_changed=(old.metadata != new.metadata),
        tags_changed=(sorted(old.tags) != sorted(new.tags)),
    )


def validate_prompt_definition(defn: PromptDefinition) -> None:
    """
    Basic validation for a single PromptDefinition.

    Raises ValueError on structural issues (used by tests / CI).
    """
    if not defn.id:
        raise ValueError("PromptDefinition.id must be non-empty")

    if not isinstance(defn.version, PromptVersion):
        raise ValueError(f"PromptDefinition.version for {defn.id} must be PromptVersion")

    # Envelope validation only for system prompts following the standard pattern.
    if defn.role == "system":
        sv = validate_sections(defn.template)
        if not sv.ok:
            raise ValueError(
                f"Prompt {defn.id} missing or misordered section markers; "
                f"missing={sv.missing_markers}, out_of_order={sv.out_of_order}"
            )


def validate_all_prompts() -> None:
    """
    Validate all registered prompts.

    Intended for test harnesses / CI.
    """
    for pd in PROMPT_REGISTRY.values():
        validate_prompt_definition(pd)


# ============================================================================
# PROMPT PAYLOAD HELPER (FOR PromptInstance CREATION)
# ============================================================================


def build_prompt_payload(
    prompt_id: str,
    *,
    actor_role: PromptActorRole = PromptActorRole.ENGINE,
    variables: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Helper used by L2 / prompt_builder to construct a payload suitable
    for PromptInstance construction.

    This function intentionally returns a plain dict to avoid introducing
    circular imports (PromptInstance lives in prompt_builder.py).

    Returns:
        {
            "prompt_id": ...,
            "definition": PromptDefinition,
            "version": PromptVersion,
            "role": str,
            "variables": Dict[str, Any],
        }
    """
    pd = get_prompt(prompt_id, actor_role=actor_role)
    return {
        "prompt_id": prompt_id,
        "definition": pd,
        "version": pd.version,
        "role": pd.role,
        "variables": variables or {},
    }


# ============================================================================
# BOOTSTRAP: SEED CORE ENVELOPE PROMPTS
# ============================================================================


def _seed_core_prompts() -> None:
    """
    Seed minimal core prompts used by v10_10.

    Each prompt:
        • Uses the envelope markers (CONTEXT / INSTRUCTIONS / OUTPUT_FORMAT).
        • Includes ACL-style metadata for:
              - layers (L1–L5)
              - agents (strategy, rag, drafting, qa, safety)
              - model_tiers (cheap / balanced / premium)
        • Defines a default_model_tier in metadata for routing.
    """

    base_version = PromptVersion(major=1, minor=0, patch=0)

    def _acl_meta(layers: List[str], agents: List[str], tiers: List[str]) -> Dict[str, Any]:
        return {
            "acl": {
                "layers": layers,
                "agents": agents,
                "model_tiers": tiers,
            }
        }

    core_prompts: List[PromptDefinition] = [
        PromptDefinition(
            id="system.resume.planner",
            version=base_version,
            role="system",
            tags=["resume", "planner", "l1", "strategy"],
            template="## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n",
            metadata={
                "description": "System prompt for L2 strategy planning over job + resume.",
                "default_model_tier": "balanced",
                **_acl_meta(layers=["L2"], agents=["strategy"], tiers=["cheap", "balanced", "premium"]),
            },
        ),
        PromptDefinition(
            id="system.resume.drafter",
            version=base_version,
            role="system",
            tags=["resume", "drafting", "l2"],
            template="## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n",
            metadata={
                "description": "System prompt for L2 drafting of resume sections.",
                "default_model_tier": "balanced",
                **_acl_meta(layers=["L2"], agents=["rag", "drafting"], tiers=["balanced", "premium"]),
            },
        ),
        PromptDefinition(
            id="system.qa.agent",
            version=base_version,
            role="system",
            tags=["qa", "l3"],
            template="## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n",
            metadata={
                "description": "System prompt for L3 QA review of drafted content.",
                "default_model_tier": "balanced",
                **_acl_meta(layers=["L3"], agents=["qa"], tiers=["cheap", "balanced", "premium"]),
            },
        ),
        PromptDefinition(
            id="system.safety.agent",
            version=base_version,
            role="system",
            tags=["safety", "l5"],
            template="## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n",
            metadata={
                "description": "System prompt for L5 safety / policy review.",
                "default_model_tier": "balanced",
                **_acl_meta(layers=["L5"], agents=["safety"], tiers=["balanced", "premium"]),
            },
        ),
    ]

    for pd in core_prompts:
        register_prompt(pd)


# Seed default prompts at import time (purely in-memory).
_seed_core_prompts()
