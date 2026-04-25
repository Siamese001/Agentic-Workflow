"""Behavioral tests for ``agentic_core.L5_safety.enforcement.registry_verification_enforcer``.

Covers RegistryVerifier — codebase scan + agent_discovery.json cross-reference:
- AgentInfo / VerificationResult dataclass defaults.
- _is_excluded: excludes paths in EXCLUDED_DIRS, accepts clean paths.
- _is_test_file: recognises tests dir + test_* names.
- _extract_layer: agentic_core/L3_orchestration → "L3", apps_rg → "Apps_RG", etc.
- _parse_agent_file: parses real *Agent.py files; returns None for non-existent
  or syntax-broken files; extracts class_name, inheritance, key_methods.
- load_registry: returns empty list when file missing; parses valid JSON;
  returns empty list on JSONDecodeError.
- verify_registry: full roundtrip on a tmp project — orphan/missing/path-mismatch
  classification; coverage_percentage math; is_complete flag.
- generate_report: renders markdown with summary counts and conditional sections.
- run_verification: convenience wrapper returns a VerificationResult.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L5_safety.enforcement.registry_verification_enforcer import (
    AgentInfo,
    RegistryVerifier,
    VerificationResult,
    run_verification,
)


# ---- fixtures -----------------------------------------------------------


@pytest.fixture
def fake_root(tmp_path: Path) -> Path:
    """Build a fake project tree with agent discovery JSON + *Agent.py files."""
    (tmp_path / "pyproject.toml").touch()  # project-root marker

    # Real agent file
    agent_dir = tmp_path / "agentic_core" / "L3_orchestration" / "reasoning"
    agent_dir.mkdir(parents=True)
    (agent_dir / "FooAgent.py").write_text(
        "class FooAgent(BaseAgent):\n"
        "    def run(self):\n        return 1\n"
        "    async def plan(self):\n        return 2\n",
        encoding="utf-8",
    )

    # Syntax-broken agent file
    bad_dir = tmp_path / "agentic_core" / "L3_orchestration"
    (bad_dir / "BrokenAgent.py").write_text("class def (", encoding="utf-8")

    # Excluded agent file (in tests/)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_FooAgent.py").write_text(
        "class TestAgent(object): pass",
        encoding="utf-8",
    )

    # Registry JSON file
    disc_dir = tmp_path / "agentic_core" / "L0_routing"
    disc_dir.mkdir(parents=True)
    (disc_dir / "agent_discovery.json").write_text(
        json.dumps(
            [
                {"class_name": "FooAgent", "path": "agentic_core/L3_orchestration/reasoning/FooAgent.py"},
                {"class_name": "GhostAgent", "path": "agentic_core/L5_safety/GhostAgent.py"},
            ]
        ),
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def verifier(fake_root: Path) -> RegistryVerifier:
    return RegistryVerifier(project_root=fake_root)


# ---- Dataclass defaults -------------------------------------------------


class TestDataclasses:
    def test_agent_info_defaults(self, tmp_path: Path) -> None:
        ai = AgentInfo(
            class_name="X",
            file_path=tmp_path / "x.py",
            relative_path="x.py",
        )
        assert ai.layer == "Unknown"
        assert ai.has_agent_class is False
        assert ai.inheritance == []
        assert ai.key_methods == []

    def test_verification_result_defaults(self) -> None:
        r = VerificationResult()
        assert r.total_filesystem_agents == 0
        assert r.total_registry_agents == 0
        assert r.orphan_agents == []
        assert r.missing_agents == []
        assert r.path_mismatches == []
        assert r.valid_agents == []
        assert r.coverage_percentage == 0.0
        assert r.is_complete is False
        assert r.errors == []


# ---- Path / layer helpers ----------------------------------------------


class TestIsExcluded:
    def test_excludes_pycache(self, verifier: RegistryVerifier, fake_root: Path) -> None:
        assert verifier._is_excluded(fake_root / "pkg" / "__pycache__" / "a.py")

    def test_clean_path_not_excluded(
        self,
        verifier: RegistryVerifier,
        fake_root: Path,
    ) -> None:
        assert not verifier._is_excluded(
            fake_root / "agentic_core" / "L3_orchestration" / "reasoning" / "FooAgent.py",
        )


class TestIsTestFile:
    def test_tests_dir(self, verifier: RegistryVerifier, fake_root: Path) -> None:
        assert verifier._is_test_file(fake_root / "tests" / "x.py")

    def test_test_prefix(self, verifier: RegistryVerifier, fake_root: Path) -> None:
        assert verifier._is_test_file(fake_root / "pkg" / "test_foo.py")

    def test_regular_file(self, verifier: RegistryVerifier, fake_root: Path) -> None:
        assert not verifier._is_test_file(fake_root / "pkg" / "foo.py")


class TestExtractLayer:
    @pytest.mark.parametrize(
        "rel,expected",
        [
            ("agentic_core/L3_orchestration/reasoning/X.py", "L3"),
            ("agentic_core/L0_routing/enforcement/X.py", "L0"),
            ("agentic_core/L5_safety/reasoning/X.py", "L5"),
            ("agentic_core/base_agents/X.py", "Base"),
            ("apps_rg/engines/X.py", "Apps_RG"),
            ("apps_lic/X.py", "Apps_LIC"),
            ("apps_shared/X.py", "Apps_Shared"),
            ("other/path.py", "Unknown"),
        ],
    )
    def test_parametric(
        self,
        verifier: RegistryVerifier,
        rel: str,
        expected: str,
    ) -> None:
        assert verifier._extract_layer(rel) == expected

    def test_root_level_returns_root(self, verifier: RegistryVerifier) -> None:
        assert verifier._extract_layer("just_a_file.py") == "Root"


# ---- _parse_agent_file --------------------------------------------------


class TestParseAgentFile:
    def test_extracts_agent_class(
        self,
        verifier: RegistryVerifier,
        fake_root: Path,
    ) -> None:
        p = fake_root / "agentic_core" / "L3_orchestration" / "reasoning" / "FooAgent.py"
        info = verifier._parse_agent_file(p)
        assert info is not None
        assert info.class_name == "FooAgent"
        assert info.has_agent_class is True
        assert "BaseAgent" in info.inheritance
        assert "run" in info.key_methods
        assert "plan" in info.key_methods
        assert info.layer == "L3"

    def test_returns_none_on_syntax_error(
        self,
        verifier: RegistryVerifier,
        fake_root: Path,
    ) -> None:
        p = fake_root / "agentic_core" / "L3_orchestration" / "BrokenAgent.py"
        assert verifier._parse_agent_file(p) is None

    def test_returns_none_when_missing(
        self,
        verifier: RegistryVerifier,
        fake_root: Path,
    ) -> None:
        assert verifier._parse_agent_file(fake_root / "no-file.py") is None

    def test_returns_none_when_no_agent_class(
        self,
        verifier: RegistryVerifier,
        fake_root: Path,
    ) -> None:
        p = fake_root / "agentic_core" / "Other.py"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("class Helper: pass", encoding="utf-8")
        assert verifier._parse_agent_file(p) is None


# ---- scan_filesystem ---------------------------------------------------


class TestScanFilesystem:
    def test_finds_real_agents_only(
        self,
        verifier: RegistryVerifier,
        fake_root: Path,
    ) -> None:
        agents = verifier.scan_filesystem()
        class_names = [a.class_name for a in agents]
        assert "FooAgent" in class_names
        # Broken file filtered out
        assert "BrokenAgent" not in class_names
        # Test file filtered out
        assert "TestAgent" not in class_names


# ---- load_registry -----------------------------------------------------


class TestLoadRegistry:
    def test_parses_json(self, verifier: RegistryVerifier) -> None:
        entries = verifier.load_registry()
        names = [e["class_name"] for e in entries]
        assert "FooAgent" in names
        assert "GhostAgent" in names

    def test_returns_empty_if_missing(self, tmp_path: Path) -> None:
        v = RegistryVerifier(project_root=tmp_path)
        assert v.load_registry() == []

    def test_returns_empty_on_malformed_json(
        self,
        verifier: RegistryVerifier,
    ) -> None:
        # Overwrite discovery with invalid JSON
        verifier.discovery_path.write_text("{not json", encoding="utf-8")
        assert verifier.load_registry() == []


# ---- verify_registry (full roundtrip) ----------------------------------


class TestVerifyRegistry:
    def test_orphan_and_missing_classified(
        self,
        verifier: RegistryVerifier,
    ) -> None:
        result = verifier.verify_registry()
        # Registry has GhostAgent but no file → orphan
        assert any(o["class_name"] == "GhostAgent" for o in result.orphan_agents)
        # All filesystem agents that are in registry → valid
        assert any(a.class_name == "FooAgent" for a in result.valid_agents)

    def test_total_counts(self, verifier: RegistryVerifier) -> None:
        result = verifier.verify_registry()
        assert result.total_filesystem_agents >= 1
        assert result.total_registry_agents == 2

    def test_coverage_computed(self, verifier: RegistryVerifier) -> None:
        result = verifier.verify_registry()
        # FooAgent is the only filesystem agent, and it IS in the registry → 100%
        assert result.coverage_percentage == pytest.approx(100.0)

    def test_is_complete_false_when_orphans(
        self,
        verifier: RegistryVerifier,
    ) -> None:
        result = verifier.verify_registry()
        assert result.is_complete is False  # GhostAgent orphan

    def test_is_complete_true_when_clean(
        self,
        verifier: RegistryVerifier,
    ) -> None:
        # Remove the orphan from the registry → clean state
        verifier.discovery_path.write_text(
            json.dumps(
                [
                    {"class_name": "FooAgent", "path": "agentic_core/L3_orchestration/reasoning/FooAgent.py"},
                ]
            ),
            encoding="utf-8",
        )
        result = verifier.verify_registry()
        assert result.is_complete is True
        assert result.orphan_agents == []
        assert result.missing_agents == []
        assert result.path_mismatches == []

    def test_path_mismatch_detected(
        self,
        verifier: RegistryVerifier,
    ) -> None:
        # Registry claims FooAgent is at a different path
        verifier.discovery_path.write_text(
            json.dumps(
                [
                    {"class_name": "FooAgent", "path": "wrong/location/FooAgent.py"},
                ]
            ),
            encoding="utf-8",
        )
        result = verifier.verify_registry()
        assert any(m["class_name"] == "FooAgent" for m in result.path_mismatches)
        assert result.is_complete is False


# ---- generate_report ---------------------------------------------------


class TestGenerateReport:
    def test_summary_rendered(self, verifier: RegistryVerifier) -> None:
        result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert "# Phase 1: Registry Verification Report" in report
        assert "## Summary" in report
        assert "Coverage:" in report
        assert "Status:" in report

    def test_orphan_section_present_when_orphans(
        self,
        verifier: RegistryVerifier,
    ) -> None:
        result = verifier.verify_registry()
        report = verifier.generate_report(result)
        assert "Orphan Agents" in report
        assert "GhostAgent" in report

    def test_orphan_section_absent_when_no_orphans(
        self,
        verifier: RegistryVerifier,
    ) -> None:
        empty = VerificationResult()
        report = verifier.generate_report(empty)
        # Section headings (H2) must NOT appear when their lists are empty;
        # the summary lines ("- **Orphan Agents:** 0") still mention the terms.
        assert "## Orphan Agents" not in report
        assert "## Path Mismatches" not in report
        assert "## Missing from Registry" not in report

    def test_missing_agents_truncated_at_50(
        self,
        verifier: RegistryVerifier,
        tmp_path: Path,
    ) -> None:
        result = VerificationResult()
        for i in range(55):
            result.missing_agents.append(
                AgentInfo(
                    class_name=f"A{i}",
                    file_path=tmp_path / f"a{i}.py",
                    relative_path=f"a{i}.py",
                ),
            )
        report = verifier.generate_report(result)
        assert "(5 more)" in report


# ---- run_verification --------------------------------------------------


class TestRunVerification:
    def test_returns_verification_result(self) -> None:
        # Uses real project root — just make sure it returns the right type
        result = run_verification()
        assert isinstance(result, VerificationResult)
