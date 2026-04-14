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


def test_normalize_relative_path_uses_posix_separators() -> None:
    config = load_module("territory_config", "territory_ssot_definitions_config.py")
    assert (
        config.normalize_relative_path(r"docs\\reports\\audit\\report.md") == "docs/reports/audit/report.md"
    )


def test_report_subdir_defaults_to_misc() -> None:
    config = load_module("territory_config", "territory_ssot_definitions_config.py")
    assert config.suggest_report_subdir("unclassified_output.bin") == "misc"
