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


def test_suggest_report_subdir_is_stable() -> None:
    config = load_module("territory_config", "territory_ssot_definitions_config.py")
    assert config.suggest_report_subdir("audit_gap_analysis.json") == "audit"
    assert config.suggest_report_subdir("weekly_status_report.md") in {"status", "misc"}


def test_classify_territory_marks_core_as_protected() -> None:
    config = load_module("territory_config", "territory_ssot_definitions_config.py")
    assert config.classify_territory("agentic_core/L0_routing/router.py") == "core"
    assert config.is_protected_territory("agentic_core/L0_routing/router.py") is True
