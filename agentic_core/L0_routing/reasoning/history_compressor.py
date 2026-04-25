"""PA.1 — Conversation History Compressor.

Deterministic compaction of conversation history when token budgets are tight.
Implements the eviction policy promised in `Prompt_Assembly_detailed.md` PA.1
(load-resolve stage) and PA.5 (token budget stage).

Doctrinal anchor: docs/reference/03_L0_Routing/Prompt Assembly/Prompt_Assembly_detailed.md PA.1, PA.5
Plan: prompt-assembly-best-practices-gap-b4e1c2 W4 (G11, G12)

Eviction policy (deterministic, replay-stable):
  1. Drop lowest-ranked evidence chunks first (rank field on HistoryItem)
  2. FIFO for conversation turns (oldest user/assistant pair drops first)
  3. Must-use items NEVER drop (preserved regardless of budget pressure)
  4. If after all drops the budget is still exceeded, raise BudgetExhausted

Determinism:
  - Sort key includes (item_kind, rank, sequence_number) — ties broken by
    insertion order so two runs with the same input produce identical output
  - No clock reads, no random sampling, no hash-bucket shuffle
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class HistoryItemKind(str, Enum):
    """Categories of history items, ordered by drop-priority (lowest first)."""

    EVIDENCE = "evidence"  # Drop first
    BACKGROUND = "background"
    CONVO_TURN = "convo_turn"  # FIFO drop
    SUPPORTING = "supporting"
    MUST_USE = "must_use"  # Never drop


@dataclass(frozen=True)
class HistoryItem:
    """One compactable item in the conversation history.

    Attributes:
        kind: Category — drives drop priority.
        content: Raw text payload.
        token_estimate: Pre-computed token count (chars/4 or provider-aware).
        rank: Lower-is-droppable. Used to break ties within a kind.
        sequence_number: Insertion order. Used for FIFO behavior on convo_turn.
        item_id: Stable identifier for replay/debugging.
    """

    kind: HistoryItemKind
    content: str
    token_estimate: int
    rank: float = 0.0
    sequence_number: int = 0
    item_id: str = ""


@dataclass(frozen=True)
class CompressionResult:
    """Outcome of a single compression pass."""

    kept_items: tuple[HistoryItem, ...]
    dropped_items: tuple[HistoryItem, ...]
    tokens_before: int
    tokens_after: int
    tokens_dropped: int
    fits_budget: bool
    items_must_use_count: int = 0


class BudgetExhausted(ValueError):
    """Raised when compression cannot fit even must-use content into budget."""


# Drop-priority order: lower index → higher drop priority (drop first).
_DROP_PRIORITY: dict[HistoryItemKind, int] = {
    HistoryItemKind.EVIDENCE: 0,
    HistoryItemKind.BACKGROUND: 1,
    HistoryItemKind.CONVO_TURN: 2,
    HistoryItemKind.SUPPORTING: 3,
    HistoryItemKind.MUST_USE: 99,  # Never droppable
}


def _drop_sort_key(item: HistoryItem) -> tuple[int, float, int]:
    """Sort key — most-droppable items come first.

    Order: (kind_priority, rank, sequence_number).
      - kind_priority ascending → evidence first
      - rank ascending → low-ranked evidence first
      - sequence_number ascending → oldest first within tied kind+rank
    """
    return (_DROP_PRIORITY[item.kind], item.rank, item.sequence_number)


def compress_history(
    items: Iterable[HistoryItem],
    available_tokens: int,
    *,
    raise_on_overflow: bool = False,
) -> CompressionResult:
    """Compress history items to fit within available_tokens.

    Deterministic given identical input — drops items in the priority order
    declared in `_DROP_PRIORITY`, breaking ties by `rank` then `sequence_number`.

    Args:
        items: Iterable of HistoryItem.
        available_tokens: Maximum total tokens permitted.
        raise_on_overflow: If True, raise BudgetExhausted when even must-use
            items exceed budget. If False (default), return a result with
            `fits_budget=False` and the must-use items intact.

    Returns:
        CompressionResult with kept_items in original sequence_number order.

    Raises:
        BudgetExhausted: When raise_on_overflow=True and must-use items
            alone exceed available_tokens.
    """
    items_list = list(items)
    tokens_before = sum(i.token_estimate for i in items_list)
    must_use = [i for i in items_list if i.kind == HistoryItemKind.MUST_USE]
    must_use_tokens = sum(i.token_estimate for i in must_use)

    # Quick path: already fits
    if tokens_before <= available_tokens:
        return CompressionResult(
            kept_items=tuple(items_list),
            dropped_items=(),
            tokens_before=tokens_before,
            tokens_after=tokens_before,
            tokens_dropped=0,
            fits_budget=True,
            items_must_use_count=len(must_use),
        )

    # Must-use exceeds budget alone — cannot compress further
    if must_use_tokens > available_tokens:
        if raise_on_overflow:
            raise BudgetExhausted(
                f"Must-use items ({must_use_tokens} tokens) exceed budget "
                f"({available_tokens} tokens); compression impossible."
            )
        # Return must-use only with fits_budget=False signal
        dropped = [i for i in items_list if i.kind != HistoryItemKind.MUST_USE]
        return CompressionResult(
            kept_items=tuple(must_use),
            dropped_items=tuple(dropped),
            tokens_before=tokens_before,
            tokens_after=must_use_tokens,
            tokens_dropped=tokens_before - must_use_tokens,
            fits_budget=False,
            items_must_use_count=len(must_use),
        )

    # Sort droppable items by drop priority — most droppable first.
    droppable = [i for i in items_list if i.kind != HistoryItemKind.MUST_USE]
    droppable.sort(key=_drop_sort_key)

    # Drop in order until under budget.
    dropped_set: set[str] = set()
    current_tokens = tokens_before
    dropped_items_list: list[HistoryItem] = []
    for item in droppable:
        if current_tokens <= available_tokens:
            break
        dropped_set.add(item.item_id or f"{item.kind.value}:{item.sequence_number}")
        dropped_items_list.append(item)
        current_tokens -= item.token_estimate

    # Reconstruct kept_items in original sequence_number order.
    kept = [i for i in items_list if (i.item_id or f"{i.kind.value}:{i.sequence_number}") not in dropped_set]
    fits = current_tokens <= available_tokens

    return CompressionResult(
        kept_items=tuple(kept),
        dropped_items=tuple(dropped_items_list),
        tokens_before=tokens_before,
        tokens_after=current_tokens,
        tokens_dropped=tokens_before - current_tokens,
        fits_budget=fits,
        items_must_use_count=len(must_use),
    )


@dataclass
class HistoryBuffer:
    """Append-only conversation history buffer with stable sequence numbers."""

    items: list[HistoryItem] = field(default_factory=list)
    _next_seq: int = 0

    def append(
        self,
        kind: HistoryItemKind,
        content: str,
        token_estimate: int,
        rank: float = 0.0,
        item_id: str = "",
    ) -> HistoryItem:
        """Append an item; assigns a stable sequence_number."""
        seq = self._next_seq
        self._next_seq += 1
        item = HistoryItem(
            kind=kind,
            content=content,
            token_estimate=token_estimate,
            rank=rank,
            sequence_number=seq,
            item_id=item_id or f"{kind.value}-{seq}",
        )
        self.items.append(item)
        return item

    def total_tokens(self) -> int:
        """Sum of token estimates across all items."""
        return sum(i.token_estimate for i in self.items)

    def compress_to(self, available_tokens: int, *, raise_on_overflow: bool = False) -> CompressionResult:
        """Compress buffer to fit budget. Buffer itself is not mutated."""
        return compress_history(self.items, available_tokens, raise_on_overflow=raise_on_overflow)

    def apply_compression(self, result: CompressionResult) -> None:
        """Replace items with the compression result's kept_items."""
        self.items = list(result.kept_items)
