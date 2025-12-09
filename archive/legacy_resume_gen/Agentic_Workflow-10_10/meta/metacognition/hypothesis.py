from __future__ import annotations

from typing import Any, List

from meta.metacognition.models import Hypothesis


def generate_initial_hypotheses(task: str, rag_result: Any, agent_card: Any) -> List[Hypothesis]:
    """Generate a small set of coarse hypotheses from task + RAG.

    This implementation is deterministic and uses only cheap heuristics:
    - if there is any evidence, we create 1–3 simple hypotheses whose
      confidence is proportional to the number of evidence items.
    - if no evidence is present, we still produce a single low-confidence
      hypothesis so downstream code has something to inspect.
    """

    evidence = getattr(rag_result, "evidence", []) or []
    evidence_ids = [str(i) for i in range(len(evidence))]
    count = len(evidence)

    base_conf = 0.2 if count == 0 else min(1.0, 0.3 + 0.1 * count)

    hypotheses: List[Hypothesis] = []
    # Primary hypothesis: task is achievable with current evidence.
    hypotheses.append(
        Hypothesis(
            id="h1",
            agent_id=getattr(agent_card, "agent_id", "unknown"),
            content=f"Task '{task}' appears achievable given current evidence.",
            confidence=base_conf,
            evidence_ids=evidence_ids,
            rationale=None,
        )
    )

    # Optional second hypothesis if we have at least some evidence.
    if count > 0:
        hypotheses.append(
            Hypothesis(
                id="h2",
                agent_id=getattr(agent_card, "agent_id", "unknown"),
                content="Additional evidence may improve specificity of the draft.",
                confidence=max(0.1, base_conf - 0.1),
                evidence_ids=evidence_ids[: max(1, len(evidence_ids) // 2)],
                rationale="Derived from partial evidence coverage.",
            )
        )

    return hypotheses



