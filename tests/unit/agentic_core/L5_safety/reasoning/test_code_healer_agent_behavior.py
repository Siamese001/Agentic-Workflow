"""Behavioral tests for ``agentic_core.L5_safety.reasoning.CodeHealerAgent``.

Covers the module-level contract. The agent is a ~37KB facade over
UnifiedAgent/CodeHealingStrategy and mixes in 4 base classes — full end-to-end
healing requires real AST fixtures, out of scope here. Locked behaviors:

- Module imports (4-mixin MRO must stay consistent).
- HealingType enum values.
- HealingAction dataclass shape.
- HealerConfig defaults.
- CodeHealerAgent constructor: project_root default, config default, backup_dir
  auto-derivation, CodeHealingStrategy wired, VerificationGate wired,
  actions list initialized.
- STDLIB_MODULES contains expected stdlib names.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from agentic_core.L5_safety.reasoning import CodeHealerAgent as mod
from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
    CodeHealerAgent,
    HealerConfig,
    HealingAction,
    HealingType,
)


# ---- HealingType enum --------------------------------------------

class TestHealingType:
    @pytest.mark.parametrize("name,value", [
        ("CANON", "CANON"),
        ("IMPORT", "IMPORT"),
        ("STRUCTURAL", "STRUCTURAL"),
    ])
    def test_values(self, name: str, value: str) -> None:
        assert HealingType[name].value == value


# ---- HealingAction dataclass --------------------------------------

class TestHealingAction:
    def test_required_fields(self, tmp_path: Path) -> None:
        a = HealingAction(
            healing_type="IMPORT",
            file_path=tmp_path / "x.py",
            line_number=1,
            description="desc",
            old_code="old",
            new_code="new",
        )
        assert a.healing_type == "IMPORT"
        assert a.applied is False
        assert isinstance(a.timestamp, datetime)

    def test_applied_overrideable(self, tmp_path: Path) -> None:
        a = HealingAction(
            healing_type="CANON",
            file_path=tmp_path / "y.py",
            line_number=5,
            description="d",
            old_code="o",
            new_code="n",
            applied=True,
        )
        assert a.applied is True


# ---- HealerConfig defaults ---------------------------------------

class TestHealerConfig:
    def test_defaults(self) -> None:
        c = HealerConfig()
        assert c.enable_canon is True
        assert c.enable_import is True
        assert c.enable_structural is True
        assert c.dry_run is True  # dry-run by default — safety-first
        assert c.backup_before_heal is True
        assert c.backup_dir is None  # derived at agent init

    def test_overrides(self) -> None:
        c = HealerConfig(
            enable_canon=False, dry_run=False, enable_structural=False,
        )
        assert c.enable_canon is False
        assert c.dry_run is False
        assert c.enable_structural is False


# ---- CodeHealerAgent construction ---------------------------------

class TestCodeHealerAgentConstruction:
    def test_defaults_project_root_is_cwd(self) -> None:
        agent = CodeHealerAgent()
        assert agent.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path) -> None:
        agent = CodeHealerAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path

    def test_config_defaults(self, tmp_path: Path) -> None:
        agent = CodeHealerAgent(project_root=tmp_path)
        assert isinstance(agent._agent_config, HealerConfig)
        assert agent._agent_config.dry_run is True

    def test_backup_dir_derived_under_project_root(
        self, tmp_path: Path,
    ) -> None:
        agent = CodeHealerAgent(project_root=tmp_path)
        # HEALING_BACKUPS_DIR is "artifacts/healing_backups"
        backup = agent._agent_config.backup_dir
        assert backup is not None
        assert tmp_path in backup.parents

    def test_backup_dir_honors_explicit_config(self, tmp_path: Path) -> None:
        custom = tmp_path / "custom_backup"
        agent = CodeHealerAgent(
            project_root=tmp_path,
            agent_config=HealerConfig(backup_dir=custom),
        )
        assert agent._agent_config.backup_dir == custom

    def test_actions_list_empty(self, tmp_path: Path) -> None:
        agent = CodeHealerAgent(project_root=tmp_path)
        assert agent._actions == []

    def test_unified_strategy_wired(self, tmp_path: Path) -> None:
        agent = CodeHealerAgent(project_root=tmp_path)
        assert agent._unified_strategy is not None

    def test_verification_gate_wired(self, tmp_path: Path) -> None:
        agent = CodeHealerAgent(project_root=tmp_path)
        assert agent.gate is not None


# ---- STDLIB_MODULES classification helper -----------------------

class TestStdlibModules:
    @pytest.mark.parametrize("name", [
        "os", "sys", "re", "json", "ast", "typing", "pathlib",
        "logging", "datetime", "collections", "functools", "itertools",
        "threading", "asyncio", "dataclasses", "enum",
    ])
    def test_expected_stdlib_modules(self, name: str) -> None:
        assert name in CodeHealerAgent.STDLIB_MODULES

    def test_stdlib_modules_is_set(self) -> None:
        assert isinstance(CodeHealerAgent.STDLIB_MODULES, set)


# ---- Module surface ----------------------------------------------

class TestModuleSurface:
    @pytest.mark.parametrize("name", [
        "CodeHealerAgent", "HealerConfig", "HealingAction",
        "HealingType", "CodeHealingStrategy",
    ])
    def test_symbol_present(self, name: str) -> None:
        assert hasattr(mod, name)
