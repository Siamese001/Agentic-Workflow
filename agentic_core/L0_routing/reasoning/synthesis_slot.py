"""Y1 Synthesis Slot — pattern-analysis content stream for prompt assembly.

Closes the documentation drift identified in
`docs/reference/prompting/current_architecture_crossmap.md` row 7:

    | 7 | SYNTHESIS (Pattern Analysis) | — | ❌ no slot;
        `SynthesisMixin` bypasses assembler |

The historical "SynthesisMixin" never existed as code — it was an aspirational
crossmap entry. This module formalizes the synthesis slot as Y1 (sibling to
the existing Y0 tool-policy slot) so that pattern-analysis material flows
through the assembler instead of being silently appended elsewhere.

Plan: prompt-assembly-reception-hardening-9c4e2b W6 (RH6.1)

Design:
  - `SynthesisProvider` Protocol — any module can produce synthesis text.
  - `compose_synthesis_slot(providers, max_tokens)` — deterministic
    concatenation with bounded length.
  - `Y1` is rendered into the system plane via the existing canonical-render
    pipeline (provider_adapters tolerates unknown slot names safely).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(frozen=True)
class SynthesisFragment:
    """One synthesis input — a pattern observation, lesson, or principle.

    Attributes:
        text: The synthesis content (will be wrapped, never mutated).
        priority: Higher → preserved under truncation. Default 0.5.
        source_id: Stable identifier for replay/debug. Empty allowed.
    """

    text: str
    priority: float = 0.5
    source_id: str = ""


class SynthesisProvider(Protocol):
    """Provider contract — anything that can emit synthesis fragments."""

    def collect(self) -> Iterable[SynthesisFragment]:
        """Return zero or more fragments for the current request."""
        ...


def compose_synthesis_slot(
    providers: Iterable[SynthesisProvider],
    *,
    max_tokens: int = 800,
    chars_per_token: int = 4,
) -> str:
    """Compose the Y1 synthesis slot string from a list of providers.

    Deterministic: providers are iterated in caller-supplied order, fragments
    are sorted by priority desc then by insertion order, and truncation
    happens at fragment boundaries (no mid-fragment cuts).

    Args:
        providers: Iterable of SynthesisProvider instances.
        max_tokens: Soft cap. Total assembled chars ≤ max_tokens * chars_per_token.
        chars_per_token: Conversion factor — 4 matches the assembler default.

    Returns:
        Composed synthesis string. Empty if no fragments collected.
    """
    char_budget = max(0, max_tokens * chars_per_token)
    if char_budget == 0:
        return ""

    # Collect all fragments preserving insertion order.
    indexed: list[tuple[int, SynthesisFragment]] = []
    seq = 0
    for provider in providers:
        try:
            for frag in provider.collect():
                indexed.append((seq, frag))
                seq += 1
        except (RuntimeError, ValueError, AttributeError, TypeError):
            # Defensive: a flaky provider must not crash the assembler.
            continue

    if not indexed:
        return ""

    # Sort: priority desc, insertion order asc (stable tie-break).
    indexed.sort(key=lambda pair: (-pair[1].priority, pair[0]))

    parts: list[str] = []
    used_chars = 0
    for _, frag in indexed:
        text = frag.text.strip()
        if not text:
            continue
        # +2 for the separator newlines we'll add between fragments.
        sep_overhead = 2 if parts else 0
        if used_chars + len(text) + sep_overhead > char_budget:
            # Skip rather than truncate — preserves fragment boundaries.
            continue
        parts.append(text)
        used_chars += len(text) + sep_overhead

    return "\n\n".join(parts)


# Convenience: one-shot helper for callers that have a static list.
def compose_from_fragments(fragments: Iterable[SynthesisFragment], *, max_tokens: int = 800) -> str:
    """Like `compose_synthesis_slot` but takes fragments directly."""

    class _StaticProvider:
        def __init__(self, frags: list[SynthesisFragment]) -> None:
            self._frags = frags

        def collect(self) -> Iterable[SynthesisFragment]:
            return self._frags

    return compose_synthesis_slot([_StaticProvider(list(fragments))], max_tokens=max_tokens)
