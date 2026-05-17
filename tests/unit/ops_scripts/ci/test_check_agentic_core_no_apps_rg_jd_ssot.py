from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_rg_jd0_gate_passes() -> None:
    script = REPO_ROOT / "ops_scripts" / "ci" / "check_agentic_core_no_apps_rg_jd_ssot.py"
    spec = importlib.util.spec_from_file_location("_rg_jd0_gate_under_test", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.main() == 0
