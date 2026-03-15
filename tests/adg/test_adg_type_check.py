"""Tests for ADG-scoped incremental type checker — Accelerator #4.

Coverage matrix per §1.1:
- Success: blast radius with 0/1/2 depth, empty file list, run_mypy clean/error
- Edge cases: depth=0 (changed files only), backslash paths, depth validation,
              file not in ADG, no importers, cycle prevention (visited guard)
- Fail-closed: Redis error propagates; mypy timeout raises; mypy not found raises
- Determinism: identical input → identical blast radius on every call
- MypyResult: passed, error_lines, error_count properties
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client(
    nodes_by_file: dict[str, set[str]],
    fan_in_imports: dict[str, set[str]],
    nodes: dict[str, dict[str, str]],
) -> object:
    """Build a minimal ADGRedisClient stub for blast radius testing."""
    from tools.adg.adg_redis_query import ADGRedisClient

    client = ADGRedisClient.__new__(ADGRedisClient)
    r = MagicMock()

    def smembers(key: str) -> set[str]:
        if key.startswith("adg:nodes:by_file:"):
            return nodes_by_file.get(key[len("adg:nodes:by_file:") :], set())
        if key.startswith("adg:edge:in:") and key.endswith(":imports"):
            nid = key[len("adg:edge:in:") : -len(":imports")]
            return fan_in_imports.get(nid, set())
        return set()

    def hgetall(key: str) -> dict[str, str]:
        nid = key[len("adg:node:") :]
        return nodes.get(nid, {})

    r.smembers.side_effect = smembers
    r.hgetall.side_effect = hgetall
    client._r = r
    return client


def _make_checker(nodes_by_file, fan_in_imports, nodes):
    from tools.adg.adg_type_check import ADGTypeChecker

    return ADGTypeChecker(
        client=_make_client(nodes_by_file, fan_in_imports, nodes),
        repo_root=ROOT,
    )


# ===========================================================================
# MypyResult dataclass
# ===========================================================================


class TestMypyResult:
    def test_passed_true_when_exit_code_zero(self):
        from tools.adg.adg_type_check import MypyResult

        r = MypyResult(exit_code=0, stdout="", stderr="")
        assert r.passed is True

    def test_passed_false_when_exit_code_nonzero(self):
        from tools.adg.adg_type_check import MypyResult

        r = MypyResult(exit_code=1, stdout="foo.py:1: error: Incompatible types", stderr="")
        assert r.passed is False

    def test_error_lines_extracts_error_lines(self):
        from tools.adg.adg_type_check import MypyResult

        stdout = "foo.py:1: error: Incompatible types\nfoo.py:2: note: something\nfoo.py:3: error: Missing"
        r = MypyResult(exit_code=1, stdout=stdout, stderr="")
        assert len(r.error_lines) == 2
        assert all(": error:" in ln for ln in r.error_lines)

    def test_error_lines_empty_when_no_errors(self):
        from tools.adg.adg_type_check import MypyResult

        r = MypyResult(exit_code=0, stdout="Success: no issues found", stderr="")
        assert r.error_lines == []

    def test_error_count_matches_error_lines(self):
        from tools.adg.adg_type_check import MypyResult

        stdout = "a.py:1: error: E1\nb.py:2: error: E2\nb.py:3: note: N1"
        r = MypyResult(exit_code=1, stdout=stdout, stderr="")
        assert r.error_count == 2

    def test_scoped_files_defaults_to_empty(self):
        from tools.adg.adg_type_check import MypyResult

        r = MypyResult(exit_code=0, stdout="", stderr="")
        assert r.scoped_files == []


# ===========================================================================
# get_blast_radius
# ===========================================================================


class TestGetBlastRadius:
    def test_depth_zero_returns_only_changed_files(self):
        checker = _make_checker(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_imports={"n1": {"importer:1"}},
            nodes={"importer:1": {"resolved_path": "agentic_core/importer.py"}},
        )
        result = checker.get_blast_radius(["prod.py"], depth=0)
        assert result == ["prod.py"]
        assert "agentic_core/importer.py" not in result

    def test_depth_one_includes_direct_importers(self):
        checker = _make_checker(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_imports={"n1": {"imp:1"}},
            nodes={"imp:1": {"resolved_path": "agentic_core/importer.py"}},
        )
        result = checker.get_blast_radius(["prod.py"], depth=1)
        assert "prod.py" in result
        assert "agentic_core/importer.py" in result

    def test_depth_two_includes_transitive_importers(self):
        checker = _make_checker(
            nodes_by_file={
                "lib.py": {"n_lib"},
                "agentic_core/consumer.py": {"n_consumer"},
            },
            fan_in_imports={
                "n_lib": {"n_consumer"},
                "n_consumer": {"n_top"},
            },
            nodes={
                "n_consumer": {"resolved_path": "agentic_core/consumer.py"},
                "n_top": {"resolved_path": "agentic_core/top.py"},
            },
        )
        result = checker.get_blast_radius(["lib.py"], depth=2)
        assert "lib.py" in result
        assert "agentic_core/consumer.py" in result
        assert "agentic_core/top.py" in result

    def test_empty_changed_files_returns_empty(self):
        checker = _make_checker({}, {}, {})
        result = checker.get_blast_radius([], depth=1)
        assert result == []

    def test_file_not_in_adg_returns_just_itself(self):
        checker = _make_checker({}, {}, {})
        result = checker.get_blast_radius(["totally_unknown.py"], depth=1)
        assert result == ["totally_unknown.py"]

    def test_no_importers_returns_only_changed_files(self):
        checker = _make_checker(
            nodes_by_file={"leaf.py": {"n1"}},
            fan_in_imports={},  # no one imports leaf
            nodes={},
        )
        result = checker.get_blast_radius(["leaf.py"], depth=1)
        assert result == ["leaf.py"]

    def test_result_is_sorted(self):
        checker = _make_checker(
            nodes_by_file={"z_prod.py": {"n1"}},
            fan_in_imports={"n1": {"imp_a", "imp_z"}},
            nodes={
                "imp_a": {"resolved_path": "a_importer.py"},
                "imp_z": {"resolved_path": "z_importer.py"},
            },
        )
        result = checker.get_blast_radius(["z_prod.py"], depth=1)
        assert result == sorted(result)

    def test_depth_negative_raises_value_error(self):
        checker = _make_checker({}, {}, {})
        with pytest.raises(ValueError, match="depth"):
            checker.get_blast_radius(["prod.py"], depth=-1)

    def test_backslash_paths_normalized(self):
        checker = _make_checker(
            nodes_by_file={"agentic_core/L0_routing/router.py": {"n1"}},
            fan_in_imports={"n1": {"imp:1"}},
            nodes={"imp:1": {"resolved_path": "agentic_core/consumer.py"}},
        )
        result = checker.get_blast_radius(["agentic_core\\L0_routing\\router.py"], depth=1)
        assert "agentic_core/L0_routing/router.py" in result

    def test_non_python_files_in_nodes_excluded(self):
        """Only .py files should be included in blast radius."""
        checker = _make_checker(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_imports={"n1": {"imp_py", "imp_json"}},
            nodes={
                "imp_py": {"resolved_path": "agentic_core/consumer.py"},
                "imp_json": {"resolved_path": "config/settings.json"},  # not .py
            },
        )
        result = checker.get_blast_radius(["prod.py"], depth=1)
        assert "agentic_core/consumer.py" in result
        assert "config/settings.json" not in result

    def test_blast_radius_deterministic(self):
        checker = _make_checker(
            nodes_by_file={"prod.py": {"n1"}},
            fan_in_imports={"n1": {"imp:1"}},
            nodes={"imp:1": {"resolved_path": "agentic_core/importer.py"}},
        )
        r1 = checker.get_blast_radius(["prod.py"], depth=1)
        r2 = checker.get_blast_radius(["prod.py"], depth=1)
        assert r1 == r2

    def test_already_visited_files_not_revisited(self):
        """Cycle guard: if file A imports B and B imports A, no infinite loop."""
        checker = _make_checker(
            nodes_by_file={
                "a.py": {"n_a"},
                "b.py": {"n_b"},
            },
            fan_in_imports={
                "n_a": {"n_b"},  # b imports a
                "n_b": {"n_a"},  # a imports b (cycle!)
            },
            nodes={
                "n_a": {"resolved_path": "a.py"},
                "n_b": {"resolved_path": "b.py"},
            },
        )
        # Must terminate and not infinite-loop
        result = checker.get_blast_radius(["a.py"], depth=3)
        assert "a.py" in result
        assert "b.py" in result


# ===========================================================================
# run_mypy
# ===========================================================================


class TestRunMypy:
    def _make_checker(self):
        from tools.adg.adg_type_check import ADGTypeChecker

        return ADGTypeChecker(client=MagicMock(), repo_root=ROOT)

    def test_empty_file_list_returns_success_without_calling_mypy(self):
        checker = self._make_checker()
        with patch("subprocess.run") as mock_run:
            result = checker.run_mypy([])
        mock_run.assert_not_called()
        assert result.passed is True
        assert result.scoped_files == []

    def test_passes_files_to_mypy_command(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found in 1 source file"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker.run_mypy(["agentic_core/L0_routing/router.py"])
        call_args = mock_run.call_args[0][0]
        assert "agentic_core/L0_routing/router.py" in call_args

    def test_strict_flag_added_when_requested(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker.run_mypy(["prod.py"], strict=True)
        call_args = mock_run.call_args[0][0]
        assert "--strict" in call_args

    def test_strict_flag_absent_by_default(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker.run_mypy(["prod.py"])
        call_args = mock_run.call_args[0][0]
        assert "--strict" not in call_args

    def test_returns_passed_false_on_nonzero_exit(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "prod.py:1: error: Incompatible types"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            result = checker.run_mypy(["prod.py"])
        assert result.passed is False
        assert result.exit_code == 1

    def test_scoped_files_reflects_input(self):
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found in 2 source files"
        mock_result.stderr = ""
        files = ["a.py", "b.py"]
        with patch("subprocess.run", return_value=mock_result):
            result = checker.run_mypy(files)
        assert result.scoped_files == files

    def test_timeout_raises_runtime_error(self):
        checker = self._make_checker()
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="mypy", timeout=120),
        ):
            with pytest.raises(RuntimeError, match="timed out"):
                checker.run_mypy(["prod.py"])

    def test_mypy_not_found_raises_runtime_error(self):
        checker = self._make_checker()
        with patch(
            "subprocess.run",
            side_effect=FileNotFoundError("mypy not found"),
        ):
            with pytest.raises(RuntimeError, match="mypy not found"):
                checker.run_mypy(["prod.py"])

    def test_no_shell_true_in_subprocess_call(self):
        """§3.2: subprocess calls must never use shell=True."""
        checker = self._make_checker()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success: no issues found"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker.run_mypy(["prod.py"])
        _, kwargs = mock_run.call_args
        assert kwargs.get("shell", False) is False


# ===========================================================================
# Fail-closed — Redis errors must propagate
# ===========================================================================


class TestBlastRadiusFailClosed:
    def test_redis_connection_error_propagates(self):
        """Redis ConnectionError must NOT be swallowed."""
        import redis

        from tools.adg.adg_redis_query import ADGRedisClient
        from tools.adg.adg_type_check import ADGTypeChecker

        client = ADGRedisClient.__new__(ADGRedisClient)
        bad_r = MagicMock()
        bad_r.smembers.side_effect = redis.ConnectionError("refused")
        client._r = bad_r

        checker = ADGTypeChecker(client=client, repo_root=ROOT)
        with pytest.raises(redis.ConnectionError):
            checker.get_blast_radius(["agentic_core/prod.py"], depth=1)
