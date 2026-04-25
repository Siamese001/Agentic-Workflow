"""RH4 — Exemplar Bank for E0 slot population.

Stores curated few-shot examples per (intent_class, agent_id) and serves them
deterministically at assembly time. Used to satisfy the "≥3 exemplars for
eligible prompts" reception-hardening rule.

Doctrinal anchor: Anthropic A6, Google G6 — uniform format across examples
Plan: prompt-assembly-reception-hardening-9c4e2b W4 (RH4.1, RH4.2)

Design:
  - In-process registry seeded by callers; no I/O at import time.
  - Lookup is deterministic: (intent_class, agent_id) → tuple of exemplars
    in insertion order. Two retrievals with the same key return identical
    tuples (replay-stable).
  - Static-similarity scoring (token-overlap) is provided as an opt-in
    helper. Dynamic embedding-based selection is a future wave (W7).

Exemplar format: each entry is an `Exemplar` with `task`, `response`, and
optional `tags`. The `format_for_e0` helper renders a tuple of exemplars
into the canonical `<example>...</example>` XML block.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Iterable


@dataclass(frozen=True)
class Exemplar:
    """One few-shot example.

    Attributes:
        task: The user-side prompt or task description.
        response: The desired model response.
        tags: Optional metadata tags for filtering (e.g. 'json', 'tool-use').
        weight: Static priority for ordering (higher → earlier in render).
    """

    task: str
    response: str
    tags: tuple[str, ...] = ()
    weight: float = 1.0


@dataclass
class _BankEntry:
    """Internal registry value — list of exemplars with a write lock."""

    exemplars: list[Exemplar] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)


class ExemplarBank:
    """Per-intent registry of exemplars, deterministic lookup."""

    MIN_EXEMPLARS_PER_PROMPT: int = 3

    def __init__(self) -> None:
        self._registry: dict[tuple[str, str], _BankEntry] = {}
        self._registry_lock: Lock = Lock()

    def register(
        self,
        intent_class: str,
        agent_id: str,
        exemplars: Iterable[Exemplar],
    ) -> None:
        """Register one or more exemplars for `(intent_class, agent_id)`.

        Idempotent for identical exemplars: duplicates by `(task, response)`
        are skipped to keep replay-key determinism stable.
        """
        if not intent_class or not agent_id:
            raise ValueError("intent_class and agent_id are required")
        key = (intent_class, agent_id)
        with self._registry_lock:
            entry = self._registry.setdefault(key, _BankEntry())
        with entry.lock:
            existing_keys = {(e.task, e.response) for e in entry.exemplars}
            for ex in exemplars:
                if (ex.task, ex.response) in existing_keys:
                    continue
                entry.exemplars.append(ex)
                existing_keys.add((ex.task, ex.response))

    def get(self, intent_class: str, agent_id: str, *, max_count: int | None = None) -> tuple[Exemplar, ...]:
        """Return exemplars for the key in deterministic weight-then-order.

        Args:
            intent_class: Routing intent class.
            agent_id: Calling agent identifier.
            max_count: If provided, return at most this many exemplars.

        Returns:
            Tuple of exemplars sorted by (-weight, insertion_order).
            Empty tuple if no entry registered.
        """
        key = (intent_class, agent_id)
        with self._registry_lock:
            entry = self._registry.get(key)
        if entry is None:
            return ()
        with entry.lock:
            # Stable sort: higher weight first, ties broken by insertion order
            indexed = list(enumerate(entry.exemplars))
            indexed.sort(key=lambda pair: (-pair[1].weight, pair[0]))
            ordered = tuple(ex for _, ex in indexed)
        if max_count is not None and max_count > 0:
            return ordered[:max_count]
        return ordered

    def has_enough(self, intent_class: str, agent_id: str, threshold: int | None = None) -> bool:
        """Check whether the entry meets the reception-hardening threshold."""
        key = (intent_class, agent_id)
        with self._registry_lock:
            entry = self._registry.get(key)
        if entry is None:
            return False
        with entry.lock:
            count = len(entry.exemplars)
        return count >= (threshold or self.MIN_EXEMPLARS_PER_PROMPT)

    def clear(self) -> None:
        """Reset the registry — for tests only."""
        with self._registry_lock:
            self._registry.clear()


def format_for_e0(exemplars: Iterable[Exemplar]) -> str:
    """Render exemplars as a canonical `<examples>` XML block for E0.

    Anthropic A6 / Google G6 best practice: uniform format across examples,
    no mixed templates. This produces:

        <examples>
          <example>
            <task>...</task>
            <response>...</response>
          </example>
          ...
        </examples>

    Empty input returns an empty string (so caller can omit E0 entirely).
    """
    items = list(exemplars)
    if not items:
        return ""
    parts: list[str] = ["<examples>"]
    for ex in items:
        parts.append("  <example>")
        parts.append(f"    <task>{_escape_xml(ex.task)}</task>")
        parts.append(f"    <response>{_escape_xml(ex.response)}</response>")
        parts.append("  </example>")
    parts.append("</examples>")
    return "\n".join(parts)


def _escape_xml(text: str) -> str:
    """Minimal XML escaping for exemplar payloads.

    We escape only the four characters that would break the wrapper:
    `&`, `<`, `>`, and `"`. This is sufficient because the exemplar content
    is rendered inside element bodies, not attributes, and providers tolerate
    apostrophes in text content.
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# Module-level singleton for app-wide use. Tests should call .clear() in
# fixtures or instantiate their own ExemplarBank() to avoid cross-test bleed.
_GLOBAL_BANK: ExemplarBank = ExemplarBank()


def get_global_bank() -> ExemplarBank:
    """Return the process-wide exemplar bank singleton."""
    return _GLOBAL_BANK


def static_similarity_score(query: str, exemplar: Exemplar) -> float:
    """Token-overlap score between `query` and an exemplar's task.

    Returns a float in [0.0, 1.0]. Used for opt-in static ranking before the
    embedding-based ranker arrives in W7. Deterministic and free of network
    dependencies.
    """
    if not query or not exemplar.task:
        return 0.0
    q_tokens = set(query.lower().split())
    e_tokens = set(exemplar.task.lower().split())
    if not q_tokens or not e_tokens:
        return 0.0
    intersection = len(q_tokens & e_tokens)
    union = len(q_tokens | e_tokens)
    return intersection / union if union else 0.0
