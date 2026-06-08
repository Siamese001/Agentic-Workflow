"""Regression tests for the pytest-config SSOT validator.

Locks the corrected contract: xdist parallelism is validated against
pyproject.toml (the canonical CI source), NOT required in pytest.ini, which
intentionally omits it to keep the VS Code / Windsurf test explorer working.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULE = REPO_ROOT / "ops_scripts" / "ci" / "_validate_pytest_config.py"


def _load():
    spec = importlib.util.spec_from_file_location("_validate_pytest_config", MODULE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


vp = _load()


def _cfg(source, *, n=None, dist=None, timeout=180, markers=("serial",)):
    return vp.PytestConfig(
        source=source,
        addopts="",
        testpaths=[],
        markers=list(markers),
        timeout=timeout,
        n_workers=n,
        dist_mode=dist,
    )


def test_xdist_only_in_pyproject_is_ok():
    # The real repo state: pytest.ini omits xdist, pyproject pins it. No error.
    ini = _cfg("pytest.ini", n=None, dist=None)
    proj = _cfg("pyproject.toml", n="24", dist="worksteal")
    assert vp.validate_configs(ini, proj, strict=True) == 0


def test_pyproject_missing_xdist_errors():
    ini = _cfg("pytest.ini", n=None, dist=None)
    proj = _cfg("pyproject.toml", n=None, dist=None)
    assert vp.validate_configs(ini, proj, strict=True) == 1


def test_conflicting_dist_is_warning_not_error():
    # If pytest.ini DOES pin dist and it disagrees with pyproject -> warning.
    ini = _cfg("pytest.ini", n="24", dist="loadfile")
    proj = _cfg("pyproject.toml", n="24", dist="worksteal")
    # Non-strict: warnings allow CI (exit 2); strict: blocks (exit 1).
    assert vp.validate_configs(ini, proj, strict=False) == 2
    assert vp.validate_configs(ini, proj, strict=True) == 1


def test_missing_timeout_or_serial_still_errors():
    ini = _cfg("pytest.ini", n=None, dist=None, timeout=None)
    proj = _cfg("pyproject.toml", n="24", dist="worksteal")
    assert vp.validate_configs(ini, proj, strict=True) == 1
    ini2 = _cfg("pytest.ini", n=None, dist=None, markers=())
    assert vp.validate_configs(ini2, proj, strict=True) == 1
