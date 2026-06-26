"""apps_rg canonical runtime entrypoint must match registry and CLI reality.

This test replaces the older xfail GovernedRgRun assertion. apps_rg is currently
canonical-dispatch governed through agentic_core.runtime.entry.apps_rg_dispatch.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_apps_eval_registry_allows_canonical_apps_rg_dispatch() -> None:
    src = (REPO_ROOT / "apps_eval" / "registry" / "apps.yaml").read_text(encoding="utf-8")
    assert "agentic_core.runtime.entry.apps_rg_dispatch:dispatch_apps_rg_run" in src


def test_apps_shared_registry_names_current_apps_rg_canonical_entrypoint() -> None:
    src = (REPO_ROOT / "apps_shared" / "integrations" / "app_registry.py").read_text(encoding="utf-8")
    assert 'runner_module="agentic_core.runtime.entry.apps_rg_dispatch"' in src
    assert 'runner_class="dispatch_apps_rg_run"' in src
    assert "apps_rg.canonical_dispatch.e2e.v1" in src


def test_apps_rg_core_entrypoint_delegates_to_canonical_dispatch() -> None:
    src = (REPO_ROOT / "agentic_core" / "runtime" / "entry" / "apps_rg_dispatch.py").read_text(encoding="utf-8")
    assert "def dispatch_apps_rg_run(" in src
    assert "run_canonical_apps_rg_from_cli_primitives" in src


def test_apps_rg_cli_uses_canonical_whole_run_orchestration() -> None:
    src = (REPO_ROOT / "apps_rg" / "__main__.py").read_text(encoding="utf-8")
    assert "run_whole_run_with_route_governance" in src
    assert "apps_rg.scripts.generate_resume" not in src
    assert "generate_resume.main" not in src
