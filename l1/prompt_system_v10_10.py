"""
Prompt Registry & Governance for resume generation system.

Single source of truth for all prompts to ensure consistent
resume improvement and job alignment.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from core.models.models import PromptDefinition, PromptVersion


# ============================================================================
# ACTOR ROLES & ACL
# ============================================================================


class PromptActorRole(str, Enum):
    """
    Logical actors that interact with the prompt registry.

    Defines roles for resume generation prompt governance and access control.
    """

    ENGINE = "engine"   # runtime engine / L2 cognition
    ADMIN = "admin"     # maintenance / DevOps
    EDITOR = "editor"   # prompt engineer
    VIEWER = "viewer"   # read-only


class PromptACL(BaseModel):
    """
    Role-based ACL for prompt access control in resume generation.

    Ensures proper governance for consistent resume improvement prompts.
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
    Enforce PromptACL for the given role and use_case.

    use_case:
        - "read"  → viewing the definition
        - "edit"  → modifying / registering the definition
        - "use"   → using in ENGINE (runtime)
    """
    acl = PROMPT_ACLS.get(prompt_id)
    if acl is None:
        # Default: permissive for ENGINE/ADMIN, read-only for others.
        return

    if use_case == "read":
        if actor_role == PromptActorRole.VIEWER and acl.viewers_can_read:
            return
        if actor_role in (PromptActorRole.ENGINE, PromptActorRole.ADMIN, PromptActorRole.EDITOR):
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
    use_case: str = "use",
) -> PromptDefinition:
    """
    Retrieve a PromptDefinition by id with ACL enforcement.
    """
    if prompt_id not in PROMPT_REGISTRY:
        raise KeyError(f"Unknown prompt id: {prompt_id}")
    _check_acl(prompt_id, actor_role, use_case)
    return PROMPT_REGISTRY[prompt_id]


def get_prompt_acl(prompt_id: str) -> Optional[PromptACL]:
    """
    Retrieve the PromptACL for a given prompt id, or None if not set.
    """
    return PROMPT_ACLS.get(prompt_id)


# ============================================================================
# DIFF / VALIDATION UTILITIES
# ============================================================================


class PromptDiff(BaseModel):
    id: str
    from_version: PromptVersion
    to_version: PromptVersion
    text_changed: bool
    metadata_changed: bool


def diff_prompts(old: PromptDefinition, new: PromptDefinition) -> PromptDiff:
    """
    Compute a simple diff between two PromptDefinitions for the same id.
    """
    if old.id != new.id:
        raise ValueError("Cannot diff prompts with different IDs")

    return PromptDiff(
        id=old.id,
        from_version=old.version,
        to_version=new.version,
        text_changed=(old.text != new.text),
        metadata_changed=(old.metadata != new.metadata),
    )


def validate_prompt_definition(defn: PromptDefinition) -> None:
    """
    Basic validation for a single PromptDefinition.

    Raises ValueError on structural issues (used by tests / CI).
    """
    if not defn.id:
        raise ValueError("PromptDefinition.id must be non-empty")
    if not isinstance(defn.version, PromptVersion):
        raise ValueError("PromptDefinition.version must be a PromptVersion")


def list_prompt_ids() -> List[str]:
    return sorted(PROMPT_REGISTRY.keys())


# ============================================================================
# CORE PROMPT SEEDING (Phase 3)
# ============================================================================


def _acl_meta(layers: List[str], agents: List[str], tiers: List[str]) -> Dict[str, Any]:
    return {
        "acl": {
            "layers": layers,
            "agents": agents,
            "model_tiers": tiers,
        }
    }


def _seed_core_prompts() -> None:
    """
    Seed minimal core prompts for the v10_10 stack.

    All templates follow the simple pattern:

        "## CONTEXT\\n\\n## INSTRUCTIONS\\n\\n## OUTPUT_FORMAT\\n"

    The richer envelope sections (Framing, Reasoning, Safety) are added
    by prompt_builder at runtime.
    """
    base_version = PromptVersion(major=1, minor=0, patch=0)

    def _pd(
        pid: str,
        description: str,
        layers: List[str],
        agents: List[str],
        tiers: List[str],
    ) -> PromptDefinition:
        text = "## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n"
        metadata = {
            "description": description,
            "default_model_tier": "balanced",
            "role": "system",
            **_acl_meta(layers=layers, agents=agents, tiers=tiers),
        }
        return PromptDefinition(id=pid, text=text, version=base_version, metadata=metadata)

    core_prompts: List[PromptDefinition] = [
        # L1 / Strategy planner
        _pd(
            pid="system.resume.planner",
            description="System prompt for L1/L2 strategy planning over job + resume.",
            layers=["L2"],
            agents=["strategy"],
            tiers=["cheap", "balanced", "premium"],
        ),
        # L2 / Drafting (also used as RAG reasoning base template)
        _pd(
            pid="system.resume.drafter",
            description="System prompt for L2 drafting of resume sections.",
            layers=["L2"],
            agents=["rag", "drafting"],
            tiers=["balanced", "premium"],
        ),
        # L3 / QA
        _pd(
            pid="system.qa.agent",
            description="System prompt for L3 QA review of drafted content.",
            layers=["L3"],
            agents=["qa"],
            tiers=["cheap", "balanced", "premium"],
        ),
        # L5 / Safety
        _pd(
            pid="system.safety.agent",
            description="System prompt for L5 safety / policy review.",
            layers=["L5"],
            agents=["safety"],
            tiers=["balanced", "premium"],
        ),
        # L2 / HYDE RAG query
        _pd(
            pid="system.rag.hyde_query",
            description=(
                "System prompt for L2 HYDE query expansion: generate an ideal answer "
                "to use as a retrieval proxy."
            ),
            layers=["L2"],
            agents=["rag"],
            tiers=["balanced", "premium"],
        ),
        # L2 / QA council member (per-agent QA)
        _pd(
            pid="system.qa.council_member",
            description=(
                "System prompt for a single QA council member evaluating drafted content "
                "and retrieved evidence."
            ),
            layers=["L2"],
            agents=["qa_council"],
            tiers=["cheap", "balanced", "premium"],
        ),
        # IDs used directly in tests/test_end_to_end_v10_10.py
        _pd(
            pid="strategy_generate_branch",
            description="L2 strategy branch generation prompt.",
            layers=["L2"],
            agents=["strategy"],
            tiers=["cheap", "balanced", "premium"],
        ),
        _pd(
            pid="strategy_select_branch",
            description="L2 strategy branch selection prompt.",
            layers=["L2"],
            agents=["strategy"],
            tiers=["cheap", "balanced", "premium"],
        ),
        _pd(
            pid="drafting_structure",
            description="L2 drafting structure prompt for resume sections.",
            layers=["L2"],
            agents=["drafting"],
            tiers=["balanced", "premium"],
        ),
        _pd(
            pid="drafting_narrative",
            description="L2 drafting narrative prompt for resume sections.",
            layers=["L2"],
            agents=["drafting"],
            tiers=["balanced", "premium"],
        ),
        _pd(
            pid="drafting_compliance",
            description="L2 drafting compliance / style prompt.",
            layers=["L2"],
            agents=["drafting"],
            tiers=["balanced", "premium"],
        ),
        _pd(
            pid="qa_semantic_check",
            description="L2 QA semantic check prompt for drafted content.",
            layers=["L2"],
            agents=["qa"],
            tiers=["cheap", "balanced", "premium"],
        ),
        _pd(
            pid="safety_check",
            description="L2 safety check prompt for drafted content.",
            layers=["L2"],
            agents=["safety"],
            tiers=["balanced", "premium"],
        ),
    ]

    for pd in core_prompts:
        validate_prompt_definition(pd)
        register_prompt(pd)


# Seed default prompts at import time (purely in-memory).
_seed_core_prompts()



