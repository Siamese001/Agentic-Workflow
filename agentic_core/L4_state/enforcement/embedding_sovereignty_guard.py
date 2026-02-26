from __future__ import annotations

from typing import Any


# Placeholder for the actual EmbeddingResult type.
# In a real system, this would be imported from the embedding service.
class EmbeddingResult:
    """A placeholder for the result of an embedding retrieval operation."""

    pass


class EmbeddingInfluenceViolation(Exception):
    """Raised when an embedding artifact is detected influencing a sovereign decision."""

    def __init__(self, decision_type: str, found_in: str):
        self.decision_type = decision_type
        self.found_in = found_in
        super().__init__(
            f"Embedding artifact illegally influenced '{decision_type}' decision. Found in: {found_in}."
        )


def guard_embedding_influence(*args: Any, decision_type: str, **kwargs: Any) -> None:
    """
    A sovereign runtime guard that prevents embedding results from influencing decisions.

    This function enforces Guarantee #21 by recursively scanning the arguments of
    critical decision-making functions (like `route_healing_tier` or safety
    classifiers) to ensure no `EmbeddingResult` objects are present. This prevents
    both direct and indirect leakage.

    This guard must be placed at the entry point of all sovereign decision boundaries.

    Args:
        decision_type: A string identifying the type of decision being made.
        *args: The positional arguments passed to the decision function.
        **kwargs: The keyword arguments passed to the decision function.

    Raises:
        EmbeddingInfluenceViolation: If an `EmbeddingResult` is found in the arguments.
    """
    all_args = list(args) + list(kwargs.values())

    def _scan_for_embedding_result(obj: Any, path: str) -> None:
        """
        Recursively scans an object for instances of EmbeddingResult.
        """
        if isinstance(obj, EmbeddingResult):
            raise EmbeddingInfluenceViolation(decision_type, path)

        if isinstance(obj, dict):
            for k, v in obj.items():
                _scan_for_embedding_result(v, f"{path}.{k}")
        elif isinstance(obj, (list, tuple)):
            for i, item in enumerate(obj):
                _scan_for_embedding_result(item, f"{path}[{i}]")

    for i, arg in enumerate(all_args):
        _scan_for_embedding_result(arg, f"arg[{i}]")


# --- Static Typing Barrier Concept ---
#
# In addition to the runtime guard, a static typing barrier would be used.
# This involves creating a specific, non-transferable type for embedding results
# that is only used for informational purposes (e.g., logging).
#
# from typing import NewType
#
# InformationalEmbeddingResult = NewType('InformationalEmbeddingResult', EmbeddingResult)
#
# Critical decision functions would then be typed to reject `EmbeddingResult` and
# `InformationalEmbeddingResult` explicitly, causing static analysis tools like
# mypy to raise an error if they are passed in.
#
# def route_healing_tier(input: HealingInput) -> HealingDecision:
#     # This function's signature does not allow EmbeddingResult
#     pass
