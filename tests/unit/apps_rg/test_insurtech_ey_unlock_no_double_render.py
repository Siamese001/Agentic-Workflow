"""W6 (apps-rg-insurtech-ey-unlock-a4c0f0) — unlock reconciliation: no double-render.

Deterministic, hermetic. Documents + guards the unlock architecture:

- The final resume assembles insurtech/ey as GENERATED sections (insurtech_bullets/ey_bullets +
  narratives), NOT as locked-copy inline sections. The locked names 'insurtech'/'ey' are NOT in the
  assembled order -> no double-render.
- The locked_copy_manifest STILL lists 'insurtech'/'ey' (LOCKED_SECTION_IDS) because it sources the
  verbatim identity atoms (company_names/titles/dates) and the x2_*_preserved gates validate the
  base-resume copy. Removing them would break those gates. So the unlock was proof-gated (W1-W3),
  not assembly-gated; no assembler edit is required or safe.

This test fails if someone (a) drops the generated insurtech/ey sections from the assembled order,
or (b) adds the locked 'insurtech'/'ey' names into the assembled order (which would double-render).
"""
from __future__ import annotations

from apps_rg.runtime.internal.final_resume_assembler import (
    CANONICAL_ASSEMBLED_SECTION_ORDER,
    GENERATED_LANE_IDS,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import LOCKED_SECTION_IDS

GENERATED_ROLE_SECTIONS = (
    "insurtech_bullets",
    "insurtech_narrative",
    "ey_bullets",
    "ey_narrative",
)


def test_generated_insurtech_ey_sections_are_generated_lanes() -> None:
    for sid in GENERATED_ROLE_SECTIONS:
        assert sid in GENERATED_LANE_IDS, f"{sid} must be a generated lane"
        assert sid in CANONICAL_ASSEMBLED_SECTION_ORDER, f"{sid} must be in the assembled order"


def test_locked_employer_names_not_in_assembled_order() -> None:
    # If 'insurtech'/'ey' (locked) appeared in the assembled order alongside the generated
    # sections, the employer would render twice. They must stay out of the assembled order.
    assert "insurtech" not in CANONICAL_ASSEMBLED_SECTION_ORDER
    assert "ey" not in CANONICAL_ASSEMBLED_SECTION_ORDER


def test_locked_manifest_still_owns_identity_atoms() -> None:
    # The locked manifest must retain insurtech/ey to source the verbatim identity atoms and the
    # x2_*_preserved gates. Removing them would break locked-copy preservation, not "unlock" them.
    assert "insurtech" in LOCKED_SECTION_IDS
    assert "ey" in LOCKED_SECTION_IDS
    for atom in ("company_names", "titles", "dates", "locations"):
        assert atom in LOCKED_SECTION_IDS


def test_generated_and_locked_employer_namespaces_are_disjoint_in_assembly() -> None:
    # No section_id is simultaneously a generated lane AND a locked assembled section.
    locked_in_order = [s for s in CANONICAL_ASSEMBLED_SECTION_ORDER if s in ("insurtech", "ey")]
    assert not locked_in_order, f"locked employer sections leaked into assembled order: {locked_in_order}"
