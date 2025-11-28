from __future__ import annotations

from typing import Any, Iterable, Mapping


def _as_mapping(obj: Any) -> Mapping[str, Any]:
    if isinstance(obj, Mapping):
        return obj
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()  # type: ignore[call-arg]
        except TypeError:  # pragma: no cover - defensive
            pass
    if hasattr(obj, "dict"):
        try:
            return obj.dict()  # type: ignore[call-arg]
        except TypeError:  # pragma: no cover - defensive
            pass
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return {}


def compute_collaboration_score(outputs: Iterable[Any]) -> float:
    """Compute a simple collaboration score over simulation outputs.

    The current implementation looks for a ``golden_eval_score`` field in
    each output's ``outcome`` mapping and returns the average. Missing
    scores are treated as zero.
    """

    total = 0.0
    count = 0
    for out in outputs:
        m = _as_mapping(out)
        outcome = m.get("outcome") or m.get("average_scores") or {}
        outcome_map = _as_mapping(outcome)
        score = float(outcome_map.get("golden_eval_score") or 0.0)
        total += score
        count += 1
    if not count:
        return 0.0
    return total / float(count)


def compute_conflict_index(outputs: Iterable[Any]) -> float:
    """Compute a heuristic conflict index from simulation outputs.

    We treat any ``correction_iterations`` > 0 or explicit
    ``agent_conflict_count`` > 0 as evidence of conflict and return the
    fraction of outputs exhibiting such signals.
    """

    conflict = 0
    total = 0
    for out in outputs:
        m = _as_mapping(out)
        outcome = m.get("outcome") or {}
        outcome_map = _as_mapping(outcome)

        corr_iters = int(outcome_map.get("correction_iterations", 0) or 0)
        agent_conflicts = int(m.get("agent_conflict_count", 0) or 0)

        if corr_iters > 0 or agent_conflicts > 0:
            conflict += 1
        total += 1

    if not total:
        return 0.0
    return conflict / float(total)



