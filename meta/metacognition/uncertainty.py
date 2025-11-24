from __future__ import annotations

from typing import Iterable

from meta.metacognition.models import Hypothesis


def compute_uncertainty(
    hypotheses: Iterable[Hypothesis],
    qa_signals: int,
    safety_signals: int,
) -> float:
    """Compute a coarse uncertainty score in [0, 1].

    Factors:
    - spread of confidence values (higher spread ⇒ higher uncertainty)
    - presence of QA / safety signals (more signals ⇒ higher uncertainty)
    """

    hs = list(hypotheses)
    if not hs:
        base = 0.8 if (qa_signals or safety_signals) else 0.5
        return min(1.0, base)

    confidences = [float(h.confidence) for h in hs]
    avg = sum(confidences) / len(confidences)
    var = sum((c - avg) ** 2 for c in confidences) / max(1, len(confidences) - 1)

    spread = min(1.0, var ** 0.5)
    qa_factor = min(1.0, qa_signals / 5.0)
    safety_factor = min(1.0, safety_signals / 3.0)

    score = 0.3 * spread + 0.4 * qa_factor + 0.3 * safety_factor
    return max(0.0, min(1.0, score))



