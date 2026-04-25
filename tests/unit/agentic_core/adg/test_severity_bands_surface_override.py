"""Tests for ADR-024 Part B SURFACE_OVERRIDE layer in severity_bands (W15).

Covers:
- Feature-flag off (default): effective_severity() returns base unchanged.
- Feature-flag on: SURFACE_OVERRIDE promotes severity when (kind, marker) matches.
- Non-prod paths (tests/, tools/, docs/) don't trigger 'prod' marker.
- L0/L5 file paths trigger L0/L5 markers.
- Write surface markers trigger for L4_state/, write_gateway, memory_authority.
- Overrides NEVER lower severity (monotonic promotion only).
- Highest-rank override wins when multiple markers match.
- effective_band wrapper round-trips band → severity → band correctly.
"""

from __future__ import annotations

import pytest

from agentic_core.adg.severity_bands import (
    SURFACE_OVERRIDE,
    effective_band,
    effective_severity,
    is_surface_override_enabled,
    resolve_surface_markers,
)


@pytest.fixture(autouse=True)
def _reset_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure each test starts with the flag unset."""
    monkeypatch.delenv("P1_RATCHET_POLICY_V2", raising=False)


class TestFlagGating:
    def test_flag_off_by_default(self) -> None:
        assert is_surface_override_enabled() is False

    @pytest.mark.parametrize("val", ["1", "true", "TRUE", "yes", "Yes", "on", "ON"])
    def test_flag_on_accepts_truthy_values(self, val: str, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", val)
        assert is_surface_override_enabled() is True

    @pytest.mark.parametrize("val", ["0", "false", "no", "off", "", "   ", "bogus"])
    def test_flag_off_rejects_falsy_values(self, val: str, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", val)
        assert is_surface_override_enabled() is False

    def test_flag_off_no_promotion(self) -> None:
        # L5 broad_exception_catch would promote LOW→MEDIUM when flag is on,
        # but returns LOW unchanged when flag is off.
        assert effective_severity("broad_exception_catch", "agentic_core/L5_safety/foo.py", "LOW") == "LOW"


class TestSurfaceMarkers:
    def test_empty_path_returns_empty(self) -> None:
        assert resolve_surface_markers("") == frozenset()

    def test_l5_path_triggers_l5_and_l5_critical(self) -> None:
        markers = resolve_surface_markers("agentic_core/L5_safety/validators/foo.py")
        assert "L5" in markers
        assert "L5_critical" in markers
        assert "prod" in markers

    def test_l0_path_triggers_l0_and_l0_critical(self) -> None:
        markers = resolve_surface_markers("agentic_core/L0_routing/path_router.py")
        assert "L0" in markers
        assert "L0_critical" in markers

    def test_l4_state_triggers_write(self) -> None:
        markers = resolve_surface_markers("agentic_core/L4_state/memory/cache.py")
        assert "write" in markers

    def test_write_gateway_triggers_write(self) -> None:
        markers = resolve_surface_markers("some/path/to/write_gateway.py")
        assert "write" in markers

    def test_memory_authority_triggers_write(self) -> None:
        markers = resolve_surface_markers("agentic_core/some/memory_authority.py")
        assert "write" in markers

    def test_tests_path_excludes_prod(self) -> None:
        assert "prod" not in resolve_surface_markers("tests/unit/foo.py")

    def test_tools_path_excludes_prod(self) -> None:
        assert "prod" not in resolve_surface_markers("tools/debug/foo.py")

    def test_docs_path_excludes_prod(self) -> None:
        assert "prod" not in resolve_surface_markers("docs/architecture/foo.py")

    def test_backslash_separator_accepted(self) -> None:
        # Windows-style path must match the same way
        markers = resolve_surface_markers(r"agentic_core\L5_safety\foo.py")
        assert "L5" in markers


class TestPromotion:
    def test_l5_broad_catch_p3_to_p2(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        assert effective_severity("broad_exception_catch", "agentic_core/L5_safety/foo.py", "LOW") == "MEDIUM"

    def test_l0_silent_swallow_p3_to_p1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        assert (
            effective_severity("silent_exception_swallow", "agentic_core/L0_routing/foo.py", "LOW") == "HIGH"
        )

    def test_write_partial_side_effects_p2_to_p1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        assert (
            effective_severity("partial_side_effects", "agentic_core/L4_state/writer.py", "MEDIUM") == "HIGH"
        )

    def test_prod_retry_without_backoff_p2_to_p1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        assert (
            effective_severity(
                "retry_without_backoff",
                "agentic_core/L2_execution/runner.py",
                "MEDIUM",
            )
            == "HIGH"
        )

    def test_never_lowers_severity(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        # Even though L5 broad_catch has MEDIUM override, a CRITICAL base stays CRITICAL.
        assert (
            effective_severity("broad_exception_catch", "agentic_core/L5_safety/foo.py", "CRITICAL")
            == "CRITICAL"
        )

    def test_no_override_for_unknown_kind(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        assert effective_severity("no_such_kind", "agentic_core/L5_safety/foo.py", "LOW") == "LOW"

    def test_no_override_for_unmapped_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        # silent_exception_swallow is only promoted on L0/L5, not L3.
        assert (
            effective_severity(
                "silent_exception_swallow",
                "agentic_core/L3_orchestration/foo.py",
                "LOW",
            )
            == "LOW"
        )

    def test_invalid_base_severity_returns_unchanged(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        assert effective_severity("broad_exception_catch", "foo.py", "UNKNOWN") == "UNKNOWN"


class TestEffectiveBand:
    def test_band_wrapper_flag_off(self) -> None:
        # P3 should stay P3 when flag is off
        assert effective_band("broad_exception_catch", "agentic_core/L5_safety/foo.py", "P3") == "P3"

    def test_band_wrapper_flag_on_promotes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        assert effective_band("broad_exception_catch", "agentic_core/L5_safety/foo.py", "P3") == "P2"

    def test_band_wrapper_l0_swallow_p3_to_p1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("P1_RATCHET_POLICY_V2", "1")
        assert effective_band("silent_exception_swallow", "agentic_core/L0_routing/foo.py", "P3") == "P1"


class TestSurfaceOverrideTable:
    def test_table_is_finite_and_non_empty(self) -> None:
        # Sanity: closed-set table with a fixed number of rows.
        assert 8 <= len(SURFACE_OVERRIDE) <= 20

    def test_all_markers_resolvable(self) -> None:
        # Every marker in the table must be producible by resolve_surface_markers
        # on at least one synthetic path (proves integration consistency).
        test_paths = {
            "write": "agentic_core/L4_state/writer.py",
            "prod": "agentic_core/L2_execution/foo.py",
            "L0": "agentic_core/L0_routing/foo.py",
            "L0_critical": "agentic_core/L0_routing/foo.py",
            "L5": "agentic_core/L5_safety/foo.py",
            "L5_critical": "agentic_core/L5_safety/foo.py",
        }
        used_markers = {marker for (_kind, marker) in SURFACE_OVERRIDE}
        for marker in used_markers:
            assert marker in test_paths, f"marker {marker!r} has no synthetic path"
            assert marker in resolve_surface_markers(test_paths[marker])
