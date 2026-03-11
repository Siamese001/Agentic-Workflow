"""
Tests for HierarchyAgent._enforce_tests_structure and _get_approved_tests_subfolders.

Branch inventory (§1.3):
  _get_approved_tests_subfolders:
    - SOVEREIGN_TERRITORIES["tests"]["subfolders"] is dict  → frozenset of keys
    - "tests" key missing from SOVEREIGN_TERRITORIES         → frozenset()
    - "subfolders" key missing from tests config            → frozenset()
    - subfolders is not a dict (e.g. list)                  → frozenset()

  _enforce_tests_structure (per file encountered):
    - file is inside approved subfolder          → skipped (no violation)
    - file is root-level whitelisted             → skipped (no violation)
    - file stem is infra (__init__, conftest)    → skipped (no violation)
    - file stem starts with __                   → skipped (no violation)
    - file has no test_ prefix AND not infra     → violation + error, NO move
    - file has test_ prefix, inside approved     → skipped (no violation)
    - file has test_ prefix, NOT inside approved → violation + error, NO move
    - healing_enabled=True, non-test_ file       → still no move (report only)
"""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from unittest.mock import MagicMock, patch

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_agent(healing_enabled: bool = False):
    """Construct a minimal HierarchyAgent with mocked dependencies."""
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    agent = object.__new__(HierarchyAgent)
    agent.project_root = Path("/fake/root")
    agent.healing_enabled = healing_enabled
    agent.agent_name = "HierarchyAgent"
    agent.gatekeeper = MagicMock()
    return agent


def _fake_sovereign_territories(tests_subfolders):
    """Return a MappingProxyType that mimics SOVEREIGN_TERRITORIES."""
    inner = {"subfolders": tests_subfolders, "depth": 2, "purpose": "tests"}
    return MappingProxyType({"tests": MappingProxyType(inner)})


def _run_enforce(agent, tmp_path, files: list[tuple[str, str]]) -> dict:
    """
    Write files into tmp_path, call _enforce_tests_structure, return results dict.

    files: list of (relative_path_string, content)
    """
    for rel, content in files:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    results = {"violations_found": 0, "files_relocated": 0}
    agent._enforce_tests_structure(tmp_path, results)
    return results


# ---------------------------------------------------------------------------
# _get_approved_tests_subfolders — branch coverage
# ---------------------------------------------------------------------------


