"""apps_rg environment bootstrap behavior."""

from __future__ import annotations

import os
from pathlib import Path

from apps_rg.runtime.env_bootstrap import (
    APPS_RG_DOTENV_ENV_VAR,
    bootstrap_apps_rg_env,
    canonical_home_dotenv,
)
import apps_rg.runtime.env_bootstrap as env_bootstrap
import apps_rg.runtime.judges.executive_summary_x1d as x1d
import apps_rg.integrations.hops._llm_client as hops_llm_client


def test_bootstrap_apps_rg_env_loads_explicit_repo_dotenv(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(APPS_RG_DOTENV_ENV_VAR, raising=False)
    (tmp_path / ".env").write_text(
        "OPENAI_API_KEY=dotenv-openai\n"
        "ANTHROPIC_API_KEY=dotenv-anthropic\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    result = bootstrap_apps_rg_env(repo_root=tmp_path)

    assert result.dotenv_path_existed is True
    assert result.dotenv_loaded is True
    assert result.dotenv_source == "repo_root"
    assert os.environ["OPENAI_API_KEY"] == "dotenv-openai"
    assert os.environ["ANTHROPIC_API_KEY"] == "dotenv-anthropic"


def test_bootstrap_apps_rg_env_preserves_shell_exports(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(APPS_RG_DOTENV_ENV_VAR, raising=False)
    (tmp_path / ".env").write_text("OPENAI_API_KEY=dotenv-openai\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "shell-openai")

    bootstrap_apps_rg_env(repo_root=tmp_path)

    assert os.environ["OPENAI_API_KEY"] == "shell-openai"


def test_apps_rg_dotenv_override_wins_over_repo_root(tmp_path: Path, monkeypatch) -> None:
    """$APPS_RG_DOTENV (the cross-worktree SSOT) takes precedence over a worktree-local .env."""
    repo = tmp_path / "worktree"
    repo.mkdir()
    (repo / ".env").write_text("ANTHROPIC_API_KEY=repo-local\n", encoding="utf-8")
    ssot = tmp_path / "ssot.env"
    ssot.write_text("ANTHROPIC_API_KEY=ssot-anthropic\n", encoding="utf-8")
    monkeypatch.setenv(APPS_RG_DOTENV_ENV_VAR, str(ssot))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    result = bootstrap_apps_rg_env(repo_root=repo)

    assert result.dotenv_source == "env_override"
    assert result.dotenv_path == str(ssot)
    assert os.environ["ANTHROPIC_API_KEY"] == "ssot-anthropic"


def test_bootstrap_falls_back_to_home_ssot_when_worktree_blank(tmp_path: Path, monkeypatch) -> None:
    """A fresh worktree with no .env and no override still resolves the canonical home SSOT."""
    repo = tmp_path / "blank_worktree"
    repo.mkdir()  # no .env materialized (mirrors `git worktree add`)
    home_ssot = tmp_path / "home" / ".apps_rg" / ".env"
    home_ssot.parent.mkdir(parents=True)
    home_ssot.write_text("ANTHROPIC_API_KEY=home-ssot\n", encoding="utf-8")
    monkeypatch.delenv(APPS_RG_DOTENV_ENV_VAR, raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(env_bootstrap, "canonical_home_dotenv", lambda: home_ssot)

    result = bootstrap_apps_rg_env(repo_root=repo)

    assert result.dotenv_source == "home_ssot"
    assert os.environ["ANTHROPIC_API_KEY"] == "home-ssot"


def test_apps_rg_cli_bootstraps_env_before_production_runtime_guard() -> None:
    src = Path("apps_rg/__main__.py").read_text(encoding="utf-8")

    assert src.index("bootstrap_apps_rg_env(repo_root=_repo_root)") < src.index(
        "assert_production_runtime(context=\"python -m apps_rg\", args=args)"
    )


def test_x1d_credential_resolver_bootstraps_process_env(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    calls = {"count": 0}

    def _bootstrap(environ) -> None:
        calls["count"] += 1
        assert environ is os.environ
        monkeypatch.setenv("ANTHROPIC_API_KEY", "dotenv-anthropic")

    monkeypatch.setattr(x1d, "bootstrap_process_env_if_needed", _bootstrap)

    key, consulted = x1d.resolve_x1d_provider_credentials("anthropic_claude", os.environ)

    assert calls["count"] == 1
    assert key == "dotenv-anthropic"
    assert consulted == ["ANTHROPIC_API_KEY"]


def test_x1d_credential_resolver_does_not_bootstrap_injected_env(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "process-openai")

    key, consulted = x1d.resolve_x1d_provider_credentials("openai_chatgpt", {})

    assert key == ""
    assert consulted == ["OPENAI_API_KEY"]


def test_hops_llm_client_bootstraps_before_provider_probe(monkeypatch) -> None:
    for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    def _bootstrap() -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "dotenv-openai")

    monkeypatch.setattr(hops_llm_client, "bootstrap_apps_rg_env", _bootstrap)
    monkeypatch.setattr(
        hops_llm_client,
        "_make_openai_generator",
        lambda **_kwargs: "openai-generator",
    )

    assert hops_llm_client.make_generator() == "openai-generator"
