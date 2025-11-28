from __future__ import annotations

from typing import List

from meta.metacognition.models import Hypothesis


def refine_low_confidence(hypotheses: List[Hypothesis], threshold: float = 0.4) -> List[Hypothesis]:
    """Refine hypotheses below a confidence threshold.

    Rules:
    - if confidence < threshold / 2, mark hypothesis as effectively discarded
      by prepending a cautionary prefix.
    - elif confidence < 1.0, append a cautious qualifier asking for more
      evidence before acting.
    - otherwise leave content unchanged.
    """

    refined: List[Hypothesis] = []
    for h in hypotheses:
        conf = float(h.confidence)
        content = h.content
        if conf < threshold / 2:
            new_content = f"[DISCARDED_CANDIDATE] {content}"
        elif conf < 1.0:
            new_content = f"{content} (needs further evidence before acting)"
        else:
            new_content = content
        refined.append(h.model_copy(update={"content": new_content}))
    return refined



