"""Delegate ``python -m apps_rg`` to WSL when Windows Smart App Control blocks PyTorch."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _in_wsl_already() -> bool:
    return bool(os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"))


def _embedding_import_blocked() -> bool:
    try:
        import torch  # noqa: F401
    except ImportError as exc:
        msg = str(exc)
        return "Application Control policy" in msg or "torch._C" in msg
    return False


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "apps_rg" / "__main__.py").is_file():
            return parent
    return Path.cwd()


def _wsl_repo_path(repo: Path) -> str:
    drive = repo.drive.rstrip(":").lower()
    tail = str(repo.relative_to(repo.anchor)).replace("\\", "/")
    return f"/mnt/{drive}/{tail}"


def should_delegate_apps_rg_to_wsl(argv: list[str] | None = None) -> bool:
    if os.environ.get("APPS_RG_WINDOWS_SAC_DELEGATED") == "1":
        return False
    if os.environ.get("APPS_RG_DISABLE_WSL_DELEGATE", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    ):
        return False
    if sys.platform != "win32" or _in_wsl_already():
        return False
    if not shutil.which("wsl"):
        return False
    args = list(argv or sys.argv[1:])
    if not args:
        return False
    if "--section" not in args and not any(
        a in args
        for a in (
            "--executive-summary",
            "--headline",
            "--unify-bullets",
            "--unify-narrative",
            "--ibm-bullets",
            "--ibm-narrative",
            "--competencies",
        )
    ):
        return False
    return _embedding_import_blocked()


def delegate_apps_rg_to_wsl(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    repo = _repo_root()
    repo_wsl = _wsl_repo_path(repo)
    runner = f"{repo_wsl}/tools/apps_rg/run_section_wsl.sh"
    venv_py = "~/.cache/awf-venv-wsl/bin/python"
    arg_line = " ".join(
        f"'{a.replace(chr(39), chr(39) * 2)}'" if " " in a or "'" in a else a for a in args
    )
    inner = (
        f"export APPS_RG_WINDOWS_SAC_DELEGATED=1; "
        f"if ! test -x {venv_py}; then sed -i 's/\\r$//' {repo_wsl}/tools/apps_rg/wsl_bootstrap.sh "
        f"&& bash {repo_wsl}/tools/apps_rg/wsl_bootstrap.sh; fi; "
        f"sed -i 's/\\r$//' {runner} && bash {runner} {arg_line}"
    )
    print(
        "Windows Smart App Control blocked PyTorch; re-running via WSL "
        f"({runner}). See docs/guides/windows_smart_app_control_apps_rg.md",
        flush=True,
    )
    proc = subprocess.run(  # guardian: allow-chokepoint-bypass -- Windows SAC workaround delegates to WSL bash; same argv contract as direct run
        ["wsl", "-e", "bash", "-lc", inner], shell=False
    )
    return int(proc.returncode)


__all__ = ["delegate_apps_rg_to_wsl", "should_delegate_apps_rg_to_wsl"]
