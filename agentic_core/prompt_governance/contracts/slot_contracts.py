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


SLOT_ORDER: tuple[str, ...] = ("S0", "D0", "I0", "C0", "U0")


class AirlockViolationError(Exception):
    """Raised when a user prompt (U0) attempts to bypass the L1→L0 Airlock gate."""
