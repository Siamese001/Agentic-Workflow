"""Tests for the cross-app envelope-loader CI gate (Wave 7)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
GATE_PATH = REPO / "ops_scripts" / "ci" / "check_cross_app_envelope_loaders.py"


def _load_gate():
    spec = importlib.util.spec_from_file_location("env_loader_gate", GATE_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_gate_passes_on_main():
    result = subprocess.run(
        [sys.executable, str(GATE_PATH)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"Gate unexpectedly failed.\nstdout={result.stdout}\n"
        f"stderr={result.stderr}"
    )


def test_gate_detects_missing_envelope_import(tmp_path, monkeypatch):
    mod = _load_gate()
    fake = tmp_path / "fake_repo"
    (fake / "apps_foo" / "integrations").mkdir(parents=True)
    (fake / "apps_foo" / "integrations" / "__init__.py").write_text("")
    (fake / "apps_foo" / "integrations" / "from_apps_bar.py").write_text(
        "# bad: no envelope import\n"
        "def load():\n"
        "    return None\n"
    )
    monkeypatch.setattr(mod, "REPO_ROOT", fake)
    monkeypatch.setattr(
        mod,
        "ALLOWLIST_PATH",
        fake / "config" / "cross_app_envelope_loader_allowlist.yaml",
    )
    violations, errors = mod.scan()
    assert not errors
    assert len(violations) == 1
    assert "from_apps_bar.py" in violations[0]["path"]


def test_gate_allows_envelope_import(tmp_path, monkeypatch):
    mod = _load_gate()
    fake = tmp_path / "fake_repo"
    (fake / "apps_foo" / "integrations").mkdir(parents=True)
    (fake / "apps_foo" / "integrations" / "__init__.py").write_text("")
    (fake / "apps_foo" / "integrations" / "from_apps_bar.py").write_text(
        "from apps_shared.contracts.cross_app import ResearchBriefEnvelope\n"
        "def load():\n"
        "    return None\n"
    )
    monkeypatch.setattr(mod, "REPO_ROOT", fake)
    monkeypatch.setattr(
        mod,
        "ALLOWLIST_PATH",
        fake / "config" / "cross_app_envelope_loader_allowlist.yaml",
    )
    violations, errors = mod.scan()
    assert not errors
    assert not violations


def test_gate_honors_allowlist(tmp_path, monkeypatch):
    mod = _load_gate()
    fake = tmp_path / "fake_repo"
    (fake / "apps_foo" / "integrations").mkdir(parents=True)
    (fake / "apps_foo" / "integrations" / "__init__.py").write_text("")
    (fake / "apps_foo" / "integrations" / "from_apps_local.py").write_text(
        "# local file, not cross-app\n"
    )
    (fake / "config").mkdir()
    (fake / "config" / "cross_app_envelope_loader_allowlist.yaml").write_text(
        "allowed_loaders:\n"
        "  - path: apps_foo/integrations/from_apps_local.py\n"
        "    reason: local-only loader, not a real cross-app consumer\n"
    )
    monkeypatch.setattr(mod, "REPO_ROOT", fake)
    monkeypatch.setattr(
        mod,
        "ALLOWLIST_PATH",
        fake / "config" / "cross_app_envelope_loader_allowlist.yaml",
    )
    violations, errors = mod.scan()
    assert not errors
    assert not violations
