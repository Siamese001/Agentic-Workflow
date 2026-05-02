"""Abstract base class for apps_underwriting_ai engines.

Establishes the canonical execute() contract — receives a context dict,
returns a context-update dict — that every concrete engine satisfies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseUnderwritingEngine(ABC):
    """Base class for all apps_underwriting_ai engines.

    Subclasses implement :meth:`execute` and may override
    :meth:`pre_execute` / :meth:`post_execute` for instrumentation hooks.
    """

    @abstractmethod
    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Run the engine against the provided context.

        Args:
            context: Mutable pipeline context. Subclasses should read only
                the keys they declare in their :class:`HopStageSpec` inputs.
            **kwargs: Engine-specific options.

        Returns:
            Dict of context updates to merge back into the pipeline context.
            Keys must match the engine's declared HopStageSpec outputs.
        """

    def pre_execute(self, context: dict[str, Any]) -> None:
        """Hook called before :meth:`execute`. Default is no-op."""

    def post_execute(
        self, context: dict[str, Any], result: dict[str, Any]
    ) -> None:
        """Hook called after :meth:`execute`. Default is no-op."""
