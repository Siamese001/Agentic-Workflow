"""Wave F1.4 regression tests — _ssot_routing / _ssot_types full deletion.

Plan: `.windsurf/plans/routing-followups-7a2c91.md` Wave F1.4.

These modules were retained as deprecated shims after Wave F1 (2026-04-21)
with 9 shim-validation tests. Fan-in scan on 2026-04-21 confirmed zero
production callers outside the archived `tools/archive/tools_graveyard_w5.12/`
directory and the shim tests themselves. This wave deletes both modules plus
their self-referential test file.

These guards assert the files remain gone.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_ssot_routing_file_deleted():
    path = REPO_ROOT / "ops_scripts" / "dev_tools" / "L0_routing_scripts" / "_ssot_routing.py"
    assert not path.exists(), f"Expected deleted but still exists: {path}"


def test_ssot_types_file_deleted():
    path = REPO_ROOT / "ops_scripts" / "dev_tools" / "L0_routing_scripts" / "_ssot_types.py"
    assert not path.exists(), f"Expected deleted but still exists: {path}"


def test_ssot_routing_shim_test_file_deleted():
    """The shim-validation test file itself is deleted because its subject
    no longer exists. Wave F1.4 regression guards (this file) replace it."""
    path = REPO_ROOT / "tests" / "unit" / "ops_scripts" / "test_ssot_routing_wave3_shim.py"
    assert not path.exists(), f"Expected deleted but still exists: {path}"


def test_ssot_routing_module_not_importable():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("ops_scripts.dev_tools.L0_routing_scripts._ssot_routing")


def test_ssot_types_module_not_importable():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("ops_scripts.dev_tools.L0_routing_scripts._ssot_types")
