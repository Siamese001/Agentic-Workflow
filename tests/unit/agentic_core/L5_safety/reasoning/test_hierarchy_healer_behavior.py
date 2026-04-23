"""Behavioral tests for ``agentic_core.L5_safety.reasoning.hierarchy_healer``.

The module is a ~100KB unified hierarchy agent. Full behavior requires a
simulated project tree, which is out of scope here. Locked behaviors:

- Module imports and exposes expected public API.
- HierarchyHealerAgent constructor: project_root resolution, healing_enabled
  default, ctx/auto_approve propagation, archive_root computation, gatekeeper
  singleton wiring, archive dir created when healing_enabled=True.
- Backward-compat alias HierarchyAgent == HierarchyHealerAgent.
- get_hierarchy_agent singleton accessor.
- Re-exported helpers get_best_target_l1 / get_best_target_l2 callable.
"""

from __future__ import annotations

from pathlib import Path

from agentic_core.L5_safety.reasoning.hierarchy_healer import (
    HEALING_BACKUPS_DIR,
    HierarchyAgent,
    HierarchyHealerAgent,
    get_best_target_l1,
    get_best_target_l2,
    get_hierarchy_agent,
)
from agentic_core.L5_safety.reasoning import hierarchy_healer as mod


# ---- Constructor ---------------------------------------------------


