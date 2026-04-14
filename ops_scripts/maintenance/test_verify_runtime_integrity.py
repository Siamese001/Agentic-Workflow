from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_run_checks_returns_named_results() -> None:
    verification = load_module("verification_module", "verification.py")
    results = verification.run_checks()
    assert results
    assert all(result.name for result in results)


def test_tempfile_write_check_passes() -> None:
    verification = load_module("verification_module", "verification.py")
    result = verification.verify_tempfile_writes()
    assert result.passed is True
