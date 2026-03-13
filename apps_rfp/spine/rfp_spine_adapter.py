"""
RFP Proposal Spine Adapter — apps_rfp.

Provides deterministic CID derivation and call-order invariants
for the apps_rfp pipeline. Subclasses BaseSpineAdapter with
prefix "rfp-".
"""

from __future__ import annotations

from typing import Any

from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

_RFP_PREFIX = "rfp-"


class RfpSpineAdapter(BaseSpineAdapter):
    """Spine adapter for apps_rfp AI proposal generation.

    CID prefix: "rfp-"
    Orchestrator: RfpOrchestrator (or compatible execute() interface)
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
            prefix=_RFP_PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """Execute RFP proposal generation through spine.

        Expects intent_input to contain at minimum:
            problem_statement: str — the RFP brief
            industry: str — target industry key

        Returns:
            Result dict with CID and orchestrator output.
        """
        return super().execute(intent_input)


__all__ = ["RfpSpineAdapter"]
