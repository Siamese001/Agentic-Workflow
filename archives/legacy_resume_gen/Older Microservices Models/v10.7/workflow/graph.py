"""Lightweight workflow graph for system tests."""
from __future__ import annotations

from typing import Iterable, List

_REQUIRED_NODES: List[str] = [
    "PromptInjectionDetector",
    "PIISanitizerAgent",
    "QAAgent",
    "StrategyAgent",
    "RAGAgent",
    "DraftingAgent",
]

_EDGES: List[str] = [
    "PromptInjectionDetector -> PIISanitizerAgent",
    "PIISanitizerAgent -> StrategyAgent",
    "StrategyAgent -> RAGAgent",
    "RAGAgent -> DraftingAgent",
    "DraftingAgent -> QAAgent",
]


def get_nodes() -> Iterable[str]:
    """Return the ordered list of workflow nodes."""

    return list(_REQUIRED_NODES)


def get_edges() -> Iterable[str]:
    """Return labelled edges in ``node_a -> node_b`` form."""

    return list(_EDGES)
