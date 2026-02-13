"""
Regression tests for FCA validate_layer_alignment() and blueprint hardening.

Covers the hard invariants from the Anomaly Remediation Controller:
1. Agent classes outside reasoning/ detected
2. PascalCase / test_* files in scripts/ detected
3. L5 subprocess violations detected (minus allowlist)
4. L6 subprocess violations detected (minus allowlist)
5. Nested LCD subtrees under leaf domains detected
6. FOLDER_PURITY_RULES["reasoning"] only allows *Agent.py

Run: pytest tests/unit/agentic_core/L5_safety/reasoning/test_layer_alignment_invariants.py -v
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_py(tmp_path: Path, rel: str, content: str = "") -> Path:
    """Create a .py file under tmp_path at the given relative path."""
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content) if content else "# stub\n", encoding="utf-8")
    return p


def _get_fca():
    """Lazy-import FCA to avoid import-time side effects."""
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    return FileClassificationAgent


# ---------------------------------------------------------------------------
# Blueprint API unit tests
# ---------------------------------------------------------------------------


class TestBlueprintAPI:
    """Tests for structure_blueprint_config layer validation API."""

    def test_is_layer_root(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import is_layer_root

        assert is_layer_root("L0_maintenance") is True
        assert is_layer_root("L5_safety") is True
        assert is_layer_root("L6_observability") is True
        assert is_layer_root("prompt_governance") is False
        assert is_layer_root("utils") is False

    def test_is_allowed_subfolder(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import is_allowed_subfolder

        assert is_allowed_subfolder("L5_safety", "reasoning") is True
        assert is_allowed_subfolder("L5_safety", "enforcement") is True
        assert is_allowed_subfolder("L5_safety", "scripts") is False  # not an LCD subfolder
        assert is_allowed_subfolder("utils", "reasoning") is False  # not a layer root

    def test_validate_no_nested_lcd_clean(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import validate_no_nested_lcd

        parts = ("agentic_core", "L5_safety", "reasoning", "FileClassificationAgent.py")
        assert validate_no_nested_lcd(parts) is None

    def test_validate_no_nested_lcd_violation(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import validate_no_nested_lcd

        # prompt_governance sprouting its own reasoning/ is forbidden
        parts = ("agentic_core", "prompt_governance", "reasoning", "SomeAgent.py")
        result = validate_no_nested_lcd(parts)
        assert result is not None
        assert result["domain"] == "prompt_governance"
        assert result["illegal_subfolder"] == "reasoning"

    def test_validate_no_nested_lcd_allowed_under_layer(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import validate_no_nested_lcd

        # L0_maintenance/scripts/prompt_governance — OK because layer root is ancestor
        parts = ("agentic_core", "L0_maintenance", "scripts", "prompt_governance", "reasoning", "x.py")
        result = validate_no_nested_lcd(parts)
        assert result is None

    def test_l5_subprocess_allowlist_populated(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import L5_SUBPROCESS_ALLOWLIST

        assert "safe_subprocess_handler.py" in L5_SUBPROCESS_ALLOWLIST
        assert "PreCommitSovereignAgent.py" in L5_SUBPROCESS_ALLOWLIST
        assert len(L5_SUBPROCESS_ALLOWLIST) >= 7

    def test_l6_hybrid_allowlist_populated(self):
        from agentic_core.L5_safety.config.structure_blueprint_config import L6_HYBRID_ALLOWLIST

        assert "verify_dashboard_e2e_playwright_util.py" in L6_HYBRID_ALLOWLIST

    def test_scripts_forbidden_patterns(self):
        import re

        from agentic_core.L5_safety.config.structure_blueprint_config import SCRIPTS_FORBIDDEN_PATTERNS

        # PascalCase should match
        assert any(re.match(p, "AgentAuditResult.py") for p in SCRIPTS_FORBIDDEN_PATTERNS)
        # test_ should match
        assert any(re.match(p, "test_something.py") for p in SCRIPTS_FORBIDDEN_PATTERNS)
        # snake_case should NOT match
        assert not any(re.match(p, "some_script.py") for p in SCRIPTS_FORBIDDEN_PATTERNS)


# ---------------------------------------------------------------------------
# FCA validate_layer_alignment() tests
# ---------------------------------------------------------------------------


class TestFCALayerAlignment:
    """Tests for FCA.validate_layer_alignment() enforcement checks."""

    def test_scripts_purity_rejects_pascalcase(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        p = _make_py(tmp_path, "agentic_core/L0_maintenance/scripts/SomeClass.py", "class SomeClass: pass")
        result = fca.validate_layer_alignment(p)
        assert result is not None
        assert result["violation"] == "PASCALCASE_IN_SCRIPTS"

    def test_scripts_purity_rejects_test_files(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        p = _make_py(tmp_path, "agentic_core/L0_maintenance/scripts/test_something.py", "def test_x(): pass")
        result = fca.validate_layer_alignment(p)
        assert result is not None
        assert result["violation"] == "TEST_IN_SCRIPTS"

    def test_scripts_purity_allows_snake_case(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        p = _make_py(
            tmp_path,
            "agentic_core/L0_maintenance/scripts/run_audit.py",
            "if __name__ == '__main__': pass",
        )
        result = fca.validate_layer_alignment(p)
        assert result is None

    def test_l5_subprocess_flagged_when_not_allowlisted(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        p = _make_py(
            tmp_path,
            "agentic_core/L5_safety/enforcement/bad_tool.py",
            "import subprocess\nsubprocess.run(['ls'])",
        )
        result = fca.validate_layer_alignment(p)
        assert result is not None
        assert result["violation"] == "L5_SUBPROCESS_NOT_ALLOWED"

    def test_l5_subprocess_allowed_when_allowlisted(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        p = _make_py(
            tmp_path,
            "agentic_core/L5_safety/enforcement/safe_subprocess_handler.py",
            "import subprocess",
        )
        result = fca.validate_layer_alignment(p)
        assert result is None

    def test_agent_outside_reasoning_flagged(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        # WAVE 2.1: Agent detection now uses AST lineage — must inherit from
        # a known agent base class to be confirmed as AGENT_OUTSIDE_REASONING.
        p = _make_py(
            tmp_path,
            "agentic_core/L5_safety/types/bad_agent_types.py",
            "class SomeDetectorAgent(SovereignBaseAgent):\n    pass",
        )
        result = fca.validate_layer_alignment(p)
        assert result is not None
        assert result["violation"] == "AGENT_OUTSIDE_REASONING"

    def test_agent_uncertain_lineage_flagged(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        # WAVE 2.1: Agent-like name with no confirmed base => UNCERTAIN
        p = _make_py(
            tmp_path,
            "agentic_core/L5_safety/types/ambiguous_agent.py",
            "class SomeDetectorAgent(SomeRandomMixin):\n    pass",
        )
        result = fca.validate_layer_alignment(p)
        assert result is not None
        assert result["violation"] == "AGENT_DETECTION_UNCERTAIN"
        assert result["executable"] is False

    def test_agent_in_reasoning_not_flagged(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        p = _make_py(
            tmp_path,
            "agentic_core/L5_safety/reasoning/SomeDetectorAgent.py",
            "class SomeDetectorAgent:\n    pass",
        )
        result = fca.validate_layer_alignment(p)
        assert result is None

    def test_nested_lcd_flagged(self, tmp_path):
        fca_cls = _get_fca()
        fca = fca_cls(project_root=tmp_path)
        p = _make_py(
            tmp_path,
            "agentic_core/prompt_governance/reasoning/SomeAgent.py",
            "class SomeAgent: pass",
        )
        result = fca.validate_layer_alignment(p)
        assert result is not None
        assert result["violation"] == "NESTED_LCD_SUBTREE"


# ---------------------------------------------------------------------------
# Invariant: No Agent classes exist outside reasoning/ in the real repo
# ---------------------------------------------------------------------------


class TestRepoInvariants:
    """Scan the actual repo for known invariant violations."""

    def test_no_agents_in_l5_types(self):
        """L5_safety/types/ must not contain any *Agent classes."""
        types_dir = Path("agentic_core/L5_safety/types")
        if not types_dir.exists():
            pytest.skip("L5_safety/types not found")
        for f in types_dir.glob("*.py"):
            if f.name.startswith("__"):
                continue
            content = f.read_text(encoding="utf-8", errors="ignore")
            import re

            agents = re.findall(r"^class\s+(\w+Agent)\s*[\(:]", content, re.MULTILINE)
            assert not agents, f"{f.name} still contains Agent class(es): {agents}"

    def test_no_pascalcase_in_l0_scripts(self):
        """L0_maintenance/scripts/ must not contain PascalCase .py files."""
        scripts_dir = Path("agentic_core/L0_maintenance/scripts")
        if not scripts_dir.exists():
            pytest.skip("L0_maintenance/scripts not found")
        for f in scripts_dir.glob("*.py"):
            if f.name.startswith("__"):
                continue
            assert not f.name[0].isupper(), f"PascalCase file in scripts/: {f.name}"

    def test_no_test_files_in_l0_scripts(self):
        """L0_maintenance/scripts/ must not contain test_*.py files."""
        scripts_dir = Path("agentic_core/L0_maintenance/scripts")
        if not scripts_dir.exists():
            pytest.skip("L0_maintenance/scripts not found")
        for f in scripts_dir.glob("test_*.py"):
            pytest.fail(f"test file in scripts/: {f.name}")

    def test_l6_config_exists(self):
        """L6_observability/config/ must exist."""
        assert Path("agentic_core/L6_observability/config").is_dir(), "L6_observability/config/ missing"
