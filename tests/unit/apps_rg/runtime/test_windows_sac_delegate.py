from __future__ import annotations

from pathlib import Path

from apps_rg.runtime import windows_sac_delegate as subject


def test_should_delegate_apps_rg_to_wsl_requires_windows_section_and_blocked_embedding(
    monkeypatch,
) -> None:
    monkeypatch.delenv("APPS_RG_WINDOWS_SAC_DELEGATED", raising=False)
    monkeypatch.delenv("APPS_RG_DISABLE_WSL_DELEGATE", raising=False)
    monkeypatch.setattr(subject.sys, "platform", "win32")
    monkeypatch.setattr(subject, "_in_wsl_already", lambda: False)
    monkeypatch.setattr(subject.shutil, "which", lambda name: "wsl.exe" if name == "wsl" else None)
    monkeypatch.setattr(subject, "_embedding_import_blocked", lambda: True)

    assert subject.should_delegate_apps_rg_to_wsl([]) is False
    assert subject.should_delegate_apps_rg_to_wsl(["--section", "headline"]) is True
    assert subject.should_delegate_apps_rg_to_wsl(["--headline"]) is True


def test_should_delegate_apps_rg_to_wsl_respects_disable_and_reentry_env(
    monkeypatch,
) -> None:
    monkeypatch.setattr(subject.sys, "platform", "win32")
    monkeypatch.setattr(subject, "_in_wsl_already", lambda: False)
    monkeypatch.setattr(subject.shutil, "which", lambda name: "wsl.exe")
    monkeypatch.setattr(subject, "_embedding_import_blocked", lambda: True)

    monkeypatch.setenv("APPS_RG_WINDOWS_SAC_DELEGATED", "1")
    assert subject.should_delegate_apps_rg_to_wsl(["--section", "headline"]) is False

    monkeypatch.delenv("APPS_RG_WINDOWS_SAC_DELEGATED", raising=False)
    monkeypatch.setenv("APPS_RG_DISABLE_WSL_DELEGATE", "true")
    assert subject.should_delegate_apps_rg_to_wsl(["--section", "headline"]) is False


def test_wsl_repo_path_translates_windows_drive_path() -> None:
    assert subject._wsl_repo_path(Path(r"C:\Git\Agentic-Workflow-FRESH")) == (
        "/mnt/c/Git/Agentic-Workflow-FRESH"
    )
