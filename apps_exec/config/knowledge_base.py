"""Canonical apps_exec knowledge base exports.

This module preserves the historical import surface:
`apps_exec.config.knowledge_base`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NodeConfig:
    """K-node configuration entry."""

    node_id: str
    description: str = ""
    settings: dict[str, Any] = field(default_factory=dict)


FROZEN_SNAPSHOT: dict[str, Any] = {
    "prompts": {
        "exec_brief_intro": (
            "Topic: {topic}\n\n"
            "You are drafting an executive brief for {audience}. "
            "Tone: {tone}. Produce a concise, high-signal brief."
        ),
        "exec_brief_section": (
            "Section: {section_title}\n\n"
            "Write a focused section for the executive brief. "
            "Evidence anchors: {evidence}."
        ),
    },
    "nodes": {
        "ingestion": NodeConfig(
            node_id="ingestion",
            description="Document ingestion and preprocessing node",
        ),
        "quality_gate": NodeConfig(
            node_id="quality_gate",
            description="Quality gate enforcement node",
        ),
    },
}


def get_prompt(prompt_id: str) -> str:
    """Return prompt template for *prompt_id*.

    Raises:
        KeyError: If prompt_id is not present in the snapshot.
    """
    prompts: dict[str, str] = FROZEN_SNAPSHOT.get("prompts", {})
    if prompt_id not in prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in knowledge base")
    return prompts[prompt_id]


def get_node_config(node_id: str) -> NodeConfig:
    """Return NodeConfig for *node_id*.

    Raises:
        KeyError: If node_id is not present in the snapshot.
    """
    nodes: dict[str, NodeConfig] = FROZEN_SNAPSHOT.get("nodes", {})
    if node_id not in nodes:
        raise KeyError(f"Node '{node_id}' not found in knowledge base")
    return nodes[node_id]


def list_all_prompts() -> list[str]:
    """Return sorted list of all registered prompt IDs."""
    return sorted(FROZEN_SNAPSHOT.get("prompts", {}).keys())
