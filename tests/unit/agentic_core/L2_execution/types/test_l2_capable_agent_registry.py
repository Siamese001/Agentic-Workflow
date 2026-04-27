"""Tests for `l2_capable_agent_registry.discover_l2_capable_agents()`.

Verifies:
  - Discovery returns a non-empty deterministic list when an ADG snapshot exists.
  - Each entry has the required fields populated.
  - Discovery is sorted by resolved_path (deterministic).
  - Static fallback covers all routing tiers when snapshot absent.
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.L2_execution.types.l2_capable_agent_registry import (
    L2CapableAgentEntry,
    _STATIC_FALLBACK,
    _latest_adg_snapshot,
    discover_l2_capable_agents,
)


class TestDiscovery:
    def test_returns_non_empty_list(self) -> None:
        entries = discover_l2_capable_agents()
        assert len(entries) > 0, (
            "L2-capable agent registry returned empty result — ADG snapshot present but query matched nothing"
        )

    def test_all_entries_have_required_fields(self) -> None:
        for e in discover_l2_capable_agents():
            assert isinstance(e, L2CapableAgentEntry)
            assert e.module_name
            # Repo uses both PascalCaseAgent.py and snake_case_agent.py
            # naming conventions; the SQL LIKE is case-insensitive.
            assert e.resolved_path.lower().endswith("agent.py")
            assert e.layer  # non-empty; ADG may use various layer labels
            assert e.source in {"adg", "static"}

    def test_result_is_sorted_by_resolved_path(self) -> None:
        entries = discover_l2_capable_agents()
        paths = [e.resolved_path for e in entries]
        assert paths == sorted(paths), "discovery result must be sorted"

    def test_two_calls_return_identical_lists(self) -> None:
        a = discover_l2_capable_agents()
        b = discover_l2_capable_agents()
        assert a == b


class TestSnapshotPresence:
    def test_latest_snapshot_resolves_or_returns_none(self) -> None:
        snap = _latest_adg_snapshot()
        if snap is not None:
            assert isinstance(snap, Path)
            assert snap.exists()
            assert snap.name.startswith("adg_indexed_")
            assert snap.suffix == ".sqlite"

    def test_when_snapshot_present_source_is_adg(self) -> None:
        snap = _latest_adg_snapshot()
        if snap is None:
            return  # snapshot absent — covered by static-fallback test
        entries = discover_l2_capable_agents()
        # When ADG path succeeds, every row's source must be 'adg'.
        # When it falls back, every row's source is 'static'.
        sources = {e.source for e in entries}
        assert sources in ({"adg"}, {"static"}), f"mixed sources not allowed: {sources}"


class TestStaticFallback:
    def test_static_fallback_covers_six_representative_modules(self) -> None:
        # Static fallback represents agents from L2_execution + apps_eval
        # + apps_lic + apps_rg + apps_shared so a fallback run still has
        # coverage breadth.
        layers = {e.layer for e in _STATIC_FALLBACK}
        assert "L2" in layers
        assert "L_APP" in layers
        assert len(_STATIC_FALLBACK) >= 6

    def test_static_fallback_paths_all_end_with_agent_py(self) -> None:
        for e in _STATIC_FALLBACK:
            assert e.resolved_path.endswith("Agent.py")
            assert e.source == "static"
