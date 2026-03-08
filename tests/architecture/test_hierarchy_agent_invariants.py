"""Invariant tests for HierarchyAgent bug-fixes 1–4.

Branch inventory (§1.3):

  Fix 1 — _enforce_tests_structure approved-subfolder guard:
    - *Agent.py inside approved subfolder (support/)  → violation logged, no move
    - conftest.py inside approved subfolder           → exempt, no violation
    - test_foo.py inside approved subfolder           → clean, no violation

  Fix 2 — _block_agent_files_in_tests:
    - *Agent.py directly in tests/                    → violation, no move
    - *Agent.py inside tests/support/                 → violation, no move
    - clean tests/ (only test_*.py files)             → zero violations from this guard

  Fix 3 — get_best_target_l2 / _calculate_subfolder_confidence_for_agent:
    - *Agent.py, l1_name="tests"   → "__ARCHIVE__" sentinel returned
    - *Agent.py, l1_name="L5_safety" (source layer) → valid subfolder (not __ARCHIVE__)
    - non-agent file, l1_name="tests" → normal routing (not __ARCHIVE__)

  Fix 4 — SSOT tests/support/ forbidden_patterns:
    - "forbidden_patterns" key present in tests/support/ config
    - pattern matches FooAgent.py
    - pattern does NOT match test_foo.py
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.architecture


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_agent(tmp_root: Path, healing_enabled: bool = False):
    """Construct a minimal HierarchyAgent with mocked gatekeeper, no filesystem side-effects."""
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    agent = object.__new__(HierarchyAgent)
    agent.project_root = tmp_root
    agent.healing_enabled = healing_enabled
    agent.agent_name = "HierarchyAgent"
    agent.gatekeeper = MagicMock()
    return agent


def _results() -> dict:
    return {"files_relocated": 0, "folders_removed": 0, "violations_found": 0, "errors": []}


# ---------------------------------------------------------------------------
# Fix 1 — _enforce_tests_structure: approved-subfolder skip is too broad
# ---------------------------------------------------------------------------


class TestFix1EnforceTestsStructure:
    """Files inside approved subfolders must still be checked for test_ prefix."""

    def _run(self, tmp_path: Path, files: list[tuple[str, str]]) -> dict:
        for rel, content in files:
            p = tmp_path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._enforce_tests_structure(tmp_path, r)
        return r

    def test_agent_file_in_approved_subfolder_raises_violation(self, tmp_path: Path) -> None:
        """*Agent.py inside tests/support/ must be flagged — no silent skip."""
        r = self._run(tmp_path, [("support/SomeAgent.py", "class SomeAgent: pass")])
        assert r["violations_found"] >= 1

    def test_infra_file_in_approved_subfolder_is_exempt(self, tmp_path: Path) -> None:
        """conftest.py inside tests/support/ must NOT produce a violation."""
        r = self._run(tmp_path, [("support/conftest.py", "# conftest")])
        assert r["violations_found"] == 0

    def test_test_prefixed_file_in_approved_subfolder_is_clean(self, tmp_path: Path) -> None:
        """test_foo.py inside tests/support/ must NOT produce a violation."""
        r = self._run(tmp_path, [("support/test_foo.py", "def test_foo(): pass")])
        assert r["violations_found"] == 0

    def test_dunder_init_in_approved_subfolder_is_exempt(self, tmp_path: Path) -> None:
        """__init__.py inside tests/support/ must NOT produce a violation."""
        r = self._run(tmp_path, [("support/__init__.py", "")])
        assert r["violations_found"] == 0

    def test_non_test_non_agent_file_in_approved_subfolder_is_flagged(self, tmp_path: Path) -> None:
        """helpers.py (no prefix, not infra) inside support/ must also be flagged."""
        r = self._run(tmp_path, [("support/helpers.py", "# helpers")])
        assert r["violations_found"] >= 1

    def test_agent_file_in_approved_subfolder_is_not_moved(self, tmp_path: Path) -> None:
        """Violation is logged but the file must not be moved."""
        src = tmp_path / "support" / "SomeAgent.py"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text("class SomeAgent: pass", encoding="utf-8")
        agent = _make_agent(tmp_path, healing_enabled=True)
        r = _results()
        agent._enforce_tests_structure(tmp_path, r)
        # File must still be in place — _enforce only reports
        assert src.exists(), "Agent file must NOT be moved by _enforce_tests_structure"
        # Gatekeeper safe_move must NOT have been called
        agent.gatekeeper.safe_move.assert_not_called()


# ---------------------------------------------------------------------------
# Fix 2 — _block_agent_files_in_tests: no pre-check blocking *Agent.py → tests/
# ---------------------------------------------------------------------------


class TestFix2BlockAgentFilesInTests:
    """_block_agent_files_in_tests scans tests/ and records violations without moving."""

    def test_block_agent_files_in_tests_root(self, tmp_path: Path) -> None:
        """*Agent.py directly in tests/ triggers a violation."""
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "SomeAgent.py").write_text("class SomeAgent: pass")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert r["violations_found"] >= 1

    def test_block_agent_files_in_tests_support(self, tmp_path: Path) -> None:
        """*Agent.py inside tests/support/ triggers a violation."""
        (tmp_path / "tests" / "support").mkdir(parents=True)
        (tmp_path / "tests" / "support" / "FooAgent.py").write_text("class FooAgent: pass")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert r["violations_found"] >= 1

    def test_no_violation_when_tests_is_clean(self, tmp_path: Path) -> None:
        """Clean tests/ (only test_*.py) produces zero violations from _block_agent_files_in_tests."""
        (tmp_path / "tests" / "unit").mkdir(parents=True)
        (tmp_path / "tests" / "unit" / "test_something.py").write_text("def test_x(): pass")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert r["violations_found"] == 0

    def test_block_does_not_move_agent_file(self, tmp_path: Path) -> None:
        """_block_agent_files_in_tests must NOT move any file (report only)."""
        (tmp_path / "tests").mkdir()
        src = tmp_path / "tests" / "BrokenAgent.py"
        src.write_text("class BrokenAgent: pass")
        agent = _make_agent(tmp_path, healing_enabled=True)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert src.exists(), "_block_agent_files_in_tests must not move the file"
        agent.gatekeeper.safe_move.assert_not_called()

    def test_multiple_agent_files_each_counted(self, tmp_path: Path) -> None:
        """Every *Agent.py file found produces a distinct violation count increment."""
        (tmp_path / "tests" / "support").mkdir(parents=True)
        (tmp_path / "tests" / "support" / "SomeAgent.py").write_text("class SomeAgent: pass")
        (tmp_path / "tests" / "support" / "OtherAgent.py").write_text("class OtherAgent: pass")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert r["violations_found"] == 2

    def test_no_tests_dir_is_noop(self, tmp_path: Path) -> None:
        """If tests/ does not exist, _block_agent_files_in_tests is a silent no-op."""
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)  # Must not raise
        assert r["violations_found"] == 0


# ---------------------------------------------------------------------------
# Fix 3 — get_best_target_l2 / _calculate_subfolder_confidence_for_agent
# ---------------------------------------------------------------------------


class TestFix3SubfolderConfidence:
    """get_best_target_l2 returns __ARCHIVE__ for agent files routed to non-source roots."""

    def test_get_best_target_l2_agent_file_tests_root_returns_archive_sentinel(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        result = get_best_target_l2("tests", "SomeAgent.py")
        assert result == "__ARCHIVE__", (
            f"Expected '__ARCHIVE__' for agent file in 'tests' root, got {result!r}"
        )

    def test_get_best_target_l2_agent_file_source_layer_returns_valid(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        result = get_best_target_l2("L5_safety", "SomeAgent.py")
        assert result != "__ARCHIVE__", (
            "Agent file in source layer 'L5_safety' must NOT get the ARCHIVE sentinel"
        )

    def test_get_best_target_l2_non_agent_file_tests_root_proceeds(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        result = get_best_target_l2("tests", "test_something.py")
        assert result != "__ARCHIVE__", "Non-agent files must go through normal routing, not ARCHIVE sentinel"

    def test_confidence_zero_for_all_low_confidence_roots(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import (
            _AGENT_LOW_CONFIDENCE_ROOTS,
            _calculate_subfolder_confidence_for_agent,
        )

        for root in _AGENT_LOW_CONFIDENCE_ROOTS:
            conf = _calculate_subfolder_confidence_for_agent(root, "FooAgent.py")
            assert conf < 0.5, f"Expected confidence < 0.5 for root {root!r}, got {conf}"

    def test_confidence_one_for_source_layer(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import (
            _calculate_subfolder_confidence_for_agent,
        )

        conf = _calculate_subfolder_confidence_for_agent("agentic_core", "FooAgent.py")
        assert conf >= 0.5, f"Expected confidence >= 0.5 for source layer, got {conf}"

    def test_docs_root_also_returns_archive_sentinel(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        assert get_best_target_l2("docs", "MyAgent.py") == "__ARCHIVE__"

    def test_data_root_also_returns_archive_sentinel(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        assert get_best_target_l2("data", "MyAgent.py") == "__ARCHIVE__"


# ---------------------------------------------------------------------------
# Fix 4 — SSOT tests/support/ forbidden_patterns
# ---------------------------------------------------------------------------


class TestFix4SSOTForbiddenPatterns:
    """tests/support/ SSOT entry must contain forbidden_patterns blocking *Agent.py."""

    def _get_support_config(self) -> dict:
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            SOVEREIGN_TERRITORIES,
        )

        return SOVEREIGN_TERRITORIES["tests"]["subfolders"]["support"]

    def test_ssot_support_has_forbidden_patterns(self) -> None:
        cfg = self._get_support_config()
        assert "forbidden_patterns" in cfg, "tests/support/ SSOT entry must have a 'forbidden_patterns' key"

    def test_ssot_support_forbidden_patterns_rejects_agent_py(self) -> None:
        cfg = self._get_support_config()
        patterns = cfg["forbidden_patterns"]
        assert any(re.match(p, "FooAgent.py") for p in patterns), (
            "forbidden_patterns must match 'FooAgent.py'"
        )

    def test_ssot_support_forbidden_patterns_allows_test_file(self) -> None:
        cfg = self._get_support_config()
        patterns = cfg["forbidden_patterns"]
        assert not any(re.match(p, "test_foo.py") for p in patterns), (
            "forbidden_patterns must NOT match 'test_foo.py'"
        )

    def test_ssot_support_forbidden_patterns_rejects_any_agent_py(self) -> None:
        cfg = self._get_support_config()
        patterns = cfg["forbidden_patterns"]
        for name in ["LocationHealerAgent.py", "HierarchyAgent.py", "SomeRandomAgent.py"]:
            assert any(re.match(p, name) for p in patterns), f"forbidden_patterns must match {name!r}"

    def test_ssot_support_forbidden_patterns_allows_conftest(self) -> None:
        cfg = self._get_support_config()
        patterns = cfg["forbidden_patterns"]
        assert not any(re.match(p, "conftest.py") for p in patterns), (
            "forbidden_patterns must NOT match 'conftest.py'"
        )
