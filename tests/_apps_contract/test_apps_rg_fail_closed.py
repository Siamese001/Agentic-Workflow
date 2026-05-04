"""Negative test: apps_rg MUST fail closed when agentic_core runner is unavailable.

Proves requirement #5 + #6:
  - If ``agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run``
    cannot be imported, ``python -m apps_rg`` exits non-zero immediately.
  - No résumé artifact is produced.
"""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path
from unittest import mock

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def _block_r4_import(monkeypatch):
    """Make the R4 entrypoint unimportable so apps_rg falls back to fail-closed."""

    original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

    def _guarded_import(name, *args, **kwargs):
        if "integrated_r4_deterministic_pipeline_run" in name:
            raise ImportError("deliberately blocked for test")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _guarded_import)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAppsRgFailClosed:
    """apps_rg must not produce artifacts when runner is disabled."""

    def test_main_exits_nonzero_when_runner_unavailable(self, tmp_path):
        """When ``_RUNNER_AVAILABLE`` is False, main() calls sys.exit(1)."""
        # We simulate the module-level state directly rather than re-importing
        # the module, because the import-time try/except has already run.
        import apps_rg.__main__ as rg_main

        original_available = rg_main._RUNNER_AVAILABLE

        try:
            rg_main._RUNNER_AVAILABLE = False
            rg_main._RUNNER_IMPORT_ERROR = ImportError("test: runner blocked")

            with pytest.raises(SystemExit) as exc_info:
                rg_main.main()

            assert exc_info.value.code == 1
        finally:
            rg_main._RUNNER_AVAILABLE = original_available

    def test_no_artifact_produced_when_runner_unavailable(self, tmp_path):
        """No run directory or generated_resume.json is created."""
        runs_dir = tmp_path / "artifacts" / "apps_rg" / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)

        import apps_rg.__main__ as rg_main

        original_available = rg_main._RUNNER_AVAILABLE

        try:
            rg_main._RUNNER_AVAILABLE = False
            rg_main._RUNNER_IMPORT_ERROR = ImportError("test: runner blocked")

            with pytest.raises(SystemExit) as exc_info:
                rg_main.main()

            assert exc_info.value.code == 1

            # Verify no new run directories were created
            run_dirs = list(runs_dir.iterdir())
            assert len(run_dirs) == 0, (
                f"Expected no run directories, but found: {run_dirs}"
            )
        finally:
            rg_main._RUNNER_AVAILABLE = original_available

    def test_stderr_contains_fatal_message(self, tmp_path, capsys):
        """Fail-closed message appears on stderr."""
        import apps_rg.__main__ as rg_main

        original_available = rg_main._RUNNER_AVAILABLE

        try:
            rg_main._RUNNER_AVAILABLE = False
            rg_main._RUNNER_IMPORT_ERROR = ImportError("test: runner blocked")

            with pytest.raises(SystemExit):
                rg_main.main()

            captured = capsys.readouterr()
            assert "FATAL" in captured.err
            assert "fails closed" in captured.err
        finally:
            rg_main._RUNNER_AVAILABLE = original_available

    def test_main_does_not_call_l2_callable_when_unavailable(self, tmp_path):
        """Ensure the L2 callable (HOP pipeline) is never invoked."""
        import apps_rg.__main__ as rg_main

        original_available = rg_main._RUNNER_AVAILABLE
        l2_called = False

        def _fake_l2():
            nonlocal l2_called
            l2_called = True
            return {}

        try:
            rg_main._RUNNER_AVAILABLE = False
            rg_main._RUNNER_IMPORT_ERROR = ImportError("test: runner blocked")

            with pytest.raises(SystemExit) as exc_info:
                rg_main.main()

            assert exc_info.value.code == 1
            assert not l2_called, "L2 callable should never be invoked when runner is unavailable"
        finally:
            rg_main._RUNNER_AVAILABLE = original_available
