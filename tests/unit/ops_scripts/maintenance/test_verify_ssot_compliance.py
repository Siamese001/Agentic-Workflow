from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parents[4] / "ops_scripts" / "maintenance"


def load_module(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, HERE / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
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
