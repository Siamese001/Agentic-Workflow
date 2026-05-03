"""Tests for the cross-app import CI gate (Wave 6, AG-1 Option C)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_gate_passes_on_main():
    """The gate must exit 0 on HEAD — all current imports are allowlisted."""
    repo = Path(__file__).resolve().parents[4]
    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_cross_app_imports.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Gate unexpectedly failed on main.\nstdout={result.stdout}\n"
        f"stderr={result.stderr}"
    )


def test_gate_detects_unallowlisted_import(tmp_path, monkeypatch):
    """Construct a minimal fake repo with an un-allowlisted peer import."""
    import importlib.util

    repo = Path(__file__).resolve().parents[4]
    spec = importlib.util.spec_from_file_location(
        "cross_app_gate",
        repo / "ops_scripts" / "ci" / "check_cross_app_imports.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    fake = tmp_path / "fake_repo"
    (fake / "apps_foo").mkdir(parents=True)
    (fake / "apps_bar").mkdir(parents=True)
    (fake / "config").mkdir()
    (fake / "apps_foo" / "__init__.py").write_text("")
    (fake / "apps_bar" / "__init__.py").write_text("")
    (fake / "apps_foo" / "module.py").write_text(
        "from apps_bar import something\n"
    )
    (fake / "config" / "cross_app_import_allowlist.yaml").write_text(
        "allowed_imports: []\n"
    )

    monkeypatch.setattr(mod, "REPO_ROOT", fake)
    monkeypatch.setattr(
        mod, "ALLOWLIST_PATH", fake / "config" / "cross_app_import_allowlist.yaml"
    )

    violations, errors = mod.scan()
    assert not errors
    assert len(violations) == 1
    assert violations[0]["target_package"] == "apps_bar"
    assert "apps_foo" in violations[0]["source_module"]


def test_gate_rejects_expired_allowlist(tmp_path, monkeypatch):
    """An expired allowlist entry must be reported as an error, not silently passed."""
    import importlib.util

    repo = Path(__file__).resolve().parents[4]
    spec = importlib.util.spec_from_file_location(
        "cross_app_gate",
        repo / "ops_scripts" / "ci" / "check_cross_app_imports.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    fake = tmp_path / "fake_repo"
    (fake / "config").mkdir(parents=True)
    (fake / "config" / "cross_app_import_allowlist.yaml").write_text(
        "allowed_imports:\n"
        "  - source: apps_foo.x\n"
        "    target: apps_bar\n"
        "    reason: expired\n"
        "    lazy: false\n"
        "    expires: '2020-01-01'\n"
    )

    monkeypatch.setattr(mod, "REPO_ROOT", fake)
    monkeypatch.setattr(
        mod, "ALLOWLIST_PATH", fake / "config" / "cross_app_import_allowlist.yaml"
    )

    violations, errors = mod.scan()
    assert errors, "expired entry must produce an error"
    assert "EXPIRED" in errors[0]


def test_gate_permits_apps_shared_target(tmp_path, monkeypatch):
    """apps_* -> apps_shared is always permitted; no allowlist entry required."""
    import importlib.util

    repo = Path(__file__).resolve().parents[4]
    spec = importlib.util.spec_from_file_location(
        "cross_app_gate",
        repo / "ops_scripts" / "ci" / "check_cross_app_imports.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    fake = tmp_path / "fake_repo"
    (fake / "apps_foo").mkdir(parents=True)
    (fake / "apps_shared").mkdir(parents=True)
    (fake / "config").mkdir()
    (fake / "apps_foo" / "__init__.py").write_text("")
    (fake / "apps_shared" / "__init__.py").write_text("")
    (fake / "apps_foo" / "m.py").write_text("from apps_shared import x\n")
    (fake / "config" / "cross_app_import_allowlist.yaml").write_text(
        "allowed_imports: []\n"
    )

    monkeypatch.setattr(mod, "REPO_ROOT", fake)
    monkeypatch.setattr(
        mod, "ALLOWLIST_PATH", fake / "config" / "cross_app_import_allowlist.yaml"
    )

    violations, errors = mod.scan()
    assert not violations
    assert not errors
