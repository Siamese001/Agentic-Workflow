"""ADG-hotspot scaffold tests for `agentic_core.config.env_loader` (fanin=1, band=P4).

Auto-generated speculative scaffold. Verify class/function names against actual
module before extending these scaffolds with behavioral assertions.
"""
from __future__ import annotations

import importlib

import pytest


MODULE_PATH = "agentic_core.config.env_loader"


def test_module_imports():
    mod = importlib.import_module(MODULE_PATH)
    assert mod is not None


def test_module_has_public_surface():
    mod = importlib.import_module(MODULE_PATH)
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    importlib.import_module(MODULE_PATH)
    importlib.import_module(MODULE_PATH)


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    mod = importlib.import_module(MODULE_PATH)
    has_callable = any(
        callable(getattr(mod, n))
        for n in dir(mod)
        if not n.startswith("_")
    )
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    mod = importlib.import_module(MODULE_PATH)
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), (
        f"{MODULE_PATH} not under agentic_core: {file}"
    )


def test_resolve_dotenv_prefers_repo_root(tmp_path, monkeypatch):
    from agentic_core.config import env_loader

    root = tmp_path / "repo"
    root.mkdir()
    (root / ".env").write_text("A=1\n", encoding="utf-8")
    home_ssot = tmp_path / "home_env" / ".env"
    home_ssot.parent.mkdir()
    home_ssot.write_text("A=2\n", encoding="utf-8")
    monkeypatch.setattr(env_loader, "_home_ssot_dotenv", lambda: home_ssot)

    assert env_loader._resolve_dotenv_path(root) == root / ".env"


def test_resolve_dotenv_falls_back_to_home_ssot(tmp_path, monkeypatch):
    """A worktree/checkout with no root .env resolves the app-neutral ~/env/.env SSOT."""
    from agentic_core.config import env_loader

    root = tmp_path / "blank_worktree"
    root.mkdir()  # no .env (mirrors `git worktree add` / retired repo-root copy)
    home_ssot = tmp_path / "home_env" / ".env"
    home_ssot.parent.mkdir()
    home_ssot.write_text("A=2\n", encoding="utf-8")
    monkeypatch.setattr(env_loader, "_home_ssot_dotenv", lambda: home_ssot)

    assert env_loader._resolve_dotenv_path(root) == home_ssot


def test_load_fails_fast_naming_both_candidates(tmp_path, monkeypatch):
    from agentic_core.config import env_loader

    root = tmp_path / "repo"
    root.mkdir()
    missing_home = tmp_path / "no_home" / ".env"
    monkeypatch.setattr(env_loader, "_home_ssot_dotenv", lambda: missing_home)

    # object.__new__ avoids the singleton; _load raises before touching self.
    instance = object.__new__(env_loader.SovereignEnv)
    with pytest.raises(FileNotFoundError) as exc:
        env_loader.SovereignEnv._load(instance, root)
    assert str(root / ".env") in str(exc.value)
    assert str(missing_home) in str(exc.value)
