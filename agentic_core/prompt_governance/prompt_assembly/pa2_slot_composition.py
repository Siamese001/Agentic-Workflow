"""PA.2 Slot composition — canonical slot order, authority stack, override rules.

Implements the canonical 10-slot order from the spec (lines 832–890):

    S0 → D0 → I0 → E0 → C0 → Y0 → M0 → U0 → H0
    (R0 is a structural binding, not an in-prompt slot — included in the
    AuthorityStack at the lowest tier.)

The :class:`AuthorityStack` enforces "higher authority wins on conflict";
:func:`compose_slots` returns an ordered list of `(slot_code, content)`
plus the resolved :class:`AuthorityStack` ready for PA.4 validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .pa1_bom_resolver import PromptBOMResolved


SLOT_ORDER: tuple[str, ...] = ("S0", "D0", "I0", "E0", "C0", "Y0", "M0", "U0", "H0")
"""Canonical composition order. Higher slot code may override lower content."""


SLOT_AUTHORITY_RANK: dict[str, int] = {
    "S0": 100,  # System identity — highest
    "D0": 90,
    "I0": 80,
    "M0": 75,
    "Y0": 60,
    "C0": 50,  # data, never instruction
    "E0": 40,
    "U0": 30,  # user request — lowest non-healing
    "H0": 20,  # healing proposal — lowest, never overrides
    "R0": 10,  # schema binding — structural
}


@dataclass(frozen=True)
class SlotEntry:
    code: str
    content: str
    authority_rank: int


@dataclass(frozen=True)
class OverrideRule:
    """A single override rule from the spec authority stack."""

    higher: str
    lower: str
    rationale: str


# Spec OVERRIDE RULES (PA.2 §authority stack):
OVERRIDE_RULES: tuple[OverrideRule, ...] = (
    OverrideRule("S0", "D0", "system identity always wins over fences"),
    OverrideRule("S0", "I0", "system identity always wins over instructional"),
    OverrideRule("S0", "U0", "system identity always wins over user task"),
    OverrideRule("S0", "C0", "system identity always wins over retrieved content"),
    OverrideRule("S0", "H0", "system identity always wins over healing hints"),
    OverrideRule("D0", "I0", "fences override instructional pattern"),
    OverrideRule("D0", "U0", "fences override user requests"),
    OverrideRule("D0", "C0", "fences override retrieved content"),
    OverrideRule("I0", "U0", "instructional pattern overrides user phrasing"),
    OverrideRule("I0", "C0", "instructional treats retrieved content as data, not orders"),
)


@dataclass(frozen=True)
class AuthorityStack:
    """Spec PA.2 authority stack — ordered top-to-bottom."""

    entries: tuple[SlotEntry, ...]
    override_rules: tuple[OverrideRule, ...] = OVERRIDE_RULES

    def has_slot(self, code: str) -> bool:
        return any(e.code == code for e in self.entries)

    def slot(self, code: str) -> SlotEntry | None:
        for e in self.entries:
            if e.code == code:
                return e
        return None

    def is_higher(self, a: str, b: str) -> bool:
        """Return True iff slot ``a`` outranks slot ``b``."""
        return SLOT_AUTHORITY_RANK.get(a, 0) > SLOT_AUTHORITY_RANK.get(b, 0)


@dataclass(frozen=True)
class CompositionResult:
    """Output of :func:`compose_slots`."""

    ordered: tuple[SlotEntry, ...]
    stack: AuthorityStack
    skipped: tuple[str, ...] = field(default_factory=tuple)


def _content_for(bom: PromptBOMResolved, code: str) -> str:
    return {
        "S0": bom.s0.content,
        "D0": bom.d0.content,
        "I0": bom.i0.content,
        "E0": bom.e0.content,
        "C0": _c0_text(bom),
        "M0": bom.m0.content,
        "U0": bom.u0.content,
        "Y0": bom.y0.content,
        "H0": bom.h0.content if bom.h0.accepted else "",
    }.get(code, "")


def _c0_text(bom: PromptBOMResolved) -> str:
    parts: list[str] = []
    for label, items in (
        ("MUST_USE", bom.c0.must_use),
        ("SUPPORTING", bom.c0.supporting),
        ("CONTRADICTS", bom.c0.contradicts),
        ("BACKGROUND", bom.c0.background),
    ):
        if items:
            parts.append(f"[{label}]")
            for it in items:
                parts.append(str(it.get("text") or it.get("id") or it))
    return "\n".join(parts)


def compose_slots(
    bom: PromptBOMResolved,
    *,
    skip: Iterable[str] = (),
) -> CompositionResult:
    """Compose slot blocks into canonical order with an authority stack."""
    skip_set = set(skip)
    entries: list[SlotEntry] = []
    skipped: list[str] = []
    for code in SLOT_ORDER:
        if code in skip_set:
            skipped.append(code)
            continue
        content = _content_for(bom, code)
        if not content:
            continue
        entries.append(SlotEntry(code=code, content=content, authority_rank=SLOT_AUTHORITY_RANK[code]))
    stack = AuthorityStack(entries=tuple(entries))
    return CompositionResult(ordered=tuple(entries), stack=stack, skipped=tuple(skipped))


def detect_authority_violations(stack: AuthorityStack) -> tuple[str, ...]:
    """Detect cases where lower-authority slots try to override higher ones.

    Heuristics: a lower slot containing 'override system', 'ignore developer
    fences', or 'as the system' is flagged.
    """
    violations: list[str] = []
    triggers = {
        "U0": ("override system", "ignore developer fences", "as the system", "act as system"),
        "C0": ("override system", "as the system", "ignore previous instructions"),
        "H0": ("override system", "ignore developer fences"),
    }
    for entry in stack.entries:
        for needle in triggers.get(entry.code, ()):
            if needle.lower() in entry.content.lower():
                violations.append(f"{entry.code}_attempts_override:{needle}")
    return tuple(violations)


__all__ = [
    "AuthorityStack",
    "CompositionResult",
    "OVERRIDE_RULES",
    "OverrideRule",
    "SLOT_AUTHORITY_RANK",
    "SLOT_ORDER",
    "SlotEntry",
    "compose_slots",
    "detect_authority_violations",
]
