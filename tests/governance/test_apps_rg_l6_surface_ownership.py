"""Governance — apps_rg L6 surface ownership (no duplicate runtime engine).

Plan: apps-rg-l6-shadow-learning-hardening-7e4c2f  W2
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_no_apps_rg_runtime_l6_shadow_learning_module() -> None:
    legacy = REPO_ROOT / "apps_rg" / "runtime" / "l6_shadow_learning.py"
    assert not legacy.exists(), "l6_shadow_learning.py must remain deleted"


def test_l6_shadow_learning_not_importable_from_runtime() -> None:
    with pytest.raises(ModuleNotFoundError):
        import apps_rg.runtime.l6_shadow_learning  # noqa: F401


def test_package_driven_l6_binding_is_canonical_engine() -> None:
    from agentic_core.L6_learning.package_driven_l6_binding import PackageDrivenL6Binding

    assert hasattr(PackageDrivenL6Binding, "process_completed_run")


def test_no_fake_l6_label_gate_passes() -> None:
    import subprocess
    import sys

    script = REPO_ROOT / "ops_scripts" / "ci" / "check_no_fake_l6_span_label.py"
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


def test_l6_w2_engine_gate_passes() -> None:
    import subprocess
    import sys

    script = REPO_ROOT / "ops_scripts" / "ci" / "check_no_apps_rg_runtime_l6_engine.py"
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
