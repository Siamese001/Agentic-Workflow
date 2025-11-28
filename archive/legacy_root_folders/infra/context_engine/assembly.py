"""
Context assembly and pruning for résumé processing workflows.

Orchestrates relevant information into structured text blocks for optimal résumé improvement prompts.
"""

from typing import List

from .pinned import PinnedItem, filter_pinned
from .relevance import ContextItem, score_relevance
from .slots import ContextSlot, assign_to_slot


def assemble_context(
    query: str,
    pinned: List[PinnedItem],
    candidates: List[ContextItem],
    slots: List[ContextSlot],
) -> List[str]:
    """
    Assembles context strings for résumé improvement prompt generation.

    Prioritizes relevant information to ensure comprehensive résumé enhancement processing.
    """

    result: List[str] = []

    # Step 1: pinned items (shared across slots for now).
    pinned_selected = filter_pinned(pinned, max_items=sum(s.max_items for s in slots))

    # Step 2: relevance scoring.
    scored = score_relevance(query, candidates)
    ranked_candidates = [item for item, _ in scored]

    pinned_texts = [p.text for p in pinned_selected]
    candidate_texts = [c.text for c in ranked_candidates]

    for slot in slots:
        # Fill each slot with pinned first, then candidates.
        texts_for_slot = pinned_texts + candidate_texts
        assigned = assign_to_slot(slot, texts_for_slot)
        result.extend(assigned)

    return result



