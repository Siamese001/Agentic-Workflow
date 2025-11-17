# memory_manager.py
"""
L4 — Memory Manager (v10_9)

Responsible for:
    • canonicalizing messages
    • pruning messages & RAG history
    • trimming summaries & world facts
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List

from ..shared.models import Message
from .context_budget import ContextBudget
from .world_model_contracts import normalize_world_facts


class MemoryManager:
    """Deterministic memory reconciliation."""

    def __init__(self, budget: ContextBudget | None = None) -> None:
        self.budget = budget or ContextBudget()

    def reconcile_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        out = copy.deepcopy(state)

        # canonical message structure
        messages = out.get("messages") or []
        normalized_msgs: List[Message] = []
        for m in messages:
            if isinstance(m, dict):
                role = str(m.get("role", ""))
                content = str(m.get("content", ""))
            else:
                role, content = "unknown", str(m)
            normalized_msgs.append({"role": role, "content": content})

        # canonical RAG items
        rag = out.get("rag_history") or []
        canonical_rag = []
        for i in rag:
            if isinstance(i, dict):
                canonical_rag.append({
                    "query": str(i.get("query", "")),
                    "evidence": i.get("evidence", []),
                })
            else:
                canonical_rag.append({"query": str(i), "evidence": []})

        # world model
        world = normalize_world_facts(out.get("world") or [])

        # apply budgets
        out["messages"] = self.budget.prune_messages(normalized_msgs)
        out["rag_history"] = self.budget.prune_rag_items(canonical_rag)
        out["summary"] = self.budget.prune_summary(out.get("summary", ""))
        out["world"] = self.budget.prune_world(world)

        return out
