# context_budget.py
"""
L4 — Context Budget Manager (v10_9)

Defines max sizes and token-based pruning for:
    • messages
    • rag history
    • world facts
    • summary
"""

from __future__ import annotations

from typing import List, Dict

from ..shared.models import Message
from ..shared.models import BudgetConfig


class ContextBudget:
    """Lightweight heuristic budgeting."""

    def __init__(self, config: BudgetConfig | None = None) -> None:
        self.config = config or BudgetConfig()

    # -------------------------------------------------------------

    def prune_messages(self, messages: List[Message]) -> List[Message]:
        max_items = self.config.max_messages
        return messages[-max_items:] if len(messages) > max_items else messages

    def prune_rag_items(self, rag: List[Dict]) -> List[Dict]:
        max_items = self.config.max_rag_items
        return rag[-max_items:] if len(rag) > max_items else rag

    def prune_summary(self, summary: str) -> str:
        max_chars = self.config.max_summary_chars
        return summary[-max_chars:] if len(summary) > max_chars else summary

    def prune_world(self, world: List[Dict]) -> List[Dict]:
        max_items = self.config.max_world_items
        return world[-max_items:] if len(world) > max_items else world
