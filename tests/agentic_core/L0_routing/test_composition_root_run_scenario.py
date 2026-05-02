"""Tests for the run_scenario hook added to composition_root.

NEXT_STEP 1 closure from .windsurf/plans/apps-e2e-auditability-harness-7c2a91.md
— proves the hook honors the four-value inner-status protocol and never
raises, regardless of input.
"""
from __future__ import annotations

import pytest

from agentic_core.L0_routing import composition_root


class TestRunScenarioHook:
    def test_returns_dict_always(self) -> None:
        for scenario_id in ("terminal_cache", "unknown_scenario", "", "\x00bad"):
            result = composition_root.run_scenario(scenario_id)
            assert isinstance(result, dict), f"non-dict for {scenario_id!r}"
            assert "status" in result

    def test_terminal_cache_runs_live(self) -> None:
        """terminal_cache exercises the real L4 evidence resolver."""
        result = composition_root.run_scenario("terminal_cache")
        assert result["status"] == composition_root.SCENARIO_STATUS_RAN
        assert result["resolver_deterministic"] is True
        assert result["resolver_fail_closed_default"] is True
        assert "probe_id" in result

    def test_unknown_scenario_returns_not_implemented(self) -> None:
        result = composition_root.run_scenario("grounded_read")
        assert result["status"] == composition_root.SCENARIO_STATUS_NOT_IMPLEMENTED
        assert result["scenario_id"] == "grounded_read"
        assert "implemented_scenarios" in result
        assert "terminal_cache" in result["implemented_scenarios"]

    def test_hook_never_raises_on_type_error_inputs(self) -> None:
        # Not a contract test but a defensive one — hook must not raise
        # even for garbage input types; it is exercised by the harness
        # and must degrade to error status rather than crash it.
        for garbage in (None, 42, [], {}):  # type: ignore[list-item]
            try:
                result = composition_root.run_scenario(garbage)  # type: ignore[arg-type]
            except Exception as exc:  # pragma: no cover
                pytest.fail(f"run_scenario raised on {garbage!r}: {exc}")
            assert isinstance(result, dict)
            assert result["status"] in {
                composition_root.SCENARIO_STATUS_RAN,
                composition_root.SCENARIO_STATUS_NOT_IMPLEMENTED,
                composition_root.SCENARIO_STATUS_ERROR,
                composition_root.SCENARIO_STATUS_SKIPPED,
            }

    def test_scenario_status_constants_are_distinct(self) -> None:
        values = {
            composition_root.SCENARIO_STATUS_RAN,
            composition_root.SCENARIO_STATUS_NOT_IMPLEMENTED,
            composition_root.SCENARIO_STATUS_ERROR,
            composition_root.SCENARIO_STATUS_SKIPPED,
        }
        assert len(values) == 4

    def test_run_scenario_is_exported(self) -> None:
        assert "run_scenario" in composition_root.__all__
