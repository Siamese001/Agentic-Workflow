"""Unit tests for outreach_experiment_cells (W4-P10)."""

from __future__ import annotations

import pytest

from apps_lic.config.outreach_experiment_cells import (
    ALL_CELLS,
    ARCHETYPES,
    CELL_ID_SEPARATOR,
    LATTICE_FINGERPRINT,
    TEMPLATES,
    ExperimentCell,
    cell_by_id,
    cell_id,
    enumerate_cells,
    is_valid_cell_id,
    lattice_fingerprint,
)


class TestLatticeShape:
    def test_45_cells(self) -> None:
        # 5 archetypes * 3 templates * 3 subject_variants.
        assert len(ALL_CELLS) == 45

    def test_archetype_count(self) -> None:
        assert len(ARCHETYPES) == 5

    def test_template_count(self) -> None:
        assert len(TEMPLATES) == 3
        assert TEMPLATES == ("initial", "followup_1", "followup_2")

    def test_every_archetype_has_nine_cells(self) -> None:
        by_archetype: dict[str, int] = {}
        for cell in ALL_CELLS:
            by_archetype[cell.archetype] = by_archetype.get(cell.archetype, 0) + 1
        for archetype in ARCHETYPES:
            assert by_archetype[archetype] == 9


class TestCellIds:
    def test_cell_id_format(self) -> None:
        cid = cell_id("EXECUTIVE", "initial", "question")
        assert cid == "EXECUTIVE.initial.question"
        assert CELL_ID_SEPARATOR in cid

    def test_dataclass_cell_id_matches_function(self) -> None:
        cell = ExperimentCell(
            archetype="EXECUTIVE", template="initial", subject_variant="question"
        )
        assert cell.cell_id == cell_id("EXECUTIVE", "initial", "question")

    def test_is_valid_cell_id_true(self) -> None:
        assert is_valid_cell_id("EXECUTIVE.initial.question")

    def test_is_valid_cell_id_false_unknown_variant(self) -> None:
        assert not is_valid_cell_id("EXECUTIVE.initial.does_not_exist")

    def test_is_valid_cell_id_false_wrong_separator(self) -> None:
        assert not is_valid_cell_id("EXECUTIVE/initial/question")

    def test_cell_by_id_roundtrip(self) -> None:
        for cell in ALL_CELLS:
            found = cell_by_id(cell.cell_id)
            assert found is not None
            assert found.cell_id == cell.cell_id

    def test_cell_by_id_unknown(self) -> None:
        assert cell_by_id("nope") is None


class TestFingerprint:
    def test_fingerprint_is_stable_string(self) -> None:
        assert isinstance(LATTICE_FINGERPRINT, str)
        assert len(LATTICE_FINGERPRINT) == 64  # sha256 hex

    def test_fingerprint_deterministic_across_calls(self) -> None:
        assert lattice_fingerprint() == lattice_fingerprint()
        assert lattice_fingerprint() == LATTICE_FINGERPRINT

    def test_enumerate_is_deterministic(self) -> None:
        a = [c.cell_id for c in enumerate_cells()]
        b = [c.cell_id for c in enumerate_cells()]
        assert a == b


class TestArchetypeAdmissibility:
    def test_senior_ta_has_pipeline_variant(self) -> None:
        cell_ids = {c.cell_id for c in ALL_CELLS}
        assert "SENIOR_TA.initial.pipeline" in cell_ids

    def test_recruiter_has_quality_filter_variant(self) -> None:
        cell_ids = {c.cell_id for c in ALL_CELLS}
        assert "RECRUITER.initial.quality_filter" in cell_ids

    def test_executive_has_mutual_ref_variant(self) -> None:
        cell_ids = {c.cell_id for c in ALL_CELLS}
        assert "EXECUTIVE.initial.mutual_ref" in cell_ids
