"""Smoke tests for benchmarking_util — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.benchmarking_util")


def test_module_imports_clean():
    assert mod is not None


def test_BenchmarkResult_present():
    assert hasattr(mod, "BenchmarkResult")
    assert isinstance(mod.BenchmarkResult, type)


def test_BenchmarkStats_present():
    assert hasattr(mod, "BenchmarkStats")
    assert isinstance(mod.BenchmarkStats, type)
