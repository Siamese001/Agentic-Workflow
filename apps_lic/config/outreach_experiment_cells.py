"""Outreach experiment cell lattice (A/B/C/D).

W4-P10 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35, Bundle B).

Defines the 3-axis experiment lattice that the reply-signal feedback
loop uses to attribute reply rate to treatment. Every outreach message
maps to exactly one cell via ``cell_id(archetype, template, subject_variant)``.

Axes
----
archetype (A, 5 levels):
    EXECUTIVE, C_LEVEL, SENIOR_TA, RECRUITER, OTHER
template (B, 3 levels):
    initial, followup_1, followup_2
subject_variant (C, 3 levels — set by SubjectLineVariantSelector, W1-P1):
    question, observation, mutual_ref / pipeline / quality_filter

Total: 5 x 3 x 3 = 45 cells.

The lattice is intentionally small so per-cell posteriors converge in
realistic campaign volumes. Cells are frozen by ``lattice_fingerprint``
at experiment start so the binder can detect lattice drift.

Cell IDs
--------
Stable string form: ``<archetype>.<template>.<subject_variant>``.
Examples:
    EXECUTIVE.initial.question
    SENIOR_TA.followup_1.pipeline
    OTHER.followup_2.quality_filter
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Final, Tuple

from apps_lic.config.subject_line_bandit_config import (
    ADMISSIBLE_VARIANTS,
)

# Canonical archetype axis (A). Matches ProfilePlanner + W1-P1 bandit.
ARCHETYPES: Final[Tuple[str, ...]] = (
    "EXECUTIVE",
    "C_LEVEL",
    "SENIOR_TA",
    "RECRUITER",
    "OTHER",
)

# Template axis (B). Matches W3-P9 FollowupCadenceEngine templates.
TEMPLATES: Final[Tuple[str, ...]] = ("initial", "followup_1", "followup_2")

# Cell-id separator. Chosen to be URL-safe and regex-stable.
CELL_ID_SEPARATOR: Final[str] = "."


@dataclass(frozen=True)
class ExperimentCell:
    """One treatment cell in the outreach experiment lattice.

    Attributes:
        archetype: One of ``ARCHETYPES``.
        template: One of ``TEMPLATES``.
        subject_variant: One of the archetype-admissible subject variants
            from W1-P1's bandit config.
        cell_id: Stable ``<archetype>.<template>.<subject_variant>`` string.
    """

    archetype: str
    template: str
    subject_variant: str
    cell_id: str = field(init=False)

    def __post_init__(self) -> None:
        cid = CELL_ID_SEPARATOR.join(
            (self.archetype, self.template, self.subject_variant)
        )
        # Frozen dataclass — bypass immutability via object.__setattr__.
        object.__setattr__(self, "cell_id", cid)


def cell_id(archetype: str, template: str, subject_variant: str) -> str:
    """Compute the canonical cell_id string without constructing a dataclass."""
    return CELL_ID_SEPARATOR.join((archetype, template, subject_variant))


def enumerate_cells() -> Tuple[ExperimentCell, ...]:
    """Materialise the full 5 x 3 x 3 = 45-cell lattice.

    Cells are emitted in deterministic order for stable fingerprinting:
    (archetype ASC, template ASC, subject_variant ASC).
    """
    cells: list[ExperimentCell] = []
    for archetype in ARCHETYPES:
        variants = ADMISSIBLE_VARIANTS.get(
            archetype,
            ADMISSIBLE_VARIANTS["OTHER"],
        )
        for template in TEMPLATES:
            for variant in variants:
                cells.append(
                    ExperimentCell(
                        archetype=archetype,
                        template=template,
                        subject_variant=variant,
                    )
                )
    return tuple(cells)


def lattice_fingerprint() -> str:
    """Return a stable SHA256 fingerprint of the materialised lattice.

    The binder records this at experiment start; a mismatch on replay
    indicates lattice drift (cell added / removed) and invalidates prior
    per-cell measurements.
    """
    cells = enumerate_cells()
    payload = "\n".join(c.cell_id for c in cells).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# Materialise once at import time — cheap, deterministic.
ALL_CELLS: Final[Tuple[ExperimentCell, ...]] = enumerate_cells()
LATTICE_FINGERPRINT: Final[str] = lattice_fingerprint()


def is_valid_cell_id(candidate: str) -> bool:
    """Return True iff ``candidate`` matches a materialised cell_id."""
    return candidate in {c.cell_id for c in ALL_CELLS}


def cell_by_id(cell_id_str: str) -> ExperimentCell | None:
    """Look up an ``ExperimentCell`` by its string id, or None."""
    for cell in ALL_CELLS:
        if cell.cell_id == cell_id_str:
            return cell
    return None


__all__ = [
    "ALL_CELLS",
    "ARCHETYPES",
    "CELL_ID_SEPARATOR",
    "ExperimentCell",
    "LATTICE_FINGERPRINT",
    "TEMPLATES",
    "cell_by_id",
    "cell_id",
    "enumerate_cells",
    "is_valid_cell_id",
    "lattice_fingerprint",
]
