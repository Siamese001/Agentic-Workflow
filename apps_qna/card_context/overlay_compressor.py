"""Overlay Compressor — compresses company overlay for card context.

W3.4: Compresses company overlay facts to fit within card context budget.
Ensures overlay is compact and doesn't dump raw briefing content.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W3.4
"""

from __future__ import annotations


def compress_overlay(
    *,
    overlay_facts: tuple[str, ...] = (),
    max_facts: int = 10,
    max_chars_per_fact: int = 200,
) -> tuple[str, ...]:
    """Compress company overlay facts to fit within budget.

    Args:
        overlay_facts: Raw overlay fact strings.
        max_facts: Maximum number of facts to include.
        max_chars_per_fact: Maximum characters per fact.

    Returns:
        Compressed overlay facts tuple.
    """
    compressed: list[str] = []
    for fact in overlay_facts[:max_facts]:
        if len(fact) > max_chars_per_fact:
            fact = fact[:max_chars_per_fact - 3] + "..."
        compressed.append(fact)
    return tuple(compressed)


__all__ = ["compress_overlay"]
