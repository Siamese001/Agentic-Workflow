"""Conceptual DAG specification for the v10.7 orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set


@dataclass(frozen=True)
class ConceptualNode:
    """Represents a conceptual workflow block and its concrete LangGraph nodes."""

    name: str
    concrete_nodes: List[str]


CONCEPTUAL_DAG: List[ConceptualNode] = [
    ConceptualNode(
        name="SafetyGuardStack",
        concrete_nodes=["run_sanitize_pii", "run_detect_prompt_injection"],
    ),
    ConceptualNode(
        name="StrategyStack",
        concrete_nodes=[
            "run_classify_complexity",
            "run_tot_strategy",
            "run_arbitration_after_strategy",
            "run_detect_ambiguity",
        ],
    ),
    ConceptualNode(
        name="RAGStack",
        concrete_nodes=[
            "prepare_parallel_run",
            "run_prompt_engineering",
            "run_rag_stack",
            "join_rag_and_prompt",
            "run_arbitration_after_join",
        ],
    ),
    ConceptualNode(
        name="BulletStack",
        concrete_nodes=[
            "run_generate_bullets",
            "run_critique_bullets",
            "run_arbitration_after_bullets",
        ],
    ),
    ConceptualNode(
        name="DraftingStack",
        concrete_nodes=[
            "run_drafting",
            "run_arbitration_after_drafting",
        ],
    ),
    ConceptualNode(
        name="QAStack",
        concrete_nodes=[
            "run_qa_validation",
            "run_arbitration_after_qa",
            "run_constitutional_review",
        ],
    ),
    ConceptualNode(
        name="HILInteractionStack",
        concrete_nodes=[
            "HIL_PAUSE",
            "run_feedback_router",
            "run_prepare_hil_strategy_reentry",
            "run_prepare_hil_drafting_reentry",
            "run_reconcile_specialists",
            "run_inject_hil_edit",
        ],
    ),
]


def conceptual_node_map() -> Dict[str, ConceptualNode]:
    """Return a lookup dictionary for conceptual nodes by name."""

    return {node.name: node for node in CONCEPTUAL_DAG}


def all_concrete_nodes() -> Set[str]:
    """Return the flattened set of concrete node names covered by the spec."""

    return {
        concrete
        for node in CONCEPTUAL_DAG
        for concrete in node.concrete_nodes
    }


def iter_concrete_nodes(node_names: Iterable[str]) -> Iterable[str]:
    """Iterate over all concrete nodes for the given conceptual node names."""

    lookup = conceptual_node_map()
    for name in node_names:
        conceptual = lookup.get(name)
        if not conceptual:
            continue
        yield from conceptual.concrete_nodes


__all__ = ["ConceptualNode", "CONCEPTUAL_DAG", "conceptual_node_map", "all_concrete_nodes", "iter_concrete_nodes"]
