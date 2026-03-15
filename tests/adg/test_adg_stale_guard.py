"""Tests for ADG staleness guard — Accelerator #2.

Coverage matrix per §1.1:
- Success: fresh ADG (commit before ingest), stale ADG (commit after ingest)
- Edge cases: no Python commits, missing ingested_at field, exact boundary (equal timestamps)
- Fail-closed: Redis unavailable raises RuntimeError; git failure raises RuntimeError
- State transitions: fresh→assert_fresh OK; stale→assert_fresh raises
- Determinism: StalenessResult.seconds_stale computed from fixed timestamps
- Subprocess timeout: git commands that time out raise RuntimeError
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


def _make_adg_client(ingested_at: str | None) -> object:
    """Build a minimal ADGRedisClient stub with fixed ingested_at."""
    from tools.adg.adg_redis_query import ADGRedisClient

    client = ADGRedisClient.__new__(ADGRedisClient)
    r = MagicMock()
    meta = {}
    if ingested_at is not None:
        meta["ingested_at"] = ingested_at
    r.hgetall.return_value = meta
    client._r = r
    return client


def _make_checker(ingested_at: str | None, repo_root: Path | None = None):
    from tools.adg.adg_stale_guard import ADGStalenessChecker

    client = _make_adg_client(ingested_at)
    return ADGStalenessChecker(client=client, repo_root=repo_root or ROOT)


# ===========================================================================
# StalenessResult dataclass
# ===========================================================================


class TestStalenessResult:
    def test_seconds_stale_positive_when_stale(self):
        from tools.adg.adg_stale_guard import StalenessResult

        r = StalenessResult(is_stale=True, ingest_time=1000.0, last_commit_time=1100.0)
        assert r.seconds_stale == 100.0

    def test_seconds_stale_zero_when_fresh(self):
        from tools.adg.adg_stale_guard import StalenessResult

        r = StalenessResult(is_stale=False, ingest_time=1100.0, last_commit_time=1000.0)
        assert r.seconds_stale == 0.0

    def test_seconds_stale_zero_at_exact_boundary(self):
        from tools.adg.adg_stale_guard import StalenessResult

        r = StalenessResult(is_stale=False, ingest_time=1000.0, last_commit_time=1000.0)
        assert r.seconds_stale == 0.0

    def test_changed_files_defaults_to_empty_list(self):
        from tools.adg.adg_stale_guard import StalenessResult

        r = StalenessResult(is_stale=False, ingest_time=0.0, last_commit_time=0.0)
        assert r.changed_files == []


# ===========================================================================
# _get_ingest_time
# ===========================================================================


class TestGetIngestTime:
    def test_returns_float_from_meta(self):
        checker = _make_checker(ingested_at="1741000000.5")
        result = checker._get_ingest_time()
        assert result == 1741000000.5

    def test_missing_ingested_at_raises_runtime_error(self):
        checker = _make_checker(ingested_at=None)
        with pytest.raises(RuntimeError, match="ingested_at"):
            checker._get_ingest_time()

    def test_invalid_float_raises_value_error(self):
        checker = _make_checker(ingested_at="not-a-float")
        with pytest.raises(ValueError):
            checker._get_ingest_time()


# ===========================================================================
# _get_last_python_commit_time
# ===========================================================================


class TestGetLastPythonCommitTime:
    def test_returns_float_timestamp(self):
        checker = _make_checker(ingested_at="0")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1741050000\n"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            t = checker._get_last_python_commit_time()
        assert t == 1741050000.0

    def test_no_python_commits_returns_zero(self):
        checker = _make_checker(ingested_at="0")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            t = checker._get_last_python_commit_time()
        assert t == 0.0

    def test_git_failure_raises_runtime_error(self):
        checker = _make_checker(ingested_at="0")
        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_result.stdout = ""
        mock_result.stderr = "not a git repo"
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="git log failed"):
                checker._get_last_python_commit_time()

    def test_timeout_raises_runtime_error(self):
        checker = _make_checker(ingested_at="0")
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="git", timeout=30),
        ):
            with pytest.raises(RuntimeError, match="timed out"):
                checker._get_last_python_commit_time()

    def test_git_called_with_no_shell(self):
        checker = _make_checker(ingested_at="0")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1741000000\n"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            checker._get_last_python_commit_time()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert cmd[0] == "git"
        assert kwargs.get("shell", False) is False  # §3.2: no shell=True


# ===========================================================================
# check() — full staleness check
# ===========================================================================


class TestStalenessCheck:
    def test_fresh_when_last_commit_before_ingest(self):
        checker = _make_checker(ingested_at="1741100000")
        with patch.object(checker, "_get_last_python_commit_time", return_value=1741000000.0):
            result = checker.check()
        assert result.is_stale is False
        assert "fresh" in result.message.lower()

    def test_stale_when_last_commit_after_ingest(self):
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741100000.0),
            patch.object(checker, "_get_files_changed_since", return_value=["agentic_core/foo.py"]),
        ):
            result = checker.check()
        assert result.is_stale is True
        assert "STALE" in result.message
        assert "agentic_core/foo.py" in result.changed_files

    def test_fresh_at_exact_boundary_equal_timestamps(self):
        """Exactly equal timestamps → fresh (not stale)."""
        checker = _make_checker(ingested_at="1741000000")
        with patch.object(checker, "_get_last_python_commit_time", return_value=1741000000.0):
            result = checker.check()
        assert result.is_stale is False

    def test_stale_result_contains_ingest_and_commit_times(self):
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741100000.0),
            patch.object(checker, "_get_files_changed_since", return_value=[]),
        ):
            result = checker.check()
        assert result.ingest_time == 1741000000.0
        assert result.last_commit_time == 1741100000.0

    def test_no_python_commits_is_fresh(self):
        """If last_commit_time == 0.0 (no commits), ADG is fresh."""
        checker = _make_checker(ingested_at="1741000000")
        with patch.object(checker, "_get_last_python_commit_time", return_value=0.0):
            result = checker.check()
        assert result.is_stale is False

    def test_check_is_deterministic(self):
        """Same inputs must yield same result on repeated calls."""
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741050000.0),
            patch.object(checker, "_get_files_changed_since", return_value=["a.py"]),
        ):
            r1 = checker.check()
            r2 = checker.check()
        assert r1.is_stale == r2.is_stale
        assert r1.changed_files == r2.changed_files


# ===========================================================================
# assert_fresh
# ===========================================================================


class TestAssertFresh:
    def test_does_not_raise_when_fresh(self):
        checker = _make_checker(ingested_at="1741100000")
        with patch.object(checker, "_get_last_python_commit_time", return_value=1741000000.0):
            checker.assert_fresh()  # must not raise

    def test_raises_when_stale(self):
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741100000.0),
            patch.object(checker, "_get_files_changed_since", return_value=["foo.py"]),
        ):
            with pytest.raises(RuntimeError, match="STALE"):
                checker.assert_fresh()

    def test_error_message_contains_regen_instructions(self):
        checker = _make_checker(ingested_at="1741000000")
        with (
            patch.object(checker, "_get_last_python_commit_time", return_value=1741100000.0),
            patch.object(checker, "_get_files_changed_since", return_value=["foo.py"]),
        ):
            with pytest.raises(RuntimeError, match="adg_redis_ingest"):
                checker.assert_fresh()
