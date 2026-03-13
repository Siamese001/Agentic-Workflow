"""
Executive Brief Spine Adapter — apps_exec.

Provides deterministic CID derivation and call-order invariants
for the apps_exec pipeline. Subclasses BaseSpineAdapter with
prefix "exec-".
"""

from __future__ import annotations

from typing import Any

from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

_EXEC_PREFIX = "exec-"


class ExecSpineAdapter(BaseSpineAdapter):
    """Spine adapter for apps_exec executive brief generation.

    CID prefix: "exec-"
    Orchestrator: ExecOrchestrator (or compatible execute() interface)
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
            prefix=_EXEC_PREFIX,
            max_reentry_attempts=max_reentry_attempts,
        )

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """Execute executive brief generation through spine.

        Expects intent_input to contain at minimum:
            audience: str — target persona key
            source_dirs: list[str] — source document directories

        Returns:
            Result dict with CID and orchestrator output.
        """
        return super().execute(intent_input)


__all__ = ["ExecSpineAdapter"]
