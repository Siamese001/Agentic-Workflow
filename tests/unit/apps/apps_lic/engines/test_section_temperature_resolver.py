"""Unit tests for section_temperature_resolver (W1-P3).

Covers:
- every (archetype, section) pair resolves to the expected value
- unknown archetype falls back to OTHER (base temperature unchanged)
- unknown section returns base temperature unchanged
- output is clamped to [0.0, 1.0]
- lowercase 'executive' alias normalises to EXECUTIVE
- pure function — identical inputs yield identical outputs
"""

from __future__ import annotations

import pytest

from apps_lic.engines.section_temperature_resolver import (
    SECTION_TEMPERATURE_CLAMP,
    resolve_section_temperature,
)


class TestKnownArchetypeSection:
    @pytest.mark.parametrize(
        "archetype,section,base,expected",
        [
            # C_LEVEL has negative deltas across the board
            ("C_LEVEL", "subject", 0.5, 0.3),
            ("C_LEVEL", "hook", 0.5, 0.4),
            ("C_LEVEL", "value", 0.5, 0.4),
            ("C_LEVEL", "cta", 0.5, 0.4),
            ("C_LEVEL", "signature", 0.5, 0.4),
            # EXECUTIVE: mixed
            ("EXECUTIVE", "subject", 0.5, 0.4),
            ("EXECUTIVE", "hook", 0.5, 0.5),
            ("EXECUTIVE", "cta", 0.5, 0.6),
            ("EXECUTIVE", "signature", 0.5, 0.6),
            # SENIOR_TA: hook is +0.1
            ("SENIOR_TA", "hook", 0.5, 0.6),
            ("SENIOR_TA", "cta", 0.5, 0.4),
            # RECRUITER: subject -0.1, value -0.1
            ("RECRUITER", "subject", 0.5, 0.4),
            ("RECRUITER", "value", 0.5, 0.4),
            # OTHER: zero-delta across the board
            ("OTHER", "hook", 0.5, 0.5),
            ("OTHER", "value", 0.5, 0.5),
        ],
    )
    def test_matrix(
        self, archetype: str, section: str, base: float, expected: float
    ) -> None:
        result = resolve_section_temperature(archetype, section, base)
        assert result == pytest.approx(expected, abs=1e-9)


class TestFallbacks:
    def test_unknown_archetype_uses_other(self) -> None:
        # OTHER has zero deltas everywhere → base returned unchanged.
        assert resolve_section_temperature("MARTIAN", "hook", 0.5) == pytest.approx(0.5)
        assert resolve_section_temperature("ANOTHER", "value", 0.3) == pytest.approx(0.3)

    def test_unknown_section_returns_base(self) -> None:
        assert resolve_section_temperature("EXECUTIVE", "does_not_exist", 0.5) == pytest.approx(0.5)

    def test_lowercase_executive_normalises(self) -> None:
        # MessagePlanner uses lowercase 'executive' alias; resolver accepts it.
        adj = resolve_section_temperature("executive", "cta", 0.5)
        assert adj == pytest.approx(0.6)


class TestClamping:
    def test_clamps_high(self) -> None:
        # EXECUTIVE/cta = +0.1. Base 0.95 + 0.1 = 1.05 → clamp to 1.0.
        result = resolve_section_temperature("EXECUTIVE", "cta", 0.95)
        assert result == pytest.approx(1.0)
        assert result <= SECTION_TEMPERATURE_CLAMP[1]

    def test_clamps_low(self) -> None:
        # C_LEVEL/subject = -0.2. Base 0.1 + -0.2 = -0.1 → clamp to 0.0.
        result = resolve_section_temperature("C_LEVEL", "subject", 0.1)
        assert result == pytest.approx(0.0)
        assert result >= SECTION_TEMPERATURE_CLAMP[0]

    def test_clamp_range_is_0_to_1(self) -> None:
        assert SECTION_TEMPERATURE_CLAMP == (0.0, 1.0)


class TestPurity:
    def test_deterministic(self) -> None:
        a = resolve_section_temperature("EXECUTIVE", "hook", 0.5)
        b = resolve_section_temperature("EXECUTIVE", "hook", 0.5)
        c = resolve_section_temperature("EXECUTIVE", "hook", 0.5)
        assert a == b == c

    def test_returns_float_type(self) -> None:
        # int base → float output (arithmetic promotion).
        out = resolve_section_temperature("EXECUTIVE", "hook", 0)
        assert isinstance(out, float)
