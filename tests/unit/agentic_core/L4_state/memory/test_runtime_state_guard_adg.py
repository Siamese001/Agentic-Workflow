"""ADG-driven tests for agentic_core/L4_state/memory/runtime_state_guard.py — fan_in=3.

Contract tests: RuntimeStateGuard importability, get_metric, increment_metric,
and batch context manager. Write gateway is mocked to avoid filesystem side effects.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.memory.runtime_state_guard import RuntimeStateGuard


def _make_guard(tmp_path: Path) -> RuntimeStateGuard:
    state_path = tmp_path / "runtime_state.json"
    state_path.write_text("{}", encoding="utf-8")
    guard = RuntimeStateGuard.__new__(RuntimeStateGuard)
    guard.state_path = state_path
    guard.backup_path = tmp_path / "runtime_state.json.bak"
    guard._state_cache = {}
    guard._batch_depth = 0
    guard._dirty = False
    return guard


class TestRuntimeStateGuardImport:
    def test_class_importable(self):
        assert callable(RuntimeStateGuard)


class TestRuntimeStateGuardGetMetric:
    def test_missing_key_returns_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            assert guard.get_metric("cycles_healed") == 0

    def test_missing_key_custom_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            assert guard.get_metric("x", default=42) == 42

    def test_existing_metric_returned(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            guard._state_cache["shared_alignment_metrics"] = {"cycles_healed": 7}
            assert guard.get_metric("cycles_healed") == 7


class TestRuntimeStateGuardIncrementMetric:
    def test_increment_adds_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            with patch.object(guard, "_atomic_persist"):
                guard.increment_metric("cycles_healed")
                assert guard.get_metric("cycles_healed") == 1

    def test_increment_cumulative(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            with patch.object(guard, "_atomic_persist"):
                guard.increment_metric("cycles_healed")
                guard.increment_metric("cycles_healed")
                guard.increment_metric("cycles_healed")
                assert guard.get_metric("cycles_healed") == 3

    def test_increment_custom_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            with patch.object(guard, "_atomic_persist"):
                guard.increment_metric("batch_count", value=5)
                assert guard.get_metric("batch_count") == 5

    def test_increment_in_batch_defers_persist(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            guard._batch_depth = 1  # inside batch context
            with patch.object(guard, "_atomic_persist") as mock_persist:
                guard.increment_metric("x")
                mock_persist.assert_not_called()
                assert guard._dirty is True

    def test_increment_outside_batch_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            with patch.object(guard, "_atomic_persist") as mock_persist:
                guard.increment_metric("x")
                mock_persist.assert_called_once()