class TestGetApprovedTestsSubfolders:
    def test_derives_from_sovereign_territories(self):
        """Success path: returns frozenset of subfolders declared in SOVEREIGN_TERRITORIES."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        fake_st = _fake_sovereign_territories({"unit": {}, "support": {}, "integration": {}})
        with patch(
            "agentic_core.L5_safety.config.structure_blueprint_config.SOVEREIGN_TERRITORIES",
            fake_st,
        ):
            result = HierarchyAgent._get_approved_tests_subfolders()

        assert "unit" in result
        assert "support" in result
        assert "integration" in result
        assert isinstance(result, frozenset)

    def test_missing_tests_key_returns_empty(self):
        """Branch: SOVEREIGN_TERRITORIES has no 'tests' key → frozenset()."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        empty_st = MappingProxyType({})
        with patch(
            "agentic_core.L5_safety.config.structure_blueprint_config.SOVEREIGN_TERRITORIES",
            empty_st,
        ):
            result = HierarchyAgent._get_approved_tests_subfolders()

        assert result == frozenset()

    def test_missing_subfolders_key_returns_empty(self):
        """Branch: tests config exists but has no 'subfolders' key → frozenset()."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        st = MappingProxyType({"tests": MappingProxyType({"depth": 2})})
        with patch(
            "agentic_core.L5_safety.config.structure_blueprint_config.SOVEREIGN_TERRITORIES",
            st,
        ):
            result = HierarchyAgent._get_approved_tests_subfolders()

        assert result == frozenset()

    def test_subfolders_is_not_dict_returns_empty(self):
        """Branch: subfolders is a list (invalid schema) → frozenset()."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        st = MappingProxyType({"tests": {"subfolders": ["unit", "integration"]}})
        with patch(
            "agentic_core.L5_safety.config.structure_blueprint_config.SOVEREIGN_TERRITORIES",
            st,
        ):
            result = HierarchyAgent._get_approved_tests_subfolders()

        assert result == frozenset()

    def test_reflects_live_ssot_not_hardcoded(self):
        """Metamorphic: adding a new subfolder to SOVEREIGN_TERRITORIES is immediately reflected."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        st = _fake_sovereign_territories({"unit": {}, "brand_new_folder": {}})
        with patch(
            "agentic_core.L5_safety.config.structure_blueprint_config.SOVEREIGN_TERRITORIES",
            st,
        ):
            result = HierarchyAgent._get_approved_tests_subfolders()

        assert "brand_new_folder" in result
        assert "unit" in result


# ---------------------------------------------------------------------------
# _enforce_tests_structure — helpers to patch approved subfolders
# ---------------------------------------------------------------------------


def _patch_approved(approved: frozenset[str]):
    """Patch _get_approved_tests_subfolders to return a fixed set."""
    return patch(
        "agentic_core.L5_safety.reasoning.hierarchy_healer.HierarchyAgent._get_approved_tests_subfolders",
        return_value=approved,
    )


APPROVED = frozenset({"unit", "integration", "support", "fixtures", "e2e"})
WHITELIST = frozenset({"conftest.py", "pytest.ini", "sovereign_smoke_test.py"})


def _patch_whitelist():
    return patch(
        "agentic_core.L5_safety.config.structure_blueprint_config.TESTS_ROOT_FILE_WHITELIST",
        WHITELIST,
        create=True,
    )


# ---------------------------------------------------------------------------
# _enforce_tests_structure — success/skip branches
# ---------------------------------------------------------------------------


class TestEnforceTestsStructureSkipBranches:
    def test_file_in_approved_subfolder_is_skipped(self, tmp_path):
        """Success path: test_ file and infra files inside approved subfolder → no violation."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("unit/test_something.py", "def test_something(): pass"),
                    ("support/conftest.py", "import pytest"),
                    ("support/__init__.py", ""),
                ],
            )
        assert results["violations_found"] == 0
        assert results["files_relocated"] == 0

    def test_root_whitelisted_file_is_skipped(self, tmp_path):
        """Success path: conftest.py at root of tests/ → no violation."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("conftest.py", "import pytest"),
                ],
            )
        assert results["violations_found"] == 0

    def test_dunder_stem_is_skipped(self, tmp_path):
        """Success path: __init__.py anywhere → no violation."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("__init__.py", ""),
                    ("support/__init__.py", ""),
                ],
            )
        assert results["violations_found"] == 0

    def test_infra_stems_exempt_from_prefix_rule(self, tmp_path):
        """Success path: conftest / pytest_plugins at non-root depth → no violation."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("conftest.py", ""),
                    ("pytest_plugins.py", ""),
                ],
            )
        assert results["violations_found"] == 0


# ---------------------------------------------------------------------------
# _enforce_tests_structure — violation branches
# ---------------------------------------------------------------------------


class TestEnforceTestsStructureViolations:
    def test_non_test_prefixed_file_is_reported(self, tmp_path):
        """Negative control: Agent file without test_ prefix in tests/ → violation + error."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            with patch("agentic_core.L5_safety.reasoning.hierarchy_healer.Logger") as mock_log:
                results = _run_enforce(
                    agent,
                    tmp_path,
                    [
                        ("DAGMutatorAgent.py", "class DAGMutatorAgent: pass"),
                    ],
                )

        assert results["violations_found"] == 1
        mock_log.error.assert_called_once()
        err_msg = mock_log.error.call_args[0][0]
        assert "NON-TEST FILE IN tests/" in err_msg
        assert "DAGMutatorAgent.py" in err_msg

    def test_non_test_prefixed_file_is_never_moved(self, tmp_path):
        """Fail-closed: even with healing_enabled=True, agent file is NEVER auto-relocated."""
        agent = _make_agent(healing_enabled=True)
        src = tmp_path / "DAGMutatorAgent.py"
        with _patch_approved(APPROVED), _patch_whitelist():
            _run_enforce(
                agent,
                tmp_path,
                [
                    ("DAGMutatorAgent.py", "class DAGMutatorAgent: pass"),
                ],
            )

        # File must still be where it was — no move
        assert src.exists(), "File must not have been relocated by the healer"
        agent.gatekeeper.safe_move.assert_not_called()

    def test_test_prefixed_file_outside_approved_is_reported(self, tmp_path):
        """Negative control: test_ file at tests/ root (not in subfolder) → violation + error."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            with patch("agentic_core.L5_safety.reasoning.hierarchy_healer.Logger") as mock_log:
                results = _run_enforce(
                    agent,
                    tmp_path,
                    [
                        ("test_orphan.py", "def test_orphan(): pass"),
                    ],
                )

        assert results["violations_found"] == 1
        mock_log.error.assert_called_once()
        err_msg = mock_log.error.call_args[0][0]
        assert "UNCATEGORIZED TEST" in err_msg
        assert "test_orphan.py" in err_msg

    def test_test_prefixed_file_outside_approved_never_moved(self, tmp_path):
        """Fail-closed: uncategorized test_ file is NEVER auto-relocated even with healing."""
        agent = _make_agent(healing_enabled=True)
        src = tmp_path / "test_orphan.py"
        with _patch_approved(APPROVED), _patch_whitelist():
            _run_enforce(
                agent,
                tmp_path,
                [
                    ("test_orphan.py", "def test_orphan(): pass"),
                ],
            )

        assert src.exists(), "Uncategorized test must not have been moved"
        agent.gatekeeper.safe_move.assert_not_called()

    def test_multiple_violations_counted_independently(self, tmp_path):
        """Branch divergence: two bad files → violations_found == 2."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("AgentX.py", "class AgentX: pass"),
                    ("AgentY.py", "class AgentY: pass"),
                ],
            )
        assert results["violations_found"] == 2

    def test_mix_of_valid_and_invalid_files(self, tmp_path):
        """Matrix: valid files don't inflate violation count; bad files do."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("unit/test_good.py", "def test_good(): pass"),  # valid → skip
                    ("support/conftest.py", "import pytest"),  # infra in approved → skip
                    ("__init__.py", ""),  # dunder → skip
                    ("conftest.py", ""),  # whitelist → skip
                    ("BadAgent.py", "class BadAgent: pass"),  # violation
                ],
            )
        assert results["violations_found"] == 1


# ---------------------------------------------------------------------------
# Boundary / edge-case coverage (§1.8)
# ---------------------------------------------------------------------------


class TestEnforceTestsStructureBoundaries:
    def test_empty_tests_directory(self, tmp_path):
        """Empty input: no files → zero violations."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = {"violations_found": 0, "files_relocated": 0}
            agent._enforce_tests_structure(tmp_path, results)
        assert results["violations_found"] == 0

    def test_approved_set_empty_every_file_is_reported(self, tmp_path):
        """Boundary: approved_subfolders is empty → all non-infra files become violations."""
        agent = _make_agent()
        with _patch_approved(frozenset()), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("unit/test_something.py", "def test_something(): pass"),
                ],
            )
        # test_something.py IS prefixed with test_ but unit/ not in approved → uncategorized
        assert results["violations_found"] == 1

    def test_deeply_nested_approved_file_is_skipped(self, tmp_path):
        """Boundary: file 3 levels deep inside approved subfolder → no violation."""
        agent = _make_agent()
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("unit/agentic_core/L5_safety/test_deep.py", "def test_deep(): pass"),
                ],
            )
        assert results["violations_found"] == 0

    def test_non_py_files_ignored(self, tmp_path):
        """Boundary: .md, .json, .txt files are never inspected."""
        agent = _make_agent()
        (tmp_path / "README.md").write_text("docs")
        (tmp_path / "data.json").write_text("{}")
        with _patch_approved(APPROVED), _patch_whitelist():
            results = {"violations_found": 0, "files_relocated": 0}
            agent._enforce_tests_structure(tmp_path, results)
        assert results["violations_found"] == 0

    def test_files_relocated_never_incremented(self, tmp_path):
        """Invariant: files_relocated is NEVER incremented by _enforce_tests_structure."""
        agent = _make_agent(healing_enabled=True)
        with _patch_approved(APPROVED), _patch_whitelist():
            results = _run_enforce(
                agent,
                tmp_path,
                [
                    ("BadAgent.py", "class BadAgent: pass"),
                    ("test_orphan.py", "def test_orphan(): pass"),
                    ("unit/test_ok.py", "def test_ok(): pass"),
                ],
            )
        assert results["files_relocated"] == 0, (
            "_enforce_tests_structure must never relocate files; files_relocated should remain 0"
        )


# ---------------------------------------------------------------------------
# Determinism (§1.10)
# ---------------------------------------------------------------------------


class TestEnforceTestsStructureDeterminism:
    def test_identical_input_identical_output(self, tmp_path):
        """Identical input → identical violation count on repeated calls."""
        agent = _make_agent()
        files = [("BadAgent.py", "class BadAgent: pass")]
        with _patch_approved(APPROVED), _patch_whitelist():
            r1 = _run_enforce(agent, tmp_path, files)
            # Re-run on same state
            results2 = {"violations_found": 0, "files_relocated": 0}
            agent._enforce_tests_structure(tmp_path, results2)

        assert r1["violations_found"] == results2["violations_found"]

    def test_approved_subfolders_is_frozenset(self):
        """Invariant: _get_approved_tests_subfolders always returns a frozenset."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        result = HierarchyAgent._get_approved_tests_subfolders()
        assert isinstance(result, frozenset)
