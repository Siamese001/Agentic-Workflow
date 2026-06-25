from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_pytest_ini_does_not_continue_after_collection_errors() -> None:
    text = (ROOT / "pytest.ini").read_text(encoding="utf-8")
    addopts_lines = [line for line in text.splitlines() if line.strip().startswith("addopts =")]
    assert addopts_lines, "pytest.ini must define addopts"
    addopts = " ".join(addopts_lines)
    assert "--continue-on-collection-errors" not in addopts


def test_runtime_observability_plugin_is_deferred_for_plain_unit_runs(monkeypatch) -> None:
    conftest_path = ROOT / "tests" / "conftest.py"
    spec = importlib.util.spec_from_file_location("_root_conftest_for_harness_test", conftest_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.delenv("PYTEST_ENABLE_RUNTIME_OBSERVABILITY_PLUGIN", raising=False)
    original_argv = list(sys.argv)
    try:
        sys.argv = ["pytest", "tests/unit/apps_rg/test_narrative_alignment_gates.py"]
        assert spec.loader is not None
        spec.loader.exec_module(module)
    finally:
        sys.argv = original_argv

    assert module.pytest_plugins == ()
