from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)


class EmbeddingResult:
    """A placeholder for the result of an embedding retrieval operation."""

    pass


class EmbeddingInfluenceViolation(Exception):
    """Raised when an embedding artifact is detected influencing a sovereign decision."""

    def __init__(self, decision_type: str, found_in: str):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "EmbeddingInfluenceViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "EmbeddingInfluenceViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "EmbeddingInfluenceViolation.__init__",
        )
        self.decision_type = decision_type
        self.found_in = found_in
        super().__init__(
            f"Embedding artifact illegally influenced '{decision_type}' decision. Found in: {found_in}.",
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
