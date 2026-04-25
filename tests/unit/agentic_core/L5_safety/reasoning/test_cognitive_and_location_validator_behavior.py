"""Behavioral tests for CognitiveDispositionAgent + LocationValidatorAgent."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.reasoning.CognitiveDispositionAgent import (
    CognitiveDispositionAgent,
    DispositionDecision,
)
from agentic_core.L5_safety.reasoning.location_validator import (
    LocationValidatorAgent,
)


# ============================================================================
# CognitiveDispositionAgent
# ============================================================================


class TestDispositionDecision:
    def test_required_field(self) -> None:
        d = DispositionDecision(action="archive")
        assert d.action == "archive"
        assert d.target_path is None
        assert d.reason == ""
        assert d.confidence == 0.0

    def test_all_fields(self) -> None:
        d = DispositionDecision(
            action="move",
            target_path="/new/loc/x.py",
            reason="drift detected",
            confidence=0.85,
        )
        assert d.action == "move"
        assert d.target_path == "/new/loc/x.py"
        assert d.confidence == 0.85


class TestCognitiveDispositionAgent:
    def test_default_project_root_cwd(self) -> None:
        agent = CognitiveDispositionAgent()
        assert agent.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path) -> None:
        agent = CognitiveDispositionAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path

    def test_default_confidence_threshold(self, tmp_path: Path) -> None:
        agent = CognitiveDispositionAgent(project_root=tmp_path)
        assert agent.confidence_threshold == 0.75

    def test_custom_confidence_threshold(self, tmp_path: Path) -> None:
        agent = CognitiveDispositionAgent(
            project_root=tmp_path,
            confidence_threshold=0.9,
        )
        assert agent.confidence_threshold == 0.9

    def test_confidence_threshold_in_unit_range(self, tmp_path: Path) -> None:
        agent = CognitiveDispositionAgent(project_root=tmp_path)
        assert 0.0 <= agent.confidence_threshold <= 1.0


# ============================================================================
# LocationValidatorAgent
# ============================================================================


class TestLocationValidatorAgentConstruction:
    def test_project_root_resolved(self, tmp_path: Path) -> None:
        agent = LocationValidatorAgent(project_root=tmp_path)
        assert agent.project_root == tmp_path.resolve()
        assert agent.project_root.is_absolute()

    def test_string_root_coerced(self, tmp_path: Path) -> None:
        agent = LocationValidatorAgent(project_root=str(tmp_path))
        assert isinstance(agent.project_root, Path)


class TestLocationValidatorAgentHeal:
    def test_heal_always_skips(self, tmp_path: Path) -> None:
        agent = LocationValidatorAgent(project_root=tmp_path)
        result = agent.heal({"type": "mislocation", "file": "x.py"})
        assert result["status"] == "skipped"
        assert "validation-only" in result["details"]
        assert result["artifacts"] == []
        assert result["errors"] == []

    def test_heal_repository_raises_not_implemented(self, tmp_path: Path) -> None:
        agent = LocationValidatorAgent(project_root=tmp_path)
        with pytest.raises(NotImplementedError, match="LocationValidatorAgent"):
            agent.heal_repository()


class TestLocationValidatorAgentValidateSovereignRoots:
    def test_returns_violations_for_missing_roots(self, tmp_path: Path) -> None:
        # Fresh tmp_path has no sovereign roots — all should be violations
        agent = LocationValidatorAgent(project_root=tmp_path)
        violations = agent.validate_sovereign_roots()
        assert isinstance(violations, list)
        # Every entry is a (Path, str) tuple
        for v in violations:
            assert isinstance(v, tuple)
            assert len(v) == 2

    def test_no_violations_when_all_roots_present(self, tmp_path: Path) -> None:
        from agentic_core.L5_safety.config.structure_blueprint import (
            ROOT_WHITELIST,
        )

        for name in ROOT_WHITELIST:
            (tmp_path / name).mkdir()
        agent = LocationValidatorAgent(project_root=tmp_path)
        assert agent.validate_sovereign_roots() == []
