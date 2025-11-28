from __future__ import annotations

from typing import List

from meta.metacognition.models import Hypothesis


def evaluate_hypotheses(hypotheses: List[Hypothesis]) -> List[Hypothesis]:
    """Return a new list of hypotheses with adjusted confidence.

    Heuristics (purely deterministic):
    - penalize very long or very short content slightly.
    - if a hypothesis has no evidence_ids, reduce confidence.
    - clamp confidence to [0, 1].
    """

    evaluated: List[Hypothesis] = []
    for h in hypotheses:
        conf = float(h.confidence)
        length = len(h.content or "")
        if length < 20 or length > 400:
            conf *= 0.9
        if not h.evidence_ids:
            conf *= 0.7
        conf = max(0.0, min(1.0, conf))
        evaluated.append(h.model_copy(update={"confidence": conf}))
    return evaluated



