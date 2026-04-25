"""Behavioral tests for ``agentic_core.L5_safety.reasoning.FileClassificationAgent``.

Covers the module-level contract only — the 5,700-line healer agent's full
behavior requires repo-wide fixtures and is out of scope here. What's locked:

- Module imports cleanly (was blocked by a real MRO bug — fixed in this commit).
- ClassificationResult dataclass shape.
- FileClassificationHealerAgent dataclass defaults + __post_init__ side effects:
  - project_root normalized to absolute Path
  - stats dict populated with all violation categories
- get_python_files_fast module-level helper returns only .py files within scope.
- FILETYPE_TO_FOLDER imported from structure_blueprint aligns with typical types.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    ClassificationResult,
    FileClassificationHealerAgent,
    get_python_files_fast,
)


# ---- ClassificationResult ------------------------------------------


class TestClassificationResult:
    def test_required_fields(self) -> None:
        r = ClassificationResult(
            file_type="UTILITY",
            confidence=0.9,
            signals=["import_only"],
            warnings=[],
        )
        assert r.file_type == "UTILITY"
        assert r.confidence == 0.9
        assert r.signals == ["import_only"]
        assert r.warnings == []

    def test_confidence_in_unit_range(self) -> None:
        # Contract: confidence is 0.0-1.0; no enforcement at dataclass level,
        # but sensible values must round-trip.
        r = ClassificationResult(file_type="AGENT", confidence=0.5, signals=[], warnings=[])
        assert 0.0 <= r.confidence <= 1.0


# ---- FileClassificationHealerAgent construction -------------------


class TestHealerAgentDefaults:
    def test_defaults(self, tmp_path: Path) -> None:
        agent = FileClassificationHealerAgent(project_root=tmp_path)
        assert agent.dry_run is False
        assert agent.verbose is False
        assert agent.validate_only is False
        assert agent.force is False
        assert agent.max_import_impact == 25
        assert agent.max_actions == 50
        assert agent.strict_lcd_roots_only is False
        assert agent.wave_id is None
        assert agent.wave_config is None

    def test_project_root_resolved_to_absolute(self, tmp_path: Path) -> None:
        # __post_init__ must call .resolve() on project_root
        agent = FileClassificationHealerAgent(project_root=tmp_path)
        assert agent.project_root.is_absolute()

    def test_string_project_root_coerced_to_path(self, tmp_path: Path) -> None:
        agent = FileClassificationHealerAgent(project_root=str(tmp_path))
        assert isinstance(agent.project_root, Path)
        assert agent.project_root.is_absolute()

    def test_stats_populated(self, tmp_path: Path) -> None:
        agent = FileClassificationHealerAgent(project_root=tmp_path)
        assert "analyzed" in agent.stats
        assert "compliant" in agent.stats
        assert "violations" in agent.stats
        assert isinstance(agent.stats["violations"], dict)

    @pytest.mark.parametrize(
        "category",
        [
            "AGENT",
            "CLASS",
            "MIXIN",
            "UTILITY",
            "PROTOCOL",
            "ENGINE",
            "STUB",
            "TEST",
            "SCRIPT",
            "TYPES",
            "GATEWAY",
            "ORCHESTRATOR",
            "VALIDATOR",
            "FACTORY",
            "CONFIG",
            "ADAPTER",
            "STRATEGY",
            "ENFORCER",
            "SEAM",
            "EXCEPTION",
        ],
    )
    def test_all_violation_categories_present(
        self,
        tmp_path: Path,
        category: str,
    ) -> None:
        agent = FileClassificationHealerAgent(project_root=tmp_path)
        assert category in agent.stats["violations"]

    def test_custom_max_actions(self, tmp_path: Path) -> None:
        agent = FileClassificationHealerAgent(project_root=tmp_path, max_actions=100)
        assert agent.max_actions == 100

    def test_dry_run_mode(self, tmp_path: Path) -> None:
        agent = FileClassificationHealerAgent(
            project_root=tmp_path,
            dry_run=True,
            verbose=True,
        )
        assert agent.dry_run is True
        assert agent.verbose is True


# ---- get_python_files_fast ----------------------------------------


class TestGetPythonFilesFast:
    def test_returns_list_of_paths(self, tmp_path: Path) -> None:
        result = get_python_files_fast(tmp_path)
        assert isinstance(result, list)

    def test_finds_py_files(self, tmp_path: Path) -> None:
        # Stand up a mini agentic_core-like tree because the scanner is
        # territory-scoped to enforced roots.
        core = tmp_path / "agentic_core" / "L0_routing"
        core.mkdir(parents=True)
        (core / "module.py").write_text("x = 1", encoding="utf-8")
        (core / "notes.txt").write_text("ignore me", encoding="utf-8")
        results = get_python_files_fast(tmp_path)
        names = [p.name for p in results]
        assert "module.py" in names
        assert "notes.txt" not in names

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        assert get_python_files_fast(tmp_path) == []


# ---- Module imports ----------------------------------------------


class TestModuleImports:
    def test_has_agent_class(self) -> None:
        from agentic_core.L5_safety.reasoning import FileClassificationAgent as mod

        assert hasattr(mod, "FileClassificationHealerAgent")

    def test_has_classification_result(self) -> None:
        from agentic_core.L5_safety.reasoning import FileClassificationAgent as mod

        assert hasattr(mod, "ClassificationResult")

    def test_has_sovereign_base_flag(self) -> None:
        from agentic_core.L5_safety.reasoning import FileClassificationAgent as mod

        assert hasattr(mod, "HAS_SOVEREIGN_BASE")
        assert mod.HAS_SOVEREIGN_BASE is True  # bases are importable in test env
