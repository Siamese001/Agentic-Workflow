"""Managed workflow manifest types — generic, app-agnostic contracts.

Phase 1.2 of apps-rg-ensemble-judge-restoration-a7c4e2.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SectionNode:
    """One bounded work unit within a managed workflow.

    L3 sequences these; L2 executes each independently via ENSEMBLE_MODEL lane.
    No app-specific names — nodes are identified by opaque IDs resolved from manifest.
    """

    node_id: str = ""
    node_order: int = 0

    # Execution shape
    lane: str = "ENSEMBLE_MODEL"  # L2 lane to use
    candidate_count: int = 3
    gate_config_ref: str = ""  # pointer to app-supplied gate config
    judge_rubric_ref: str = ""  # pointer to app-supplied judge rubric
    prompt_profile_ref: str = ""  # pointer to app-supplied prompt variants

    # Provider routing
    generator_provider_profile_ref: str = ""
    judge_provider_profile_ref: str = ""

    # Merge metadata
    merge_order: int = 0
    merge_strategy_ref: str = ""  # pointer to app-supplied merge function

    # Constraints
    max_tokens: int = 0
    timeout_seconds: int = 120

    schema_version: str = "1.0"


@dataclass(frozen=True, slots=True)
class ManagedWorkflowSpec:
    """Declarative specification of a multi-node managed workflow.

    Resolved from app-supplied manifest via registry.
    L3 consumes this to drive sequencing.
    """

    workflow_id: str = ""
    workflow_version: str = ""
    app_context: str = ""
    task_class: str = ""

    # Nodes
    nodes: tuple[SectionNode, ...] = field(default_factory=tuple)

    # Merge
    final_merge_strategy_ref: str = ""

    # Registry provenance
    manifest_digest: str = ""
    registry_digest_set: str = ""
    policy_hash: str = ""

    # Constraints
    max_total_timeout_seconds: int = 600
    fail_on_any_node_failure: bool = True

    # Tracing
    trace_root: str = ""
    resolved_at: str = ""

    schema_version: str = "1.0"
