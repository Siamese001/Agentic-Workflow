"""RAG planning stack stubs for orchestration tests."""
from __future__ import annotations

from typing import Any, Dict


class RAGPlanningStack:
    """Produces deterministic RAG plans for downstream execution."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        goal = state.get("metadata", {}).get("goal", "")
        return {
            "rag": {
                "plan": {
                    "goal": goal,
                    "use_hyde": state.get("rag", {}).get("use_hyde", True),
                }
            }
        }