class TestHierarchyHealerAgentConstruction:
    def test_project_root_resolved(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path.resolve()
        assert agent.project_root.is_absolute()

    def test_healing_enabled_default(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path)
        assert agent.healing_enabled is True

    def test_healing_disabled_mode(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path, healing_enabled=False)
        assert agent.healing_enabled is False

    def test_ctx_default_none(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path)
        assert agent.ctx is None

    def test_ctx_passthrough(self, tmp_path: Path) -> None:
        sentinel = object()
        agent = HierarchyHealerAgent(project_root=tmp_path, ctx=sentinel)
        assert agent.ctx is sentinel

    def test_archive_root_computed(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path)
        expected = tmp_path / HEALING_BACKUPS_DIR / "hierarchy_violations"
        assert agent.archive_root == expected

    def test_agent_name(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path)
        assert agent.agent_name == "HierarchyAgent"

    def test_gatekeeper_wired(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path)
        # Gatekeeper is a singleton for this project_root
        assert agent.gatekeeper is not None
        assert hasattr(agent.gatekeeper, "set_require_approval")

    def test_auto_approve_disables_gatekeeper_approval(
        self,
        tmp_path: Path,
        monkeypatch,
    ) -> None:
        captured = {}

        def fake_set_require(flag: bool) -> None:
            captured["flag"] = flag

        # Reset the singleton so our patch takes effect freshly
        from agentic_core.L5_safety.enforcement import archival_gatekeeper_gate as ag

        ag.ArchivalGatekeeper._instance = None  # type: ignore[attr-defined]

        agent = HierarchyHealerAgent(project_root=tmp_path, auto_approve=True)
        monkeypatch.setattr(
            agent.gatekeeper,
            "set_require_approval",
            fake_set_require,
        )
        # Simulate reconstruction to trigger the branch
        agent2 = HierarchyHealerAgent(project_root=tmp_path, auto_approve=True)
        # set_require_approval(False) was called somewhere — check behavior
        # by inspecting current gatekeeper state (private field name varies)
        internal = getattr(agent2.gatekeeper, "_require_approval", None)
        assert internal is False

    def test_archive_dir_created_when_healing(self, tmp_path: Path) -> None:
        HierarchyHealerAgent(project_root=tmp_path, healing_enabled=True)
        expected = tmp_path / HEALING_BACKUPS_DIR / "hierarchy_violations"
        assert expected.is_dir()


# ---- Backward-compat alias ----------------------------------------


class TestAlias:
    def test_hierarchy_agent_alias(self) -> None:
        assert HierarchyAgent is HierarchyHealerAgent


# ---- Singleton accessor ------------------------------------------


class TestSingletonAccessor:
    def test_returns_same_instance(self, tmp_path: Path) -> None:
        # Reset the module-level singleton so we control the lifecycle
        mod._hierarchy_agent_instance = None
        first = get_hierarchy_agent(tmp_path)
        second = get_hierarchy_agent(tmp_path)
        assert first is second

    def test_instance_type(self, tmp_path: Path) -> None:
        mod._hierarchy_agent_instance = None
        agent = get_hierarchy_agent(tmp_path)
        assert isinstance(agent, HierarchyHealerAgent)


# ---- Re-exported helpers -----------------------------------------


class TestReexportedHelpers:
    def test_get_best_target_l1_callable(self) -> None:
        assert callable(get_best_target_l1)

    def test_get_best_target_l2_callable(self) -> None:
        assert callable(get_best_target_l2)


# ---- Module-level imports ----------------------------------------


class TestModuleSurface:
    def test_has_agent_class(self) -> None:
        assert hasattr(mod, "HierarchyHealerAgent")

    def test_has_healing_backups_dir(self) -> None:
        assert hasattr(mod, "HEALING_BACKUPS_DIR")
        assert isinstance(mod.HEALING_BACKUPS_DIR, str)

    def test_has_alias(self) -> None:
        assert hasattr(mod, "HierarchyAgent")


# ---- heal() dispatcher behavior ----------------------------------


class TestHealDispatcher:
    """Exercise the heal() public method's observed status vocabulary.

    The outer heal() is wrapped by @standard_heal (SovereignBaseAgent) which
    normalizes returns into: status in {'success', 'error', 'skipped',
    'manual_required'} with an ``error`` field on failure. These tests lock
    the OBSERVED envelope, not the inner heal() implementation.
    """

    _ALLOWED_STATUS = {"success", "error", "skipped", "manual_required", "partial_success", "failed"}

    def test_heal_non_dict_returns_error_status(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal("not a dict")  # type: ignore[arg-type]
        assert result["status"] == "error"
        assert "error" in result
        assert "dict" in str(result["error"]).lower()

    def test_heal_missing_file_path_is_skipped(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal({"type": "STRUCTURE"})
        assert result["status"] in {"skipped", "manual_required", "error"}

    def test_heal_unknown_violation_type_manual_required(self, tmp_path: Path) -> None:
        """Unknown violation types exit the dispatcher with 'manual_required'."""
        agent = HierarchyHealerAgent(project_root=tmp_path, healing_enabled=True)
        result = agent.heal({"type": "NONSENSE_TYPE", "file": str(tmp_path / "x.py")})
        assert result["status"] == "manual_required"

    def test_heal_structure_disabled_manual_required(self, tmp_path: Path) -> None:
        """Disabled healing on a known violation type surfaces as 'manual_required'."""
        agent = HierarchyHealerAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal({"type": "STRUCTURE", "file": str(tmp_path / "x.py")})
        assert result["status"] == "manual_required"

    def test_heal_depth_disabled_manual_required(self, tmp_path: Path) -> None:
        agent = HierarchyHealerAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal({"type": "DEPTH_VIOLATION", "file": str(tmp_path / "x.py")})
        assert result["status"] == "manual_required"

    def test_heal_envelope_has_status_for_every_input(self, tmp_path: Path) -> None:
        """Every heal() path returns a dict with a status key from the allowed set."""
        agent = HierarchyHealerAgent(project_root=tmp_path, healing_enabled=False)
        for violation in (
            "not a dict",
            {},
            {"type": "STRUCTURE"},
            {"type": "UNKNOWN", "file": "x.py"},
            {"type": "MISPLACED", "file": "x.py"},
            {"type": "DEPTH_EXCEEDED", "file": "x.py"},
        ):
            result = agent.heal(violation)  # type: ignore[arg-type]
            assert isinstance(result, dict), f"violation={violation!r} returned non-dict {type(result)}"
            assert "status" in result, f"violation={violation!r} missing status: {result}"
            assert result["status"] in self._ALLOWED_STATUS, (
                f"violation={violation!r} returned unknown status={result['status']!r}"
            )

    def test_heal_nonexistent_file_path_still_dispatches(self, tmp_path: Path) -> None:
        """heal() does not stat() the file_path; the dispatcher proceeds regardless."""
        agent = HierarchyHealerAgent(project_root=tmp_path, healing_enabled=False)
        result = agent.heal({"type": "STRUCTURE", "file": "/absolutely/does/not/exist.py"})
        assert isinstance(result, dict)
        assert result["status"] in self._ALLOWED_STATUS
