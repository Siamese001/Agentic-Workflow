"""Behavioral tests for ``agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent``.

Covers the dataclass agent constructor + __post_init__ initialization. The
1500+ line agent's scan/enforce behavior requires whole-repo fixtures; locked
here is the constructor contract that consumers rely on.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
    LAYER_DIRS,
    ArchitectureGovernorAgent,
)


# ---- Dataclass defaults + __post_init__ --------------------------

class TestConstructor:
    def test_defaults(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        assert agent.healing_enabled is True
        assert agent.auto_approve is False
        assert agent.ci_mode is False

    def test_project_root_default_is_cwd(self) -> None:
        agent = ArchitectureGovernorAgent()
        assert agent.project_root == Path.cwd()

    def test_string_project_root_coerced(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=str(tmp_path))
        assert isinstance(agent.project_root, Path)

    def test_violations_list_empty(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        assert agent.violations == []

    def test_stats_shape(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        assert agent.stats == {
            "violations_found": 0,
            "violations_fixed": 0,
            "errors": 0,
            "drift_detected": 0,
        }

    def test_name_set_to_classname(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        assert agent.name == "ArchitectureGovernorAgent"

    def test_python_files_empty(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        assert agent.python_files == []

    def test_baseline_dir_path(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        assert agent.baseline_dir == tmp_path / "agentic_core" / "config" / "baselines"

    def test_audit_log_dir_path(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        assert agent.audit_log_dir == tmp_path / "logs" / "sovereign_audit"

    def test_lazy_collaborators_none(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        assert agent._structure_validator is None
        assert agent._gravity_repair_agent is None
        assert agent._archival_gatekeeper is None
        assert agent._cognitive_agent is None

    def test_adg_signals_dict(self, tmp_path: Path) -> None:
        agent = ArchitectureGovernorAgent(project_root=tmp_path)
        # adg_signals is populated from GuardianPrioritizer if ADG is loadable
        # on this env; the type guarantee is dict regardless.
        assert isinstance(agent.adg_signals, dict)

    @pytest.mark.parametrize("flag", ["healing_enabled", "auto_approve", "ci_mode"])
    def test_flags_overrideable(self, tmp_path: Path, flag: str) -> None:
        kwargs = {"project_root": tmp_path, flag: True}
        agent = ArchitectureGovernorAgent(**kwargs)
        assert getattr(agent, flag) is True


# ---- Module constants --------------------------------------------

class TestModuleConstants:
    def test_layer_dirs_is_set(self) -> None:
        assert isinstance(LAYER_DIRS, set)

    def test_layer_dirs_populated_or_empty(self) -> None:
        # CORE_SUBFOLDER_MAP can be empty on some envs (territory loader state);
        # the constant must still be a set.
        assert LAYER_DIRS is not None
