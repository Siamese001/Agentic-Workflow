# FILE: 10_10/prompt_system_v10_10.py
"""
Prompt Registry & Governance (v10_10 · Phase 0)
===============================================

This module provides the **central prompt registry** and basic governance
primitives required to address:

    • G24 – PromptVersion system
    • G25 – Prompt registry
    • G26 – Prompt ACL governance
    • G27 – Context richness / envelope structure (partial)
    • G28 – ContextBudget manager (indirect, via metadata)

Phase 0 goals:
    • Define a single source-of-truth for prompts (by ID).
    • Provide semantic versioning via PromptVersion.
    • Provide simple ACLs to distinguish engine/runtime vs editor access.
    • Provide utilities for listing, diffing, and validating prompts.

Phase 0 explicitly **does NOT**:
    • Rewrite L1/L2/cognitive_agents to use this registry (Phase 2+).
    • Implement UI or external storage.
    • Implement full prompt lifecycle tooling.

The registry is intentionally in-memory and deterministic.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Iterable, Any

from pydantic import BaseModel, Field

from .models import PromptDefinition, PromptVersion


# ======================================================================
# ACTOR ROLES & ACL
# ======================================================================


class PromptActorRole(str, Enum):
    """
    High-level roles for prompt governance.

    • ENGINE  – runtime / code paths invoking prompts during execution.
    • ADMIN   – can create, update, and deprecate prompts.
    • EDITOR  – can propose / edit content but not change IDs or versions.
    • VIEWER  – read-only access to prompt definitions.
    """

    ENGINE = "engine"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class PromptACL(BaseModel):
    """
    Simple role-based ACL for a single prompt ID.
    """

    id: str
    engine_can_use: bool = True
    admins_can_edit: bool = True
    editors_can_edit: bool = False
    viewers_can_read: bool = True


# In-memory ACL registry keyed by prompt ID.
PROMPT_ACLS: Dict[str, PromptACL] = {}


# ======================================================================
# PROMPT REGISTRY (IN-MEMORY)
# ======================================================================

# In-memory prompt registry keyed by prompt ID.
PROMPT_REGISTRY: Dict[str, PromptDefinition] = {}


def register_prompt(defn: PromptDefinition, acl: Optional[PromptACL] = None) -> None:
    """
    Register or update a prompt definition in the global registry.

    This is deterministic and side-effect free beyond the in-memory map.
    """

    PROMPT_REGISTRY[defn.id] = defn
    if acl is not None:
        PROMPT_ACLS[defn.id] = acl
    elif defn.id not in PROMPT_ACLS:
        # Default ACL: engine and admins may use/edit; others read-only.
        PROMPT_ACLS[defn.id] = PromptACL(id=defn.id)


def get_prompt(prompt_id: str, actor_role: PromptActorRole = PromptActorRole.ENGINE) -> PromptDefinition:
    """
    Retrieve a prompt by ID, enforcing ACL for the caller's role.
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


# ======================================================================
# DIFF & VALIDATION UTILITIES
# ======================================================================


class PromptDiff(BaseModel):
    """
    Structured diff between two prompt versions.

    This is intentionally simple but enough for:
        • CI checks (breaking vs non-breaking changes).
        • Human review in logs or tooling.
    """

    id: str
    from_version: str
    to_version: str
    changed_fields: List[str] = Field(default_factory=list)
    metadata_changes: Dict[str, Any] = Field(default_factory=dict)


def diff_prompts(old: PromptDefinition, new: PromptDefinition) -> PromptDiff:
    """
    Compute a simple, deterministic diff between two PromptDefinitions
    with the same ID.
    """

    if old.id != new.id:
        raise ValueError(f"Cannot diff different prompt ids: {old.id} vs {new.id}")

    changed_fields: List[str] = []

    if old.version.as_str() != new.version.as_str():
        changed_fields.append("version")

    if old.role != new.role:
        changed_fields.append("role")

    if old.tags != new.tags:
        changed_fields.append("tags")

    if old.template != new.template:
        changed_fields.append("template")

    metadata_changes: Dict[str, Any] = {}
    if old.metadata != new.metadata:
        metadata_changes = {
            "old": old.metadata,
            "new": new.metadata,
        }
        changed_fields.append("metadata")

    return PromptDiff(
        id=old.id,
        from_version=old.version.as_str(),
        to_version=new.version.as_str(),
        changed_fields=changed_fields,
        metadata_changes=metadata_changes,
    )


SECTION_MARKERS_DEFAULT = [
    "## CONTEXT",
    "## INSTRUCTIONS",
    "## OUTPUT_FORMAT",
]


class SectionValidationResult(BaseModel):
    """
    Result of template section validation.

    For Phase 0 we only check for:
        • presence of configured markers
        • strict order of these markers
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
    the expected order. This is a basic structural guard for G27.

    This does not enforce content semantics, only section structure.
    """

    markers = required_markers or SECTION_MARKERS_DEFAULT
    missing: List[str] = []
    last_index = -1
    out_of_order = False

    for marker in markers:
        idx = template.find(marker)
        if idx == -1:
            missing.append(marker)
        else:
            if idx < last_index:
                out_of_order = True
            last_index = idx

    ok = not missing and not out_of_order
    return SectionValidationResult(ok=ok, missing_markers=missing, out_of_order=out_of_order)


# ======================================================================
# ACL ENFORCEMENT
# ======================================================================


def _check_acl(prompt_id: str, actor_role: PromptActorRole, use_case: str) -> None:
    """
    Internal ACL check.

    use_case: "read" | "edit" | "use"
    """

    acl = PROMPT_ACLS.get(prompt_id)
    if acl is None:
        # Default: engine can use; admins can edit; viewers read.
        acl = PromptACL(id=prompt_id)
        PROMPT_ACLS[prompt_id] = acl

    if use_case == "read":
        if actor_role == PromptActorRole.ENGINE:
            # Engine reads for execution.
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


# ======================================================================
# BOOTSTRAP: SEED CORE PROMPT DEFINITIONS (PLACEHOLDERS)
# ======================================================================

def _seed_core_prompts() -> None:
    """
    Seed registry with minimal, placeholder prompt definitions.

    NOTE: These are placeholders to make the registry usable in Phase 0.
    Real content will be introduced / migrated in Phase 2+ when L1/L2 and
    cognitive agents are refactored to use this system.
    """

    base_version = PromptVersion(major=1, minor=0, patch=0)

    core_prompts = [
        PromptDefinition(
            id="system.resume.planner",
            version=base_version,
            role="system",
            tags=["resume", "planner", "l1"],
            template="## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n",
            metadata={"description": "System prompt for L1 resume planning."},
        ),
        PromptDefinition(
            id="system.resume.drafter",
            version=base_version,
            role="system",
            tags=["resume", "drafting", "l2"],
            template="## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n",
            metadata={"description": "System prompt for drafting resume sections."},
        ),
        PromptDefinition(
            id="system.qa.agent",
            version=base_version,
            role="system",
            tags=["qa", "l3"],
            template="## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n",
            metadata={"description": "System prompt for QA agent checks."},
        ),
        PromptDefinition(
            id="system.safety.agent",
            version=base_version,
            role="system",
            tags=["safety", "l5"],
            template="## CONTEXT\n\n## INSTRUCTIONS\n\n## OUTPUT_FORMAT\n",
            metadata={"description": "System prompt for safety / policy checks."},
        ),
    ]

    for pd in core_prompts:
        register_prompt(pd)


# Seed default prompts at import time (purely in-memory).
_seed_core_prompts()
