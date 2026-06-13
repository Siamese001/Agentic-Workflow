"""
Evaluation Lab Spine Adapter — apps_eval.

Provides deterministic CID derivation and call-order invariants
for the apps_eval pipeline. Subclasses BaseSpineAdapter with
prefix "eval-".

EVAL-PIPELINE SCOPE: NON_CANONICAL_EVAL_LAB
This module is intentionally outside the canonical runtime evaluation pipeline.
EvalSpineAdapter.execute() delegates spine CID management to BaseSpineAdapter;
it does not invoke ExitControlGate, build shadow packets, or perform UWG handoff.
Do not add canonical pipeline wiring here.
"""

from __future__ import annotations

from typing import Any

from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

_EVAL_PREFIX = "eval-"


class EvalSpineAdapter(BaseSpineAdapter):
    """Spine adapter for apps_eval evaluation lab.

    CID prefix: "eval-"
    Orchestrator: EvalOrchestrator (or compatible execute() interface)
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
            prefix=_EVAL_PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """Execute evaluation lab run through spine.

        Expects intent_input to contain at minimum:
            suite_ids: list[str] — benchmark suites to run

        Returns:
            Result dict with CID and orchestrator output.
        """
        return super().execute(intent_input)


__all__ = ["EvalSpineAdapter"]
