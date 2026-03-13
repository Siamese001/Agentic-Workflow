"""
Research Spine Adapter — apps_research.

Provides deterministic CID derivation and call-order invariants
for the apps_research pipeline. Subclasses BaseSpineAdapter with
prefix "rsch-".
"""

from __future__ import annotations

from typing import Any

from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

_RESEARCH_PREFIX = "rsch-"


class ResearchSpineAdapter(BaseSpineAdapter):
    """Spine adapter for apps_research autonomous research generation.

    CID prefix: "rsch-"
    Orchestrator: ResearchOrchestrator (or compatible execute() interface)
    """

    def __init__(
        self,
        cid_registry: Any,
        orchestrator: Any,
        *,
        max_reentry_attempts: int = 3,
    ) -> None:
        super().__init__(
            cid_registry,
            orchestrator,
            prefix=_RESEARCH_PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """Execute research artifact generation through spine.

        Expects intent_input to contain at minimum:
            topic: str — research topic
            mode: str — artifact mode (brief, comparison, trend, position, thought_leadership)

        Returns:
            Result dict with CID and orchestrator output.
        """
        return super().execute(intent_input)


__all__ = ["ResearchSpineAdapter"]
