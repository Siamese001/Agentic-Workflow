"""Quarantine / removal regression — retired paths must not return to product spine.

Plan apps-rg-quarantine-ssot-fanin-delete-c7e4a1 (W1.3). Supersedes W0A import-time stub tests
for modules that were hard-deleted (ModuleNotFoundError), not RuntimeError(QUARANTINE).
"""
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Hard-deleted or never on product spine — must not import successfully.
REMOVED_MODULES: tuple[tuple[str, str], ...] = (
    ("apps_rg.runtime.entry.dispatch", "runtime.entry.dispatch"),
    ("apps_rg.integrations.gates.online_judges", "integrations.gates.online_judges"),
    ("apps_rg.engines.judges.executive_positioning_judge", "engines.judges.executive_positioning_judge"),
    ("apps_rg.tools.compute_word_count", "tools.compute_word_count"),
)

REMOVED_PATHS: tuple[str, ...] = (
    "apps_rg/reasoning/",
    "apps_rg/_quarantine/",
    "apps_rg/runtime/dry_run/",
    "apps_rg/runtime/entry/dispatch.py",
    "apps_rg/engines/judges/executive_positioning_judge.py",
    "apps_rg/integrations/gates/online_judges.py",
    "apps_rg/tools/compute_word_count.py",
)


def _purge(mod_name: str) -> None:
    for key in list(sys.modules):
        if key == mod_name or key.startswith(mod_name + "."):
            del sys.modules[key]


@pytest.mark.parametrize("mod_name,hint", REMOVED_MODULES)
def test_removed_modules_raise_module_not_found(mod_name: str, hint: str) -> None:
    _purge(mod_name)
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(mod_name)


@pytest.mark.parametrize("rel_path", REMOVED_PATHS)
def test_removed_paths_absent_on_disk(rel_path: str) -> None:
    target = REPO_ROOT / rel_path
    if rel_path.endswith("/"):
        assert not target.is_dir(), rel_path
    else:
        assert not target.is_file(), rel_path


class TestRemovedModulesFailInSubprocess:
    @pytest.mark.parametrize("mod_name", [m[0] for m in REMOVED_MODULES])
    def test_subprocess_import_fails(self, mod_name: str) -> None:
        code = f"import importlib; importlib.import_module({mod_name!r})"
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode != 0
