"""Typed slot contracts for Zero-Loss Taxonomy prompt assembly.

No pydantic. No runtime imports beyond stdlib. No behavior methods.
All dataclasses are frozen (immutable).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SlotS0:
    """SYSTEM / STATE slot — ABSOLUTE authority. Hard-coded constitutions + invariants."""

    content: str


@dataclass(frozen=True)
class SlotD0:
    """INJECTIONS slot — BINDING authority. Role fences, tool constraints, scope boundaries."""

    content: str
    authority: str


@dataclass(frozen=True)
class SlotI0:
    """INSTRUCTIONAL slot — GOVERNED authority. Identity and mixin capability definitions."""

    content: str


@dataclass(frozen=True)
class SlotC0:
    """DEPENDENCY slot — INFORMATIONAL authority. Validated context payload (RAG/citations)."""

    content: dict


@dataclass(frozen=True)
class SlotU0:
    """USER PROMPT slot — ZERO authority. Raw intent from L1; must pass Airlock before L0."""

    content: str


@dataclass(frozen=True)
class SlotE0:
    """EXEMPLARS slot — GUIDING authority. Golden Context, few-shot examples, best-in-class patterns."""

    content: str


@dataclass(frozen=True)
class SlotM0:
    """META-COGNITIVE slot — PRIVATE authority. Chain-of-Thought, Tree-of-Thought internal reasoning."""

    content: str


@dataclass(frozen=True)
class SlotY0:
    """SYNTHESIS slot — ANALYTIC authority. Pattern analysis, telemetry summarization, meta-learning proposals."""

    content: dict


@dataclass(frozen=True)
class SlotH0:
    """HEALING PROPOSAL slot — PROPOSED authority. L2.3 healing corrections with re-entry validation required."""

    content: str
    requires_reentry: bool = True


@dataclass(frozen=True)
class SlotR0:
    """OUTPUT FORMAT slot — SCHEMA authority. Response schema, format constraints, structural requirements."""

    content: str


SLOT_ORDER: tuple[str, ...] = ("S0", "D0", "M0", "I0", "E0", "C0", "Y0", "U0", "H0", "R0")


class SlotOrderViolation(Exception):
    """Raised when assembled prompt slot tags violate the canonical SLOT_ORDER.

    REQ-PT-011: Negative control — tampered slot order MUST be detected and
    rejected at assembly time.  Fail-closed: missing or misordered slots
    abort prompt assembly.
    """


def validate_slot_order(prompt_text: str) -> None:
    """Enforce canonical SLOT_ORDER in an assembled prompt.

    Scans *prompt_text* for ``<SLOT_XX>`` open-tags and verifies:
    1. Every slot in ``SLOT_ORDER`` appears at least once.
    2. Their first-occurrence positions are strictly ascending (S0 < D0 < I0 < C0 < U0).

    Raises:
        SlotOrderViolation: on missing or misordered slots.
    """
    positions: list[tuple[str, int]] = []
    for slot_key in SLOT_ORDER:
        tag = f"<SLOT_{slot_key}>"
        idx = prompt_text.find(tag)
        if idx == -1:
            raise SlotOrderViolation(f"SLOT_MISSING: <SLOT_{slot_key}> not found in assembled prompt")
        positions.append((slot_key, idx))
    for i in range(1, len(positions)):
        prev_key, prev_pos = positions[i - 1]
        curr_key, curr_pos = positions[i]
        if curr_pos <= prev_pos:
            raise SlotOrderViolation(
                f"SLOT_ORDER_VIOLATED: <SLOT_{curr_key}> (pos {curr_pos}) must appear after <SLOT_{prev_key}> (pos {prev_pos})",
            )


class AirlockViolationError(Exception):
    """Raised when a user prompt (U0) attempts to bypass the L1→L0 Airlock gate."""
